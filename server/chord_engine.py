"""See Harmony chord engine (v66).

Per audio segment:
  1. harmonic part of the signal (HPSS, removes drums and transients)
  2. tuned constant-Q spectrum, 36 bins per octave, E1 to about C8
  3. local spectral whitening along frequency
  4. note salience by non-negative least squares against a dictionary of
     harmonic series, so a note's overtones are not counted as other notes
     (in the spirit of Mauch & Dixon's NNLS chroma)
  5. treble chroma and bass chroma from the note saliences
  6. per-frame chord scores: cosine to binary chord templates + bass-root term
  7. Viterbi decoding with a constant penalty per chord change

Vocabulary = the chord types the semantic colour layer can show.
Parameters were tuned on a synthetic development set and checked on a
separate held-out set (see EVALUATION.md).
"""
import numpy as np
import librosa
from scipy.optimize import nnls
from scipy.ndimage import uniform_filter1d

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# quality -> (intervals above the root, display suffix)
VOCAB = {
    'maj': ([0, 4, 7], ''), 'min': ([0, 3, 7], 'm'), '7': ([0, 4, 7, 10], '7'),
    'maj7': ([0, 4, 7, 11], 'maj7'), 'min7': ([0, 3, 7, 10], 'm7'), 'hdim7': ([0, 3, 6, 10], 'm7b5'),
    'dim7': ([0, 3, 6, 9], 'dim7'), 'dim': ([0, 3, 6], 'dim'), 'aug': ([0, 4, 8], 'aug'),
    'sus4': ([0, 5, 7], 'sus4'),
}

SR = 22050
P = dict(
    hop=1024, frame_agg=2,             # ~0.093 s per decoded frame
    bpo=36, fmin_midi=28, n_oct=6.5,   # E1 .. ~C8
    hpss_margin=2.0, whiten_oct=1.0,
    harm_decay=0.7, n_harm=12,
    treble_lo=36, treble_hi=95, bass_lo=28, bass_hi=55,
    w_bass=0.6, triad_bias=-0.05, switch=1.6,
    qual_bias={'sus4': -0.08, 'aug': -0.08, 'dim7': -0.04},
    silence_rel=0.02,
    win_hpss=True, win_hpss_light=True, win_res_type=None,    # microphone windows (analyze_window)
)

KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

_DICT = {}


def _dictionary(n_bins):
    if n_bins in _DICT:
        return _DICT[n_bins]
    midis = np.arange(P['fmin_midi'], P['fmin_midi'] + int(P['n_oct'] * 12))
    bins = np.arange(n_bins)
    D = np.zeros((n_bins, len(midis)))
    per_semi = P['bpo'] / 12
    for j, m in enumerate(midis):
        for h in range(1, P['n_harm'] + 1):
            pos = (m - P['fmin_midi']) * per_semi + P['bpo'] * np.log2(h)
            if pos > n_bins:
                break
            D[:, j] += (P['harm_decay'] ** (h - 1)) * np.exp(-0.5 * ((bins - pos) / 0.6) ** 2)
    D /= np.linalg.norm(D, axis=0, keepdims=True) + 1e-9
    _DICT[n_bins] = (midis, D)
    return midis, D


def _salience(y, hpss=True, res_type=None, hpss_light=False):
    margin = P['hpss_margin'] if hpss else 0
    n_fft = 2048 if len(y) >= 2048 * 2 else 512
    if margin and hpss_light:      # cheaper separation for short windows
        yh = librosa.effects.harmonic(y, margin=margin, n_fft=1024, hop_length=256, kernel_size=13)
    elif margin:
        yh = librosa.effects.harmonic(y, margin=margin, n_fft=n_fft)
    else:
        yh = y
    tuning = float(librosa.estimate_tuning(y=yh, sr=SR, bins_per_octave=36)) if len(yh) > SR else 0.0
    n_bins = int(P['n_oct'] * P['bpo'])
    kw = {'res_type': res_type} if res_type else {}
    C = np.abs(librosa.cqt(yh, sr=SR, hop_length=P['hop'], fmin=librosa.midi_to_hz(P['fmin_midi']),
                           n_bins=n_bins, bins_per_octave=P['bpo'], tuning=tuning, **kw))
    k = P['frame_agg']
    if k > 1 and C.shape[1] >= k:
        T = C.shape[1] // k
        C = C[:, :T * k].reshape(n_bins, T, k).mean(2)
    w = max(3, int(P['whiten_oct'] * P['bpo']))
    mu = uniform_filter1d(C, w, axis=0, mode='nearest')
    sd = np.sqrt(np.maximum(uniform_filter1d(C ** 2, w, axis=0, mode='nearest') - mu ** 2, 1e-12))
    Cw = np.maximum(0, (C - mu) / (sd + 1e-9))
    midis, D = _dictionary(n_bins)
    A = np.zeros((len(midis), Cw.shape[1]))
    for t in range(Cw.shape[1]):
        if Cw[:, t].sum() > 1e-6:
            A[:, t] = nnls(D, Cw[:, t], maxiter=200)[0]
    times = librosa.frames_to_time(np.arange(A.shape[1]), sr=SR, hop_length=P['hop'] * k)
    return midis, A, times


