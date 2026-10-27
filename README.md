# See Harmony
**Real-time synesthetic visual feedback for music learning**

A browser application that listens to live or recorded music and shows its harmony as colour. A continuous background field follows the sound itself (pitch, timbre, tonal tension); a central orb and a history ribbon follow the chord being played.

Part of the **Neural Conservatory** research programme.

🔗 **Live app:** [gatherandre.github.io/see-harmony](https://gatherandre.github.io/see-harmony/)

---

## What you see

**Background field — physical layer (continuous)**

| Sound | Colour |
|---|---|
| Pitch height (E2–E6, log-frequency) | Lightness |
| Spectral centroid (timbral brightness) | Colourfulness |
| Tonal tension (distance from the nearest key profile) | Hue, cool → warm |

**Orb and ribbon — semantic layer (chord type)**

| Chord | Colour |
|---|---|
| Major | gold |
| Minor | deep blue |
| Dominant 7th | orange-red |
| Major 7th | violet |
| Minor 7th | teal |
| Half-diminished, diminished, augmented | dark reds and plums |
| Suspended | yellow-green |

Extended chords take the colour of their family (C9 → dominant, Cmaj9 → major 7th). In both layers, red means tension.

**Orb shape — energy and texture (ferrofluid)**

The orb keeps its chord colour, but behaves like ferrofluid in a magnetic field: round when the music is soft, spiky when it is loud and harsh.

| Sound | Shape |
|---|---|
| Onsets (spectral flux) | spikes shoot out on each hit, then melt back |
| Loudness | how long the spikes are and how long they stay up |
| Harshness (noisiness, brightness, sensory roughness) | how many spikes, and how pointed: rounded swells for clean sounds, needles for distorted ones |

It is drawn in 3D with WebGL: spikes rise all over the sphere, towards the viewer too, except on a smooth patch behind the chord name; at rest it looks exactly like the plain orb. On slow devices it lowers its mesh detail, and falls back to a flat outline if needed.

---

## Modes and options

- **Mic** — play into a microphone or plug in an instrument. Chords come from the analysis server (a 1 s window every 0.5 s; the shown chord changes when two windows agree, and a window still counts for the chord on screen when that chord scores almost as well as its best, which stops flicker between a chord and its seventh). If the server is offline or slow, an in-browser detector takes over. Only one detector is used at a time.
- **File** — load an MP3 or WAV. The track is analysed in ~30 s sections before playback, then the chords play back in sync.
- **Play / Review** — live view, or the enlarged harmonic trace of what was played.
- **Colour only** (button or key `C`, or `?colouronly=1`) — hides chord names and readouts, so the colours carry the information on their own. Intended for studies and listening exercises.
- **Ferrofluid** (button or key `F`; on by default, `?ferro=0` to start with it off) — the orb's shape layer. The choice is remembered in that browser. `T` shows a tuning panel (sensitivity, spike length, snap on beats, melt-back speed, texture response) with live meters.
- `?stereo=1` — experimental stereo edge colours (off by default).
- `?debug=1` — developer readout.

Keys: `P` play, `V` review, `M` microphone, `C` colour only, `F` ferrofluid, `T` ferrofluid tuning, space = record / play-pause.

---

## Architecture

```
browser (index.html)                          server (server/, Flask + librosa)
  Web Audio capture ──► features every frame
    pitch, spectral centroid, chroma ──► background field
  file: 30 s sections (+3 s context) ──► POST /segment ──► chord timeline
  mic:  last 1 s every 0.5 s         ──► POST /chord   ──► chord + top candidates
  fallbacks: in-browser detector (mic), Pyodide (file, server offline)
```

**Chord engine (`server/chord_engine.py`, v66):**

1. Harmonic part of the signal (harmonic–percussive separation)
2. Tuned constant-Q spectrum, 36 bins per octave, E1 to about C8
3. Local spectral whitening
4. Note salience by non-negative least squares against harmonic-series note templates, so a note's overtones are not mistaken for other notes (after Mauch & Dixon's NNLS chroma)
5. Separate treble and bass chroma
6. Chord scores: cosine to chord templates plus a bass-root term, over the chord types the colour layer shows
7. Viterbi decoding with a penalty per chord change

The free hosting tier sleeps when idle. The app waits up to 75 s for it to wake (and says so), pings it every 10 minutes while a page is open, and keeps retrying if it was offline. For classes, open the app a minute or two before you start.

---

## Accuracy

Measured on a synthetic, ground-truth test set: 30 held-out tracks, 20 minutes, random keys and progressions, plucked / piano-like / sustained timbres, strummed / fingerpicked / block playing, with and without melody and noise. Duration-weighted recall (`mir_eval`):

| | Root | Major/minor | Sevenths | Time per audio second |
|---|---|---|---|---|
| v65 (per-window detector, 9-window vote) | 58 % | 50 % | 32 % | ~0.3 s |
| v65 with a 3-window vote | 73 % | 64 % | 43 % | ~0.3 s |
| **v66 engine** | **93 %** | **89 %** | **81 %** | **0.06 s** |

Settings were tuned only on a separate development set. Known limits: inversions are usually reported with the bass note as root; plucked strings are the hardest timbre (65 % at the sevenths level); real recordings have not yet been tested (GuitarSet is the next step). See [`eval/EVALUATION.md`](eval/EVALUATION.md).

---

## Running locally

```bash
cd server && pip install -r requirements.txt && python app.py      # API on :5000
python -m http.server 8000                                          # app on :8000
```

On `localhost` the app talks to `http://localhost:5000` automatically.

## Repository

```
see-harmony/
├── index.html              — the app
├── server/
│   ├── app.py              — Flask API: /chord, /segment, /analyze
│   ├── chord_engine.py     — v66 chord engine
│   ├── chord_detector.py   — v65 detector (kept for comparison)
│   └── render.yaml, requirements.txt
└── eval/                   — test-set generator and evaluation scripts
```

---

## Author

André Guimarães — [gatherandre](https://github.com/gatherandre)
Neural Conservatory · 2026 · MIT License
