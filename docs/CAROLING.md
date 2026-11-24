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
| Master | `studio.py master vNNN --genre caroling` (= `--target rock --lufs -14 --tp -1 --eq 0.5 --translate 0.2`, mono below 120 Hz) | "The mastering decision" |

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
- **What the engine has:** `singer` `"source": "svs"` (DiffSinger) with seven **female** voices (docs/voice/VOICES.md, engine/voices.json): `hanami` (warm, clear; tagged "carol choir"), `hanami-soft` (soft, dark: choir pads), `hanami-dark` (solemn, covered: an alto colour, less intelligible), `hanami-power`, and the LEONA voices (bright, youthful: wrong for a carol choir except as a child-like colour). **There is no licence-clean male voice**, so a real SATB choir is impossible: build the carolers as **female upper voices** (soprano and alto, divisi, doubled takes with other `seed`s, modes and banks a third or sixth apart; `examples/vocals/svs/choir-line-dry.mp3`), and give tenor and bass lines to instruments (brass, organ, low strings) or to `choir`/`vox2` pads. The `tts` male voices (Kokoro `am_michael`, `am_adam`) are speech-derived and weak for sustained choral singing: at most a spoken or half-sung call.
- **Range:** write the svs voices A3-D5 (sweet spot F#4-B4; Hanami's training data sits G3-D5). Both verified carols below sit D4-D5 in their hymnal keys: sing them there, or transpose down.
- **What a voice may do here:** a refrain fragment ("Nowell, Nowell", "to hear the angels sing"), a wordless choir ("oo", "ah") under the bells, a call at the door, a hummed verse. Never a carol sung through verse after verse by one voice.
- **Words:** only public-domain words may be sung (the stanzas of the verified carols below, as printed in their sources), or original words the producer writes. Note the voices' licence: credit Lotte V and the Potluck vocoder in the README (credit lines in engine/voices.json) and never use them for a political subject. The carols' words are religious; the terms as summarised in docs/voice/VOICES.md exclude political, hateful and illegal use, not religious texts.
- **Mix (choir texture):** voices a little behind the bells and brass, sharing one room (one reverb send for all carolers), panned like a small group standing in a line (soprano left of centre, altos right, doubles wider); see the recommended svs mix chain in docs/MANUAL.md "Voices".

## Mixing and recording practice
- **A choir is recorded as a group, at a distance:** a stereo pair (ORTF, or spaced cardioids about half the choir's width apart), one to two metres in front of the front row and a metre or more above it; the distance sets the balance of direct and reverberant sound; a spot mic for piano or organ, not too prominent; outriggers for a large choir; or close and "too dry", with reverb added in the mix ([Sound On Sound, Q&A](https://www.soundonsound.com/sound-advice/q-how-do-you-record-choir)). A live choral recording got convolution reverb on its close mics "to impose the acoustics of a real concert hall" and about 6 dB of compression on the vocal subgroup's peaks ([Sound On Sound, live choral](https://www.soundonsound.com/techniques/recording-live-choral-performance)).
- **Outdoors in winter the room is the street:** fresh snow is a strong absorber (a 4-inch layer has an NRC of 0.89, like acoustic panels); compacted snow and ice reflect far more ([Acentech](https://www.acentech.com/resources/the-quiet-snow/)). A carol at the door is dry and close, with short early reflections off the house fronts and no long tail; a church or hall carol (King's College) has a long reverb. Choose one space per moment and let a change of space mean something (the door opening, coming inside).
- **Tonal shape of holiday records:** sparkly top ends on modern productions, roll-off below about 80 Hz on Mariah Carey's single, mono mixes on the early-1960s classics ([iZotope 2025](https://www.izotope.com/community/blog/holiday-songs-lufs-2025)).

## Catalogue measurements (AcousticBrainz, 2026-11-24)
Track lengths from MusicBrainz; tempo, key and ReplayGain from AcousticBrainz (Essentia 2.1-beta2 low-level data, submitted by users for any edition of each recording). ReplayGain was converted to loudness with **LUFS ≈ -23.7 - RG**, fitted on Spectre's own eleven masters (Essentia ReplayGain against pyloudnorm, spread ±0.7 dB on those; choral spectra may shift it by another dB or two). Tempo estimates on unaccompanied choirs are unreliable (rubato, no drums, octave errors). Scripts in the orchestrator's workspace; the raw numbers are reproduced here.

| album (MusicBrainz release) | tracks | median length (middle half) | est. LUFS median (range) |
|---|---|---|---|
| Ray Conniff Singers, *Here We Come A-Caroling* (1965; CD 2004, [e42549b1](https://musicbrainz.org/release/e42549b1-d584-32f5-9c05-371da9bc15b0)) | 12 | 2:25 (2:11-2:48) | -19.4 (-20.6 to -15.6) |
| Pentatonix, *That's Christmas to Me* (2014, [d4a03a1d](https://musicbrainz.org/release/d4a03a1d-3d19-4868-acfe-5c3c890393b3)) | 11 | 3:05 (2:42-3:23) | -12.4 (-18.9 to -9.5) |
| Straight No Chaser, *Holiday Spirits* (2008, [ff026852](https://musicbrainz.org/release/ff026852-5125-4a27-8f8e-8ad2e4beec90)) | 14 | 3:13 (2:30-3:36) | -13.6 (-15.4 to -11.9) |
| Chanticleer, *A Chanticleer Christmas* (2010, [5f65ba72](https://musicbrainz.org/release/5f65ba72-196c-46b0-85fa-c7a12a45bbc5)) | 15 | 2:39 (2:22-4:32) | -20.1 (-24.0 to -18.7) |
| King's College Choir, *Christmas Carols from King's College* (1986, [690d994c](https://musicbrainz.org/release/690d994c-6f78-4e2c-ac76-28ff831564c6)) | 22 (15 with data) | 3:10 (2:32-3:42) | -22.8 (-29.2 to -12.8) |

Carols on the caroling album (Conniff), length / tempo estimate / key estimate / est. LUFS: "Here We Come A-Caroling" 2:28 / 100 / -20.2; "Silent Night" 2:48 / 148 (eighths: dotted quarter about 49) / F / -20.6; "God Rest Ye Merry, Gentlemen" 2:43 / 148 / -17.9; "Away in a Manger" 2:13 / 112 / A / -19.2; "Joy to the World" 2:14 / 86 / A-flat / -19.2; "It Came Upon the Midnight Clear" 2:46 / 130 / A-flat / -20.4; "O Little Town of Bethlehem" 2:48 / 122 / G / -19.2. Robert Shaw Chorale and Mormon Tabernacle Choir albums were looked up too but have (almost) no AcousticBrainz data.

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
| carolers' choir (upper voices, words or vowels) | `singer` `"source": "svs"` (female voices only; docs/voice/VOICES.md), doubles and divisi on separate tracks | exists; **no male voice**, so no real SATB |
| choir pad (wordless) | `choir` (sawtooth through fixed vowel formants; crude), `vox2` (wordless, LF glottal source), `pad` | weak: the `choir` pad reads synthetic; use it under the svs voices, not alone |
| tenor and bass lines | brass (missing), `organ`, `strings`, `ebass` (bass guitar as an upright stand-in), `tts` male singer (spoken-voice derived) | weak |
| handbells | `bell` (FM bell: `ratio` 3.5 by default, inharmonic, church-bell-like; `ratio` 3.0 puts the strong partial at the third harmonic like a tuned handbell, `decay` 2-3 s) | **weak**: no handbell model (no handbell partial set, no damping or martellato) |
| brass quartet, trombone choir | none (`trembita` is a natural-harmonic alphorn, monophonic; `lead`, `organ` and `supersaw` are not brass) | **missing** |
| pipe organ | `organ` (additive sine drawbars: a Hammond-like tone, no pipe chiff, no mixtures or reeds) | **weak** for a church or parlour organ |
| sleigh bells | none (`shaker`: a 4-11 kHz noise burst; `tridksnis`: a staff of jingling plates and rings, the closest) | **missing** |
| glockenspiel, celesta | `musicbox`, `bell` | approximate |
| piano, strings, acoustic guitar | `piano`, `strings`, `violin`, `acguitar` (nylon or steel) | exist |
| street and room | `room` fx, reverb send; no outdoor ambience textures (snow, footsteps, a door) | partial |
