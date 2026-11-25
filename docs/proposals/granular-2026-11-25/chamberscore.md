# Proposal: chamber score (`chamberscore`) brought up to PRODUCTION.md section 5, item 10

From the genre research agent, 2026-11-25. The research itself is in `docs/CHAMBER_SCORE.md`, new section **"Granularity: idioms, eras, schools and the current practice"** (A-G), plus two corrected rows in "Configuration" (Tonal balance, Master: they still said `rock`) and one new "nearest wrong feeling" (the functional mood-playlist piano). Nothing below has been applied to the shared files; each item says where it goes.

Files next to this one (same folder):
- `chamberscore_piano.json`: the proposed curve (refcurve catalogue file, 13 releases, n 150, 2010-2019, with the title list).
- `chamberscore_film.json`: measured as a check, **not proposed** (27 score albums, n 423): within 1.5 dB of `chamberscore_ref` from 250 Hz to 12.5 kHz, so scores need no curve of their own.

## 1. engine/targets.json: add `chamberscore_piano`
```
flock /tmp/spectre-musicbrainz.lock python3 tools/refcurve.py add <proposals>/chamberscore_piano.json --note "felt / close-miked neo-classical piano, 2010-2019 (13 albums); docs/CHAMBER_SCORE.md Granularity F"
```
To rebuild it (from the cache; always with the flock):
```
flock /tmp/spectre-musicbrainz.lock python3 tools/refcurve.py catalogue --name chamberscore_piano \
  --release a0063e3a-15d8-4ed2-a481-60059480928b --release b0e16b9e-5853-4f8b-93ad-b4ddc1a958cf \
  --release 66c8a4e5-5bcd-43e7-a6a7-0a2dc56d2cc2 --release 365f338c-1771-49f2-b14a-9c96d0c59b7e \
  --release 9895b991-9318-4a02-9320-02eea0454cfd --release 56a15cf2-a435-48c9-8fdc-642e24aff561 \
  --release 617e7410-bddc-4a42-9599-88656061ad7a --release a0a0f5f7-1732-4b7e-a347-b8c42158ffff \
  --release 885f8562-cad2-4f1d-bba5-e85faca1d99d --release 3c08cf59-891f-4526-b00b-0aa7eaf25204 \
  --release f8fec791-eb15-4902-a2d3-5402649b6be5 --release e5da4a98-3fa9-4446-b674-0497ce05511b \
  --release 9a54c033-af59-436d-b3d7-77cd445e5ba0 --list-tracks --out <file>
```
Curve (dB re 1 kHz): 31.5 -16, 40 -11.5, 50 -7.5, 63 -3.5, 80 -0.5, 100 +2, 125 +4.5, 160 +6.5, 200 +8, 250 +8.5, 315 +9, 400 +8.5, 500 +7, 630 +5, 800 +3, 1k 0, 1.25k -3.5, 1.6k -6, 2k -10.5, 2.5k -15, 3.15k -20, 4k -24, 5k -28, 6.3k -31.5, 8k -34.5, 10k -37, 12.5k -39, 16k -40.5. Est. loudness -17.0 LUFS (-18.6 to -14.6); 79% lossless; fit residual max 0.6 dB. Spread (middle half) 12-15 dB at 3.15-6.3 kHz: a guard, so `eq` 0.3.
Against `chamberscore_ref`: -12 to -13.5 dB at 4-12.5 kHz, -5.5 to -11 dB at 2-3.15 kHz, +4 to +5.5 dB at 125-400 Hz.

