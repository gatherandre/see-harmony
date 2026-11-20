"""Holm correction across the whole family of tests, not one channel at a time.

Four channels (hue, lightness, chroma, shape) x ten qualities = 40 tests of the same data.
Each channel was corrected within itself, across ten. A strict reading says the family is
forty. This recomputes every raw p-value from the same nulls and applies one Holm correction
across all of them, so the question is settled by computation rather than by assertion.

Shape runs on the 30 listeners who used the corrected instrument (plan section 3); hue,
lightness and chroma run on all 32.
"""
import json, glob
import numpy as np

Q = ['maj','min','dom7','maj7','min7','hdim7','dim7','dim','aug','sus4']
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
NPERM = 10000

allsubs, shapesubs = [], []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    lab = np.array([Q.index(r['quality']) for r in d['responses']])
    rec = (lab,
           np.radians(np.array([r['H'] for r in d['responses']])),
           np.array([r['L'] for r in d['responses']], float),
           np.array([r['C'] for r in d['responses']], float),
           np.array([r['spiky'] for r in d['responses']], float))
    allsubs.append(rec)
    if 'startL' in d['responses'][0]:
        shapesubs.append(rec)

# ---- circular channel (hue): statistic and weight exactly as primary.py ----
def circ_stats(lab, hue):
    m = np.zeros(10, dtype=complex); R = []
    for q in range(10):
        s = lab == q
        if s.sum() == 0: m[q] = np.nan; continue
        v = np.mean(np.exp(1j*hue[s])); m[q] = v/(abs(v)+1e-12); R.append(abs(v))
    return m, float(np.mean(R))*(1-abs(np.mean(m[~np.isnan(m)])))

def circ_group(ms, w):
    out = np.zeros(10)
    for q in range(10):
        col = np.array([m[q] for m in ms]); ok = ~np.isnan(col)
        out[q] = abs(np.sum(w[ok]*col[ok])/w[ok].sum())
    return out

# ---- linear channels (L, C, shape): statistic and weight exactly as shape.py ----
def lin_stats(lab, val):
    m = np.full(10, np.nan); wi = []
    for q in range(10):
        s = lab == q
        if s.sum(): m[q] = val[s].mean()
        if s.sum() > 1: wi.append(val[s].var(ddof=1))
    ok = ~np.isnan(m)
    w = 0.0 if (not wi or np.mean(wi) <= 1e-12) else m[ok].var(ddof=1)/np.mean(wi)
    return m, w

def lin_group(ms, w):
    Z = []
    for m in ms:
        ok = ~np.isnan(m); s = m[ok].std(ddof=1); z = np.full(10, np.nan)
        if s > 1e-9: z[ok] = (m[ok]-m[ok].mean())/s
        Z.append(z)
    out = np.zeros(10)
    for q in range(10):
        col = np.array([z[q] for z in Z]); ok = ~np.isnan(col)
        out[q] = abs(np.sum(w[ok]*col[ok])/w[ok].sum()) if w[ok].sum() > 0 else 0.0
    return out

def channel(subs, idx, circular, name):
    rng = np.random.default_rng(2026)
    st = circ_stats if circular else lin_stats
    gp = circ_group if circular else lin_group
    ms, ws = zip(*[st(s[0], s[idx]) for s in subs])
    obs = gp(ms, np.array(ws))
    null = np.zeros((NPERM, 10))
    for i in range(NPERM):
        pm, pw = zip(*[st(rng.permutation(s[0]), s[idx]) for s in subs])
        null[i] = gp(pm, np.array(pw))
    raw = np.array([(1 + (null[:, q] >= obs[q]).sum())/(NPERM+1) for q in range(10)])
    return [(name, Q[q], obs[q], raw[q]) for q in range(10)]

tests = []
tests += channel(allsubs,   1, True,  'hue')
tests += channel(allsubs,   2, False, 'lightness')
tests += channel(allsubs,   3, False, 'chroma')
tests += channel(shapesubs, 4, False, 'shape')

def holm(ps):
    n = len(ps); order = np.argsort(ps); out = np.zeros(n); run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, ps[i]*(n-k))); out[i] = run
    return out

raw = np.array([t[3] for t in tests])
h40 = holm(raw)
h10 = np.zeros(len(tests))
for ch in ('hue','lightness','chroma','shape'):
    idx = [i for i, t in enumerate(tests) if t[0] == ch]
    h10[idx] = holm(raw[idx])

print('%d tests in the family (%d listeners for hue/lightness/chroma, %d for shape)\n'
      % (len(tests), len(allsubs), len(shapesubs)))
print('%-11s %-14s %9s %10s %10s  %s' % ('channel','quality','raw p','Holm /10','Holm /40','verdict'))
rows = sorted(range(len(tests)), key=lambda i: raw[i])
for i in rows[:14]:
    ch, q, o, p = tests[i]
    v = 'survives both' if h40[i] < .05 else ('lost at 40' if h10[i] < .05 else '')
    print('%-11s %-14s %9.4f %10.4f %10.4f  %s' % (ch, NICE[q], p, h10[i], h40[i], v))
print('   ... remaining %d tests all have raw p > %.2f' % (len(tests)-14, raw[rows[14]]))

surv10 = sum(1 for i in range(len(tests)) if h10[i] < .05)
surv40 = sum(1 for i in range(len(tests)) if h40[i] < .05)
print('\nsignificant with each channel corrected separately (10 at a time): %d' % surv10)
print('significant with one correction across the whole family of 40:      %d' % surv40)
lost = [ (tests[i][0], NICE[tests[i][1]]) for i in range(len(tests)) if h10[i] < .05 <= h40[i] ]
print('lost by the stricter correction: %s' % (', '.join('%s/%s' % l for l in lost) if lost else 'none'))
