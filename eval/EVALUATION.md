# See Harmony v66 — chord engine evaluation

## Test material

`gen_set.py` synthesises tracks whose chords are known exactly:

- keys: all 12, major (60 %) and minor; functional progressions, ~10 % secondary dominants, a few diminished-seventh, augmented and suspended chords
- chord types: major, minor, dominant 7th, major 7th, minor 7th, half-diminished, diminished, diminished 7th, augmented, sus4
- chord lengths 2–4 s; ~12 % of major/minor chords in first inversion
- timbres: plucked string (Karplus–Strong), piano-like (inharmonic decaying partials), sustained pad
- playing: strummed, fingerpicked arpeggio, block chords; close and open voicings
- half the tracks have a sung-style melody on top; some have background noise

Two disjoint sets of 30 tracks: **dev** (seed 101, 18 min), used for every design choice and parameter, and **test** (seed 202, 20 min), scored once at the end.

Scoring: duration-weighted recall with `mir_eval` at three levels — root, major/minor, and sevenths (full chord type).

## File mode (held-out test set)

| | Root | Major/minor | Sevenths | Changes / true changes | Time per audio second |
|---|---|---|---|---|---|
| v65 (per-window detector, 9-window vote) | 0.579 | 0.496 | 0.315 | 0.59 | ~0.3 s |
| v65 with a 3-window vote | 0.731 | 0.643 | 0.427 | 0.78 | ~0.3 s |
| **v66 engine** | **0.926** | **0.885** | **0.811** | **1.05** | **0.061 s** |

v66 at the sevenths level, by condition: pad 0.88, piano 0.90, plucked 0.65; arpeggio 0.88, block 0.79, strum 0.81.

Dev set (for reference): v65 0.525 / 0.445 / 0.273, v66 0.916 / 0.884 / 0.793.

The browser's section-by-section analysis (30 s sections with 3 s context) gives the same scores as analysing each file in one piece (difference ≤ 0.002 on four test tracks run through the live app).

## Microphone mode (dev set, 15 tracks)

A 1 s window every 0.5 s; "settled" = from 1.5 s after each chord change to the end of the chord.

| Display rule | Settled exact-chord accuracy | Changes / true changes | Median lag |
|---|---|---|---|
| Show each result immediately | 0.79 | 2.19 | 1.0 s |
| **Change when two consecutive windows agree (used)** | **0.78** | **1.07–1.11** | **1.5 s** |
| Decaying evidence accumulation (best setting) | 0.78 | 1.47 | 1.0 s |

Lag excludes network time (≈0.2 s locally; measured ≈0.85 s per request on the free Render host).

### v66.1: lighter analysis for microphone windows

Harmonic–percussive separation took about half of each 1 s window's computing time. Options compared (two-window rule):

| Separation in mic windows | Dev: settled exact-chord | Real recording*: settled agreement | Roots (real) | Time per window (local) |
|---|---|---|---|---|
| Full (v66) | 0.775 | 90 % | 98 % | 95 ms |
| **Lighter: n_fft 1024, kernel 13 (v66.1)** | **0.768** | **89 %** | **98 %** | **67 ms** |
| None | 0.766 | 82 % | 98 % | 50 ms |

\*"I Miss You All" (4:36, some percussion), compared with the file-mode timeline at moments ≥2.5 s after a chord change. Skipping the separation costs little on the drum-free synthetic set but 8 points on real music, so the lighter version is used. File mode is unchanged.

Also tested and rejected: letting a single high-confidence window change the chord (no reduction in median lag, more flicker).

### v66.2: steadier display of a chord's quality

On a real recording the two-window rule flickered between a chord and its seventh (C ↔ Cmaj7, Em ↔ Em7): 82 displayed changes for 42 played chords, 13 of them flips away from a chord and back again within the same played chord. The synthetic sets barely show this.

Rule chosen (`index.html`: `micVote`; offline: `mic_rules.py`): a window still votes for the chord on screen when that chord's score is within 0.04 of the window's best (scores from the top-8 list `/chord` returns); then the two-window rule as before. The client changed; the server did not.

