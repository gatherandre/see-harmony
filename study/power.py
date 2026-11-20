"""How many listeners does the primary analysis actually need?

Simulates the procedure in the plan: n participants, each contributing one mean direction per
chord quality, weighted by the information measure (weights drawn from the range the four pilot
participants produced), tested against the permutation null with Holm correction across ten
qualities. Reports how often a quality with a given level of true agreement is detected.
"""
import numpy as np
rng = np.random.default_rng(11)
ALPHA = 0.05 / 10          # conservative: the strictest Holm step
SIMS, NULLS = 600, 2000

def wres(dirs, w):
    v = np.sum(w * np.exp(1j * dirs)) / w.sum()
    return float(np.abs(v))

def pairwise_deg(kappa, m=4000):
    d = rng.vonmises(0, kappa, m)
    x = np.abs(np.degrees(d[::2] - d[1::2])) % 360
    return np.median(np.minimum(x, 360 - x))

print('agreement between listeners is shown as the typical angle between two of them;')
print('90 degrees is no agreement at all.  Detection must survive correction for ten chord types.\n')
print('%-26s' % 'listeners needed ->' + ''.join('%7d' % n for n in (8, 10, 12, 15, 20, 25, 30)))
for kappa in (0.8, 1.3, 2.0, 3.0, 5.0):
    row = '%-26s' % ('listeners ~%2.0f%s apart' % (pairwise_deg(kappa), '°'))
    for n in (8, 10, 12, 15, 20, 25, 30):
        w = rng.uniform(0.2, 0.6, (SIMS, n))
        obs = np.array([wres(rng.vonmises(0, kappa, n), w[s]) for s in range(SIMS)])
        null = np.array([wres(rng.uniform(-np.pi, np.pi, n), w[s % SIMS]) for s in range(NULLS)])
        thr = np.quantile(null, 1 - ALPHA)
        row += '%6.0f%%' % (100 * np.mean(obs > thr))
    print(row)
print('\nfor reference, the four pilot participants sit about 25 degrees apart on minor')
print('and about 51 degrees apart on major 7th.')
