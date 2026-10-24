"""Evaluate the chord engine on a generated test set.

    python gen_set.py dev 101 30      # development set (used for tuning)
    python gen_set.py test 202 30     # held-out test set
    python evaluate.py test           # v66 engine
    python evaluate.py test --v65     # also the v65 per-window flow (slow)

Scores are duration-weighted mir_eval recall (root, majmin, sevenths).
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'server')); sys.path.insert(0, HERE)
import numpy as np
import soundfile as sf
import chord_engine
from common import load_gt, timeline_to_intervals, score, aggregate


def vote(raw, k):
    h = k // 2; out = []
    for i in range(len(raw)):
        w = [x for x in raw[max(0, i - h):i + h + 1] if x]; order = []
        for x in w:
            if x not in order:
                order.append(x)
        out.append(max(order, key=lambda x: w.count(x)) if order else raw[i])
    return out


def hold(sm):
    held = [sm[0]]; cur = sm[0]
    for i in range(1, len(sm)):
        if sm[i] == cur:
            held.append(cur); continue
        p = 1 + sum(1 for j in range(i + 1, min(i + 3, len(sm))) if sm[j] == sm[i])
        if p >= 2:
            cur = sm[i]
        held.append(cur)
    return held


def v65_timeline(y, sr, k=9):
    from chord_detector import analyze_chunk
    win, hop = int(3.0 * sr), int(1.0 * sr)
    raw = []
    for i in range(max(1, (len(y) - win) // hop + 1)):
        c = y[i * hop:i * hop + win]
        raw.append(analyze_chunk(np.pad(c, (0, win - len(c))), sr)['chord'])
    tl, prev = [], None
    for i, c in enumerate(hold(vote(raw, k))):
        if c and c != prev:
            tl.append({'t': float(i), 'chord': c}); prev = c
    return tl


if __name__ == '__main__':
    d = sys.argv[1]; with_v65 = '--v65' in sys.argv
    idx = json.load(open(os.path.join(d, 'index.json')))
    res = {'v66': []}; durs = []; t66 = 0.0
    if with_v65:
        res['v65'] = []
    for t in idx:
        y, sr = sf.read(os.path.join(d, t['name'] + '.wav'), dtype='float32')
        ref_iv, ref_lb = load_gt(os.path.join(d, t['name'] + '_gt.json')); dur = ref_iv.max(); durs.append(dur)
        t0 = time.time(); tl = chord_engine.analyze_file(y, sr)['timeline']; t66 += time.time() - t0
        res['v66'].append(score(ref_iv, ref_lb, *timeline_to_intervals(tl, dur)))
        if with_v65:
            res['v65'].append(score(ref_iv, ref_lb, *timeline_to_intervals(v65_timeline(y, sr), dur)))
        print(t['name'], flush=True)
    for k, v in res.items():
        print(k, {m: round(x, 3) for m, x in aggregate(v, durs).items()})
    print('v66 processing time / audio time:', round(t66 / sum(durs), 3))
