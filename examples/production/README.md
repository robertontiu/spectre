# Production upgrade A/B: stacks against the published sound

Queue item 9b, sound side (2026-11-25). Two published trance excerpts, each rendered twice from the session's own `project.json`: **A** as published, **B** with the kick, bass and lead rebuilt as stacks with the new engine (same patterns, same arrangement, same notes; nothing else changed). For the owner's ear, and for the professional trance producer whose feedback started this work.

| Case | A (published) | B (stacks) | Picture | Numbers |
|---|---|---|---|---|
| First Light (007), second wave (`rel2`, 8 bars, 5:48-6:02) | [first-light-A-published.mp3](first-light-A-published.mp3) | [first-light-B-stacks.mp3](first-light-B-stacks.mp3) | [first-light.png](first-light.png) | [first-light.json](first-light.json) |
| Half of Me (013), main drop (`mainA`, 8 bars, 2:03-2:17) | [half-of-me-A-published.mp3](half-of-me-A-published.mp3) | [half-of-me-B-stacks.mp3](half-of-me-B-stacks.mp3) | [half-of-me.png](half-of-me.png) | [half-of-me.json](half-of-me.json) |

Rebuild: `python3 examples/production/build.py` (about 2.5 minutes for both; the recipes are in the script).

## What B is
- **Kick**: `kicksub` tuned to the key (Ab1 = 51.9 Hz in First Light, F#1 = 46.2 Hz in Half of Me) with a little drive, `kickpunch` (115 Hz, high-passed at 80 Hz), `kickclick` (3.2 kHz, high-passed at 1.5 kHz), the bus soft-clipped (`clip`, 2 dB drive, -1.5 dBFS). No carving of the fundamental. In Half of Me it also replaces the published sine thump under the kick (`ksub`, which measured 60 dB under the mix: inaudible).
- **Bass**: `sub` (a sine with a little 2nd/3rd harmonic, role `sub`: low-passed near 100 Hz by the trance preset), the published rolling `trancebass` with its own sub removed (role `bass`: high-passed at 90 Hz, +3 dB body), an upper bass an octave up (`polysynth` saw and pulse pluck, role `upper-bass`); the bus keeps the published sidechain and adds a 2:1 compressor and light saturation. In Half of Me the bass line sits on the kick's own note, so its sub is 5 dB lower.
- **Lead**: main `supersaw` `"model": 2` (the published lead's voices, detune, mix and filter envelope, cutoff x 1.3, drift 0.35, a 10-cent delayed vibrato), support `supersaw` model 2 an octave up (slower attack, longer release, wider, 7 dB down; in First Light it replaces the published octave double `lead2`, which plays the same notes), an `air` layer, a narrow square centre 10 dB down; the bus: `ott` at depth 0.3, a 2:1 compressor, light chorus, the published sends and sidechain.
- Role EQ presets from the trance map (`"genre": "trance"`), overridden where the build script says.

## How it was made fair
- Each B stack is **level-matched** to the A tracks it replaces, with a gain at the end of the stack's bus chain: the kick by its peak (as kicks are set in a mix), bass and lead by A-weighted energy over the excerpt.
- Both excerpts go through **the same quick master**: the engine's own (high-pass 25 Hz, 2:1 glue, -10 LUFS integrated, -1 dBFS limiter), **without** the release master's tonal EQ, so the master does not pull either version toward the target and hide the difference. 192 kbps MP3, 13.7-13.9 s.
- Both renders start from a fresh random state; the sessions keep their shared seed mode, so tracks that were not rebuilt keep notes and sound but get new random phases (free-running oscillators: inaudible).

## Measured (`listen --clarity` analysis of each excerpt, genre trance, target `trance_2015`)
Tonal balance of the excerpt against the era target (dB, the target laid over the mix at its level around 1 kHz):

| | 50-80 Hz (kick and sub) | 100-250 Hz (build-up) | 315-400 Hz | 2-5 kHz | 8-12.5 kHz (air) |
|---|---|---|---|---|---|
| First Light A | **-6.7** | +0.4 | -0.2 | -2.1 | **-8.2** |
| First Light B | **+1.2** | -2.7 | -2.2 | -2.3 | **-1.6** |
| Half of Me A | **-5.2** | +2.8 | +3.5 | +0.8 | **-4.3** |
| Half of Me B | **+0.1** | +0.4 | +1.6 | -0.4 | **+1.0** |

Stems and layers:

| | First Light A | First Light B | Half of Me A | Half of Me B |
|---|---|---|---|---|
| occupancy sub / bass / low-mid / mid / presence / air (stems within 6 dB per cell) | 1.06 / 1.01 / 1.11 / 1.98 / 2.45 / 2.11 | 1.03 / 1.06 / 1.18 / 2.01 / 2.04 / 1.57 | 1.15 / 1.03 / 1.13 / 1.53 / 1.27 / 1.39 | 1.25 / 1.09 / 1.19 / 1.58 / 1.43 / 1.34 |
| crest per region, 10 ms (dB) sub / low-mid / air | 11.7 / 12.8 / 8.1 | 8.0 / 9.3 / 4.8 | 12.3 / 10.8 / 8.2 | 8.6 / 7.0 / 5.6 |
| lead: masked / own | 12% / 69% (plus `lead2` 8% / 74%) | 2% / 88% | 1% / 94% | 1% / 94% |
| bass: masked / own | 62% / 26% | 66% / 21% | 17% / 69% | 20% / 67% |
| kick: masked / own | 4% / 87% | 9% / 84% | 8% / 85% | 13% / 67% |
| core roles empty (flags) | sub, air | none | air | none |

Stack view of B (each layer's share of its stack's energy; level against the stack's loudest layer):

| Stack | First Light | Half of Me |
|---|---|---|
| kick | sub 91%, punch 9% (-10 dB), click 0.5% (-22 dB; it owns 100% of the stack's 2-18 kHz) | sub 86%, punch 14% (-8 dB), click 0.9% (-20 dB) |
| bass | sub 52%, roll 45% (-0.6 dB), upper 3% (-13 dB) | sub 34% (-2.6 dB), roll 62%, upper 4% (-12 dB) |
| lead | main 77%, support 12% (-8 dB), air 6% (-11 dB), centre 5% (-12 dB) | main 74%, support 17% (-6 dB), air 5% (-12 dB), centre 5% (-12 dB) |

## Reading it, honestly
- **What moved:** the kick-and-sub band came up to the era target in both (by 8 and 5 dB, against the 6-7 dB gap docs/TRANCE.md C measured on the masters), and the air band from 8 and 4 dB short to within 1.6 dB, built from sources (the kick sub, the bass sub, the air and support layers) instead of master EQ. The "role empty" flags for sub and air are gone; the lead is less masked and owns more of its cells in First Light (the octave double became a support layer a fifth of the level, instead of a second lead).
- **What it did not do, or did worse:**
  - First Light B is 2.7 dB under the target at 100-250 Hz: the published mix was on the target there only through the kick's +5 dB at 105 Hz and heavy saturation (the carving the research called dated); the rebuild has not replaced that body yet (more rolling-bass body or punch would). Half of Me B is on the target there.
  - Crest fell in every region (sub 11.7 to 8.0 dB, low-mid 12.8 to 9.3 dB, air 8.1 to 4.8 dB in First Light): the new low end is more continuous (sub layers between the kicks) and the air more sustained (air and support layers under OTT). Denser is the intent; whether it reads as fuller or as less punchy is an ear question. docs/PRODUCTION.md names a collapsing low-mid crest as the measurable side of mud: watch it.
  - The published shaker hats in First Light (`chh`, not rebuilt) go from audible to 100% masked by the louder air of the lead stack: the hats would be the next thing to rebuild (`metalhat`).
  - The mid region stays a blend of 2 (First Light) and 1.6 (Half of Me) stems per cell; the stacks fill the edges, not the middle.
  - Occupancy barely changed (a stack counts as one stem: by design, a stack is one perceived sound).
- **What numbers cannot say:** whether B sounds current, rich, or just different. The professional producer's point was about richness and depth; the measurements say the roles are now filled and the balance is near the genre's records. The ear decides (docs/PRODUCTION.md section 4).
- Nothing in the sessions was changed. A remix of 007 or 013 (queue item 9d) would start from these stacks, and would also rebuild pads, plucks, arps and hats.

The reference recordings and samples used for the instrument measurements (TR-808 and TR-909 samples from oramics/sampled) were measured only and never stored in the repo or used in a track.
