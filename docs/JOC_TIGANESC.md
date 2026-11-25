# Joc țigănesc: a working brief

For sessions that make Romanian lăutar wedding dance music, the *joc țigănesc* (Romani dance tune) with a solo violin over guitar, bass and percussion. A vocabulary, not a rulebook. The wider Romanian folk vocabulary (doina, hora, sârba, modes, instruments) is in docs/ROMANIAN.md; this file holds the researched configuration, the violin idiom, the band's patterns and the wedding. Researched 2026-11-24 for session 010.

## Configuration (engine: `--genre joc` in engine/genres.json)
| Setting | Value | Source |
|---|---|---|
| Length | **3:00-5:00**, typically 3:30-4:30 | Seven Taraf de Haïdouks recordings measured by AcousticBrainz run 2:51 ("Leliță cîrciumăreasă"), 3:19 ("Sîrba"), 4:34 ("Azi eram frumoasă jună"), 5:21 ("Turceasca a lu Kalo"), 6:08 ("A la Turk"), 6:09 ("Turceasca"), 7:14 ("Tot taraful", a medley); median 5:21, single dance tunes at the short end ([AcousticBrainz](https://acousticbrainz.org/4ae7b894-a617-44ec-a017-0b1a47325f59), see Sources for all seven). No wider dataset of lăutar track lengths was found; the 3:00-5:00 window is the single-dance end of that sample |
| Form | **rounds of a dance tune**: strains of 8 or 16 bars of 2/4 (the reference tune is 24 bars), each repeated with variation, round after round, faster each round; an optional slow (rar) opening, then the fast (repede) dance; a stop or cadence at the end. Primaș preludes and interludes between rounds | the reference score plays its 24-bar tune four times at quarter = 50, 70, 90, 110 (analysis below); "Dans Țigănesc Rar, Dans Țigănesc Repede" (Muntenia, taught by Theodor Vasilescu): a slow part in 6/8, then a fast part in 2/4 whose strains A B C D repeat three times ([SoCal Folk Dance](https://socalfolkdance.org/dances/D/Dans_Tiganesc_Rar-Dans_Tignanesc_Repede.pdf)); the Romani (Hungarian) order slow, medium, fast and "even faster" ([Wikipedia, Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)); the primaș "plays preludes and interludes" ([Wikipedia, Romanian folk violin](https://en.wikipedia.org/wiki/Romanian_folk_violin)) |
| Tempo | **dance tempo quarter = 110-140 in 2/4** (the bar passes 55-70 times a minute); quarter = 50 is the reference score's practice tempo, not a dance tempo; a slow rar or listening (de ascultare) section can sit far lower; **tempo rises round by round and accelerates at the end** | the score's tempo ladder 50 → 70 → 90 → 110 over four identical passes (a learning progression ending at 110); AcousticBrainz tempo estimates for the seven Taraf recordings above: 94-172 bpm (algorithmic, octave errors possible); "a clear duple pulse in the accompaniment" in medium and fast horas ([Wikipedia, Lăutărească music](https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music)); the cimbalom "indicates accelerations and de-accelerations" and the fast czardas is followed by "the even faster friss" ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)) |
| Meter and feel | **2/4**, felt in two (one pulse per beat) or, at fast tempos, in one per bar; bass on the beats, chords on the afterbeats ("oom-pa"); melodic 16ths with slurred pairs and fours, three-16th pickups into each phrase; the soloist plays "just too early, or just too late" against the band | afterbeat ("estam") in fast movements ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)); the cobza's off-beat țiitură (docs/ROMANIAN.md); the score's rhythm cells (analysis below). In the engine one pattern bar = two bars of 2/4 (docs/MANUAL.md, "Other meters") |
| Rate of change | **something changes every strain** (8-16 bars of 2/4 = 4-8 pattern bars): a new variation of the tune, an ornament level, an instrument in or out; the tempo steps up each round | derived from the dance form above (strains repeated with variation; lăutari improvise, "an improvisation or a trill" added to the melody, [The Attic](https://theatticmag.com/features/2409/l%C4%83ut%C4%83rie-then-and-now%3A-inside-romania's-romani-musical-heritage.html)); the exact rate is **hand-tuned** craft |
| Role | the **violin leads throughout** (melody, preludes, interludes, improvisation); guitar and bass hold the dance (țiitură); percussion carries the dancers' feet and claps; a voice is optional (shouts to the dancers, strigături) | "In most regions the first violin (primaș) acts as artistic leader" and players hold the violin so their voice is free "for calls to dancers" ([Romanian folk violin](https://en.wikipedia.org/wiki/Romanian_folk_violin)); a wedding band with "a violinist, a guitarist, a string bass player" and a vocalist ([Beissinger 2007, Folklorica](https://journals.ku.edu/folklorica/article/view/3757)) |
| Loudness of releases | folk masters run **-14 to -10 LUFS** integrated (-10 "acceptable" for commercial full arrangements; sparse ones quieter), with a loudness range of **at least 6 LU**, mild compression and limiting; acoustic genres are often left near -16 because they "live on dynamics"; streaming normalizes to -14 (Spotify), -16 (Apple); chart pop averages -8.3 | [Sage Audio, mastering folk](https://www.sageaudio.com/articles/mastering-for-folk-music); [RoEx](https://www.roexaudio.com/blog/what-lufs-should-i-master-at) (advice, not measurement); [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends). No loudness survey of Romanian lăutar or Balkan Romani releases was found |
| True peak | **-1 dBTP** (as every Spectre master; MP3 encoding adds about 0.5 dB) | streaming guidance ([RoEx](https://www.roexaudio.com/blog/what-lufs-should-i-master-at)); docs/MANUAL.md |
| Dynamics | keep the arc: a quieter slow opening, the climax loudest; no dense, heavily compressed sound | "never resorts to a highly compressed and dense sound", LRA at least 6 LU ([Sage Audio](https://www.sageaudio.com/articles/mastering-for-folk-music)) |
| Tonal balance | acoustic records have a "natural top-end decay": in the Pestana et al. 2013 genre averages, folk has the lowest spectral centroid (603 Hz) of the genres measured | [Pestana, Ma, Reiss, Barbosa & Black 2013](https://joshreiss.github.io/documents/2013/Pestana%20Ma%20Reiss%20-%20AES135.pdf) (Table 2 and the text on Fig. 5); docs/MASTERING.md |
| Low end and width | bass and toba in the centre, mono below 120 Hz; avoid "an excessively wide stereo image"; the 2024 chart average is -8.5 LU side minus mid | [Sage Audio](https://www.sageaudio.com/articles/mastering-for-folk-music); [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends) |
| Master | `studio.py master vNNN --genre joc` (= `--target rock --lufs -11 --tp -1 --eq 0.7 --translate 0.3`, mono below 120 Hz) | see "The mastering decision" |

### The mastering decision: `joc`, the measured `rock` curve reused, -11 LUFS
- **Curve: `rock`, reused, until the folk curve is extracted.** Pestana et al. (2013) measured a folk average spectrum in the same Fig. 5 that gave Spectre its hip-hop, trance and rock curves, but the figure couldn't be fetched here (the network blocks the PDF; `tools/pestana_ltas.py` already lists the folk group, so `python3 tools/pestana_ltas.py p5.svg` prints it once the PDF is reachable). Of the three measured curves, `rock` (the mean of pop and rock) has the steepest top (-12.5 dB at 10 kHz, -23 at 16 kHz against -8/-18 for trance and -9.5/-20 for hip hop), which is closest to the paper's "natural top-end decay on more acoustic endeavors", and it asks for 100-400 Hz body, which a guitar body, a bass guitar and a bass drum give. **Status: reused measured curve, not measured on folk; replace it with the folk curve when the figure is reachable.**
- **-11 LUFS:** inside the folk range (-14 to -10) for a full arrangement with drums and bass, the dance end of it; 1.5 LU quieter than Spectre's other genres so the bow attacks and the arc survive. -11 is a choice inside a sourced range, not a measured median.
- **`translate` 0.3 and `eq` 0.7: hand-tuned** (as `rock`): little bass-harmonic enhancement, since the bass guitar already speaks in its 2nd and 3rd harmonics.
- **Where the engine can't match practice:** it can't target a loudness range; keep the dynamics in the arrangement (a quiet opening, the climax loudest) and read the master report's LRA.

## What "joc țigănesc" is
- **The term.** *Joc* is the Romanian word for a dance (and a dance tune); *țigănesc* means Gypsy, i.e. Romani. Archives use it as a label for Romani dance tunes: a 1972 field recording from Ördöngösfüzes (Transylvania) titled "joc ţigănesc" was played by two violins, a viola (brácsa) and a double bass ([Hungaricana / ZTI](https://zti.hungaricana.hu/en/82189)). In Muntenia the "Dans Țigănesc" is a slow part in 6/8 followed by a fast part in 2/4, danced solo or in a loose circle, the steps fixed but the arms free and improvised, "hands held freely above shoulder height, with fingers snapping", with clapping, thigh slapping, small "chugging hops" and a slow turn with the torso bent forward ([SoCal Folk Dance](https://socalfolkdance.org/dances/D/Dans_Tiganesc_Rar-Dans_Tignanesc_Repede.pdf)). Related lăutar genres: the medium and fast *hora lăutărească* or *hora țigănească* ([Lăutărească music](https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music)) and the *manea*, once an in-group Romani women's solo dance ([RomArchive, manele](https://www.romarchive.eu/en/music/balkan/manele/)). No source found gives a fixed definition of the joc țigănesc: treat it as a performers' label for a Romani dance tune, fast, in 2/4, in minor with augmented seconds, led by the violin.
- **Who plays it.** Lăutari: professional Romani musicians who play weddings, christenings and funerals; the violin is "the central instrument", the accordion became key in the 20th century, the cimbalom partly replaced the cobza ([Lăutărească music](https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music)). Lăutari play "by feeling, by ear, without notation" and improvise: "they play according to banknotes!" ([The Attic](https://theatticmag.com/features/2409/l%C4%83ut%C4%83rie-then-and-now%3A-inside-romania's-romani-musical-heritage.html)).
- **References to listen for (context):** Taraf de Haïdouks (Clejani; violinist Nicolae Neacșu), Grigoraș Dinicu ("Hora staccato"), Alexandru Cercel, Constantin Lupu (Moldavian glissando style), Fănică Luca (nai), vocalists Romica Puceanu and Gabi Luncă ([Romanian folk violin](https://en.wikipedia.org/wiki/Romanian_folk_violin); [Lăutărească music](https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music)). Fanfare Ciocărlia and Fanfara Zece Prăjini are the brass-band side of the same world: context, not this track's sound.

## The violin: what an expert will listen for
**Technique of the lăutar violin** ([Wikipedia, Romanian folk violin](https://en.wikipedia.org/wiki/Romanian_folk_violin) unless noted):
- **Left hand:** the neck rests deep in the palm and the strings are stopped "with flatter finger pads rather than fingertips", which gives "a wide, slow vibrato"; shifts are slower and audible, "often shaped as expressive glissandi". Measured string vibrato elsewhere: 5.5-8 Hz, 0.2-0.35 semitones extent ([Timmers & Desain 2003](https://www.mcg.uva.nl/mmm-2003/papers/mmm-35/mmm-35.html), citing Seashore, Sundberg and Meyer): the lăutar vibrato sits at the slow, wide end.
- **Bow:** often gripped higher than the frog "for short, sharp strokes"; the typical stroke has "a pause in the middle", separating an on-beat from an off-beat ([BabaYaga Music](https://www.babayagamusic.com/Music/romanian-music.htm)).
- **Ornaments, the *floricele* ("little flowers"):** mordents, trills and grace notes; "false lăutar trills" are "intense tremolos with brief touches of the upper note"; glissando and portamento everywhere; in the Moldavian school (Constantin Lupu) "short terminal glissandi at phrase endings". Romanian ornament studies list simple, double and triple appoggiaturas (from above and below), the trill, the upper and lower mordent, the gruppetto and the glissando, plus folk forms: the sliding appoggiatura, the sliding trill and the sliding mordent ([Types of ornaments in traditional instrumental music](https://doaj.org/article/dc854ca39618413bb55220b1448e4ba0)). "A long note is not simply played but is either approached by an elaborate ornament", or slides into the pitch ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)).
- **The primaș's vocabulary:** "chromatic runs, double stops, arpeggios" ([BabaYaga Music](https://www.babayagamusic.com/Music/romanian-music.htm)); in Romani style the soloist takes "breathing spaces" (Luftpausen) and "lingers on the dominant" ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)).
- **Intonation:** "non-tempered intonation and microchromatic inflections" are part of the style: leading tones pulled up into their resolution, the augmented second played wide, never a sloppy pitch.
- **Tuning:** pitch is not fixed; scordatura ("stricarea drăsurii") is common in Oltenia and Muntenia; a common one lowers the E string to D (G-D-A-D).

**What separates the real thing from a cliché (for the producer; partly craft):**
- Ornaments are placed, not sprayed: graces on strong beats and on the target notes of phrases, crushed into the note from a semitone below (the reference score: 32 of 35 graces); trills and false trills on long notes; mordents on short accented notes; runs clean, without vibrato.
- Vibrato only on notes long enough to bloom, starting after the attack and widening; none on 16ths.
- Bow attacks speak: up-bow pickups into a down-bow downbeat (the score's bowing marks), short sharp strokes with a gap in fast passages, a bitten accent at the peak, a slurred run inside one bow.
- The 2/4 swings: the violin plays a little early or late against the afterbeat, never stiff on the grid (the hand's `humanize_ms` plus written anticipations), while the bass and chords stay steady.
- Phrases breathe: a long note at the phrase end (often with a grace or a fall), then a three-16th pickup.

## Instruments and roles in a modern wedding band
- **Violin** (primaș): melody, preludes, interludes, improvisation. Engine: `violin` (docs/MANUAL.md, "Lăutar band").
- **Guitar:** chords on the afterbeats, short and damped (the țiitură, the job of the cobza in older tarafs, docs/ROMANIAN.md). A wedding band of the 2000s had "three accordionists, a violinist, a guitarist, a string bass player, and a cimbalom player" plus a synthesizer guest, amplified to "ear-splitting volume" ([Beissinger 2007](https://journals.ku.edu/folklorica/article/view/3757)). Engine: `acguitar` (nylon or steel, `chop` for the afterbeat chops).
- **Bass:** roots and fifths on the beats, approach notes into chord changes; in Romani style "the double bass may glide towards the right tone" ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)). Engine: `ebass` (fingers: `pick` 0.2).
- **Percussion (essential):** in Moldavia, Maramureș and Bihor, "medium sized drums with two skins and a cymbal mounted on the top", struck "with a wooden mallet on one skin and with a thinner stick on the rim or cymbal" ([eliznik](https://eliznik.org.uk/traditions-in-romania/traditional-music/percussion/)); the fanfares' big drum; modern wedding and manele bands add the drum kit and the "oriental" sound of synthesizer, electric violin, clarinet and drums, over the čoček/kyuchek rhythm in 2/4 and 4/4 ([RomArchive](https://www.romarchive.eu/en/music/balkan/manele/)); the dancers clap and snap their fingers ([SoCal Folk Dance](https://socalfolkdance.org/dances/D/Dans_Tiganesc_Rar-Dans_Tignanesc_Repede.pdf)). Engine: `toba` (boom, cinel, both, rim), `kitsnare` (tobă mică, afterbeats), `darbuka` (modern colour), `handclap`, `snap`.
- **Also in the world, not requested:** accordion (reinforces "the after-beat", [Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)), cimbalom (sets the rhythm, signals accelerations), synthesizer (manele).

### "Chitară rece", "vioară rece": the reading
*Rece* means "cold". Searches for "chitară rece", "vioară rece", "chitare reci" and "pe rece" with lăutar terms found no musical use (only shop pages), so it is **not an established term** in the sources reached. Readings, most plausible first:
1. **A timbre word: a dry, clean, natural acoustic sound** ("cold" against the "warm", sweetened, reverb- and chorus-heavy amplified sound of modern wedding bands: electric violin, synthesizer, effects, [RomArchive](https://www.romarchive.eu/en/music/balkan/manele/); Beissinger's "ear-splitting" amplification). This reading is adopted: an acoustic nylon or steel-string guitar played dry and close, an acoustic violin with a clear, unsentimental tone, short reverb sends.
2. **Unamplified / acoustic** as opposed to electric guitar and electric violin: leads to the same instruments.
3. A slip of the keyboard for another word: nothing obvious fits.
Engine: `acguitar` is dry by design (no amp, no chorus); `violin` has `cold` 0-1 (less and later vibrato, a leaner low body, a clearer 2.5-5 kHz). How cold is the producer's choice; a fully cold violin (`cold` 1) loses the "wide, slow vibrato" that defines the lăutar sound, so somewhere around 0.3-0.6 keeps both.

## Harmony and scales
- **Scale:** G minor with a raised 7th (F#) and a raised 4th (C#): G A Bb C# D Eb F#, two augmented seconds (Bb-C#, Eb-F#), the "Gypsy" or "Hungarian" minor; F natural in descending lines; the dominant's own colour D Eb F# G A Bb C is the Phrygian dominant, *hicaz* in Turkish terms (manele are "characterised by Turkish-derived scales (such as hicaz)", [RomArchive](https://www.romarchive.eu/en/music/balkan/manele/); docs/ROMANIAN.md). Much lăutar repertoire is built on Western major and minor scales, with "Turkish modal concepts" in a significant part ([Lăutărească music](https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music)); the Romani-style article warns that "exotic scales like the so-called 'Gypsy scale' are rarely used" in Hungarian Romani music ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)), so the augmented seconds are a colour of this tune family, not of every Romani tune.
- **Chords (in G minor):** i (Gm), the **major** V and V7 (D, D7), the diminished seventh on C# (C#dim7 = the raised 4th's chord, resolving to D or to Gm), iv (Cm), III (Bb), V/V (A7), one chord per 2/4 bar, i and V alternating. This is the implied harmony of the reference tune (analysis below) and matches the Romani-style "preference for diminished chords", the added "transitional chords at the ends of melodies" and the lingering on the dominant ([Gypsy style](https://en.wikipedia.org/wiki/Gypsy_style)). The flat II (Ab, the Neapolitan) is a possible colour from the Phrygian side of the mode: **craft, unsourced**; use it rarely.
- **Cadences:** V7-i at phrase ends; a final G major (B natural) is possible at the end of the last round (the score's last pass has a B natural).

## Rhythm patterns per instrument (one pattern bar = two bars of 2/4; 16 steps)
- **Bass (`ebass`):** beats: `0` `4` `8` `12` (root, fifth, root, fifth), length 2 steps (short, `legato` 0.6); approach notes on `14`-`15` into a chord change; a chromatic walk up into the climax.
- **Guitar (`acguitar`, `chop` 0.7-0.9):** afterbeats `..x...x...x...x.`, `stab_len` 1, `strum` down; a 16th push (`..x..xx...x..xx.`) or up-strums (`strum: alt`) to lift a round; full strums on the downbeat only at cadences.
- **Toba:** `boom` on the beats (`X...x...X...x...`), `both` or `cinel` on the 1 of each 2/4 bar (`X.......X.......`) or on the afterbeats in the hottest round; `rim` knocks for a sparse section.
- **Snare (`kitsnare` as tobă mică):** afterbeats `..x...x...x...x.` with ghost 16ths (`o`) before them; rolls (`R`, `T`) into a new round.
- **Darbuka (modern wedding colour):** `doum` on the beats, `tek` on afterbeats and 16ths, `ka` ghosts.
- **Claps and snaps:** afterbeats or 2 and 4 of the 2/4 pair; they are the dancers: let them join as the wedding heats up.
- **Violin:** the cells of the reference (below): 16-16-8-8-8, 8-8-8-16-16, straight 16ths, a long phrase-ending note with a grace, a three-16th pickup; slurred pairs and fours.

## The reference score: what it teaches (described, never to be copied)
A simplified violin part of a "Joc țigănesc" (arranged by ViolinSAcademy; MusicXML, G minor, 2/4), parsed and analysed with a script; **the melody is not reproduced here and must not be used in a track**.
- **Form and tempo:** one 24-bar tune (after a bar of rest) played four times, at quarter = 50, 70, 90 and 110; the first three passes are identical, the fourth varies its second half and ends high, on G5. It is a practice ladder towards a dance tempo of at least 110, which is how the request's "50" should be read.
- **Range:** D4 (the open D string) to Bb5, mostly on the D and A strings in first position; most frequent pitches D5, Bb4, C5, A4, G4.
- **Accidentals:** F# (leading tone, 30 times) mostly between Eb and G (an augmented second up into the tonic); C# (28) mostly between Bb and D (an augmented second up into the dominant); F natural (26) in descending lines; B natural (13) and E natural (12) rare, mostly in the last pass. So: G harmonic minor plus the raised 4th.
- **Melodic motion:** mostly semitones and whole tones, many repeated notes, minor-third leaps, and octave-displaced leaps back to the low D (a pedal-like return to the open string).
- **Rhythm:** 16ths (256) and 8ths (168) dominate, quarters are rare (21); the commonest bar shapes are 16-16-8-8-8 and 8-8-8-16-16 (with a grace before the third 8th); phrase ends are a quarter (often with a grace) followed by a 16th rest and a **three-16th pickup**.
- **Ornaments:** 35 grace notes, all slashed acciaccaturas, 32 of them a semitone below their main note, all on the beat (16th positions 0 and 4 of the bar).
- **Bowing and articulation:** up-bow marks (37) mostly on the 16th after beat 2 (the start of the pickup), down-bows on downbeats, staccato 8ths on the beats, few slurs (14, mostly pairs), ties across beats.
- **Implied harmony (one chord per bar, a crude fit):** Gm 8 bars, D7 5, C#dim7 3, A7 2, Bb 2, D 2, Cm 2.
- **Phrase:** short cells of 1-2 bars combined into 4-bar phrases with a cadence to Gm every 2-4 bars; the opening two-bar cell returns near the end.

## The wedding (nunta): context for the subject
From a three-day Romani village wedding documented by Beissinger ([Folklorica 2007](https://journals.ku.edu/folklorica/article/view/3757)): Saturday evening the groom is shaved to the "Bridegroom's Song"; Sunday morning processions with the lăutari and the bride readied to the "Bride's Song"; in the afternoon the "Bride's Hora" (hora miresei) and the "Hora of the Fir Tree"; at the gift ceremony (the *dar*) the ritual wedding dance (nunească); the banquet (*masa mare*) with manele and lăutar horas, music "virtually non-stop" and dancing almost constantly until about 4 a.m.; near dawn the bride's veil is removed to "The Bride's Song" and the *hora mare* is danced; at dawn the guests escort the godparents home, still with music. Lăutari have played weddings for centuries, and "you can't have a wedding without muzica lăutărească" ([The Attic](https://theatticmag.com/features/2409/l%C4%83ut%C4%83rie-then-and-now%3A-inside-romania's-romani-musical-heritage.html)). The hora, the closed circle, is the dance of community and unity (docs/ROMANIAN.md). The peak of the night is not one song but the band and the room lifting each other: faster rounds, the violin taking more risks, guests shouting and clapping, money pressed on the musicians ("they play according to banknotes").

## Nearest wrong feelings
- **The tourist "gypsy" cliché:** a csárdás-style showpiece, Monti's Csárdás or "Hora staccato" quoted, wailing vibrato on everything, a sobbing violin and a sudden presto for effect. The real thing is a dance for a room, with steady time and a purpose.
- **The kitsch wedding band:** a synth keyboard sheen, a drum machine, reverb on everything, a cheerful major-key bounce. The brief asks for dry ("rece") acoustic instruments and real minor-mode tension.
- **The mournful doina:** free rhythm, a lament, the slow opening that never leaves. The slow part (if any) is a door, not the room.
- **Chaos:** everything fast and ornamented at once. The bass and the afterbeat never waver; the violin's freedom is heard against them.
- **Generic Balkan brass:** a fanfare (trumpets, tuba, Kočani-style čoček), "Balkan party" clichés. This is a string band with a guitar and percussion.
- **A battle or a stampede:** a pounding four-on-the-floor or a march. The 2/4 here lifts and turns (the dancers hop and turn), it doesn't march.

## Vocals
Weddings have singers (the band above had a female vocalist) and shouts: dancers and musicians call out (*strigături*), and the lăutar violin hold leaves the voice free "for calls to dancers" ([Romanian folk violin](https://en.wikipedia.org/wiki/Romanian_folk_violin)). A voice is optional. Engine limits: no voice sings Romanian (docs/voice/languages/ro.md); a Romanian word sung by the English or Spanish voices comes out with that language's pronunciation. If a voice is used, keep it to a few short calls or wordless lines, and check that they read as the room, not as a gimmick.

## Mixing the voice (researched 2026-11-24)
A voice in a joc is a call, a shout or a short wordless line, never the lead: the violin leads. The principles for every genre and the check procedure are in [docs/voice/MIXING.md](voice/MIXING.md). Values marked *(hand-tuned)* are Spectre's starting points. No engineer's account with settings for a lăutar or Romanian folk vocal was found; the sources are ethnographic.

**What the research says**
- **What voices do over a dance.** *Strigături* are rhythmic shouts in rhyming verse, "an integral part of Romanian folk dances in all zones except Banat": shouted by the dancers, their cadence "the same as the cadence of the steps", usually eight syllables a line, by one person, by a group in unison, or as a dialogue between two groups. A *comandă* is a single word or short shout from the dance leader that signals a change of figure, found mainly in the south ([Eliznik](https://eliznik.org.uk/traditions-in-romania/traditional-dance/strigaturi-and-comanda/)). So the idiomatic voice is spoken-chanted, in the room with the dancers, on the dance's rhythm; a sung lead line belongs to the song genres, not to the joc.
- **The space musicians ask for.** Rom lăutari recording at home asked the ethnomusicologist to add reverb, "typically a 'plate' reverb with a long audible tail", which they felt "opened" the sound; a proper recording is "clean and well arranged", made without an audience, and studio tricks (layering, edits) are normal ([Stoichiță 2024, Journal of Sonic Studies](https://researchcatalogue.net/view/2623369/2623376)). Wedding bands play amplified (the same source recorded one from 200 m away). The polished, reverberant studio sound is the tradition's own taste, not a foreign gloss.
- **Level:** nothing measured for folk. In a band where the primaș leads, a call sits with the accompaniment, under the violin.
- **Mastering:** folk masters -14 to -10 LUFS with a loudness range of at least 6 LU (Configuration); at `joc`'s -11 the master barely touches a short call. The borrowed `rock` curve is the risk: don't brighten a voice to satisfy it (MIXING.md, "What Spectre's master does to a voice").

**What the engine can sing here.** Romanian sung words are not supported yet (docs/voice/languages/ro.md: no voice was trained on Romanian; the Hanami phoneme mapping is an experiment awaiting a native listener; the svs voices are female and may not be used on a political subject). So today: wordless lines and shouts on open vowels (`vox2`, or an svs voice on "ah" or "hey": the svs voices read English words from their dictionary and sing an unknown word as "ah", with a render warning), or no voice.

**Starting chains** (*hand-tuned*):
```json
"mix": {"reverb": {"size": 0.6, "damping": 0.5, "return_db": -6, "lpf": 7000}},

"strigat": {"inst": {"type": "singer", "source": "svs", "voice": "hanami-power", "svs_vibrato": 0.3,
                     "svs_fade_in_ms": 5, "svs_fade_out_ms": 40},
            "pan": 0.3, "send_reverb": 0.15, "reverb_predelay_ms": 30, "push_ms": 0,
            "fx": [{"type": "hpf", "hz": 150}, {"type": "eq", "hz": 800, "gain_db": -2, "q": 0.9},
                   {"type": "comp", "threshold_db": -22, "ratio": 3}, {"type": "highshelf", "hz": 8000, "gain_db": 2}]},

"doina":   {"inst": {"...": "hanami or hanami-soft on 'ah', long notes, svs_vibrato 1"},
            "send_reverb": 0.3, "reverb_predelay_ms": 60,
            "fx": [{"type": "hpf", "hz": 110}, {"type": "eq", "hz": 800, "gain_db": -2.5, "q": 0.9},
                   {"type": "highshelf", "hz": 8000, "gain_db": 3}]}
```
- **Shouts and calls (`strigat`):** short notes on the dance's rhythm, one pitch or a narrow chant, off-centre like a dancer in the room, 3-6 LU under the violin and never in its phrases' peaks; several shouters = several tracks with other `seed`s and voices, all at `push_ms` 0 if they shout words together (MIXING.md, choirs). The plate the musicians ask for is `size` 0.6-0.75 (1.4-2.1 s) on the bus, shared with the violin.
- **A wordless slow line (`doina`, for a rar opening):** the one place a voice may carry a phrase: more reverb behind a pre-delay, natural vibrato, level with the violin or handing over to it.
- **No doubles, no delay throws, no chops:** none of them belongs to the idiom (editorial).

**How to check:** a wordless call has nothing to transcribe; measure the vocal-versus-band loudness (MIXING.md "Checking a voice") and look at the violin's phrase peaks in the zoom view to see that the call sits in the gaps. If the Romanian mapping is approved later, check words with Whisper `small` forced to Romanian as `examples/vocals/svs/romanian.py` does.

## Engine mapping (details in docs/MANUAL.md, "Lăutar band", "Tempo changes", "Other meters")
- `violin` (bowed waveguide, modal body, articulations after the length: `/g-1`, `/m+1`, `/tr+1`, `/ftr+1`, `/sl-3`, `/fall-3`, `/turn`, `/d=D4`, `/h`, `/pz`, `/sp`, `/trem`, `/s`, `/acc`, `cold` 0-1).
- `acguitar` (nylon by default, dry; `chop` for the țiitură), `ebass`, `toba` (boom, cinel, both, rim), `kitsnare`, `darbuka`, `handclap`, `snap`.
- Section `"bpm"`: a number or `[from, to]` for a tempo ramp (the accelerando of the last round). 2/4: one pattern bar = two bars of 2/4.
- A/B renders and spectrograms: `examples/joc/` (old `fiddle` against the new `violin`, the articulations one by one, the band at quarter = 110, the old `cleanguitar` against `acguitar`, an accelerando from 100 to 140, the phrase at quarter = 50).

## What session 010 ("Unison") learned
- **Tempo:** quarter = 50 worked as a metred slow-dance door (bass on the beat, the chop on the afterbeat), not a lament; the dance then ran 100 → 140 in steps between rounds and ramps where the room gets up and in the last round. The climb itself carried the wedding's lift.
- **"Rece":** `acguitar` almost dry, `violin` `cold` 0.45 with more bow noise, a short small room and no delay read as cold without losing the lăutar vibrato on long notes. Still an interpretation; check it with the brief's author.
- **Violin idiom in the engine:** hand-check double stops for playability (`d=` accepts impossible pairs; a same-pitch unison renders well); mark 16ths `nv` at slow tempos; velocity goes after the articulations (`step:note:len/art:vel`).
- **Mix:** body comes from the sources (guitar body EQ, bass drive, the toba tuned and notched away from the bass notes); the dry band's top end stays 5-6 dB under the borrowed rock curve above 10 kHz, and that is the band, not a fault. A measured folk/acoustic curve is still open.

## Layering and EQ carving (researched 2026-11-25)
The cross-genre method is in [PRODUCTION.md](PRODUCTION.md). Labels: **[M]** measured, **[S]** a named source, **[P]** carried over from a professional trance producer's EQ map (2026) where it applies, **[H]** hand-tuned. No source specific to mixing lăutar bands was found; the map below applies general acoustic-instrument guidance to this band and is marked accordingly.

**An acoustic band is not carved like a synth mix.** In acoustic ensemble music, giving each instrument its own frequency slot "breaks up the natural blend"; EQ should be "gentle and broad", and what sounds muddy is usually balance or arrangement (Thinkspace) [S]. The lăutar sound the brief chose is the dry, clean, "cold" one ("Chitară rece" above). So: few sources, each whole; high-pass only what has no business in the bass; cuts of 1-3 dB, wide.

**Layer roles.** The stack is the band, and the "layers" of the lead are doublings:
| Part | Layers and their jobs | Label |
|---|---|---|
| **Lead (violin)** | alone for the tune; at climaxes doubled in thirds, sixths or octaves by a second violin, by its own double stops, or shadowed by cimbalom or accordion; the bow noise is its "air", the body modes at 275 and 470-540 Hz its warmth (docs/MANUAL.md) | [H] from this brief's roles |
| **Afterbeat (țiitură)** | guitar chops as the dry, percussive mid layer; accordion or cimbalom can double the afterbeat for width and sustain | [S] this brief ("Instruments and roles") |
| **Bass** | one bass, roots and fifths on the beats: the only low instrument besides the drum | [S] this brief |
| **Drum (tobă)** | one player, two layers by construction: the boom (60 Hz head) and the cymbal on top; the snare drum or claps on the afterbeats add the crack | [S] this brief |
| **Dancers** | claps, snaps, shouts: the room | [S] this brief |

**EQ map** (starting ranges, all [H] applications of the cited general guidance; confirm on the engine's instruments):
| Instrument | High-pass | Cut / control | Emphasise | Source of the range |
|---|---|---|---|---|
| Violin | 180-200 Hz (its lowest note, G3, is 196 Hz) | 200-500 Hz only if boxy with the guitar; harshness somewhere in 1-4 kHz, narrow and small | 2-4 kHz so it leads; air above 10 kHz | iZotope EQ cheat sheet (orchestral strings); Beat Kitchen (violins roll off below about 200 Hz); [P] strings |
| Acoustic guitar (chops) | 100-120 Hz (docs/MANUAL.md) | 200-400 Hz mud | 1.5-2.5 kHz presence; 8-12 kHz air sparingly (the chop is percussion) | iZotope (acoustic guitar) |
| Bass guitar | 30-40 Hz | 300-500 Hz mud | 40-120 Hz low end; 800 Hz-1 kHz definition (the finger) | iZotope (bass guitar) |
| Tobă, boom | 30-40 Hz | 200-500 Hz boxiness | 60-80 Hz, 100-200 Hz knock | iZotope (kick) |
| Tobă, cymbal; hats | 150-500 Hz | about 4 kHz harshness | 8-12 kHz | iZotope (cymbals) |
| Snare drum (tobă mică) | 80-120 Hz | 300-700 Hz boxiness and ring | 150-250 Hz body, 2-3.5 kHz | iZotope (snare) |
| Cimbalom | 100-150 Hz | 200-400 Hz | 2-5 kHz hammer, 8-12 kHz | iZotope (piano, acoustic guitar), applied |
| Accordion | 100-150 Hz | 300-600 Hz; reediness at 1-3 kHz against the violin | 1-3 kHz when it leads | [P] pads and strings, applied |
| Claps, snaps | 200-300 Hz | 400-800 Hz | 1-2 kHz snap, 2-8 kHz | docs/TRANCE.md "Claps" |
| Voice (shouts, a refrain) | this brief, "Mixing the voice" | | | |
| Reverb return (the plate the lăutari ask for) | 200-500 Hz | 300-600 Hz | low-pass at 6-12 kHz | [P]; Houghton, Sound On Sound 2022 |

**Glue** [H]: one shared short room or plate for the whole band, sent from every instrument in different amounts, is what makes five dry sources one band; a gentle mix-bus compressor (2:1, 1-2 dB: Beat Kitchen) at most.

**Where Spectre stands** [M] (session 010's project): violin, guitar, bass, tobă (four strokes), snare, snaps and claps, one track each; the layering is in the writing (double stops, the two motifs fusing). No stem analysis was run on 010 for this brief; run the clarity analysis proposed in PRODUCTION.md before any remix.

## Era assessment of the master target (2026-11-25)
**What the current target is.** `joc` reuses the `rock` curve (Pestana et al. 2013, pop and rock number-one singles 1950-2010) at `eq` 0.7 and -11 LUFS: a stand-in, never measured on lăutar music.

**Measured** [M] (method, validation and limits in docs/TRANCE.md, section C; AcousticBrainz Bark-band data, medians, dB relative to each track's level at 510 Hz-2 kHz). Two yardsticks: the broad MusicBrainz tags `folk`, `balkan`, `romanian folk` (2,084 tracks 1995-2017, mostly not Romanian), and **100 recordings by Taraf de Haïdouks** (releases 1992-2007), the string taraf this brief already uses as its reference. For contrast, 125 recordings by Fanfare Ciocărlia (brass) and 44 by Mahala Raï Banda (a modern amplified band).
| Band (Hz, as analysed) | `folk` tags 2010-14 | Taraf de Haïdouks | Fanfare Ciocărlia | Mahala Raï Banda | `rock` curve | 010 Unison |
|---|---|---|---|---|---|---|
| 32-97 (bass, drum) | +5.6 | +7.9 | +7.9 | +9.7 | +6.2 | +7.6 |
| 97-140 | +4.5 | +5.8 | +4.9 | +6.3 | +9.1 | +8.8 |
| 140-183 | +3.8 | +2.4 | +2.4 | +3.9 | +8.2 | +6.4 |
| 183-291 | +7.5 | +5.2 | +5.6 | +6.0 | +9.2 | +10.0 |
| 5300-6400 | -11.8 | -11.8 | -8.3 | -5.7 | -7.3 | -9.5 |
| 7700-9500 | -11.9 | -17.7 | -10.3 | -6.9 | -9.8 | -13.5 |
| 9500-12000 | -13.8 | -20.3 | -12.6 | -9.1 | -12.3 | -17.6 |
| 12000-15500 | -17.9 | -20.8 | -16.2 | -10.9 | -16.6 | -22.6 |

- Estimated loudness of the Taraf recordings: median -13.2 LUFS (middle half -15.5 to -12.1), a little quieter than the -11 this brief uses.
- **The curve against the taraf:** `rock` asks for 3-6 dB more at 97-291 Hz and 4.5-8 dB more from 5.3 to 12 kHz than Taraf de Haïdouks' records have. An acoustic string band is leaner in the low mids and much darker on top than pop rock. Against a modern amplified band (Mahala Raï Banda) the same curve is 1.5-6 dB too *dark*: the two lăutar worlds are 9-11 dB apart above 7.7 kHz, which is the "cold" acoustic sound against the amplified one, in numbers.
- **010 Unison** follows the curve in the low mids (3-5 dB over the taraf at 97-291 Hz) and sits between the taraf and the folk tag on top: 2-6 dB brighter than Taraf de Haïdouks from 2 to 9.5 kHz, 1.6-4.7 dB darker than the `folk` tags above 7.7 kHz. For the dry acoustic reading the brief chose, its top is in the right place; its low mids are the borrowed curve's.
- **A current target.** *Interim* [M, fitted to the 100 Taraf recordings as in TRANCE.md C; not adopted]: 31.5 Hz -16.5, 40 -12, 50 -6, 63 -0.5, 80 +3, 100 +4, 125 +2, 160 +0.5, 200 0, 250 +1.5, 315 +1.5, 400 +2, 500 +2, 630 +2, 800 +1.5, 1k 0, 1.25k -1, 1.6k -1.5, 2k -3, 2.5k -4, 3.15k -6, 4k -8.5, 5k -11, 6.3k -13.5, 8k -17.5, 10k -20.5, 12.5k -21.5, 16k -28.5 (dB re 1 kHz). One band's records from 1992-2007, and the lăutar recordings as a set spread widely on top (middle half 8-11 dB wide above 6.4 kHz): use it lightly (`eq` 0.3-0.4 [H]) or only as a check. *Definitive:* the owner chooses which lăutar sound is meant (the acoustic taraf or today's wedding bands) and 20-30 recordings of it are measured locally (PRODUCTION.md "Era-appropriate targets").

Sources for these two sections: iZotope, EQ cheat sheet: https://izotope.com/en/learn/eq-cheat-sheet ; M. Houghton, How to achieve better separation in your mixes, Sound On Sound (2022): https://www.soundonsound.com/techniques/how-achieve-better-separation-your-mixes ; M. Senior, Q. What should I EQ to improve my muddy mixes?, Sound On Sound (2008): https://www.soundonsound.com/sound-advice/q-what-should-eq-improve-my-muddy-mixes ; a professional trance producer's EQ map (2026; docs/TRANCE.md); MusicBrainz search API and AcousticBrainz low-level data (CC0; https://acousticbrainz.org/), measured 2026-11-25; everything else in docs/PRODUCTION.md "Sources". Also: Thinkspace Education, Great mixing advice can ruin your orchestral mix: https://thinkspace.ac.uk/blog/great-mixing-advice-can-ruin-your-orchestral-mix/ ; Beat Kitchen, Orchestral mixing: https://beatkitchen.io/guides/orchestral/11-orchestral-mixing/

## Sources
- Wikipedia, "Romanian folk violin": https://en.wikipedia.org/wiki/Romanian_folk_violin (read via the mirror https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Romanian_folk_violin)
- Wikipedia, "Lăutărească music": https://en.wikipedia.org/wiki/L%C4%83ut%C4%83reasc%C4%83_music (mirror: https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/L%C4%83ut%C4%83reasc%C4%83_music)
- Wikipedia, "Gypsy style": https://en.wikipedia.org/wiki/Gypsy_style
- Wikipedia, "Cobza": https://en.wikipedia.org/wiki/Cobza
- M. H. Beissinger, "Romani (Gypsy) Music-Making at Weddings in Post-Communist Romania", Folklorica 2007: https://journals.ku.edu/folklorica/article/view/3757
- Hiebert & Beissinger, lăutari in the 20th century, Musicology Today 50: https://musicologytoday.ro/50/MT50studiesHiebertBeissinger.pdf
- "Lăutărie Then and Now", The Attic: https://theatticmag.com/features/2409/l%C4%83ut%C4%83rie-then-and-now%3A-inside-romania's-romani-musical-heritage.html
- RomArchive, "Manele": https://www.romarchive.eu/en/music/balkan/manele/
- "Dans Țigănesc Rar, Dans Țigănesc Repede" (dance notes, Muntenia): https://socalfolkdance.org/dances/D/Dans_Tiganesc_Rar-Dans_Tignanesc_Repede.pdf
- Hungaricana / ZTI folk music archive, "joc ţigănesc", Ördöngösfüzes 1972: https://zti.hungaricana.hu/en/82189
- BabaYaga Music, Romanian music (primaș, contra, bowing): https://www.babayagamusic.com/Music/romanian-music.htm
- eliznik, Romanian percussion: https://eliznik.org.uk/traditions-in-romania/traditional-music/percussion/
- Types of ornaments in traditional instrumental music (abstract): https://doaj.org/article/dc854ca39618413bb55220b1448e4ba0
- R. Timmers & P. Desain, "Vibrato: questions and answers from musicians and science" (2003): https://www.mcg.uva.nl/mmm-2003/papers/mmm-35/mmm-35.html
- AcousticBrainz (Taraf de Haïdouks, length and estimated tempo): https://acousticbrainz.org/14c059d4-b4ff-4072-b80e-cf2ea445dfcc (A la Turk), https://acousticbrainz.org/784f3c92-fb0f-45ce-a71b-47453ccbb375 (Turceasca a lu Kalo), https://acousticbrainz.org/c2258465-e8f4-450f-89c2-6f0854a07fe2 (Leliță cîrciumăreasă), https://acousticbrainz.org/5054d66c-9bb2-413d-aaf5-9e3877b3f7c8 (Turceasca), https://acousticbrainz.org/4ae7b894-a617-44ec-a017-0b1a47325f59 (Sîrba), https://acousticbrainz.org/5871fb81-9c68-4f38-908c-c22dfc6d9e86 (Tot taraful), https://acousticbrainz.org/05708f12-d794-45f4-9249-564f22a4ff00 (Azi eram frumoasă jună)
- Mastering: Sage Audio, https://www.sageaudio.com/articles/mastering-for-folk-music ; RoEx, https://www.roexaudio.com/blog/what-lufs-should-i-master-at ; iZotope 2024, https://www.izotope.com/en/learn/mastering-trends ; Pestana et al. 2013, https://joshreiss.github.io/documents/2013/Pestana%20Ma%20Reiss%20-%20AES135.pdf
- Violin acoustics (engine): J. Woodhouse, "The acoustics of the violin: a review", Rep. Prog. Phys. 2014: https://core.ac.uk/download/42337723.pdf (Helmholtz motion, the friction-curve bowed-string model, the Schelleng force limits, flattening); C. Gough, violin modes, Acoustics Today: https://acousticstoday.org/supplementary-text-violinacoustics-colin-e-gough/ (A0 below the 300 Hz Helmholtz frequency, the breathing mode B1 at about 430-560 Hz with the sound post); the bridge "typically has strong resonances around 3000 and 6000 Hz": https://caml.music.mcgill.ca/~gary/618/week5/node4.html ; the waveguide follows Smith's bowed string as implemented in the STK `Bowed` class (Cook & Scavone).
- The reference score: "Joc țigănesc - Tutorial", arranged by ViolinSAcademy (MusicXML, supplied for style only; not in the repo, not to be copied).
