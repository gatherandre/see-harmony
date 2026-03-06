import numpy as np
import librosa

NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

CHORD_SUFFIX = {
    'maj':'', 'min':'m', 'dim':'dim', 'aug':'aug',
    'maj7':'maj7', 'min7':'m7', 'dom7':'7', 'dim7':'dim7',
    'm7b5':'m7b5', 'mMaj7':'mMaj7',
    '6':'6', 'm6':'m6',
    'sus2':'sus2', 'sus4':'sus4', '7sus4':'7sus4',
    'add9':'add9',
}

CHORD_TEMPLATES = {
    'maj':    [1,0,0,0,1,0,0,1,0,0,0,0],
    'min':    [1,0,0,1,0,0,0,1,0,0,0,0],
    'dim':    [1,0,0,1,0,0,1,0,0,0,0,0],
    'aug':    [1,0,0,0,1,0,0,0,1,0,0,0],
    'maj7':   [1,0,0,0,1,0,0,1,0,0,0,1],
    'min7':   [1,0,0,1,0,0,0,1,0,0,1,0],
    'dom7':   [1,0,0,0,1,0,0,1,0,0,1,0],
    'dim7':   [1,0,0,1,0,0,1,0,0,1,0,0],
    'm7b5':   [1,0,0,1,0,0,1,0,0,0,1,0],
    'mMaj7':  [1,0,0,1,0,0,0,1,0,0,0,1],
    '6':      [1,0,0,0,1,0,0,1,0,1,0,0],
    'm6':     [1,0,0,1,0,0,0,1,0,1,0,0],
    'sus2':   [1,0,1,0,0,0,0,1,0,0,0,0],
    'sus4':   [1,0,0,0,0,1,0,1,0,0,0,0],
    '7sus4':  [1,0,0,0,0,1,0,1,0,0,1,0],
    'add9':   [1,0,1,0,1,0,0,1,0,0,0,0],
}

COMPLEXITY = {t: max(0, sum(v) - 3) for t, v in CHORD_TEMPLATES.items()}

KK_MAJ = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KK_MIN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])


def detect_key(chroma_mean):
    best, det_key, det_mode = -np.inf, 0, 'maj'
    for r in range(12):
        for mode, prof in [('maj', KK_MAJ), ('min', KK_MIN)]:
            pv = np.roll(prof, r)
            a = chroma_mean - chroma_mean.mean()
            b = pv - pv.mean()
            cor = np.dot(a, b) / (np.sqrt(np.dot(a, a) * np.dot(b, b)) + 1e-10)
            if cor > best:
                best = cor
                det_key = r
                det_mode = mode
    return det_key, det_mode


def chord_label(root, ctype):
    return NOTES[root] + CHORD_SUFFIX.get(ctype, ctype)


def score_chord(ch_norm, root, ctype, bass_root, bass_conf):
    tmpl = np.array(CHORD_TEMPLATES[ctype], dtype=float)
    rolled = np.roll(ch_norm, -root)
    score = float(np.dot(rolled, np.where(tmpl > 0, 2.5, -0.8)))
    if root == bass_root:
        score += bass_conf * 20.0
    score -= COMPLEXITY[ctype] * 0.4
    return score


def _bass_chroma_fft(chunk, sr):
    """Fast bass chroma via FFT — vectorised, no CQT overhead."""
    N = len(chunk)
    fft_mag = np.abs(np.fft.rfft(chunk))
    freqs = np.fft.rfftfreq(N, 1.0 / sr)
    ch_bass = np.zeros(12)
    mask = (freqs >= 55) & (freqs <= 250) & (fft_mag > 0)
    if mask.any():
        bf = freqs[mask]
        bm = fft_mag[mask]
        pcs = (np.round(69 + 12 * np.log2(np.maximum(bf, 1e-9) / 440)).astype(int)) % 12
        np.add.at(ch_bass, pcs, bm * bm)  # power weighting
    ch_bass /= (ch_bass.sum() + 1e-8)
    return ch_bass


