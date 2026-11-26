# Techno, fitted: 909 kick, hats, toms, rim; congas and bongos; the rumble; hard kick and hoover; free-running loops; the loud master

Built 2026-11-26 for queue item 14 ("Fast & Furious": hard techno at 150 bpm, hard-groove percussion, a distorted acid line), standing rule 19: docs/TECHNO.md "Engine mapping" gaps 1-7, each fitted to openly licensed recordings as examples/production/dubstep-v2/ did for bass music. Everything is opt-in (docs/MANUAL.md "Techno, fitted"; code `engine/techno.py`, presets `engine/techno_presets.json`): a project that names none of it renders exactly as before (below, "Bit-identity").

## 1. The references

- **A recorded TR-909**: the "TR-909 Detroit" kit of oramics/sampled (recorded through API and Neve; the collection says "public domain or similar", the kit names no licence, so it is measured only), already used for the 909 snare, clap and ride (examples/production/modern/measure909.py): its kick, two closed hats, two open hats, two toms and rimshot. `engine/third_party.json` `refs-tr909-detroit`.
- **56 Freesound sounds**, each licence checked on its sound page: 33 CC0 1.0, 15 CC BY 4.0, 8 CC BY 3.0; the HQ previews (128 kbps MP3), measured, never used in a track, never committed (`refs-techno-cc0`, `refs-techno-ccby`; `python3 tools/engine_assets.py install refs-techno-cc0 refs-techno-ccby refs-tr909-detroit` puts them in `~/.cache/spectre/refs/`).

| Role | n | What |
|---|---|---|
| rumble | 8 | kick-and-rumble loops, 124-156 bpm (titles say rumble, or the 30-150 Hz level between kicks stays within 11 dB of the kick); plain kick loops and a rolling bass loop found by the same searches were dropped |
| hardkick | 15 | hard-techno kick one-shots |
| kick909, hat909, openhat909, tom909, rim909 | 4, 2, 3, 1, 1 | other 909 recordings (the independent test of the 909 models); a JD-Xi "909 closed hat" whose energy sat at 150-500 Hz was dropped |
| conga, bongo | 8, 8 | one-shots, open tones and slaps mixed |
| hoover | 6 | hoover one-shots and loops (hard house, hard techno) |

CC BY credits: Cyclez "Hard Techno Schranz Rumble Kick Loop 150 BPM Wav" and "SCHRANZ HARDCORE TECHNO KICK DRUM LOOP 155 BPM", vinodibiza "RUMBLE KICK LOOP A#", Victek "909 Rumble Kick Loop 130BPM", vortexsamples "Distorted Hard Techno Kick - VS_OGKush_Kick_Loops_4_F#_150BPM" and "Hard Techno Dominator Hoover - VS_OGKush_Synths_Loops_1_Fminor_150BPM", BConstructSound "Techno Kick.wav", kaiodeleis "KICK TECHNO.aif", AaronGNP "GNP Bass Drum - 9-oh-no-9.wav", NoiseCollector "909 hat2.wav" and "909 hat open2.wav", DWSD "hat_appetizer.wav", "hat_detailedopen909.wav", "prc_phat909roomtom.wav" and "rim_909analog.wav", Thirsk "Conga1.wav", "Conga2.wav", "Conga3.wav", MrRentAPercussionist "LP Congas Quinto Muted Slap.wav", altemark "conga.wav", Fran89 "Bongo.wav", CorrodedMaster "Bongo2.wav", HUKO "CZ1000 - 135 bpm - Hoover" (pages and licence versions in the manifest).

**Caveats.** Previews are lossy (attacks smeared by a few ms). The Freesound sets are small and mixed (one-shots and loops of different machines and processing): medians are targets, the spread is wide. The 909 models are fitted to one machine's recording; the Freesound 909s test them.

## 2. Method

