"""Score the chord engine on GuitarSet (Xi et al., ISMIR 2018; CC BY 4.0).

    python score_guitarset.py <annotation dir> <audio dir> [--players 00,01,02] [--layer both]

GuitarSet is the counterweight to the composer-annotated songs: those are almost
entirely seventh chords, while GuitarSet's lead sheets are 87 % plain triads. A change
that merely makes the engine readier to call a seventh gains on one and loses on the
other, so the two together pin the trade-off down.

Two chord layers are annotated per excerpt and both are reported, because the truth sits
between them: `instructed` is the lead sheet the player was given (it understates what was
played — a jazz player handed "Eb" plays Ebmaj7), and `performed` is a semi-automatic
transcription of what was actually played, verified by hand (175 distinct chord types, only
64 % of them expressible in the engine's ten-type vocabulary; mir_eval excludes the rest at
the levels where they are out of gamut, and the comparable share is reported).

Only the 180 `comp` excerpts are scored. The `solo` excerpts are monophonic improvisation
over the same progressions, where there is no chord in the signal to detect.
"""
import argparse
import collections
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import librosa
import mir_eval

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_HERE, os.path.join(_HERE, '..', 'server')]
import chord_engine as CE
from common import timeline_to_intervals

LAYERS = ('instructed', 'performed')


def chord_layers(jams_path):
    d = json.load(open(jams_path))
    anns = [a for a in d['annotations'] if a.get('namespace') == 'chord']
    out = {}
    for name, a in zip(LAYERS, anns):
        iv, lb = [], []
        for e in a['data']:
            if e['duration'] <= 0:
                continue
            iv.append([e['time'], e['time'] + e['duration']]); lb.append(e['value'])
        out[name] = (np.array(iv), lb)
    return out, float(d['file_metadata']['duration'])


def comparable(ref_lb, est_lb, iv, level):
    """Share of the scored time whose reference label mir_eval can compare at this level."""
    cmp_fn = {'root': mir_eval.chord.root, 'majmin': mir_eval.chord.majmin,
              'sevenths': mir_eval.chord.sevenths}[level]
    s = cmp_fn(ref_lb, est_lb)
    w = np.array([b - a for a, b in iv])
    return float(w[s >= 0].sum() / max(w.sum(), 1e-9))


def one(args):
    jams_path, audio_path = args
    layers, dur = chord_layers(jams_path)
    y, sr = librosa.load(audio_path, sr=CE.SR, mono=True)
    tl = CE.analyze_segment(y, sr)['timeline']
    est_iv, est_lb = timeline_to_intervals(tl, min(dur, len(y) / sr))
    res = {'file': os.path.basename(jams_path), 'dur': dur, 'n_est': len(est_lb)}
    for name, (ref_iv, ref_lb) in layers.items():
        if not len(ref_iv):
            continue
        ei, el = mir_eval.util.adjust_intervals(est_iv, est_lb, ref_iv.min(), ref_iv.max(),
                                                mir_eval.chord.NO_CHORD, mir_eval.chord.NO_CHORD)
        iv, rl, eln = mir_eval.util.merge_labeled_intervals(ref_iv, ref_lb, ei, el)
        m = mir_eval.chord.evaluate(ref_iv, ref_lb, ei, el)
        res[name] = {k: float(m[k]) for k in ('root', 'majmin', 'sevenths', 'seg')}
        res[name]['n_ref'] = len(ref_lb)
        for lev in ('majmin', 'sevenths'):
            res[name]['cmp_' + lev] = comparable(rl, eln, iv, lev)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('annotations'); ap.add_argument('audio')
    ap.add_argument('--players', default='00,01,02,03,04,05')
    ap.add_argument('--out')
    a = ap.parse_args()
    keep = set(a.players.split(','))

    jobs = []
    for j in sorted(glob.glob(os.path.join(a.annotations, '*_comp.jams'))):
        b = os.path.basename(j)[:-5]
        if b[:2] not in keep:
            continue
        cands = [os.path.join(a.audio, b + s) for s in ('_mic.wav', '.wav')]
        cands += glob.glob(os.path.join(a.audio, '**', b + '_mic.wav'), recursive=True)
        audio = next((c for c in cands if os.path.exists(c)), None)
        if audio:
            jobs.append((j, audio))
    print(f'{len(jobs)} comping excerpts, players {sorted(keep)}', flush=True)
    if not jobs:
        sys.exit('no audio found next to the annotations')

    rows = []
    with ProcessPoolExecutor(max_workers=max(1, os.cpu_count())) as ex:
        for i, r in enumerate(ex.map(one, jobs), 1):
            rows.append(r)
            if i % 20 == 0:
                print(f'  {i}/{len(jobs)}', flush=True)

    w = np.array([r['dur'] for r in rows])
    print(f'\n{len(rows)} excerpts, {w.sum()/60:.0f} min of comping\n')
    for name in LAYERS:
        have = [r for r in rows if name in r]
        if not have:
            continue
        ww = np.array([r['dur'] for r in have])
        agg = {k: float(np.sum([r[name][k] for r in have] * ww) / ww.sum())
               for k in ('root', 'majmin', 'sevenths', 'seg', 'cmp_majmin', 'cmp_sevenths')}
        ratio = sum(r['n_est'] for r in have) / sum(r[name]['n_ref'] for r in have)
        print(f'== {name}')
        print('   root %.3f  majmin %.3f  sevenths %.3f  seg %.3f   changes %.2f x reference'
              % (agg['root'], agg['majmin'], agg['sevenths'], agg['seg'], ratio))
        print('   comparable share of time: majmin %.0f%%, sevenths %.0f%%'
              % (100 * agg['cmp_majmin'], 100 * agg['cmp_sevenths']))
        by = collections.defaultdict(list)
        for r in have:
            by[r['file'].split('_')[1][:-1].rstrip('0123456789')].append(r)
        print('   by style:', '  '.join(
            '%s %.2f' % (st, float(np.sum([x[name]['sevenths'] for x in v] * np.array([x['dur'] for x in v]))
                                   / sum(x['dur'] for x in v))) for st, v in sorted(by.items())))
    if a.out:
        json.dump(rows, open(a.out, 'w'))
        print('\nper-excerpt results ->', a.out)


if __name__ == '__main__':
    main()
