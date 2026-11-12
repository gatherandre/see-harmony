"""The primary analysis, exactly as written in study/elicitation-plan.md.

Weighted circular mean per chord quality, weights = within x spread computed from each
participant's own answers; permutation null with the quality labels shuffled within each
participant (weights recomputed on each permutation, so the null is self-consistent); Holm
correction across the ten qualities. Nobody is excluded.
"""
import json, glob
import numpy as np

QUALS = ['maj', 'min', 'dom7', 'maj7', 'min7', 'hdim7', 'dim7', 'dim', 'aug', 'sus4']
NICE = {'maj': 'major', 'min': 'minor', 'dom7': 'dominant 7th', 'maj7': 'major 7th',
        'min7': 'minor 7th', 'hdim7': 'half-dim', 'dim7': 'dim 7th', 'dim': 'diminished',
        'aug': 'augmented', 'sus4': 'sus4'}
DESIGNED = {'maj': 42, 'maj7': 288, 'sus4': 58, 'dom7': 14, 'min': 235, 'min7': 200,
            'hdim7': 320, 'dim': 348, 'dim7': 355, 'aug': 340}
NPERM = 10000
rng = np.random.default_rng(2026)

subs = []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    subs.append((d['code'],
                 np.array([QUALS.index(r['quality']) for r in d['responses']]),
                 np.radians(np.array([r['H'] for r in d['responses']]))))

def stats(labels, hues):
    """per-quality mean direction (complex, unit), and this participant's weight"""
    means = np.zeros(10, dtype=complex)
    Rs = []
    for q in range(10):
        m = labels == q
        if m.sum() == 0:
            means[q] = np.nan; continue
        v = np.mean(np.exp(1j * hues[m]))
        means[q] = v / (abs(v) + 1e-12)
        Rs.append(abs(v))
    within = float(np.mean(Rs))
    spread = 1 - abs(np.mean(means[~np.isnan(means)]))
    return means, within * spread

def group_R(all_means, w):
    out = np.zeros(10)
    for q in range(10):
        col = np.array([m[q] for m in all_means]); ok = ~np.isnan(col)
        v = np.sum(w[ok] * col[ok]) / w[ok].sum()
        out[q] = abs(v)
    return out

def group_dir(all_means, w):
    out = np.zeros(10)
    for q in range(10):
        col = np.array([m[q] for m in all_means]); ok = ~np.isnan(col)
        v = np.sum(w[ok] * col[ok]) / w[ok].sum()
        out[q] = np.degrees(np.angle(v)) % 360
    return out

obs_means, obs_w = [], []
for code, lab, hue in subs:
    m, w = stats(lab, hue); obs_means.append(m); obs_w.append(w)
obs_w = np.array(obs_w)
obs_R = group_R(obs_means, obs_w)
obs_dir = group_dir(obs_means, obs_w)

null = np.zeros((NPERM, 10))
for it in range(NPERM):
    ms, ws = [], []
    for code, lab, hue in subs:
        m, w = stats(rng.permutation(lab), hue); ms.append(m); ws.append(w)
    null[it] = group_R(ms, np.array(ws))

p_raw = np.array([(1 + np.sum(null[:, q] >= obs_R[q])) / (NPERM + 1) for q in range(10)])
order = np.argsort(p_raw)
holm = np.zeros(10); run = 0.0
for k, q in enumerate(order):
    run = max(run, p_raw[q] * (10 - k))
    holm[q] = min(1.0, run)

def cdiff(a, b):
    x = abs(a - b) % 360
    return min(x, 360 - x)

print('%d participants, nobody excluded.  %d permutations.\n' % (len(subs), NPERM))
print('%-14s %9s %9s %9s   %s' % ('chord quality', 'agreement', 'p', 'Holm p', 'listener colour'))
for q in order:
    star = '  SHARED' if holm[q] < 0.05 else ''
    print('%-14s %9.3f %9.4f %9.4f   %5.0f°%s' % (NICE[QUALS[q]], obs_R[q], p_raw[q], holm[q], obs_dir[q], star))
print('\nagreement is the weighted resultant length: 1.00 = every listener the same hue.')

print('\nFor the qualities that pass, the distance from the designed colour:')
any_pass = False
for q in order:
    if holm[q] < 0.05:
        any_pass = True
        print('  %-14s listeners %5.0f°  designed %5.0f°  apart %4.0f°'
              % (NICE[QUALS[q]], obs_dir[q], DESIGNED[QUALS[q]], cdiff(obs_dir[q], DESIGNED[QUALS[q]])))
if not any_pass:
    print('  none')
print('\nparticipant weights:', ', '.join('%s %.2f' % (c, w) for (c, _, _), w in zip(subs, obs_w)))