def analyze_chunk(audio, sr):
    """Detect chord from a short audio chunk (0.5-3s). Used for real-time mic."""
    if len(audio) < sr * 0.1:
        return {'chord': '', 'confidence': 0.0, 'chroma': [0.0]*12}

    try:
        chroma = librosa.feature.chroma_cqt(
            y=audio, sr=sr, bins_per_octave=36, norm=2,
            fmin=librosa.note_to_hz('C2'))
    except Exception:
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr, n_fft=8192)

    ch = np.mean(chroma, axis=1)
    ch_norm = ch / (ch.sum() + 1e-8)

    ch_bass = _bass_chroma_fft(audio, sr)
    bass_root = int(np.argmax(ch_bass))
    bass_conf = float(ch_bass[bass_root])

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


def analyze_file(audio, sr, win_sec=2.0, hop_sec=0.5):
    """
    Full file analysis — mid-ground optimisation:
    ✓ CQT chroma per window  (accurate — logarithmic frequency resolution)
    ✓ FFT bass detection      (fast — replaces second CQT pass)
    ✗ No full-track HPSS      (this was ~80% of processing time)
    
    Expected: ~30-40s for a 4:35 song on Render free tier.
    """
    import time
    t0 = time.time()

    target_sr = 22050
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    duration = len(audio) / sr
    print(f'[analysis] {duration:.1f}s audio @ {sr}Hz')

    # ── Key detection (STFT over full track — fast + sufficient) ──
    chroma_full = librosa.feature.chroma_stft(y=audio, sr=sr, n_fft=8192)
    ch_global = np.mean(chroma_full, axis=1)
    det_key, det_mode = detect_key(ch_global)
    key_label = NOTES[det_key] + (' min' if det_mode == 'min' else '')
    print(f'[analysis] key={key_label} ({time.time()-t0:.1f}s)')

    # ── Per-window chord detection (CQT chroma — accurate) ───────
    win = int(win_sec * sr)
    hop = int(hop_sec * sr)
    n_frames = max(1, (len(audio) - win) // hop + 1)

    raw = []
    for i in range(n_frames):
        start = i * hop
        chunk = audio[start:start + win]
        if len(chunk) < win:
            chunk = np.pad(chunk, (0, win - len(chunk)))

        # CQT chroma — the accurate path
        try:
            chroma = librosa.feature.chroma_cqt(
                y=chunk, sr=sr, bins_per_octave=36, norm=2,
                fmin=librosa.note_to_hz('C2'))
        except Exception:
            chroma = librosa.feature.chroma_stft(y=chunk, sr=sr, n_fft=8192)

        ch = np.mean(chroma, axis=1)
        ch_norm = ch / (ch.sum() + 1e-8)

        # Bass via FFT (fast)
        ch_bass = _bass_chroma_fft(chunk, sr)
        bass_root = int(np.argmax(ch_bass))
        bass_conf = float(ch_bass[bass_root])

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

        raw.append(chord_label(best_root, best_type))

        if i % 50 == 0 and i > 0:
            elapsed = time.time() - t0
            eta = elapsed / i * (n_frames - i)
            print(f'[analysis] {i}/{n_frames} frames ({elapsed:.1f}s, ~{eta:.0f}s remaining)')

    print(f'[analysis] detection done: {n_frames} frames ({time.time()-t0:.1f}s)')

    # ── Majority vote smoothing (5-frame window) ─────────────────
    smoothed = []
    for i, c in enumerate(raw):
        window = raw[max(0, i-2):i+3]
        votes = {}
        for x in window:
            votes[x] = votes.get(x, 0) + 1
        smoothed.append(max(votes, key=votes.get) if votes else c)

    # ── Timeline (emit on chord change only) ─────────────────────
    timeline = []
    prev = None
    for i, chord in enumerate(smoothed):
        if chord and chord != prev:
            timeline.append({'t': round(i * hop_sec, 2), 'chord': chord})
            prev = chord

    total = time.time() - t0
    print(f'[analysis] DONE: key={key_label}, {len(timeline)} changes, {total:.1f}s')

    return {
        'key': key_label,
        'timeline': timeline,
        'duration': round(duration, 2)
    }
