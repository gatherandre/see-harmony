import numpy as np
import librosa

NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

CHORD_SUFFIX = {
    'maj':'', 'min':'m', 'dim':'dim', 'aug':'aug',
    'maj7':'maj7', 'min7':'m7', 'dom7':'7', 'dim7':'dim7',
    'm7b5':'m7b5', 'mMaj7':'mMaj7',
    '6':'6', 'm6':'m6',
    'sus2':'sus2', 'sus4':'sus4', '7sus4':'7sus4',
    'maj9':'maj9', 'min9':'m9', 'dom9':'9',
    '7b9':'7b9', '7#9':'7#9',
    'add9':'add9', 'madd9':'madd9',
    'dom11':'11', 'min11':'m11',
    'dom13':'13', 'maj13':'maj13', 'min13':'m13',
}

# Chord templates — interval vectors (root=0)
CHORD_TEMPLATES = {
    # Triads
    'maj':    [1,0,0,0,1,0,0,1,0,0,0,0],
    'min':    [1,0,0,1,0,0,0,1,0,0,0,0],
    'dim':    [1,0,0,1,0,0,1,0,0,0,0,0],
    'aug':    [1,0,0,0,1,0,0,0,1,0,0,0],
    # Seventh chords
    'maj7':   [1,0,0,0,1,0,0,1,0,0,0,1],
    'min7':   [1,0,0,1,0,0,0,1,0,0,1,0],
    'dom7':   [1,0,0,0,1,0,0,1,0,0,1,0],
    'dim7':   [1,0,0,1,0,0,1,0,0,1,0,0],
    'm7b5':   [1,0,0,1,0,0,1,0,0,0,1,0],
    'mMaj7':  [1,0,0,1,0,0,0,1,0,0,0,1],
    '6':      [1,0,0,0,1,0,0,1,0,1,0,0],
    'm6':     [1,0,0,1,0,0,0,1,0,1,0,0],
    # Sus chords
    'sus2':   [1,0,1,0,0,0,0,1,0,0,0,0],
    'sus4':   [1,0,0,0,0,1,0,1,0,0,0,0],
    '7sus4':  [1,0,0,0,0,1,0,1,0,0,1,0],
    # Ninth chords
    'maj9':   [1,0,1,0,1,0,0,1,0,0,0,1],
    'min9':   [1,0,1,1,0,0,0,1,0,0,1,0],
    'dom9':   [1,0,1,0,1,0,0,1,0,0,1,0],
    '7b9':    [1,1,0,0,1,0,0,1,0,0,1,0],
    '7#9':    [1,0,0,1,1,0,0,1,0,0,1,0],
    'add9':   [1,0,1,0,1,0,0,1,0,0,0,0],
    'madd9':  [1,0,1,1,0,0,0,1,0,0,0,0],
    # Eleventh chords
    'dom11':  [1,0,1,0,1,1,0,1,0,0,1,0],
    'min11':  [1,0,1,1,0,1,0,1,0,0,1,0],
    # Thirteenth chords
    'dom13':  [1,0,1,0,1,1,0,1,0,1,1,0],
    'maj13':  [1,0,1,0,1,1,0,1,0,1,0,1],
    'min13':  [1,0,1,1,0,1,0,1,0,1,1,0],
}

# Complexity penalty per chord type (notes above root/3rd/5th)
COMPLEXITY = {t: max(0, sum(v) - 3) for t, v in CHORD_TEMPLATES.items()}

KK_MAJ = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KK_MIN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])


def detect_key(chroma_mean):
    """Krumhansl-Schmuckler key detection."""
    best, det_key, det_mode = -np.inf, 0, 'maj'
    for r in range(12):
        for mode, prof in [('maj', KK_MAJ), ('min', KK_MIN)]:
            pv = np.roll(prof, r); mp = pv.mean()
            a = chroma_mean - chroma_mean.mean()
            b = pv - mp
            cor = np.dot(a, b) / (np.sqrt(np.dot(a,a)*np.dot(b,b)) + 1e-10)
            if cor > best:
                best = cor; det_key = r; det_mode = mode
    return det_key, det_mode


def chord_label(root, ctype):
    sfx = CHORD_SUFFIX.get(ctype, ctype)
    return NOTES[root] + sfx


def score_chord(ch_norm, root, ctype, bass_root, bass_conf):
    """Score a chord given normalised chroma."""
    tmpl = np.array(CHORD_TEMPLATES[ctype], dtype=float)
    rolled = np.roll(ch_norm, -root)
    pos_w, neg_w = 2.5, -0.8
    score = float(np.dot(rolled, np.where(tmpl > 0, pos_w, neg_w)))
    # Bass root anchoring — decisive
    if root == bass_root:
        score += bass_conf * 20.0
    # Prefer simpler chords — penalty for each extra note beyond triad
    score -= COMPLEXITY[ctype] * 0.4
    return score


