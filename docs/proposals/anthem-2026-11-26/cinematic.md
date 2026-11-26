# Proposal: the `cinematic` genre (cinematic hybrid / epic), queue 13

Research: docs/CINEMATIC_HYBRID.md (2026-11-26). Nothing here is applied: genres.json, targets.json, eqmaps.json, catalogue_references.json, ORCHESTRATION.md and MASTERING.md are shared files being edited by other agents. Apply in this order, then commit by path.

Files in this folder:
- `cinematic_2012.json`, `cinematic_2019.json`, `cinematic_choir.json`, `cinematic_film.json`: curve files from `tools/refcurve.py catalogue ... --out` (**proposed targets**).
- `cinematic_sounddesign.json`, `cinematic_pop.json`, `cinematic_game.json`, `cinematic_sports.json`: measured, **not proposed** (lossy-only or thin; reported in the doc).
- `catalogue_references_additions.json`: the album list (94 releases by strand, MBIDs) and the four target specs.

## 1. Targets (engine/targets.json)
```bash
for c in cinematic_2012 cinematic_2019 cinematic_choir cinematic_film; do
  python3 tools/refcurve.py add <this folder>/$c.json
done
```
Notes to pass with `--note` (optional):
- `cinematic_2012`: "trailer-house albums 2012-2021 (Two Steps From Hell, Audiomachine, Really Slow Motion, Ivan Torrent, Fired Earth, Bergersen), 21 albums with data, 454 tracks; docs/CINEMATIC_HYBRID.md"
- `cinematic_2019`: "trailer albums 2019-2021, 4 albums with data, 58 tracks: thin; 2022-2026 extrapolated"
- `cinematic_choir`: "epic-choir era albums 2001-2011, 14 albums with data, 273 tracks"
- `cinematic_film`: "hybrid film-score albums 2010-2021 (Inception, The Dark Knight Rises, Interstellar, Fury Road, Batman v Superman, Dunkirk, Tenet), 108 tracks"

Rebuild note: the curves were made with `--min-length 60`; `catalogue_stats.py targets` passes `--min-length 30` for album lists, so a rebuild takes in a few more short cues (mostly in the choir and sound-design sets). Check with `refcurve.py check` after a rebuild; expected within 0.5 dB.

