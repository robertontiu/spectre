# 017: Captive

| | |
|---|---|
| Mode | Briefed. Genre: **dubstep, modern** (2015-2026). Subject: **the soul taken and held captive against its will**: the fight, the panic, the cold acceptance, and the absence the struggle leaves. The energy falls across the track: the second drop colder and simpler than the first, the end in absence |
| Producer | Spectre, run on Claude Opus 5.5 for this session |
| Genre / strand | Dubstep, modern: a deep / 140 frame (the sub as the subject, space as dread) carrying tearout in drop 1 (two bass voices in call and response, answers cut off) and riddim in drop 2 (one motif looping, no answer) |
| Feeling | A weight that is not yours leaning on the sternum; the diaphragm pushing back in bursts; the inside going rough; then the same pressure without the pushing; then the room after the sub stops, where the ribs still expect it |
| Length / tempo / key | 3:53 (136 bars, the last four silent), 140 bpm in half time, straight grid for the captor and the soul 12 ms late; F♯ Phrygian (the ♭2, G, is the captor's note; sub root F♯1 = 46 Hz) |
| Sounds | the captor (an `fmgrowl` stack: a bare FM wub body, a clean low `weight`, a folded `bite` an octave up, a comb `teeth` top), the soul (a `wavetable` on the vocal table, talking "ee-ah"), one clean mono `sub`; kick stack (sub on C♯2, punch, click), 909 snare and clap crack with a gated tail, `metalhat`; drop 2's `husk` riddim motif; a resampled chop of the captor; a cold filtered texture; a granular freeze of the motif |
| Voices | `singer` `svs`: `hanami-soft`, two words, "still here": clean in the intro (cut on "here" by the drop), pitched down and veiled with `vowel` in the breakdown, where it finishes |
| Iterations | 29 journal entries, 27 renders (v001-v021 the session, v022-v027 the revision), trial masters on v016, v018, v021-v027 |
| Master | `studio.py master v027 --genre dubstep --lufs -8` (master v2, target `dubstep_2015`): -8.2 LUFS, -1.03 dBTP, PLR 7.2; drop 1 at -6.5 / -6.4 / -6.2 LUFS short-term (the loudest moment of the track), drop 2 1.1-1.4 LU under it. Published 2026-11-26 as the revision v027 (below); the first finished version v021 (-8.7 LUFS) was never published |
| Credits | Vocals: Hoshino Hanami (DiffSinger voicebank by Lotte V, lottev.moe), Potluck Vocoder by tigermeat |

## Revision before release (2026-11-26)
The owner heard v021 and said it "doesn't quite peak at the genre". An engineering pass compared every dubstep sound with 118 CC0/CC-BY references and fitted presets (examples/production/dubstep-v2/), and diagnosed the cause: the drop continued the build instead of arriving. The revision (journal entry 29; "remix, no compositional change, and a revision at the transitions") changed only the last bar of build 1b, the first beat of drop 1A, the last two beats of build 2 and the panic's level, and swapped in the fitted growl (the captor's body), kick (sub tuned to E1) and snare. Results: 50-80 Hz at the drop's downbeat from -0.8 to +27 dB over the build's end (half a beat of silence, then sub and impact together); drop 1 -7.2/-7.0/-6.8 to -6.5/-6.4/-6.2 LUFS short-term, now the loudest moment (the panic moved from -5.9 to -6.6); the captor's 2-5 / 5-16 kHz from -14.1 / -18.0 to -5.8 / -8.1 dB and its brightness movement from 0.22 to 1.12 octaves (references -6.8 / -7.5, 0.69); drum crest kick/snare 17.6/26.3 to 14.7/17.4 dB. The cut word "here" is now cut by the half-beat of silence before the drop instead of at its first sample. The owner approved the revision by ear on 2026-11-26.

