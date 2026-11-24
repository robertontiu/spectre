# Proposal: industry-aimed mastering for trance and pop rock (2026-11-24)

Standing rule 8 (docs/ORCHESTRATION.md): master each genre like the industry does, with sources. This file proposes new `engine/genres.json` entries for `trance` and `rock`. It is a proposal only: engine/master.py and engine/genres.json were left untouched, because another agent is fixing the top-end bug in master.py at the moment. The research behind every value is in docs/TRANCE.md and docs/POP_ROCK.md, under "Mastering (industry practice)".

Labels used below: **[M]** measured (a published measurement), **[E]** engineer or platform guidance (an opinion or a policy, not a measurement), **[T]** tested on Spectre's engine (this file, section "Engine tests"), **[H]** hand-tuned or estimated (no published number exists).

## Recommended configuration

```json
"trance": {
  "master": {"target": "trance", "lufs": -9.0, "tp": -1.0, "eq": 0.7, "translate": 0.4, "mono_below": 120.0}
},
"rock": {
  "master": {"target": "rock", "lufs": -8.5, "tp": -1.0, "eq": 0.7, "translate": 0.3, "mono_below": 120.0}
}
```

| Setting | trance | rock (pop rock) | Basis |
|---|---|---|---|
| `lufs` | **-9.0** (was -10). Use -8.5 only once the mix controls the kick's peaks (see the tests) | **-8.5** (was -10) | [M] Hot Dance/Electronic top 10 (2025): -8.3 average, range -11.3 to -6.2. Hot Rock & Alternative (July 2025): -8.1 average, range -11.9 to -5.1. Billboard Global 200 top 10 (H1 2024): -8.3 ±1 LU. [E] club masters are about -7 to -6 LUFS short-term at the drop. [T] the engine reaches these levels without its true-peak guard holding it back. Trance stays 0.7 LU under the chart average because this engine shaves the clubkick's peaks hard |
| `tp` | -1.0 (unchanged) | -1.0 (unchanged) | [E] Spotify asks for -1 dBTP, or -2 dBTP when a master is louder than -14 LUFS. [M] about 80% of hits peak at or above 0 dBTP. [T] after a 320 kbps MP3 round trip (the website's format), masters at -1 dBTP peaked at -0.5 to -0.9 dBTP, never above 0. -2 dBTP costs trance about 1.6 dB more clipping. Keep -1 for the site. Make a -2 dBTP variant only for distributor uploads |
| target curve | `trance_modern` (below), or keep `trance` | `rock_modern` (below), or keep `rock` | Pestana 2013 shape, 100 Hz-5 kHz unchanged [M]. Era offsets at the extremes [H], derived below |
| `mono_below` | 120 Hz (unchanged) | 120 Hz (unchanged) | [E] mono below about 100-200 Hz (LWMR wiki: 120-200). Club PAs use mono subs, so check in mono (Nihil Young, NI 2024). Low-end focus at 50-120 Hz (same source). No measured value exists, so 120 stays inside the sourced range |
| `eq` | 0.7 | 0.7 | [H] no source. Keep it until the top-end fix lands and the curves are verified on references |
| `translate` | 0.4 | 0.3 | [H] no numeric source. [E] supports the principle: add harmonics so bass reads on systems that roll off below about 80 Hz (Sound On Sound, White/Senior 2001). Trance gets more because its sub-heavy offbeat bass has fewer upper harmonics than a guitar-driven rock low end |
| width (QC, not a setting) | aim at -9 to -6 LU side minus mid | aim at -11 to -7 LU | [M] 2024 top 10: average -8.5 LU, middle half -10.9 to -6. Pop is widest, hip-hop narrowest, alternative in the middle. There are no trance or rock numbers. The test masters measured -6.3 (trance) and -7.7 (rock): both are inside the range |

Short-term maximum is a check, not a setting [M]. Expect it about 1.2-2 LU above integrated: 2024 hits ran -6 ±1 LUFS short-term max, 2-4 LU above integrated. The rock chart's short-term average was -5.3.

## Modernised target curves (proposed new `--target` entries)

dB relative to 1 kHz, per 1/3 octave. Only bands that change are listed. Every other band keeps its current measured value, so 80 Hz-5 kHz (rock) and 100 Hz-6.3 kHz (trance) are unchanged Pestana.

| Hz | `trance` now | **`trance_modern`** | `rock` now | **`rock_modern`** | Uncertainty |
|---|---|---|---|---|---|
| 31.5 | -11 | **-9** | -15 | **-12.5** | ±3 dB |
| 40 | -7.5 | **-5** | -11.5 | **-9** | ±3 |
| 50 | -3 | **-1** | -7 | **-5** | ±2.5 |
| 63 | +0.5 | **+2** | -3 | **-1.5** | ±2 |
| 80 | +4.5 | **+5** | +1.5 | **+2** | ±1.5 |
| 125 | +9 | **+8.5** | +7 | 7 | ±1.5 |
| 160 | +6.5 | **+6** | +6.5 | 6.5 | ±1.5 |
| 6300 | -4 | -4 | -8 | **-7.5** | ±1.5 |
| 8000 | -6 | **-5.5** | -9.5 | **-8.5** | ±2 |
| 10000 | -8 | **-7** | -12.5 | **-11** | ±2.5 |
| 12500 | -11.5 | **-9.5** | -16 | **-13.5** | ±3 |
| 16000 | -18 | **-14.5** | -23 | **-19** | ±4 |

**How the offsets were derived (estimates [H], from qualitative measurements [M]).** Nobody publishes a numeric 1/3-octave spectrum of 2015-2025 trance or pop rock. iZotope's Tonal Balance Control targets and its "2024 Mastering Trends" preset exist only as plugin files and images, and the Beatport studies (e.g. arXiv 2509.11474, 3,500 tracks) report no per-genre band levels. So the offsets come from the direction and rough size of these findings:
- **Low end, up 1.5-2.5 dB at 31.5-63 Hz.** Pestana et al. found that recent decades have "an extended low frequency response with a lower resonant peak" and a flatter spectrum. Țînț & Drăgulin (2025; Billboard year-end top 30, iZotope TBC) found the 2020 set had the most low and low-mid energy of 1990-2020. Trance kicks are tuned at about 48-55 Hz (docs/TRANCE.md). So the trance peak moves slightly down (+2 at 31.5-63, -0.5 at 125-160), and rock gains sub (modern pop rock carries electronic sub under the kit). The size is chosen to stay well inside the low end's genre spread in Pestana (more than 5 dB). It is not measured.
- **High end, up 0.5-4 dB from 8 to 16 kHz, rising with frequency.** Pestana's genre curves pool 1950-2010 #1 singles, and pop and rock lean on 1960s-80s records. The iZotope decade comparison shows 1980s-era masters with nothing above 16 kHz and modern digital masters extending to about 20 kHz. That is the reason for the largest offset at 16 kHz (the band covers 14-18 kHz). Two findings argue against a big lift: the Țînț & Drăgulin 2020 set had *less* high end than 2000 and 2010, and Pestana notes the genre high-end differences are "negligible" against the overall era brightening. So the offsets stay small at 8-10 kHz. Trance gets less than rock because "electronic" was already among Pestana's brightest genres. Trance with constant 16th hats is percussion-heavy, and more percussion means more treble (Elowsson & Friberg 2017), so trance is not darkened.
- **Interaction with the top-end bug.** The engine currently lands 2-7 dB *hotter* than target above about 8 kHz. Once that is fixed, masters will land on whatever curve is chosen. With the current Pestana curves they would get noticeably darker than recent Spectre masters. The modern offsets recover about 1-4 dB of that.

**How to remove this uncertainty (recommended next step).** Measure 10-20 reference masters per genre with the engine's own analyser (`third_octave` on the mid channel, gated, normalised to 1 kHz) and take the median per band. Good candidates are recent Beatport uplifting and progressive trance top-100 tracks, and modern pop rock such as Paramore, The Killers, Imagine Dragons, Foo Fighters and sombr. This needs audio files that the owner owns. None could be obtained or downloaded here.

## Engine tests (read-only; engine snapshot from 2026-11-24, before the top-end fix)

Method: a copy of `engine/` in /tmp rendered `examples/trance-test.json` and `examples/poprock-test.json`, then called `master.master()` with each genre's settings at several `--lufs` values. Measured: the engine's own report values; the clipper's input peak above its ceiling (the most the soft clipper shaved, in dB); the share of 4x-oversampled samples above the clipper's knee; and the true peak after a 320 kbps MP3 encode and decode with ffmpeg (the website's format).

| Genre | `--lufs` | LUFS out | dBTP | PLR | ST max | LRA | Limiter GR max | TP guard | Clipper shaves (peak) | Samples in clip knee | MP3 true peak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| trance | -10 | -10.2 | -1.03 | 9.2 | -8.9 | 2.4 | 1.1 | -0.16 | 6.8 dB | 1.6% | -0.69 |
| trance | -9 | -9.3 | -1.03 | 8.3 | -8.0 | 2.5 | 1.3 | -0.18 | 8.0 dB | 2.2% | -0.62 |
| trance | -8.5 | -8.7 | -1.03 | 7.7 | -7.5 | 2.7 | 1.4 | -0.20 | 8.7 dB | 2.8% | -0.57 |
| trance | -8 | -8.3 | -1.03 | 7.2 | -7.1 | 2.8 | 1.6 | -0.21 | 9.4 dB | 3.6% | -0.51 |
| trance | -7 | -7.3 | -1.03 | 6.3 | -6.1 | 2.9 | 1.9 | -0.23 | n/m | n/m | n/m |
| trance | -8.5 @ -2 dBTP | -8.8 | -2.03 | 6.8 | -7.6 | 2.8 | 1.8 | -0.22 | 10.1 dB | 4.8% | -1.52 |
| rock | -10 | -10.1 | -1.05 | 9.0 | -8.6 | 4.1 | 0.7 | none | 3.3 dB | 0.2% | -0.94 |
| rock | -9 | -9.1 | -1.03 | 8.1 | -7.7 | 4.1 | 0.8 | none | 4.3 dB | 0.6% | -0.88 |
| rock | -8.5 | -8.5 | -1.04 | 7.5 | -7.1 | 4.0 | 0.8 | none | 5.0 dB | 1.1% | -0.79 |
| rock | -8 | -8.0 | -1.03 | 7.0 | -6.7 | 4.0 | 0.8 | none | 5.6 dB | 1.7% | -0.78 |
| rock | -7 | -7.1 | -1.03 | 6.1 | -5.7 | 3.9 | 1.0 | none | n/m | n/m | n/m |
| rock | -8.5 @ -2 dBTP | -8.6 | -2.04 | 6.5 | -7.2 | 3.9 | 0.9 | none | 6.1 dB | 2.6% | -1.74 |

n/m: not measured in that run. "Clipper shaves" is the drive-scaled input peak above the clipper ceiling. Most of it is kick and snare transients.

**Findings**
1. **The "-9.5 LUFS engine limit" in docs/MASTERING.md is out of date for these examples.** The true-peak guard only trims about 0.2 dB, and both genres reach -8 and even -7 LUFS while staying at or under -1 dBTP. The limiter does little (at most 0.7-1.9 dB of reduction); the **soft clipper does the work**.
2. **Trance's cost is the clubkick's crest.** Even at today's -10 the clipper shaves 6.8 dB off the kick peaks, and every extra LU adds about 0.7-0.8 dB more. Working mastering engineers keep clipping to about 1-2 dB per stage (Nihil Young, NI 2024) and split the work over several stages. Spectre is already past that at -10, so trance gets -9 rather than the chart -8.3. The fix belongs in the mix: tame the kick's peak with a clipper or saturator on the kick or drum bus. Mix-bus clipping is common EDM practice. As a rule of thumb, once the premaster's kick peaks sit within about 4-5 dB of the loud passages, `--lufs -8.5` is fine.
3. **Rock is clean down to about -8.5.** The clipper shaves 5 dB of peaks (1.1% of samples), LRA holds at 4.0 (the verse-chorus contrast survives) and PLR is 7.5, close to the 2010-2020 hit average of 9.3 minus the loudness difference. -8 is still plausible (PLR 7.0, but the engine warns under 7). -8.5 is the recommended value.
4. **MP3 safety.** At -1 dBTP, the 320 kbps MP3 decodes peaked 0.1-0.5 dB higher than the WAV but stayed at or under -0.5 dBTP. Overshoot grows with loudness (trance -0.69 at -10 to -0.51 at -8). No clipping in the website's files.
5. **Width doesn't change with loudness** (trance -6.3 to -5.8 LU, rock -7.7 LU).

## What the engine can't do yet (and what would close the gap)
- **Staged or transient-aware clipping.** One soft clipper takes 7-10 dB off trance kick peaks. Industry chains spread this over a mix-bus clipper, a mastering clipper (1-2 dB) and a limiter. Possible engine options: a clip stage on the drum peaks before the glue, or report `clip_peak_db` in the master report and warn above about 6 dB. Proposed, not implemented.
- **Distortion metric in the report.** The report has no clipper statistics. The tests used a spy on `soft_clip`. Adding `clip_peak_db` and `clip_knee_pct` to the report would let producers see the cost of loudness.
- **Codec check.** An optional MP3/AAC round-trip true-peak measurement in QC (the method above) would cover the website and lossy streaming.
- **Separate club and streaming masters.** Club practice is louder (-7 to -6 short-term at the drop) and often above 0 dBTP; streaming guidance is -1 or -2 dBTP. One master per track is a choice. An optional `--tp -2` streaming variant is cheap (about 0.1 LU quieter here, more clipping).
- **Sidechain pumping is a mix decision.** The master's glue (2:1, 30/200 ms, about 0.7 dB) is too gentle to undo or add pumping. Keep the pump in the mix (docs/TRANCE.md).
- **Section-aware level rides.** Engineers ride sections by fractions of a dB (Greg Calbi on "Too Sweet": about +0.4 dB in the choruses, iZotope 2025). The engine applies one global drive.

## What changes against the current genres.json
- `trance.lufs` -10 to -9; `rock.lufs` -10 to -8.5. "Engine-limited" was the reason for -10, and these tests don't support it.
- New optional curves `trance_modern` and `rock_modern`: the same as the measured curves in the mids, with era offsets of +1.5 to +2.5 dB at 31.5-63 Hz and +0.5 to +4 dB at 8-16 kHz. These are estimates and should be adopted only after the top-end fix lands and the producer listens. The cleanest path is to verify against owned reference tracks first.
- `tp`, `mono_below`, `eq` and `translate`: unchanged. `tp` and `mono_below` are now sourced (see the docs); `eq` and `translate` are still hand-tuned.
- Update the `hand_tuned` lists: remove "lufs -10 is an engine-limited choice", add "target offsets at 31.5-63 Hz and 8-16 kHz (era estimate)".

## Sources
- iZotope, LUFS and tonal analysis of 10 top-charting dance and electronic songs (2025): https://www.izotope.com/en/learn/dance-electronic-analysis
- iZotope, LUFS and tonal analysis of top-charting rock and alternative songs (2025): https://www.izotope.com/en/learn/rock-alternative-analysis
- iZotope, Mastering trends 2024 (54 Billboard Global 200 top-10 songs): https://www.izotope.com/en/learn/mastering-trends
- iZotope, 1920s to now: comparing tonal balance in popular music: https://www.izotope.com/en/learn/comparing-tonal-balance-in-popular-music
- Mastering The Mix, Mastering trends for 2026 (top 15 Spotify songs of 2025): https://www.masteringthemix.com/blogs/learn/mastering-trends-for-2026
- Țînț & Drăgulin (2025), From data to hits (Billboard year-end top 30, 1990-2020): https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335
- Pestana, Ma, Reiss, Barbosa & Black (2013), Spectral characteristics of popular commercial recordings 1950-2010, AES 135: https://www.aes.org/e-lib/browse.cfm?elib=17010
- Elowsson & Friberg (2017), LTAS in popular music and its relation to the level of the percussion, AES 142: https://www.aes.org/e-lib/browse.cfm?elib=18638
- Tamer (2021), Spectral and dynamic analyses of popular music playlists, JAES 69(5) (abstract only: steeper presence-band slope in current playlists): https://aes2.org/publications/elibrary-page/?id=21036
- Mourgela, Quinton, Bissas, Ronan & Reiss (2024), Exploring trends in audio mixes and masters, AES 157: https://arxiv.org/pdf/2412.03373
- Gerdes & Siedenburg (2023), Lead-vocal level in recordings of popular music 1946-2020, JASA Express Letters 3(4): https://doi.org/10.1121/10.0017773
- Spotify, Loudness normalization: https://support.spotify.com/artists/article/loudness-normalization/
- Ian Shepherd, Spotify upload true peak: https://productionadvice.co.uk/spotify-upload-true-peak/
- Hugh Robjohns, Sound On Sound, How loud should master tracks intended for streaming be (2019): https://www.soundonsound.com/sound-advice/q-how-loud-should-master-tracks-intended-streaming
- Ian Shepherd for iZotope, How to master metal: https://izotope.com/en/learn/how-to-master-metal.html
- Native Instruments, Mastering with Nihil Young: https://blog.native-instruments.com/mastering-with-nihil-young/
- Dance Music NW (A. Hume, 2018), Electronic music mastering, LUFS and true peak: https://www.dancemusicnw.com/electronic-music-mastering-lufs-and-true-peak-explained/
- Sound On Sound (P. White, M. Senior, 2001), Increasing loudness in dance music production: https://www.soundonsound.com/techniques/increasing-loudness-dance-music-production
- LWMR wiki, Low end management: https://tuttopassastudios.github.io/LWMR-wiki/Topics/Mixing/Low-End-Management
- Not reachable here: github.com/alunxu/edm-overspec (per-genre Beatport features; permission not granted in time), and the Pestana PDF on joshreiss.github.io (proxy refused direct download; read through WebFetch).
