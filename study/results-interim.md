# Elicitation: interim result

**2026-11-11 — 10 participants.** Interim. Collection continues under the
stopping rule in `elicitation-plan.md`; these numbers will change, and are published as they stand
so that the analysis is visible while it happens rather than only once it has finished.

Produced by `primary.py`, which implements the plan and nothing else. Nobody is excluded.

```
10 participants, nobody excluded.  10000 permutations.

chord quality  agreement         p    Holm p   listener colour
major 7th          0.701    0.0089    0.0890      74°
minor              0.636    0.0185    0.1665     247°
diminished         0.444    0.1725    1.0000     271°
augmented          0.371    0.2967    1.0000     270°
sus4               0.322    0.4055    1.0000     159°
minor 7th          0.314    0.4166    1.0000      80°
half-dim           0.312    0.4289    1.0000     256°
dim 7th            0.220    0.6639    1.0000     297°
dominant 7th       0.146    0.8377    1.0000      13°
major              0.099    0.9246    1.0000     200°

agreement is the weighted resultant length: 1.00 = every listener the same hue.

For the qualities that pass, the distance from the designed colour:
  none

participant weights: L183 0.25, L196 0.49, L205 0.30, L287 0.57, L363 0.40, L507 0.40, L588 0.26, L590 0.36, L693 0.19, L706 0.28
```

## What this is and is not

**Nothing passes correction at ten participants.** Major 7th and minor both sit below 0.05 before
the correction for testing ten chord types, and above it after.

At nine participants major 7th did pass, at Holm p = 0.046, and the note written at the time said
one more participant could move it either way. The tenth moved it: the agreement fell from 0.741
to 0.701 and the corrected p from 0.046 to 0.089. That is the ordinary behaviour of a result
sitting on the threshold, and it is recorded here rather than quietly replaced, because a reader
who only ever sees the final number cannot tell the difference between a finding and a coin that
landed well.

Minor moved the other way over the same step, from a raw p of 0.030 to 0.019.

The plan's own power table says that at ten listeners only the strongest effects are visible.
Both candidates look like moderate effects, which the table puts at 59 % detection at ten and
90 % at fifteen. Fifteen to twenty participants should settle both.

Two qualities that looked convincing at two to four participants — minor and dominant 7th — were
named at the time as solid. Dominant 7th is now ninth of ten. They are recorded because they are
the reason the plan was written before the analysis was run.

No additional test has been run on these data beyond the one the plan specifies, and nothing has
been changed in response to a result.

## Why the per-response files are not here

Participants up to this point were told their answers would appear as grouped figures. The
trial-by-trial records are therefore kept out of this repository, and only the group result and
the participant weights — one number each, not anyone's answers — are published. From
11 November the consent wording states that the anonymous responses may be published alongside
the thesis, so later participants' records can be released; the earlier ones need asking first.

## Section 10b: the prediction test, at ten participants

Declared before it was run. Each participant is predicted by a mapping fitted to the other nine,
and compared on the same person with See Harmony's designed table.

```
10 participants, each predicted by a mapping fitted to the other 9.

code     learned error designed error     better
L183               76°           107°    learned
L196              112°           119°    learned
L205               92°            85°   designed
L287               81°            47°   designed
L363               54°            88°    learned
L507               80°           110°    learned
L588               71°            93°    learned
L590              106°            86°   designed
L693               75°            74°   designed
L706               56°            81°    learned
mean               80°            89°

guessing would average 90°

paired Wilcoxon across participants: p = 0.3223  (learned better for 6 of 10)
learned vs chance: 80° against 90° | designed vs chance: 89° against 90°
```

**The outcome is the middle one of the three declared: no difference.** The learned mapping is
9° closer than the designed one, better for six participants of ten, p = 0.32.

The more sobering number is the second column. The designed table — the colours See Harmony uses
today — predicts a listener it has not seen at 89°, where guessing averages 90°.

Both figures have to be read against how noisy the target is. On the chords they heard twice,
these ten listeners' own two answers differ by 63° on average. The thing being predicted is
measured with roughly that much error, so at this sample size neither mapping can be separated
from the other or from chance. This is a working pipeline returning an uninformative answer, not
evidence that a learned mapping does not help.

Two different things would make this test informative, and they are not the same. More
participants sharpens the fitted mapping. More answers per chord type from each person sharpens
the target. The second is a change to the instrument — more repetitions per quality, fewer
qualities, or a longer session — and is worth considering before any comparison study is run.