## How it carries the feeling
- **Two voices and a body.** The captor is a cold, articulate FM machine locked to the grid, leaning on the ♭2; the soul is a talking formant voice that always climbs (A, C♯, E, F♯, A), slightly late, and never resolves; the sub under both is the body that is held, and the last thing to leave.
- **A fight is overlap, not turns.** The soul starts under the captor's last note, and the captor's pickup on beat 4 cuts the soul's held note before every bar line: the captor always wins by a 16th. Across drop 1 the answer shrinks: two bars, half a bar, two notes, then the captor's own call resampled into a machine-gun where the soul used to start.
- **The taking interrupts a word.** "still here" is sung once clean; the second time, "here" is cut at the drop's first sample. In the breakdown it returns a fourth lower and veiled, and this time it finishes: only once the fight is lost.
- **The panic belongs to the soul.** Not tempo: the subdivisions climb (16ths, 16th triplets, hats to 32nds) and the roughness lives inside the soul's voice (a level flutter rising 30-70 Hz), so it reads as a voice choking at speed inside a machine, not as noise. Then the only hard cut in the track: two beats of digital black.
- **Acceptance is a broken promise.** In drop 2 the captor's riddim motif plays one bar and leaves the next empty, exactly where the soul always answered: that place is 14 dB emptier than in drop 1, and nothing answers for 24 bars. The motif goes numb section by section (5.6 dB less edge), while kick, snare and sub do not change.
- **The absence is removal.** Mid-bass, drums, sub leave in that order; a frozen grain cloud of the motif dissolves; four bars of nothing, inside the track.
- **Wrong feelings kept out:** a horror trailer (every threat has a groove, no stinger, no final hit), festival brostep (the peak is the first third; drop 2 is quieter by design), a boss fight (no lead melody, no phase two that wins), sad ambient (no warm pad, no piano), shock value (the roughness peaks once), melodic-dubstep catharsis (no major chord, no lift).

## Song form (engine bars, start)
- **intro A (1-4, 0:00):** the sub alone swelling in from far away under a cold texture
- **intro B, intro sing (5-16, 0:06):** a sparse deep-140 kit with a dub reverb on the snare; the soul's ladder, bright and talking; "still here"
- **build 1 (17-24, 0:27):** the captor creeps in under a filter, the soul's ladder cut shorter, "still here" again; no silence before the drop
- **drop 1A-1C (25-48, 0:41):** tearout call and response, the answer shrinking; 1B adds 16th hats, 1C the machine-gun chop; the loudest stretch of the track
- **panic (49-56, 1:22):** rising subdivisions, the soul's voice buzzing; two beats of silence
- **breakdown (57-72, 1:36):** no drums, a long dark hall, the voice a fourth lower and finished, the sub far away, the captor a filtered shadow
- **build 2 (73-80, 2:03):** energy falls: heartbeat kick, the captor's filter closing, no riser
- **drop 2A-2C (81-104, 2:17):** riddim: one bar of motif, one bar of nothing, kick on the snare, triplet hats; the motif drains
- **gone 1-3, silence (105-136, 2:58):** mid-bass gone, drums gone, sub gone and the cloud fading, then four bars of silence

## Departures from Spectre's habits
The peak is the first third and everything after it is less; no silence before drop 1 (the taking is an interruption); the ending does not return to the intro (the voice never comes back); the intro starts with the sub, not a lone melodic instrument behind a filter.

## Files
- `captive-mastered.mp3`: the track
- `journal.md`: the producer's numbered moves
- `project.json`: reproduces the published track exactly (equals `renders/v027.project.json`, the revision; *showcase copy note: corrected from "v021", which was the first finished version; its project is in `revision/v021.project.json`*)
- helpers: `fastlisten.py` (the overview listen with an FFT convolution), `stems.py`, `stackview.py`
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"It carries what I set out to make; one more move would be explaining. The thing I'd keep is the empty bar in drop 2: fourteen decibels of nothing where the soul used to speak, with the sub still holding under it. Misses, honestly: drop 2 is only 1.1 LU under drop 1, not the 1.5-2 I planned; the first step of the absence is mostly the motif leaving, so on small speakers it is smaller than on a system; and the captor's stack view came back empty in the last clarity runs, so its top layer was judged only by the mix's numbers."
