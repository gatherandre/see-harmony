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

## 10a. How many listeners this needs

Simulated on the exact procedure above — weighted circular mean, permutation null, Holm
correction across ten qualities, participant weights drawn from the range the four pilot
participants produced. The table gives the chance of detecting a quality, by how much the
listeners genuinely agree about it. Ninety degrees apart is no agreement at all.

| typical angle between two listeners | 8 | 10 | 12 | 15 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|
| ~26° apart | 96 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % |
| ~35° apart | 83 % | 92 % | 95 % | 100 % | 100 % | 100 % | 100 % |
| ~45° apart | 42 % | 59 % | 82 % | 90 % | 97 % | 100 % | 100 % |
| ~58° apart | 15 % | 19 % | 36 % | 48 % | 65 % | 80 % | 88 % |
| ~75° apart | 5 % | 5 % | 9 % | 10 % | 19 % | 36 % | 42 % |

In the pilot the four participants sat about 25° apart on minor and about 51° apart on major
7th. So **twelve to fifteen listeners is a real study** for qualities where agreement is strong,
and twenty is comfortable for moderate ones. A quality whose listeners sit 75° apart is not
detectable at any realistic sample size, and would not be a usable mapping if it were.

The simulation draws its null from uniform directions, while the real permutation null draws
from each participant's own answers; for a listener who uses a narrow part of the wheel the real
null is narrower and the real test therefore somewhat more conservative than this table.

The 40-participant floor in §9 applies only to the exploratory clustering. It is not a
requirement of the study, and if the sample stops short of it that section is simply not run.

## 10b. Does a mapping learned from listeners predict a listener better than the designed one?

Declared 11 November 2026, before being run. Exploratory, and separate from the question in
§7: that asks whether shared structure exists, this asks whether a mapping built from other
people is *useful* for a person it has never seen.

Leave one participant out. Fit the weighted group mapping of §6 on everyone else, then measure
how far its prediction falls from the held-out person's own mean direction for each chord
quality. Compare, on the same held-out person, with the distance from See Harmony's designed
table. Repeat for every participant; compare the two error distributions with a paired
Wilcoxon signed-rank test across participants.

Three outcomes and what each means:

- **Learned closer than designed.** A mapping taken from listeners predicts a new listener better
  than the one a designer wrote. That is the elicitation claim, in its smallest testable form.
- **No difference.** The designed table is already as good as anything the listeners produce,
  and the argument for learning the mapping has to rest on something other than accuracy.
- **Designed closer than learned.** The designed table beats the listeners' own consensus, which
  would be a genuine finding against the resonance claim and is reported as such.

Both errors are also compared against 90°, the error of guessing, since a learned mapping that
beats the designed one while both are near chance has not established anything.

