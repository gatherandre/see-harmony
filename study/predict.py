"""Section 10b: does a mapping learned from listeners predict a listener it has never seen
better than the designed table does?

Leave one participant out, fit the weighted group mapping on the rest, measure how far it
falls from the held-out person's own mean direction for each chord quality, and compare with
the distance from See Harmony's designed colour on the same person.
"""
import json, glob
import numpy as np
from scipy.stats import wilcoxon

QUALS = ['maj', 'min', 'dom7', 'maj7', 'min7', 'hdim7', 'dim7', 'dim', 'aug', 'sus4']
DESIGNED = {'maj': 42, 'maj7': 288, 'sus4': 58, 'dom7': 14, 'min': 235, 'min7': 200,
            'hdim7': 320, 'dim': 348, 'dim7': 355, 'aug': 340}

def cdiff(a, b):
    x = abs(a - b) % 360
    return min(x, 360 - x)

subs = []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    means, Rs = {}, []
    for q in QUALS:
        hs = np.radians([r['H'] for r in d['responses'] if r['quality'] == q])
        if len(hs) == 0: continue
        v = np.mean(np.exp(1j * hs)); means[q] = v / (abs(v) + 1e-12); Rs.append(abs(v))
    spread = 1 - abs(np.mean(list(means.values())))
    subs.append((d['code'], means, float(np.mean(Rs)) * spread))

rows = []
for i, (code, mine, _) in enumerate(subs):
    others = [s for j, s in enumerate(subs) if j != i]
    le, de = [], []
    for q in QUALS:
        if q not in mine: continue
        cols = [(m[q], w) for _, m, w in others if q in m]
        v = sum(w * c for c, w in cols) / sum(w for _, w in cols)
        learned = np.degrees(np.angle(v)) % 360
        truth = np.degrees(np.angle(mine[q])) % 360
        le.append(cdiff(learned, truth)); de.append(cdiff(DESIGNED[q], truth))
    rows.append((code, float(np.mean(le)), float(np.mean(de))))

L = np.array([r[1] for r in rows]); D = np.array([r[2] for r in rows])
print('%d participants, each predicted by a mapping fitted to the other %d.\n' % (len(rows), len(rows) - 1))
print('%-7s %14s %14s %10s' % ('code', 'learned error', 'designed error', 'better'))
for code, l, d in rows:
    print('%-7s %13.0f° %13.0f° %10s' % (code, l, d, 'learned' if l < d else 'designed'))
print('%-7s %13.0f° %13.0f°' % ('mean', L.mean(), D.mean()))
print('\nguessing would average 90°')
stat, p = wilcoxon(L, D)
print('\npaired Wilcoxon across participants: p = %.4f  (learned better for %d of %d)'
      % (p, int((L < D).sum()), len(rows)))
print('learned vs chance: %.0f° against 90° | designed vs chance: %.0f° against 90°'
      % (L.mean(), D.mean()))
