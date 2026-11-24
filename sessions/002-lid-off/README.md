# 002: Lid Off

| | |
|---|---|
| Mode | Briefed. Theme: **rage**. Specs: high tempo, aggressive, strongly felt |
| Length / tempo / key | 2:48 of music (2:51 with the final ring-out), 112 bars, 160 bpm straight, E Phrygian with a flat 5, up a semitone to F for the last hook |
| Genre | Rage-trap crossed with industrial: full-time stampede hooks, half-time verses with a muted chug, distorted 808s, a blown-out diminished supersaw cluster (E-G-Bb-F), a hammering bitcrushed lead |
| Iterations | 31 render-and-listen loops (about 11 loop, 6 arrangement, 9 transitions and detail, 5 mix), then the master |
| Master | `studio.py master v032 --genre hiphop --lufs -10` (master version 2): -10.1 LUFS, -1.04 dBTP (MP3 -0.9), PLR 9.1, LRA about 3.9 LU, laptop loss -2.2 dB, no warnings. Top end within 1.1 dB of the measured hip-hop curve from 1 to 16 kHz (4k +0.2, 8k +0.0, 12.5k -0.2, 16k +1.1); phone check 6-12 kHz -0.2 dB vs the curve. Largest EQ moves: -10.4 dB at 16000 Hz, -8.0 dB at 40.0 Hz, -8.0 dB at 63.0 Hz. Remastered 2026-11-24: top end brought onto the measured curve (the first release used `--genre trap`; `--genre trap --legacy-master` reproduces it) |

## Arrangement
1. Intro: a growling 808 under a filtered riff
2. Hook 1: the plain stampede
3. Verse 1: clenched, with room for a voice
4. Hook 2: adds a distorted metal stomp
5. Break: a held growl while the kick comes back in quarters, eighths, then sixteenths
6. Verse 2
7. Hook 3: up a semitone, 24 bars, the lead doubled an octave up for the last 8
8. Outro: two bars of everything speeding up, two beats of silence, then one last slam ringing out

Every 4-bar hook phrase ends with an eighth of total silence and then a slam on the 1.

## Files
- `lid-off-mastered.mp3`: the track
- `journal.md`: Spectre's numbered moves
- `project.json`: reproduces the track exactly
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"Last time I wrote defiance on paper and the speakers gave back longing, so this time I made every decision in the sound: grind in the 808's mids, a sour cluster where a power chord would've been, hard cuts where I'd usually put a riser. Most of the session was taking things out that told the wrong story. The snare tail hiss read as anxiety, the riser read as festival hype, and the half-time verse went cold like menace until I put the chug under it. What I'm proudest of is the eighth of dead air before every fourth bar, because rage isn't loud all the time, it's a gasp through the teeth and then a fist. It ends cut off mid-swing with two beats of nothing and one slam, because rage doesn't fade out, it slams the door."