## 2. engine/genres.json: new entry `cinematic`
```json
"cinematic": {
  "name": "Cinematic hybrid / epic (trailer-style orchestral-electronic music), modern era (2012-2026)",
  "doc": "docs/CINEMATIC_HYBRID.md",
  "status": "researched 2026-11-26 (queue item 13); targets measured from the open catalogue (album lists by strand and era); album dynamics from the Dynamic Range Database; loudness untested in the engine; needs brass, orchestral percussion and a contrabass section before the first session (docs/CINEMATIC_HYBRID.md 'Engine mapping')",
  "master": {
    "target": "cinematic_2012",
    "lufs": -12.0,
    "tp": -1.0,
    "eq": 0.6,
    "translate": 0.3,
    "mono_below": 120.0,
    "dynamics": "normal"
  },
  "target_source": "21 MusicBrainz releases of trailer houses 2012-2021 (Two Steps From Hell, Audiomachine, Really Slow Motion, Ivan Torrent, Fired Earth Music, Thomas Bergersen); AcousticBrainz low-level Bark bands (CC0)",
  "target_era": "2012-2021",
  "target_tracks": 454,
  "target_method": "catalogue (tools/refcurve.py; docs/MASTERING.md 'Era targets'); --min-length 60",
  "target_date": "2026-11-26",
  "era_targets": {
    "2012-2021, hybrid trailer albums (default)": "cinematic_2012",
    "2019-2026, the newest sound (measured 2019-2021, 58 tracks: thin; 1.5-2.3 dB darker above 8 kHz; 2022-2026 extrapolated)": "cinematic_2019",
    "2001-2011, the epic-choir era (273 tracks; within 1.5 dB of cinematic_2012)": "cinematic_choir",
    "note": "the master uses `target`; a brief aimed at an era or strand passes `--strand` (docs/CINEMATIC_HYBRID.md 'Mastering per subdivision')"
  },
  "master_by_strand": {
    "note": "trailer-house albums are heavily limited in every era (album DR 4-6, 2007-2026; Dynamic Range Database) at whole-track est. -12 to -12.5 LUFS; hybrid film-score albums are 3 dB quieter and dynamic (est. -15.2, DR 7-12). Read the loudest section after mastering: the derived norm is about -8 to -6.5 LUFS short-term for the trailer strands. None of these levels has been tested in the engine",
    "default": {"label": "hybrid orchestral-electronic, modern (2012-2026)", "note": "the genre's master"},
    "newest": {"label": "newest sound (2019-2026)", "target": "cinematic_2019", "lufs": -12.0, "tp": -1.0, "note": "thin: 58 tracks"},
    "choir": {"label": "epic orchestral with choir (the 2000s template)", "target": "cinematic_choir", "lufs": -12.0, "tp": -1.0},
    "score": {"label": "hybrid film score or pulse score (album)", "target": "cinematic_film", "lufs": -14.5, "tp": -1.0, "eq": 0.5, "translate": 0.2, "mono_below": 80.0, "dynamics": "keep", "note": "108 tracks, est. -15.2 LUFS, DR 7-12; the dynamic path as chamber score"},
    "sounddesign": {"label": "sound-design trailer (pulses, hits, silences)", "lufs": -11.5, "tp": -1.0, "note": "its own set is lossy-only and thin (34 tracks, est. -11.1): the default curve is used"},
    "pop": {"label": "cinematic pop / rock anthem", "lufs": -10.5, "tp": -1.0, "note": "thin (20 tracks, est. -10.6; Imagine Dragons album DR 4-6)"},
    "anthem": {"label": "a long quiet first act before a full climax (queue 13)", "lufs": -12.5, "tp": -1.0, "note": "check that the final act reaches about -8 to -7 LUFS short-term; lower --lufs rather than crush the climax"},
    "sports": {"label": "sports and broadcast themes (a contrast, not a strand to make)", "valid": false, "note": "no target; one library album measured (-12.3, 70% major)"}
  },
  "length": "3:00-4:30; a standalone narrative track 3:40-4:20, aim about 4:00 (measured: trailer-house albums 2012-18 median 3:03, middle half 2:32-3:47; 2019-21 3:57 (thin); epic-choir albums 2001-11 2:53; sound-design library cues 2:22; hybrid film-score albums 4:02 (2010-16) and 4:48 (2017-21))",
  "form": "three acts: a sparse setup that may state the theme, a build of rising rhythm and density (a pulse or ostinato climbing a layer every 4-8 bars), a climax at full scale; hard boundaries (a hit, a cut, a bar of silence); the lead-in to the climax nearly without bass; a final hit or held chord; for a standalone track a fourth part (a coda, the theme returning quietly)",
  "tempo": "90-130 bpm written in 4/4 (measured medians, Essentia folded 70-140: epic-choir albums 91, hybrid trailer albums 2012-18 105 (middle half 81-121), 2019-21 about 120 (thin), hybrid film scores 96-100, game scores 92); the felt pulse is often half the written one under 16th-note ostinati",
  "meter": "4/4 (6/8 or 12/8 for galloping cues); ostinati in 8ths and 16ths, big drums on a slower grid, hits on the downbeats of act changes",
  "change_rate": "a new layer or rhythm level every 4-8 bars inside an act; a hard change at every act boundary",
  "role": "the theme is the lead and must be singable: first small (one instrument or voice), then everyone; percussion and ostinati carry the momentum; voices wordless, as instruments",
  "hand_tuned": [
    "lufs -12 sits on the measured median (-12.3) but is untested in the engine; the strand levels -14.5 / -11.5 / -10.5 / -12.5 are choices on measured medians",
    "the loudest-section norm (-8 to -6.5 LUFS short-term) is derived from album DR, not measured",
    "eq 0.6",
    "translate 0.3",
    "mono_below 120 (80 for the score strand)",
    "the 4:00 aim and the change rate in bar counts"
  ],
  "sources": "docs/CINEMATIC_HYBRID.md 'Configuration', 'Catalogue measurements' and 'Mastering per subdivision' (catalogue lengths, tempo, keys, dynamic complexity, loudness and curves by Spectre from MusicBrainz + AcousticBrainz, 2026-11-26; Dynamic Range Database https://dr.loudness-war.info/ ; Sound On Sound library music part 7, Rare Form Audio, UJAM for the three acts; Synchtank/Trailaurality 2017 and Universal Production Music 2024 for trends; epicomposer 2026 for mixing; TASA, EBU R128, Spotify for playback)"
}
```

