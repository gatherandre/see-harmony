"""Broader synthetic chord test set with exact ground truth.

Varies: key (all 12 roots, major and minor), progression (random functional
progressions incl. secondary dominants), chord duration (2-4 s, irregular),
timbre (plucked string, piano-like, sustained pad), playing style (strum,
fingerpicked arpeggio, block), voicing (close, open, ~12% inversions),
melody on top (half the tracks), background noise (some tracks).

Two disjoint seeds -> dev set (for tuning) and test set (held out).
Usage: python gen_set.py OUTDIR SEED N
"""
import json, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import lfilter

SR = 22050
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
QUAL = {'maj': [0, 4, 7], 'min': [0, 3, 7], '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10], 'hdim7': [0, 3, 6, 10], 'dim7': [0, 3, 6, 9], 'dim': [0, 3, 6],
        'aug': [0, 4, 8], 'sus4': [0, 5, 7]}
LABEL = {'maj': '', 'min': 'm', '7': '7', 'maj7': 'maj7', 'min7': 'm7', 'hdim7': 'm7b5',
         'dim7': 'dim7', 'dim': 'dim', 'aug': 'aug', 'sus4': 'sus4'}

MAJ_DEG = [(0, ['maj', 'maj7']), (2, ['min', 'min7']), (4, ['min', 'min7']), (5, ['maj', 'maj7']),
           (7, ['maj', '7']), (9, ['min', 'min7']), (11, ['hdim7', 'dim'])]
MIN_DEG = [(0, ['min', 'min7']), (2, ['hdim7', 'dim']), (3, ['maj', 'maj7']), (5, ['min', 'min7']),
           (7, ['7', 'maj']), (8, ['maj', 'maj7']), (10, ['maj', '7'])]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ks(f, dur, rng, amp=1.0, bright=0.6, decay_s=1.8):
    n = int(dur * SR); period = max(2, int(round(SR / f)))
    exc = rng.uniform(-1, 1, period)
    k = max(1, int(3 * (1 - bright)) + 1)
    exc = np.convolve(exc, np.ones(k) / k, mode='same')
    # Karplus-Strong as an IIR comb with averaging lowpass: y[n] = x[n] + d*0.5*(y[n-P] + y[n-P-1])
    x = np.zeros(n); x[:period] = exc
    a = np.zeros(period + 2); a[0] = 1; a[period] = -0.498; a[period + 1] = -0.498
    y = lfilter([1.0], a, x)
    return amp * y * np.exp(-np.arange(n) / (SR * decay_s))