The criterion was fixed before looking at held-out data: fewest changes on the first half of "I Miss You All", with exact-chord accuracy down by at most 2 points there and on the dev set. Candidates: stricter agreement for same-root changes (3 or 4 windows), this stickiness (0.02–0.15, same-root only or all chords), accumulating quality evidence while the root holds, and pooling scores over 2–4 windows.

| | Song, 2nd half (held out) | Test set (held out, 30 tracks) | Dev set (30 tracks) |
|---|---|---|---|
| Two-window rule (v66.1): settled exact / changes per played chord | 0.63 / 2.10 | 0.742 / 1.20 | 0.763 / 1.19 |
| **Sticky 0.04 + two-window (v66.2)** | **0.62 / 1.38** | **0.736 / 1.13** | **0.750 / 1.07** |

Whole song, against the composer's annotation: displayed changes 82 → 61 (1.95 → 1.45 per played chord), back-and-forth flips 13 → 2, settled exact 0.70 → 0.69 (0.77 → 0.79 with the verse chord scored as Am7, the chord its voicing sounds), major/minor 0.94 both, median lag 1.5 s both. The remaining extra changes are mostly single refinements (C, then Cmaj7 once the seventh is heard). Median lag on the synthetic sets is unchanged at 1.5 s.

The in-browser fallback detector (used only when the server is offline or slow) is unchanged.

## Orb shape (ferrofluid, v67)

The orb's shape follows the sound's energy and texture: onsets (positive spectral flux from a 2048-point unsmoothed analyser), loudness (relative to the loudest recent level, capped so a quiet room never reads as loud) and harshness (0.45 × spectral flatness + 0.35 × brightness + 0.20 × sensory roughness of the 24 strongest peaks). It is drawn in 3D with WebGL: up to 64 spikes over the sphere, more and more pointed as harshness rises.

`ferro_test_track.py` builds the 60 s check track: soft pad, loud clean piano, a 12 s passage of a recording, distorted rock with drums, soft pad. The track was fed to the browser as its microphone input (Chromium, fake audio capture), and the orb's state was recorded every frame:

