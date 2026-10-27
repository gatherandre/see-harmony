"""Test track for the orb's shape layer (ferrofluid, v67).

    python ferro_test_track.py out.wav                      # soft pad, clean piano, rock, soft pad
    python ferro_test_track.py out.wav --song my_song.wav   # adds a 12 s passage of a recording

Sections: soft sustained chord (-34 dBFS RMS), loud clean piano chords (-14 dBFS), [a 12 s passage of a
recording, from 2:00], distorted power chords with drums (-13 dBFS), the soft chord again. Play the file into
See Harmony as its microphone input (or load it in file mode) with the ferrofluid on, and press T to watch the
loudness, beat and harshness meters. The paper's check (Section 7.4.6) used "I Miss You All" for the song passage.
"""
import argparse
import numpy as np
import soundfile as sf

SR = 48000


def t(n):
    return np.arange(int(n * SR)) / SR


def norm(y, db):
    return y / np.sqrt(np.mean(y ** 2)) * 10 ** (db / 20)


def pad(dur, freqs, db):
    x = t(dur)
    y = sum(np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x) for f in freqs)
    return norm(y * np.minimum(1, np.minimum(x / 1.5, (dur - x) / 1.5)), db)


def piano(dur, db, bpm=80):
    x = t(dur); y = np.zeros_like(x); beat = 60 / bpm
    chords = [[130.81, 164.81, 196.0, 261.63], [110.0, 130.81, 164.81, 220.0],
              [87.31, 130.81, 174.61, 220.0], [98.0, 123.47, 146.83, 196.0]]       # C, Am, F, G
    for b in range(int(dur / beat)):
        s = int(b * beat * SR); xx = x[:len(x) - s]
        tone = sum(sum(np.sin(2 * np.pi * f * h * xx * (1 + 0.0004 * h * h)) * 0.55 ** (h - 1) for h in range(1, 7))
                   for f in chords[(b // 4) % 4])
        y[s:] += tone * np.exp(-xx * 1.8) * (1 - np.exp(-xx * 400))
    return norm(y, db)


def rock(dur, db, bpm=120):
    x = t(dur); y = np.zeros_like(x); riff = [82.41, 82.41, 98.0, 110.0]; beat = 60 / bpm
    rng = np.random.default_rng(1)
    for b in range(int(dur / beat)):
        f = riff[(b // 2) % 4]; s = int(b * beat * SR); e = min(len(x), int((b + 1) * beat * SR)); xx = x[:e - s]
        y[s:e] += np.tanh(6 * sum(((f * m * xx) % 1 - 0.5) for m in (1, 1.5, 2))) * np.exp(-xx * 1.2)  # distorted power chord
        k = np.sin(2 * np.pi * (55 + 90 * np.exp(-xx * 30)) * xx) * np.exp(-xx * 12) * 1.6             # kick
        if b % 2 == 1:
            k = k * 0.3 + rng.standard_normal(len(xx)) * np.exp(-xx * 18) * 0.9                       # snare on 2 and 4
        y[s:e] += k
        h = rng.standard_normal(len(xx)) * np.exp(-xx * 60) * 0.25; y[s:e] += h                       # hi-hat on eighths
        hs = int(beat / 2 * SR); y[s + hs:e] += h[:e - s - hs]
    return norm(y, db)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--song')
    a = ap.parse_args()
    parts = [pad(10, [261.63, 329.63, 392.0], -34), piano(12, -14)]
    if a.song:
        y, sr = sf.read(a.song, dtype='float32')
        y = y.mean(1) if y.ndim > 1 else y
        if sr != SR:
            import librosa
            y = librosa.resample(y, orig_sr=sr, target_sr=SR)
        parts.append(y[120 * SR:132 * SR])
    parts += [rock(16, -13), pad(10, [261.63, 329.63, 392.0], -34)]
    out = np.clip(np.concatenate(parts), -0.99, 0.99)
    sf.write(a.out, out, SR, subtype='PCM_16')
    print(f'{a.out}: {len(out) / SR:.0f} s')