## 3. engine/eqmaps.json: new entry `cinematic` (optional; `listen --clarity --genre cinematic`)
Roles use the existing role names; `brass`, `taiko` and `perc` are new role names only if the engineering agent adds them to the role list (MANUAL "role"), otherwise map brass to `lead`/`support` and drums to `kick`/`snare`.
```json
"cinematic": {
  "source": "docs/CINEMATIC_HYBRID.md 'Layering and EQ carving': epicomposer 2026 (bass band 20-80 Hz, brass vs percussion, high-pass only where needed), docs/voice/MIXING.md (choir), the chamberscore, dubstep and hip-hop maps for the orchestral, sub and drum rows; points marked [H] in the doc; light moves, orchestration first",
  "tolerance_db": 8,
  "core": ["sub", "low-strings", "strings", "brass|lead", "choir"],
  "roles": {
    "sub": {"hp": [20, 25], "lp": [100, 120], "own": [[30, 60]]},
    "low-strings": {"hp": [30, 40], "cut": [[200, 400]], "own": [[60, 200]]},
    "strings": {"hp": [80, 150], "cut": [[1000, 4000]], "own": [[8000, 16000]]},
    "brass": {"hp": [60, 80], "cut": [[250, 500]], "own": [[500, 2000]]},
    "lead": {"hp": [150, 250], "cut": [[400, 800]], "own": [[1500, 4000]]},
    "choir": {"hp": [100, 200], "cut": [[200, 400]], "own": [[1000, 3000], [8000, 16000]]},
    "kick": {"hp": [25, 35], "cut": [[250, 500]], "own": [[50, 150], [2000, 5000]]},
    "snare": {"hp": [60, 100], "cut": [[300, 600]], "own": [[1000, 5000]]},
    "pad": {"hp": [150, 300], "cut": [[200, 500]], "own": [[1000, 3000]]},
    "return": {"hp": [200, 300], "lp": [6000, 10000], "cut": [[300, 600]]}
  }
}
```

## 4. data/catalogue_references.json
Merge `catalogue_references_additions.json`: `albums.cinematic` (94 releases with strand, artist, album, year, MBID and how many tracks have AcousticBrainz data) and `targets.cinematic_2012 / _2019 / _choir / _film` (album list + strands). Update `_about` and data/README.md: "cinematic (docs/CINEMATIC_HYBRID.md, 2026-11-26)".