## 2. engine/genres.json, `chamberscore`
Keep `master` as it is (`chamberscore_ref`, -15, eq 0.4, translate 0.2, mono_below 80): the 27 score albums agree with it (above). Add (field names are suggestions; whatever the engine reads):
```json
"subdivisions": {
  "default": "the blend (score frame, neo-classical piano at the centre): master as configured",
  "score": "animation / indie-film score of any school (Hollywood, European, Japanese), minimalist or game chamber that is not piano-led: master as configured; European, Japanese and game briefs --lufs -16",
  "piano": "felt / neo-classical piano strand: --target chamberscore_piano --lufs -16.5 --eq 0.3 (mono_below 60 only through a genres.json block such as master_piano: studio.py master has no --mono-below flag)",
  "trailer": "not this genre (a contrast): no target"
},
"master_piano": {"target": "chamberscore_piano", "lufs": -16.5, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 60.0}
```
- `status`: replace "the tonal target reuses the measured `rock` curve with a light EQ (no orchestral or acoustic curve is measured)" by a past-tense note; append "; 2026-11-25: granularity research (strands, eras, schools; DC dynamics; `chamberscore_piano`)".
- `hand_tuned`: add "lufs -16.5 for the piano strand: its median (-17.0) nudged toward the 2015-21 modern-classical tag (-15.6)"; "eq 0.3 for chamberscore_piano: its spread is 12-15 dB at 3-6 kHz"; "mono_below 60 for the piano strand (a close pair puts the bass strings to one side: SOS piano guide)".
- `sources`: add "strands, eras, schools and dynamics: docs/CHAMBER_SCORE.md 'Granularity' (MusicBrainz + AcousticBrainz, 2026-11-25: 27 score albums, 13 felt-piano albums, 4 minimalist, 7 game, 6 trailer albums; tags soundtrack, modern classical, video game music, trailer music, pop rock); Essentia DynamicComplexity".

