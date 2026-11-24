# Pop rock for Spectre: a working brief

For sessions that make pop rock. A vocabulary, not a rulebook. Spectre has so far made only 808 beats on a programmed grid: pop rock is a **band playing in a room**. The drums are a kit played by one person, guitars and bass are strings, and the song's shape comes from dynamics between sections rather than from loops and drop-outs.

## The references
- **Pop rock and arena pop rock:** Foo Fighters, Paramore, The Killers, Coldplay, Snow Patrol, Jimmy Eat World, Kelly Clarkson's rock singles, Imagine Dragons, Fall Out Boy.
- **Songs about getting through depression:** Coldplay "Fix You", Paramore "Last Hope", R.E.M. "Everybody Hurts", Jimmy Eat World "The Middle", Twenty One Pilots "Car Radio", Linkin Park "Numb", Bastille "Pompeii". Listen to how they *move*, not to their words.

## Tempo and the kit (engine names in brackets)
- **Tempo:** most pop rock sits around 100-150 bpm; 115-135 is the comfortable middle. Ballad-builders like "Fix You" start slow (68 bpm) and open up. Feel is straight 8ths (`"swing": 0.5`) with a human hand (`humanize_ms` 4-8 on drums, a little `push_ms` on the snare for a laid-back backbeat).
- **Backbeat:** snare on 2 and 4 (`kitsnare`). The kick plays 1 and 3 with pushes ("x.......x.x....." or "x...x...x.x....."), and follows the bass.
- **Hats:** 8ths in verses (`kithat`, `dyn` accents on the beat). A half-open washy hat or **ride** in choruses (`kitride`, `bell` for cut). Pedal "chick" on 2 and 4 in quiet sections (`kithat` `"pedal": true`). Open hats choked by the closed hat (`"choke_by"`).
- **Crash on the one** of every chorus and big section (`kitcrash`), often with the kick.
- **Fills into choruses** in the last bar of the pre-chorus: snare 16ths, then toms falling high to floor (`kittom` tune 150-180 rack, 85-100 floor). Use a section `fill`.
- **Half-time** (snare on 3 only) for bridges and big outros: the same tempo feels twice as heavy.
- **Sound:** rock drums are about snap and attack. Kick: body 80-120 Hz, cut 200-600 Hz boxiness, beater 2-4 kHz. Snare: body 100-200 Hz, box 300-600 Hz, crack 2-4 kHz, sparkle around 10 kHz. Toms: 80-120 Hz power, 4-6 kHz attack. Room mics and parallel compression make the kit big and glued (`room` fx on each kit piece, a shared `send_reverb`, `comp`).

## Guitars
- **Verses:** clean, chorused electric guitar arpeggios (`cleanguitar` with an `arp` and the `guitar` voicing), or no guitar at all.
- **Pre-chorus:** palm-muted 8ths on power chords, building (`eguitar` with `mute` 0.7-0.9, stabs `"x.x.x.x.x.x.x.x."`).
- **Chorus:** distorted power chords (root, fifth, octave: `"voicing": "power"`) and open chords strummed (`"voicing": "guitar"`, `"strum": "alt"`).
- **Double-tracking is the big-guitar trick:** two takes panned hard left and right, with different tones or guitars. Make them complement: one anchors the low register, the other plays higher voicings or inversions; one palm-mutes while the other rings (keep the ringing one quieter); one drives steady 8ths while the other hits accents. Drop guitars out of the verse so the chorus hits harder. In the engine: two `eguitar` tracks at `pan` -0.85 and 0.85 with different `drive`, `dark`, `pickup` and voicings.
- **Lead lines:** melodic hooks between vocal phrases, octave doubling for size, unisons at phrase ends, harmonies used sparingly.

## Bass and keys
- **Bass guitar:** roots in 8ths that lock with the kick in choruses (`ebass`, stabs + `"voicing": "root"`), longer notes and space in verses, walking up into chorus changes. Picked for drive (`pick` near 1), fingered for warmth.
- **Keys:** piano quarter-note chords or stabs in pre-choruses and choruses, an organ or pad underneath for warmth (`piano`, `organ`, `pad`).

## Song form, and dynamics as the main tool
- **Form:** intro, verse 1, pre-chorus, chorus, (tag), verse 2, pre-chorus, chorus, bridge (middle 8), last chorus doubled, outro. Sections are usually 8 bars (4 and 16 are common); the chorus is usually 8, often doubling to 16 at the end. A tag of 2-4 bars gives a breather after a chorus.
- **Dynamics:** quiet verse, loud chorus. The pre-chorus builds the energy the chorus releases. The middle 8 drops main elements out and changes pace before the final chorus. Contrast between sections, not loudness, makes the chorus land.
- **Lift tricks:** a key change up a semitone or whole tone for the last chorus; a half-time bridge; a drop-out before the last chorus (one bar of only the voice, or silence); a new layer in the last chorus (octave lead, gang "oh"s, ride on the bell); the last chorus doubled.
- **Spectre's shape** (2:30-3:30; at 124 bpm a bar is 1.94 s): intro 4, verse 8, pre 4, chorus 8, verse 8, pre 4, chorus 8, bridge 8, drop-out 1-2, double chorus 16, outro 4 = about 80 bars, 2:35.