def piano(f, dur, rng, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    B = 0.0004  # inharmonicity
    out = np.zeros(n)
    for h in range(1, 12):
        fh = f * h * np.sqrt(1 + B * h * h)
        if fh > SR / 2.2:
            break
        out += (0.8 ** (h - 1)) * np.sin(2 * np.pi * fh * t + rng.uniform(0, 6.28)) * np.exp(-t * (0.9 + 0.35 * h))
    att = np.minimum(1, t / 0.004)
    return amp * out * att


def pad(f, dur, rng, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    out = sum((0.55 ** (h - 1)) * np.sin(2 * np.pi * f * h * t * (1 + 0.0015 * rng.normal())) for h in range(1, 7))
    env = np.minimum(1, t / 0.08) * np.minimum(1, np.maximum(0, (dur - t)) / 0.12)
    return amp * out * env


def voicing(root, q, style, rng, inversion=False):
    ivs = QUAL[q]
    bass_pc = (root + (ivs[1] if inversion else 0)) % 12
    bass = 40 + ((bass_pc - 4) % 12)                    # E2..D#3
    if style == 'close':
        base = 52 + ((root - 4) % 12)                   # E3..D#4 region
        tones = [base + iv for iv in ivs]
        if len(ivs) == 3:
            tones.append(base + 12)
    else:                                               # open / drop voicing
        base = 52 + ((root - 4) % 12)
        tones = [base + ivs[0] + 12 if len(ivs) > 3 else base + 12] + \
                [base + iv + (12 if k % 2 else 0) for k, iv in enumerate(ivs[1:])]
    return bass, sorted(set(tones))


def progression(rng, n):
    key = int(rng.integers(12)); mode = 'maj' if rng.random() < 0.6 else 'min'
    deg = MAJ_DEG if mode == 'maj' else MIN_DEG
    out = []
    for i in range(n):
        r = rng.random()
        if r < 0.10:                                     # secondary dominant
            tgt = deg[int(rng.integers(1, 6))][0]
            out.append(((key + tgt + 7) % 12, '7'))
        elif r < 0.14:
            out.append(((key + int(rng.integers(12))) % 12, str(rng.choice(['dim7', 'aug', 'sus4']))))
        else:
            d, qs = deg[int(rng.integers(len(deg)))]
            out.append(((key + d) % 12, str(rng.choice(qs))))
        if i and out[-1] == out[-2]:
            out[-1] = ((out[-1][0] + 5) % 12, out[-1][1])
    return key, mode, out


def render_track(rng, n_chords):
    timbre = str(rng.choice(['pluck', 'piano', 'pad']))
    play = str(rng.choice(['strum', 'arpeggio', 'block'])) if timbre != 'pad' else 'block'
    vstyle = str(rng.choice(['close', 'open']))
    melody = rng.random() < 0.5
    noise_db = float(rng.choice([-99, -99, -40, -30]))
    key, mode, prog = progression(rng, n_chords)
    durs = rng.choice([2.0, 3.0, 4.0, 4.0], size=n_chords).astype(float)
    total = float(durs.sum()) + 1.5
    y = np.zeros(int(total * SR))
    gt, t0 = [], 0.0

    def add(seg, at):
        a = max(0, int(at * SR)); b = min(len(y), a + len(seg))
        if a < len(y):
            y[a:b] += seg[:b - a]

    def note(m, dur, amp):
        f = midi_hz(m)
        if timbre == 'pluck':
            return ks(f, dur, rng, amp, bright=float(rng.uniform(0.45, 0.8)))
        if timbre == 'piano':
            return piano(f, dur, rng, amp)
        return pad(f, dur, rng, amp)

    for (root, q), d in zip(prog, durs):
        inv = (q in ('maj', 'min')) and rng.random() < 0.12
        bass, tones = voicing(root, q, vstyle, rng, inv)
        lbl = NOTES[root] + LABEL[q]
        harte = f"{NOTES[root]}:{q}" + (f"/{'3' if q=='maj' else 'b3'}" if inv else '')
        gt.append({'start': t0, 'end': t0 + d, 'harte': harte, 'label': lbl, 'quality': q, 'inversion': bool(inv)})
        if play == 'block':
            add(note(bass, d + 0.3, 0.9), t0)
            for m in tones:
                add(note(m, d + 0.3, 0.5), t0 + rng.normal(0, 0.004))
        elif play == 'strum':
            per = float(rng.choice([1.0, 0.5]))
            for s in np.arange(0, d - 1e-6, per):
                st = t0 + s + rng.normal(0, 0.01)
                for k, m in enumerate([bass] + tones):
                    add(note(m, 1.4, (0.9 if k == 0 else 0.55) * rng.uniform(0.8, 1.0)), st + k * 0.012)
        else:                                            # fingerpicked arpeggio, bass on the beat
            step = 0.25; seq = tones + tones[-2:0:-1] if len(tones) > 2 else tones
            add(note(bass, d, 0.9), t0)
            for j, s in enumerate(np.arange(step, d - 1e-6, step)):
                add(note(seq[j % len(seq)], 1.2, 0.5 * rng.uniform(0.8, 1.0)), t0 + s)
        if melody:
            pcs = QUAL[q] + [2, 5, 9]
            nn = int(d / 0.5)
            for j in range(nn):
                m = 72 + ((root + pcs[int(rng.integers(len(pcs)))]) % 12)
                f = midi_hz(m); dd = 0.5; n = int(dd * SR); t = np.arange(n) / SR
                ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))) / SR
                tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
                env = np.minimum(1, t / 0.03) * np.minimum(1, (dd - t) / 0.05)
                add(0.3 * tone * env, t0 + j * dd)
        t0 += d
    y /= np.max(np.abs(y)) + 1e-9
    if noise_db > -90:
        y += rng.normal(0, 10 ** (noise_db / 20), len(y))
    y = 0.9 * y / np.max(np.abs(y))
    meta = {'key': NOTES[key] + ('' if mode == 'maj' else 'm'), 'timbre': timbre, 'play': play, 'voicing': vstyle,
            'melody': bool(melody), 'noise_db': noise_db, 'duration': t0}
    return y.astype(np.float32), gt, meta


if __name__ == '__main__':
    out, seed, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(seed)
    index = []
    for i in range(n):
        y, gt, meta = render_track(rng, int(rng.integers(10, 15)))
        name = f'trk{i:02d}'
        sf.write(f'{out}/{name}.wav', y, SR)
        json.dump(gt, open(f'{out}/{name}_gt.json', 'w'))
        index.append({'name': name, **meta})
    json.dump(index, open(f'{out}/index.json', 'w'), indent=1)
    print(out, n, 'tracks')
