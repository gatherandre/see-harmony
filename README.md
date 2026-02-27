# See Harmony

**Real-time synesthetic visual feedback for music learning**

A browser application that listens to live or recorded audio and renders a stable, learnable visual field where colour, brightness, and motion reflect the harmonic properties of your playing — in real time.

---

## What it does

See Harmony listens to your instrument and maps four acoustic features to four visual dimensions simultaneously:

| Acoustic feature | Visual dimension | Psychophysical basis |
|---|---|---|
| Pitch height (log frequency) | Brightness (HSV Value) | Marks, 1975 |
| Spectral centroid (timbre) | Saturation | Ward et al., 2006 |
| Harmonic tension (tonal distance) | Hue: warm → cool | Spence, 2011 |
| Onset strength (rhythm) | Orb pulse radius | — |

All mappings are **continuous** and **ratio-preserving**: equal musical intervals produce equal perceptual steps. An octave up always shifts brightness by the same amount. Moving from consonance to dissonance always shifts the colour field toward blue. The mapping is learnable, not decorative.

A **history ribbon** at the bottom of the screen displays the last 10 seconds of harmonic colour — a visual memory trace of your performance that you can study, compare, and reflect on.

---

## Why it was built

This is the Minimal Viable Prototype of the **Neural Conservatory** — a theoretical framework for AI-assisted multisensory music pedagogy developed in the thesis *"The Neural Conservatory: Computational Synesthesia as a Bridge Between Music Cognition, Multisensory Learning, Philosophy of Mind and Consciousness"* (André Guimarães, 2026).

The central hypothesis: that ratio-preserving cross-modal mappings between acoustic and visual features can improve music learning and reflective practice, by making the harmonic structure of music visible as well as audible.

See Harmony operationalises Sections 5.9 and 10.2 of that thesis. It is designed to be the first artifact in a pilot study testing whether the visual mapping is learnable and whether it improves music retention.

---

## How to use it

**Option 1 — Open directly (no setup needed)**

Download `index.html` and open it in any modern browser (Chrome, Firefox, Safari, Edge). That is the entire application.

**Option 2 — GitHub Pages**

Fork this repository, then go to *Settings → Pages → Deploy from branch → main → / (root)*. Your app will be live at `https://gatherandre.github.io/see-harmony/`.

**Option 3 — Local server (recommended for file input)**

```bash
# Python
python3 -m http.server 8080

# Node
npx serve .
```

Then open `http://localhost:8080`.

---

## Controls

| Control | Action |
|---|---|
| **Begin Listening** | Request microphone access and start |
| **Learn** mode | Visual updates live as you play; ribbon records |
| **Reflect** mode | Ribbon freezes; study your harmonic trace |
| **⬤ Mic** | Switch to live microphone input |
| **↑ File** | Load a WAV, MP3, or other audio file |
| `L` | Switch to Learn mode |
| `R` | Switch to Reflect mode |
| `M` | Switch to Mic input |

---

## Reading the display

**Background sky** — The full-screen colour field shows the overall harmonic state of your playing. Warm orange tones indicate consonant, in-key harmony. Cool blue tones indicate dissonance or chromatic tension. Brightness rises with pitch; saturation rises with timbral brightness (open strings and clear tones produce more vivid colours than muted or dampened ones).

**Central orb** — Pulses with each rhythmic onset. Its colour mirrors the harmony field.

**History ribbon** — A scrolling strip at the bottom of the screen showing the last 10 seconds of harmonic colour, left to right. The vertical line at the right edge marks "now." The ribbon is updated only in Learn mode.

**HUD text** (bottom-left) — Shows the detected pitch (note name and Hz) and harmonic tension level (consonant / neutral / tense / dissonant with percentage).

---

## Success criteria (pilot study version)

This prototype is considered validated when:

1. It runs stably in real time on a standard laptop
2. The visual field does not flicker under normal playing conditions
3. It produces visually distinguishable signatures for: major vs. minor triads; consonant vs. dissonant intervals; bright vs. dark timbres
4. **Users can predict what they will see after a short learning period** — this is the key criterion, proving the mapping is cognitively learnable, not random decoration

---

## Technical notes

**Stack**
- [WebAudio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) — microphone capture and FFT
- [Meyda.js v5.6.0](https://meyda.js.org) — spectral centroid, chroma vector, RMS, spectral flux
- Pitch estimation via Normalised Square Difference Function (NSDF) — a simplified McLeod Pitch Method implemented in-browser
- HTML5 Canvas — all rendering
- No backend, no server, no build step

**Pitch detection**  
Autocorrelation-based (NSDF) over a 2048-sample window, operating on raw time-domain data from the AnalyserNode. Practical range: ~78 Hz – 1400 Hz (covers full guitar and piano in typical pedagogical register).

**Tonal distance**  
Chroma vector from Meyda compared against all 24 Krumhansl-Kessler key profiles (12 major + 12 minor). Maximum Pearson correlation determines the nearest key; distance from that key drives harmonic tension. This is the psychophysically grounded basis for the hue mapping.

**Smoothing**  
All features smoothed with exponential moving average (EMA, α = 0.18 for pitch/harmony, α = 0.32 for onset). This prevents visual flicker without introducing perceptible lag.

---

## Limitations (v0.1)

- Pitch detection is autocorrelation-based; polyphonic pitch estimation is not yet implemented. The display responds primarily to the strongest fundamental.
- Chroma accuracy depends on signal quality; noisy environments will produce less stable hue mapping.
- The Reflect mode currently freezes the ribbon for visual study; full session playback is planned for v0.2.
- Tested on Chrome 120+, Firefox 121+, Safari 17+. WebAudio API availability may vary on mobile.

---

## Roadmap

- [ ] v0.2 — Polyphonic pitch tracking; Reflect mode session replay
- [ ] v0.3 — Pilot study mode: session recording, pre/post comparison, Likert export
- [ ] v0.4 — Integration with trained Neural Conservatory model (Music Transformer fine-tuned on harmonic tension annotation)
- [ ] v1.0 — Full Neural Conservatory MVP as described in thesis Section 5.9

---

## Research context

This prototype is part of an ongoing research programme. If you are a music educator, researcher, or student interested in participating in the pilot study described in Section 5.9.5 of the thesis, please open an issue or reach out directly.

The pilot study design:
- 10–20 participants (music students, any instrument)
- Within-subject: learn 2 short phrases (audio-only vs. audio + visual)
- ~30 minutes per participant
- Measures: time to criterion, error count, 5-item Likert, 10-minute retention test

---

## References

de Cheveigné, A. and Kawahara, H. (2002). YIN, a fundamental frequency estimator for speech and music. *JASA*, 111(4), 1917–1930.

Krumhansl, C. L. (1990). *Cognitive Foundations of Musical Pitch*. Oxford University Press.

Marks, L. E. (1975). On colored-hearing synesthesia. *Psychological Bulletin*, 82(3), 303–331.

Rawlinson, D., Segal, N., and Fiala, J. (2015). Meyda: An audio feature extraction library for the Web Audio API. *Web Audio Conference*.

Spence, C. (2011). Cross-modal correspondences: A tutorial review. *Attention, Perception, & Psychophysics*, 73(4), 971–995.

Ward, J., Huckstep, B., and Tsakanikos, E. (2006). Sound-colour synaesthesia. *Cortex*, 42(2), 264–280.

---

## License

MIT — see `LICENSE`

---

*See Harmony is a prototype. It is part of the Neural Conservatory research programme. The Visual field you see is the music thinking.*
