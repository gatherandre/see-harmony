# Elicitation study: interim results

**32 listeners, as of 19 November 2026.** Nobody excluded. Collection closes 30 November
or at 60 participants, whichever comes first (plan, §11).

Aggregate figures only. Individual responses are not published; see
`elicitation/README.md`.

## Hue — the pre-registered analysis (§6, §7)

Weighted circular mean per chord quality, weights = within × spread from each listener's
own answers, permutation null with quality labels shuffled within each participant,
10,000 permutations, Holm correction across the ten qualities.

| chord quality | agreement | Holm p | listeners | designed | apart |
|---|---|---|---|---|---|
| minor | 0.652 | **0.0010** | 249° | 235° | 14° |
| major 7th | 0.590 | **0.0018** | 60° | 288° | **132°** |
| augmented | 0.627 | **0.0018** | 260° | 340° | 80° |
| diminished | 0.595 | **0.0028** | 274° | 348° | 74° |
| major | 0.313 | 1.00 | — | | |
| sus4 | 0.302 | 1.00 | — | | |
| minor 7th | 0.222 | 1.00 | — | | |
| half-dim | 0.188 | 1.00 | — | | |
| dim 7th | 0.112 | 1.00 | — | | |
| dominant 7th | 0.038 | 1.00 | — | | |

Agreement is the weighted resultant length: 1.00 would be every listener on the same hue.

## The within-root null (§13, 15 Nov)

A stricter test. Quality labels are shuffled **within each root**, so each listener's
root-to-hue tendency survives the shuffle and only the quality mapping is destroyed.
Minor, diminished and major 7th survive it. Augmented does not survive it consistently,
and is excluded from the main claim on separate grounds — its three stimuli are one
chord in three voicings.

**The headline is three qualities: minor, diminished, major 7th.**

## The other channels — exploratory (§13, 13 and 19 Nov)

| | hue | lightness | chroma | shape |
|---|---|---|---|---|
| major 7th | ✓ 60° | ✓ 0.75 | ✓ 0.14 | ✓ sharper |
| minor | ✓ 249° | — | — | ✓ 0.36, smoothest |
| diminished | ✓ 274° | — | — | — |
| dim 7th | — | — | — | ✓ sharper |

Major 7th is the only quality that agrees on all four channels. Minor agrees on hue and
shape but not on lightness, which argues against the common claim that minor chords are
heard as dark. Shape runs on the 30 listeners who used the corrected instrument (§3).

## Generalisation (§10b, renamed from "prediction" 19 Nov)

Each listener held out, the group mapping fitted on the other 31, both mappings scored
against that listener's own mean directions.

| | mean error |
|---|---|
| mapping learned from the other listeners | **69°** |
| See Harmony's designed table | 87° |
| guessing | 90° |

Learned closer for 28 of 32; paired Wilcoxon p = 0.0001. The advantage is concentrated
in the qualities where listeners agreed. Where they did not — dominant 7th especially —
the learned mapping is worse than the designed one, which is why a deployed map should
take learned values only where agreement was demonstrated.

## Robustness

- **Equal weights.** Counting every listener equally gives the same four qualities in
  the same order. The weighting is not doing the work.
- **Forty tests.** Four channels × ten qualities corrected as one family rather than
  four: nine of the ten significant results survive. The exception is the shape result
  for diminished 7th (0.0224 → 0.0868). `family40.py`.
- **Training.** 20 listeners report formal training (median 28 years), 12 report none.
  Mean weight 0.327 and 0.318 respectively — formal training does not predict how
  informative a listener's answers are. `split_training.py`.

## Sample

32 listeners, predominantly Brazilian, recruited through the author's own contacts.
23 took it in Portuguese, 9 in English; guitar is by far the most common instrument.
Median session length 5.8 minutes. One reports colour-vision difficulty. This is a convenience sample and every
claim is a claim about these listeners.
