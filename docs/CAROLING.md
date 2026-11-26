# American Christmas caroling: a working brief

For sessions that make an instrumental in the world of American Christmas caroling: carolers at the door and in the street, close four-part harmony, handbells, a brass quartet on the corner, an organ behind the door. A vocabulary, not a rulebook. Researched 2026-11-24 for session 012. Spectre makes instrumentals: the carolers' voices are an instrument here (a choir texture, a refrain fragment, a call at the door; see "Voices"), never a sung carol carried by a lead vocal.

## Configuration (engine: `--genre caroling` in engine/genres.json)
| Setting | Value | Source |
|---|---|---|
| Length | **2:00-3:30**, typically 2:20-3:15 (one carol, two to four verses; medleys and concert anthems run longer) | MusicBrainz track lengths of five Christmas choral albums (catalogue below): Ray Conniff Singers, *Here We Come A-Caroling* (1965; 12 tracks): median **2:25**, middle half 2:11-2:48; Pentatonix, *That's Christmas to Me* (2014, a cappella): 3:05; Straight No Chaser, *Holiday Spirits* (2008, a cappella): 3:13; Chanticleer, *A Chanticleer Christmas* (2010): 2:39; King's College Choir, *Christmas Carols from King's College* (1986): 3:10. A caroling group aims at "two or three minutes, a moment of respite" for passers-by ([Milwaukee Magazine](https://www.milwaukeemag.com/meet-wisconsins-traveling-troupe-of-dickens-carolers/)) |
| Form | **strophic**: verses of four or eight phrases (two or four bars each) with a refrain or chorus ("Nowell, Nowell", "Gloria"); two to four verses; verses vary by texture (unison, four parts, a descant, a solo verse, a key lift, a bell or brass interlude); an introduction of the last phrase or a bell peal; a held, often slowed final cadence | the hymnal and carol-book settings below (Hutchins 1916; Bramley & Stainer 1871): every carol is printed as one verse of music with further stanzas below it, refrains marked "Chorus" or "Refrain", dynamics per stanza (*p* ... *cr* ... *f*), some carols marked "Unison"; Neale and Helmore's *Carols for Christmas-tide* (1853) "harmonized in four parts" ([Gresham College](https://www.gresham.ac.uk/node/13042)) |
| Tempo | **6/8 carols: dotted quarter about 50-60; 3/4 and 4/4 carols: quarter about 84-112**; slow carols ("Silent Night") lower; rubato at phrase ends and a ritardando into the last chord (*rall.*, *molto rall.* in the carol books) | Mutopia's MIDI tempo marks: CAROL (6/8) quarter = 85, i.e. dotted quarter about 57; THE FIRST NOWELL (3/4) quarter = 107 ([Mutopia](https://www.mutopiaproject.org/)); AcousticBrainz tempo estimates of the recordings below (Conniff: "Joy to the World" 86, "Away in a Manger" 112, "O Little Town" 122, "Here We Come A-Caroling" 100; algorithmic, unreliable on unaccompanied rubato choirs, octave errors likely); the hymn tempo follows the text: "reverent", "meditative" slower, "jubilant", "triumphant" faster ([BYU Organ Tutor](https://organ.byu.edu/organtutor/hymn_playing/tempo/influence_tempo/page1.htm)) |
| Meter and feel | **3/4, 6/8 or 4/4**, no backbeat, no drum kit; the pulse lives in the harmony changes and the bells; a 3-beat carol bar = **12 steps** in the engine (4 carol bars = 3 engine bars) | the carol books above; engine notation docs/MANUAL.md |
| Keys | the hymnal keys sit the melody between about D4 and E5 for untrained singers: CAROL ("It Came Upon the Midnight Clear") mostly B-flat (also A-flat, A, G); THE FIRST NOWELL D (Stainer) or E-flat (Hutchins); STILLE NACHT ("Silent Night") B-flat; ANTIOCH ("Joy to the World") D | hymnary.org tune pages: [CAROL](https://hymnary.org/tune/carol_willis), [STILLE NACHT](https://hymnary.org/tune/stille_nacht_gruber), [ANTIOCH](https://hymnary.org/tune/antioch_handel); the scans below |
| Rate of change | **by verse and by phrase**: something changes every verse (4-8 carol bars); inside a verse, dynamics and texture follow the words | the per-stanza dynamics in the carol books; **hand-tuned** craft |
| Role | the carolers carry the tune as a **choir texture** (voices as instruments), bells and brass answer and fill, an organ or piano may hold the harmony; no lead vocal carrying verses | standing rule "voices are instruments" (docs/ORCHESTRATION.md); the traditions below |
| Loudness of releases | **Billboard Holiday 100** (week of 6 Dec 2025, 10 songs): **average -12.9 LUFS** integrated (range -8.8 to -23.3), short-term max average -9.2, **LRA average 7.0 LU** (against 5.5 for 2025 releases in general); "the most popular Christmas music tends not to be pushed as loud". Choral and caroling albums are far quieter: estimated **-19 to -23 LUFS** (Conniff -19.4, Chanticleer -20.1, King's -22.8, medians); a cappella pop **-12 to -14** (Pentatonix -12.4, Straight No Chaser -13.6) | [iZotope 2025, holiday songs](https://www.izotope.com/community/blog/holiday-songs-lufs-2025); the catalogue below (AcousticBrainz ReplayGain, calibrated on Spectre's own masters; about ±1-2 dB) |
| True peak | **-1 dBTP** (every Spectre master; MP3 adds about 0.5 dB) | docs/MANUAL.md |
| Dynamics | keep the verse-to-verse arc (a quiet verse, a full last verse), LRA 6-8 LU; no dense limiting | iZotope 2025 (LRA 7.0 average); the carol books' per-stanza dynamics |
| Tonal balance | acoustic records have a "natural top-end decay"; choirs and bells carry little below 100 Hz; no measured choral curve exists in the engine | Pestana et al. 2013 (docs/MASTERING.md); "The Mastering decision" below |
| Low end and width | mono below 120 Hz (an organ pedal, a tuba or bass only); a wide but natural stereo picture (a spaced pair across the choir) | Sound On Sound (Mixing and recording, below) |
| Master | `studio.py master vNNN --genre caroling` (since 2026-11-25 = `--target caroling_ref --lufs -14 --tp -1 --eq 0.3 --translate 0.2`, no low-end boosts, mono below 120 Hz; the released 012 used `--target rock --eq 0.5`, reproduced by `--published`) | "The mastering decision" (history), "Era assessment" (the change) |
| Strand and era | a brief names its strand (street, choir, crooner, a cappella, handbells, brass) and era, or takes the current practice; the master settings per strand (`caroling_choir` at -18, `caroling_acappella` at -12, the default otherwise) are in engine/targets.json and genres.json `caroling.master_by_strand` since 2026-11-26 | "Granularity" below (2026-11-25) |

### The mastering decision: `caroling`, the `rock` curve reused, -14 LUFS
- **Loudness -14 LUFS.** Between the Holiday 100 average (-12.9) and the estimated choral albums (-19 to -23), at the level streaming services normalize to (Spotify -14). A caroling track at -10 would be louder than all but the two loudest songs of the Holiday 100 and would flatten the verse-to-verse arc. -14 is a choice inside a sourced range, not a measured median.
- **Curve: `rock`, reused** (as `joc` does), because it has the steepest top of the three measured curves, closest to an acoustic record's natural top-end decay. It was measured on pop and rock, not on choirs: it asks for 100-400 Hz body that a choir and bells don't have. So the EQ is lighter (`eq` 0.5, hand-tuned) and the master report will show boosts at the low end when the arrangement has no low instrument. If `eq_at_limit` lists 31-250 Hz, that is the curve, not a fault: add body in the mix only where the arrangement wants it (organ pedal, tuba or bass trombone, low strings), and don't chase the curve with sub. **Status: reused measured curve, hand-tuned EQ strength; replace with a measured choral or folk curve when one exists** (Pestana et al.'s folk average, Fig. 5, can be extracted with tools/pestana_ltas.py once the PDF is reachable).
- `translate` 0.2: little bass-harmonic enhancement, nothing leads in the bass.
- Test (examples/caroling/, two bare piano melodies): `master --genre caroling` runs and reaches -14.0 LUFS, -2.0 dBTP; the EQ sits at its limits because a lone piano line is nothing like the curve: a full arrangement is the real test.

