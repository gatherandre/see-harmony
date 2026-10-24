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

## Design decisions tested and rejected (dev set)

- **Partial bass credit for inversions** (bass on the third or fifth): no gain overall (root 0.916 → 0.907–0.915), so not used.
- **Evidence accumulation for the microphone**: no setting beat the two-window rule on accuracy and flicker together.

## What changed from v65

1. One spectrum per section instead of one per 3 s window (about 5× faster).
2. NNLS note salience: a bass note's overtones no longer read as chord tones (v65's main cause of minor → major and 7th → triad errors).
3. Vocabulary limited to the chord types the colour layer can show.
4. Viterbi decoding with a change penalty instead of a 9-window majority vote, which had erased real chord changes.

## Limitations

- Synthetic audio only; real recordings (GuitarSet, classroom repertoire) are the next test.
- First-inversion chords are usually reported with the bass note as root.
- Plucked-string timbres are the weakest condition.
- The speed figure is from a cloud CPU; the free hosting tier is slower.