- **909 drums** (`fit909.py`): third-octave spectra (25 Hz-16 kHz) in time windows after the onset (the kick's in four windows, 0-10, 10-40, 40-150, 150-450 ms, so its pitch fall counts), each relative to the whole sound's power, and the time each band takes to fall 20 dB. Distance = spectral RMS dB difference over the bands within 40 dB of the reference's loudest + 4 x the RMS log2 error of the decay times (0.1 = 7% off). Nelder-Mead in log-parameter space (a real initial simplex, three restarts) on the Detroit recording; engine sounds averaged over 5 seeds; then the same distance to the other 909 recordings, which were not fitted to.
- **Hand drums** (`fithand.py`): the same features in three windows; the score is the median over the 8 recordings of each one's distance (the open stroke fitted; slap, mute and bass strokes are set from it by hand [H]).
- **Rumble** (`fitrumble.py`): on each loop, the 30-150 Hz level through the beat folded over every beat from kick to kick (20 phase bins: the dip after the kick, the swell before the next), and the third-octave shares of 25-800 Hz. The engine's `hardkick` with its rumble, 8 bars at 150 bpm (bars 3-8), is fitted on the median over the loops of pump RMS + spectrum RMS (decay, drive, low-pass, duck depth, release, swell curve, level). The references' kicks are not the engine's: the fit sets the rumble, not the kick.
- **Presets** (`fitpresets.py`, `fithardkick.py`): as dubstep-v2/fit.py, a `curve` (minimum-phase third-octave EQ) moved toward the references' median spectrum render by render; the patch's dynamics by a search on crest, loudness density (the loudest 400 ms at a -1 dBFS peak), band decay times and band shares. The hard kick's distortion makes a curve before it non-linear, so its curve sits after the distortion, before the last clip, and the dynamics were refitted around it.

## 3. What was fitted, and how close (lower is closer)

| Sound | Fitted to | NEW | Old stand-ins |
|---|---|---|---|
| `kick909` | the recorded 909 kick | spectrum 4.14 dB, decay 0.33 | `clubkick` 4.17 / 0.70; `kick` 6.0 / 0.77; kicksub+punch+click 9.0 / 0.73 |
| (test) | 4 other 909 kicks | 7.18 / 1.24 | `clubkick` **6.80** / 1.10; `kick` 7.1 / 1.32 |
| `hat909` | the two recorded 909 closed hats | 8.15 / 0.33 | `metalhat` 16.6 / 1.38; `hat` 23.1 / 1.18; `kithat` 21.1 / 0.56 |
| (test) | 2 other 909 closed hats | 13.1 / 0.75 | `metalhat` **12.4** / 0.69; `kithat` 15.4 / 0.68 |
| `openhat909` | the two recorded 909 open hats | 6.35 / 0.20 | `metalhat` open 15.4 / 2.30; `openhat` 24.8 / 2.01 |
| (test) | 3 other 909 open hats | 13.6 / 0.77 | `metalhat` open 14.1 / 1.96; `openhat` 16.6 / 1.67 |
| `tom909` | the recorded 909 low and high toms | 6.98 / 0.21 | `tom` 8.2 / 1.06; `kittom` 8.3 / 1.83 |
| (test) | 1 other 909 tom | 6.99 / 0.25 | `tom` 9.5 / 1.06 |
| `rim909` | the recorded 909 rimshot | 6.70 / 0.15 | `rim` 10.3 / 0.28 |
| (test) | 1 other 909 rim | 6.46 / 0.48 | `rim` 10.1 / 0.53 |
| `conga` (open) | 8 congas | 9.95 / 0.99 | `darbuka` doum 12.4 / 1.68; `tom` 14.3 / 2.07 |
| `bongo` (open) | 8 bongos | 9.74 / 1.08 | `darbuka` tek 14.6 / 1.37, slap 12.3 / 1.04 |
| `hardkick` | 15 hard-techno kicks | third-octave RMS 7.0 dB (13.3 before the curve); crest 3.8-4.1 dB (refs 7.0); density -9.3 to -10.1 LUFS (-8.6); low band -20 dB in 173-191 ms (192) | TECHNO.md's workaround (kicksub + punch + click, asym, hard clip, transient): crest 6.8, density -9.0, its low band rings for seconds (an asym offset) |
| `hoover` | 6 hoovers | third-octave RMS 6.2 dB (13.9 before the curve); crest 17 dB (refs 12.4) | a polysynth patch by hand: crest 17.0 |
| rumble | 8 kick-and-rumble loops | pump 3.99 dB RMS, spectrum 4.92; level between kicks -6.8 dB (refs -6.1) | the parts by hand (reverb return size 1, asym, three 150 Hz low-passes, follower duck): 4.24 / 5.22, between -10.0; the kick alone: 18.97 / 5.13, -20.0 |

Numbers: 909-numbers.json, hand-numbers.json, rumble-numbers.json, numbers.json; the 909 spectra against the recording in 909.png.

**Reading it honestly.** On the recording they were fitted to, the 909 models are much closer than the old stand-ins (hats by 8-9 dB, decays by 2-10x). On other 909 recordings they are **not** better for the kick and the closed hat (7.2 against `clubkick`'s 6.8; 13.1 against `metalhat`'s 12.4), a little better for the open hat (13.6 against 14.1), better for the tom and rim (7.0 against 9.5; 6.5 against 10.1). The other recordings disagree with each other as much as with the model (two to four previews of different machines and processing), so this shows the limit of one machine's fit, not a better old sound. The rumble's fitted tail is short (T60 0.67 s against Futureproof's 3-5 s reverb): the recorded loops swell from near silence every beat, and a short, hard-driven tail that is silent at each hit and swells back over 1.43 beats matched them best; with a longer `decay` the rumble is denser between kicks (the sources' way; a `tone` and `decay` per brief). The fitted low-pass (390 Hz) is inside the sources' range (96.6-800 Hz). The hard kick is denser and its top dies faster than the references (crest 3.8-4.1 against 7; the high band -20 dB in 6 ms against 48): what is left between its spectrum fit and its dynamics.

## 4. A/B demos

150 bpm, 8 bars (the excerpt 16), through the engine's quick master at -10.5 LUFS (both within 0.4 dB: loudness-matched), 192 kbps MP3; pictures are mel spectrograms, A left, B right; numbers in numbers.json (the changed stems' descriptors and the whole excerpt's band shares and short-term loudness).

| Case | A | B | Picture | What changes |
|---|---|---|---|---|
| Rumble | [rumble-A.mp3](rumble-A.mp3) | [rumble-B.mp3](rumble-B.mp3) | [rumble.png](rumble.png) | the same hardkick and 909 hats; A the parts by hand, B `"rumble": true`. B's rumble pumps (silent on the kick, swells to the next), denser (crest 13.8 to 9.1 dB), and stops with the kick; A's washes on (its low band takes 742 ms to fall 20 dB) |
| Hard kick | [hardkick-A.mp3](hardkick-A.mp3) | [hardkick-B.mp3](hardkick-B.mp3) | [hardkick.png](hardkick.png) | A TECHNO.md's workaround, B `hardkick`: a brighter, harder top (mix 2-5 kHz -28.7 to -23.2 dB), a body that ends (A's low rings) |
| 909 kick | [kick909-A.mp3](kick909-A.mp3) | [kick909-B.mp3](kick909-B.mp3) | [kick909.png](kick909.png) | `clubkick` against `kick909`: the recorded 909's shape (a fast pitch fall, a click, less 150-500 Hz: -10.1 to -18.3 dB of the mix) |
| 909 hats | [hats909-A.mp3](hats909-A.mp3) | [hats909-B.mp3](hats909-B.mp3) | [hats909.png](hats909.png) | `metalhat` (808 tones, centroid 8.2 kHz) against `hat909` / `openhat909` (6-bit grain, centroid 4.9 / 6.8 kHz, the closed hat's highs gone in 46 ms against 119) |
| Groove | [groove-A.mp3](groove-A.mp3) | [groove-B.mp3](groove-B.mp3) | [groove.png](groove.png) | darbuka, `tom`, `rim` against `conga`, `bongo` (open and slap), `tom909` on a free-running 3-step loop, `rim909`; swung 54% |
| Hoover | [hoover-A.mp3](hoover-A.mp3) | [hoover-B.mp3](hoover-B.mp3) | [hoover.png](hoover.png) | a hand patch against `hoover` |
| **Excerpt** | [excerpt-A.mp3](excerpt-A.mp3) | [excerpt-B.mp3](excerpt-B.mp3) | [excerpt.png](excerpt.png) | 16 bars of hard techno with everything together (kick, rumble, 909 hats and clap, percussion with the 3-step tom, acid opening, the hoover in the second half): A the old stand-ins, B the fitted sounds; same acid, clap and patterns |

**Which I would pick:** B in the excerpt, the rumble, the hard kick, the hats and the groove: the rumble is the change a listener hears first (it breathes with the kick instead of washing under it), the hard kick ends instead of ringing, and the percussion has pitch and skin instead of a darbuka's. For the 909 kick alone the choice is closer: `kick909` follows the recorded machine, `clubkick` is as close to other 909 recordings and denser; for hard techno the kick is `hardkick` anyway. The hoover is a colour, not a fit I would trust far (6 mixed references; peakier than they are). All by the numbers and the spectrograms: the owner's ear decides.

## 5. Master test (docs/TECHNO.md gap 4)

`mastertest.py`: the excerpt's fitted sounds in TECHNO.md's DJ form at 150 bpm, 176 bars (4:45): intro 32 bars of kick and rumble (hats from bar 17), main 48 (percussion, acid), breakdown 16 without the kick, peak 48 (the hoover), outro 32; and a version with 8-bar ends (3:28). Each premaster through engine/master.py; short-term loudness (3 s windows, 1 s hop) read over the loudest 2 minutes and per section (numbers.json, "master").

| Track, flags | Integrated | Loudest 2 min: integrated / short-term median / max | Main / peak (median short-term) | Intro / breakdown | True peak | PLR | Limiter max GR |
|---|---|---|---|---|---|---|---|
| DJ ends, `--genre techno --strand hard` at -8.5 (as researched) | -8.7 | -8.4 / -8.0 / -7.8 | -7.9 / -8.0 | -9.5 / -10.8 | -1.03 | 7.6 | 1.6 dB |
| DJ ends, `--strand hard --lufs -8` | -8.1 | -7.9 / **-7.5 / -7.3** | **-7.4 / -7.5** | -8.9 / -10.3 | -1.03 | 7.1 | 1.7 dB |
| DJ ends, `--genre techno` (-9.5) | -9.5 | -9.3 / -8.8 / -8.7 | -8.8 / -8.9 | -10.4 / -11.7 | -1.02 | 8.5 | 1.4 dB |
| short ends, `--strand hard` at -8.5 | -8.6 | -8.6 / -8.2 / -8.0 | -8.1 / -8.2 | -9.7 / -11.1 | -1.03 | 7.6 | 1.5 dB |
| short ends, `--strand hard --lufs -8` | -8.2 | -8.2 / -7.7 / -7.6 | -7.7 / -7.8 | -9.2 / -10.6 | -1.03 | 7.1 | 1.6 dB |
| short ends, `--genre techno` | -9.5 | -9.5 / -9.1 / -9.0 | -9.1 / -9.1 | -10.7 / -12.0 | -1.03 | 8.5 | 1.3 dB |

Reading it: the researched hard-strand level (-8.5) lands the loud sections 0.5 dB under TECHNO.md's aim (-7.5 to -7, Hard Techno previews -7.3); `--lufs -8` lands them at -7.4 to -7.5 short-term (max -7.3) with the true peak at -1.03 dBTP, the limiter reducing at most 1.7 dB and PLR 7.1: the drive comes from the mix (the hard kick, the driven rumble, the clipped drum bus), not from the limiter. So the `hard` strand now masters at **-8** (engine/genres.json, measured here). The default `--genre techno` (-9.5) behaves with long DJ ends: the intro with kick and rumble is only 1.4-1.6 dB under the main sections (a rumble intro is loud), so the integrated level follows the loud sections closely and they read -8.8 to -8.9 (Peak Time / Driving previews -8.6); with short ends the same. The breakdown without the kick sits 3 dB under. Not tested: a track much sparser in its intro than this one (kick alone, no rumble), where the long ends would pull the integrated level down and push the loud section up by a few tenths more.

## Bit-identity

Nine projects rendered with the engine as it was before this pass (commit 48f8280, `git archive`) and with it, sha256 of the audio samples (float32) of the premaster and of the quick master: **identical in all nine**: examples/engine-test, trance-test, trance-modern-test, dubstep-test, latinpop-test; session 007's project and published project; session 014's published project; session 017's project.

## Rebuild

```bash
python3 tools/engine_assets.py install refs-techno-cc0 refs-techno-ccby refs-tr909-detroit
python3 examples/production/techno/fit909.py check       # 909-numbers.json, 909.png (fit: `fit909.py fit [kind]`)
python3 examples/production/techno/fithand.py check      # hand-numbers.json (fit: `fithand.py fit`)
bash tools/remix/waitfree.sh render && python3 examples/production/techno/fitrumble.py check    # rumble-numbers.json (fit: `fit`)
bash tools/remix/waitfree.sh render && python3 examples/production/techno/fitpresets.py hoover  # refits the hoover's curve
bash tools/remix/waitfree.sh render && python3 examples/production/techno/build.py       # the A/Bs (~4 minutes)
bash tools/remix/waitfree.sh master && python3 examples/production/techno/mastertest.py  # the master test (~10 minutes)
```