## Mixing and loudness
- The (here instrumental) vocal is king: everything is carved around the lead. Kick, snare, bass and lead are centred; double-tracked guitars hard left and right; toms and overheads (ride, crash, hats) panned by the drummer's perspective.
- Guitars and bass fight at 100-300 Hz; give the bass the bottom and the guitars the 300 Hz-3 kHz band. Kick and bass lock in time.
- **Loudness:** nine Billboard Hot Rock & Alternative songs (July 2025) averaged about -8 LUFS integrated (range -5 to -12) with true peaks near 0 dBTP, but the chart shows wide freedom in density and dynamics. For Spectre: `studio.py master --target rock --lufs -10` (-9.5 at most). Keep the verse-to-chorus contrast; don't crush it.

## The "vocal" role (instrumental)
A pop rock song without a singer still needs **the sung melody**. Carry it with `vox`, a wordless vocal-like lead (formant "oo" in verses opening to "ah" in choruses, scoops, glides with `~`, vibrato that blooms late), and/or a singing lead guitar that doubles or answers it in the last chorus. Write it like a singer would: phrases with breaths (rests), a verse in a narrow low range, a chorus that climbs a third to a fifth higher with long notes at phrase ends, and one held peak note in the last chorus.

## Getting through depression: how songs do it
- **The arc starts inside the weight.** "Fix You" opens on a church-organ drone at 68 bpm. The drums come in like a heartbeat returning, then an electric guitar breaks through and the production turns from inward reflection to a communal, anthem-like sound. The emotional path runs from quiet desperation through flickering hope and relapse to an earned, hollow-but-standing acceptance.
- **The relapse belongs in the arc.** The second verse goes back down; the song doesn't climb in a straight line.
- **Company is the cure, not victory.** Hayley Williams wrote "Last Hope" at a low point ("unfortunately, it is how I feel"). Live, it became a shared moment where "everyone in the room has survived so many different things." The lift is people around you and a reason to keep going.
- **Musical tools:** a low, narrow, close verse (clean guitar, room, a voice alone); drums entering in stages (pedal hat, then kick, then the full kit); a chorus whose melody reaches up and lands; major-key lift with the weight still audible (a minor vi or iv in the chorus progression, a sus chord that takes time to resolve, the verse motif returning in the last chorus); forward motion (8th-note drive in bass and guitars) instead of sheer volume; an ending that keeps one trace of the dark (the verse figure, now with the band behind it).
- **"Thriving over depression"** is more than surviving: by the end the music should have momentum and warmth, someone who is living, not just enduring. But it doesn't pretend the depression never happened.

### Nearest wrong feelings
- **Toxic positivity or a cheesy motivational anthem:** relentless major, stomp-clap and "whoa-oh" gang chants, a key change for its own sake, a sports-ad energy from bar 1. It denies the weight, so the lift means nothing.
- **Wallowing:** it stays in the verse; a slow dirge with no lift, or a lift that collapses back every time.
- **Teen angst rage:** fast pop-punk aggression, palm-muted fury, everything distorted all the time. Anger at the world, not climbing out.
- **A clean victory, "cured":** the final chorus as a triumph that resolves everything to I with a big rock ending and no trace of the struggle. Getting through is ongoing.

## Engine mapping
| Role | Engine |
|---|---|
| Kit | `kitkick`, `kitsnare`, `kittom`, `kithat` (`open`, `pedal`), `kitride` (`bell`), `kitcrash`; `room` fx; `"choke_by"` on the open hat |
| Distorted guitars | `eguitar` (`drive`, `mute`, `dark`, `pickup`), voicings `power` / `guitar`, stabs with `strum` |
| Clean guitar | `cleanguitar` (`chorus`), `arp` with the `guitar` voicing |
| Bass | `ebass` (`pick`, `mute`, `drive`, `tone`), stabs + `root` voicing |
| Keys | `piano`, `organ`, `pad` |
| Lead "voice" | `vox` (`voice`, `vowel`, `vowel2`, `vibrato`, `glide_ms`) and/or a lead `eguitar` line |
| Master | `--target rock --lufs -10` |

## Sources
- MusicRadar, Anatomy of an arrangement (song sections): https://www.musicradar.com/how-to/song-sections-explained-intro-verse-chorus-middle8-outro-tag-bridge
- Mastering The Mix, How to mix big, punchy rock drums: https://www.masteringthemix.com/blogs/learn/how-to-mix-big-punchy-rock-drums
- Premier Guitar, Double trouble: make rhythm guitar parts great again: https://www.premierguitar.com/double-trouble-make-rhythm-guitar-parts-great-again
- iZotope, A LUFS and tonal analysis of top-charting rock and alternative songs: https://www.izotope.com/en/learn/rock-alternative-analysis
- Songtell, "Fix You" (Coldplay): https://songtell.com/coldplay/fix-you
- IBTimes, Hayley Williams on how mental health struggles shaped "Last Hope": https://www.ibtimes.co.uk/ive-wanted-not-here-hayley-williams-reveals-how-mental-health-struggles-shaped-last-hope-1759886
