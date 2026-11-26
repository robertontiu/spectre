# Bass music, second pass: recorded references, fitted sounds, why Captive doesn't peak

Built 2026-11-26 after the owner's request: "Download samples for each of the sounds, then compare our synthesized sounds to the real ones and fix the gaps", and on session 017 "Captive": "The track is ok, but there's just some feeling that it doesn't quite peak at the genre." The first pass (examples/production/dubstep/) built the tools from the research; this one measures them against recordings. Everything new is opt-in (docs/MANUAL.md "Bass music, fitted"): a project that names none of it renders exactly as before.

## 1. The references

118 sounds from Freesound, each checked on its own page for its licence: **103 CC0 1.0, 9 CC BY 3.0, 6 CC BY 4.0**; the HQ previews (128 kbps MP3, downloadable without an account) measured, never used in a track, never committed. Listed with URL, author, licence, size and sha256 in `engine/third_party.json` (`refs-dubstep-cc0`, `refs-dubstep-ccby`, optional; `python3 tools/engine_assets.py install refs-dubstep-cc0 refs-dubstep-ccby` puts them in `~/.cache/spectre/refs/dubstep/<role>/`).

| Role | n | What they are |
|---|---|---|
| growl (modern / FM) | 11 | one-shots and phrases tagged dubstep growl, FM growl, Serum growl |
| riddim | 8 | riddim and tearout bass loops and stabs (140-150 bpm) |
| wobble (LFO) | 10 | 1/8 and 1/16 wobble loops, FM wubs |
| reese | 8 | reese and neuro bass loops |
| sub | 6 | sine subs and sub lines |
| snare | 10 | dubstep, brostep and tearout snares |
| clap | 8 | clap one-shots (EDM, dubstep, layered) |
| kick | 9 | dubstep and EDM kicks |
| hats | 8 | closed hats (electronic) |
| screech | 8 | screech basses and leads |
| vocal chop | 8 | vocal chops and shots |
| riser | 8 | noise and synth risers, uplifters |
| impact | 8 | impacts, booms, hits |
| downlifter | 8 | downlifters, downsweeps |

CC BY credits (the licence asks for them): OttoRecV8 "Dubstep Growl like Skrillex !", Ongitak "B9 Wobble LFO Bass8d", AdRem1 "Brostep Fm Wub", emmithi123 "Reese Bass" and "Dubstep kick drum", tim.kahn "subby" and "subby2", shainexedubstep "Dubstep Snare", a deleted Freesound user's "Big Room Clap", Bertrof "Dub Kick v1", MakoFox "Screech", mkoenig "Vocal Chop Fx", Sabacky "Riser - Gleamer", l8ent_space "DSGNDown SubDownlifter 1Bar", sandyrb "PINK NOISE DOWNSWEEP 01" (pages in the manifest).

**Caveats.** Previews are lossy: attack times are smeared by a few ms (reported, not used) and joint stereo can narrow the side a little. The set is what Freesound has under open licences: one-shots and loops of mixed provenance and quality, not released masters; the median is the target, the spread is wide (the tables give p25 and p75). Roles were picked by title and tag, then checked by their numbers (a "sub" whose energy sat above 150 Hz would have been dropped; none was).

## 2. The comparison

`describe.py` measures every sound the same way, trimmed and peak-normalised to -1 dBFS: third-octave spectrum (shares of the total, and above 150 Hz for bass voices whose lows belong to the sub), tilt, spectral centroid and its movement, flatness, harmonicity and even/odd harmonics, the level modulation of 300 Hz-6 kHz (rate, note value, depth), crest, the time each band takes to fall 20 dB, side against mid per band, and loudness density (the loudest 400 ms in LUFS at a -1 dBFS peak). `refs.py` runs it on the references, on the engine's sounds before this pass (OLD: the first A/B's patches and session 017's tracks) and after (NEW), and writes **[tables.md](tables.md)** (every role, every metric) and refs-numbers.json. The gaps, ranked by what a listener hears first (reference median against OLD):

