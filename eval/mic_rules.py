"""Microphone-mode display rules, simulated offline.

    python gen_set.py test 202 30      # if not generated yet
    python mic_rules.py test           # two-window rule vs the v66.2 rule

Each track is cut into 1 s windows every 0.5 s and analysed as the server's /chord endpoint does
(chord_engine.analyze_window). A display rule turns the window results into the chord shown on screen.
Scores: exact-chord agreement at settled moments (from 1.5 s after each chord change to its end, every
0.1 s), displayed changes per played change, and median lag to the correct chord (before network time).

Optional: python mic_rules.py --audio song.wav --annotation song.json  scores one real recording against a
list of {"t", "chord"} change points (the format saved by the annotation page).
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'server')); sys.path.insert(0, HERE)
import numpy as np
import soundfile as sf
import chord_engine
from common import to_harte

W, HOP = 1.0, 0.5


def windows(y, sr):
    out = []
    for te in np.arange(W, len(y) / sr + 1e-6, HOP):
        r = chord_engine.analyze_window(y[int((te - W) * sr):int(te * sr)], sr)
        out.append((float(te), r['chord'], r.get('top', [])))
    return out


def root(lbl):
    m = re.match(r'[A-G][#b]?', lbl or '')
    return m.group(0) if m else ''


def display(stream, sticky=0.0):
    """Two-window rule. With sticky > 0 (v66.2 uses 0.04), a window still votes for the chord on
    screen when that chord's score is within `sticky` of the window's best (index.html: micVote)."""
    shown, last, tl = '', '', []
    for t, chord, top in stream:
        if not chord:
            continue
        vote = chord
        if sticky and shown and chord != shown:
            sc = dict((l, s) for l, s in top)
            if shown in sc and sc[shown] >= sc.get(chord, max(sc.values())) - sticky:
                vote = shown
        if vote == last and vote != shown:
            shown = vote; tl.append((t, vote))
        last = vote
    return tl


def score(tl, gt):
    ok = tot = 0; lags = []
    ts = [t for t, _ in tl]
    for g in gt:
        for x in np.arange(g['start'] + 1.5, g['end'], 0.1):
            k = np.searchsorted(ts, x, side='right') - 1
            if k >= 0:
                tot += 1; ok += to_harte(tl[k][1].split('/')[0]) == g['harte'].split('/')[0]
        hit = [t for t, c in tl if t >= g['start'] and c == g['label']]
        if hit and hit[0] < g['end']:
            lags.append(hit[0] - g['start'])
    return ok, tot, len(tl), len(gt), lags


def back_and_forth(tl, gt):
    def seg(t):
        return max((k for k, g in enumerate(gt) if g['start'] <= t), default=-1)
    return sum(1 for k in range(2, len(tl)) if tl[k - 2][1] == tl[k][1] and seg(tl[k - 2][0]) == seg(tl[k][0]))


def report(streams, gts):
    for name, sticky in (('two-window rule (v66.1)', 0.0), ('two-window + sticky 0.04 (v66.2)', 0.04)):
        OK = TOT = CH = NR = BF = 0; LAGS = []
        for key, st in streams.items():
            tl = display(st, sticky)
            ok, tot, ch, nr, lags = score(tl, gts[key])
            OK += ok; TOT += tot; CH += ch; NR += nr; LAGS += lags; BF += back_and_forth(tl, gts[key])
        print(f'{name:34s} settled exact {OK / TOT:.3f}  changes/played {CH / NR:.2f}  '
              f'back-and-forth {BF}  median lag {np.median(LAGS):.2f} s')


def mono(path):
    y, sr = sf.read(path, dtype='float32')
    return (y.mean(1) if y.ndim > 1 else y), sr


if __name__ == '__main__':
    if '--audio' in sys.argv:
        y, sr = mono(sys.argv[sys.argv.index('--audio') + 1])
        ann = json.load(open(sys.argv[sys.argv.index('--annotation') + 1]))
        segs = ann['segments'] if isinstance(ann, dict) else ann
        ref = []
        for s in sorted(segs, key=lambda s: s['t']):
            if not ref or ref[-1]['chord'] != s['chord']:
                ref.append(s)
        dur = len(y) / sr
        gt = [dict(start=s['t'], end=(ref[k + 1]['t'] if k + 1 < len(ref) else dur), label=s['chord'],
                   harte=to_harte(s['chord'])) for k, s in enumerate(ref)]
        report({'rec': windows(y, sr)}, {'rec': gt})
    else:
        d = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'test')
        idx = json.load(open(os.path.join(d, 'index.json')))
        streams, gts = {}, {}
        for t in idx:
            y, sr = mono(os.path.join(d, t['name'] + '.wav'))
            streams[t['name']] = windows(y, sr)
            gts[t['name']] = json.load(open(os.path.join(d, t['name'] + '_gt.json')))
        report(streams, gts)
