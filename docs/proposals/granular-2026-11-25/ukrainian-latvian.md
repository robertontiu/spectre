# Proposal: Ukrainian and Latvian folk (sessions 005, 006) brought up to PRODUCTION.md section 5, item 10

From the genre research agent (folk side), 2026-11-25. The research itself is in `docs/UKRAINIAN.md` and `docs/LATVIAN.md`, new sections "Granularity: ..." (uncommitted edits in the working tree; nothing committed or pushed). This file holds only the changes to shared files, for the orchestrator to merge.

## 1. docs/LESSONS.md ("Across genres", the "Shared modes" bullet)
Current text says Ukrainian Dorian, Romanian minor and Misheberak are the same Dorian #4. Add one clause:
> The Hutsul mode of the Ukrainian Carpathians is not that mode: it raises the 7th as well (1 2 b3 #4 5 6 7; Grove, "Ukraine", part II §3). The augmented second is a Carpathian and duma colour, not a pan-Ukrainian one: Ukrainian ritual songs are narrow and diatonic.

And one new bullet (folk part-singing, applies to Ukrainian, Latvian and any Slavic/Baltic brief):
> **Village part-singing closes to one pitch.** Ukrainian and Latvian ensembles split into seconds and thirds (heterophony), hold a sung drone, or put a solo high voice over a group "bass", and end each stanza in unison or at the octave. Stacked open fifths and fourths are not the documented texture (docs/UKRAINIAN.md and docs/LATVIAN.md, "Granularity").

## 2. docs/ORCHESTRATION.md, "Genre conventions"
There is no own row for these culture briefs: folk-fusion trap sits in the "Hip hop / beats" row. Add to that row's brief column (after "folk-fusion trap"): "; culture briefs for the folk side: docs/ROMANIAN.md, docs/UKRAINIAN.md, docs/LATVIAN.md ('Granularity')", and add this note under the table: "Folk side by region, genre layer and era: docs/UKRAINIAN.md / docs/LATVIAN.md 'Granularity'. The brief names its region (UA: Polissia, Middle Dnipro/Poltava, left bank and Slobozhanshchyna, steppe south and Cossack song, Podillia, Carpathians (Hutsul, Boyko, Lemko, Bukovina), or kobzar/lirnyk; LV: south-west Kurzeme and the Suiti, north Latgale, south-east Latgale and Sēlija, Vidzeme and north Kurzeme), its layer (UA: ritual or lyric; LV: recited or sung) and its era; without them it takes the current-practice checklist."

## 3. docs/PRODUCTION.md, section 6 "Gaps and proposals" (engine and voices)
Instruments missing for both traditions (ranked by how often the sources name them for current practice [H]):
1. **Jew's harp** (drymba / vargans): named for Hutsul shepherd music, DakhaBrakha, Latvian instruments. Not in the engine at all.
2. **Accordion / bayan**: the third member of troisti muzyky and "the main instrument used for traditional dance music" in late-20th-century Latvia (Muktupāvels 1998); DakhaBrakha.
3. **Bandura** (many treble strings plucked with the nails): ONUKA, the kobzar tradition; today approximated with `cimbalom`/`pluck`/`oud`.
4. **Sopilka with an overblown register, and telenka** (hole-less overtone flute): Go_A, Kalush; today `nai`/`ney`.
5. **Frame drum with jingles** (buben, bubins, sietiņš) and **tree-trunk / big folk drums** (Auļi).
6. **Second kokle type**: a `type` switch for the small Kurzeme kokle (5-9 strings, lap) and the larger Latgale kokle (up to 12, upright).
7. **Ģīga** (bowed zither), mandolin, clarinet (Tautumeitas' band).
8. **Heterophony helper** [H]: generate two or three sung lines from one melody that split by seconds and thirds and close to unison or the octave at the stanza end (Skazhenyk & Di Virgilio 2024). Today written by hand as separate `vox2`/`choir` tracks.
9. **Odd metres**: a pattern bar is always four beats (MANUAL "Other meters"); Latvian sung songs with 5/8, 5/4 and 7/8 bars and Ukrainian long songs with frequent metre changes need bars of other lengths.

Voices (docs/voice/VOICES.md "What is missing"): no DiffSinger bank sings Ukrainian or Latvian; no hard, chest-register "white" voice; no penetrating high solo folk voice (the Latgalian "half part", the Ukrainian head-voice "thin" solo); no male bass for Cossack songs. **Licence flag:** the Lotte V voices forbid political use; anti-war (005) and revolution (006) briefs should not use them for words without the owner's decision.

## 4. Mastering: engine/genres.json, engine/targets.json, docs/MASTERING.md "Era targets", data/catalogue_references.json
Measured with `tools/refcurve.py catalogue` (always under `flock /tmp/spectre-musicbrainz.lock`), 2026-11-25. Curve files (aggregates and title lists only) in `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/ukrainian-latvian-curves/`:

| file | artists (MusicBrainz MBID) | n, years | est. LUFS (middle half) | finding |
|---|---|---|---|---|
| `ua_electrofolk.json` | Go_A 80b54212-19f5-42ce-bfd7-e08db9c298ae, Onuka fbe2ebe7-30b3-4efe-af11-e0563bb8744a, Alina Pash 95593341-529e-40e3-ad57-4622f2aacdf8, KALUSH 628d9735-f961-4eb0-92ee-31d77f9c8b8f, Kalush Orchestra 45d9e75f-cbdf-47df-b4e6-1578d8a17e25 (Kalush: no AcousticBrainz data) | 23 (Onuka 12, Go_A 7), 2014-2022 | -9.9 (-10.3 to -8.8) | `hiphop_2015` read through Bark is within 3.5 dB everywhere (mean 1.3): **no separate target** |
| `ua_dakhabrakha.json` | DakhaBrakha 208334a1-abf0-4791-9705-b45838244b29, --limit 300 | 48, 2007-2021 | -11.8 (-13.2 to -10.3) | 6-7.4 dB darker than `hiphop_2015` at 6.4-12 kHz, 3.7 dB less at 32-97 Hz: **a real difference** for acoustic ethno-fusion briefs |
| `lv_folk_nometal.json` | Tautumeitas 3a3b9876-a3a7-4689-bcbc-bba79f86f910, Auļi 6dcf4734-69fc-48b1-b239-00c2a0c68a1b (also queried, no data: Iļģi, Saucējas, Raxtu Raxti, Laimas muzykanti, Alsungas Suitu Sievas, Laima Jansone) | 26, 2005-2020 | -11.8 (-12.9 to -10.6) | 4-5 dB darker than `hiphop_2015` above 6 kHz, 2 dB less at 183-400 Hz, 3.4 dB less at 32-97 Hz: **a difference** for band-led folk-pop briefs |
| `lv_folkfusion_with_metal.json` | the Latvian set plus Skyforger | 80 (54 Skyforger), 1998-2020 | -10.1 | metal-dominated: **do not add** |
| `ukr_folkfusion_all.json` | the Ukrainian sets pooled (Dakh Daughters, Mavka included; 13 tracks credited to "Crossworlds" entered through the artist query) | 73, 2007-2022 | -11.8 | pooled, DakhaBrakha-dominated: **do not add** |

Lossless share 4-17%, so the top bands read low in all sets (the same holds for `hiphop_2015`, so the comparison is fair, but the absolute top is uncertain). True peak, PLR, LRA, width and low-end mono are not in the catalogue data: no proposal for them (house -1 dBTP and `mono_below` 120 stay).

Proposed changes:
1. **engine/targets.json** (via `python3 tools/refcurve.py add <file> --note ...`): add `ua_dakhabrakha` and `lv_folk_nometal` as **stop-gap, thin** curves (note: "n 48 / 26, one or two acts, AcousticBrainz ≤2022, low lossless share; for briefs naming acoustic Ukrainian ethno-fusion / Latvian band-led folk-pop, not for folk-fusion trap"). Do **not** add `ua_electrofolk` (it matches `hiphop_2015`).
2. **engine/genres.json**: no new genre. In `hiphop` (and the `trap` entry's name, which already lists "folk-fusion trap"), add a `subdivisions` note: "Ukrainian and Latvian folk-fusion trap: this configuration (measured: Ukrainian electro-folk 2014-2022, n 23, within 3.5 dB of hiphop_2015, est. -9.9 LUFS); acoustic Ukrainian ethno-fusion: `--target ua_dakhabrakha --lufs -12 --eq 0.4`; Latvian band-led folk-pop: `--target lv_folk_nometal --lufs -12 --eq 0.4` (stop-gaps; docs/UKRAINIAN.md, docs/LATVIAN.md 'Mastering per subdivision'). eq 0.4 follows the joc and chamber-score practice for acoustic sets; -12 rounds the measured -11.8 [H]."
3. **docs/MASTERING.md "Era targets"**: if (1) is merged, add the two columns to the curves table with provenance rows (artists, n, years, method as above) and the label "stop-gap, thin".
4. **data/catalogue_references.json**: add the artist MBID lists above under `ukrainian_folk` and `latvian_folk` so `catalogue_stats.py targets` can rebuild them.
5. Nothing measured for village/archive recordings, Soviet ensemble releases or Latvian choir releases: say "no data" (already in the genre docs).


## 5. Contradictions with existing docs (flagged; the research was followed)
- docs/UKRAINIAN.md "Instruments": white voice "with stacked open fifths and fourths"; "Modes": "parallel open fifths". Not supported by the polyphony sources (Skazhenyk & Di Virgilio 2024; Grove). Annotated in place, not deleted.
- docs/UKRAINIAN.md "Modes": "minor modes with augmented seconds are the most striking feature" of Ukrainian folk music. Grove: ritual songs narrow and diatonic, traditional music greatly influenced by the major-minor system; the augmented second is regional (Hutsul mode, duma mode). Qualified in place.
- docs/LATVIAN.md "Modes and rhythm": "Even metres (2/4, 3/4, 6/8)". Boiko 2025: solo sections of recited songs in strict, loose or free metre; MFS 495 notes: shifting metres (5/8, 5/4, 7/8, 2/4+3/4) common in sung songs. Qualified in place.
- docs/LATVIAN.md "No augmented seconds": mostly right; an augmented fourth and a diminished fourth are documented in archaic songs. Qualified in place.
