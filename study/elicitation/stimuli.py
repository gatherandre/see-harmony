"""Chord stimuli for the elicitation study.

Ten qualities, three roots each, one neutral piano-like timbre. Roots are spread so that
no quality sits systematically higher or lower than another, and every chord is normalised
to the same loudness, so a listener's colour cannot be driven by register or volume.
"""
import json, sys, subprocess
import numpy as np

SR = 22050


def tone(f, dur, rng, amp=1.0):
    """A piano-like tone, deliberately gentler than the evaluation set's.

    A bright harmonic series puts real energy on the major seventh of a plain triad -- the
    fifth's own fifth harmonic is that note -- which would blur the very distinction the
    study asks listeners to make. Nine harmonics with a faster roll-off keep the chords
    musical and keep each quality acoustically distinct."""
    n = int(dur * SR); t = np.arange(n) / SR
    B = 0.0004
    out = np.zeros(n)
    for h in range(1, 10):
        fh = f * h * np.sqrt(1 + B * h * h)
        if fh > SR / 2.2:
            break
        out += (0.62 ** (h - 1)) * np.sin(2 * np.pi * fh * t + rng.uniform(0, 6.28)) * np.exp(-t * (0.9 + 0.5 * h))
    return amp * out * np.minimum(1, t / 0.004)

QUALS = {'maj': [0,4,7], 'min': [0,3,7], 'dom7': [0,4,7,10], 'maj7': [0,4,7,11],
         'min7': [0,3,7,10], 'hdim7': [0,3,6,10], 'dim7': [0,3,6,9], 'dim': [0,3,6],
         'aug': [0,4,8], 'sus4': [0,5,7]}
DUR, ROLL = 2.4, 0.022
rng = np.random.default_rng(7)

def render(root_midi, ivs):
    n = int(DUR * SR); out = np.zeros(n)
    notes = [root_midi + i for i in ivs]
    while max(notes) - min(notes) > 24:
        notes[-1] -= 12
    for k, m in enumerate(sorted(notes)):
        f = 440.0 * 2 ** ((m - 69) / 12)
        v = tone(f, DUR, rng, amp=1.0)
        d = int(k * ROLL * SR)                       # a slight roll, so it sounds played
        out[d:] += v[:n - d] * (0.95 ** k)
    out *= np.minimum(1, (np.arange(n) / SR) / 0.004)
    tail = int(0.12 * SR); out[-tail:] *= np.linspace(1, 0, tail)
    return out / (np.sqrt(np.mean(out ** 2)) + 1e-9) * 0.12      # equal loudness

man = []
for q, (name, ivs) in enumerate(QUALS.items()):
    for j, step in enumerate((0, 4, 8)):
        root = 48 + (q * 5 + step) % 12              # C3..B3, spread across qualities
        y = render(root, ivs)
        sid = 's%02d' % (len(man) + 1)
        raw = f'/root/work/elicit/audio/{sid}.wav'
        import soundfile as sf
        sf.write(raw, np.clip(y, -0.99, 0.99), SR, subtype='PCM_16')
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', raw,
                        '-codec:a', 'libmp3lame', '-b:a', '96k', '-ac', '1',
                        f'/root/work/elicit/audio/{sid}.mp3'], check=True)
        man.append({'id': sid, 'quality': name, 'root': int(root % 12), 'midi': int(root)})
json.dump(man, open('/root/work/elicit/manifest.json', 'w'), indent=0)
print(len(man), 'stimuli')
import collections
print('roots used:', dict(sorted(collections.Counter(m['root'] for m in man).items())))
print('mean midi per quality:', {q: round(np.mean([m['midi'] for m in man if m['quality']==q]),1) for q in QUALS})
