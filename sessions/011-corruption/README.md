# 011: Din somnul cel de moarte

| | |
|---|---|
| Mode | Briefed. Genre: **aggressive hip hop**, built on identifiable elements of the Romanian national anthem. Subject: **corruption in Romania**: a beautiful country that corruption keeps damaging. The anger is aimed at corruption, never at the country or its people |
| Producer | Spectre (Claude Opus 5.5) |
| Feeling | Anger held in the jaw at a rot inside something loved |
| Length / tempo / key | 3:26 (76 bars), 90 bpm, swing 0.58 (hardcore boom-bap pocket), G minor (natural minor) with a foreign A♭ as the rot |
| Anthem | "Deșteaptă-te, române!": melody by Anton Pann (1839), words by Andrei Mureșanu (1848), both public domain. Quoted in fragments only, exactly as in the verified melody (docs/ROMANIAN.md, "Anthem" > "Verified melody", checked against the official score in the annex of Law 75/1994, a CC BY-SA score, a MIDI file and a recording), with harmony of Spectre's own. No words are sung |
| Iterations | 28 journal entries, 22 renders; resumed once after a server restart; v022 fixed the intro quote, which first ended on the next line's upbeat ("bar-") |
| Master | `studio.py master v022 --genre hiphop` (master v2): -10.6 LUFS, -1.03 dBTP (MP3 -0.77), PLR 9.6, LRA 5.2 LU, width -15.7 LU, laptop loss -1.9 dB, top end within 0.8 dB of the measured curve, phone check clean, no warnings |

## How it carries the feeling
- **Two sound worlds.** The country: piano, strings and a wordless choir in a room, played slightly late, like people. Corruption: one foreign semitone (A♭ against the home note G), dry, bitcrushed and locked to the grid.
- **The rot spreads.** It starts as a quiet hum under the anthem's seventh bar ("te-adânciră", sank you), then moves into the bass (the 808 slides to A♭), then the harmony, then the melody itself: in the second hook the anthem's held D is "bought" down to D♭.
- **The copy gets worse every time.** Hook 1 quotes the anthem clean; hook 2 plays it back through a bad copy (wow and flutter, 9 bits, a low sample rate); hook 3 is a crushed 6-bit copy that stops at "Deș-teap-tă-te, ro-" with silence where "române" was. The drums harden only as the rot spreads, so the anger always has an object.
- **The melody is never destroyed.** The bridge has no rot at all: a wordless choir sings "Acum ori niciodată... croiește-ți altă soarte" (now or never... make yourself another fate) clean. At the end the beat dies and the clean piano plays the opening phrase exactly as written, stopping on "din", with the A♭ still ticking underneath. Not dead, not won.
- **Wrong feelings kept out:** cheap shock (the damage has one cause and grows), mocking the anthem (every clean quote is exact; the damage is corruption's work, never a joke), generic rage (drive without volume), nationalist pride (no march, no triumph, no enemy people).

## Song form
- **Intro (8):** strings on G minor from the first beat; the clean piano plays the first two lines, ending on "-ră" (te-adânciră), which rings into the hum; the A♭ hum creeps in under bar 7; a dry meter ticks in bar 8
- **Verse 1 (8 + 8):** the swung beat and 808; the anthem's opening fourth (D-G, "Deș-teap-") chopped on lo-fi piano across every bar line; then an open hat, the 808 starts sliding into A♭, the rot ticks in 8ths
- **Hook 1 (8):** the clean quote, twice, over the full beat, strings in Spectre's own harmony
- **Verse 2 (8 + 4 + 4):** driven kick and saturated snare, the chop bitcrushed, the rot in 16ths, the 808 on A♭; then subtraction (beat, 808 and rot only); then the crushed chop returns
- **Hook 2 (8):** the quote through a bad copy, the held D bought down to D♭, strings grinding A♭ against G; on the last beat everything cuts but the choir's upbeat
- **Bridge (8):** no rot; the wordless choir sings period b clean, twice; clean drums return for the second pass
- **Hook 3 (8):** a crushed copy that breaks off before "române", then only "Deș-teap-", then the crushed chop under the hardest drums; one beat of silence
- **End (4):** the beat is dead; the clean piano plays the opening phrase and stops on "din", the A♭ and the meter still ticking

## Departures from Spectre's habits
The hooks decay instead of growing; a verse comes before the first hook; no wind-down outro (the beat stops dead and the clean phrase ends unresolved). The first boom-bap track after five half-time trap tracks, with no crowd joining and no call-and-response.

## Remix (2026-11-25)
**v026 replaces v022 as the published version.** A remix with no compositional change: tempo, swing, seed, patterns and arrangement are frozen, and every track's events are identical to v022; the anthem tracks, the intro edit and every quote are untouched. The kicks and the 808 were pulled apart: both kicks' tails went from 0.35 to 0.22 s; the 808 became a stack (its own sound plus an octave layer 12 dB under it), with notches at the kicks' 62 Hz keyed by each kick, ducking by `kickX` too (the old sidechain listened to `kick` only), and +3 dB at 40 Hz for the low hook notes. In hook 3 the 808 is 31% masked, 59% before. The hat became a stack with a tonal `metalhat`, and the clap came up 3 dB, so the top has two sources. The target is the hip hop 2015-21 era curve (`hiphop_2015`, 347 catalogue tracks): `studio.py master v026 --genre hiphop`: -10.7 LUFS, -1.03 dBTP, PLR 9.6, no EQ at its limit, top end within 0.9 dB of the curve, no warnings; mean gap to the catalogue 0.93 dB (the previous master 1.53). Every section within 0.2 LU of the previous master except the end (+0.8 LU, the clean piano alone); the hooks' decay and the bridge's valley are intact. The intro has the same notes and timing but is not bit-identical (the new layers shift the shared random stream; -0.1 LU, accepted). Details in journal entry 29.

The previous release (v022) is reproduced by `project-published.json`; the table above describes it. `ear-overview.png` still shows v022's render: no overview ear was saved for the remix.

## Files
- `din-somnul-cel-de-moarte-mastered.mp3`: the track
- `journal.md`: the producer's numbered moves
- `project.json`: reproduces the track exactly
- `stems.py`, `bands.py`, `wait.sh`: the producer's helpers
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"I didn't want to burn the house down; I wanted to show the rot in the beams while the house is still beautiful. The hardest part was letting the hook get worse instead of bigger. Every instinct says the last hook should lift, but corruption doesn't give you a lift; it gives you a worse copy every year. The moment I trust most is the end: the beat just dies, and Pann's melody plays exactly as written, stops on 'din', and you can still hear the A♭ ticking underneath. It isn't over."