| # | Role | Gap | Reference | OLD | NEW |
|---|---|---|---|---|---|
| 1 | growl (017's captor) | energy above 150 Hz in 2-5 / 5-16 kHz | -6.8 / -7.5 dB | -13.7 / -17.8 | -5.1 / -6.9 (`growl`) |
| 2 | growl | movement of the brightness (centroid, std in octaves); median centroid | 0.69 oct; 1.2 kHz | 0.20; 0.80 kHz | 1.1; 2.1 kHz |
| 3 | riddim (017's husk) | 2-5 / 5-16 kHz above 150 Hz; side against mid above 1 kHz | -5.4 / -10.6; -0.3 dB | -21.5 / -24.6; -15 | -5.4 / -10.3; +2.5 (`riddim`) |
| 4 | snare (017's stack) | 500 Hz-2 kHz / 150-500 Hz of the total; crest | -13.3 / -6.3 dB; 12.2 dB | -3.6 / -15.2; 18.8 | -14.2 / -2.4 (150-500 Hz now 3.8 dB over); 10.6 (`snare`) |
| 5 | snare | loudness at a -1 dBFS peak; highs -20 dB after | -9.5 LUFS; 242 ms | -15.0; 117 | -8.9; 274 |
| 6 | kick (017's stack) | crest; loudness at -1 dBFS peak | 8.4 dB; -11.5 LUFS | 14.4; -14.3 | 9.8; -10.2 (`kick`) |
| 7 | impact | 60-150 / 150-500 Hz of the total; crest; side above 1 kHz | -4.8 / -10.4 dB; 12.2; -1.4 dB | -28 / -40; 2.7; mono | -6.3 / -4.5 (150-500 Hz now 6 dB over); 10.8; -1.8 (`"fx_model": 2`) |
| 8 | riser, downlifter | side against mid 150 Hz-5 kHz; riser 60-150 Hz | -4 to -5 / -1 dB; -25 dB | mono; -67 | -4.1 / +1.3; -24 |
| 9 | wobble | loudness at -1 dBFS peak; crest | -8.5 LUFS; 10.8 dB | -14.6; 15.2 | -9.1; 10.8 (`wobble`) |
| 10 | reese | loudness at -1 dBFS peak; 5-16 kHz above 150 Hz; side below 150 Hz | -5.9 LUFS; -17.7; -24 dB | -18.2; -34.2; -3 | -13.4; -19.4; -14 (`reese`) |
| 11 | clap (909) | 5-16 kHz above 150 Hz; loudness at -1 dBFS peak | -8.5 dB; -15.6 | -16.9; -19.1 | -7.8; -14.7 (`clap`) |
| 12 | hats (metalhat) | -20 dB decay; 60-150 Hz | 42 ms; -48 dB | 95; -140 | 45; -81 (`hats`) |
| - | sub | matches: one band at the note, mono, loudness -6.7 against -6.7 LUFS at -1 dBFS peak | | | unchanged |
| - | vocal chop (017's `singer` phrase) | cleaner, more harmonic and mono than chopped vocals: HNR 11.9 against 1.1 dB, side -200 against -7 dB (in tables.md when the voicebanks are installed) | | | not changed: a voice is the producer's choice |

The common thread: the engine's sounds were **darker, peakier (less dense at the same peak) and narrower** than recorded ones, and its bass timbres moved less. Recorded dubstep sounds come out of OTT and clippers; the engine's came out of the synthesis with a light touch of both.

## 3. The fixes (engine/dubstep2.py, engine/bass_presets.json)

- **Presets**, fitted to the references: `growl`, `riddim`, `wobble`, `reese`, `screech`, `snare`, `clap`, `kick`, `hats`. Each is a patch and chain set by hand against the descriptors (dynamics, movement, width), plus a `curve` (a minimum-phase third-octave EQ) fitted by `fit.py`: four renders, each moving the curve 0.8 of the way to the references' median spectrum (smoothed over five bands, anchored where the sound's energy is). Third-octave RMS distance to the references' median before and after the curve: growl 3.8 to 2.0 dB, riddim 4.4 to 2.7, wobble 4.9 to 3.1, reese 7.3 to 5.9, screech 5.5 to 3.8, snare 10.7 to 7.1, clap 9.6 to 3.0, kick 9.5 to 9.3 (a sine is a line where recorded kicks are a band: its crest and density were fitted, its spectrum only partly), hats 4.8 to 3.5.
- **New fx**: `curve`, `transient` (attack / sustain from two followers), `widen` (mono-compatible width above a frequency, for mono sources).
- **Transitions** (`"fx_model": 2`): stereo, with a body (the impact a pitched boom 170 to 50 Hz plus a noise body and a room; the riser with the rising saws and a low noise; the downlifter with a falling tone).
- **Bit-identity**: none of this runs unless a project names it. Checked: see "Bit-identity" below.

## A/B demos

140 bpm, through the engine's quick master (both at -10.5 LUFS), 192 kbps MP3; pictures are mel spectrograms, A left, B right; numbers in [numbers.json](numbers.json) (the changed stem's descriptors for A and B beside the references' median: no reference audio is published).

| Case | A | B | Picture | What to listen for |
|---|---|---|---|---|
| Growl | [growl-A.mp3](growl-A.mp3) | [growl-B.mp3](growl-B.mp3) | [growl.png](growl.png) | 017's captor against the `growl` preset on drop 1A's notes, 017's drums and sub under both. B is brighter (2-5 kHz above 150 Hz -14.0 to -4.7 dB, references -6.8) and its brightness moves with every wub (0.20 to 0.99 octaves, references 0.69). |
| Riddim | [riddim-A.mp3](riddim-A.mp3) | [riddim-B.mp3](riddim-B.mp3) | [riddim.png](riddim.png) | 017's husk against `riddim`, drop 2's notes. 2-5 kHz -21.5 to -5.0 dB (references -5.4); wide above 150 Hz like the references. |
| Wobble | [wobble-A.mp3](wobble-A.mp3) | [wobble-B.mp3](wobble-B.mp3) | [wobble.png](wobble.png) | The old LFO wobble against `wobble`: denser (crest 17.0 to 12.1 dB, references 10.8). |
| Reese | [reese-A.mp3](reese-A.mp3) | [reese-B.mp3](reese-B.mp3) | [reese.png](reese.png) | Detuned saws against `reese`: a top (5-16 kHz -34.4 to -20.3 dB, references -17.7), a mono low, denser (still short). |
| Screech | [screech-A.mp3](screech-A.mp3) | [screech-B.mp3](screech-B.mp3) | [screech.png](screech.png) | The first A/B's comb screech against `screech`. |
| Drums | [drums-A.mp3](drums-A.mp3) | [drums-B.mp3](drums-B.mp3) | [drums.png](drums.png) | 017's kick, snare and hats against the presets, drop 1C's pattern. Snare crest 20.2 to 10.6 dB (references 12.2), its loudness at a -1 dBFS peak -15.6 to -9.7 LUFS (references -9.5); kick crest 15.0 to 11.4 (8.4). |
| Transitions | [transitions-A.mp3](transitions-A.mp3) | [transitions-B.mp3](transitions-B.mp3) | [transitions.png](transitions.png) | A riser into an impact, a reverse cymbal, a downlifter: mono and thin against `"fx_model": 2`. |
| **Drop** | [drop-A.mp3](drop-A.mp3) | [drop-B.mp3](drop-B.mp3) | [drop.png](drop.png) | 017's build 1b into drop 1A as published (A), and with the captor, kick, snare and hats swapped for the presets and `"fx_model": 2` (B), everything else as published. B is brighter and its drums denser; it is **not** louder or more of an arrival (below): the presets fix timbre, not the arrangement. |

The drop excerpt through the genre master as 017 was mastered (`--genre dubstep --lufs -8.5` on these 12 bars, so the absolute level is set by the excerpt's own integrated target; compare A with B, not with the full track):

| | A (as published) | B (presets, fx_model 2) |
|---|---|---|
| drop 1A short-term LUFS, median / max | -8.2 / -7.8 | -8.1 / -7.7 |
| momentary step into the drop (its first 2 s against the build's last 2 s) | +1.9 LU | +0.8 LU |
| drop 1A against `dubstep_2015` (1/3 octave re 1 kHz): RMS | 3.8 dB | 3.5 dB |
| ... at 5-8 kHz / 10 kHz / 12.5-16 kHz | -1.9 to -3.0 / -3.7 / -5.1 to -5.8 | -1.3 to -1.4 / -1.6 / -1.8 to -2.0 |
| ... at 63-100 Hz | -1.7 to -3.8 | -1.9 to -4.3 |
| kick / snare stem crest in the drop | 17.6 / 26.4 dB | 14.6 / 16.6 dB |
| kick / snare peak against the bass stems' peak | +3.9 / +5.3 dB | -2.8 / -1.8 dB |

Reading it: the top end comes up to the genre's curve (the master no longer has to lift it) and the drums lose 3-10 dB of crest, but the excerpt is no louder and the step into the drop is smaller, because the new kick, snare and hats play in the build too and are denser there as well, and B's riser is fuller. The presets were set at their default levels, not balanced by ear: a remix sets the levels and, above all, the arrival.

## Why Captive doesn't peak

Measured on a render and master of `sessions/017-captive/project.json` outside the session folder (identical to the published master: -8.7 LUFS integrated, -1.03 dBTP, PLR 7.6, short-term max -5.9), by [diagnose.py](diagnose.py) ([diagnosis.json](diagnosis.json)); the sounds against the references from tables.md. Ranked by how much each takes from the peak, most first:

1. **The drop does not arrive; it continues.** Build 1b sits at -8.8 LUFS short-term (median), drop 1A at -7.2: the first bar of the drop is only +1.2 LU over the build's last bar (momentary medians). There is no gap: the build's quietest 400 ms in its last beat is -8.1 LUFS and its last beat peaks at -1.1 dBFS. The low end does not step up either: 50-80 Hz in the drop's first two beats is 0.8 dB *under* the build's last two (the sub already plays in the build, 3 dB down, and the captor at full range from its filter's top). The one transition on the downbeat is the old impact (`enter` `impact` 0.7): a mono 40 Hz sine with nothing in 60-500 Hz (-28 to -40 dB of its energy, against -5 to -10 in recorded impacts) and a crest of 2.7 dB (12.2 in recorded ones). DUBSTEP.md's own practice: elements removed before the drop "to create a silence gap"; silence and gaps are "part of the impact". The journal chose "no silence before the drop (the taking is an interruption)", but the interruption reads as more of the same. And the loudest moment of the track is not a drop: panic 2 reads -5.9 LUFS, drop 1 -7.2 / -7.0 / -6.8. **Addressed by this pass only in part:** `"fx_model": 2` gives the downbeat a stereo, full-bodied impact (60-150 Hz -6.3 dB of its energy, crest 10.8). The arrival itself is arrangement: in the drop A/B the presets alone made the step smaller (+1.9 to +0.8 LU) because the build carries the same drums. For the remix: thin the build's last bar or two (drums and sub out, or the captor's filter closing), a half to one beat of silence before the drop, the sub entering *on* the drop (a dive into it), the new impact, and the panic no louder than drop 1.
2. **The lead growl is dark and static.** The captor's energy above 150 Hz is 14.1 dB under at 2-5 kHz and 18.0 dB under at 5-16 kHz (relative shares; references -6.8 and -7.5), its brightness moves 0.2 octaves (references 0.69) and centres at 0.8 kHz (1.2). After the master's EQ (already +1.5 to +2.7 dB at 1.6-16 kHz, near its limit) drop 1 still reads -1.9 dB at 1.6-4 kHz, -2.8 at 5-10 kHz and -5.0 at 12.5-16 kHz against `dubstep_2015`. This is the "doesn't peak" a listener hears first in the sound itself: the bass that is the genre's lead has no bite and no motion in its top. **Addressed:** the `growl` preset (2-5 / 5-16 kHz -5.1 / -6.9 dB, movement 1.1 octaves; in the drop A/B the master's top comes to -1.3 to -2.0 dB of the curve). A remix can keep the captor's notes, rates and character and put its body through the preset (or the preset's chain on the captor).
3. **The drums are spikes, and the limiter shaves them.** In drop 1A the kick stem's crest is 17.6 dB and the snare's 26.3 dB (recorded dubstep kicks and snares: 8.4 and 12.2 as one-shots); the snare's peaks sit 5 dB over the bass's while its RMS is 6.1 dB under it, so after the drum bus's clip and the master's limiter what is left of it is small. Its tone is the wrong way round for the genre: 10 dB too much at 500 Hz-2 kHz (the 909 clap layer) and 9 dB too little at 150-500 Hz (the body) against recorded dubstep snares. **Addressed:** the `snare` and `kick` presets (one-shot crest 10.6 and 9.8 dB, loudness at -1 dBFS peak -8.9 and -10.2 LUFS against the references' -9.5 and -11.5; in the drop 16.6 and 14.6 dB with the hats and the bus). Their level against the bass is the remix's to set by ear.
4. **The drop is 1 LU under the genre's loud sections.** Drop 1 at -7.2 / -7.0 / -6.8 LUFS short-term against loud dubstep previews at -6 (middle half -6.5 to -4; DUBSTEP.md, Mixgraph); its peak-to-short-term ratio is 5.6-6.0 dB. The master's settings explain about 0.5 LU (`--lufs -8.5`; the first pass measured `-8` landing a drop at -6.5), the rest is density: 017's captor reaches -9.0 LUFS at a -1 dBFS peak where recorded growls reach -7.8, the riddim husk -9.4 against -5.9. **Addressed in part:** the presets reach the references' density at the source (growl -7.6, riddim -7.4, wobble -9.1, snare -8.9, kick -10.2); then `--lufs -8` in the master, reading the drop's short-term loudness (aim -6.5 to -6) as MANUAL "Mastering a loud drop" says.
5. **The low end is one note.** Against `dubstep_2015` drop 1 reads -10.1 dB at 31.5-40 Hz (nothing is written below F#1 = 46 Hz; the master's EQ is at its +4 dB limit there), on target at 50-63 Hz, and -3.7 dB at 80-125 Hz: the sub is one sine at 46 Hz and the kick's sub layer sits on C#2 (69 Hz) with little below or above it. Recorded kicks spread their energy below 60 Hz with a longer dive (the `kick` preset: a 30-semitone, 40 ms dive). Part of this is the key and the deep frame (accepted in the session, rightly). **Addressed in part** (the kick); a sub dive into the drop would also give point 1 its weight.
6. Not a cause: drop 2 at -8.0 to -8.2 is quieter by design (the arc's "cold acceptance"), and the master's quiet outro lifts the drops by only 0.2-0.4 dB (first pass).

**For the remix brief, in order:** the arrival (1), the growl's top and motion (2), the snare and kick (3), then the master at `--lufs -8` (4); keep the arc, the voices, the notes and the empty bar of drop 2.

## Bit-identity

Nine projects rendered with the engine as it was before this pass (commit f1d51b6, `git archive`) and with this pass, sha256 of the audio samples of the premaster and of the quick master: **identical in all nine**: examples/engine-test, trance-test, trance-modern-test, dubstep-test, latinpop-test; session 007's project and published project; session 014's published project; session 017's project. (The premaster files' own hashes differ between any two renders: libsndfile writes a time stamp into the float WAV's PEAK chunk; the samples do not.)

## Rebuild

```bash
python3 tools/engine_assets.py install refs-dubstep-cc0 refs-dubstep-ccby
bash tools/remix/waitfree.sh render && python3 examples/production/dubstep-v2/refs.py      # tables.md, refs-numbers.json (~1 min)
bash tools/remix/waitfree.sh render && python3 examples/production/dubstep-v2/fit.py       # refits engine/bass_presets.json (~30 s)
bash tools/remix/waitfree.sh render && python3 examples/production/dubstep-v2/build.py     # the A/Bs (~5 min; "drop" masters twice)
# the diagnosis: diagnose.py's docstring (a render and master of 017 outside the session folder)
```
