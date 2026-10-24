"""Shared evaluation helpers: label conversion and mir_eval scoring."""
import json
import numpy as np
import mir_eval

SFX2HARTE = {'': 'maj', 'm': 'min', '7': '7', 'maj7': 'maj7', 'm7': 'min7', 'dim': 'dim', 'aug': 'aug',
             'dim7': 'dim7', 'm7b5': 'hdim7', 'mMaj7': 'minmaj7', 'mM7': 'minmaj7', '6': 'maj6', 'm6': 'min6',
             'sus2': 'sus2', 'sus4': 'sus4', 'sus': 'sus4', '7sus4': 'sus4(b7)', 'maj9': 'maj9', 'm9': 'min9',
             '9': '9', '7b9': '7(b9)', '7#9': '7(#9)', 'add9': 'maj(9)', 'madd9': 'min(9)', '11': '11',
             'm11': 'min11', '13': '13', 'maj13': 'maj13', 'm13': 'min13'}


def to_harte(lbl):
    if not lbl or lbl == 'N':
        return 'N'
    root = lbl[:2] if len(lbl) > 1 and lbl[1] in '#b' else lbl[:1]
    return f"{root}:{SFX2HARTE[lbl[len(root):]]}"


def load_gt(path):
    gt = json.load(open(path))
    iv = np.array([[g['start'], g['end']] for g in gt])
    return iv, [g['harte'] for g in gt]


def timeline_to_intervals(tl, dur):
    """tl: list of {'t','chord'} change points."""
    iv, lb = [], []
    for k, e in enumerate(tl):
        end = tl[k + 1]['t'] if k + 1 < len(tl) else dur
        if end > e['t']:
            iv.append([e['t'], end]); lb.append(to_harte(e['chord']))
    return np.array(iv), lb


def score(ref_iv, ref_lb, est_iv, est_lb):
    est_iv, est_lb = mir_eval.util.adjust_intervals(est_iv, est_lb, ref_iv.min(), ref_iv.max(),
                                                    mir_eval.chord.NO_CHORD, mir_eval.chord.NO_CHORD)
    m = mir_eval.chord.evaluate(ref_iv, ref_lb, est_iv, est_lb)
    out = {k: float(m[k]) for k in ['root', 'majmin', 'sevenths', 'seg']}
    out['n_est'] = len(est_lb); out['n_ref'] = len(ref_lb)
    return out


def aggregate(per_track, durations):
    """Duration-weighted mean over tracks."""
    w = np.array(durations)
    keys = ['root', 'majmin', 'sevenths', 'seg']
    agg = {k: float(np.sum([p[k] for p in per_track] * w) / w.sum()) for k in keys}
    agg['changes_ratio'] = float(sum(p['n_est'] for p in per_track) / sum(p['n_ref'] for p in per_track))
    return agg
