"""Summarise the elicitation responses collected so far.

Hues are circular, so everything here uses circular statistics: the mean direction and
the resultant length R, which is 1 when every answer points the same way and 0 when they
are scattered evenly. Chance agreement between two independent listeners is 90 degrees.
"""
import json, glob, os, sys
import numpy as np

QUALS = ['maj', 'min', 'dom7', 'maj7', 'min7', 'hdim7', 'dim7', 'dim', 'aug', 'sus4']
NICE = {'maj': 'major', 'min': 'minor', 'dom7': 'dominant 7th', 'maj7': 'major 7th',
        'min7': 'minor 7th', 'hdim7': 'half-dim', 'dim7': 'dim 7th', 'dim': 'diminished',
        'aug': 'augmented', 'sus4': 'sus4'}
# See Harmony's designed hues, for comparison only
DESIGNED = {'maj': 42, 'maj7': 288, 'sus4': 58, 'dom7': 14, 'min': 235, 'min7': 200,
            'minmaj7': 210, 'hdim7': 320, 'dim': 348, 'dim7': 355, 'aug': 340}

def cdiff(a, b):
    x = abs(a - b) % 360
    return min(x, 360 - x)

def circ(hs):
    v = np.mean([np.exp(1j * np.radians(h)) for h in hs])
    return np.degrees(np.angle(v)) % 360, abs(v)

subs = []
for f in sorted(glob.glob('/root/work/elicit/data/*.json')):
    d = json.load(open(f))
    d['_file'] = os.path.basename(f)
    d['_fixed'] = 'startL' in d['responses'][0]        # the corrected version records this
    subs.append(d)

print('%d participant%s\n' % (len(subs), '' if len(subs) == 1 else 's'))
print('%-7s %-4s %-5s %-9s %6s %7s %9s' % ('code', 'lang', 'yrs', 'instrument', 'mins', 'repeat', 'version'))
for d in subs:
    mins = (np.datetime64(d['finished'][:19]) - np.datetime64(d['started'][:19])).astype(int) / 60
    print('%-7s %-4s %-5s %-9s %6.1f %6s° %9s' % (
        d['code'], d['lang'], d['background']['trainingYears'], d['background']['instrument'][:9],
        mins, d['repeatHueSpread'], 'fixed' if d['_fixed'] else 'original'))
print('\nthe repeat figure is only meaningful on the fixed version; before it, the repeated')
print('items were the opening trials, when people are still learning the controls\n')

print('=' * 78)
print('HUE BY CHORD QUALITY, PER PARTICIPANT   (R = how tightly that person agrees with themselves)')
print('%-14s' % '' + ''.join('%-22s' % ('  ' + d['code']) for d in subs) + 'designed')
for q in QUALS:
    row = '%-14s' % NICE[q]
    for d in subs:
        hs = [r['H'] for r in d['responses'] if r['quality'] == q]
        if hs:
            m, R = circ(hs)
            row += '%-22s' % ('  %5.0f°  R=%.2f  n=%d' % (m, R, len(hs)))
        else:
            row += '%-22s' % '  —'
    row += '%5.0f°' % DESIGNED[q]
    print(row)

if len(subs) >= 2:
    print('\n' + '=' * 78)
    print('DO THEY AGREE WITH EACH OTHER?   (90° apart = no better than chance)')
    print('%-14s %12s %14s' % ('quality', 'between them', 'vs. designed'))
    gaps, dgaps = [], []
    for q in QUALS:
        ms = []
        for d in subs:
            hs = [r['H'] for r in d['responses'] if r['quality'] == q]
            if hs: ms.append(circ(hs)[0])
        if len(ms) < 2: continue
        pair = np.mean([cdiff(ms[i], ms[j]) for i in range(len(ms)) for j in range(i + 1, len(ms))])
        grp = circ(ms)[0]
        dg = cdiff(grp, DESIGNED[q])
        gaps.append(pair); dgaps.append(dg)
        flag = '  <- agree' if pair < 40 else ('  <- scattered' if pair > 75 else '')
        print('%-14s %11.0f° %13.0f°%s' % (NICE[q], pair, dg, flag))
    print('%-14s %11.0f° %13.0f°   (mean)' % ('', np.mean(gaps), np.mean(dgaps)))

print('\n' + '=' * 78)
print('SHAPE BY CHORD QUALITY   (0 = round, 1 = sharp)')
print('%-14s' % '' + ''.join('%-14s' % ('  ' + d['code']) for d in subs))
for q in QUALS:
    row = '%-14s' % NICE[q]
    for d in subs:
        sp = [r['spiky'] for r in d['responses'] if r['quality'] == q]
        row += '%-14s' % ('  %.2f ±%.2f' % (np.mean(sp), np.std(sp)) if sp else '  —')
    print(row)

print('\n' + '=' * 78)
print('DID THE FIX WORK?  (only the corrected version records where each slider started)')
for d in subs:
    if not d['_fixed']:
        print('  %-6s original version \u2014 no check possible' % d['code']); continue
    sp = [(r['startSpiky'], r['spiky']) for r in d['responses']]
    ll = [(r['startL'], r['L']) for r in d['responses']]
    rs = np.corrcoef([a for a, b in sp], [b for a, b in sp])[0, 1]
    rl = np.corrcoef([a for a, b in ll], [b for a, b in ll])[0, 1]
    stuck = sum(1 for a, b in sp if abs(a - b) < 0.03)
    print('  %-6s shape vs its random start r=%+.2f | lightness vs its start r=%+.2f | %d of %d answers left untouched'
          % (d['code'], rs, rl, stuck, len(sp)))
print('  r near 0 means the starting position did not drag the answer')

print('\n' + '=' * 78)
print('SELF-CONSISTENCY vs WHAT THEY REPORTED ABOUT THEMSELVES')
print('%-7s %-11s %-9s %8s %8s %8s %9s' % ('code', 'colour w/ sound', 'version', 'repeat',
      'within', 'spread', 'useful'))
for d in subs:
    Rs, means = [], []
    for q in QUALS:
        hs = [r['H'] for r in d['responses'] if r['quality'] == q]
        if len(hs) > 1:
            m, R = circ(hs); Rs.append(R); means.append(m)
    within = float(np.mean(Rs))
    # How far apart this person puts the different chord types. Someone who answers blue
    # to everything scores a perfect repeat and tells you nothing, so consistency alone
    # is not a measure of how much a listener contributes.
    spread = 1 - circ(means)[1]
    print('%-7s %-11s %-9s %7s\u00b0 %8.2f %8.2f %9.2f' % (d['code'], d['background']['colourWithSound'],
          'fixed' if d['_fixed'] else 'original', d['repeatHueSpread'], within, spread, within * spread))
print('  repeat: 90\u00b0 is chance.  within: 1.00 = the same hue every time for a given chord type.')
print('  spread: 1.00 = the ten chord types sent all over the wheel, 0 = all to the same place.')
print('  useful = within x spread: tight answers that also distinguish the chord types.')
