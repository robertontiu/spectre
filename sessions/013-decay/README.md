# 013: Half of Me

| | |
|---|---|
| Mode | Briefed. Genre: **trance, radio edit**. Subject: **radioactive decay**. Brief: tense build-ups and big drops; the emotional nerve stays on alert the whole time; vocals mandatory, used as an instrument. The producer chose what decay is in sound |
| Producer | Spectre, run on Claude Fable 5.2 for this session |
| Feeling | On alert: weight on the balls of the feet, a breath taken and not let out, a pulse that never gives the rest you expect |
| Length / tempo / key | 3:36 (124 bars), 140 bpm, straight 16ths, F♯ minor with a Phrygian ♭2 (G), no major chord but the ♭2 |
| Voices | `singer` `svs`: `hanami`, `hanami-dark`, `leona-power`, `leona-soft`. Words are Spectre's own: "half of me is light", "half of what is left holds on", and the chops "half / me / light / hold" |
| Iterations | 34 journal entries, 32 renders; resumed once after a server restart. v027-v032 revised it after the owner's listening: real builds and cliffs (the drop into drop 1 went from 2.9 to 12.5 LU, into the main drop from 11.1 to 13.4 LU), a transition on the missing last word, and the words made readable per docs/TRANCE.md "Mixing the voice" (nearly dry worded lines, wet throws only on tails; Whisper on the master 4/36 to 31/36 words; "light" is still not heard) |
| Master | `studio.py master v032 --genre trance_radio` (master v2, measured trance curve): -9.3 LUFS, -1.03 dBTP (MP3 -0.58), PLR 8.2, LRA 7.8 LU, width -10.5 LU, laptop loss -1.8 dB, top end within 1.2 dB, phone check clean, no warnings |
| Credits | Vocals: Hoshino Hanami and LEONA (DiffSinger voicebanks by Lotte V, lottev.moe; LEONA under CC BY 4.0), Potluck Vocoder by tigermeat |

## How it carries the feeling
- **Decay is a half-life.** The lead's 8-note hook halves every 8 bars in the main drop (8, 4, 2, 1 notes) and never reaches zero. Every note the lead loses is picked up by a vocal chop (0, 4, 6, 7), so the drop keeps its density and force but changes hands: a parent turning into a daughter.
- **One unstable nucleus.** The G over the F♯ tonic (the ♭2) never resolves: the hook hangs on it, the voice holds it before the main drop, and the track ends on it.
- **Decay everywhere in time.** The breakdown's ticks thin 16-8-4-2-1 per two bars; the tail's chops halve 4-2-1; at the end the kick's gaps double (half a bar, a bar, two bars) instead of fading.
- **Tension by denying, not adding.** The second build's roll stops half a bar early into two bars of one dry voice holding "hold" on the wrong note until the kick cuts it off; one beat of kick goes missing at every half-life boundary; there is no silence before the main drop.
- **The last line loses its last word.** The far voice sings "half of me is" and stops; the lead's one surviving note plays the G where "light" would be and rings out.
- **Wrong feelings kept out:** a horror score, a science-documentary bed, a cheerful festival anthem, constant loudness, a Geiger-counter gimmick, and First Light's euphoria again.

## Song form (bars, start)
- **Intro (1-8, 0:00):** the far voice sings the line twice over the filtered rolling bass and a tuned tick; "hold" at bar 8
- **Theme A (9-16, 0:14):** kick, rolling bass, the 8-note cell as a filtered stab
- **Theme B (17-24, 0:27):** hats, claps, gated saws; the filter opens
- **Build 1 (25-32, 0:41):** snare roll, accelerating "hold" chops rising G4 to C♯5, the kick gone for the last two bars, a one-beat cut
- **Drop 1 (33-48, 0:55):** the cell whole; the sung call at bars 39-40 while the lead rests
- **Breakdown (49-64, 1:22):** no kick; the roll under a closing filter; ticks thinning; the line and its answer; two dark voices rocking a third apart
- **Build 2 (65-70, 1:50):** the roll tightens and stops half a bar early
- **Hold (71-72, 2:00):** one dry voice holds "hold" on G, cut off by the kick
- **Main drop (73-104, 2:03):** four half-lives of 8 bars; the lead 8, 4, 2, 1 notes, the chops 0, 4, 6, 7; dark voices from bar 89; the call returns at bars 103-104
- **Tail (105-124, 2:58):** chops halve, the kick's gaps double, "half of me is" on a reverse swell with "is" thrown into the echo, then the lone G lands where "light" would be and rings out for four bars

## Departures from Spectre's habits (against 007, First Light)
The hook comes first and is then taken apart (a bigger second wave would have been First Light again); the breakdown starts dense and thins and stays minor; no silence before the main drop; the rolling bass runs from bar 1; the ending cuts mid-phrase on the ♭2 instead of a closing filter; 140 bpm in F♯ Phrygian minor.

## Remix (2026-11-25)
**v039 replaces v032 as the published version.** A remix with no compositional change: tempo, swing, seed, patterns, arrangement and the words are frozen, and every original track's events are identical to v032. No voice track is edited, and the reverb and delay that carry the voices stay as approved. The kick's carving for the old curve came out and the kick became a stack (sub on the key's root F#1, punch, click); the bass a sub, the original bass opened up, and an upper bass, with a notch keyed by the kick; the lead supersaw model 2 with support, transient and air layers; the pad a polysynth body and a bright layer; tonal `metalhat` over the hats; a drum bus and a music bus; the synths and drums on their own returns; a dip at 3.2 kHz in the centre of the lead to leave room for the words. The target is the trance 2015-21 era curve (`trance_2015`): `studio.py master v039 --genre trance_radio`: -9.1 LUFS, -1.03 dBTP, PLR 8.0, LRA 7.3 LU, no warnings (EQ at its limit only at 31.5 Hz). Against the target (50-80 Hz / 100-250 / 315-400 / 2-5 kHz / 8-12.5 kHz): previously -7.3 / +3.3 / +2.6 / -0.1 / -4.2 dB, now -0.1 / +0.2 / +0.7 / -0.1 / -1.8. Every section within 0.8 LU of the previous master; words 31/36, as before. A miss: the builds and drops did not get bigger (the cliffs measure 12.0 and 12.8 LU, previously 12.5 and 13.4); more band against the voices cost the main call's words, so the words won. Details in the journal's remix entry (35).

The previous release (v032) is reproduced by `project-published.json`; the table above describes it. `ear-overview.png` still shows v032's render: no overview ear was saved for the remix. `build.py` still writes v032's project: running it overwrites the remix. `remix.py` is the recipe: applied to `project-published.json` it gives `project.json` exactly (it reads `project.json`, which is now the remix, so point it at `project-published.json` before running it again).

## Files
- `half-of-me-mastered.mp3`: the track
- `journal.md`: the producer's numbered moves
- `project.json`: reproduces the track exactly; generated by `build.py full`
- `stems.py`, `peaks.py`, `bands.py`, `r.sh`: the producer's helpers
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"I started from the back of the neck, not from a melody: a bass that never leaves you a hole to lean into, and one note a semitone too high that nobody is allowed to bring home. The hard part was making the main drop lose its hook without losing its force. The first versions just dimmed, until the voice that replaces the lead got teeth of its own and the top end opened as the melody died. The moment I trust most is the two bars where everything stops and one dry voice holds the wrong note until the kick cuts it off. I stopped when the last line lost its last word and the one surviving note of the lead said it instead."