def analyze_chunk(audio: np.ndarray, sr: int) -> dict:
    """
    Detect chord from a short audio chunk (0.5–3s).
    Returns {'chord': str, 'confidence': float, 'chroma': list}
    """
    if len(audio) < sr * 0.1:
        return {'chord': '', 'confidence': 0.0, 'chroma': [0.0]*12}

    # Harmonic separation
    try:
        y_harm = librosa.effects.harmonic(audio, margin=4)
    except Exception:
        y_harm = audio

    # CQT chroma — much better than STFT for polyphonic music
    try:
        chroma = librosa.feature.chroma_cqt(
            y=y_harm, sr=sr,
            bins_per_octave=36,
            norm=2,
            fmin=librosa.note_to_hz('C2')
        )
    except Exception:
        chroma = librosa.feature.chroma_stft(y=y_harm, sr=sr, n_fft=8192)

    ch = np.mean(chroma, axis=1)
    ch_norm = ch / (ch.sum() + 1e-8)

    # Bass chroma — bottom 2 octaves only (root detection)
    try:
        chroma_bass = librosa.feature.chroma_cqt(
            y=y_harm, sr=sr,
            bins_per_octave=36,
            n_octaves=2,
            fmin=librosa.note_to_hz('E1'),
            norm=2
        )
        ch_bass = np.mean(chroma_bass, axis=1)
    except Exception:
        ch_bass = ch.copy()

    bass_root = int(np.argmax(ch_bass))
    bass_conf = float(ch_bass[bass_root] / (ch_bass.sum() + 1e-8))

    # Score all chords
    best_score = -np.inf
    best_root, best_type = 0, 'maj'
    for root in range(12):
        for ctype in CHORD_TEMPLATES:
            s = score_chord(ch_norm, root, ctype, bass_root, bass_conf)
            if s > best_score:
                best_score = s
                best_root = root
                best_type = ctype

    label = chord_label(best_root, best_type)
    conf = min(1.0, max(0.0, (best_score + 5) / 30.0))

    return {
        'chord': label,
        'confidence': round(conf, 3),
        'chroma': [round(float(x), 4) for x in ch_norm.tolist()]
    }


def analyze_file(audio: np.ndarray, sr: int,
                 win_sec: float = 2.0, hop_sec: float = 0.5) -> dict:
    """
    Full file analysis — returns key + chord timeline.
    """
    target_sr = 22050
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    # Global key detection
    try:
        y_harm_full = librosa.effects.harmonic(audio, margin=4)
    except Exception:
        y_harm_full = audio

    try:
        chroma_full = librosa.feature.chroma_cqt(
            y=y_harm_full, sr=sr, bins_per_octave=36, norm=2,
            fmin=librosa.note_to_hz('C2')
        )
    except Exception:
        chroma_full = librosa.feature.chroma_stft(y=y_harm_full, sr=sr)

    ch_global = np.mean(chroma_full, axis=1)
    det_key, det_mode = detect_key(ch_global)
    key_label = NOTES[det_key] + (' min' if det_mode == 'min' else '')

    # Windowed chord detection
    win = int(win_sec * sr)
    hop = int(hop_sec * sr)
    n_frames = max(1, (len(audio) - win) // hop + 1)

    raw = []
    for i in range(n_frames):
        start = i * hop
        chunk = audio[start:start + win]
        if len(chunk) < win:
            chunk = np.pad(chunk, (0, win - len(chunk)))
        result = analyze_chunk(chunk, sr)
        raw.append(result['chord'])

    # Smooth with median filter (window = 5 frames = 2.5s)
    from scipy.ndimage import median_filter
    # mode vote smoothing
    smoothed = []
    for i, c in enumerate(raw):
        window = raw[max(0, i-2):i+3]
        votes = {}
        for x in window:
            if x:
                votes[x] = votes.get(x, 0) + 1
        smoothed.append(max(votes, key=votes.get) if votes else c)

    # Build timeline — only emit on chord change
    timeline = []
    prev = None
    for i, chord in enumerate(smoothed):
        if chord and chord != prev:
            timeline.append({
                't': round(i * hop_sec, 2),
                'chord': chord
            })
            prev = chord

    duration = float(len(audio) / sr)
    return {
        'key': key_label,
        'timeline': timeline,
        'duration': round(duration, 2)
    }