| Section | Spikes up (median) | Tallest spike (median / 90th pct, × spike length) |
|---|---|---|
| Soft pad | 0 | 0 |
| Loud clean piano | 22 broad swells | 0.47 / 0.86 (on each chord's attack) |
| A song mix ("I Miss You All") | 33 | 0.24 / 0.49 |
| Distorted rock with drums | 58 narrow needles | 0.68 / 1.07 (on the drum hits) |
| Soft pad again | 0 (all melted back within 0.6 s) | 0 |

These examples also set the harshness scale (`ROUGH_CAL` in `index.html`), so they show the mapping behaves as intended; they are not an independent test, and no listener study has been run on the shape layer yet.

Speed: 58 fps at full mesh detail (40,962 vertices) on a MacBook's Intel HD Graphics 5000. On slower devices the mesh steps down to 10,242 and 2,562 vertices, then to a flat outline, after two slow two-second periods; `?ferroq=4..6` fixes the detail for testing.

## Orb motion (v68)

Each spike was a value eased toward its target, so every spike moved together and stepped to its new height within a frame or two. v68 gives the motion a physical model:

- **Springs.** Each spike is a damped spring (stiff and lightly damped while rising, soft and heavily damped while melting back), so it overshoots a little on a hit and settles, instead of snapping to its target.
- **Ripple.** Each detected onset picks a point on the sphere; a spike's excitement is delayed by how far it sits from that point, reaching the far side about 70 ms later. A hit therefore travels across the surface.
- **Sway and spin.** Spike positions drift slightly, and the field turns faster when the music is energetic (0.07 to 0.37 rad/s).
- **Body pulse.** The orb's radius swells up to 10 % on a hit.

Measured by replaying `ferro_test_track.py`'s track into the browser as microphone input and recording the orb's state every frame (60 fps in both versions):

| | v67 | v68 |
|---|---|---|
| Jerkiness (second difference / first difference), clean piano | 0.83 | **0.67** |
| Jerkiness, song passage | 0.82 | **0.65** |
| Melt-back after the loud passage | 0.57 s | **0.35 s** |
| Movement per spike per second, rock | 1.64 | 2.00 |
| First piano chord: 10–90 % rise | 33 ms | 33 ms (starting 50 ms after the sound) |

Smoother per unit of travel, more movement overall, and spikes at different heights as a ripple passes, rather than moving in unison.

## Chord detection: what was tried and rejected (v68 review)

A systematic search for an improvement over the v66 engine found none that survives held-out testing. Recorded here so it is not repeated.

Tried on cached note saliences, scored on the dev set, the held-out test set, and the composer-annotated recording:

| Change | Result |
|---|---|
| Frame weighting by energy (loud frames count more) | dev sevenths 0.793 → 0.801, test 0.811 → 0.807 — within noise |
| Re-choosing each decoded segment's quality from its mean chroma | dev 0.793 → 0.804, but loses it again once the app splits a file into 30 s sections (song sevenths 0.831 → 0.810) |
| Overtone decay 0.5 / 0.6 / 0.85 / 0.95 (0.7 in use) | all worse; 0.95 collapses major/minor to 0.770 |
| Chroma smoothing over 3 / 5 / 9 frames | helps the song, costs the dev set |
| Notes ringing on within a chord, reset at chord changes | song root 0.951 → 0.961, dev sevenths 0.801 → 0.786 |
| Soft "is this note present" chroma, seventh-weighted templates | dev and test sevenths collapse (0.80 → 0.52–0.63) while the song improves |
| Triad bias, bass weight, switch penalty, root weight sweeps | no setting beats the current one on both sets |
| Microphone: an extra window aligned to each detected strum | offline, +2.4 points exact on the held-out test set; in the browser, no gain on the real song (0.75–0.77 either way, run-to-run spread ±0.02) and more flicker (flips 2–3 → 4). Rejected. |

Two findings explain the ceiling:

1. **The seventh is physically faint on plucked strings.** In the chroma, the seventh's energy relative to the triad's notes is 0.85 for the pad, 0.78 for the piano-like tone, and **0.35 for plucked strings** — which is where seventh recall is weakest (0.60 against 0.85–0.91). It is under-represented in the signal, not merely mis-scored.
2. **One real recording cannot arbitrate.** Changes that improve the annotated song mostly do so by reporting more sevenths, and five of that song's six chords are sevenths. Every such change costs accuracy on the synthetic sets.

Moving past this needs more annotated real recordings (so real music can decide, instead of one seventh-heavy song), not further tuning.

## A second real recording as reference: "Walking in the Railroad" (v69)

The composer marked every chord of "Walking in the Railroad" (3:08, drums and bass throughout,
24 chord changes a minute) on a tap screen, without seeing the detector's output: 75 segments,
full coverage, seven chords and every one of them a seventh — Cmaj7, Abmaj7, Bbmaj7, Ebmaj7,
Fmaj7, Dbmaj7, Dm7.

| | Root | Major/minor | Sevenths | Segmentation | Changes / true changes |
|---|---|---|---|---|---|
| Held-out synthetic test set (30 tracks) | 0.926 | 0.885 | 0.811 | — | 1.05 |
| "I Miss You All" (4:36, light percussion) | 0.951 | 0.94 | 0.831 | — | — |
| **"Walking in the Railroad"** | **0.778** | **0.748** | **0.613** | **0.815** | **1.28** |

Scored as the app runs it (30 s sections with 3 s of context); whole-file decoding gives the same
figures (root 0.775, sevenths 0.624). The annotation is in `annotations/walking-in-the-railroad.json`
and every figure in this section is reproduced by
`python score_real.py annotations/walking-in-the-railroad.json <the recording>` — the recordings
themselves are the composer's masters and are not in the repository.

**The synthetic set overstates real performance by 15 to 20 points.** This is the first real
recording in the set with drums and bass under the whole song and a fast harmonic rhythm, and it
is 15 points below the held-out synthetic set at the root level and 20 at the sevenths level.

**Timing is not the problem.** 70 of the 74 reference chord changes have an engine change within
0.5 s of them, median offset 0.17 s. The engine hears *when* the harmony moves.

**Quality is the problem.** Of the song's duration, 78 % gets the right root; 16 points of that
are the right root with the wrong chord type. The largest single error modes:

| Share of the song | Error |
|---|---|
| 5.0 % | Cmaj7 reported as C |
| 3.6 % | Bbmaj7 reported as Bb7 |
| 2.3 % | Cmaj7 reported as C7 |
| 2.1 % | Bbmaj7 reported as Dm7 |
| 2.0 % | Ebmaj7 reported as Eb |

### Why: the seventh's audibility predicts the error

For each annotated segment, the energy on each chord degree in the engine's treble chroma,
relative to the mean of the three triad notes (1.00 = as loud as a triad note):

| Chord | root | 3rd | 5th | major 7th | Reported correctly |
|---|---|---|---|---|---|
| Dbmaj7 | 1.76 | 0.99 | 0.25 | **2.77** | 57 % |
| Abmaj7 | 1.10 | 0.78 | 1.12 | **1.89** | 87 % |
| Fmaj7 | 1.15 | 0.42 | 1.43 | 0.78 | 56 % |
| Ebmaj7 | 1.43 | 0.90 | 0.67 | **0.52** | 59 % |
| Cmaj7 | 1.35 | 0.62 | 1.04 | **0.49** | 45 % |
| Bbmaj7 | 0.73 | 0.94 | 1.33 | **0.43** | 23 % |

The ordering is almost monotonic: where the major seventh is loud it is identified, where it is
faint the engine falls back to the plain triad or to the dominant seventh. This is the plucked-string
finding above (seventh/triad energy ratio 0.35 for plucked strings) measured on real music against
a real annotation, and it is a property of the signal, not of the scoring.

Bbmaj7 fails worst for a second, compounding reason: its root is the *weakest* of its own triad
notes in the treble (0.73), while its 3rd and 5th are strong, so the treble chroma reads as D–F–A
and Dm7 wins 19 % of its duration. The bass carries Bb for 78 % of it, and the bass-root term
(`w_bass` 0.6) is not enough to overcome this; raising it was already tried and costs the
synthetic sets.

### What this reference can and cannot settle

It settles that the synthetic figures are optimistic, that segmentation is sound, and that the
remaining error is chord quality rather than root or timing.

It cannot settle the seventh-versus-triad trade-off. All seven of its chords are sevenths, so a
change that reported sevenths more freely would never be penalised here — the same limitation as
"I Miss You All" (five of six chords sevenths), and more extreme. Arbitrating that trade-off needs
an annotated recording with a mixed vocabulary of triads and sevenths; none of the real recordings
annotated so far has one.

## GuitarSet as the triad-side reference, and what it exposed (v66.3)

Both composer-annotated songs are almost entirely seventh chords, so neither can judge whether
the engine calls sevenths too freely. [GuitarSet](https://zenodo.org/records/3371780)
(Xi et al., ISMIR 2018; CC BY 4.0) supplies the opposite bias: 360 excerpts of solo acoustic
guitar, six players, five styles, three progressions, with two annotated chord layers.

Only the 180 **comping** excerpts are used (90 min). The other 180 are monophonic solos over the
same progressions, where there is no chord in the signal to detect. Players 00–02 are the dev
set, 03–05 held out, so a parameter cannot be fitted to the players it is tested on.

Census of the two layers, by share of annotated time:

| | plain triads | with a 6th or 7th | expressible in the engine's 10 types |
|---|---|---|---|
| `instructed` (the lead sheet the player was given) | 87 % | 13 % | 100 % |
| `performed` (hand-verified transcription of what was played) | 45 % | 34 % | 64 % |

The lead sheet understates what was played — a player handed "Eb" plays Ebmaj7 — so both are
reported and `performed` is treated as primary. 175 distinct chord types appear in it; mir_eval
excludes the out-of-gamut ones at the levels where they do not map, and `score_guitarset.py`
prints the comparable share of time rather than quietly scoring a subset.

### The finding: v66 called sevenths four times too often

| | share of time |
|---|---|
| lead sheet asks for a chord with a 6th or 7th | 13 % |
| players actually played one | 18 % |
| **v66 reports one** | **71 %** |
| v66 reports `maj7` specifically | 42 % (played: 2 %) |

One Rock excerpt, lead sheet A–D–A–E–D–A, transcribed as plain triads throughout, is reported as
Amaj7, Dmaj7, A, E, Amaj7, Amaj7.

This had been invisible: the synthetic sets represent sevenths well, so nothing there punished the
lean, and both annotated songs actively rewarded it. The earlier conclusion that "one real
recording cannot arbitrate" was right about arbitration and wrong about the direction — every
rejected change that helped the songs by reporting more sevenths was pushing the wrong way.

### Tried and rejected: scoring the seventh on its own evidence

The natural fix, and the one the Railroad diagnostic points at, is to call a seventh only when
there is energy on the seventh degree: replace the flat bias with `w7 x (chroma at the 7th -
floor x mean chroma of the chord's own triad notes)`. It was worse at every weight tried, and it
damaged **root** accuracy badly (GuitarSet dev root 0.729 → 0.638 at the best setting, 0.17 at
`w7` 1.0), because a term keyed to a single chroma bin lets wrong-root chords win on an
accidentally strong bin. Best criterion value 0.584 against 0.660 for the flat fix. Rejected.

Note that the in-browser fallback detector already does gate sevenths this way (a 1.8 penalty
unless the seventh reaches 0.18 of the normalised chroma) and is unchanged. The idea is sound for
a template-correlation score over a raw chroma; it does not transfer to NNLS saliences decoded by
Viterbi, where the per-chord terms are on a different scale.

### The change

`triad_bias` −0.05 → **−0.02** and a new `qual_bias['maj7']` of **−0.06**. Selection rule, fixed
before any result was read: maximise the unweighted mean of sevenths recall on the synthetic dev
set and the GuitarSet dev players against the `performed` layer, and among settings within 0.005
of the best prefer the one nearest the current parameters. The songs were shown throughout as
observation only; being nearly all sevenths, they were not allowed to choose.

A lighter `w_bass` (0.60 → 0.40) scored higher still on the criterion (0.675 against 0.660) and
was **not** taken: it buys 1.6 points of GuitarSet sevenths for 2.8 points of Railroad root
accuracy, and the visualiser leans hardest on the root.

| | Synthetic test (held out) | GuitarSet test players (held out) | Walking in the Railroad |
|---|---|---|---|
| v66.2 | 0.926 / 0.885 / **0.811** | 0.610 / 0.586 / **0.382** | 0.778 / 0.748 / **0.613** |
| **v66.3** | 0.927 / 0.889 / **0.746** | 0.616 / 0.593 / **0.457** | 0.767 / 0.722 / **0.431** |

(root / major-minor / sevenths. GuitarSet against `performed`; against the lead sheet, sevenths
0.232 → 0.344. Songs scored the way the app runs them, in 30 s sections.)

The seventh-call rate over all 180 comping excerpts falls from 71 % to 45 %, against 18 % actually
played — improved, not solved. The trade is deliberate: 7.5 points of seventh accuracy on guitar
players the tuning never saw, and a small gain in major/minor on both held-out sets, against
6.5 points of synthetic sevenths and 18 on a song whose every chord is a seventh.

## The adaptive prior: tried, bounded, abandoned (v66.3 review)

After v66.3 the engine still reports a seventh 45 % of the time where players play one 18 %,
and the obvious next move is to let it form an expectation of a piece's vocabulary while it
listens rather than carry a fixed bias. Three experiments, in order, and none of them is used.

**1. Per-piece seventh evidence, absolute.** Decode once, then measure over the whole piece how
much chroma energy sits a major seventh above each *decoded root* — conditioning on the root
only, so the measure cannot merely confirm the first pass's own bias — and set the maj7 bias
from it. The statistic does not separate the corpora, and it fails in the revealing direction:

| | energy on the maj 7th above the decoded root (1.0 = as loud as root and fifth) |
|---|---|
| GuitarSet dev (87 % plain triads) | 0.252 |
| synthetic tracks that are >45 % sevenths | 0.050 |
| "Walking in the Railroad" (every chord a seventh) | 0.430 |

Real guitar carries *five times* the energy on the major-seventh degree that clean synthetic
seventh chords do, because of string ring, room and broadband noise. The best single threshold
separates triad-heavy GuitarSet from seventh-heavy synthetic 48 % of the time — worse than
chance. Any absolute measure of "is the seventh there" is dominated by a per-recording offset.

**2. Per-root pooled prior.** Decode once; for each root the piece uses, pool the chroma over
every frame assigned to that root across the whole piece, score the qualities on that pooled
evidence — many seconds instead of one segment — and feed the result back as a prior for a
second decode. This is the within-piece comparison the absolute measure lacks, and it uses the
fact that music repeats.

| strength | synthetic dev | GuitarSet dev (played) | Railroad |
|---|---|---|---|
| none (v66.3) | 0.914 / 0.882 / 0.777 | 0.740 / 0.672 / 0.543 | 0.776 / 0.731 / 0.462 |
| 0.2 | 0.916 / 0.888 / 0.755 | 0.745 / 0.679 / 0.550 | 0.786 / 0.756 / 0.426 |
| 0.5 | 0.918 / 0.892 / 0.732 | 0.748 / 0.683 / 0.551 | 0.786 / 0.756 / 0.426 |
| 2.0 | 0.914 / 0.873 / 0.668 | 0.752 / 0.678 / 0.550 | 0.788 / 0.739 / 0.388 |

It sharpens root and major/minor on all three references (Railroad +1.0 root, +2.5 major/minor)
and costs chord quality everywhere, because committing a root to one quality for a whole piece
erases the pieces that genuinely use both C and Cmaj7. Not used as it stands; the root and
major/minor gain is real and could be revisited as a change aimed at those levels rather than
at sevenths.

**3. The oracle that ended it.** Before building an adaptive rule, bound what one could win:
give every piece the maj7 bias that is best *for that piece*, chosen knowing the answer. No
rule can beat that.

| | best single bias | shipped bias (−0.06) | per-piece oracle |
|---|---|---|---|
| synthetic dev | 0.787 (at 0.00) | 0.777 | **0.791** |
| GuitarSet dev | 0.587 (at −0.22) | 0.543 | **0.601** |

Perfect per-piece knowledge is worth 1.4 points on GuitarSet and 0.4 on the synthetic set over
the best *fixed* setting. And the oracle's choices are not piece-specific at all: 80 of
GuitarSet's 90 excerpts want the strongest penalty on the grid, and so do 14 of the 30 synthetic
tracks. The oracle is not discovering that pieces differ; it is saying that the fixed bias
should be stronger on one corpus than the other, which is the trade-off of v66.3 restated.

**Conclusion.** Adapting a decode-side parameter per piece has almost no headroom, which is
consistent with everything else in this file: ten changes rejected in the v68 review, the
per-frame evidence term, the two experiments above. The remaining error is not recoverable by
weighting the same decisions differently — it is in what the front end can see. Moving it needs
a learned acoustic model over the CQT in place of template matching, which is a different scale
of work and is what the paper's own architecture proposes. Further parameter work on this engine
is not warranted.

## Design decisions tested and rejected (dev set)

- **Partial bass credit for inversions** (bass on the third or fifth): no gain overall (root 0.916 → 0.907–0.915), so not used.
- **Evidence accumulation for the microphone**: no setting beat the two-window rule on accuracy and flicker together.

## What changed from v65

1. One spectrum per section instead of one per 3 s window (about 5× faster).
2. NNLS note salience: a bass note's overtones no longer read as chord tones (v65's main cause of minor → major and 7th → triad errors).
3. Vocabulary limited to the chord types the colour layer can show.
4. Viterbi decoding with a change penalty instead of a 9-window majority vote, which had erased real chord changes.

## Limitations

- Synthetic audio plus two real recordings annotated by their composer, both of them almost
  entirely seventh chords; a recording with a mixed triad/seventh vocabulary, and recordings
  by other players (GuitarSet, classroom repertoire), are the next test.
- On real music with drums, bass and a fast harmonic rhythm the engine scores 0.78 / 0.75 / 0.61,
  not the 0.93 / 0.89 / 0.81 of the synthetic set.
- First-inversion chords are usually reported with the bass note as root.
- Plucked-string timbres are the weakest condition.
- The speed figure is from a cloud CPU; the free hosting tier is slower.
