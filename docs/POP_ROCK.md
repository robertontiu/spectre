# Pop rock for Spectre: a working brief

For sessions that make pop rock. A vocabulary, not a rulebook. Spectre has so far made only 808 beats on a programmed grid: pop rock is a **band playing in a room**. The drums are a kit played by one person, guitars and bass are strings, and the song's shape comes from dynamics between sections rather than from loops and drop-outs.

## Configuration (researched 2026-11; engine: `--genre rock` in engine/genres.json)
| Setting | Value | Source |
|---|---|---|
| Length | **3:00-4:00**, typically about 3:15-3:30 | Average song 3:15 in the 2020s, 4:14 in the 1990s (Washington Post via [HuffPost](https://huffingtonpost.co.uk/entry/pop-songs-are-shorter-now_uk_66b0d65de4b022eb04aa13cb)); Billboard Hot 100 #1 hits averaged 3:30 in 2024, 25% over 4:00 ([Hit Songs Deconstructed](https://hitsongsdeconstructed.com/wp-content/uploads/2025/02/The-Hit-Songs-Deconstructed-1-Hit-Focus-Report-Highlights.pdf)); Billboard year-end top 30 averaged 3:14 in 2020 ([Țînț & Drăgulin 2025](https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335)). No rock-only length survey found |
| Form | intro, verse, pre-chorus, chorus, (tag), verse, pre-chorus, chorus, bridge (middle 8), final chorus (often doubled), outro | Section order and the 2-4-bar tag ([MusicRadar](https://www.musicradar.com/how-to/song-sections-explained-intro-verse-chorus-middle8-outro-tag-bridge); it calls the pre-chorus "bridge" and the bridge "middle 8"). Of 2024's #1 hits: 88% start with an intro (average 14 s), 75% end with an outro (average 21 s), 69% have three choruses, 44% a bridge, 38% a pre-chorus; the first chorus arrives at 0:45 on average (Hit Songs Deconstructed). In classic rock (Rolling Stone 200, 1949-2003) only about 6% have a pre-chorus and 31-38% a bridge ([de Clercq 2017](https://www.midside.com/publications/declercq_2017_jmt.pdf)): the pre-chorus is a modern pop-rock habit, optional |
| Section lengths (bars) | sections 8 bars, 4 and 16 common; chorus 8, doubling to 16 late in the song; tag 2-4; intro 4-8 (about 14 s) | [MusicRadar](https://www.musicradar.com/how-to/song-sections-explained-intro-verse-chorus-middle8-outro-tag-bridge); intro length from Hit Songs Deconstructed |
| Tempo | **typically 115-130 bpm**; the wider 100-150 range is unsourced | Western music clusters at 115-127 bpm, peak 125 (Moelants 2002, DJ bpm lists plus tapping, as summarised by [Dahl et al. 2014](https://vbn.aau.dk/ws/files/201902553/Dancetempo_JNMR_accepted_source_Jan2014.pdf)); Mixgraph's editorial pop range 95-130 ([Mixgraph](https://www.mixgraph.io/bpm-for)); 2024 #1 hits (mostly hip-hop and country) averaged 100 (Hit Songs Deconstructed). No pop-rock-specific tempo dataset was reachable, so the range is only partly sourced |
| Meter and groove | 4/4, backbeat (snare on 2 and 4), straight 8ths, a played (humanized) kit | genre definition, **unsourced**. Hit records have played to a click since about 1979, so tempo is steady (CV 0.2-0.5 for a drummer on a click) ([Carter & von Appen 2025](https://theory.esm.rochester.edu/integral/?p=9705)) |
| Rate of change | a new section every 8 bars (4 or 16); dynamics between sections carry the song | [MusicRadar](https://www.musicradar.com/how-to/song-sections-explained-intro-verse-chorus-middle8-outro-tag-bridge) (chorus at a higher energy than the verse) |
| Role of the instrumental | the verses leave room for a voice; a vocal-like lead carries the sung melody | the brief's own requirement (instrumental pop rock), not research |
| Loudness of releases | Hot Rock & Alternative top songs (July 2025): -8.1 LUFS integrated average (-11.9 to -5.1), short-term average -5.3, true peaks -0.45 to +1.11 dBTP; streaming plays at -14 (Spotify), about -16 (Apple) | [iZotope rock/alternative analysis](https://www.izotope.com/en/learn/rock-alternative-analysis); [Spotify](https://support.spotify.com/artists/article/loudness-normalization/); [iZotope streaming guide](https://www.izotope.com/en/learn/mastering-for-streaming-platforms) |
| Dynamics (PLR, LRA) and width | PLR about 9.3 dB for hits since 2010; LRA of the rock chart songs 4.1-17 LU (median about 4.8); width: 2024 top-10 songs averaged -8.5 LU side minus mid, "alternative" in the middle of the genres; no rock number | [Țînț & Drăgulin 2025](https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335); iZotope rock analysis; [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends) |
| Master | `studio.py master vNNN --genre rock` (= `--target rock --lufs -10 --tp -1 --translate 0.3`) | Target curve: the mean of Pestana et al.'s measured pop and rock spectra (docs/MASTERING.md). -10 LUFS is an engine-limited choice, quieter than the charts. `--translate 0.3` and `--eq 0.7` are **hand-tuned** |

Changed from the previous setup: Spectre's shape now fills 3:00-4:00 (it summed to 2:35 before); typical tempo narrowed to 115-130; the tonal target is now measured, with much more 100-400 Hz (+5 to +7 dB re 1 kHz) and less sub and air than the old hand-tuned curve (kept as `--target rock_handtuned`). **Unsourced** in this brief: the drum patterns, hat/ride/crash usage, fills and half-time (craft knowledge), the lift tricks (key change, drop-out), and the "nearest wrong feelings" (an editorial brief).

## The references
- **Pop rock and arena pop rock:** Foo Fighters, Paramore, The Killers, Coldplay, Snow Patrol, Jimmy Eat World, Kelly Clarkson's rock singles, Imagine Dragons, Fall Out Boy.
- **Songs about getting through depression:** Coldplay "Fix You", Paramore "Last Hope", R.E.M. "Everybody Hurts", Jimmy Eat World "The Middle", Twenty One Pilots "Car Radio", Linkin Park "Numb", Bastille "Pompeii". Listen to how they *move*, not to their words.

## Tempo and the kit (engine names in brackets)
- **Tempo:** typically 115-130 bpm (see Configuration; the wider 100-150 range is unsourced). Ballad-builders like "Fix You" start slow (68 bpm) and open up. Feel is straight 8ths (`"swing": 0.5`) with a human hand (`humanize_ms` 4-8 on drums, a little `push_ms` on the snare for a laid-back backbeat).
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
- **Spectre's shape** (3:00-4:00; at 124 bpm a bar is 1.94 s): intro 8, verse 16, pre 4, chorus 8, tag 4, verse 16, pre 4, chorus 8, bridge 8, drop-out 1-2, double chorus 16, outro 8 = about 102 bars, 3:17. The first chorus lands at bar 29, about 0:54 (hits average 0:45; see Configuration). Shorter verses (8 bars) are fine if the song still reaches 3:00.

## Mixing and loudness
- The (here instrumental) vocal is king: everything is carved around the lead. Kick, snare, bass and lead are centred; double-tracked guitars hard left and right; toms and overheads (ride, crash, hats) panned by the drummer's perspective.
- Guitars and bass fight at 100-300 Hz; give the bass the bottom and the guitars the 300 Hz-3 kHz band. Kick and bass lock in time.
- **Loudness:** nine Billboard Hot Rock & Alternative songs (July 2025) averaged -8.1 LUFS integrated (range -11.9 to -5.1) with true peaks -0.45 to +1.11 dBTP, but the chart shows wide freedom in density and dynamics. For Spectre: `studio.py master vNNN --genre rock` (-10 LUFS; -9.5 at most). Keep the verse-to-chorus contrast; don't crush it.

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
| Master | `--genre rock` |

## Mastering (industry practice)
Researched 2026-11-24 under standing rule 8. The proposed configuration, the engine tests and every source are in [docs/proposals/mastering-trance-poprock.md](proposals/mastering-trance-poprock.md). **Measured** means a published measurement; **opinion** means engineer or platform guidance.

**Measured**
- **Loudness:** nine Hot Rock & Alternative songs (July 2025) averaged -8.1 LUFS integrated (range -11.9 "Wildflower" to -5.1 "Back To Friends"). Short-term max averaged -5.3 (max -3.3), true peaks ran -0.45 to +1.11 dBTP, and LRA 4.1-17 LU (most 4-6) ([iZotope 2025](https://www.izotope.com/en/learn/rock-alternative-analysis)). Global top-10 hits (H1 2024) averaged -8.3 ±1 LUFS, with LRA mostly 3.7-6.8 LU ([iZotope 2024](https://www.izotope.com/en/learn/mastering-trends)). The top 15 Spotify songs of 2025 had a short-term max of about -7 to -3.3 and LRA 3.7-10.4 LU ([Mastering The Mix](https://www.masteringthemix.com/blogs/learn/mastering-trends-for-2026)). PLR: 12.6 dB in 1990, 9.3 in 2010 and 2020 ([Țînț & Drăgulin 2025](https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335)).
- **Normalization:** Spotify turns louder masters down to -14 LUFS and raises quieter ones only within 1 dB of true-peak headroom ([Spotify](https://support.spotify.com/artists/article/loudness-normalization/)). A -10 master is therefore not quieter on normalized streaming, only less dense. Loudness numbers now describe density more than playback level (iZotope 2025).
- **Tonal balance:** the 2020 Billboard set had the most low and low-mid energy of 1990-2020, subdued high mids, and the least high end (Țînț & Drăgulin, iZotope Tonal Balance Control, no dB values). Pop and rock in Pestana et al. (2013) pool 1950-2010 #1s. Digital-era masters extend to about 20 kHz, while 1980s masters had nothing above 16 kHz ([iZotope decades](https://www.izotope.com/en/learn/comparing-tonal-balance-in-popular-music)). One modern-chart note: "Stargazing" dips about 4.5 kHz to tame saturation brashness (iZotope 2025). The lead vocal sits about 0.2 dB above the accompaniment in rock, against 2.7 dB in pop (1990-2020 Grammy nominees; Gerdes & Siedenburg 2023, JASA EL): rock buries the voice in the band.
- **Width:** 2024 hits averaged -8.5 LU side minus mid, with alternative in the middle of the genres (iZotope 2024). There is no rock number. "Messy" modulates width between verses and choruses.

**Opinion (engineers, platforms)**
- Keep short-term loudness at or under about -9 LUFS at the loudest moments for dense guitar music. Many releases push to -6 or louder and are then turned down 5-6 dB. Share the work between compressor and limiter. Add bite at 2-5 kHz only gently (mid channel), stop before guitar upper mids get painful, and use side-channel low-mid lift for hard-panned guitars ([Ian Shepherd for iZotope](https://izotope.com/en/learn/how-to-master-metal.html)).
- Ride sections by fractions of a dB (Greg Calbi: about +0.4 dB in the choruses of "Too Sweet"). Watch for "dynamic inversions", where limiting makes verses louder than choruses. Density, grit and saturation are accepted in current alt-rock masters ("Back To Friends" borders on distortion) (iZotope 2025).
- True peak: under -1 dBTP, or -2 dBTP above -14 LUFS (Spotify). Robjohns argues for -3 dBTP with lossy codecs (Sound On Sound 2019).

**For Spectre (proposal; genres.json not yet changed)**
- `--lufs -8.5`. Keep `--tp -1`, mono below 120 Hz, and aim width at -11 to -7 LU. Tested on `examples/poprock-test.json`: it lands at -8.5 LUFS and -1.04 dBTP, with PLR 7.5 and LRA 4.0 (unchanged from -10, so the verse-to-chorus contrast survives). The clipper shaves 5 dB of drum peaks (1.1% of samples), limiter reduction is 0.8 dB, and the true-peak guard is not needed. A 320 kbps MP3 peaks at -0.79 dBTP. -8 is possible (PLR 7.0).
- Proposed curve `rock_modern` = the measured `rock` with era offsets: +2 to +2.5 dB at 31.5-50 Hz, +1.5 at 63 Hz, +1 at 8 kHz, +1.5 at 10 kHz, +2.5 at 12.5 kHz, +4 at 16 kHz. These are estimates (±2-4 dB), pending measurement of owned modern pop-rock references.

## What session 008 learned
- Tune the kick around 72 Hz with a short decay; keep the bass off A1/B1 in verses; give distorted guitars low-shelf body (160-260 Hz) and pan the doubles about ±0.85.
- Darken the snare (fewer wires, a shelf from 4.5 kHz, a 9 kHz low-pass, a little 2.5 kHz crack); shelve hats, ride and crash so the top end isn't harsh on phones.
- The wordless `vox` gets buried behind guitars; a lead guitar or piano can carry the melody, or push the vox at 2.8 kHz.
- Playing a section 20-30 ms behind the beat reads as weight; playing on top reads as momentum.

## Sources
- MusicRadar, Anatomy of an arrangement (song sections): https://www.musicradar.com/how-to/song-sections-explained-intro-verse-chorus-middle8-outro-tag-bridge
- Mastering The Mix, How to mix big, punchy rock drums: https://www.masteringthemix.com/blogs/learn/how-to-mix-big-punchy-rock-drums
- Premier Guitar, Double trouble: make rhythm guitar parts great again: https://www.premierguitar.com/double-trouble-make-rhythm-guitar-parts-great-again
- iZotope, A LUFS and tonal analysis of top-charting rock and alternative songs (July 2025): https://www.izotope.com/en/learn/rock-alternative-analysis
- Hit Songs Deconstructed, 2024 #1 Hit Focus Report highlights (length, intro, form, tempo): https://hitsongsdeconstructed.com/wp-content/uploads/2025/02/The-Hit-Songs-Deconstructed-1-Hit-Focus-Report-Highlights.pdf
- T. de Clercq (2017), Interactions between harmony and form in a corpus of rock music, Journal of Music Theory 61(2): https://www.midside.com/publications/declercq_2017_jmt.pdf
- Dahl, Huron, Brod & Altenmüller (2014), Preferred dance tempo, JNMR 43(2) (summarises Moelants 2002): https://vbn.aau.dk/ws/files/201902553/Dancetempo_JNMR_accepted_source_Jan2014.pdf
- Carter & von Appen (2025), Tempo variability in Billboard Hot 100 songs 1966-1995, Intégral 38: https://theory.esm.rochester.edu/integral/?p=9705
- M. A. Țînț & S. Drăgulin (2025), From data to hits (loudness, PLR, length of Billboard year-end hits): https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335
- Pestana et al. (2013), spectral characteristics of commercial recordings (the rock target curve; see docs/MASTERING.md): https://www.aes.org/e-lib/browse.cfm?elib=17010
- Songtell, "Fix You" (Coldplay): https://songtell.com/coldplay/fix-you
- IBTimes, Hayley Williams on how mental health struggles shaped "Last Hope": https://www.ibtimes.co.uk/ive-wanted-not-here-hayley-williams-reveals-how-mental-health-struggles-shaped-last-hope-1759886
- Industry mastering research, tests and full source list: docs/proposals/mastering-trance-poprock.md
