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
Upload any audio file (MP3, WAV, etc). See Harmony analyses the entire track automatically before playback using Python-quality chord detection (numpy + scipy running via WebAssembly), then displays the correct chord in sync with the music. No setup required — just upload and play.

**First load takes ~20 seconds** while Python/scipy loads in the background. After that it's cached for the session.

---

## Chord detection algorithm

File mode uses a full offline analysis pipeline:

1. **Bandpass filter** (82–500 Hz) — isolates the harmonic register, removes kick drum and melody
2. **FFT + chroma extraction** — maps frequency content to 12 pitch classes
3. **Key detection** — Krumhansl-Kessler profile correlation across the full track
4. **Diatonic constraint** — builds a search set of diatonic chords, secondary dominants, and borrowed chords for the detected key
5. **Bass-anchored root detection** — uses the lowest register (82–200 Hz) to anchor the root, eliminating root/fifth confusion
6. **Majority smoothing** — 5-frame median window (2.5s) to eliminate transient noise
7. **Timeline playback** — pre-computed chord changes displayed in sync with audio

Mic mode uses a real-time version of the same pipeline with a rolling harmonic buffer.

---

## Tech

- Pure HTML/CSS/JS — single file, no build step, no dependencies
- [Pyodide](https://pyodide.org) — Python + numpy + scipy running in WebAssembly for file analysis
- Web Audio API — mic input and real-time analysis
- GitHub Pages — zero-config deployment

---

## Repository

```
see-harmony/
├── index.html      — the entire app
├── analyse.py      — optional CLI reference (not required by the app)
├── README.md
└── LICENSE
```

---

## analyse.py (optional reference)

The app handles analysis automatically via Pyodide. `analyse.py` is included only as a reference implementation and for offline use on slow connections:

```bash
pip install numpy scipy pydub
python3 analyse.py mysong.mp3
```

---

## Research context

See Harmony is a component of the **Neural Conservatory** — a framework for AI-augmented music pedagogy that uses multimodal representations (harmonic colour fields, latent space trajectories, synesthetic feedback) to make musical structure visible and learnable.

The app is designed for use in guitar and general instrument instruction, where students can connect their instrument directly and receive immediate visual feedback on the harmonic quality of what they're playing.

---

## Author

André Gather — [gatherandre](https://github.com/gatherandre)  
Neural Conservatory MVP · 2026  
MIT License
