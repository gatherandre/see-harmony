# See Harmony
**Real-time synesthetic visual feedback for music learning**

A browser application that listens to live or recorded audio and renders a stable, learnable visual field where colour, brightness, and motion reflect the harmonic properties of what you're playing — in real time.

Built as part of the **Neural Conservatory** research project at the Media Lab.

🔗 **Live app:** [gatherandre.github.io/see-harmony](https://gatherandre.github.io/see-harmony/)

---

## What it does

See Harmony maps musical harmony to colour in a consistent, learnable way:

- **Warm colours (orange/red)** → tension, dissonance, dominant chords
- **Cool colours (blue/green)** → rest, consonance, tonic chords
- **Brightness** → signal strength and harmonic clarity
- **Orb size and motion** → dynamic envelope and resonance

The orb displays the detected chord name and pulses with the music. A ribbon at the bottom shows chord history over time.

---

## Modes

### 🎤 Mic mode

Connect a microphone or plug in an instrument. See Harmony listens in real time and updates the visual field as you play. Designed for use in music lessons — students can see the harmonic colour of what they're playing without needing to read notation.

### 📁 File mode

Upload any audio file (MP3, WAV, etc). See Harmony analyses the entire track before playback using a full Python signal processing pipeline (numpy + scipy) running inside a Web Worker via WebAssembly. The correct chord is displayed in sync with the music. No setup required — just upload and play.

**First load takes ~20 seconds** while Python/scipy loads in the background. After that it's cached for the session.

---

## Chord detection algorithm

File mode runs a full offline analysis pipeline — the same pipeline as `analyse.py`, running verbatim in the browser:

1. **Zero-phase bandpass filter** (`scipy.signal.filtfilt`, 82–500 Hz) — isolates the harmonic register, removes kick drum and melody. Uses `filtfilt` (forward + backward pass) for zero phase distortion — critical for accurate chroma extraction.
2. **FFT + chroma extraction** — Hann-windowed `numpy.fft.rfft` maps frequency content to 12 pitch classes
3. **Key detection** — Krumhansl-Kessler profile correlation sampled across the full track
4. **Diatonic constraint** — builds a search set of diatonic chords, secondary dominants, and borrowed chords for the detected key
5. **Bass-anchored root detection** — separate 82–200 Hz filter pass anchors the chord root, eliminating root/fifth confusion
6. **Majority smoothing** — 5-frame median window (2.5s) eliminates transient noise
7. **Timeline playback** — pre-computed chord changes displayed in sync with audio

Mic mode uses a real-time version of the same pipeline with a rolling harmonic buffer and Web Audio API filtering.

---

## Why Pyodide, and why a Web Worker

Early versions (v1–v40) attempted to port the Python analysis pipeline to JavaScript. This turned out to be harder than it looks — not because the algorithm is complex, but because of a subtle difference between browser audio filters and scipy:

Web Audio API `BiquadFilter` nodes process audio **causally** (one forward pass). `scipy.signal.filtfilt` processes audio **zero-phase** (forward pass then backward pass), which doubles the effective filter order and eliminates phase distortion. At low frequencies (82–200 Hz), this phase difference is large enough to shift formant timing by tens of milliseconds, corrupting both the key detection and the bass-root anchoring that distinguishes Cmaj7 from C7.

The solution is to not port the pipeline at all — just run Python in the browser. [Pyodide](https://pyodide.org) runs CPython + numpy + scipy compiled to WebAssembly. The analysis runs in a Web Worker so the UI stays alive during the ~15s processing time for a typical song. The worker is initialised in the background when the user clicks *Begin*, so it's usually ready (or close to it) by the time they pick a file.

---

## Tech

- Pure HTML/CSS/JS — single file, no build step, no runtime dependencies
- [Pyodide](https://pyodide.org) v0.26 — CPython + numpy + scipy via WebAssembly, loaded in a Web Worker
- Web Audio API — mic input, real-time analysis, file playback
- GitHub Pages — zero-config deployment

---

## Repository

```
see-harmony/
├── index.html      — the entire app (v41)
├── analyse.py      — CLI reference implementation
├── README.md
└── LICENSE
```

---

## analyse.py

`analyse.py` is the reference implementation — the same algorithm that runs inside the browser. Useful for verifying results offline or on slow connections:

```bash
pip install numpy scipy pydub
python3 analyse.py mysong.mp3
```

The Python code embedded in `index.html` is a direct copy of the core analysis logic from this file.

---

## Research context

See Harmony is a component of the **Neural Conservatory** — a framework for AI-augmented music pedagogy that uses multimodal representations (harmonic colour fields, latent space trajectories, synesthetic feedback) to make musical structure visible and learnable.

The app is designed for use in guitar and general instrument instruction, where students can connect their instrument directly and receive immediate visual feedback on the harmonic quality of what they're playing.

---

## Author

André Gather — [gatherandre](https://github.com/gatherandre)  
Neural Conservatory MVP · 2026  
MIT License
