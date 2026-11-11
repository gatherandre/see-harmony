# Colour elicitation: analysis plan

**Written 11 November 2026.** Recorded before the data were analysed as a set, so that the
analysis is a plan rather than a story told afterwards.

## Honest disclosure of what had been seen

This plan was not written blind. Four pilot participants (L183, L287, L205, L706) had already
been collected and inspected individually when it was written, and two of them changed it:

- L205 produced colour choices at chance (96° between repeats, where 90° is random), which is
  why §4 commits to keeping everyone rather than filtering.
- L706 produced the tightest repeats in the set (15°) while sending more than half his answers
  to the same region of the wheel regardless of what he heard. An earlier draft of this plan
  weighted participants by repeat consistency alone, which would have given him the heaviest
  vote in the study. §5 is the correction.

Those four are included in the analysis and are **not** counted as an independent test of
anything stated here. A plan written after four participants is weaker than one written after
none; it is much stronger than one written after thirty. Anything below that was motivated by
the pilot is marked *pilot-derived* and is to be re-examined, never "confirmed", on data that
includes the pilot.

## 1. Question

Do listeners share a mapping from chord quality to colour, and where does any shared mapping
agree or disagree with the designed mapping See Harmony currently uses?

This is the elicitation stage. It produces a listener-derived mapping. It does not test whether
that mapping is easier to learn — that is the separate comparison study.

## 2. Material and procedure

Thirty synthesised chords: ten chord qualities (major, minor, dominant 7th, major 7th, minor
7th, half-diminished, diminished 7th, diminished, augmented, sus4), each in three keys, one
neutral piano-like timbre, equal loudness, matched register. No chord is ever named on screen.
Order is shuffled per participant; four items from the middle of the run are repeated 14 to 18
trials later. Two non-chord practice items precede the run.

Each response records hue, chroma and lightness in OKLab, a smooth-to-sharp shape value,
response time, and the number of replays.

## 3. Two versions of the instrument

An earlier version (used by L183 and L287) drew its repeated items from the opening four trials
and opened both sliders at a fixed position. The corrected version randomises both slider
starting points per trial, records them, and takes repeats from the middle of the run.

- **Hue** is analysed from both versions.
- **Shape** is analysed from the corrected version only; in the earlier one the slider had a
  default that a third of answers never left.
- **Repeat spread** is reported from the corrected version only.

Version is detected automatically from the presence of the `startL` field.

## 4. Inclusion

**No participant is excluded, for any reason, at any stage.** Not for inconsistency, not for
speed, not for disagreeing with anyone. A participant who answers at chance is evidence about
how widely this capacity is distributed, which is part of the question.

Pre-specified covariates may be used to *describe* subgroups (§8). They are never used to remove
anyone from the primary analysis.

## 5. How much each listener counts

Each participant is weighted by how much information their answers carry, measured from their
own responses alone and never from agreement with anyone else.

For participant *p*:

- `within` — for each quality, the resultant length *R* of that person's hue answers for it;
  averaged over the ten qualities. 1.00 means the same hue every time for a given chord type.
- `spread` — 1 minus the resultant length of the ten per-quality mean directions. 1.00 means
  the ten chord types were sent all over the wheel; 0 means all to the same place.
- `w = within × spread`.

Both terms are necessary. Tight answers that do not distinguish the chord types are a habit, not
a mapping; answers that distinguish the chord types but are not reproducible are noise. The
product is near zero if either fails.

The repeat trials are **not** used as the weight. They are a four-pair estimate, and they are
confounded with how much of the wheel a person uses. They are reported as an independent
validity check: if `w` and the repeat spread disagree strongly across the sample, that is
reported, not resolved quietly.

A parallel weight for the shape channel uses the ratio of between-quality to within-quality
variance of the shape value.

## 6. Primary analysis

For each of the ten qualities, the group mapping is the **weighted circular mean** of the
per-participant mean directions, weighted by `w`. Confidence intervals by bootstrap over
participants (10,000 resamples), resampling whole participants, not responses.

The same procedure gives group values for chroma, lightness and shape.

## 7. Is there a shared mapping at all?

The null is that each participant has a private mapping unrelated to anyone else's. It is tested
by permutation: within each participant, shuffle the chord-quality labels across their responses,
recompute the weighted group resultant length for each quality, and repeat 10,000 times. A
quality counts as showing shared structure if its observed resultant exceeds the 95th percentile
of that null, with Holm correction across the ten qualities.

Only qualities that pass are compared with the designed mapping. **Where listeners do not agree
with each other, the distance from the designed colour is not reported**: averaging scattered
answers can land anywhere, and in the pilot one quality landed 10° from the designed hue purely
by luck while its listeners were 74° apart.

Two pilot-derived observations to re-examine rather than confirm: minor appeared stable and close
to the designed blue; major 7th appeared stable and far from the designed purple.

## 8. Covariates — exploratory

Tested against `w` and against each participant's mapping, and reported as exploratory with no
correction claimed: years of training, main instrument, interface language, self-reported
experience of colour with sound, self-reported colour-vision difficulty, median response time.

The pilot gave no sign that self-reported colour experience predicts anything: of the two
participants who answered "never", one was at chance and one produced the tightest repeats in the
set. That is recorded here so the question is not quietly re-asked until it answers well.

## 9. Structure in disagreement — exploratory

If listeners fall into distinct families rather than scattering around one consensus, averaging
produces a colour belonging to nobody. This is examined only when at least 40 participants have
been collected, on the qualities that passed §7, by clustering the per-participant mean
directions (circular k-means, k = 1…4, selected by silhouette with a permutation baseline).

Reported as exploratory in all cases. Finding two families would be a result about the
programme's central claim — that a mapping can be fitted to a listener rather than imposed on
them — and would need its own confirmatory study, not this one.

## 10. The output

The deliverable is a listener-derived mapping: for each quality that passes §7, a hue, chroma,
lightness and shape with its confidence interval, plus an explicit statement of which qualities
showed no shared mapping and are therefore left to the designer. The honest result may be a
mapping that covers three chord types and declines to cover the other seven.

## 11. Stopping rule

Collection closes on **30 November 2026**, or at 60 participants, whichever comes first. The
date may be changed, but only before the closing analysis is run and the change must be recorded
in §13 with its reason. Collection does not continue because a result is not yet significant.

## 12. What a null result looks like

If no quality passes §7, the finding is that listeners do not share a mapping from chord quality
to colour at a level this method can detect. That is a publishable answer to the question asked,
and it argues against the resonance claim rather than for it. It is reported as plainly as a
positive result would be.

## 13. Deviations

Every departure from this plan is recorded here with its date and reason.

| Date | Change | Reason |
|---|---|---|
| — | — | — |
