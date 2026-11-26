# Bass-music tools: A/B, a drop, the master test

Built 2026-11-25/26 for the dubstep session (standing rule 19), from the gaps in docs/DUBSTEP.md "Engine mapping". Each case is a short project (140 bpm, 8 bars, 13.7 s) rendered twice: **A** = the old approximation the research names ("Without it"), **B** = the new tool, same notes. Both go through the engine's quick master at -10.5 LUFS (loudness-matched, no tonal EQ) and come out as 192 kbps MP3. Pictures are mel spectrograms, A left and B right; numbers are in [numbers.json](numbers.json). Parameters and measurements: docs/MANUAL.md "Bass music". Every case has kick (`kicksub` + `kickclick` on F1), `snare909` tuned to 200 Hz and a `sub` on the same 2-bar phrase (F1, F1, Ab1, F1, Eb1).

| Case | A | B | Picture | What to listen for |
|---|---|---|---|---|
| FM growl | [growl-A.mp3](growl-A.mp3) | [growl-B.mp3](growl-B.mp3) | [growl.png](growl.png) | A: polysynth saws, resonant low-pass wobbled at 7 Hz, drive, bitcrush, OTT (a 2011 wobble). B: `fmgrowl`, 3 operators with feedback, unison 3. Its FM index wobbles at a note value with a new rate on each note, its vowel sweeps oo-ee each beat, and each note gets a pitch blip. |
| Synced, per-note modulation | [mod-A.mp3](mod-A.mp3) | [mod-B.mp3](mod-B.mp3) | [mod.png](mod.png) | The same polysynth patch. A: one rate typed in Hz. B: `"rate": "1/8t"` and `/r=` per note (1/8t, 1/16, 1/8, 1/4): the wobble's rhythm becomes the riff. Measured on the notes at steps 0, 8, 16, 24 of each phrase: A 7.2, 7.2, 7.2, 7.7 Hz; B 7.19, 9.16, 4.86, 2.43 Hz (asked: 7.0, 9.33, 4.67, 2.33). |
| Vowel (formant) filter | [vowel-A.mp3](vowel-A.mp3) | [vowel-B.mp3](vowel-B.mp3) | [vowel.png](vowel.png) | A: a resonant band-pass swept each beat (a filter sweep). B: the `vowel` fx swept oo-oh-ah-eh-ee each beat, so the bass talks. The formants are within 2.5% of Peterson & Barney's (MANUAL). |
| Wavetable | [wavetable-A.mp3](wavetable-A.mp3) | [wavetable-B.mp3](wavetable-B.mp3) | [wavetable.png](wavetable.png) | A: pulse-width modulation, the closest the old engine had. B: `wavetable` on the "vocal" table, its position swept over half a bar and back. |
| Resampling | [resample-A.mp3](resample-A.mp3) | [resample-B.mp3](resample-B.mp3) | [resample.png](resample.png) | A: the growl played live. B: the growl printed (its track muted) and played by two `sampler`s: bar 1 cut into 8 slices and re-sequenced as 16ths; bar 2 reversed, pitched down a fifth and an octave at the end of each phrase. |
| Multiband | [multiband-A.mp3](multiband-A.mp3) | [multiband-B.mp3](multiband-B.mp3) | [multiband.png](multiband.png) | A: one drive over the whole growl. B: `multiband`: below 150 Hz compressed and clean; 150 Hz-2.5 kHz folded with OTT; above 2.5 kHz hard-clipped and wider. The fundamental band (40-50 Hz) against the distortion products at 50-150 Hz: A -3.3 dB, B -13.3 dB. |
| Distortion types | [dist-A.mp3](dist-A.mp3) | [dist-B.mp3](dist-B.mp3) | [dist.png](dist.png) | A: the old `drive` (tanh). B: `fold`, then `asym` (even harmonics), then `hardclip`. |
| Comb and flanger | [comb-A.mp3](comb-A.mp3) | [comb-B.mp3](comb-B.mp3) | [comb.png](comb.png) | A: the old `chorus`. B: a `comb` tuned to F4 with its delay swept every 8th (metallic screech), then a `flanger` on the half bar. |
| Vocoder (colour bass) | [vocoder-A.mp3](vocoder-A.mp3) | [vocoder-B.mp3](vocoder-B.mp3) | [vocoder.png](vocoder.png) | A growl on F2 and Db2. B: the same growl through a `vocoder` with an Fm7 carrier, so it rings as a chord. Energy at Ab3, Eb4 and Ab4 (not harmonics of F2), against 150-1500 Hz: A -25.4 dB, B -6.5 dB. |
| Gated reverb | [gatedverb-A.mp3](gatedverb-A.mp3) | [gatedverb-B.mp3](gatedverb-B.mp3) | [gatedverb.png](gatedverb.png) | A 909 snare into a long reverb, without (A) and with (B) the return's `gate`. The return per 16th after each hit: A 0, +3.0, -0.3, -3.2, -6.2 ... -15.4 dB; B 0, +3.0, -0.3, -9.5, -50.7 dB. |
| **Drop** | [drop-A.mp3](drop-A.mp3) | [drop-B.mp3](drop-B.mp3) | [drop.png](drop.png) | 8 bars of a drop. A: everything as the old engine would make it (polysynth wobble with drive, bitcrush and OTT; `kitsnare`, `handclap`; the chops as a faster wobble). B: `fmgrowl` with synced per-note mods through `multiband`, `suppress` and `mseq`; `snare909` and `clap909` into a gated reverb; chops by `sampler` from the growl; clipped drum and bass buses. Against `dubstep_2015` (1/3 octave, re 1 kHz) B is not closer than A: RMS 5.5 dB against 4.8. B is short at 100-250 Hz (-7) and at 2-5 kHz (-4). That is the growl patch's spectrum, which the vowel filter scoops below 300 Hz; it is a mixing job, and the master's EQ (0.7 toward the target) pulls it. |

**The master test** ([mastertest.py](mastertest.py); numbers.json "master"). The B drop runs as 16 bars between an 8-bar intro and a 16-bar outro that fades 14 dB, then through `master --genre dubstep`:

| Flags | Drop, short-term (median / max) | Integrated | True peak | PLR | Most limiting |
|---|---|---|---|---|---|
| `--lufs -8` (the genre's) | -6.5 / -6.4 | -8.2 | -1.03 | 7.1 | 2.6 dB |
| `--lufs -8`, no outro | -6.7 / -6.6 | -8.2 | -1.03 | 7.2 | 2.6 dB |
| `--lufs -8.5` | -6.9 / -6.9 | -8.7 | -1.03 | 7.6 | 2.5 dB |
| `--lufs -8.5`, no outro | -7.3 / -7.3 | -8.7 | -1.03 | 7.7 | 2.5 dB |
| `--lufs -7` | -5.3 / -5.2 | -7.2 | -1.03 | 6.2 | 2.8 dB |
| `--lufs -6.5` | -4.8 / -4.7 | -6.7 | -1.03 | 5.7 | 2.8 dB |

The genre's -8 lands the drop at -6.5 to -6 (the loud previews of current releases) with no change to the master chain: it soft-clips before a true-peak limiter, and the mix's clipped buses do the rest. A long quiet outro lifts the drop by only 0.2-0.4 dB.

Rebuild:

```bash
bash tools/remix/waitfree.sh render && python3 examples/production/dubstep/build.py [case]   # about 1 minute for all
bash tools/remix/waitfree.sh master && python3 examples/production/dubstep/mastertest.py     # about 6 minutes
```

The engine's test project for all of this is `examples/dubstep-test.json`.
