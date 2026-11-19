# The elicitation instrument

Everything needed to run the listener study again, or to check what the listeners
were actually asked.

| | |
|---|---|
| `index.html` | The page participants used. Bilingual (pt-BR / en), self-contained apart from `audio/`. Open it in a browser and it runs. |
| `stimuli.py` | Generates the thirty chords. Ten qualities in three keys, one piano-like timbre, equal loudness, matched register. Writes `audio/` and `manifest.json`. |
| `manifest.json` | What each stimulus is: id, chord quality, root. |
| `audio/` | The thirty chords as served, plus two non-chord practice items (`p01`, `p02`). |

Run `python3 stimuli.py` to regenerate the audio from scratch; it needs `numpy`,
`soundfile` and `ffmpeg` on the path. The files in `audio/` are the ones the
participants actually heard, so regenerating is a check rather than a necessity.

## What is not here

The thirty-two individual response files are deliberately excluded. Participants
were told their answers would be used for the study, and the first ten saw wording
that did not cover publication of their individual rows. Aggregate results are in
`../results-interim.md`; the analysis scripts in `../` read from a local `data/`
directory that is not part of this repository.

## Known fault in the stimulus design

The three roots of each quality are assigned as `(5q + step) % 12` for step in
`(0, 4, 8)`. A root step of four semitones is the augmented triad's own interval
structure, so augmented -- alone among the ten -- receives the same pitch-class set
`{0,4,8}` three times, in three voicings. `../stimulus_check.py` prints this. A root
step of one or two semitones would give three distinct augmented triads in any
future collection.