## 3. data/catalogue_references.json, `albums.chamberscore`
Add these 37 releases (strand labels as given):
- strand `score` (11): Desplat *The Grand Budapest Hotel* 492f34de-755a-49e9-89eb-7c9de9fbd844, *Isle of Dogs* 15619ae3-b7e3-4e4c-9800-ab84ab6a0c8b, *Little Women* 2f4f461b-46b2-4179-8eb0-d814b7baac63, *The Shape of Water* 57b8051f-04b6-4cd4-9144-4b71b598c284, *The Curious Case of Benjamin Button* 0f22b36d-2ba9-4396-99a9-ff263186bfe2; Giacchino *Jojo Rabbit* 2df0a330-8c9f-46bf-a2d3-dbb862e65ae9; Newman *Finding Dory* 0aeed865-d471-43db-af50-758cf3fbab97; Hisaishi *The Wind Rises* d4db7c8a-6d29-40e4-8a0f-b8174b09a5c9, *The Tale of the Princess Kaguya* b8b8583e-14ba-4acc-b770-555aca83644f, *Ponyo* 49d486d0-7209-43cb-ba21-dc732e405ee5; Marianelli *Paddington 2* 3535bf71-1b2b-4955-9122-0d1a142e43d1.
- strand `felt-piano` (9 new + the 4 post-2010 neo-classical already listed): Frahm *Screws* 9895b991-9318-4a02-9320-02eea0454cfd; Arnalds *Living Room Songs* 56a15cf2-a435-48c9-8fdc-642e24aff561, *re:member* 617e7410-bddc-4a42-9599-88656061ad7a; Beving *Prehension* a0a0f5f7-1732-4b7e-a347-b8c42158ffff; Hania Rani *Esja* 885f8562-cad2-4f1d-bba5-e85faca1d99d; Albanese *The Blue Hour* 3c08cf59-891f-4526-b00b-0aa7eaf25204; Lambert *Sweet Apocalypse* f8fec791-eb15-4902-a2d3-5402649b6be5; Einaudi *Elements* e5da4a98-3fa9-4446-b674-0497ce05511b; Goldmund *Sometimes* 9a54c033-af59-436d-b3d7-77cd445e5ba0.
- strand `minimalist-score` (4): Glass *The Hours* ffe351a7-4a05-4575-b450-fba900424efe; Newman *American Beauty* ef6ce4ab-c0ff-4249-9a5b-db616c290a16; Jóhannsson *The Theory of Everything* 517ceef8-ccf2-4aad-a2a0-10a87a0a7206; Mansell *The Fountain* 33abead4-3015-438f-9ea3-97f2cc5cb278.
- strand `game` (7): Wintory *Journey* da883948-946a-4e11-9001-ca6e41b07bde; Larkin *Hollow Knight* 085d63c1-d39f-4943-a6e5-704ce896f8a0; C418 *Minecraft - Volume Alpha* 5e396e48-5bc1-4d28-ab34-ee77dc534fed; Berlinist *GRIS* 04c11071-1147-4076-ab78-4ae784cbff2b; Coker *Ori and the Blind Forest* 17eeae4b-5e4e-4170-944c-9a4066d8591a; ConcernedApe *Stardew Valley* 6c730c73-ca63-4673-85b7-22f570ad25d0; Santaolalla *The Last of Us* 2d6fb74b-e5e5-4e1f-96fa-f42b00392d28.
- strand `trailer` (6, contrast): Two Steps From Hell *Invincible* 95fdd1aa-725a-4bc8-b050-613dbd2b5c00, *Archangel* 7cdf6a6f-8677-4598-a475-a8aa2d8bfe43, *Battlecry* 49eb94a3-e012-4e4d-93e4-55fa8979fd71; Bergersen *Sun* eec1c2f2-1a7f-41f9-9b7d-a453c8b0ed8f; Audiomachine *Phenomena* 1aca18e0-3470-468d-9019-8040d7234fc3; Zimmer *Inception* 472cb359-003e-4045-8602-a1804c427a49.
- a `school` field per score album: Hollywood = Up, Ratatouille, Finding Nemo, WALL·E, Big Fish, Eternal Sunshine, The Royal Tenenbaums, Jojo Rabbit, Finding Dory; European = Amélie, Moonrise Kingdom, Fantastic Mr. Fox, Chocolat, A Little Princess, Grand Budapest, Isle of Dogs, Little Women, Shape of Water, Paddington 2, Benjamin Button; Japanese = Totoro, Kiki, Kikujiro, Spirited Away, The Wind Rises, Kaguya, Ponyo.
- `targets`: add the `chamberscore_piano` command above (so `catalogue_stats.py targets` rebuilds it).
- Caution: these new strands would change the strand summaries `catalogue_stats.py albums chamberscore` prints, and the 30-album pool behind `chamberscore_ref`, if the tool pools every listed release. Either give the new entries a flag (e.g. `"pool": false`) or keep them in a second list (`albums.chamberscore_granularity`); `chamberscore_ref` must keep its 30 releases.

