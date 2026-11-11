"""Score the chord engine against a composer-annotated real recording.

    python score_real.py annotations/walking-in-the-railroad.json path/to/song.mp3

The recordings themselves are not in this repository (they are the composer's masters);
the annotations are, so the figures in EVALUATION.md can be reproduced from a local copy
of the audio. Prints the three mir_eval recall levels both whole-file and the way the app
runs it (30 s sections with 3 s of leading context), the error modes by share of the song,
the accuracy of the change times, and how loud each chord degree actually is in the signal.
"""
import argparse
import collections
import sys

import numpy as np
import librosa
import mir_eval

_HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
sys.path[:0] = [_HERE, __import__('os').path.join(_HERE, '..', 'server')]
import chord_engine as CE
from common import to_harte, timeline_to_intervals, score

FLAT2SHARP = {'Ab': 'G#', 'Bb': 'A#', 'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#'}


def sectioned(y, sr, dur, sec=30.0, ctx=3.0):
    """The app's own decoding: 30 s sections, each given 3 s of leading context."""
    tl, t0 = [], 0.0
    while t0 < dur - 0.2:
        a, b = max(0.0, t0 - ctx), min(dur, t0 + sec)
        for e in CE.analyze_segment(y[int(a * sr):int(b * sr)], sr)['timeline']:
            t = a + e['t']
            if t >= t0 - 1e-6 or not tl:
                tl.append({'t': max(t, t0), 'chord': e['chord']})
        t0 += sec
    out = []
    for e in sorted(tl, key=lambda x: x['t']):
        if not out or out[-1]['chord'] != e['chord']:
            out.append(e)
    return out


def error_modes(ref_iv, ref_lb, est_iv, est_lb):
    ei, el = mir_eval.util.adjust_intervals(est_iv, est_lb, ref_iv.min(), ref_iv.max(),
                                            mir_eval.chord.NO_CHORD, mir_eval.chord.NO_CHORD)
    iv, rl, eln = mir_eval.util.merge_labeled_intervals(ref_iv, ref_lb, ei, el)
    root_ok = qual_only = 0.0
    cause = collections.Counter()
    for (a, b), r, e in zip(iv, rl, eln):
        d = b - a
        if mir_eval.chord.encode(r)[0] == mir_eval.chord.encode(e)[0]:
            root_ok += d
            if r.split(':')[1] != e.split(':')[1]:
                qual_only += d
                cause[f'right root, wrong quality: {r} -> {e}'] += d
        else:
            cause[f'wrong root: {r} -> {e}'] += d
    tot = sum(b - a for a, b in iv)
    return root_ok / tot, qual_only / tot, [(k, v / tot) for k, v in cause.most_common(8)]


def degree_energy(y, sr, ref):
    """How loud each chord degree is in the treble chroma, relative to the triad notes."""
    midis, A, times = CE._salience(y / (np.max(np.abs(y)) + 1e-9))
    T, _ = CE._chromas(midis, A)
    Tn = T / (T.sum(0, keepdims=True) + 1e-9)
    grp = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in ref:
        i0, i1 = np.searchsorted(times, r['start']), np.searchsorted(times, r['end'])
        if i1 - i0 < 2:
            continue
        name = r['chord']
        rt = name[:2] if len(name) > 1 and name[1] in '#b' else name[:1]
        root = CE.NOTES.index(FLAT2SHARP.get(rt, rt))
        third = 3 if 'm' in name[len(rt):] and not name[len(rt):].startswith('maj') else 4
        seg = Tn[:, i0:i1].mean(1)
        triad = sum(seg[(root + d) % 12] for d in (0, third, 7)) / 3 + 1e-9
        for label, d in (('root', 0), ('3rd', third), ('5th', 7), ('7th', 11 if third == 4 else 10)):
            grp[name][label].append(seg[(root + d) % 12] / triad)
    return grp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('annotation')
    ap.add_argument('audio')
    a = ap.parse_args()

    import json
    ref = json.load(open(a.annotation))
    ref_iv = np.array([[r['start'], r['end']] for r in ref])
    ref_lb = [r.get('harte') or to_harte(r['chord']) for r in ref]
    dur = float(ref_iv[-1][1])

    y, sr = librosa.load(a.audio, sr=CE.SR, mono=True)
    dur = min(dur, len(y) / sr)

    runs = [('whole file', CE.analyze_segment(y, sr)['timeline']),
            ('30 s sections (as the app runs it)', sectioned(y, sr, dur))]
    for name, tl in runs:
        est_iv, est_lb = timeline_to_intervals(tl, dur)
        s = score(ref_iv, ref_lb, est_iv, est_lb)
        print(f'\n== {name}')
        print('  root %.3f  majmin %.3f  sevenths %.3f  seg %.3f   changes %d vs %d ref (%.2f)'
              % (s['root'], s['majmin'], s['sevenths'], s['seg'],
                 s['n_est'], s['n_ref'], s['n_est'] / s['n_ref']))
        root_ok, qual_only, modes = error_modes(ref_iv, ref_lb, est_iv, est_lb)
        print('  right root %.0f%%, of which wrong quality %.0f%% of the song'
              % (100 * root_ok, 100 * qual_only))
        for k, v in modes:
            print('    %5.1f%%  %s' % (100 * v, k))
        rt = [r['start'] for r in ref][1:]
        et = np.array([e['t'] for e in tl])
        near = [float(np.min(np.abs(et - t))) for t in rt]
        print('  change times: %d of %d within 0.5 s (median offset %.2f s)'
              % (sum(1 for x in near if x < 0.5), len(rt), float(np.median(near))))

    print('\n== how loud each chord degree is in the recording (1.00 = as loud as a triad note)')
    print('%-9s %6s %6s %6s %6s' % ('chord', 'root', '3rd', '5th', '7th'))
    grp = degree_energy(y, sr, ref)
    for name, g in sorted(grp.items(), key=lambda kv: -np.mean(kv[1]['7th'])):
        print('%-9s %6.2f %6.2f %6.2f %6.2f'
              % (name, np.mean(g['root']), np.mean(g['3rd']), np.mean(g['5th']), np.mean(g['7th'])))


if __name__ == '__main__':
    main()
