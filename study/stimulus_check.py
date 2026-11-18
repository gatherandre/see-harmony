"""Does every chord quality get three genuinely different chords?

stimuli.py assigns the three roots of quality q as (5q + step) % 12 for step in (0, 4, 8).
Stepping the root by 4 semitones is the augmented triad's own interval structure, so for
the augmented triad -- and only for it -- the three roots produce the same pitch-class set.
Listeners heard one chord three times in different voicings, not three chords.

This script is the check that should have been run before collection started. It is kept in
the repository so the fault is visible in the code and not only in the write-up.
"""
QUALS = {'maj': [0,4,7], 'min': [0,3,7], 'dom7': [0,4,7,10], 'maj7': [0,4,7,11],
         'min7': [0,3,7,10], 'hdim7': [0,3,6,10], 'dim7': [0,3,6,9], 'dim': [0,3,6],
         'aug': [0,4,8], 'sus4': [0,5,7]}
NICE = {'maj':'major','min':'minor','dom7':'dominant 7th','maj7':'major 7th','min7':'minor 7th',
        'hdim7':'half-dim','dim7':'dim 7th','dim':'diminished','aug':'augmented','sus4':'sus4'}
STEPS = (0, 4, 8)

def sets_for(q_index, intervals):
    out = []
    for step in STEPS:
        root = (q_index * 5 + step) % 12
        out.append(frozenset((root + i) % 12 for i in intervals))
    return out

def show(s):
    return '{' + ','.join(str(x) for x in sorted(s)) + '}'

degenerate = []
print('quality          roots        distinct pitch-class sets')
for qi, (name, ivs) in enumerate(QUALS.items()):
    roots = [(qi * 5 + step) % 12 for step in STEPS]
    sets = sets_for(qi, ivs)
    distinct = sorted(set(sets), key=lambda s: sorted(s))
    if len(distinct) < len(STEPS):
        degenerate.append(name)
    print('%-15s %-12s %d   %s%s' % (
        NICE[name], ','.join(str(r) for r in roots), len(distinct),
        ' | '.join(show(s) for s in distinct),
        '   <-- DEGENERATE' if len(distinct) < len(STEPS) else ''))

print()
if degenerate:
    print('Degenerate: ' + ', '.join(NICE[d] for d in degenerate) + '.')
    print('Its three stimuli are one chord in three voicings, so its agreement score is')
    print('inflated by a hidden repeat trial and the within-root control does not apply to it.')
    print('A root step of 1 or 2 semitones instead of 4 would give three distinct chords.')
else:
    print('No quality is degenerate under this root assignment.')
