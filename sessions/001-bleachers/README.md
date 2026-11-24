# 001: Bleachers

| | |
|---|---|
| Feeling | **defiance** (picked at random from a list of feelings) |
| Feedback | it came across closer to longing: "it didn't feel aggressive enough" |
| Length / tempo / key | 3:12, 72 bars, 90 bpm, F minor, swing 0.53 |
| Genre | Stomping boom-bap and 808-trap hybrid: stomp-stomp-clap groove, gritty 808s that slide up, organ stabs, a brass-like chant lead, gang-vocal hits |
| Iterations | 27 (loop, arrangement, transitions/detail, mix/master, final listen) |
| Master | `studio.py master v028 --genre hiphop --eq 0.9 --lufs -11` (master version 2): -11.1 LUFS, -1.06 dBTP (MP3 -0.93), PLR 10.1, LRA about 4.1 LU, laptop loss -2.4 dB, no warnings. Top end within 0.7 dB of the measured hip-hop curve from 1 to 16 kHz (4k -0.1, 8k -0.5, 12.5k -0.7, 16k -0.0); phone check 6-12 kHz -0.1 dB vs the curve. Largest EQ moves: -8.0 dB at 31.5 Hz, -8.0 dB at 40.0 Hz, -8.0 dB at 50.0 Hz. Remastered 2026-11-24: top end brought onto the measured curve (the first release used `--genre trap`; `--genre trap --legacy-master` reproduces it) |
| Update | **v028: clap replaced with handclap and off-beat fixes, 2026-11-24.** The old `clap` took `spread` in seconds (0.9), so every clap fired a second burst 0.9 s later, off the beat (103 stray hits, about as loud as the claps). It is now `handclap` (model 2, fitted to recorded claps), peaks 6.9 dB under the kick as before, same pattern, push, width and send. Audit of every other track (onsets of each drum stem against the scheduled hits, every hit against the feel-free grid): no other off-grid hits; the remaining offsets are the intended feel (swing, push, humanize, strums, rolls). |

## Files
- `bleachers-mastered.mp3`: the track
- `journal.md`: Spectre's 27 numbered moves
- `project.json`: reproduces the track exactly (render it with the engine)
- `ear-overview.png`: what the producer "saw" of the final render (arrangement lanes, spectrogram, band energy, loudness)
- `master-tonal-balance.png`, `master-report.json`: the mastering stage's before/after

## Spectre's note
"It started as a wall of organ and synth all shouting at once, and the first real decision was to shut most of it up so the fist only lands when the foot does. Once the stomp-and-clap pocket locked, everything else had to talk back to it. The chant answers in the gaps, the piano in the verse sits on one note and won't move, and the bridge piles weight on top with strings sinking a half-step at a time. The best moments are the stops, where the band drops out and the voices keep going without it."

## Why it came across as longing
See [docs/LESSONS.md](../../docs/LESSONS.md). In short: "minor melodies that climb back up every time the chords pull them down" means refusal on paper but sounds like yearning, and the synthesized timbres lacked the bite that defiance needs.

Note: this track was first mastered after the session with the then-new mastering stage (`--eq 0.9 --lufs -11`); the session itself ended with the engine's quick master. The remaster re-renders `project.json` (deterministic: the legacy chain reproduces the first master's report exactly) and keeps those two settings: the mix is very sub-heavy, and -11 LUFS is its documented loudness.