def _chromas(midis, A):
    pc = midis % 12
    tw = ((midis >= P['treble_lo']) & (midis <= P['treble_hi'])).astype(float)
    bw = np.clip(1 - np.abs(midis - (P['bass_lo'] + 10)) / 18.0, 0, 1) * (midis <= P['bass_hi'])
    T = np.zeros((12, A.shape[1])); B = np.zeros((12, A.shape[1]))
    for k in range(12):
        T[k] = (A[pc == k] * tw[pc == k, None]).sum(0)
        B[k] = (A[pc == k] * bw[pc == k, None]).sum(0)
    return T, B


def _chord_list():
    out = []
    for q, (ivs, sfx) in VOCAB.items():
        for r in range(12):
            t = np.zeros(12); t[[(r + i) % 12 for i in ivs]] = 1
            out.append((r, q, NOTES[r] + sfx, t / np.linalg.norm(t)))
    return out


CHORDS = _chord_list()


def _scores(T, B):
    Tn = T / (np.linalg.norm(T, axis=0, keepdims=True) + 1e-9)
    Bn = B / (B.sum(0, keepdims=True) + 1e-9)
    S = np.zeros((len(CHORDS) + 1, T.shape[1]))
    for i, (r, q, lbl, tn) in enumerate(CHORDS):
        s = tn @ Tn + P['w_bass'] * Bn[r]
        if len(VOCAB[q][0]) == 3:
            s += P['triad_bias']
        S[i] = s + P['qual_bias'].get(q, 0.0)
    tot = T.sum(0)
    ref = np.median(tot[tot > 0]) if (tot > 0).any() else 1.0
    S[-1] = np.where(tot < P['silence_rel'] * ref, 2.0, -1.0)      # no-chord on near-silence
    return S


def _viterbi(S, switch):
    K, Tn = S.shape
    dp = S[:, 0].copy(); bp = np.zeros((K, Tn), dtype=np.int32)
    idx = np.arange(K)
    for t in range(1, Tn):
        best = int(dp.argmax())
        jump = dp[best] - switch
        choose = jump > dp
        bp[:, t] = np.where(choose, best, idx)
        dp = np.where(choose, jump, dp) + S[:, t]
    path = np.zeros(Tn, dtype=np.int32); path[-1] = int(dp.argmax())
    for t in range(Tn - 1, 0, -1):
        path[t - 1] = bp[path[t], t]
    return path


def _label(i):
    return CHORDS[i][2] if i < len(CHORDS) else 'N'


def detect_key(chroma):
    c = np.asarray(chroma, float)
    if c.sum() <= 0:
        return 'C'
    a = c - c.mean(); best, label = -np.inf, 'C'
    for r in range(12):
        for prof, sfx in ((KK_MAJ, ''), (KK_MIN, ' min')):
            b = np.roll(prof, r) - prof.mean()
            cor = (a @ b) / (np.sqrt((a @ a) * (b @ b)) + 1e-10)
            if cor > best:
                best, label = cor, NOTES[r] + sfx
    return label


def _prepare(audio, sr):
    y = np.asarray(audio, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=1)
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    peak = float(np.max(np.abs(y))) if len(y) else 0.0
    return y / peak if peak > 1e-6 else y


def analyze_segment(audio, sr):
    """Chord timeline for a segment: {'timeline': [{'t','chord'}], 'chroma': [12], 'duration'}.
    'N' marks silence."""
    y = _prepare(audio, sr)
    dur = len(y) / SR
    if dur < 0.3:
        return {'timeline': [], 'chroma': [0.0] * 12, 'duration': round(dur, 3)}
    midis, A, times = _salience(y)
    T, B = _chromas(midis, A)
    path = _viterbi(_scores(T, B), P['switch'])
    tl, prev = [], None
    for t, i in zip(times, path):
        lbl = _label(int(i))
        if lbl != prev:
            tl.append({'t': round(float(t), 3), 'chord': lbl}); prev = lbl
    tc = T.sum(1); tc = tc / (tc.sum() + 1e-9)
    return {'timeline': tl, 'chroma': [round(float(x), 5) for x in tc], 'duration': round(dur, 3)}


def analyze_window(audio, sr):
    """One label for a short window (microphone mode)."""
    y = _prepare(audio, sr)
    if len(y) < SR * 0.25 or float(np.sqrt(np.mean(y ** 2))) < 1e-4:
        return {'chord': '', 'confidence': 0.0, 'chroma': [0.0] * 12}
    midis, A, _ = _salience(y, hpss=P['win_hpss'], res_type=P['win_res_type'], hpss_light=P['win_hpss_light'])
    T, B = _chromas(midis, A)
    S = _scores(T.mean(1, keepdims=True), B.mean(1, keepdims=True))[:-1, 0]
    order = np.argsort(S)[::-1]
    i = int(order[0]); margin = float(S[order[0]] - S[order[1]])
    tc = T.mean(1); tc = tc / (tc.sum() + 1e-9)
    # top candidates with scores, so the browser can accumulate evidence over time
    top = [[_label(int(j)), round(float(S[j]), 4)] for j in order[:8]]
    return {'chord': _label(i), 'confidence': round(min(1.0, margin / 0.15), 3),
            'chroma': [round(float(x), 4) for x in tc], 'top': top}


def analyze_file(audio, sr):
    """Whole file in one call (kept for the /analyze endpoint)."""
    r = analyze_segment(audio, sr)
    tl, prev = [], None
    for e in r['timeline']:
        if e['chord'] != 'N' and e['chord'] != prev:
            tl.append(e); prev = e['chord']
    return {'key': detect_key(r['chroma']), 'timeline': tl, 'duration': r['duration']}