## 5. docs/ORCHESTRATION.md, "Genre conventions"
Table row (after the dubstep row):
```
| Cinematic hybrid / epic, modern (2012-2026; strands: hybrid orchestral-electronic, epic orchestral with choir, sound-design trailer, cinematic pop / rock anthem, game scoring; sports and broadcast themes as a contrast; European art-house scoring is docs/CHAMBER_SCORE.md); brief: docs/CINEMATIC_HYBRID.md (timeline 2000-09 / 2010-16 / 2017-26 and strands; a bleeding-edge checklist; the verified Ode to Joy with its phrase table; engine gaps in "Engine mapping") | 3:00 to 4:30 (a standalone narrative track 3:40-4:20; trailer-house albums median 3:03 in 2012-18, 3:57 in 2019-21; library cues 2:22; film-score albums 4:02-4:48) | three acts (setup, build, climax) with hard boundaries, the lead-in to the climax nearly without bass, a held final chord; a fourth part (a coda) for a standalone track; a new layer every 4-8 bars inside an act; 90-130 bpm in 4/4 (catalogue medians 91 for the 2000s choir albums, 105 for 2012-18 hybrid albums, about 120 in 2019-21), ostinati in 8ths and 16ths, big drums on a slower grid | a singable theme that grows from one voice to everyone; percussion and ostinati carry the momentum; voices wordless, as instruments | `studio.py master vNNN --genre cinematic` (target `cinematic_2012`, -12 LUFS, -1 dBTP, mono below 120 Hz); strands `--strand newest / choir / score / sounddesign / pop / anthem` (genres.json `master_by_strand`; score: `cinematic_film`, -14.5, dynamics keep) |
```
Sources bullet (after the dubstep bullet):
```
- Cinematic hybrid (full table, catalogue and the mastering decision in docs/CINEMATIC_HYBRID.md, researched 2026-11-26): lengths, tempo, keys, dynamic complexity and whole-track loudness by strand and era from album lists (MusicBrainz + AcousticBrainz: 94 releases, 21 with data behind `cinematic_2012`, 454 tracks); album dynamics 2001-2026 from the Dynamic Range Database (https://dr.loudness-war.info/: trailer houses DR 4-6 in every era, *Unleashed* DR5 against its uncompressed mix DR10; film-score albums DR 7-12); three acts from [Sound On Sound](https://www.soundonsound.com/music-business/all-about-library-music-part-7), [Rare Form Audio](https://www.rareformaudio.com/blog/how-production-music-reveals-trailer-structure) and [UJAM](https://www.ujam.com/tutorials/secrets-of-trailer-soundtracks/); trends from [Trailaurality via Synchtank 2017](https://www.synchtank.com/blog/a-look-at-trends-in-trailer-music) and [Universal Production Music 2024](https://d1vtsdbnm97sef.cloudfront.net/en-us/news/2025-trends-in-trailer-music-advertising-and-gaming); mixing from [epicomposer 2026](https://epicomposer.com/trailer-music-production-tips/). **Hand-tuned:** -12 LUFS and the strand levels (untested in the engine), the derived loudest-section norm (-8 to -6.5 LUFS short-term, from DR), `eq` 0.6, `translate` 0.3, mono below 120 Hz, the change rate in bars.
```
Also: add `cinematic_2012` (plus `cinematic_2019`, `cinematic_choir`, `cinematic_film` by era and strand) to the "Master targets since 2026-11-25" paragraph, and the queue item 13 line "(1) genre research: DONE 2026-11-26: docs/CINEMATIC_HYBRID.md, `--genre cinematic` proposed; (2) melody verified (Breitkopf 1863 and CCARH 2009 from IMSLP), phrase table in the doc".

## 6. docs/MASTERING.md
Genre configurations table, row after `dubstep`:
```
| `cinematic` | `cinematic_2012` (21 trailer-house albums 2012-2021, 454 tracks); `cinematic_2019` (thin), `cinematic_choir`, `cinematic_film` by era and strand | -12 (untested); by strand -12 (newest, choir), -14.5 (score, `dynamics` keep), -11.5 (sound design), -10.5 (pop anthem), -12.5 (a long quiet first act) | -1 | 0.6 | 0.3 | none | docs/CINEMATIC_HYBRID.md; mono below 120 Hz (80 for the score strand); genres.json `master_by_strand` |
```
Era-target curves (a new table after the dubstep table: "Cinematic hybrid (2026-11-26, docs/CINEMATIC_HYBRID.md 'Catalogue measurements')"):
| Hz | `cinematic_2012` | `cinematic_2019` | `cinematic_choir` | `cinematic_film` |
|---|---|---|---|---|
| 31.5 | +0.5 | +2 | -1 | +9 |
| 40 | +2 | +2 | +0.5 | +8 |
| 50 | +3 | +2.5 | +2 | +7.5 |
| 63 | +3.5 | +2.5 | +3 | +7 |
| 80 | +4 | +3 | +3.5 | +6.5 |
| 100 | +3.5 | +2.5 | +3.5 | +6.5 |
| 125 | +2.5 | +2.5 | +2.5 | +6 |
| 160 | +1.5 | +1.5 | +1.5 | +5.5 |
| 200 | +1 | +1 | +1 | +5 |
| 250 | +1 | +1.5 | +1 | +4.5 |
| 315 | +1.5 | +2.5 | +1.5 | +4.5 |
| 400 | +2 | +2.5 | +2 | +4.5 |
| 500 | +2 | +2 | +2 | +3.5 |
| 630 | +1.5 | +1 | +2 | +2.5 |
| 800 | +1 | +1 | +1.5 | +1.5 |
| 1000 | 0 | 0 | 0 | 0 |
| 1250 | -1.5 | -1.5 | -1.5 | -1.5 |
| 1600 | -2.5 | -2 | -2 | -2.5 |
| 2000 | -3 | -2.5 | -3 | -3.5 |
| 2500 | -3.5 | -3.5 | -3.5 | -5 |
| 3150 | -5.5 | -5 | -5.5 | -7 |
| 4000 | -8 | -7.5 | -7.5 | -10 |
| 5000 | -10 | -10 | -10 | -13.5 |
| 6300 | -12 | -12.5 | -11.5 | -16.5 |
| 8000 | -14 | -15.5 | -13.5 | -19.5 |
| 10000 | -17 | -19 | -15.5 | -22.5 |
| 12500 | -20 | -22.5 | -18.5 | -26 |
| 16000 | -24 | -26.5 | -21 | -30.5 |