Run at any sample size and reported with the sample size attached; at ten participants it is a
pilot of the method, not an answer.

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
| 2026-11-11 | §10b added, before running it | A prediction test is a different question from §7 and was worth declaring rather than improvising. |
| 2026-11-11 | §10a added | Sample size was stated without justification; simulated before any group analysis was run. |
| 2026-11-13 | A blank `trainingYears` is coded as **no formal training**, not as missing | The recruiting message told people to leave the field empty if they had none, so blank carries that meaning rather than being a skipped question. The decision was made after the split was known (12 with formal training, 8 without) and is recorded for that reason. |
| 2026-11-13 | §8 wording: the training covariate is *formal* training only | The field asks for years of formal training, so the group coded as having none may include self-taught players who read no notation and took no lessons. Subgroup results are reported as "no formal training", never as "non-musicians" or "untrained". |
| 2026-11-13 | The shape channel's significance test defined, **after** the hue results were known | Section 5 gave the shape weight and section 6 said the same procedure yields group shape values, but no test was specified for a linear variable. The test used: each listener's ten per-quality mean shape values are z-scored within that listener, the weighted mean across listeners is taken per quality, and the null shuffles quality labels within each participant with weights recomputed, Holm across ten -- the section 7 procedure with the circular step replaced. Because it was defined after the hue analysis had been seen, **the shape channel is reported as exploratory**, never as a confirmatory result. |
| 2026-11-13 | Shape is reported on 19 of the 21 listeners | Section 3 already restricted shape to the corrected instrument. L183 and L287 used the earlier version, whose slider had a fixed default. They are excluded from this channel only and remain in every other analysis. Section 4 is unchanged: no participant is excluded from the study. |
| 2026-11-15 | A **within-root null** added as a stricter test of section 7, run alongside it and reported beside it | Prompted by the user's observation, on 15 Nov, that a listener looked attached to the root rather than the chord. Checking it showed the hue of 15 of 23 listeners was organised more strongly by root pitch than by chord quality, and that the stimulus design yields only four distinct root-sets across the ten qualities -- {0,4,8} major / minor 7th / augmented, {1,5,9} minor / half-dim / sus4, {2,6,10} dominant 7th / dim 7th, {3,7,11} major 7th / diminished -- so qualities sharing a set are heard at identical pitches. The new null shuffles quality labels **within each root**, leaving every listener's root-to-hue tendency intact and destroying only the quality mapping. Statistic, weights and Holm correction are unchanged. It was devised after the results were known, so it is reported as a **confirmatory check on the primary analysis, not as a replacement for it**, and both are reported together. |
| 2026-11-15 | The within-root test's limit, stated wherever it is reported | It can only separate a quality from the two or three qualities sharing its root-set, because the design never pairs, say, major 7th with minor at the same pitch. It is a partial control, not a complete one. |
| 2026-11-15 | The root effect is reported as a finding, not suppressed as a nuisance | That most listeners organise hue more strongly by pitch than by chord is a result about this sample and belongs in the write-up, whatever it does to the chord-quality claim. |
| 2026-11-18 | **Augmented is excluded from the main claim**, and reported separately with the reason stated | Prompted by the user asking, on 18 Nov, whether the augmented triad's ambiguity explained its unstable result. Checking it found the opposite of the proposed explanation and a fault in the stimulus design. stimuli.py assigns the three roots of quality q as (5q + step) % 12 for step in (0, 4, 8); stepping the root by 4 semitones is the augmented triad's own interval structure, so its three stimuli are the single pitch-class set {0,4,8} in three voicings. Every other quality receives three distinct pitch-class sets. Listeners therefore heard one augmented chord three times, which is a hidden repeat trial: its within-listener consistency is the highest of the ten qualities (0.67) for that reason, its agreement score on the primary test is inflated, and the within-root control does not apply to it, since the root carries no harmonic information for a symmetric chord. Its movement around the 0.05 line across four consecutive additions is therefore not a marginal effect resolving. study/stimulus_check.py is the check, kept in the repository so the fault is visible in the code. A root step of 1 or 2 semitones would give three distinct augmented triads in any future collection. |
| 2026-11-18 | The user's proposed explanation for augmented is recorded as **not supported**, rather than dropped | That the augmented triad is harmonically unresolved and so draws mixed responses is musically reasonable and was the first hypothesis offered. The data contradicts it: listeners were more consistent with themselves on augmented than on any other quality, and the chord that actually drew mixed responses was sus4 (0.48). The hypothesis is recorded here with its refutation so that it is not quietly re-asked later. |
| 2026-11-19 | Lightness and chroma analysed as channels of their own, **after** the hue results were known | Section 6 said the same procedure gives group values for chroma and lightness, but no test was specified for them. The shape channel's test (recorded 13 Nov) is reused unchanged: each listener's ten per-quality means z-scored within that listener, weighted mean across listeners, labels shuffled within each participant, Holm across ten. Defined after the hue analysis had been seen, so **both channels are exploratory**. At 32 listeners, major 7th is the only quality that agrees on all four channels; minor agrees on hue and shape but not on lightness, which argues against the common claim that minor chords are heard as dark. |
| 2026-11-19 | A **correction across the whole family of 40 tests** added as a robustness check, reported beside the pre-registered correction and not in place of it | Four channels times ten qualities is forty tests of one dataset, and each channel was corrected within itself across ten. A stricter reading treats the family as forty. study/family40.py recomputes every raw p-value from the same nulls and applies one Holm correction across all forty. Nine of the ten results significant at ten survive at forty; the exception is the shape result for diminished 7th (0.0224 at ten, 0.0868 at forty). Minor survives on hue and shape, diminished on hue, and major 7th on all four channels. The pre-registered ten-way correction remains the primary analysis, because a pre-registration is not revised after the data are seen. |
| 2026-11-19 | The leave-one-out test of section 10b renamed from a **prediction** test to a **generalisation** test | Prompted by the user observing that "prediction" implies the designed table was a forecast being scored, when it was an arbitrary starting point adopted so the system had something to build on. The test measures how well each mapping describes a listener it has not seen; the designed table is the incumbent baseline, the one See Harmony currently ships, not a rival hypothesis. The statistic, the procedure and the result are unchanged. |
