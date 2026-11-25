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

## Mixing the voice (researched 2026-11-24)
For a sung hook or line in a pop rock track (the wordless `vox` lead follows the same rules without the word checks). The principles for every genre, the choir research and the check procedure are in [docs/voice/MIXING.md](voice/MIXING.md). Values marked *(hand-tuned)* are Spectre's starting points.

**What the research says**
- **Level with the band, not on top of it:** rock leads sit 0.2 dB over the accompaniment on average (pop 2.7 dB; metal -3.1 dB; solo rock artists 2.5 dB higher than bands) ([Gerdes & Siedenburg 2023](https://www.geidai.ac.jp/~marui/course_enshu_2024/gerdes_siedenburg_202304.pdf)). A rock voice is heard through the guitars because it is denser and because the band makes room, not because it is louder.
- **How engineers keep it there.** Ken Andrews (Paramore) builds a strong instrumental first and then makes the vocal "compete": a high-pass at 62 Hz, a multiband for general control, an optical compressor hit hard, saturation at "around 30 to 40 percent" that he raises (sometimes automates) in dense passages to keep the vocal on top instead of riding the fader, and a de-esser last; to make room he takes "some 1k or 2k out of the guitars or keyboards" or pans parts wider ([Sound On Sound](https://www.soundonsound.com/techniques/inside-track-paramore)). Jacquire King (Kings of Leon) runs EQ, a fast FET compressor and a de-esser in series and blends in a compressed, excited copy for high-frequency presence ([Sound On Sound](https://www.soundonsound.com/techniques/inside-track-kings-leon-sex-fire)).
- **Space is a plate and delays, in changing amounts.** Both use an EMT 140 plate and slap and longer delays, "two or three delays and two or three reverbs in total", with different amounts in different song sections; King adds a distant double in the chorus recorded in another space (same sources). No decay times or levels are published. General practice for a voice that must stay in front: pre-delay of 30-100 ms, the reverb pulled down until the voice separates from the band and then halfway back, a slap of about 100 ms without feedback, a short ambience under 100 ms to lock the voice into the band ([Paul White, Sound On Sound](https://www.soundonsound.com/techniques/vocal-production); [Mix Rescue](https://www.soundonsound.com/techniques/mix-rescue-jay-menon)).
- **Mastering:** rock masters are dense (chart average -8.1 LUFS; Spectre -10). The master's compression and limiter bring reverb up between phrases, and its bus EQ may lift the highs (King's did), which lifts sibilance. Set the vocal reverb a little lower than sounds right on the premaster, and check words on the master.

**The owner's note on "Here You Are" (session 009, candidate v032): "reverb a bit too loud".** The measurements agree, and so does the research. The candidate's voice sends 0.32 into the bus behind a 60 ms pre-delay, plus 0.12 to the delay. In the blend study that setting put the voice's reverb 8.4 dB under the dry voice, while the band's own reverb sat 22.6 dB under the band: the voice is about 14 dB wetter than everything around it. The setting was chosen because it scored best on the study's width and Whisper measures, not by ear, and no source supports a rock lead that much wetter than its band. The study's own table gives the scale: send 0.22 = 11.4 dB under; each halving of the send is 6 dB. **Recommended:** `send_reverb` 0.16-0.20 (about 12.5-14.5 dB under the dry voice), the pre-delay kept at 60-80 ms, and the sense of space made up with a slap instead of more reverb. An A/B of sends 0.32, 0.18 and 0.12 on the study's chorus was started and abandoned (the machine was busy with three producers), so the effect of the lower send on the word score was not measured then. **Measured on the next render (session 009, v034):** the chain below with send 0.18, pre-delay 70 and the slap put the voice's reverb 13.2 dB under its dry signal in every chorus (v032: 8.2; the band 20-23), and with the level held (-0.2 to +0.4 LU against the band) Whisper on the master read 79 / 58 / 46 / 63 % of the words per chorus against v032's 71 / 54 / 42 / 54 %: no chorus worse, a gain within the model's noise. Two things the chain hides: at the voice's level after the compressor, `sat` 0.15 is almost linear and acts as +4.2 dB of gain (take it out of the final `gain`), and the lower send plus the slap's `mix` 0.1 (dry -0.9 dB) cost the voice about 1.2 LU, so the final `gain` goes back up by that much (v033 left it down: -0.8 to -1.4 LU, and the word score fell to 38-54 %). Net: `gain` 11 where v032 had 14.

**Starting chain: a sung hook over double-tracked guitars** (the blend-d chain from MANUAL "Voices" with less reverb and a slap; *hand-tuned* except where the blend study measured it):
```json
"mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -6, "lpf": 7000},
        "delay":  {"beats": 0.75, "feedback": 0.3, "return_db": -9, "lpf": 4500}},
"voxC": {"inst": {"type": "singer", "source": "svs", "voice": "hanami", "double": 0.2, "double_pan": 0.7,
                  "inhale": 0.3, "svs_fade_in_ms": 30, "svs_fade_out_ms": 120},
         "send_reverb": 0.18, "reverb_predelay_ms": 70, "send_delay": 0.08,
         "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 800, "gain_db": -2.5, "q": 0.9},
                {"type": "highshelf", "hz": 8000, "gain_db": 3}, {"type": "comp", "threshold_db": -22, "ratio": 3},
                {"type": "sat", "amount": 0.15}, {"type": "delay", "beats": 0.25, "feedback": 0, "mix": 0.1},
                {"type": "gain", "db": 11}], "gain_db": 12},
"guitars": {"fx": ["...", {"type": "eq", "hz": 2500, "gain_db": -2.5, "q": 0.7}]}
```
- **Reverb:** a plate-length space (`size` 0.5-0.6 = 1.15-1.4 s), send 0.16-0.20 in choruses, 0.10-0.14 in verses (drier and closer when the band is small), pre-delay 60-80 ms. The slap (`beats` 0.25 is 110 ms at 136 bpm) gives depth without a tail.
- **Level:** -1 to +0.5 LU against the band in a chorus (the measured rock figure; session 009's candidate sits at -0.2 to +0.3), up to +2 in a sparse verse.
- **Room in the band:** 2.5 dB out of the guitars at 2.5 kHz (measured in the blend study); more voice level beyond that only puts it on top (session 009, v031).
- **Density instead of level:** `sat` 0.1-0.2 after the compressor, a little more in the last chorus (Andrews' move); `double` 0.2 panned 0.7, up to 0.35 for the final chorus.
- **Words that got lost in session 009** ("round and round" heard as "running down") are short syllables on 8th notes with soft consonants: that is a writing and note-length problem (MANUAL "Voices", syllable rate), not a mix problem; no chain will bring them back.
- **Backing voices and "oohs":** MIXING.md "Choir and ensemble voices": 4-8 LU under the lead, `hpf` 150-200, panned out, more reverb than the lead, `svs_vibrato` 0.4.

**How to check:** MIXING.md "Checking a voice": Whisper on each sung line on the master and on the voice alone; the vocal-versus-band loudness and the wet-to-dry ratio from the muted and returns-off renders (`examples/vocals/svs/blend.py` does exactly this for session 009's chorus). Expect 50-60% of words on a dense guitar chorus at best; compare versions.

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

## Layering and EQ carving (researched 2026-11-25)
The cross-genre method is in [PRODUCTION.md](PRODUCTION.md). Labels: **[M]** measured, **[S]** a named source, **[P]** carried over from a professional trance producer's EQ map (2026) where the instrument is shared, **[H]** hand-tuned.

**Layer roles.** A rock band is layered by the way it is recorded and doubled, not by stacking synths:
| Part | Layers and their jobs | Label |
|---|---|---|
| **Rhythm guitars** | two takes hard left and right with *different* tones or voicings (one low and anchored, one higher; one muted while the other rings: "Guitars" above), optionally a third in the centre in the last chorus; a clean or acoustic layer under the driven pair for note definition | [S] this brief; the third layer [H] |
| **Kick** | the shell's weight (60-80 Hz), the knock (100-200 Hz), the beater (1-5 kHz): one drum heard through close and room microphones; in the engine one `kitkick` plus its `room` | [S] iZotope EQ cheat sheet |
| **Snare** | body (150-250 Hz), crack (2-3.5 kHz), wires and air (8 kHz up), the room; a tambourine or clap layered on the chorus backbeat | [S] iZotope; the chorus layer [H] |
| **Bass guitar** | low end (40-120 Hz) and definition (800 Hz-1 kHz, the pick or the amp's growl), often recorded as a clean and a driven signal blended | [S] iZotope; the two-signal habit [H] |
| **Keys** | organ or pad as glue under the guitars, piano for attack on top of them | [H] |
| **Voice (or the vocal lead)** | lead in the centre, a quieter wide double, harmonies and gang vocals in the last chorus ("Mixing the voice") | [S] |

**EQ map** (starting ranges; confirm on the actual sounds):
| Instrument | High-pass | Cut / control | Emphasise | Source |
|---|---|---|---|---|
| Kick | 30-40 Hz [H] | 200-500 Hz boxiness | 60-80 Hz punch, 100-200 Hz knock, 1-5 kHz attack | iZotope cheat sheet |
| Snare | 80 Hz | 300-500 Hz boxiness, 400-700 Hz ring, 900 Hz-1.5 kHz papery | 150-250 Hz body, 2-3.5 kHz attack, 8 kHz up | iZotope |
| Toms | 50-60 Hz [H] | 250-600 Hz mud | 60-120 Hz body, 800 Hz-1.5 kHz attack | iZotope |
| Hats, ride, crashes | 150 Hz at least; 300-500 Hz on hats [H] | about 4 kHz harshness (3-7 kHz on hats) | 8-12 kHz air | iZotope |
| Bass guitar | 30-40 Hz [H] | 300-500 Hz mud | 40-120 Hz low end, 800 Hz-1 kHz definition | iZotope |
| Driven guitars | 100 Hz | 200-300 Hz tubbiness, 3-6 kHz fizz | 300 Hz-1.5 kHz, the body of the sound | iZotope. **Local caveat [M]:** the engine's `eguitar` is thin at 100-300 Hz, so session 008 added low-shelf body at 160-260 Hz ("What session 008 learned"); cut there only on a guitar that has it |
| Clean and acoustic guitar | 70-100 Hz | 200-400 Hz mud | 1.5-2.5 kHz presence, 8-12 kHz air | iZotope |
| Piano | 60 Hz; 100-200 Hz under a full band [P] | 200-500 Hz mud | 2-5 kHz in a dense mix [P] (iZotope lists 2-4 kHz as possible harshness on an exposed piano) | iZotope; [P] |
| Organ, pads | 150-250 Hz | 200-500 Hz | 1-3 kHz | [P] |
| Voice | 80-120 Hz (svs voices: this brief's chain) | 200-400 Hz; nasal 500 Hz-1.2 kHz; 5-8 kHz sibilance | 2-5 kHz; air from 10 kHz | iZotope; [P] |
| Reverb and delay returns | 200-500 Hz | 300-600 Hz | low-pass at 6-12 kHz | [P]; Houghton, Sound On Sound 2022 |

General moves [S]: a 70 Hz, 12 dB/octave high-pass on most sources except kick and bass; decide which of two clashing sources matters and cut the other there, a small boost on the first and a small cut on the second; a sidechained dynamic EQ cut in place of broadband ducking (Houghton, Sound On Sound 2022). Measured reference for the voice level: lead vocal against accompaniment averages +0.2 dB in rock and +2.7 dB in pop (A-weighted, Grammy nominees 1990-2020; Gerdes and Siedenburg 2023).

**Glue** [S], [H]: the kit on one bus (the engine's `room` on each piece stands in for it); both guitars on one bus with a little compression; light mix-bus compression (2:1, 1-2 dB) is the rock norm. The engine has no buses yet (PRODUCTION.md, proposals).

**Where Spectre stands** [M] (stems of session 009's last chorus, rendered in memory, 2026-11-25; 15 sounding stems): the voice is the loudest stem in every region from 150 Hz to 18 kHz; both guitars, the bass and the kick are 44-66% masked; the organ is 98% masked, in effect absent; five sources sit within 10 dB at 150-400 Hz (voice, both guitars, snare, bass). The voice is carved well; what is under it has no slots of its own. Nothing but the voice, the snare and the cymbals reaches above 6 kHz.

## Era assessment of the master target (2026-11-25)
**What the current curve is.** `rock`: the mean of Pestana et al.'s (2013) "pop" and "rock" genre averages: number-one singles 1950-2010, leaning on 1960s-1980s records, magnitude-averaged (docs/MASTERING.md). The earlier `rock_handtuned` curve is kept for comparison.

**Measured against the catalogue** [M] (method, validation and limits in docs/TRANCE.md, section C: MusicBrainz recordings tagged `pop rock`, up to 100 per year, with AcousticBrainz data; 1,387 tracks 1995-2021):
| Band (Hz, as analysed), dB re 510 Hz-2 kHz | 1995-99 | 2000-04 | 2005-09 | 2010-14 | 2015-21 | `rock` curve | `rock_handtuned` | 008 Anyway | 009 Here You Are |
|---|---|---|---|---|---|---|---|---|---|
| tracks | 266 | 220 | 225 | 252 | 424 | | | | |
| 32-97 (kick and bass) | +6.1 | +6.9 | +8.6 | +7.8 | **+9.5** | **+6.2** | +9.3 | +7.0 | +7.1 |
| 97-140 | +4.9 | +5.5 | +5.7 | +5.4 | +6.5 | +9.1 | +6.7 | +8.2 | +8.1 |
| 140-183 | +3.2 | +3.3 | +3.7 | +3.9 | **+4.8** | **+8.2** | +5.0 | +7.4 | +6.2 |
| 183-291 | +5.6 | +6.0 | +5.7 | +6.5 | +6.6 | +9.3 | +6.8 | +9.2 | +8.9 |
| 291-400 | +2.9 | +3.1 | +3.1 | +4.3 | +4.0 | +6.0 | +4.3 | +6.9 | +5.6 |
| 6400-7700 | -8.2 | -8.6 | -7.7 | -9.2 | -7.5 | -8.6 | -5.9 | -9.1 | -9.6 |
| 7700-9500 | -9.6 | -9.8 | -8.5 | -10.1 | -8.4 | -9.8 | -6.5 | -11.0 | -10.6 |
| 9500-12000 | -12.0 | -11.7 | -10.6 | -12.1 | **-9.6** | **-12.3** | -7.8 | **-14.7** | **-13.7** |
| 12000-15500 | -16.1 | -17.1 | -14.7 | -16.9 | -13.2 | -16.5 | -10.1 | -18.6 | -17.3 |

- **What changed in pop rock** [M]: the kick-and-bass band rose by about 3.4 dB from the late 1990s to 2015-21 and the top (9.5-15.5 kHz) by 2.4-2.9 dB; the low mids rose slightly. The loudness estimate for this tag is too scattered to quote (middle half about -18 to -10 LUFS in every period); the chart figures in "Configuration" stand.
- **Where the target stands** [M]: `rock` matches pop rock of the late 1990s in the kick-and-bass band and on top, as its sources suggest, but it has 1.7-3.4 dB more at 97-400 Hz than any period. Against 2015-21 it is 3.3 dB short at 32-97 Hz and 1-3.3 dB dark from 6.4 kHz up. `rock_handtuned` fits 2015-21 within 0.4 dB from 32 to 510 Hz but is 1.6-3.2 dB too bright from 4.4 kHz up.
- **Spectre's masters** [M]: 2.5 dB short in the kick-and-bass band, 1.5-3 dB heavy from 97 to 510 Hz, and 1.6-5.4 dB dark from 6.4 kHz up (darker than the curve itself: the master may boost the top by at most 2 dB, and little in these mixes is up there to boost).
- **A current target.** *Interim* [M, fitted as in TRANCE.md C; adopted 2026-11-25 as `rock_2015`, below]: 31.5 Hz -11.5, 40 -7.5, 50 -2.5, 63 +2, 80 +4, 100 +5, 125 +3.5, 160 +3, 200 +2.5, 250 +2.5, 315 +2, 400 +1.5, 500 +2, 630 +2, 800 +1.5, 1k 0, 1.25k -0.5, 1.6k -0.5, 2k -2, 2.5k -2.5, 3.15k -4, 4k -5.5, 5k -7, 6.3k -7.5, 8k -8, 10k -10.5, 12.5k -13, 16k -20 (dB re 1 kHz). *Definitive:* 20-30 current pop rock masters measured locally (PRODUCTION.md "Era-appropriate targets"). This curve was also borrowed by `joc`, `caroling`, `latinpop` and `chamberscore`; each of those docs has its own assessment, and since 2026-11-25 each has its own target.
- **Adopted (2026-11-25): `rock_2015`**, the default target of `--genre rock` (408 tracks tagged pop rock, 2015-2021): against the old `rock` curve +6 to +7.5 dB at 31.5-63 Hz, -1 to -3.5 dB at 100-400 Hz, +1.5 to +3.5 dB at 6.3-16 kHz. It is the same measurement refit by `tools/refcurve.py` (which reproduces the medians above within 0.4 dB; curve, n, spread and validation in docs/MASTERING.md "Era targets", provenance in engine/genres.json); the released tracks keep their masters until the owner approves a remaster (`master --published` reproduces their settings).

Sources for these two sections: iZotope, EQ cheat sheet: https://izotope.com/en/learn/eq-cheat-sheet ; M. Houghton, How to achieve better separation in your mixes, Sound On Sound (2022): https://www.soundonsound.com/techniques/how-achieve-better-separation-your-mixes ; M. Senior, Q. What should I EQ to improve my muddy mixes?, Sound On Sound (2008): https://www.soundonsound.com/sound-advice/q-what-should-eq-improve-my-muddy-mixes ; a professional trance producer's EQ map (2026; docs/TRANCE.md); MusicBrainz search API and AcousticBrainz low-level data (CC0; https://acousticbrainz.org/), measured 2026-11-25; everything else in docs/PRODUCTION.md "Sources". Also: K. Gerdes and K. Siedenburg (2023), Lead-vocal level in recordings of popular music 1946-2020, JASA Express Letters 3(4), doi:10.1121/10.0017773

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