Provenance rows (the target table):
```
| `cinematic_2012` | 21 MusicBrainz releases of trailer houses (Two Steps From Hell, Audiomachine, Really Slow Motion, Ivan Torrent, Fired Earth Music, Thomas Bergersen), 2012-2021 | 2012-2021 | 454 | -12.3 (-13.5 to -10.8) | `rock_2015`: within 2.3 dB below 2 kHz, 4-6 dB too bright at 5-15 kHz; `chamberscore_ref`: 5-7 dB too dark at 5-15 kHz, 6.5 dB short at 32-97 Hz; `trance_2015`: 7-13 dB too bright on top (`refcurve.py check`) |
| `cinematic_2019` | the 2019-2021 albums of the same houses with data (Two Steps From Hell *Dragon*, *Orion*; Audiomachine *Another Sky*; Bergersen *Seven*); **thin** | 2019-2021 | 58 | -11.8 (-12.6 to -10.8) | `cinematic_2012`: within 2.3 dB (1.5-2.3 dB darker at 8-15.5 kHz); 2022-2026 extrapolated |
| `cinematic_choir` | 14 epic-choir era albums with data (E.S. Posthumus, Immediate Music, X-Ray Dog, Globus, Two Steps From Hell to *Archangel*, Bergersen *Illusions*) | 2001-2011 | 273 | -12.1 (-13.1 to -11.2) | `cinematic_2012`: within 1.5 dB (mean 0.4) |
| `cinematic_film` | 7 hybrid film-score albums (*Inception*, *The Dark Knight Rises*, *Interstellar*, *Mad Max: Fury Road*, *Batman v Superman*, *Dunkirk*, *Tenet*) | 2010-2021 | 108 | -15.2 (-18.7 to -13.5) | `cinematic_2012`: +3 to +8.5 dB under 250 Hz, -5 to -6.5 dB above 8 kHz; `chamberscore_ref`: within 1.6 dB on average, up to 10 dB apart at the extremes |
```
Caveat line for MASTERING "Caveats": "The cinematic sets are album lists of trailer houses whose library albums often have no AcousticBrainz data (Brand X Music, most Hidden Citizens, the *Humanity* chapters, all 2020-2021 Two Steps From Hell albums): the 2019-2021 curve rests on four albums; the sound-design (34 tracks) and pop-anthem (20) sets are lossy-only and are not targets."

## 7. Engine work before the session (standing rule 19; ranked in the doc's "Engine mapping")
Essential: (1) a brass section (horns, trumpets, trombones incl. bass trombone, tuba; sustain, marcato, stabs, swells, rips, falls; section scatter like `strings_section`); (2) orchestral and epic percussion (timpani with rolls, a taiko / large-drum ensemble, orchestral bass drum, suspended-cymbal swell and clash cymbals); (3) a contrabass section (`strings_section` `basses`) and a verified fast spiccato / marcato ostinato on sections. Important: (4) trailer FX (braam voice, impacts with sub boom and tail, whooshes, Shepard riser); (5) a large hall / scoring stage with early reflections and depth; (6) a wordless epic choir built from `vox2` (section helper, chant syllables, marcato hits) with an A/B for the owner; (7) woodwinds (flute, oboe, clarinet, bassoon); (8) folk instruments for a wider relay (accordion, pipes / whistle, mandolin or bouzouki, frame drum, nyckelharpa, bandura). The five-voice relay the engine can play today: `nai`, `kokle`, `lira`, `violin`, with `cimbalom` and `trembita`.
No `singer` voice may be used (every voice bank carries Lotte V's no-political-use terms; the subject is political).
