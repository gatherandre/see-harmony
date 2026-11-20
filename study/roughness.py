"""Is the shape channel just a dissonance rating?

Roughness of each stimulus computed from its own partials, reconstructed exactly as
stimuli.py synthesises them (9 harmonics, 0.62 roll-off, inharmonicity B=4e-4, per-voice
0.95^k, the octave-drop voicing rule), with each partial weighted by its RMS over the note
so the faster-decaying high harmonics count less. Pairwise roughness is the Plomp-Levelt
curve in Sethares' parameterisation, summed over every pair of partials in the chord, with
each chord's partial amplitudes normalised to unit norm because the stimuli were loudness
matched.
"""
import json
import numpy as np
from scipy import stats as st

SR, DUR = 22050, 2.4
QUALS = {'maj': [0,4,7], 'min': [0,3,7], 'dom7': [0,4,7,10], 'maj7': [0,4,7,11],
         'min7': [0,3,7,10], 'hdim7': [0,3,6,10], 'dim7': [0,3,6,9], 'dim': [0,3,6],
         'aug': [0,4,8], 'sus4': [0,5,7]}
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
B = 0.0004

def partials(root_midi, ivs):
    notes = [root_midi + i for i in ivs]
    while max(notes) - min(notes) > 24:
        notes[-1] -= 12
    fs, as_ = [], []
    for k, m in enumerate(sorted(notes)):
        f0 = 440.0 * 2 ** ((m - 69) / 12)
        for h in range(1, 10):
            fh = f0 * h * np.sqrt(1 + B * h * h)
            if fh > SR / 2.2:
                break
            a0 = (0.62 ** (h - 1)) * (0.95 ** k)
            r = 0.9 + 0.5 * h                       # this harmonic's decay rate
            rms = np.sqrt((1 - np.exp(-2 * r * DUR)) / (2 * r * DUR))
            fs.append(fh); as_.append(a0 * rms)
    a = np.array(as_); return np.array(fs), a / np.linalg.norm(a)

def roughness(fs, amps):
    b1, b2, s1, s2, xs = 3.5, 5.75, 0.0207, 18.96, 0.24
    tot = 0.0
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            fmin, fmax = sorted((fs[i], fs[j]))
            s = xs / (s1 * fmin + s2)
            d = s * (fmax - fmin)
            tot += amps[i] * amps[j] * (np.exp(-b1 * d) - np.exp(-b2 * d))
    return tot

man = json.load(open('/root/work/elicit/manifest.json'))
per_q = {}
for m in man:
    fs, a = partials(m['midi'], QUALS[m['quality']])
    per_q.setdefault(m['quality'], []).append(roughness(fs, a))

# group shape values from the shape analysis (section 5/6 weighting), recomputed here
import glob
Q = list(QUALS)
subs = []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    if 'startL' not in d['responses'][0]: continue
    subs.append((np.array([Q.index(r['quality']) for r in d['responses']]),
                 np.array([r['spiky'] for r in d['responses']], dtype=float)))
means, ws = [], []
for lab, val in subs:
    mq = np.full(10, np.nan); wi = []
    for q in range(10):
        m = lab == q
        if m.sum(): mq[q] = val[m].mean()
        if m.sum() > 1: wi.append(val[m].var(ddof=1))
    ok = ~np.isnan(mq)
    means.append(mq); ws.append(0.0 if not wi else mq[ok].var(ddof=1) / np.mean(wi))
ws = np.array(ws)
shape = np.array([np.sum(ws * np.array([m[q] for m in means])) / ws.sum() for q in range(10)])
rough = np.array([np.mean(per_q[q]) for q in Q])

print('%-14s %10s %10s' % ('quality', 'roughness', 'group shape'))
for i in np.argsort(-rough):
    print('%-14s %10.4f %10.2f' % (NICE[Q[i]], rough[i], shape[i]))

r, pr = st.pearsonr(rough, shape); rs, ps = st.spearmanr(rough, shape)
print('\nacross the ten qualities (n = 10):')
print('  Pearson  r = %+.3f  p = %.4f' % (r, pr))
print('  Spearman rho = %+.3f  p = %.4f' % (rs, ps))
print('  shared variance: %.0f%%' % (100 * r * r))

resid = shape - (np.polyval(np.polyfit(rough, shape, 1), rough))
print('\nwhat roughness does not explain (residual shape, + = sharper than roughness predicts):')
for i in np.argsort(-resid):
    print('  %-14s %+.3f' % (NICE[Q[i]], resid[i]))
