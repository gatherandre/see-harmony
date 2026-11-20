"""Exploratory (plan section 8): does formal training predict anything?

Blank trainingYears is coded 0: the recruiting message told people to leave it blank
if they had no training. Decision recorded 13 Nov 2026, after the split was known.
"""
import json, glob, sys
import numpy as np

sys.path.insert(0, '/root/work/elicit')
QUALS = ['maj','min','dom7','maj7','min7','hdim7','dim7','dim','aug','sus4']
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
DESIGNED = {'maj':42,'maj7':288,'sus4':58,'dom7':14,'min':235,'min7':200,
            'hdim7':320,'dim':348,'dim7':355,'aug':340}
NPERM = 10000

def load():
    out = []
    for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
        d = json.load(open(f))
        ty = (d.get('background', {}).get('trainingYears') or '').strip()
        yrs = float(ty) if ty.replace('.', '', 1).isdigit() else 0.0
        out.append((d['code'], yrs,
                    np.array([QUALS.index(r['quality']) for r in d['responses']]),
                    np.radians(np.array([r['H'] for r in d['responses']]))))
    return out

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

def run(subs, label):
    rng = np.random.default_rng(2026)
    means, ws = [], []
    for _, _, lab, hue in subs:
        m, w = stats(lab, hue); means.append(m); ws.append(w)
    ws = np.array(ws)
    obs = group(means, ws); dirs = group(means, ws, True)
    null = np.zeros((NPERM, 10))
    for i in range(NPERM):
        pm, pw = [], []
        for _, _, lab, hue in subs:
            m, w = stats(rng.permutation(lab), hue); pm.append(m); pw.append(w)
        null[i] = group(pm, np.array(pw))
    raw = np.array([(1 + (null[:, q] >= obs[q]).sum()) / (NPERM + 1) for q in range(10)])
    order = np.argsort(raw); holm = np.zeros(10); run_max = 0.0
    for k, q in enumerate(order):
        run_max = max(run_max, min(1.0, raw[q] * (10 - k))); holm[q] = run_max
    print('\n== %s  (n = %d) ==' % (label, len(subs)))
    print('%-14s %9s %9s %8s %7s' % ('quality', 'agreement', 'Holm p', 'listeners', 'vs you'))
    for q in np.argsort(-obs):
        d = abs((dirs[q] - DESIGNED[QUALS[q]] + 180) % 360 - 180)
        print('%-14s %9.3f %9.4f %7.0f° %6.0f°%s' % (
            NICE[QUALS[q]], obs[q], holm[q], dirs[q], d, '  SHARED' if holm[q] < .05 else ''))

subs = load()
trained   = [s for s in subs if s[1] > 0]
untrained = [s for s in subs if s[1] == 0]
print('trained %d (median %g yrs) | untrained %d'
      % (len(trained), float(np.median([s[1] for s in trained])), len(untrained)))
print('codes untrained:', [s[0] for s in untrained])

wall = {c: stats(l, h)[1] for c, _, l, h in subs}
tw = [wall[s[0]] for s in trained]; uw = [wall[s[0]] for s in untrained]
print('mean weight — trained %.3f, untrained %.3f' % (np.mean(tw), np.mean(uw)))

run(trained, 'trained only')
run(untrained, 'untrained only')