## 4. docs/MASTERING.md
- "Era targets": a row for `chamberscore_piano` in the provenance table ("13 felt / close-miked neo-classical piano albums, 2010-2019 | 150 | -17.0 (-18.6 to -14.6) | `chamberscore_ref`: -12 to -13.5 dB at 4-12.5 kHz, +4 to +5.5 dB at 125-400 Hz") and a column in the curve table (values in 1).
- A sentence in the genre-settings table row for `chamberscore`: "piano strand: `--target chamberscore_piano --lufs -16.5 --eq 0.3`".
- "Loudness" (new, cross-genre and sourced): **with streaming normalization the playback level of a dynamic master is set by its PLR, not by its integrated loudness**: Spotify raises a quiet master only until its true peak reaches -1 dBTP (its own example: -20 LUFS with -5 dBTP peaks is raised to -16), so a master of PLR *p* plays at most at -1 - *p* LUFS. For the acoustic genres (PLR 12-16) this means -13 to -17 in a playlist whatever the integrated target; a louder target only adds limiting. (https://support.spotify.com/artists/article/loudness-normalization/)
- "Dynamics" (new, measured): Essentia dynamic complexity (DC) on AcousticBrainz, 2026-11-25: pop rock 2015-21 3.6 (238 tracks); trailer albums 5.1, `trailer music`/`epic music` tag 4.8; video-game tag 4.6; chamber idioms 5.6-6.8 (score albums 6.6, European school 5.9, felt piano 6.8, game chamber 5.6); neo-classical before 2010 7.5. 015 *Again, Again* master v030 measured DC 3.96 (Essentia 2.1-b6; AcousticBrainz ran 2.1-beta2), PLR 13.9, LRA 8.2. Proposed QC check for the acoustic genres: DC (or LRA) reported next to PLR, with a warning when a chamber or caroling master falls below about 5 [H threshold from the medians].

## 5. Engine (docs/PRODUCTION.md section 6, "Engine", a new item; engine/master.py)
- **A dynamic-master path.** `master()` always applies the 2:1 glue (1-2 dB), the multiband and the soft clipper. Chamber sources ask for "about .5 to 1dB of steady compression", "little limiting" (Sage Audio) and "mild peak-limiting" on a score album (SOS, *Encanto* 2022). Proposal: per-genre `glue` (on / light / off) and `clip` (on / off) settings in genres.json, `chamberscore` and `caroling` set to light glue and no clipper, the report printing DC or LRA. Effect expected [H]: more loudness movement (015 DC 3.96 against 5.6-6.8 in the genre), most of which must still come from the arrangement.
- **Contradiction:** `engine/chamber.py`'s module docstring lists `toy_piano` ("struck steel rods: bright, short, slightly out of tune"), but no `toy_piano` function exists and HANDOFF section 6 says there is none. Either build it or drop the line.
- Instruments the strands ask for that the engine lacks (adds to HANDOFF section 6): marimba (Newman, *Flow*), harp, accordion / harmonium / melodica (European school, Bertelmann), mandolin, recorder, piano mechanism noise (hammer, damper, pedal, bench), plus the known brass, orchestral woodwinds, toy piano, double bass, the piano's top end.

## 6. docs/PRODUCTION.md
- Section 3, the "Where each master target comes from today" table still lists `chamberscore` as "`rock` reused, eq 0.4, none of its own". Since 2026-11-25 it is `chamberscore_ref` (and `caroling_ref`, `latinpop_ref`, `joc_taraf` for the others): **contradiction with docs/MASTERING.md and engine/genres.json**; update the row (and the others if the orchestrator agrees).
- Section 5 item 10: nothing to change; this genre is the first acoustic example where the split is by idiom more than by era (the piano strand vs the score strand: 12-13 dB at 4-12 kHz, while the score timeline moved less than 2.5 dB in any band on the tag).

## 7. docs/HANDOFF.md section 6 (not on the no-edit list, but shared; left for the orchestrator)
- "master curves borrowed from rock for caroling, joc, Latin pop and chamber score (no measured choral, folk, Latin or orchestral curve)" is out of date since the era targets of 2026-11-25.

## 8. docs/ORCHESTRATION.md, "Genre conventions"
- A chamber-score brief names its strand: the blend (default), a score idiom (and optionally a school: Hollywood, European, Japanese), the felt-piano strand, a minimalist cue or a game-style piece; "newest sound" takes CHAMBER_SCORE.md "Granularity" G. Trailer-hybrid is not this genre.

## 9. docs/LESSONS.md (one lesson, to the orchestrator's judgement)
- "015 *Again, Again*: peaks fine (PLR 13.9) but its loudness moved like a pop record (Essentia dynamic complexity 3.96; chamber records 5.6-6.8, pop rock 3.6). In the acoustic genres, keep the quiet passages quiet in the arrangement and don't let the master ride them up."

## What could not be sourced or measured
A tempo census per strand; PLR, LRA and true peak of commercial score and piano albums (AcousticBrainz has no peak data; DC stands in); anything after 2022 (2024-26 is extrapolated or sourced qualitatively); a multitrack census of a Hisaishi or Desplat cue; recording-room practice outside Hollywood; a primary source for trailer-music loudness (only the catalogue measurement: -11.4 LUFS, 6 albums, and forum talk); the Japanese school rests on one composer (Hisaishi, 7 albums).
