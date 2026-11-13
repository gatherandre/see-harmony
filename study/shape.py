"""The shape channel, following sections 3, 5, 6 and 7 of the plan.

Section 3: shape is analysed from the corrected instrument only -- in the earlier version
the slider had a fixed default that a third of answers never left.

Section 5, parallel weight: between-quality over within-quality variance of the shape value,
so a listener who moves the slider at random, or barely moves it at all, counts for little.

Section 7, adapted: for hue, agreement is the weighted resultant length of unit vectors. The
linear analogue here removes each listener's own range first (z-score their ten per-quality
means within themselves), then takes the weighted mean across listeners. It is large only
when listeners agree on WHICH WAY a quality departs from their own middle. Null: shuffle the
quality labels within each participant, weights recomputed each time; Holm across ten.
"""
import json, glob
import numpy as np

QUALS = ['maj','min','dom7','maj7','min7','hdim7','dim7','dim','aug','sus4']
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
NPERM = 10000
rng = np.random.default_rng(2026)

subs, skipped = [], []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    if 'startL' not in d['responses'][0]:
        skipped.append(d['code']); continue
    subs.append((d['code'],
                 np.array([QUALS.index(r['quality']) for r in d['responses']]),
                 np.array([r['spiky'] for r in d['responses']], dtype=float)))

def stats(lab, val):
    """per-quality mean shape, and this listener's weight (between / within variance)"""
    means = np.full(10, np.nan); wi = []
    for q in range(10):
        m = lab == q
        if m.sum() == 0: continue
        means[q] = val[m].mean()
        if m.sum() > 1: wi.append(val[m].var(ddof=1))
    ok = ~np.isnan(means)
    between = means[ok].var(ddof=1)
    within = np.mean(wi) if wi else np.nan
    w = 0.0 if (not wi or within <= 1e-9) else float(between / within)
    return means, w

def group(all_means, w):
    """weighted mean of each listener's within-self z-scored per-quality means"""
    Z = []
    for m in all_means:
        ok = ~np.isnan(m); s = m[ok].std(ddof=1)
        z = np.full(10, np.nan)
        if s > 1e-9: z[ok] = (m[ok] - m[ok].mean()) / s
        Z.append(z)
    out = np.zeros(10)
    for q in range(10):
        col = np.array([z[q] for z in Z]); ok = ~np.isnan(col)
        out[q] = abs(np.sum(w[ok] * col[ok]) / w[ok].sum()) if w[ok].sum() > 0 else 0.0
    return out

def signed(all_means, w):
    Z = []
    for m in all_means:
        ok = ~np.isnan(m); s = m[ok].std(ddof=1)
        z = np.full(10, np.nan)
        if s > 1e-9: z[ok] = (m[ok] - m[ok].mean()) / s
        Z.append(z)
    out = np.zeros(10)
    for q in range(10):
        col = np.array([z[q] for z in Z]); ok = ~np.isnan(col)
        out[q] = np.sum(w[ok] * col[ok]) / w[ok].sum()
    return out

obs_means, obs_w = [], []
for _, lab, val in subs:
    m, w = stats(lab, val); obs_means.append(m); obs_w.append(w)
obs_w = np.array(obs_w)
obs = group(obs_means, obs_w)
sgn = signed(obs_means, obs_w)

# raw group mean shape per quality, in slider units, for reporting
raw_val = np.zeros(10)
for q in range(10):
    col = np.array([m[q] for m in obs_means]); ok = ~np.isnan(col)
    raw_val[q] = np.sum(obs_w[ok] * col[ok]) / obs_w[ok].sum()

null = np.zeros((NPERM, 10))
for i in range(NPERM):
    pm, pw = [], []
    for _, lab, val in subs:
        m, w = stats(rng.permutation(lab), val); pm.append(m); pw.append(w)
    null[i] = group(pm, np.array(pw))

raw_p = np.array([(1 + (null[:, q] >= obs[q]).sum()) / (NPERM + 1) for q in range(10)])
order = np.argsort(raw_p); holm = np.zeros(10); run = 0.0
for k, q in enumerate(order):
    run = max(run, min(1.0, raw_p[q] * (10 - k))); holm[q] = run

print('shape channel: %d listeners on the corrected instrument' % len(subs))
print('excluded from THIS channel only (earlier instrument, fixed slider default): %s' % (skipped or 'none'))
print()
print('%-14s %10s %8s %8s   %s' % ('quality', 'agreement', 'raw p', 'Holm p', 'group shape'))
for q in np.argsort(-obs):
    tag = 'sharper' if sgn[q] > 0 else 'smoother'
    print('%-14s %10.3f %8.4f %8.4f   %.2f  (%s than their own middle)%s'
          % (NICE[QUALS[q]], obs[q], raw_p[q], holm[q], raw_val[q], tag,
             '  SHARED' if holm[q] < .05 else ''))
print()
print('listener weights (between/within):',
      ', '.join('%s %.2f' % (c, w) for (c, _, _), w in zip(subs, obs_w)))
