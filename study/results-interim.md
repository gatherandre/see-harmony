# Elicitation: interim result

**2026-11-11 — 9 participants.** Interim. Collection continues under the
stopping rule in `elicitation-plan.md`; these numbers will change and are published so that the
analysis is visible as it happens rather than only once it is finished.

Produced by `primary.py`, which implements the plan and nothing else. Nobody is excluded.

```
9 participants, nobody excluded.  10000 permutations.

chord quality  agreement         p    Holm p   listener colour
major 7th          0.741    0.0046    0.0460      79°  SHARED
minor              0.623    0.0295    0.2655     244°
diminished         0.460    0.1658    1.0000     278°
minor 7th          0.383    0.2726    1.0000      84°
augmented          0.336    0.3934    1.0000     270°
sus4               0.329    0.4057    1.0000     150°
half-dim           0.278    0.5348    1.0000     252°
dim 7th            0.218    0.6856    1.0000     283°
major              0.150    0.8276    1.0000     185°
dominant 7th       0.109    0.9122    1.0000      28°

agreement is the weighted resultant length: 1.00 = every listener the same hue.

For the qualities that pass, the distance from the designed colour:
  major 7th      listeners    79°  designed   288°  apart  151°

participant weights: L183 0.25, L196 0.49, L205 0.30, L287 0.57, L363 0.40, L507 0.40, L588 0.26, L590 0.36, L706 0.28
```

## What this is and is not

The one quality that passes correction is the major seventh, at Holm p = 0.046 — barely inside
the line. One more participant could move it either way. At nine people the plan's own power
table says only the strongest effects are visible, so a quality like minor, sitting at 0.62 and
failing correction, may be real and merely not yet detectable.

Two qualities that looked convincing while the sample was two to four people — minor and
dominant 7th — did not survive. Dominant 7th is now the weakest of the ten. They are recorded
here because they are the reason the plan was written before the analysis was run.

No additional test has been run on these data beyond the one the plan specifies.

## Why the per-response files are not here

Participants are told their answers appear as grouped figures. The trial-by-trial records are
therefore kept out of this repository, and only the group result and the participant weights —
one number each, not anyone's answers — are published. Full trial-level data can be released
once participants have been asked, or for participants who take part under the revised wording.
