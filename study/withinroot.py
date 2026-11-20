"""Does chord quality explain hue beyond the root pitch?

The stimulus design gives each quality three roots, but only four distinct root-sets exist
across the ten qualities, so qualities sharing a set are heard at identical pitches. A
listener who colours by pitch alone would therefore give those qualities the same hue.

The primary null (plan section 7) shuffles quality labels freely within a participant, which
destroys any root-to-hue mapping along with the quality mapping. This stricter null shuffles
quality labels WITHIN EACH ROOT, so every listener's root-to-hue tendency is preserved
exactly and the only thing destroyed is the quality mapping. A quality that still stands out
is distinguished from the other qualities heard at the same pitches.

Statistic, weights and Holm correction are unchanged from primary.py.
"""
import json, glob
import numpy as np

QUALS = ['maj','min','dom7','maj7','min7','hdim7','dim7','dim','aug','sus4']
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
DESIGNED = {'maj':42,'maj7':288,'sus4':58,'dom7':14,'min':235,'min7':200,
            'hdim7':320,'dim':348,'dim7':355,'aug':340}
NPERM = 10000
rng = np.random.default_rng(2026)

subs = []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    lab = np.array([QUALS.index(r['quality']) for r in d['responses']])
    root = np.array([r['root'] for r in d['responses']])
    hue = np.radians(np.array([r['H'] for r in d['responses']]))
    # index groups sharing a root, for the within-root shuffle
    groups = [np.where(root == r)[0] for r in np.unique(root)]
    subs.append((d['code'], lab, hue, groups))

def stats(labels, hues):
    means = np.zeros(10, dtype=complex); Rs = []
    for q in range(10):
        m = labels == q
        if m.sum() == 0: means[q] = np.nan; continue
        v = np.mean(np.exp(1j * hues[m])); means[q] = v / (abs(v) + 1e-12); Rs.append(abs(v))
    return means, float(np.mean(Rs)) * (1 - abs(np.mean(means[~np.isnan(means)])))

def group(all_means, w, want_dir=False):
    out = np.zeros(10)
    for q in range(10):
        col = np.array([m[q] for m in all_means]); ok = ~np.isnan(col)
        v = np.sum(w[ok] * col[ok]) / w[ok].sum()
        out[q] = (np.degrees(np.angle(v)) % 360) if want_dir else abs(v)
    return out

def shuffle_within_root(lab, groups):
    out = lab.copy()
    for g in groups:
        out[g] = rng.permutation(lab[g])
    return out

means, ws = [], []
for _, lab, hue, _ in subs:
    m, w = stats(lab, hue); means.append(m); ws.append(w)
ws = np.array(ws)
obs = group(means, ws); dirs = group(means, ws, True)

null = np.zeros((NPERM, 10))
for i in range(NPERM):
    pm, pw = [], []
    for _, lab, hue, groups in subs:
        m, w = stats(shuffle_within_root(lab, groups), hue); pm.append(m); pw.append(w)
    null[i] = group(pm, np.array(pw))

raw = np.array([(1 + (null[:, q] >= obs[q]).sum()) / (NPERM + 1) for q in range(10)])
order = np.argsort(raw); holm = np.zeros(10); run = 0.0
for k, q in enumerate(order):
    run = max(run, min(1.0, raw[q] * (10 - k))); holm[q] = run

# which qualities share each quality's root-set
share = {}
for q, name in enumerate(QUALS):
    rs = {(5 * q + s) % 12 for s in (0, 4, 8)}
    share[name] = [QUALS[p] for p in range(10)
                   if p != q and {(5 * p + s) % 12 for s in (0, 4, 8)} == rs]

print('%d listeners, %d within-root permutations\n' % (len(subs), NPERM))
print('%-14s %9s %8s %8s  %-26s' % ('quality', 'agreement', 'raw p', 'Holm p', 'heard at the same roots as'))
for q in np.argsort(-obs):
    print('%-14s %9.3f %8.4f %8.4f  %-26s%s' % (
        NICE[QUALS[q]], obs[q], raw[q], holm[q],
        ', '.join(NICE[s] for s in share[QUALS[q]]), '  SURVIVES' if holm[q] < .05 else ''))
