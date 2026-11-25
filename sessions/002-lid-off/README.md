# 002: Lid Off

| | |
|---|---|
| Mode | Briefed. Theme: **rage**. Specs: high tempo, aggressive, strongly felt |
| Length / tempo / key | 2:48 of music (2:51 with the final ring-out), 112 bars, 160 bpm straight, E Phrygian with a flat 5, up a semitone to F for the last hook |
| Genre | Rage-trap crossed with industrial: full-time stampede hooks, half-time verses with a muted chug, distorted 808s, a blown-out diminished supersaw cluster (E-G-Bb-F), a hammering bitcrushed lead |
| Iterations | 31 render-and-listen loops (about 11 loop, 6 arrangement, 9 transitions and detail, 5 mix), then the master |
| Master | `studio.py master v033 --genre hiphop --lufs -10` (master version 2): -10.0 LUFS, -1.0 dBTP (MP3 -0.85), PLR 9.0, LRA about 3.9 LU, laptop loss -2.2 dB, no warnings. Top end within 0.7 dB of the measured hip-hop curve from 1 to 16 kHz (4k -0.1, 8k -0.3, 12.5k -0.2, 16k +0.7); phone check 6-12 kHz -0.2 dB vs the curve. Largest EQ moves: -8.4 dB at 16000 Hz, -8.0 dB at 40.0 Hz, -8.0 dB at 63.0 Hz. Remastered 2026-11-24: top end brought onto the measured curve (the first release used `--genre trap`; `--genre trap --legacy-master` reproduces it) |
| Update | **v033: clap replaced with handclap and off-beat fixes, 2026-11-24.** The old `clap` (`spread` 0.6, in seconds) fired a second burst 0.6 s after every clap, off the beat (157 stray hits, as loud as the claps); it is now `handclap` (model 2), drive dropped, peaks 6 dB under the kick (5.2 before), same pattern, push and width. Spot fix: the snare's 3.5 kHz high shelf from -5 to -9 dB (the backbeat carried about 95% of the hooks' 4-12 kHz): the snare's 4-12 kHz -3.4 dB, the premaster's 6-12 kHz on the phone check from +3.5 to +0.2 dB over the curve, worst window from +4.9 to +1.7 dB. Audit of every other track (onsets of each drum stem against the scheduled hits, every hit against the feel-free grid): no other off-grid hits; the remaining offsets are the intended feel (swing, push, humanize, strums, rolls). |

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

## Remix (2026-11-25)
**v036 replaces v033 as the published version.** A remix with no compositional change: tempo, swing, seed, patterns and arrangement are frozen, and every track's events are identical to v033. The low end was carved for the old curve and is now carved for the new one: the kick's +3 dB at 100 Hz became -3 dB at 170 Hz and its notch at its own 62 Hz went from -5 to -2 dB; the stomp -3 dB at 150 Hz; the 808 and 808long lost their -8 dB notch at 45 Hz and gained 3 and 2 dB after their drive; a notch at the kick's 62 Hz on the 808, keyed by the kick. The target is the hip hop 2015-21 era curve (`hiphop_2015`, 347 catalogue tracks): `studio.py master v036 --genre hiphop --lufs -10`: -10.2 LUFS, -1.03 dBTP, PLR 9.2, top end within 0.5 dB of the curve, no warnings (EQ at its limit only at 31.5 Hz, where nothing plays); mean gap to the catalogue 0.79 dB (the previous master 1.75). The hooks sit 0.2-0.3 LU lower against the track; the sections carried by the 808long growl rise (intro1 +1.6, intro2 +0.9, the closing slam +1.9 LU), kept on purpose: the growl was what the old curve made the mix hide. Details in journal entry 34.

The previous release (v033) is reproduced by `project-published.json`; the table above describes it. `ear-overview.png` still shows v033's render: no overview ear was saved for the remix.

## Files
- `lid-off-mastered.mp3`: the track
- `journal.md`: Spectre's numbered moves
- `project.json`: reproduces the track exactly
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"Last time I wrote defiance on paper and the speakers gave back longing, so this time I made every decision in the sound: grind in the 808's mids, a sour cluster where a power chord would've been, hard cuts where I'd usually put a riser. Most of the session was taking things out that told the wrong story. The snare tail hiss read as anxiety, the riser read as festival hype, and the half-time verse went cold like menace until I put the chug under it. What I'm proudest of is the eighth of dead air before every fourth bar, because rage isn't loud all the time, it's a gasp through the teeth and then a fist. It ends cut off mid-swing with two beats of nothing and one slam, because rage doesn't fade out, it slams the door."