## What American caroling is
- **The English roots.** Carols were "industrious servant-maid and humble labourer" songs in 1823 (William Hone listed 89 still in circulation); Davies Gilbert printed eight with their tunes in 1822, William Sandys's *Christmas Carols, Ancient and Modern* (1833) gave the earliest known tunes of "The First Nowell" and "I Saw Three Ships"; from 1850 the church took the carol over: Novello's church carols, Neale and Helmore's *Carols for Christmas-tide* (1853) in four parts, the Truro Nine Lessons and Carols (1880) ([Gresham College](https://www.gresham.ac.uk/node/13042)). The *waits*, bands that played the streets at Christmas for money, survive in the Salvation Army's band practice ([Caring](https://caringmagazine.org/what-is-the-short-story-of-salvation-army-music-and-salvation-army-musical-practice-at-christmas/)).
- **The American revival (about 1900-1930).** Hymnals with many Christmas songs spread caroling among ordinary people in the early 1800s; in the early 1900s caroling was revived in cities and towns (Washington, New York, Philadelphia), Detroit caroled for children's charities in 1919, and newspapers printed carols for readers to sing: the *Midland Journal* (1925, "The Christmas Carol: Pleasing Revival of an Old-Time Custom": "Silent Night", "God Rest You Merry Gentlemen"), the *Evening Star* booklet (1926: "Hark! The Herald Angels Sing", "O Come, All Ye Faithful") ([Library of Congress](https://blogs.loc.gov/headlinesandheroes/2018/12/the-merry-tradition-of-christmas-caroling/)). A Philadelphia department store printed *Christmas Carols together with Certain Familiar Hymns and Songs* (John Wanamaker, 1925) ([hymnary.org](https://www.hymnary.org/hymnal/CCCF1925?page=0)); Boston's *Carols Old and Carols New* (Hutchins, 1916) holds several hundred carols ([archive.org](https://archive.org/details/carolsoldcarolsn00hutc)).
- **Beacon Hill, Boston: door to door with handbells.** On Christmas Eve 1924 Margaret Nichols Shurcliff and her children rang handbells at her parents' house on Mount Vernon Street and walked the neighborhood; the crowd grew and followed them for about two hours; the Beacon Hill Bell Ringers drew people from across the US and Canada, streets were closed and the ringing went out on the radio, with one pause in the wartime blackouts; it now happens in front of a house on Louisburg Square, about 500 people, warm drinks and cookies after ([Nichols House Museum](https://nicholshousemuseum.org/?p=2606)).
- **Moravian brass.** The Moravian trombone choir (Posaunenchor, from 1733) came with the first settlers: trombones in soprano, alto, tenor and bass, still kept in Bethlehem (PA) and Winston-Salem (NC); brass "to announce special events and to accompany singing at outdoor services" ([Moravian Music Festival](https://moravianmusicfestival.org/festival-music/trombone-choir)).
- **Salvation Army brass at the kettle.** The kettles began in San Francisco in 1893 without a band; carols for brass groups from 1886; a brass quartet at the kettle "brings in a great deal more money" than a bell ringer; *Carolers' Favorites* (1953, arranged by Erik Leidzén); the New York Staff Band's Stock Exchange Carol Sing since 1948 ([Caring](https://caringmagazine.org/what-is-the-short-story-of-salvation-army-music-and-salvation-army-musical-practice-at-christmas/)).
- **The Dickensian carolers.** Today's hired caroling quartets dress Victorian ("hoop skirts, top hats and bonnets"), are often classically trained, sing "four-part harmony" (one Wisconsin troupe has about 20 singers and a book of just under 70 pieces, from "Silent Night" to pop songs) and aim at a few minutes of respite for passers-by ([Milwaukee Magazine](https://www.milwaukeemag.com/meet-wisconsins-traveling-troupe-of-dickens-carolers/)). This costume tradition sits next to the kitsch (see "Nearest wrong feelings").

## Instruments and roles
- **The carolers' choir (the tune):** four-part hymn harmony (soprano tune, alto, tenor, bass, mostly one chord per beat) or unison on refrains; a small group, close together, breathing together, slightly uneven. In the engine: female upper voices only (see "Voices"); lower parts on instruments.
- **Handbells:** the Beacon Hill sound. A tuned handbell radiates its fundamental and a strong third harmonic (its (3,0) mode is tuned to three times the fundamental), plus a sixth harmonic ([Rossing et al., ASA 1993](https://auditory.org/asamtgs/asa93ott/4pMU/4pMU10.html)): a near-harmonic bell, sweeter than a church bell. Bells ring a melody, a peal or chords; they ring on unless damped.
- **Brass quartet or trombone choir:** chorale voicing in four parts, the Salvation Army corner, the Moravian announcement; soft and round in the street, never a fanfare.
- **Organ:** behind the door or in the church: sustains the harmony, the pedal gives the only real bass.
- **Sleigh bells:** the secular side ("Jingle Bells", the sleigh ride); a jingle on beats, used sparingly.
- **Also:** piano or reed organ in the parlour, strings (orchestral recordings, Conniff), acoustic guitar (folk carolers; Gruber wrote "Stille Nacht" for two voices, choir and guitar, [hymnary.org](https://hymnary.org/tune/stille_nacht_gruber)).

## Harmony, rhythm, form
- **Harmony:** diatonic major, I-IV-V with secondary dominants at cadences (CAROL's V/V on "Peace on the earth", the F#4 leading into G), half cadences at the middle of a verse, plagal and perfect cadences at its end; a minor-mode carol ("God Rest Ye Merry, Gentlemen") is the exception. Four voices in close position, the tune on top; inner voices often move in thirds and sixths.
- **Rhythm:** the words' rhythm; triple and compound meters sway (6/8: two beats a bar); phrases start on upbeats and end on long notes; no syncopation.
- **Form:** the verse is the unit (8 or 16 bars), repeated with new words; a refrain or chorus at the end of each verse; variation by texture, not by new material. An introduction plays the last phrase; the end slows and holds.

## Voices (standing rule: voices are instruments)
- **What the engine has:** `singer` `"source": "svs"` (DiffSinger) with seven **female** voices (docs/voice/VOICES.md, engine/voices.json): `hanami` (warm, clear; tagged "carol choir"), `hanami-soft` (soft, dark: choir pads), `hanami-dark` (solemn, covered: an alto colour, less intelligible), `hanami-power`, and the LEONA voices (bright, youthful: wrong for a carol choir except as a child-like colour). Build the carolers as **female upper voices** (soprano and alto, divisi, doubled takes with other `seed`s, modes and banks a third or sixth apart; `examples/vocals/svs/choir-line-dry.mp3`). **Male voice (since 2026-11-25):** `hanami-male` (Hanami made male inside her synthesizer, B2-E4; docs/voice/VOICES.md "Male voices") can take tenor and bass lines for an SATB choir; it is soft and covered, not a trained choral tenor, and was not yet tried as a choir, so judge it by ear, or give tenor and bass to instruments (brass, organ, low strings) or to `choir`/`vox2` pads.
- **Range:** write the svs voices A3-D5 (sweet spot F#4-B4; Hanami's training data sits G3-D5). Both verified carols below sit D4-D5 in their hymnal keys: sing them there, or transpose down.
- **What a voice may do here:** a refrain fragment ("Nowell, Nowell", "to hear the angels sing"), a wordless choir ("oo", "ah") under the bells, a call at the door, a hummed verse. Never a carol sung through verse after verse by one voice.
- **Words:** only public-domain words may be sung (the stanzas of the verified carols below, as printed in their sources), or original words the producer writes. Note the voices' licence: credit Lotte V and the Potluck vocoder in the README (credit lines in engine/voices.json) and never use them for a political subject. The carols' words are religious; the terms as summarised in docs/voice/VOICES.md exclude political, hateful and illegal use, not religious texts.
- **Mix (choir texture):** voices a little behind the bells and brass, sharing one room (one reverb send for all carolers), panned like a small group standing in a line (soprano left of centre, altos right, doubles wider); see "Mixing the voice" below for the researched chain and the session 012 diagnosis.

## Mixing and recording practice
- **A choir is recorded as a group, at a distance:** a stereo pair (ORTF, or spaced cardioids about half the choir's width apart), one to two metres in front of the front row and a metre or more above it; the distance sets the balance of direct and reverberant sound; a spot mic for piano or organ, not too prominent; outriggers for a large choir; or close and "too dry", with reverb added in the mix ([Sound On Sound, Q&A](https://www.soundonsound.com/sound-advice/q-how-do-you-record-choir)). A live choral recording got convolution reverb on its close mics "to impose the acoustics of a real concert hall" and about 6 dB of compression on the vocal subgroup's peaks ([Sound On Sound, live choral](https://www.soundonsound.com/techniques/recording-live-choral-performance)).
- **Outdoors in winter the room is the street:** fresh snow is a strong absorber (a 4-inch layer has an NRC of 0.89, like acoustic panels); compacted snow and ice reflect far more ([Acentech](https://www.acentech.com/resources/the-quiet-snow/)). A carol at the door is dry and close, with short early reflections off the house fronts and no long tail; a church or hall carol (King's College) has a long reverb. Choose one space per moment and let a change of space mean something (the door opening, coming inside).
- **Tonal shape of holiday records:** sparkly top ends on modern productions, roll-off below about 80 Hz on Mariah Carey's single, mono mixes on the early-1960s classics ([iZotope 2025](https://www.izotope.com/community/blog/holiday-songs-lufs-2025)).

## Mixing the voice (researched 2026-11-24)
The principles that hold in every genre, the choir and ensemble research, and how to run the checks are in [docs/voice/MIXING.md](voice/MIXING.md). This section is what changes for a carol. Values marked *(hand-tuned)* are Spectre's starting points, not sourced numbers.

**What the research says**
- **Two traditions, two amounts of reverb.** A church or cathedral choir is recorded from a distance in a long room (see "Mixing and recording practice"); when a choir is close-miked in a small room, the engineer adds the room afterwards: early reflections with no pre-delay plus a hall tail of 2.66 s in one documented mix of a 20-voice choir ([Sound On Sound, Session Notes](https://www.soundonsound.com/techniques/session-notes-recording-choir)). The a cappella pop tradition (Pentatonix) does the opposite: dry, close voices, each tuned and de-essed twice, the backing voices alone sent to a church-preset reverb, the lead on a quarter-note and a slap delay ([Sound On Sound, Inside Track: Pentatonix](https://www.soundonsound.com/techniques/inside-track-pentatonix)). Door-to-door caroling is the driest of all: fresh snow absorbs like acoustic panels (Acentech, above). So "how much reverb" is a choice of place, and a carol sung at a door or in a parlour is a short room, not a church.
- **Singers themselves prefer a moderate room.** Singers tested in three simulated rooms preferred 1.77 s over 4.79 s and over the dry room, sang slower as the room grew (84, 79.5 and 71.7 bpm) and rated the dry room best for singing in time ([Fischinger, Frieler & Louhivuori 2015](https://jyx.jyu.fi/bitstream/123456789/49954/1/influenceofroomacousticsonchoirsinging.pdf)).
- **Sung words are fragile, and the consonants carry them.** Unaccompanied sung words were misheard 7 times as often as the same words spoken, and 78% of the phoneme errors were consonants ([Collister & Huron 2008](https://d-scholarship.pitt.edu/19444/1/EMR000050a%2DCollister%2DHuron.pdf)). Reverberation fills exactly the gaps consonants make, and a group that does not place its consonants together smears them: paired singers started notes 57 ms apart on average with eye contact, and listeners noticed differences of 10-38 ms ([D'Amario, Daffern & Bailes 2019](https://eprints.whiterose.ac.uk/148848/1/journal.pone.0218162.pdf)).
- **A choir is not several soloists.** Singers in choral mode put less energy at 2-4 kHz and more in the fundamental than the same singers singing solo, use narrower vibrato, and listeners prefer the blended mode; a section's pitch scatter is tolerated up to about 14 cents but zero is preferred ([Ternström, overview of choir acoustics](https://scispace.com/pdf/choir-acoustics-an-overview-of-scientific-research-published-2em0kyqmrt.pdf)). Details and what they mean for svs choirs: MIXING.md, "Choir and ensemble voices".
- **Processing is light.** High-pass at 85-110 Hz, a high shelf only to make dull microphones match (Session Notes, above); about 6 dB of compression on the choir subgroup's peaks in a live recording (Sound On Sound, live choral, above). No published source gives a choir-versus-accompaniment level; in the genre the choir is the lead and bells, brass and organ answer it.
- **Mastering.** Christmas choral albums sit at about -19 to -23 LUFS and a cappella pop at -12 to -14 (catalogue below); at Spectre's -14 the limiter barely works, so the master changes the voices through its tonal EQ, not its dynamics. The `caroling` configuration borrows the `rock` curve, which expects far more energy at 5-12 kHz than voices, bells and organ have. Do not make up the difference with shelves on the voices (see the diagnosis): let the bells and the organ's upper stops carry the top, and accept a top-end note in the master report if the alternative is hissing consonants. The phone check matters here: its presence peak at 3 kHz is where a choir's consonants and its harshness both live.

**The engine's reverb, measured** (one shared bus, `mix.reverb`; decay time T30 through the bus filters): `size` 0.25 = 0.8 s, 0.35 = 0.9 s, 0.5 = 1.15 s, 0.6 = 1.4 s, 0.75 = 2.1 s (the default), 0.85 = 3.0 s, 0.9 = 4.0 s. It cannot go under about 0.7 s: a parlour or a doorstep is a small `send_reverb` into a small `size`, not a small room simulated exactly. The `room` effect on a voice blends it but smears the words (MANUAL "Voices").

**Starting chain: carolers singing words** (each voice its own track and take; all values *hand-tuned* except where the diagnosis below measured them):
```json
"mix": {"reverb": {"size": 0.3, "damping": 0.4, "return_db": -7, "lpf": 9000}},
"sop":  {"inst": {"type": "singer", "source": "svs", "voice": "hanami", "seed": 3, "svs_vibrato": 0.4,
                  "inhale": 0.3, "svs_fade_in_ms": 20, "svs_fade_out_ms": 140},
         "pan": -0.35, "send_reverb": 0.12, "reverb_predelay_ms": 30, "push_ms": 0, "humanize_ms": 0,
         "fx": [{"type": "hpf", "hz": 110}, {"type": "eq", "hz": 850, "gain_db": -2.5, "q": 0.9},
                {"type": "highshelf", "hz": 8000, "gain_db": 3}]},
"alto": {"...the same, with": "voice hanami or hanami-soft, another seed, pan 0.35, 2-3 dB under the soprano"}
```
- **Voices for words:** `hanami` (and `hanami-soft` for a second colour). **Never `hanami-dark` on words:** its lowered formants blur them (measured below and in VOICES.md); keep it for "oo" and "ah".
- **Reverb:** parlour or doorstep `send_reverb` 0.08-0.15 into `size` 0.25-0.35; a hall carol 0.2-0.3 into `size` 0.6-0.75 with `reverb_predelay_ms` 60-80; a church (`size` 0.85, 3 s) only for wordless lines or a closing chord. Pre-delay 30-100 ms keeps a voice in front of its reverb ([Sound On Sound, Vocal Production](https://www.soundonsound.com/techniques/vocal-production)). One space at a time; change it only where the story changes place.
- **Timing:** on a line with words every voice gets `push_ms` 0 and `humanize_ms` 0, so plosives and sibilants land together; give the line its own breath (a rest of at least an 8th before its first word, never tied to a preceding "ah"). Timing and pitch scatter belong on wordless textures.
- **Words on every voice.** Putting the words on one voice and "ah" on the others hid them in the test below (1 word of 8); fewer voices singing the same words together is the way to thin a line.
- **Wordless choir texture ("oo", "ah"):** `svs_vibrato` 0.3-0.5, different `seed`s, modes and banks, `push_ms` spread over ±10-25 ms, `send_reverb` 0.2-0.35, pans wider (±0.4-0.8), 3-6 dB under the word line, no high shelf (a dull pad is right).
- **EQ:** `hpf` 110, a small 800-850 Hz dip, one high shelf of 3-4 dB at 8 kHz; the engine has no de-esser, so every further dB of shelf is paid in sibilance and breath. No compressor on a carol voice, or `{"type": "comp", "threshold_db": -20, "ratio": 2}` at most; set levels with `gain_db` and section `auto`.
- **Level:** the word line 0-3 LU over the accompaniment under it when bells or organ play, and the quoted line never under the texture voices around it *(hand-tuned; no published choir figure)*. Lower voices go under the tune, not over it.
- **Width:** sopranos left of centre, altos right, doubles wider; no `double` on a voice that already has a second take on its own track.

**How to check** (procedure in MIXING.md, "Checking a voice"): Whisper (small.en) on the quick master of the bars that carry words, once on the mix and once on the voices alone (premaster minus a render with the voice tracks muted); the vocal-versus-band loudness from the same two renders. A line that reads on the voices alone and not in the mix is a level or masking problem; a line that does not read on the voices alone is a voice, timing or register problem, and no mix move will fix it.

### Diagnosis: the quote in "The Note She Kept" (session 012, v028; measured 2026-11-24)
The owner heard the quoted line "Peace on the earth, good will to men" as very hard to understand, its start "like a cat meowing", and suspected the reverb. Excerpts of the two places it is sung were re-rendered with one change at a time and transcribed by Whisper (small.en, on the quick master, one run per variant: read a difference of one word as noise). "Words heard" counts the line's eight words found in order.

| the meeting (0:25-0:36; soprano `hanami` at D5, alto `hanami-dark` an octave below) | words heard in the mix | transcription |
|---|---|---|
| as released (sends 0.3 into a 1.15 s reverb, return -7 dB) | 2 of 8 | "Beside the Earth, they're glitching and the wind" |
| no reverb | 5 | "Beside the earth, good will to man" |
| soprano alone, no reverb | 7 | "Peace on the Earth, Goodwill to man" |
| alto alone, no reverb | 0 | nothing in the mix; the voice alone: "This song is too much and I'm" |
| **alto on `hanami` instead of `hanami-dark`, reverb as released** | 7 | "Peace on the earth, good will to man" |
| the same with sends 0.18, 0.10, 0.05, 0 | 7 each | the same words |

| the a cappella reprise (1:52-2:02; four voices on the words, `low` on "ooh") | words heard | transcription |
|---|---|---|
| as released | 4 of 8 | "I am stronger, with good will to men" |
| no reverb | 7 | "God is on the earth, good will to men" |
| a rest before "Peace" (it was tied to the "ah" before it), alto on `hanami` | 6 | "Is on the earth good will to man" |
| **the rest, the alto on `hanami`, and all four voices on `push_ms` 0 (they were +14, -9, +22, +27 ms), reverb as released** | 8 | "Peace on the Earth, Goodwill to Men" |
| the words on one soprano, the other three on "ah" | 1 | "There's something I've been through to live" |

What it shows:
1. **Two causes, and the reverb is only one of them.** Taking the reverb away brings back three words in each place (2 to 5, 4 to 7), so the owner's ear is right that it hurts. But the first word never comes back that way, and changing the voices instead brings back more (2 to 7 in the meeting, 4 to 8 in the reprise) with the reverb left as it was.
2. **The alto voice.** It is `hanami-dark` (formants lowered), which Whisper cannot follow even alone and dry, and in the meeting it is automated 1.5-3 dB *over* the soprano: two voices sing the same words in octaves and the blurred one leads.
3. **The reverb.** Sends of 0.3-0.5 into a 1.15 s reverb fill the gap at the "s" of "Peace" by 10-14 dB (the vowel band dips 19 dB there with the reverb, 29-33 dB without). The room is also larger than the story's parlour.
4. **The door-bar filter removes a consonant.** The 5 kHz low-pass that opens the door takes 8 dB off the "s" of "Peace" (sibilant level against the vowel: -8.3 dB filtered, +0.4 dB open).
5. **In the reprise the word has no beginning.** "Peace" is tied to the preceding "ah" and the four voices start it up to 36 ms apart, so there is no silence before the "p" and no single plosive. Only the rest and the aligned voices together brought the word back.
6. **The "meow" (an inference from 2-5, not a measurement):** with "p" and "s" gone, what is left of "Peace on the" is the vowel glide "ee-ah" and then an octave fall (D5 to D4), which is the shape of a meow.
7. **The long EQ chain did not help.** Each voice carries eight bands, including +11 dB shelves at 4.7 and 13 kHz added to bring the mix up to the borrowed master curve. The three-band chain above read the same (7 of 8 in the meeting, dry, with the alto fixed; 7 of 8 in the reprise with the rest, the alto fixed and sends of 0.15), with the sibilants about 10 dB lower against the vowels.

Fixes in order: alto on `hanami` and under the soprano; a rest before "Peace" and `push_ms` 0 on the quote; no low-pass on the voices in the door bar (filter the organ only); sends of about 0.12 into `size` 0.3; the short EQ chain.

## Catalogue measurements (AcousticBrainz, 2026-11-24)
Track lengths from MusicBrainz; tempo, key and ReplayGain from AcousticBrainz (Essentia 2.1-beta2 low-level data, submitted by users for any edition of each recording). ReplayGain was converted to loudness with **LUFS ≈ -23.7 - RG**, fitted on Spectre's own eleven masters (Essentia ReplayGain against pyloudnorm, spread ±0.7 dB on those; choral spectra may shift it by another dB or two). Tempo estimates on unaccompanied choirs are unreliable (rubato, no drums, octave errors). Reproduce the table with `python3 tools/catalogue_stats.py albums caroling` (album list in `data/catalogue_references.json`) and the calibration with `python3 tools/catalogue_stats.py calibrate` (needs `pip install essentia`).

| album (MusicBrainz release) | tracks | median length (middle half) | est. LUFS median (range) |
|---|---|---|---|
| Ray Conniff Singers, *Here We Come A-Caroling* (1965; CD 2004, [e42549b1](https://musicbrainz.org/release/e42549b1-d584-32f5-9c05-371da9bc15b0)) | 12 | 2:25 (2:11-2:48) | -19.4 (-20.6 to -15.6) |
| Pentatonix, *That's Christmas to Me* (2014, [d4a03a1d](https://musicbrainz.org/release/d4a03a1d-3d19-4868-acfe-5c3c890393b3)) | 11 | 3:05 (2:42-3:23) | -12.4 (-18.9 to -9.5) |
| Straight No Chaser, *Holiday Spirits* (2008, [ff026852](https://musicbrainz.org/release/ff026852-5125-4a27-8f8e-8ad2e4beec90)) | 14 | 3:13 (2:30-3:36) | -13.6 (-15.4 to -11.9) |
| Chanticleer, *A Chanticleer Christmas* (2010, [5f65ba72](https://musicbrainz.org/release/5f65ba72-196c-46b0-85fa-c7a12a45bbc5)) | 15 | 2:39 (2:22-4:32) | -20.1 (-24.0 to -18.7) |
| King's College Choir, *Christmas Carols from King's College* (1986, [690d994c](https://musicbrainz.org/release/690d994c-6f78-4e2c-ac76-28ff831564c6)) | 22 (15 with data) | 3:10 (2:32-3:42) | -22.8 (-29.2 to -12.8) |

Carols on the caroling album (Conniff), length / tempo estimate / key estimate / est. LUFS: "Here We Come A-Caroling" 2:28 / 100 / -20.2; "Silent Night" 2:48 / 148 (eighths: dotted quarter about 49) / F / -20.6; "God Rest Ye Merry, Gentlemen" 2:43 / 148 / -17.9; "Away in a Manger" 2:13 / 112 / A / -19.2; "Joy to the World" 2:14 / 86 / A-flat / -19.2; "It Came Upon the Midnight Clear" 2:46 / 130 / A-flat / -20.4; "O Little Town of Bethlehem" 2:48 / 122 / G / -19.2. Robert Shaw Chorale and Mormon Tabernacle Choir albums were looked up too but have (almost) no AcousticBrainz data.

## Layering and EQ carving (researched 2026-11-25)
The cross-genre method is in [PRODUCTION.md](PRODUCTION.md). Labels: **[M]** measured, **[S]** a named source, **[P]** carried over from a professional trance producer's EQ map (2026) where it applies, **[H]** hand-tuned.

**A choir is already a stack.** Several voices on each part are the unison layers; the parts are the registers; bells and organ are the doublings above and below. The mixing sources for acoustic ensembles are plain that this blend must not be carved apart: slot-by-slot EQ "breaks up the natural blend of sections", EQ should be "gentle and broad", and mud is usually balance or voicing (Thinkspace) [S]. A choir is recorded as one group at a distance and compressed, if at all, as a group ("Mixing and recording practice" above) [S].

**Layer roles:**
| Part | Layers and their jobs | Label |
|---|---|---|
| **The tune (sopranos)** | 2-4 voices in unison, slightly apart in time and pitch (the group), one of them nearer; at the last verse a descant above | [S] this brief; "Mixing the voice" |
| **Inner parts (alto; tenor on an instrument)** | fill the 250 Hz-1 kHz body under the tune; kept softer than the tune | [S] this brief |
| **Bass** | organ pedal (the "only real bass"), or cello | [S] this brief |
| **Bells** | double the tune at the octave or ring the harmony: fundamental plus a strong third harmonic; they are the "air" and the transient of the choir | [S] Rossing et al., this brief |
| **Brass, organ manuals, strings** | sustain the harmony in the middle; one of them at a time is enough | [H] |

**EQ map** (starting ranges; gentle, broad moves of 1-3 dB):
| Instrument | High-pass | Cut / control | Emphasise | Source |
|---|---|---|---|---|
| Choir, upper voices (svs voices: follow "Mixing the voice") | 100-250 Hz by voice | 200-400 Hz on the group if the organ is under it; nasal 500 Hz-1.2 kHz; 5-8 kHz harshness and sibilance | 2-5 kHz for words; air from 10 kHz for the *group* only (a shelf that suits five voices is hiss on one: docs/LESSONS.md, 012) | iZotope EQ cheat sheet (vocals); [P]; [M] this repo |
| Handbells, glockenspiel | 300-500 Hz [H] | harsh partials at 3-5 kHz | the fundamental and third harmonic; 8-12 kHz shimmer | [P] air layer; Rossing |
| Brass (chorale) | 150 Hz | 500-800 Hz boxiness; 1-5 kHz harshness | 5 kHz up only if it must speak | iZotope (brass) |
| Organ manuals | 100-150 Hz [H] | 200-500 Hz under the choir | reeds at 1-3 kHz to fill a presence gap (LESSONS, 012) | [P] pads; [M] this repo |
| Organ pedal, cello bass | 30-40 Hz | 200-400 Hz | 60-200 Hz body | iZotope (piano low end, strings) |
| Piano | 60 Hz | 200-500 Hz mud | 60-200 Hz body; 2-5 kHz only if masked | iZotope |
| Sleigh bells | 1-2 kHz [H] | 5-8 kHz | 8-12 kHz, quiet | [P] hats |
| Reverb return (the church or the street) | 200-500 Hz | 300-600 Hz | low-pass at 6-12 kHz | [P]; Houghton, Sound On Sound 2022 |

**Glue** [S]: one space for everything (a street's short reflections or a church's long tail, chosen per moment: this brief); the vocal group compressed together, about 6 dB on peaks in the Sound On Sound live recording; nothing on single voices that the others don't get.

**Where Spectre stands** [M] (session 012's project): eleven `singer` tracks as the choir, three organ tracks (door, manuals, pedal), strings as cello, piano, three bell tracks: the richest stack of any Spectre track, built from voices. Its known weak point is the low end against the borrowed curve (next section), not layering. No stem analysis was run on 012 for this brief.

**How to build it in Spectre** (engine since 2026-11-25; docs/MANUAL.md "Production"). Set `"genre": "caroling"`: light presets (-1.5 dB cuts, no boosts).
- *A section as a stack*: one choir part as several `singer` layers on the same notes, each its own voice, `seed` and a few ms apart: `{"layers": [{"name": "a", "inst": {"type": "singer", "voice": "hanami", "seed": 1, "svs_vibrato": 0.4}, "role": "choir"}, {"name": "b", "inst": {"type": "singer", "voice": "hanami-soft", "seed": 2, "svs_vibrato": 0.4}, "role": "choir", "offset_ms": 14, "pan": -0.4, "gain_db": -2}, {"name": "c", "inst": {"type": "singer", "voice": "leona-soft", "seed": 3, "svs_vibrato": 0.4}, "role": "choir", "offset_ms": -9, "pan": 0.4, "gain_db": -3}], "fx": [{"type": "comp", "threshold_db": -24, "ratio": 2}]}` (each layer sings its own take: render time grows with the layers).
- *Bells over the choir*: a `bell` (`"clean": true`) or `glockenspiel` layer an octave up on the tune's stack, `vel` 0.5-0.7: the choir's transient and air.
- *Spaces*: one church `hall` return (`mix.returns`, `predelay_ms` 20-30, `hpf` 250, `lpf` 7000); organ pedal and cello on a `low` bus.

## Era assessment of the master target (2026-11-25)
**What the current target is.** `caroling` reuses the `rock` curve (Pestana et al. 2013, pop and rock number-one singles 1950-2010) at `eq` 0.5 and -14 LUFS; this brief already notes that "a choir-and-bells arrangement without low instruments will show low-end boosts at the EQ limit, which is the borrowed curve, not a mix fault".

**Measured** [M] (method, validation and limits in docs/TRANCE.md, section C; AcousticBrainz Bark-band data, medians, dB relative to each track's level at 510 Hz-2 kHz). Two yardsticks: the MusicBrainz tags `christmas`, `carol`, `choral` (1,195 tracks 1995-2021: cathedral choirs and pop Christmas mixed), and the **five albums of "Catalogue measurements" above** (Ray Conniff Singers, Pentatonix, Straight No Chaser, Chanticleer, King's College; 67 tracks).
| Band (Hz, as analysed) | tags, 2015-21 | the five albums (middle-half width) | `rock` curve | 012 The Note She Kept |
|---|---|---|---|---|
| 32-97 | -0.9 | +1.4 (18 dB) | +6.2 | +3.6 |
| 97-140 | +0.2 | -0.1 (15 dB) | **+9.1** | **+9.7** |
| 140-183 | -1.0 | -3.1 (9 dB) | **+8.2** | **+7.6** |
| 183-291 | +2.8 | +3.9 | +9.2 | +8.9 |
| 510-630 | +3.4 | +6.1 | +2.4 | +3.6 |
| 3700-4400 | -12.6 | -13.3 | -4.9 | -3.7 |
| 5300-6400 | -17.7 | -17.4 (12 dB) | -7.3 | -11.4 |
| 7700-9500 | -20.3 | -16.7 (15 dB) | -9.8 | -14.1 |
| 9500-12000 | -23.2 | -19.5 (17 dB) | -12.3 | -18.8 |
| 12000-15500 | -27.5 | -28.4 (18 dB) | -16.6 | -22.7 |

- **The curve against carol records:** `rock` asks for 9-11 dB more at 97-183 Hz, 5 dB more at 32-97 and 183-291 Hz, and 7-12 dB more from 3.7 kHz up than the five albums have at their median. A choir's energy sits at 300 Hz-1.5 kHz; it has neither a rock band's low mids nor its cymbals.
- **012 The Note She Kept** was pulled toward that curve: about 10 dB more at 97-183 Hz than the reference albums (the organ pedal and cello in the mix; the master's EQ also sat at its boost limit at 31.5-63 Hz), 5-10 dB more at 3.7-7.7 kHz. Estimated loudness of the albums: median -19.1 LUFS (middle half -20.6 to -13.6); 012 was mastered to the genre setting, -14.
- **The spread is the second finding:** between these albums the low end differs by 15-18 dB and the top by 12-18 dB (an a cappella pop group, a 1965 studio chorus and a chapel choir share little but the repertoire). No single curve describes "caroling". A tonal target can only be a loose guard here.
- **A current target.** *Interim* [M, fitted to the five albums as in TRANCE.md C; residual up to 1.8 dB; adopted 2026-11-25 as `caroling_ref`, below]: 31.5 Hz -20.5, 40 -16.5, 50 -11.5, 63 -7, 80 -4, 100 -2.5, 125 -4, 160 -4.5, 200 -3.5, 250 0, 315 +1, 400 +2.5, 500 +3.5, 630 +4, 800 +2.5, 1k 0, 1.25k -2, 1.6k -3, 2k -5.5, 2.5k -7, 3.15k -9.5, 4k -12, 5k -15.5, 6.3k -19, 8k -17, 10k -20, 12.5k -27.5, 16k -34.5 (dB re 1 kHz). Recommended use [H]: `eq` 0.2-0.3, no low-end boosts at all (clean-up and a ceiling only), and the loudness decision revisited (-16 to -18 LUFS would sit inside the references). *Definitive:* the owner names the carol sound meant (street carolers and bells, or a chapel choir) and 20-30 such recordings are measured locally (PRODUCTION.md "Era-appropriate targets").
- **Adopted (2026-11-25): `caroling_ref`**, the default target of `--genre caroling` (the five albums, 67 tracks), with the recommended use: `eq` 0.3 and no low-end boosts (`max_low_boost_db` 0). Against the borrowed `rock` curve -8 to -11 dB at 100-200 Hz, +2.5 dB at 500-630 Hz, -4 to -12 dB from 2 kHz up. The loudness (-14 LUFS) is unchanged: whether to move toward the albums' -19 is the owner's decision. It is the same measurement refit by `tools/refcurve.py` (which reproduces the medians above within 0.4 dB; curve, n, spread and validation in docs/MASTERING.md "Era targets", provenance in engine/genres.json); the released tracks keep their masters until the owner approves a remaster (`master --published` reproduces their settings).

Sources for these two sections: iZotope, EQ cheat sheet: https://izotope.com/en/learn/eq-cheat-sheet ; M. Houghton, How to achieve better separation in your mixes, Sound On Sound (2022): https://www.soundonsound.com/techniques/how-achieve-better-separation-your-mixes ; M. Senior, Q. What should I EQ to improve my muddy mixes?, Sound On Sound (2008): https://www.soundonsound.com/sound-advice/q-what-should-eq-improve-my-muddy-mixes ; a professional trance producer's EQ map (2026; docs/TRANCE.md); MusicBrainz search API and AcousticBrainz low-level data (CC0; https://acousticbrainz.org/), measured 2026-11-25; everything else in docs/PRODUCTION.md "Sources". Also: Thinkspace Education, Great mixing advice can ruin your orchestral mix: https://thinkspace.ac.uk/blog/great-mixing-advice-can-ruin-your-orchestral-mix/

## Granularity: strands, eras and the current carol (researched 2026-11-25)
Item 10 of docs/PRODUCTION.md section 5. Labels: **[M]** measured here, **[S]** a named source, **[H]** hand-tuned. Catalogue numbers are AcousticBrainz (Essentia 2.1-beta2) data for MusicBrainz releases, measured 2026-11-25 with `tools/refcurve.py catalogue` and a per-album script (method under "How the strands were measured"); like every catalogue number in this repo they end in 2022 and come from users' files of any edition (CD reissues of the mid-century records).

**What a brief names.** A caroling brief names its **strand** (below) and, if it wants one, its **era**. A brief that names neither takes the **current practice** (the checklist at the end of this section) and the default `--genre caroling` master. Spectre makes instrumentals: in every strand the carolers are a choir texture, never a lead singing verses.

### The dimensions, and why each boundary is there
1. **Strand (tradition and setting): the dimension that changes the sound most.** Six strands, split where the ensemble, the room and the master change together, and the catalogue shows it: between the choir records and the a cappella records the tonal balance differs by up to 25 dB at 63-80 Hz and 16-20 dB at 6.3-10 kHz, the loudness by 9-10 dB and the dynamics (Essentia dynamic complexity) by a factor of two ("Mastering by strand" below) [M]. The strands:
   - **A. Street and door carolers** (Dickens quartets, neighbourhood caroling, Beacon Hill's handbells): a quartet to a dozen singers, SATB, unaccompanied or with handbells, outdoors. Its boundary is the setting (outdoors, walking, no microphones): it has almost no commercial recordings, so it has no measured master and borrows from A's nearest recorded neighbours (choir for the voicing, the default for the master) [S, see table].
   - **B. Choir carols** (the English cathedral and collegiate tradition of King's College and St John's, and the American concert choir: Robert Shaw, Chanticleer, the Tabernacle Choir): 12-360 voices, organ or orchestra, a long room, a classical master. **The UK and US halves measured the same** (within 3.5 dB in every band, about 1 dB typical; loudness -22.5 against -21.6 LUFS, dynamics 8.3 against 7.7) [M], so region is an influence on repertoire and arrangement here, not a separate sound: one strand, one target.
   - **C. Choral pop and the crooner standards** (Tin Pan Alley and mid-century: Bing Crosby, Nat King Cole, Andy Williams, Perry Como; the studio choruses of Ray Conniff, Harry Simeone, Mitch Miller, Norman Luboff): a soloist or a studio chorus of about 25 with orchestra, celesta and bells; mono or early stereo. It separates from B by its studio sound and loudness (reissues at -14 to -18.5 LUFS, half B's dynamics) and from D by its dark top [M].
   - **D. The a cappella school** (collegiate a cappella, Take 6, Straight No Chaser, Pentatonix, Home Free): five to sixteen close-miked voices, vocal bass (often with a digital octave below) and vocal percussion, a pop master. The brightest and loudest strand and the only one with a pop low end [M].
   - **E. Handbell choirs**: 8-15 ringers on two to five octaves, or 32 in the Tabernacle concerts; the instrument of strand A's Beacon Hill and of American churches. Measured data are too thin for a target (below).
   - **F. Brass carols**: the Salvation Army band or quartet at the kettle, the Moravian trombone choir, the brass quintet (Canadian Brass, Empire Brass) and the English brass ensemble (Philip Jones). A classical master, darker and leaner than B's choir at the bottom, a little less dynamic [M].
2. **Timeline: four periods**, split where a recording or arranging practice arrived, not on decades [S]:
   - **Mid-century records, about 1945-1966** (the first and last releases of the mid-century sets in MusicBrainz: Crosby's *Merry Christmas* 1945, Simeone's *Little Drummer Boy* album 1966). From the crooners' albums to the studio choruses: Conniff's Singers (1959: 12 women and 13 men, the women written where a big band's trumpets would be and the men on the saxophone lines, "wordless vocals that backed the melody" at first: [Space Age Pop](https://www.spaceagepop.com/conniff.htm)); *Carols for Choirs* (OUP, 1961: Willcocks's descants "have become standard", over a million copies: [Wikipedia, Carols for Choirs](https://en.wikipedia.org/wiki/Carols_for_Choirs)). Mono mixes on the early-1960s classics ("Jingle Bell Rock", the Ronettes' "Sleigh Ride"), hard-panned early stereo on Brenda Lee's ([iZotope 2025](https://www.izotope.com/community/blog/holiday-songs-lufs-2025)).
   - **The CD era, about 1980-2005.** The choir and brass catalogues of this repo are mostly from here: King's and St John's carol CDs (1986-1997), Rutter's Cambridge Singers (1993-1997), Canadian Brass Christmas albums (1985-2007), Take 6's *He Is Christmas* (1991), the Contemporary A Cappella Society (1991; [Wikipedia, Collegiate a cappella](https://en.wikipedia.org/wiki/Collegiate_a_cappella)). Masters of this period in the classical strands are quiet and dynamic (B -21 to -23, F -18 LUFS) [M].
   - **The a cappella and streaming era, 2008-2021.** Straight No Chaser's *Holiday Spirits* (2008), Pentatonix's four Christmas albums (2014-2021); the holiday canon becomes a yearly streaming playlist dominated by old recordings: "All I Want for Christmas Is You" (1994) is the most-streamed holiday song in almost every country Spotify surveyed, the 1950s and 1960s are represented by "Jingle Bell Rock" and "Rockin' Around the Christmas Tree" ([Spotify, via CBS News](https://www.cbsnews.com/news/mariah-carey-spotify-reveals-most-streamed-holiday-songs); [Just Jared on Spotify's 2024 decade list](https://www.justjared.com/2024/12/22/the-most-popular-holiday-songs-by-decade-spotify-reveals-streaming-data/)). Reissues of the mid-century records are mastered up for this: Nat King Cole's "The Christmas Song" measures -23.3 LUFS in its original transfer and -14.1 in the 1999 remaster (iZotope 2025). Inside this period the a cappella masters got louder: Take 6 1991 -14.6 LUFS, Straight No Chaser and Pentatonix 2016-2018 -9 to -10, with unchanged dynamics; the choir masters did not (per-album table below) [M].
   - **Current practice, 2022-2026** (the checklist at the end): no catalogue data (AcousticBrainz ends in 2022); sources only.
3. **Region: an influence, not a split.** The English cathedral tradition reached American choirs through *Carols for Choirs* and the King's broadcast (BBC every year since 1931: [King's College](https://www.kings.cam.ac.uk/history-festival-nine-lessons-and-carols)); the US added its own strands (the a cappella scene, about 1,200 US collegiate groups: Wikipedia, Collegiate a cappella; the handbell choir; the Salvation Army kettle quartet; the Moravian trombone choir; the Dickens caroler) [S]. Where measured, UK and US choirs sound the same (strand B) [M]; the British brass band (cornets, tenor horns, euphoniums, as at the Salvation Army) and the American brass quintet (two trumpets, horn, trombone, tuba) differ in instruments, not measurably in master (both in F; thin data).

### The shared core (holds in every strand and era)
| element | the core | source |
|---|---|---|
| repertoire | the public-domain carols (above) and the Christmas standards; the tune is known and must be recognisable | this brief; [S] the catalogues' track lists |
| harmony | diatonic major, I-IV-V with secondary dominants at cadences, voices in close position with the tune on top | "Harmony, rhythm, form" above |
| form | strophic, two to four verses, variation by texture between verses, a held or slowed final cadence | the carol books above |
| meter | 3/4, 6/8 or 4/4, no backbeat in A, B, E, F; D and C may swing or add a beat (vocal percussion, a rhythm section) | [S] the strands below |
| voices | the carol is sung, or played as if sung: phrases end with breaths | this brief |
| length | 2:00-4:00 per carol (strand medians 2:25-3:37, below) | [M] |
| no sub | nothing below about 40 Hz in any strand; the lowest instrument is a vocal bass, an organ pedal, a tuba or an upright bass | [M] the curves below |
| loudness | quieter than the pop of its year: the Holiday 100 averages -12.9 LUFS against -8.3 for 2025 releases (iZotope 2025); every caroling strand measured is at or under -12.5 | [S], [M] |

### Each strand's elements (checkable; "shared" or "varies")
| element | A street / door | B choir (cathedral, concert) | C choral pop, crooner | D a cappella | E handbells | F brass |
|---|---|---|---|---|---|---|
| ensemble size | 4 (SATB, two men two women) to about 12; troupes of 20-50 split into quartets ([KCUR](https://www.kcur.org/post/dickens-carolers-reveal-what-it-takes-keep-bringing-holiday-cheer-busy-kansas-citians); [Milwaukee Magazine](https://www.milwaukeemag.com/meet-wisconsins-traveling-troupe-of-dickens-carolers/)) | King's: 16 boy choristers, 14 choral scholars (ATB) ([King's College](https://www.kings.cam.ac.uk/choir/about-choir)); Chanticleer 12 men; the Tabernacle Choir 360 voices, 150-200 players and 32 handbell ringers ([Church News](https://thechurchnews.com/living-faith/2026/11/02/tabernacle-choir-orchestra-2026-christmas-concert-ticket-registration/)) | a crooner and orchestra; Conniff's 25 singers (Space Age Pop) | 5 (Pentatonix: bass, baritone, countertenor, soprano, beatboxer) ([Sound On Sound](https://www.soundonsound.com/techniques/inside-track-pentatonix)); collegiate groups 8-16 (Wikipedia) | 8 ringers for two octaves, 11 for three, 15 for four ([UMC Discipleship](https://umcdiscipleship.org/resources/all-about-handbells)) | 4 (the first Salvation Army band was a brass quartet: [Wikipedia](https://en.wikipedia.org/wiki/Salvation_Army_brass_band)); quintet 5; brass band about 25 | **varies** (4 to 360) |
| voicing | SATB, tune in soprano | SATB or SATB divisi, trebles on top (King's), a descant over the last verse | unison or block harmony, wordless "oo" and "ah" pads behind a soloist (C) | close harmony in 5-6 parts, lead plus backing, vocal bass, vocal percussion | bells in chords and melody, ringing on (LV) | four-part chorale | **varies** |
| last-verse devices | a key lift rare; a held last chord | **descant and reharmonised last verse** (Willcocks; *Carols for Choirs*), organ full | modulation up a step (Dalla Riva: a quarter of No. 1 hits 1958-1990 had a key change, almost none after 1990: [NPR 2022](https://www.npr.org/2022/11/30/1139707179/where-did-all-the-key-changes-go)) | key lifts and big final chords (Pentatonix; no measured count) | a peal; martellato accents | a descant on a trumpet or cornet | **varies** |
| instruments | voices, handbells, sometimes a lantern-and-songbook look only | organ; orchestra (Rutter, the Tabernacle Choir); handbells | orchestra, celesta, glockenspiel, sleigh bells, harp | none (strand's identity); since 2025 Pentatonix adds brass, woodwinds, strings and harp (below) | handbells, handchimes; techniques LV, martellato, shake, thumb damp, mallets ([Handbell Musicians of America notation guide](https://handbellmusicians.org/wp-content/uploads/2022/11/NotationGuide.pdf)) | trumpets or cornets, horn or tenor horns, trombones, euphonium, tuba | **varies** |
| low end (measured) | not measured | **none below 100 Hz**: -17 to -25 dB re 1 kHz at 50-100 Hz | lean: -4.5 to -15 at 50-100 Hz (crooner); Bublé's 2011 retro album full (+2.5 to +3.5 at 63-100) | **full**: +3 to +3.5 at 80-100 Hz (vocal bass, "a digital lower octave": Wikipedia, Collegiate a cappella) | not usable (thin) | very lean: -12.5 to -25.5 at 50-100 Hz | **varies, up to 28 dB** |
| top end (measured, 6.3-10 kHz re 1 kHz) | not measured | darkest: -26.5 to -30 | dark: -14.5 to -23 | brightest: -10 to -11 | not usable | dark: -26 to -29.5 | **varies, up to 20 dB** |
| room | dry and close, short reflections, snow absorbs (this brief: Acentech) | long: a chapel or hall, the choir recorded at a distance (this brief: Sound On Sound) | a studio with echo chamber; the iZotope article praises the Ronettes' depth | dry close voices; church-preset reverb on the backing only, delays on the lead (Sound On Sound, Pentatonix) | a church; bells ring on | outdoors (kettle) or a church (Canadian Brass with the St Patrick's Cathedral organ, 1981) | **varies** |
| tempo and feel | walking pace, free; rubato | rubato, a ritardando, slow carols slower | swing or a light two-beat on the secular songs | a groove from vocal percussion on the secular songs, rubato on the carols | rubato; LV smears the beat | march or chorale | **varies** |
| length (median) | "two or three minutes" (Milwaukee Magazine) | 3:12 UK, 3:15 US [M] | 2:25 (1965 Conniff) to 2:49 crooners, 3:37 Bublé [M] | 3:01 [M] | 4:00 (Raleigh Ringers, not Christmas; thin) | 3:04 [M] | **varies** (2:25-3:40) |
| tuning | uneven, a group | pure intervals, straight tone, narrow vibrato (Ternström, above) | equal tempered with the orchestra | every voice tuned (Melodyne) before the mix (Sound On Sound) | fixed (the bells) | equal tempered | **varies** |

### Mastering by strand (measured 2026-11-25)
AcousticBrainz has no true peak, LRA or stereo data. Loudness is estimated from ReplayGain (LUFS ≈ -23.7 - RG, ±1-2 dB; "Catalogue measurements" above). **Dynamics are Essentia's dynamic complexity** (the mean deviation of the loudness from its average, in dB; higher = more dynamic), a relative index: on Spectre's 15 published masters it correlates only loosely with LRA (r 0.44; slope about 1.4 LU per unit), and those masters span 2.9-5.4. 012 *The Note She Kept* measures **2.9** (-14.0 LUFS, LRA 5.2 LU, PLR 12.9 dB, pyloudnorm) [M, 2026-11-25].

| strand (set) | albums, years, tracks with data | est. LUFS median (middle half) | dynamic complexity | 32-140 Hz | 6.4-15.5 kHz | length |
|---|---|---|---|---|---|---|
| B choir, UK (King's, St John's, Cambridge Singers, Tenebrae, VOCES8, Tallis Scholars) | 13, 1986-2012, 43 | **-22.5** (-24.5 to -19.8) | **8.3** (6.6-10.1) | -13.9 | -29.2 | 3:12 |
| B choir, US (Chanticleer, Robert Shaw Chorale, Tabernacle Choir) | 10, 1987-2010, 63 | **-21.6** (-23.9 to -19.7) | **7.7** (6.4-8.7) | -10.8 | -27.5 | 3:15 |
| F brass (Canadian Brass ×6, Empire Brass, Philip Jones) | 8, 1982-2013, 44 | **-18.1** (-20.8 to -16.2) | 5.6 (4.7-6.6) | -8.1 | -28.0 | 3:04 |
| C mid-century choral pop (Conniff, Mitch Miller, Robert Shaw; reissues) | 11 listed, 20 tracks with data (thin) | -18.5 (-19.6 to -14.2) | 3.3 (3.1-4.2) | +1.9 | -19.5 | 2:25 |
| C crooner standards (Crosby, Cole, Williams, Como; CD reissues 1986-2019) | 7, 55 | **-14.1** (-16.1 to -12.5) | 4.8 (4.3-5.4) | -0.2 | -19.5 | 2:49 |
| C current retro (Michael Bublé, *Christmas*, 2011) | 1 album, 15 | -9.9 (-10.9 to -9.1) | 4.6 (4.0-5.2) | +7.4 | -14.2 | 3:37 |
| D a cappella (Pentatonix 2014-2018, Straight No Chaser 2008-2016, Take 6 1991; Home Free 2010 has no data) | 8, 87 | **-12.5** (-14.4 to -10.2) | **4.0** (3.4-5.1) | +7.9 | **-10.6** | 3:01 |
| E handbells (Raleigh Ringers, Sonos) | 18 tracks, mostly not Christmas, no lossless file | -28.7 (?) | 7.2 | -2.7 | -15.4 | 4:00 |
| the five albums (`caroling_ref`) | 5, 1965-2014, 67 | -19.1 (-20.6 to -13.6) | | | | |
| Billboard Holiday 100, 10 songs (iZotope 2025) | 1957-2014 | average -12.9 (-8.8 to -23.3); LRA 7.0 (3.5-13.5); true peaks -7.8 to +1.3 dBTP | | | | |

("32-140 Hz" and "6.4-15.5 kHz": the medians of the tracks' mean Bark-band levels in those ranges, dB re 510 Hz-2 kHz.)

**Per-album loudness and dynamics** (est. LUFS / dynamic complexity / tracks with data): B UK: King's College 1986 -22.6 / 7.0 / 14, 1997 -21.7 / 6.9 / 12, *Noël* 1995 -21.6 / 7.3 / 7; VOCES8 2012 -23.8 / 10.6 / 18. B US: Chanticleer 1995 -23.0 / 6.6 / 17, 2001 -21.4 / 8.0 / 18, 2010 -20.1 / 8.1 / 15; Robert Shaw Chorale 1987 -23.7 / 8.4 / 10. C: Crosby *Merry Christmas* (1995 CD) -15.3 / 4.7 / 10, (2019 digital) -13.8 / 4.6 / 9; Cole *The Christmas Song* (1986 CD) -14.0 / 5.3 / 11, (1999) -13.9 / 5.2 / 14; Andy Williams (2004 CD) -15.6 / 4.2 / 11; Como (2001) -13.4 / 5.0 / 18; Conniff (2004 CD of the 1965 album) -19.4 / 3.2 / 12; Mitch Miller (1999 digital) -14.1 / 3.3 / 7; Bublé 2011 -9.9 / 4.6 / 15. D: Take 6 1991 -14.6 / 4.7 / 10; Straight No Chaser 2008 -13.6 / 4.5 / 14, 2009 -12.9 / 4.0 / 15, 2016 **-9.1** / 4.2 / 15; Pentatonix 2014 -12.4 / 4.0 / 11, 2016 -18.5 / 3.3 / 11 (an outlier: the users' files of this album are quiet; its dynamics are not), 2018 **-10.0** / 3.2 / 11. F: Canadian Brass 1994 -20.8 / 5.9 / 18, 1997 -16.2 / 5.1 / 20 (the other brass albums have 1-3 tracks with data). **What it shows over time:** the choir records do not get louder (King's 1986 -22.6, VOCES8 2012 -23.8); the a cappella records do, by about 4 dB in 25 years (Take 6 1991 -14.6, both groups' 2016-2018 albums -9 to -10) with the same dynamics. Albums with no AcousticBrainz data: Simeone, Luboff, Shaw 1950s, the Tabernacle Choir, St John's, Tenebrae, Home Free, Philip Jones.

**Tonal curves** (dB re 1 kHz, `tools/refcurve.py` fits; the existing `caroling_ref` for comparison):
| Hz | `caroling_ref` | choir UK | choir US | **`caroling_choir`** (UK + US) | **`caroling_acappella`** | crooner | brass | mid-century (thin) |
|---|---|---|---|---|---|---|---|---|
| 31.5 | -18.5 | -23 | -22.5 | **-22.5** (19.9) | **-14** (9.9) | -28 | -32.5 | -20.5 |
| 40 | -14 | -24 | -24 | **-24** (12.4) | **-8.5** (7.4) | -21 | -29 | -15 |
| 50 | -9.5 | -24.5 | -25 | **-25** (12.4) | **-3.5** (7.4) | -15 | -25.5 | -10 |
| 63 | -6.5 | -23.5 | -24.5 | **-24.5** (12.4) | **+0.5** (7.4) | -9.5 | -22 | -5.5 |
| 80 | -4.5 | -21 | -22.5 | **-22** (12.4) | **+3** (7.4) | -6.5 | -17.5 | -3 |
| 100 | -4 | -17 | -18.5 | **-17.5** (8.2) | **+3.5** (4.1) | -4.5 | -12.5 | -2 |
| 125 | -4.5 | -12.5 | -13.5 | **-13** (8.2) | **+2** (4.1) | -3.5 | -9 | -3 |
| 160 | -5 | -10 | -9.5 | **-9.5** (6.8) | **+0.5** (5) | -1.5 | -7.5 | -3.5 |
| 200 | -3.5 | -8.5 | -6 | **-7** (6.1) | **0** (4.9) | +0.5 | -6.5 | -2 |
| 250 | -1 | -6.5 | -3 | **-4.5** (6.1) | **+0.5** (4.9) | +1 | -4.5 | 0 |
| 315 | 0 | -3.5 | 0 | **-1.5** (5.1) | **+1** (5.1) | +1 | -2 | +1 |
| 400 | +2 | 0 | +2 | **+1.5** (5) | **+1** (4.1) | +2 | -0.5 | +1.5 |
| 500 | +4 | +3.5 | +3.5 | **+4** (5) | **+1.5** (4.1) | +2.5 | +0.5 | +3 |
| 630 | +4 | +4.5 | +3.5 | **+4** (2.9) | **+2** (2.4) | +2 | +0.5 | +3 |
| 800 | +1.5 | +1.5 | +1.5 | **+1.5** (2.7) | **+1.5** (2.1) | +1 | 0 | +1.5 |
| 1000 | 0 | 0 | 0 | **0** (3.5) | **0** (1.5) | 0 | 0 | 0 |
| 1250 | -1.5 | -1 | -3.5 | **-2** (3.3) | **-1.5** (1.9) | -1 | -0.5 | -0.5 |
| 1600 | -4 | -5.5 | -7.5 | **-6.5** (4.1) | **-2.5** (2.1) | -3.5 | -2 | -1.5 |
| 2000 | -6.5 | -9.5 | -10 | **-10** (5) | **-4.5** (4.1) | -5.5 | -5 | -3.5 |
| 2500 | -7 | -10 | -9.5 | **-10** (4.8) | **-6.5** (4.7) | -6 | -8 | -4.5 |
| 3150 | -8.5 | -13.5 | -11 | **-12** (4.9) | **-7.5** (4.2) | -7 | -12.5 | -6 |
| 4000 | -13 | -22 | -19.5 | **-20** (5) | **-10** (6.2) | -9.5 | -17.5 | -10.5 |
| 5000 | -17 | -28 | -26.5 | **-26.5** (3.6) | **-11.5** (5.8) | -12.5 | -22.5 | -14 |
| 6300 | -18 | -28 | -26.5 | **-27** (4.5) | **-11** (3.8) | -14.5 | -26 | -15 |
| 8000 | -18 | -27.5 | -27 | **-27** (4.5) | **-10** (5.1) | -17 | -28 | -16 |
| 10000 | -20.5 | -30 | -30 | **-30** (5.2) | **-10.5** (4.5) | -23 | -29.5 | -19.5 |
| 12500 | -28 | -35.5 | -35 | **-35** (5.8) | **-15** (4.3) | -30.5 | -33 | -26.5 |
| 16000 | -36 | -41.5 | -41 | **-41** (5.9) | **-22.5** (5.3) | -37.5 | -37.5 | -34 |

Fits: choir UK n 43, residual ≤2.5 dB; US n 63, ≤2.7; **`caroling_choir` n 106 (23 albums, 1986-2012, 64% lossless), est. -22.3 LUFS (-24.3 to -19.7), residual ≤2.5 dB (mean 0.62)**; **`caroling_acappella` n 87 (8 albums, 1991-2018, 29% lossless), est. -12.5 LUFS (-14.4 to -10.2), residual ≤1.9 dB (mean 0.39)**; crooner n 55, ≤1.1; brass n 44, ≤5.7 (thin at the bottom); mid-century n 20, ≤6.8 (thin). In brackets: the middle-half width per band (dB) of the two proposed targets. The curve files (with track lists) are `caroling_choir.json` and `caroling_acappella.json` in the proposal folder.

What it says:
1. **Two masters, not one.** The choir (B) and the a cappella (D) records sit at the two ends of every measure: 9-10 dB apart in loudness, about twice as dynamic (8 against 4), 20-25 dB apart at 50-100 Hz and 16-20 dB apart at 6.3-10 kHz. `caroling_ref` was fitted to a mix of both (two a cappella albums, two choirs, Conniff), which is why its spread was 15-18 dB at the low end and on top (Era assessment above): it describes neither.
2. **The choir master is a classical master.** -21.6 to -22.5 LUFS, no low end, the top falling 27-30 dB under 1 kHz by 6-10 kHz: distance and the room supply the top, not air EQ. Classical mastering practice agrees: -16 to -20 LUFS for full ensembles and lower for chamber pieces, "little limiting" or none, volume riding instead of a limiter ([Sage Audio](https://www.sageaudio.com/articles/how-to-master-dynamic-classical-music); [Violet Recording](https://violetrecording.com/how-to-master-classical-music/); [Sound On Sound Q&A](https://www.soundonsound.com/sound-advice/q-how-should-compress-classical-recording); an AES panel's mastering engineer: "around -20 LUFS or even lower", [AES](https://aes2.org/?p=59290)).
3. **The a cappella master is a pop master.** -12.5 LUFS, the dynamics of Spectre's own pop masters, a full 80-100 Hz from the vocal bass and the brightest top of any strand (two de-essers on the lead, Melodyne on every voice before the mix, compression on every part: Sound On Sound's Inside Track on a 2015 Pentatonix session, not a Christmas one; *That's Christmas to Me* was mixed by Ed Boyer and mastered by Bill Hare: [Wikipedia](https://en.wikipedia.org/wiki/That%27s_Christmas_to_Me)).
4. **Brass carols** sit between (-18 LUFS, dynamic complexity 5.6), leaner at the bottom than any strand (-12.5 dB at 100 Hz, -22 at 63 Hz) and as dark on top as the choir. One ensemble dominates the set (Canadian Brass, 6 of 8 albums): no target proposed.
5. **The crooner standards** measure as CD and streaming reissues (-14.1), not as originals (Cole's original transfer -23.3, iZotope). Their curve is within 4.5 dB of `caroling_ref` from 125 Hz to 8 kHz: no separate target needed.
6. **012 was mastered like a pop carol** (dynamic complexity 2.9, with 004 the lowest of Spectre's fifteen masters, and lower than every caroling set) toward a curve that mixed choirs and a cappella. For a choir carol that is the wrong end; for a pop carol it is the right loudness.

**Low end, width and top, by strand** (sources; AcousticBrainz is mono, so width is not measured):
- *B choir:* a spaced pair or ORTF across the choir, outriggers for a large one, the organ on a spot mic (Sound On Sound, above): a natural, wide image; the low end is the organ pedal alone; no de-essing or air boosts in the sources; true peak: classical masters are peak-normalised with "little limiting" (Sage Audio), so their PLR is high (about 18-22 dB if peaks reach -1 dBTP at -20 to -23 LUFS) [H: inferred, not measured].
- *D a cappella:* stacks of doubled backing voices on their own buses, a choir widened with a stereo imager (Waves S1), the bass vocal through a channel strip with multiband compression (Sound On Sound): a wide, dense pop image; the vocal bass and vocal percussion in the centre [H: standard pop practice, no a cappella source].
- *C mid-century:* mono (early 1960s) or hard-panned early stereo (Brenda Lee: backing vocals hard left, band hard right; iZotope 2025); reissues are brighter, louder and wider than the originals and can sound "flat and distorted" (iZotope on Cole's 1999 remaster).
- *Playback:* the Holiday 100 is the streaming-and-radio canon (Billboard); choir carols are released on CD and broadcast (the King's service on BBC radio since 1931) and heard in churches; Pentatonix's 2025 album was also mixed for immersive audio (Josh Bowman: [Wikipedia](https://en.wikipedia.org/wiki/Christmas_in_the_City_(Pentatonix_album))). **On streaming a quiet choir master stays quiet:** Spotify normalises each track of a playlist to -14 LUFS but raises a quiet track only as far as its true peak allows, keeping 1 dB of headroom ("a track at -20 dB LUFS with a -5 dB FS true peak is raised only to -16"; [Spotify](https://support.spotify.com/us/artists/article/loudness-normalization/)); Apple Music's Sound Check aims at about -16 LUFS ([iZotope](https://www.izotope.com/en/learn/mastering-for-streaming-platforms), secondary source). A choir carol at -22 LUFS with peaks at -1 dBTP plays 8 dB under the pop carol before and after it in a holiday playlist.

### Which master each brief uses (merged into the engine 2026-11-26: genres.json `caroling.master_by_strand`)
| brief names | `--target` | `--lufs` | `--tp` | `--eq` | low-end boosts | why |
|---|---|---|---|---|---|---|
| nothing, or "current" | `caroling_ref` (the default, unchanged) | -14 | -1 | 0.3 | none | a mixed curve and a loudness between the strands (Holiday 100 average -12.9, choirs -22), at the level Spotify plays everything; kept because no 2023-2026 measurement says otherwise [H] |
| strand A (street, door) or E (handbells) | `caroling_ref` | -16 [H] | -1 | 0.3 | none | no measured masters for either; the outdoor quartet and the handbell choir are acoustic and unamplified, so the master leans toward the classical strands; -16 is Apple's playback level and leaves the dynamics of an outdoor group |
| strand B (choir, cathedral, church, concert choir) | **`caroling_choir`** (new, measured) | **-18** [H] | -1 | 0.3 | none | measured median -22; classical guidance -16 to -20; -18 keeps the choir dynamic (the limiter barely works) while costing 4 dB, not 8, against pop neighbours in a playlist |
| strand C (crooner, mid-century choral pop) | `caroling_ref` | -14 | -1 | 0.3 | none | the reissues' median -14.1; the curve is within 4.5 dB of the crooner curve; mono for the early-1960s sound is a mix decision (engine gap) |
| strand D (a cappella, pop carol, Pentatonix) | **`caroling_acappella`** (new, measured) | **-12** | -1 | 0.5 | allowed (as other genres) | measured median -12.5, Holiday 100 average -12.9; the curve is tight enough for a firmer `eq` (spread below); the vocal bass is the low end |
| strand F (brass) | `caroling_choir` [H] | -18 | -1 | 0.3 | none | measured -18.1 and as dark as the choirs; the brass set is too one-ensemble for its own curve |
| an era: mid-century | as C | -16 [H] | -1 | 0.3 | none | the mid-century recordings as streamed today span -10.5 to -23.3 LUFS (Andy Williams -10.5, the Ronettes -11.5, Brenda Lee -15.9, Cole's original -23.3: iZotope 2025); the choral-pop reissues measure -18.5 (thin) and the crooner reissues -14.1; -16 is between |

`translate`: 0.2 everywhere, 0.3 for D (a vocal bass leads) [H]. `mono_below` 120 stays.

### Current practice (2023-2026): the checklist
For a brief that asks for a contemporary carol. Sources only: no catalogue data after 2022.
| # | element (newest first) | source | engine |
|---|---|---|---|
| 1 | **Voices first, instruments back**: the leading a cappella group added brass, woodwinds, strings and harp to its 2025 album, aiming at "the old classic Christmas sound — the Nat King Cole, Bing Crosby with the orchestra" and a "big band orchestral sound" | [Wikipedia, Christmas in the City](https://en.wikipedia.org/wiki/Christmas_in_the_City_(Pentatonix_album)); [iHeartRadio](https://ripcityradio.iheart.com/featured/iheartradio-live/content/2025-11-10-pentatonix-opens-up-about-posthumous-frank-sinatra-holiday-song-collab/) | strings (`strings_section`, `cello`, `viola`), `celesta`, `glockenspiel`, `vibraphone` exist; **brass and harp missing** |
| 2 | **Retro orchestral pop** remains the canon's sound: Bublé's 2011 album was reissued in 2021, 2024 and 2025 editions; Kelly Clarkson's "Underneath the Tree" (2013) is the loudest of iZotope's ten Holiday 100 songs (-8.8 LUFS) | MusicBrainz releases; iZotope 2025 | as 1 |
| 3 | **A new carol every year** in the cathedral tradition: King's commissions (Cheryl Frances-Hoad, *The Cradle*, 2023; Bill Ives, *Three Points of Light*, 2024); *Carols for Choirs 6* (2023, Chilcott and Hill) | [Wise Music](https://www.wisemusicclassical.com/news/4668/A-new-carol-for-Kings-by-Cheryl-Frances-Hoad/); [Magdalen College](https://www.magd.ox.ac.uk/news/bill-ives-commissioned-to-write-a-new-carol/); Wikipedia, Carols for Choirs | an original melody in the idiom: the producer writes it (this brief, "Public-domain carols") |
| 4 | **Choir with orchestra and bells** as the big American Christmas concert: 360 voices, 150-200 players, 32 handbell ringers (the Tabernacle Choir, 2022-2026); VOCES8 Foundation Choir and Orchestra, *A Choral Christmas* (2023) | Church News; MusicBrainz | svs choir (female voices plus `hanami-male`; SATB not yet tried), `strings_section`, `bell` `"clean"`; organ weak; brass, handbell missing |
| 5 | **The descant and the last-verse lift** stay the carol's climax device in choirs (Willcocks standard), while pop key changes have nearly vanished since 1990 (NPR 2022) | as above | writing; a key lift is notes in the new key (or a new track with `transpose`) |
| 6 | **Dry, tuned, close voices**: each voice tuned, de-essed twice, the backing voices alone into a church reverb, the lead on a quarter-note and a slap delay; the vocal bass with a digital octave below | Sound On Sound, Pentatonix; Wikipedia, Collegiate a cappella | svs voices, `push_ms` 0, reverb and `delay` sends exist; **no de-esser**; a sub octave under a vocal bass needs a `sine` layer (`notes: "lowest"`); **no vocal percussion** (kit drums are not a mouth) |
| 7 | **Immersive mixes** of holiday albums (Atmos credit on the 2025 album) | Wikipedia | stereo only (not needed for Spectre's releases) |
| 8 | **Quieter than the year's pop**: the holiday canon averages -12.9 LUFS and LRA 7.0 LU against -8.3 and 5.5 for 2025 releases | iZotope 2025 | the master does this (`--lufs`) |

### Engine gaps for the strands (in order of what a listener would hear)
1. **Brass** (strands C, F, current item 1): no brass instrument at all; the brass quartet, trombone choir and big-band brass of a retro arrangement cannot be played (already "missing" in "Engine mapping").
2. **Handbell model** (A, E): `bell` with `ratio` 3 is an FM approximation; real handbells ring LV, are damped, martellato'd and shaken; English handbells tune the twelfth (3 × f0) ([Wikipedia, Handbell](https://en.wikipedia.org/wiki/Handbell); Rossing et al., above). A modal handbell measured like `glockenspiel` (engine/chamber.py) would close it.
3. **Pipe organ** (B): `organ` is additive drawbars (Hammond-like), no chiff, mixtures or reeds.
4. **An SATB svs choir** (A, B, D): `hanami-male` exists for tenor and bass but has not been tried as a choir, and no voice reaches a vocal bass's E2-G2 (`hanami-male` B2-E4).
5. **De-esser** (D, and every worded choir): already flagged in "Mixing the voice".
6. **Vocal percussion** (D): missing.
7. **Harp** (C, current item 1): missing.
8. **A mono master** (C, mid-century): the master has `mono_below` only; a mono mix is possible by panning every track centre.

### How the strands were measured
`tools/refcurve.py catalogue --release <mbid> ...` per strand, under `flock /tmp/spectre-musicbrainz.lock`; a per-album script read the same AcousticBrainz records for ReplayGain, `dynamic_complexity` and the Bark bands (the scripts are not kept; the curve files of the two proposed targets are in the orchestrator's proposal folder). Album lists, by MusicBrainz release: C mid-century: e42549b1, 6f212aa7, fa259608, c700bf20, 964df524, 8ca8d11f, e82b88d8, eba3511a, 5ef1b185, 084d8c1e, 8e7df632; C crooner: 7bf4f9a8, 4711abca, 2910ed7b, 26ee61fd, 1ce6af91, be161b56, 1aebbbf0; C retro: 16fec7a7, a8e3dc79; B UK: 690d994c, 089a1b66, 7431d24f, 601c195e, 8f43912e, 0e532324, c0b3980c, eee830ad, 79086ce7, e0ab6509, 519ef1f3, dd9e24f1, ed65197e; B US: 5f65ba72, 076af14a, 3cde4bc4, 9339f4a7, 2804712e, 27dbdb87, 9d152d00, 05c6a6ba, 836c22c6, 618ee7fb; D: d4a03a1d, f89ac131, 15c12c37, ff026852, 3ee3fad8, 36463ba3, 38900b22, 873bf1ce; F: 4a6f5861, 6f9aa4ae, 5c95c951, 23efafc8, 53351655, 31ffc42a, 38eab328, 4f07c878; E: release 5fa7db65 and the MusicBrainz artists Raleigh Ringers and Sonos Handbell Ensemble (100 recordings each) (first 8 characters of each MBID; the full lists are in the proposal for data/catalogue_references.json).

### What could not be sourced or measured
- **Strand A (street carolers)** has no measured recording: its master settings are hand-tuned [H].
- **Handbells**: the only handbell data are 18 mostly secular tracks without a lossless file (-28.7 LUFS is likely the quiet CD releases of a church ensemble, but unverified): no target.
- **True peak, LRA, PLR and width per strand**: AcousticBrainz has none; dynamic complexity is a loose proxy (r 0.44 with LRA on Spectre's masters). The definitive numbers need 20-30 reference files per strand measured with `refcurve.py measure`.
- **2022-2026**: no catalogue data; current practice is from sources only.
- **The mid-century set** is thin (20 tracks, mostly Mitch Miller and Conniff reissues; fit residual up to 6.8 dB); the crooner set measures reissues.
- **Key lifts in a cappella carols**: no count found.
- **Choir-versus-accompaniment level** (already noted in "Mixing the voice"): still unsourced.

## Public-domain carols (melody AND words published before 1929)
Dates come from the linked references (the Wikipedia list of carols, hymnary.org, the carol books); "to confirm" marks a date not checked in a source during this research. Confirm every date again when a carol is verified.

Rule for every Spectre track: a quoted carol must be public domain as melody and words (published before 1929); later arrangements, harmonizations and translations are not (write your own harmony). **Only the two carols under "Verified melodies" may be quoted as they stand**; any other carol in this list needs the same verification (two independent scores, an engine check, a phrase table) before a session quotes it, or the producer writes an original melody in the idiom.

| carol | words | melody | status |
|---|---|---|---|
| **It Came Upon the Midnight Clear** | Edmund H. Sears, 1849 (Massachusetts) | CAROL, Richard Storrs Willis, 1850 (*Church Chorals and Choir Studies*) | **verified below**; American text and tune ([hymnary.org](https://hymnary.org/tune/carol_willis)) |
| **The First Nowell** | traditional (Gilbert 1823; Sandys 1833) | traditional (Sandys 1833) | **verified below** ([Gresham](https://www.gresham.ac.uk/node/13042); [Wikipedia list](https://en.wikipedia.org/wiki/List_of_Christmas_carols)) |
| Silent Night | Joseph Mohr 1818; English John Freeman Young 1859 | Franz Xaver Gruber 1818, published 1833; the sung version differs "slightly (particularly in the final strain)" from Gruber's | candidate; verify which version ([Wikipedia](https://en.wikipedia.org/wiki/Silent_Night); [hymnary.org](https://hymnary.org/tune/stille_nacht_gruber)) |
| Hark! The Herald Angels Sing | Charles Wesley 1739 (altered by Whitefield, Madan) | Felix Mendelssohn (adapted; dates of the adaptation to confirm) | candidate ([list](https://en.wikipedia.org/wiki/List_of_Christmas_carols)) |
| O Come, All Ye Faithful | J. F. Wade c. 1743; English Frederick Oakeley 1841 | ADESTE FIDELES, Wade c. 1743-51 | candidate |
| Joy to the World | Isaac Watts 1719 | ANTIOCH, adapted by Lowell Mason from Handel (19th century; date to confirm) | candidate ([hymnary.org](https://hymnary.org/tune/antioch_handel)) |
| O Little Town of Bethlehem | Phillips Brooks 1867-68 | ST. LOUIS, Lewis H. Redner 1868 (published by 1894) | candidate; American ([hymnary.org](https://hymnary.org/tune/st_louis_redner)) |
| We Three Kings | John Henry Hopkins (published 1863) | Hopkins | candidate; American |
| Jingle Bells | James Lord Pierpont, "The One Horse Open Sleigh", Boston 1857 | Pierpont 1857; the familiar chorus is a later variant (recorded by 1898, still before 1929) | candidate; secular ([Wikipedia](https://en.wikipedia.org/wiki/Jingle_Bells)) |
| God Rest Ye Merry, Gentlemen | traditional (Sandys 1833; Rimbault 1847) | traditional (minor) | candidate; Hutchins 1916 prints it twice (carols 509, 722) |
| Good King Wenceslas | J. M. Neale 1853 | TEMPUS ADEST FLORIDUM (Piae Cantiones 1582) | candidate; Mutopia has Hutchins's 1916 setting |
| Here We Come A-wassailing | traditional (Yorkshire), Bramley & Stainer 1871 | traditional | candidate; the door-to-door song ("we are not daily beggars that beg from door to door, but we are neighbours' children whom you have seen before"); Hutchins carol 670 |
| Deck the Halls | English words Thomas Oliphant 1862 | Welsh "Nos Galan" (traditional; date to confirm) | candidate |
| What Child Is This? | William Chatterton Dix 1865 | "Greensleeves" (16th century) | candidate |
| Angels We Have Heard on High | French 1842; English James Chadwick 1862 | "Les Anges dans nos campagnes" (1842 publication) | candidate; **not** Edward Shippen Barnes's later arrangement ([Wikipedia](https://en.wikipedia.org/wiki/Angels_We_Have_Heard_on_High)) |
| Go Tell It on the Mountain | African American spiritual, published 1901-1909 (Work; Fenner 1909) | spiritual | candidate ([Wikipedia](https://en.wikipedia.org/wiki/Go_Tell_It_on_the_Mountain_(song))) |
| Up on the Housetop | Benjamin Hanby (1860s; date to confirm) | Hanby | candidate |
| **Not usable as sung** | | | "We Wish You a Merry Christmas": the familiar West Country tune was unknown before Arthur Warrell's 1935 arrangement (Oxford University Press) ([Wikipedia](https://en.wikipedia.org/wiki/We_Wish_You_a_Merry_Christmas)); "Carol of the Bells": Wilhousky's English words (1936) are copyrighted, Leontovych's melody (before 1916, published in Ukraine) is older ([Wikipedia](https://en.wikipedia.org/wiki/Carol_of_the_Bells)); everything from the 1930s on (Rudolph, White Christmas, Winter Wonderland, Let It Snow, The Little Drummer Boy, ...) |

## Verified melodies
Both melodies were read from two independent public-domain scores, compared note by note with a third machine-readable source, and played back by the engine and pitch-tracked. They are in `examples/caroling/check/melodies.py` (the strings below), with a piano check render `examples/caroling/carols-check.mp3` (CAROL at 84 bpm, then THE FIRST NOWELL at 104 bpm) and `examples/caroling/project.json`.

**The grid.** A carol bar of three beats is **12 steps** (4 carol bars = 3 engine bars). CAROL is in 6/8: an eighth = 2 steps, the engine bpm counts the carol's quarter notes (dotted quarter = bpm / 1.5; 84 bpm = dotted quarter 56). THE FIRST NOWELL is in 3/4: a quarter = 4 steps, bpm = quarter notes. Each tune has a one-bar pickup pattern (the upbeat sits at the end of that bar) and a body pattern whose step 0 is the first downbeat; carol bar *n* starts at step 12(*n*-1). Carol barlines therefore fall inside engine bars: count phrases in steps, not engine bars. Change key with the track's `"transpose"`. Drums and chord stabs that should follow the carol's bars need the same 12-step thinking (e.g. a 3-engine-bar pattern = 4 carol bars).

### It Came Upon the Midnight Clear (CAROL, R. S. Willis 1850; words E. H. Sears 1849). B-flat major, 6/8, 16 bars + upbeat
```
"carol_pickup": {"bars": 1, "<track>": "14:F4:2"}
"carol": {"bars": 12, "<track>": "0:D5:4 4:C5:2 6:C5:2 8:Bb4:2 10:G4:2 12:F4:4 16:G4:2 18:F4:4 22:F4:2 24:G4:2 26:A4:2 28:Bb4:2 30:Bb4:2 32:C5:2 34:D5:2 36:C5:10 46:F4:2 48:D5:4 52:A4:2 54:C5:2 56:Bb4:2 58:G4:2 60:F4:4 64:G4:2 66:F4:4 70:F4:2 72:G4:4 76:G4:2 78:A4:2 80:G4:2 82:F4:2 84:Bb4:10 94:D5:2 96:D5:4 100:D4:2 102:D4:2 104:E4:2 106:F#4:2 108:G4:4 112:A4:2 114:Bb4:4 118:D5:2 120:C5:2 122:Bb4:2 124:A4:2 126:G4:2 128:A4:2 130:G4:2 132:F4:10 142:F4:2 144:D5:4 148:A4:2 150:C5:2 152:Bb4:2 154:G4:2 156:F4:4 160:G4:2 162:F4:4 166:F4:2 168:G4:4 172:G4:2 174:A4:2 176:G4:2 178:F4:2 180:Bb4:12"}
```
Form: A (lines 1-2, ending on the dominant), A' (lines 3-4, ending home), B (lines 5-6, "Peace on the earth": the low D4 and the rising chromatic F#4-G4 line, ending on F), A' (lines 7-8). Range D4-D5.

**Quote by phrase, not by bar.** Every line begins on an eighth-note upbeat (the last eighth of the previous bar). Each phrase runs from its own upbeat to its last note; drop the next line's upbeat:

| line | text (stanza 1, Hutchins 1916) | notes | syllables on notes (melismas joined with `_` style) |
|---|---|---|---|
| 1 | It came upon the midnight clear, | `carol_pickup` + `carol` 0-21 (ends 18:F4 "clear"; drop 22:F4 "That") | It F4 / came D5 / up- C5 / -on C5-Bb4 / the G4 / mid- F4 / -night G4 / clear F4 |
| 2 | That glorious song of old, | 22-45 (ends 36:C5:10 "old"; drop 46) | That F4 / glo- G4-A4 / -rious Bb4 / song Bb4-C5 / of D5 / old C5 |
| 3 | From angels bending near the earth | 46-69 (ends 66:F4; drop 70) | From F4 / an- D5 / -gels A4 / bend- C5-Bb4 / -ing G4 / near F4 / the G4 / earth F4 |
| 4 | To touch their harps of gold: | 70-93 (ends 84:Bb4:10; drop 94) | To F4 / touch G4 / their G4 / harps A4-G4 / of F4 / gold Bb4 |
| 5 | "Peace on the earth, good will to men, | 94-117 (ends 114:Bb4; drop 118) | Peace D5 / on D5 / the D4 / earth D4-E4 / good F#4 / will G4 / to A4 / men Bb4 |
| 6 | From heaven's all-gracious King;" | 118-141 (ends 132:F4:10; drop 142) | From D5 / then C5 Bb4 A4 G4 A4 G4 for "heav'n's all-gracious" / King F4. The scan does not show the melismas of this bar clearly: play it, or set your own underlay and say so in the journal |
| 7 | The world in solemn stillness lay | 142-165 (ends 162:F4; drop 166) | The F4 / world D5 / in A4 / sol- C5-Bb4 / -emn G4 / still- F4 / -ness G4 / lay F4 |
| 8 | To hear the angels sing. | 166-191 (ends 180:Bb4:12) | To F4 / hear G4 / the G4 / an- A4-G4 / -gels F4 / sing Bb4 |

Lines 1, 3 and 7 share their shape; lines 2, 4 and 8 answer it. Other stanzas (Hutchins): 2 "Still through the cloven skies they come", 3 "O ye, beneath life's crushing load", 4 "For lo! the days are hastening on"; stanza 3 ("O rest beside the weary road, and hear the angels sing") is the most human one.

**Sources and checks (CAROL).**
- *Carols Old and Carols New* (C. L. Hutchins, Boston: Parish Choir, 1916), carol 607, p. 491, B-flat, 6/8, SATB, stanzas 1-4 ([archive.org scan, leaf 523](https://archive.org/details/carolsoldcarolsn00hutc/page/n523)): read bar by bar for pitches, rhythm, ties and the stanza 1 underlay.
- hymnary.org, tune CAROL: incipit **5 3 2 2 1 6 5 6 5 5 6 7 1 1 2**, one hymnal (LDS 1985) **5 3 7 2 1** ([hymnary.org](https://hymnary.org/tune/carol_willis)).
- Mutopia Project, "Carol (hymntune)", typeset from cyberhymnal.org, public domain ([carol.mid / carol.ly](https://www.mutopiaproject.org/ftp/WillisRS/carol/), MD5 of carol.mid a779e06106657fbec961e67f475b4534, kept outside the repo in ~/.cache/spectre/refs/carols/).
- **The one disagreement:** the second note of line 1 ("up-") is C5 in Hutchins and in hymnary's standard incipit, A4 in Mutopia (and the LDS hymnal). Lines 3 and 7 have A4 in every source. The block keeps **C5** (two sources against one).
- `examples/caroling/check/check_midi.py`: the block against Mutopia's soprano: 65/66 notes at the same pitch and onset, the miss being that note; Mutopia's slurs on one pitch (re-struck in its MIDI) are tied in the scores and merged.
- `examples/caroling/check/check_render.py`: the engine's piano render pitch-tracked (pYIN): **66/66** notes at the written pitch.

### The First Nowell (traditional; Sandys 1833; as in Bramley & Stainer 1871). D major, 3/4, 24 bars + upbeat
```
"nowell_pickup": {"bars": 1, "<track>": "12:F#4:2 14:E4:2"}
"nowell": {"bars": 18, "<track>": "0:D4:6 6:E4:2 8:F#4:2 10:G4:2 12:A4:8 20:B4:2 22:C#5:2 24:D5:4 28:C#5:4 32:B4:4 36:A4:8 44:B4:2 46:C#5:2 48:D5:4 52:C#5:4 56:B4:4 60:A4:4 64:B4:4 68:C#5:4 72:D5:4 76:A4:4 80:G4:4 84:F#4:8 92:F#4:2 94:E4:2 96:D4:6 102:E4:2 104:F#4:2 106:G4:2 108:A4:8 116:B4:2 118:C#5:2 120:D5:4 124:C#5:4 128:B4:4 132:A4:8 140:B4:2 142:C#5:2 144:D5:4 148:C#5:4 152:B4:4 156:A4:4 160:B4:4 164:C#5:4 168:D5:4 172:A4:4 176:G4:4 180:F#4:8 188:F#4:2 190:E4:2 192:D4:6 198:E4:2 200:F#4:2 202:G4:2 204:A4:8 212:D5:2 214:C#5:2 216:B4:8 224:B4:4 228:A4:8 236:A4:4 240:D5:4 244:C#5:4 248:B4:4 252:A4:4 256:B4:4 260:C#5:4 264:D5:4 268:A4:4 272:G4:4 276:F#4:12"}
```
Form: verse = two identical 8-bar halves (bars 1-16), chorus 8 bars (bars 17-24) that opens like the verse and ends on "Born is the King of Israel". The whole tune circles the same four-bar descent (D C# B A); range D4-D5.

| phrase | text (stanza 1, Stainer 1871) | notes | syllables on notes |
|---|---|---|---|
| v1 | The first Nowell the Angel did say | `nowell_pickup` + `nowell` 0-43 (ends 36:A4:8 "say"; drop 44, 46 "Was to") | The F#4-E4 / first D4-E4 / Now- F#4-G4 / -ell A4 / the B4-C#5 / An- D5 / -gel C#5 / did B4 / say A4 |
| v2 | Was to certain poor shepherds in fields as they lay; | 44-91 (ends 84:F#4:8; drop 92, 94 "In") | one syllable per note: Was B4 / to C#5 / cer- D5 / -tain C#5 / poor B4 / shep- A4 / -herds B4 / in C#5 / fields D5 / as A4 / they G4 / lay F#4 |
| v3 | In fields where they lay keeping their sheep, | 92-139 (ends 132:A4:8; drop 140, 142 "On a") | In F#4-E4 / fields D4-E4 / where F#4-G4 / they A4 / lay B4-C#5 / keep- D5 / -ing C#5 / their B4 / sheep A4 |
| v4 | On a cold winter's night that was so deep. | 140-187 (ends 180:F#4:8; drop 188, 190 "Now-") | On B4 / a C#5 / cold D5 / win- C#5 / -ter's B4 / night A4-B4 / that C#5 / was D5-A4 / so G4 / deep F#4 (Hutchins 1916: "freezing so deep") |
| c1 | Nowell, | 188-199 | Now- F#4-E4 / -ell D4-E4 |
| c2 | Nowell, | 200-211 | Now- F#4-G4 / -ell A4 |
| c3 | Nowell, | 212-223 | Now- D5-C#5 / -ell B4 |
| c4 | Nowell, | 224-239 | Now- B4 / -ell A4 (held, re-struck at 236 under one slur) |
| c5 | Born is the King of Israel. | 240-287 (ends 276:F#4:12) | Born D5 / is C#5 / the B4 / King A4-B4 / of C#5 / Is- D5-A4 / -ra- G4 / -el F#4 |

The four "Nowell" calls (c1-c4) each stand alone: a call at the door can be one of them. Other stanzas: 2 "They looked up and saw a Star", 3 "And by the light of that same Star", up to 6 (Stainer; Hutchins prints 6 with small word differences).

**Sources and checks (THE FIRST NOWELL).**
- *Christmas Carols New and Old*, first series (H. R. Bramley and J. Stainer, London: Novello, about 1871), no. VI, pp. 12-13, D major, 3/4 ([archive.org](https://archive.org/details/christmascarolsn00staiiala)): read bar by bar, all 24 bars and the stanza 1 underlay.
- Hutchins 1916, carol 266, E-flat major ([archive.org, leaf 262](https://archive.org/details/carolsoldcarolsn00hutc/page/n262)): the verse agrees with Stainer bar for bar (transposed); the chorus differs in two bars: bar 17 (E-flat half note and two eighths, not the verse's dotted rhythm) and bar 20 (a dotted half instead of a half slurred to a quarter). The block follows Stainer and Mutopia (two against one).
- Mutopia Project, "The First Noel (hymntune)", public domain ([first_noel.mid / .ly](https://www.mutopiaproject.org/ftp/Traditional/first_noel/), MD5 of first_noel.mid bfded4cef3167f399a4fbcec8725536e, outside the repo): **73/73** notes at the same pitch and onset as the block (`check_midi.py`).
- Engine render pitch-tracked: **73/73** (`check_render.py`).

## Nearest wrong feelings (and what separates them)
- **Greeting-card kitsch:** sugar on everything: sleigh bells on every beat, glockenspiel sparkle, a major-key smile with no shadow, reverb wash. The real thing has cold air, breath, a slightly uneven group, and a reason to be singing at this door.
- **A shopping-mall jingle:** a loop of a famous tune with a bright pad and a beat, built to be heard and not listened to; the quote as a brand. The carol must be a song people bring to someone, not background.
- **A sad Christmas ballad:** a slow minor piano, a lonely voice, absence as the subject. Melancholy can be a shadow inside the warmth, not the room.
- **A church service:** an organ prelude, a cathedral reverb, a hymn sung through in four parts in order, reverence as the subject. Caroling is outside, at the threshold, among neighbours; sacred words, street manners.
- **A novelty song:** jingle-bell comedy, a swing band, sound effects (sleigh, reindeer, ho-ho-ho), a wink. Humour is not the register.

## Engine mapping (what exists, what is weak, what is missing)
| need | engine | status |
|---|---|---|
| carolers' choir (upper voices, words or vowels) | `singer` `"source": "svs"` (female voices, and `hanami-male` for tenor and bass; docs/voice/VOICES.md), doubles and divisi on separate tracks | exists; SATB with `hanami-male` not tried yet |
| choir pad (wordless) | `choir` (sawtooth through fixed vowel formants; crude), `vox2` (wordless, LF glottal source), `pad` | weak: the `choir` pad reads synthetic; use it under the svs voices, not alone |
| tenor and bass lines | brass (missing), `organ`, `strings`, `ebass` (bass guitar as an upright stand-in); `hanami-male` (soft, covered; docs/voice/VOICES.md "Male voices") | weak |
| handbells | `bell` (FM bell: `ratio` 3.5 by default, inharmonic, church-bell-like; `ratio` 3.0 puts the strong partial at the third harmonic like a tuned handbell, `decay` 2-3 s; `"clean": true` lets each note ring out) | **weak**: no handbell model (no handbell partial set, no LV, damping, martellato or shake) |
| brass quartet, trombone choir | none (`trembita` is a natural-harmonic alphorn, monophonic; `lead`, `organ` and `supersaw` are not brass) | **missing** |
| pipe organ | `organ` (additive sine drawbars: a Hammond-like tone, no pipe chiff, no mixtures or reeds) | **weak** for a church or parlour organ |
| sleigh bells | none (`shaker`: a 4-11 kHz noise burst; `tridksnis`: a staff of jingling plates and rings, the closest) | **missing** |
| glockenspiel, celesta | `glockenspiel`, `celesta` (engine/chamber.py, measured on reference recordings; docs/MANUAL.md); `vibraphone`; `bell` with `"clean": true` rings out without the click | exist (since 2026-11-24) |
| piano, strings, acoustic guitar | `piano`, `strings`, `strings_section`, `cello`, `viola`, `violin`, `acguitar` (nylon or steel) | exist |
| harp, vocal percussion, de-esser | none | **missing** ("Granularity", engine gaps) |
| street and room | `room` fx, reverb send; no outdoor ambience textures (snow, footsteps, a door) | partial |
