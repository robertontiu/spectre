# Cinematic hybrid: the orchestra and trailer sounds, A/B (2026-11-26)

The engine gaps of docs/CINEMATIC_HYBRID.md "Engine mapping" (queue item 13), built in `engine/orchestra.py`
(`strings_section` `basses` in `engine/chamber.py`, the `hall` return in `engine/spacefx.py`; docs/MANUAL.md
"Orchestra and trailer"). The owner delegated tonight's A/B choices: each was picked by measurement where recordings
exist, and is listed below so it can be overruled in the morning.

**A** is the stand-in the brief names in its "Without it" column, **B** the new sound. Each pair is the same phrase
through the same `hall` return (except the hall pair), loudness-matched to -20 LUFS. Rebuild:
`python3 examples/production/cinematic/build.py audio` (renders in a temporary folder) and `... measure` (needs the
reference recordings, below).

| Pair | A (stand-in) | B (new) |
|---|---|---|
| `brass-*.mp3` | `polysynth` horns and low brass | `brass` horns (4 players) and trombones: swell, sfz, stabs, fall |
| `drums-*.mp3` | tuned `tom`, `kittom`, `toba`, `crash` on the downbeat | `timpani` (a crescendo roll at the end), `taiko`, `bassdrum`, `suscymbal` swell |
| `basses-*.mp3` | celli 16th spiccato + `sub` | the same celli + `basses` spiccato an octave down |
| `hall-*.mp3` | `reverb` return, size 0.9 | `hall` return |
| `choir-*.mp3` | six `vox2` tracks by hand + `choir` pad | one `vox2choir` (6 voices) + `choir` pad |
| `trailer-*.mp3` | `supersaw` glide, `toba`, `fmgrowl` + `sub` | `shepard`, `whoosh`, `impact`, `braam` |
| `winds-*.mp3` | `ney` (flute), `polysynth` (clarinet, bassoon) | `woodwind` flute, clarinet, bassoon |
| `accordion-*.mp3` | `organ` | `accordion` (two reeds, musette) |

## Measurements (`measurements.json`)
Third-octave spectrum distance to the recording at the same pitch (mean absolute dB over the bands within 30 dB of the
loudest; steady part 0.3-1.3 s for winds and strings, the first second or so for percussion), median per sound.
The new models were fitted on these same recordings (`fit_winds.py`, `fit_drums.py`, `fit_bass.py`), so this says
how well each model and stand-in reproduces them, not how it generalises to other instruments or rooms.

| Sound | Notes | A (stand-in) | B (new) | B worse than A on |
|---|---|---|---|---|
| horn | 11 | `polysynth` 6.0, `trembita` 6.8 | 2.5 | 1 (Iowa C4) |
| trumpet | 10 | 5.7 | 1.7 | 0 |
| trombone | 11 | 6.5 | 3.7 | 3 (Iowa Bb2, F3, F4) |
| bass trombone | 3 | 9.9 | 2.9 | 0 |
| tuba | 10 | 7.6 | 6.3 | 2 (Iowa Bb1, VSCO F2) |
| flute | 5 | `ney` 6.3 | 2.5 | 2 (C6, G5: the `ney` is close up high) |
| oboe / clarinet / bassoon | 4 / 5 / 5 | 5.6 / 7.0 / 7.5 | 1.3 / 1.6 / 1.3 | 0 |
| basses | 5 | celli 8va + `sub` 14.2 | 5.0 | 0 |
| timpani | 3 | `tom` 39.0 | 4.1 | 0 |
| bass drum | 1 | `toba` 17.3 | 2.9 | 0 |
| suspended cymbal hit / swell | 1 / 1 | `crash` 18.6 / reversed `crash` 23.8 | 3.8 / 1.6 | 0 |

Brass is one model averaged over two collections (University of Iowa MIS ff and VSCO-2-CE's loudest layers); where
they disagree (the notes in the last column, all but one from Iowa) the model sits between them and a stand-in can
come out closer to one of them.

**Hall** (Schroeder T20 per octave, 125 Hz-4 kHz; first reflection): `hall` 2.82 / 2.72 / 2.82 / 2.79 / 2.56 / 1.91 s,
20 ms; `reverb` size 0.9: 4.73 / 4.53 / 4.51 / 4.17 / 3.51 / 2.49 s, 25 ms, no early reflections. Targets: the brief's
2.5-3.5 s with pre-delay and early reflections at 15-35 ms for choirs (gap 5; docs/voice/MIXING.md); concert halls
1.8-2.2 s with a first reflection near 20 ms (Beranek 2004).

**Decay** (ms from the peak to -20 dB): timpani recordings 441-719, `timpani` 879-997, `tom` 1370; bass drum
recording 102, `bassdrum` 340, `toba` 522. The recorded stroke transient stands further above the ring than the
model's; the spectra match, the first 100 ms are softer.

**Fast spiccato** (the brief's "untested" check): 16ths at 100-140 bpm on `strings_section` articulate. Note-to-note
contrast (dB, the envelope's peak in each note's first half against its minimum before the next): basses `/sp` 5-8
against 1-6 for VSCO-2-CE's solo contrabass spiccato overlap-added at the same rate; celli 11 with `/sp`, 7 without;
violins 15-18 with `/sp`, 8 without. An isolated bass spiccato note rang over 1.5 s before `sp_stop_ms`; now
455-645 ms to -20 dB (the recordings 270-720).

## Choices made (overrule any of them)
1. **B for every pair with recordings** (brass, woodwinds, basses, timpani, bass drum, suspended cymbal): closer to the
   recordings on 67 of 75 notes, and on every percussion and string measurement.
2. **The `hall` over the `reverb` return** as the orchestra's room: inside the brief's 2.5-3.5 s range with early
   reflections at 20 ms; the stand-in rings 4.2-4.7 s with none. Default `decay` 2.8 s, the middle of the brief's range
   (`decay` 2.0 for a concert-hall size).
3. **`vox2choir` over hand-made `vox2` stacks**: the same voices (width measured alike: left/right correlation 0.79
   for both); one track instead of six to twelve. The choice is convenience; the sound is the same method.
4. **Trailer effects and accordion B: by ear only, not measured** (no CC0 braam, impact, Shepard riser or accordion
   recording to measure against; all hand-designed and marked [H] in the code).
5. **Brass brightness follows the level** (the recordings: soft to loud gains 13 dB at 2 kHz on trumpet, 30-36 dB on
   trombone, horn and tuba). Woodwinds were recorded at one dynamic only: softer woodwind notes darken by a
   hand-tuned 8 dB per octave above 1 kHz at `dyn` 0.
6. **Basses balance**: `trim` -12.75 dB puts the section at the celli's RMS an octave up [H]; spiccato bow stop at 750 ms
   (fitted to three recorded notes).
7. **Taiko** is hand-tuned (no recording): 3 drums at 72 Hz within 12 ms.

## References (measurement only; not in git)
University of Iowa Musical Instrument Samples (theremin.music.uiowa.edu/MIS.html; free to use): Horn, BbTrumpet,
TenorTrombone, BassTrombone, Tuba, Flute, Oboe, BbClarinet, Bassoon, DoubleBass arco ff. Versilian Studios
VSCO-2-CE (github.com/sgossner/VSCO-2-CE, CC0): brass sustains, timpani, bass drum, suspended cymbal, solo contrabass
spiccato. Fetched into `~/.cache/spectre/refs/cinematic` for the fits and deleted after; the scripts take the folder
as an argument or `REFS=`.
