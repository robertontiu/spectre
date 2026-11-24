# 003: Throw It Back

| | |
|---|---|
| Mode | Briefed. Thematic: **oriental trap**. Subject: **rebellion** |
| Length / tempo / key | 2:44.6 of music (96 bars), 140 bpm straight, half-time trap pocket, D Hijaz (Phrygian dominant) |
| Instruments | oud, ney, darbuka (doum, tek, ka), trap kit, 808, crowd chant sections. The engine got oud, ney and darbuka for this session |
| Iterations | 27 (12, then an interruption, then 15 more resumed from the saved project and journal) |
| Master | `studio.py master v026 --genre hiphop` (master version 2): -10.5 LUFS, -1.04 dBTP (MP3 -0.81), PLR 9.5, LRA about 8.4 LU, laptop loss -2.1 dB, no warnings. Top end within 1.2 dB of the measured hip-hop curve from 1 to 16 kHz (4k -0.6, 8k -1.1, 12.5k -0.2, 16k +0.8); phone check 6-12 kHz -1.6 dB vs the curve. Largest EQ moves: -9.8 dB at 16000 Hz, -8.0 dB at 31.5 Hz, -8.0 dB at 40.0 Hz. Remastered 2026-11-24: top end brought onto the measured curve (the first release used `--genre trap`; `--genre trap --legacy-master` reproduces it) |
| Update | **v026: clap replaced with handclap and off-beat fixes, 2026-11-24.** The old `clap` (`spread` 1.0 and `decay` 0.12, in seconds) never sounded as a clap: its later bursts and tail fell outside its 0.66 s buffer, so each hit was a bare 4 ms click, peaking 3.9 dB over the kick (no off-beat hits). It is now `handclap` (model 2), drive dropped, peaks 6 dB under the kick, same pattern, push, width and send. Audit of every other track (onsets of each drum stem against the scheduled hits, every hit against the feel-free grid): no other off-grid hits; the remaining offsets are the intended feel (swing, push, humanize, strums, rolls). |

## Arrangement
- **Intro (1-8):** the oud calls alone through a slowly opening filter, darbuka rims only
- **Gather (9-12):** crowd stomp-stomp-clap, doum, low oud, the crowd's first answers; one beat of everything cut
- **Hook 1 (13-20):** trap drums and a singing 808; the oud calls, one crowd section answers
- **Verse 1 (21-36):** pared down for a rapper; the crowd answers once every four bars
- **Hook 2 (37-44):** both crowd sections answer; trap drums fall out for 2 beats at the end
- **March (45-52):** no kick, no 808. Feet on every quarter, hands on 3, darbuka, a held chant that swells; a fill where the crowd speeds up, then half a beat of silence
- **Verse 2 (53-68):** the march's feet keep walking under the verse groove
- **Standoff (69-72):** the beat drops away; feet and hands louder, the ney shouts the call, the full crowd answers with nothing under it; half a beat of silence
- **Hook 3 (73-88):** slams in with an impact; a third, higher crowd section joins, a gritty ney leads, darbuka runs hot in 16ths
- **Outro (89-96):** feet, darbuka and the oud call go on while the crowd keeps answering, filtered and fading down the road

## Files
- `throw-it-back-mastered.mp3`: the track
- `journal.md`: Spectre's 27 numbered moves
- `project.json`: reproduces the track exactly
- `build.py`, `levels.py`, `trem.py`: helper scripts the producer wrote for itself during the session (generating parts of the project, checking levels, oud tremolo)
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"Rebellion isn't one man shouting. It's a line thrown out and a whole street throwing it back louder every time, so the work here was making the crowd grow and keeping the hype out: no risers, no major lift, nothing that sounds like we already won. The best move was taking things away. The march where the trap drops out and only feet, hands and the darbuka walk, and the standoff where the crowd shouts with nothing under it before the last hook hits. It ends with the voices still going down the road, because the fight isn't over."
