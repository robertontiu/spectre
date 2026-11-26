# Proposal: techno, modern era (queue item 14), 2026-11-26

Research: docs/TECHNO.md (written, not committed). Nothing here has been applied to a shared file (genres.json, targets.json, eqmaps.json, catalogue_references.json, ORCHESTRATION, MASTERING, PRODUCTION, LESSONS, MANUAL): the orchestrator applies it. Labels: [M] measured, [S] sourced, [H] hand-tuned.

## 1. Curve files (this folder) and how to add them
Made with `tools/refcurve.py catalogue ... --out` (run under `flock /tmp/spectre-musicbrainz.lock`):

| File | Command | n | Est. LUFS (middle half) | Lossless | Fit (max / mean residual) | Propose as target |
|---|---|---|---|---|---|---|
| `techno_2015.json` | `refcurve.py catalogue --tag techno --years 2015-2021 --per-year 300 --name techno_2015` | 424 | -12.1 (-13.9 to -10.6) | 58% | 1.6 / 0.23 dB | **yes** (default) |
| `techno_2018.json` | `refcurve.py catalogue --tag techno --years 2018-2021 --per-year 300 --name techno_2018` | 203 | -11.6 (-13.7 to -10.2) | 67% | 1.2 / 0.21 dB | **yes** (newest; within 0.5 dB) |
| `techno_2008.json` | `refcurve.py catalogue --tag techno --years 2008-2014 --per-year 300 --name techno_2008` | 1369 | -12.5 (-14.4 to -11.1) | 28% | 1.1 / 0.2 dB | no (within 0.5-1.5 dB of 2015) |
| `techno_2000.json` | `refcurve.py catalogue --tag techno --years 2000-2007 --per-year 300 --name techno_2000` | 1588 | -12.4 (-14.3 to -10.7) | 17% | 1.0 / 0.17 dB | **yes** (minimal era) |
| `techno_1990.json` | `refcurve.py catalogue --tag techno --years 1990-1999 --per-year 300 --name techno_1990` | 2206 | -14.9 (-17.5 to -12.4) | 30% | 0.9 / 0.2 dB | **yes** (roots) |
| `techno_hard.json` | `refcurve.py catalogue --artist "Amelie Lens" --artist "Charlotte de Witte" --artist "I Hate Models" --artist "Dax J" --artist "Perc" --artist "Kobosil" --artist "SNTS" --artist "Paula Temple" --artist "Rebekah" --artist "Ansome" --artist "Clouds" --artist "999999999" --artist "Chris Liebing" --artist "DJ Rush" --artist "Nico Moreno" --artist "Kwartz" --limit 100 --era "2010-2021 (artist set)" --list-tracks --name techno_hard` | 540 | -12.0 (-13.6 to -10.6) | 9% | 1.2 / 0.16 dB | **yes** (hard, industrial; this brief) |
| `techno_dub.json` | `refcurve.py catalogue --tag "dub techno" --years 2005-2021 --per-year 200 --name techno_dub` | 792 | -15.1 (-16.9 to -12.9) | 37% | 1.9 / 0.25 dB | **yes** (dub) |
| `techno_minimal.json` | `refcurve.py catalogue --tag "minimal techno" --years 2005-2021 --per-year 200 --name techno_minimal` | 406 | -13.5 (-15.8 to -11.8) | 60% | 1.4 / 0.23 dB | no (within 1.5 dB of 2015 below 12 kHz) |
| `techno_acid.json` | `refcurve.py catalogue --tag "acid techno" --years 2005-2021 --per-year 200 --name techno_acid` | 77 | -13.7 (-15.6 to -10.3) | 27% | 0.9 / 0.18 dB | no (within 1.5 dB below 12 kHz) |
| `techno_melodic.json` | `refcurve.py catalogue --tag "melodic techno" --years 2005-2021 --per-year 200 --name techno_melodic` | 51 | -11.3 (-11.7 to -10.5) | 92% | 1.2 / 0.3 dB | **yes, thin** (melodic) |
| `techno_detroit.json` | `refcurve.py catalogue --tag "detroit techno" --years 2005-2021 --per-year 200 --name techno_detroit` | 28 | -12.7 (-14.2 to -11.5) | 79% | 1.3 / 0.27 dB | no (28 tracks) |
| `techno_industrial.json` | `refcurve.py catalogue --tag "industrial techno" --years 2005-2021 --per-year 200 --name techno_industrial` | 238 | -11.2 (-13.5 to -9.8) | 25% | 0.6 / 0.12 dB | no (tag mixes industrial bands: 7.5 dB less sub) |

Not made: `hard techno` tag (818 recordings, 3 with AcousticBrainz data: replaced by the artist set), `schranz` (5), `hypnotic techno` (0), `hard groove` (0), `deep techno` (9), `ebm` (MusicBrainz 503 twice). The hard set's artists resolved to the MBIDs in section 4 (checked by name, disambiguation and country); a re-run by MBID may differ by a few tracks (MusicBrainz search drift).

Add (orchestrator): `python3 tools/refcurve.py add <folder>/techno_2015.json` and the same for `techno_2018`, `techno_hard`, `techno_dub`, `techno_melodic`, `techno_2000`, `techno_1990`.

## 2. engine/genres.json: the new `techno` entry
```json
"techno": {
  "name": "Techno, modern (2009-2026), original / extended mix (one long DJ version)",
  "doc": "docs/TECHNO.md",
  "status": "researched 2026-11-26 (queue item 14); targets measured from the open catalogue (tag techno by era, strand tags, a hard-techno artist set); loud sections from Mixgraph's store previews; loudness untested in the engine",
  "master": {
    "target": "techno_2015",
    "lufs": -9.5,
    "tp": -1.0,
    "eq": 0.7,
    "translate": 0.4,
    "mono_below": 120.0,
    "max_low_boost_db": 2.0
  },
  "target_source": "MusicBrainz tag techno, first release 2015-2021, up to 300 per year; AcousticBrainz low-level Bark bands (CC0)",
  "target_era": "2015-2021",
  "target_tracks": 424,
  "target_method": "catalogue (tools/refcurve.py; docs/MASTERING.md 'Era targets')",
  "target_date": "2026-11-26",
  "era_targets": {
    "2015-2021 (the modern period pooled; default)": "techno_2015",
    "2019-2026, the newest sound (measured 2018-2021, 203 tracks; within 0.5 dB of techno_2015; 2022-2026 extrapolated)": "techno_2018",
    "the minimal era (2000-2007, 1,588 tracks: 3-6 dB less at 31.5-63 Hz, 2 dB brighter at 3-5 kHz)": "techno_2000",
    "roots (1990-1999, 2,206 tracks: 4.5-7 dB less at 31.5-63 Hz)": "techno_1990",
    "note": "2008-2014 (1,369 tracks) reads within 0.5-1.5 dB of techno_2015 and has no target of its own; a brief aimed at an era or strand passes `--strand` (docs/TECHNO.md 'Mastering per subdivision')"
  },
  "master_by_strand": {
    "note": "the loud section varies by strand (store previews, Mixgraph 2026-08-11: Hard Techno -7.3, Peak Time / Driving -8.6, Raw / Deep / Hypnotic -8.7, Minimal / Deep Tech -10.3, Melodic House & Techno -10.5); whole tracks sit 4-5 dB lower (catalogue 2015-21 -12.1; long DJ intros and outros). Integrated levels here aim the loud section at the previews when the main sections are most of the track; read the loudest 2 minutes after mastering. None of these levels has been tested in the engine",
    "default": {
      "label": "modern peak-time / driving (2009-2026)",
      "note": "the genre's master"
    },
    "newest": {
      "label": "newest sound (2019-2026)",
      "target": "techno_2018",
      "lufs": -9.5,
      "tp": -1.0,
      "note": "within 0.5 dB of techno_2015; 2022-2026 extrapolated"
    },
    "hard": {
      "label": "hard techno, schranz, fast hard groove (2020s revival; queue 14)",
      "target": "techno_hard",
      "lufs": -8.5,
      "tp": -1.0,
      "mono_below": 150.0,
      "note": "16-artist set, 540 tracks, 9% lossless (16 kHz on the smoothness term); Hard Techno loud sections -7.3 (-8.2 to -6.2): aim the loudest 2 minutes at about -7.5 to -7, never louder than -6.5"
    },
    "industrial": {
      "label": "industrial / EBM-adjacent",
      "target": "techno_hard",
      "lufs": -9.0,
      "tp": -1.0,
      "note": "the industrial techno tag mixes industrial bands (7.5 dB less sub) and is not used; the hard set includes the industrial school"
    },
    "hypnotic": {
      "label": "hypnotic, raw, deep",
      "target": "techno_2015",
      "lufs": -9.5,
      "tp": -1.0,
      "note": "Raw / Deep / Hypnotic previews -8.7, range 3.2 LU (the flattest); no tag data"
    },
    "dub": {
      "label": "dub techno",
      "target": "techno_dub",
      "lufs": -12.0,
      "tp": -1.0,
      "eq": 0.5,
      "dynamics": "keep",
      "note": "792 tracks, whole tracks -15.1 (the quietest); 3.5-5.5 dB darker from 5 kHz"
    },
    "minimal": {
      "label": "minimal",
      "target": "techno_2015",
      "lufs": -10.5,
      "tp": -1.0,
      "note": "minimal techno tag (406 tracks) within 1.5 dB of techno_2015 below 12 kHz; Minimal / Deep Tech previews -10.3"
    },
    "melodic": {
      "label": "melodic techno and the progressive crossover",
      "target": "techno_melodic",
      "lufs": -11.0,
      "tp": -1.0,
      "eq": 0.5,
      "note": "thin: 51 tracks (92% lossless); 4-4.5 dB less at 50-160 Hz; Melodic House & Techno previews -10.5; trance's melodic crossover masters at -11 too"
    },
    "minimal_era": {
      "label": "the minimal era (2000-2008)",
      "target": "techno_2000",
      "lufs": -11.0,
      "tp": -1.0,
      "note": "whole tracks -12.4; CD albums DR 6-8"
    },
    "roots": {
      "label": "roots (1990s Detroit, Berlin, UK)",
      "target": "techno_1990",
      "lufs": -13.0,
      "tp": -1.0,
      "dynamics": "keep",
      "note": "whole tracks -14.9; albums DR 9-14"
    }
  },
  "length": "5:30-7:00, aim about 6:00-6:30 (one long DJ version; measured: tag techno median 5:59 in 2015-21 (middle half 4:44-7:02), 6:08-6:12 in 2009-18, 5:29 in 2019-21; minimal 6:22, dub 6:01, melodic 5:40, acid 5:08; Original Mix titles 6:04, Extended Mix 5:48; Mixgraph 5-7 min; Futureproof hard techno 6-8 min)",
  "form": "a DJ tool: intro 16-32 bars of kick (and rumble) only; a main section 32-64 bars that adds bass, the hook sound and percussion layer by layer; a breakdown 16-32 bars without the kick (0-8 in hypnotic and minimal strands); a re-entry and peak 32-64 bars; an outro 16-32 bars back to kick and percussion; an element in or out about every 16 bars over an 8-bar loop; builds by filters, density and layers rather than silence and drops",
  "tempo": "by strand: 124-128 melodic, dub, minimal; 130-140 peak-time / driving, hypnotic, industrial, hard groove; 145-155 hard techno (peak-time festival 150-155); over 160 is hardstyle, hardcore, hardtekk. Mixgraph techno median 133 (128-140; yearly median 128 in 1991 to 140 in 2025, lowest 126 in 2013); hard techno median 146 (136-155); catalogue (Essentia) 132 in the 1990s, 136 in 2000-08, 126-127 in 2009-18, 130 in 2019-21",
  "meter": "4/4, kick on every quarter (never half time); offbeat open hat, bass or ride; 16th hats; swing 50-54% on hats and percussion only (Attack); swung and syncopated in hard groove and Detroit, straight in hard techno and industrial",
  "change_rate": "an element in or out about every 16 bars (8 in the busy strands); slow movement inside sections (filter, resonance, decay, sends over 8-16 bars); the kick leaves only for the breakdown",
  "role": "the kick and its low end are the lead; one repeating hook sound (an acid line, a stab, a riff of one or two notes, a loop) over percussion; voices as short loops, shouts or chopped phrases",
  "hand_tuned": [
    "lufs -9.5 and the strand levels (-8.5 hard, -9 industrial, -9.5 hypnotic, -10.5 minimal, -11 melodic and minimal era, -12 dub, -13 roots): choices against the measured loud sections (Mixgraph previews) and whole tracks (catalogue); untested in the engine",
    "eq 0.7 and translate 0.4 (as trance and dubstep)",
    "max_low_boost_db 2 (the heaviest measured low end in the project: the mix must supply 50-80 Hz)",
    "mono_below 120 (MusicRadar; Nihil Young's 50-120 Hz low-end focus) and 150 for hard (Futureproof)",
    "the default tempos and bar counts inside the sourced ranges"
  ],
  "sources": "docs/TECHNO.md 'Configuration', 'Catalogue measurements' and 'Mastering per subdivision' (Mixgraph techno BPM https://www.mixgraph.io/bpm-for/techno ; hard techno BPM https://www.mixgraph.io/bpm-for/hard-techno ; Mixgraph loudness by genre https://www.mixgraph.io/tools/lufs-meter ; catalogue lengths, tempo, loudness and curves by Spectre from MusicBrainz + AcousticBrainz, 2026-11-26; Futureproof hard techno, MusicRadar 2023 techno guide, MusicRadar / Computer Music and Bonedo rumble guides, Attack Magazine for form, drums, rumble and mixing; Dynamic Range Database for album dynamics)"
}
```

## 3. engine/eqmaps.json: a `techno` map (optional, for `"genre": "techno"` role presets and `listen --clarity`)
```json
"techno": {"source": "docs/TECHNO.md 'Layering and EQ carving': MusicRadar 2023, Attack (dark techno rumble, reverb kick), Futureproof hard techno, MusicRadar rumble (10 steps), Bonedo; clap, perc, lead, pad rows from the trance and dubstep maps [H]", "tolerance_db": 6, "inherit": "dubstep", "core": ["kick", "sub|bass|upper-bass", "hats|cymbals", "clap|snare|perc"], "roles": {"kick": {"hp": [25, 30], "cut": [[300, 600]], "own": [[45, 80], [100, 200], [2000, 5000]]}, "sub": {"hp": [20, 30], "lp": [100, 200], "cut": [[125, 145]], "own": [[30, 100]]}, "bass": {"hp": [120, 160], "cut": [[200, 300]], "own": [[300, 3000]]}, "upper-bass": {"hp": [120, 160], "cut": [[200, 300]], "own": [[300, 3000]]}, "clap": {"hp": [150, 250], "cut": [[400, 800]], "own": [[1000, 8000]]}, "snare": {"hp": [100, 150], "cut": [[300, 700]], "own": [[180, 250], [2000, 5000]]}, "hats": {"hp": [500, 1000], "cut": [[2000, 5000]], "own": [[6000, 14000]]}, "cymbals": {"hp": [500, 1000], "cut": [[2000, 5000]], "own": [[6000, 14000]]}, "perc": {"hp": [80, 150], "cut": [[300, 500]], "own": [[150, 400], [2000, 6000]]}, "lead": {"hp": [200, 300], "cut": [[300, 600]], "own": [[1000, 4000]]}, "support": {"hp": [200, 300], "cut": [[300, 600]], "own": [[1000, 4000]]}, "pad": {"hp": [200, 300], "cut": [[200, 500]], "own": [[1000, 3000], [8000, 16000]]}, "texture": {"hp": [200, 300], "cut": [[200, 500]], "own": [[1000, 3000], [8000, 16000]]}, "vocal": {"hp": [100, 150], "cut": [[200, 400]], "own": [[2000, 5000]]}, "return": {"hp": [200, 500], "lp": [6000, 12000], "cut": [[300, 600]]}}}
```
Rows and sources in docs/TECHNO.md "Layering and EQ carving". `inherit: "dubstep"` for roles not listed. The `sub` row covers the rumble return too (a role `sub` on it); its 125-145 Hz cut is MusicRadar's 135 Hz notch.

## 4. data/catalogue_references.json: `targets` additions
```json
"techno_2015": {"tag": ["techno"], "years": "2015-2021", "per_year": 300},
"techno_2018": {"tag": ["techno"], "years": "2018-2021", "per_year": 300},
"techno_2000": {"tag": ["techno"], "years": "2000-2007", "per_year": 300},
"techno_1990": {"tag": ["techno"], "years": "1990-1999", "per_year": 300},
"techno_hard": {"artist": ["67db280d-c3e4-49d9-978e-4050f4e209ef", "1de4e373-e597-4087-bf3d-256ec597749e", "f9a4de7f-d3c6-4de8-8892-7aca52610edd", "8a860182-6587-4bc3-b578-88e56424b6dc", "7693c255-9697-4ba2-ac70-8bbbe3f9f7eb", "c6b2c2c3-e771-4228-9401-b263369d5b48", "91b8f0ac-17ee-470a-afcd-457bd45971cd", "c106c230-ab47-4550-adf2-d27db91f0b24", "10d274f0-a063-4fb6-a924-5631e9d9b633", "f2db511c-76ac-490a-8881-b4ee31283d79", "b6a899e8-d886-4562-bc22-269b9589c760", "fee18f64-e35c-4ca6-be78-605d73d0cefa", "86a1c458-2d97-42cd-a142-a8fee30ae4a1", "e1649010-6ebe-4ce7-98d8-cc6e5fa686fa", "82f2714c-f532-482a-859a-5b170901f9e9", "64a285e7-e990-4bd8-934e-732e8e000d69"], "limit": 100, "names": ["Amelie Lens", "Charlotte de Witte", "I Hate Models", "Dax J", "Perc", "Kobosil", "SNTS", "Paula Temple", "Rebekah", "Ansome", "Clouds", "999999999", "Chris Liebing", "DJ Rush", "Nico Moreno", "Kwartz"]},
"techno_dub": {"tag": ["dub techno"], "years": "2005-2021", "per_year": 200},
"techno_melodic": {"tag": ["melodic techno"], "years": "2005-2021", "per_year": 200}
```
(`techno_hard` follows `ro_fusion`'s format: artist MBIDs with `names`; it was measured by name with `--limit 100 --min-length 90`.) data/README.md: add "and the techno era, strand and hard-artist targets (2026-11-26)".

## 5. docs/ORCHESTRATION.md "Genre conventions": row and sources
Row:
| Techno, modern (2009-2026; strands: peak-time / driving, hard techno, industrial / EBM-adjacent, hypnotic / dub / deep, melodic techno, acid, hard groove and schranz, minimal; scenes as craft schools: Berlin, Detroit, Belgium / Netherlands, UK, Tbilisi); brief: docs/TECHNO.md (timeline 1985-99 / 2000-08 / 2009-19 / 2020-26 and strands; a bleeding-edge checklist; engine gaps in "Engine mapping") | 5:30 to 7:00, aim about 6:00-6:30 (one long DJ version; measured median 5:59 in 2015-21, 6:08-6:12 in 2009-18, 5:29 in 2019-21; radio edits are not the genre's habit) | a DJ tool: intro 16-32 bars of kick (and rumble), main 32-64 adding bass, hook and percussion layer by layer, breakdown 16-32 without the kick (0-8 in hypnotic and minimal), re-entry and peak 32-64, outro 16-32 back to kick and percussion; an element in or out every 16 bars (8 in busy strands) over an 8-bar loop; builds by filters, density and layers; four on the floor at 124-128 (melodic, dub, minimal), 130-140 (peak-time, hypnotic, industrial, hard groove), 145-155 (hard techno; Mixgraph median 146) | the kick and its low end lead; one repeating hook sound (acid, stab, riff of one or two notes, loop) over percussion; voices as short shouts, loops or chopped phrases | `studio.py master vNNN --genre techno` (target `techno_2015`, -9.5 LUFS, -1 dBTP, mono below 120 Hz, low boosts capped at +2 dB); strands `--strand hard / industrial / hypnotic / dub / minimal / melodic / newest / minimal_era / roots` (genres.json `master_by_strand`; hard: `techno_hard`, -8.5, mono below 150) |

Sources line:
- Techno (full table, catalogue and the mastering decision in docs/TECHNO.md, researched 2026-11-26): lengths, tempo and whole-track loudness by era and strand tag from the open catalogue (MusicBrainz + AcousticBrainz, `tools/catalogue_stats.py tag`: tag techno median 5:59 and 127 bpm in 2015-21, 5:29 and 130 bpm in 2019-21; dub techno -15.1 est. LUFS, minimal -13.5, techno 2015-21 -12.1); tempo from Mixgraph (techno median 133, middle half 128-140, yearly median 140 in 2025: https://www.mixgraph.io/bpm-for/techno ; hard techno median 146, middle half 136-155: https://www.mixgraph.io/bpm-for/hard-techno); loud sections of releases by strand (Hard Techno -7.3, Peak Time / Driving -8.6, Raw / Deep / Hypnotic -8.7, Melodic House & Techno -10.5: https://www.mixgraph.io/tools/lufs-meter); form and kick / rumble practice from [Futureproof](https://futureproofmusicschool.com/blog/making-hard-techno-a-path-to-unique-sound-design), [MusicRadar 2023](https://musicradar.com/news/techno-guide-2023), [MusicRadar rumble](https://musicradar.com/how-to/rumbling-techno-kick), [Bonedo](https://www.bonedo.de/artikel/bass-drum-rumble-rattle-for-techno/) and [Attack](https://www.attackmagazine.com/technique/beat-dissected/dark-techno-rumble/); the fast era from [Mixmag 2023](https://mixmag.net/feature/has-dance-music-got-harder-faster-hor-berlin-hard-techno-rave-music-interview-investigation) and [Attack 2023](https://www.attackmagazine.com/features/long-read/has-techno-lost-its-groove/); `techno_2015` from `tools/refcurve.py catalogue --tag techno --years 2015-2021` (424 tracks), `techno_hard` from a 16-artist set (540 tracks). **Hand-tuned:** -9.5 LUFS and the strand levels (untested in the engine), `eq` 0.7, `translate` 0.4, `max_low_boost_db` 2, mono below 120 Hz (150 for hard), the bar counts inside the sourced ranges.

Also add `techno_2015` (plus `techno_2018`, `techno_hard`, `techno_dub`, `techno_melodic`, `techno_2000`, `techno_1990` by era and strand) to the "Master targets since 2026-11-25" paragraph.

Queue item 14: prefix "[(1) genre research DONE 2026-11-26: docs/TECHNO.md, `--genre techno` proposed (target `techno_2015`; this brief `--strand hard`, `techno_hard`)]"; the engine gaps to build before the brief (standing rule 19): docs/TECHNO.md "Engine mapping" 1-4 (rumble, hard kick, 909 kick and hats, the loud master test), 5 for hard-groove percussion.

## 6. docs/MASTERING.md
Genre configurations table row:
| `techno` | `techno_2015` (catalogue, 424 tracks); strands `techno_hard` (540), `techno_dub` (792), `techno_melodic` (51, thin), eras `techno_2018` (203), `techno_2000`, `techno_1990` | -9.5; by strand -8.5 (hard), -9 (industrial), -9.5 (hypnotic, newest), -10.5 (minimal), -11 (melodic, minimal era), -12 (dub), -13 (roots) | -1 | 0.7 | 0.4 | none yet | docs/TECHNO.md; loud sections Mixgraph previews; low boosts capped at +2 dB |

Era targets, a new curve table "Techno (2026-11-26, docs/TECHNO.md "Catalogue measurements")":

| Hz | `techno_2015` | `techno_2018` | `techno_hard` | `techno_dub` | `techno_melodic` | `techno_2000` | `techno_1990` |
|---|---|---|---|---|---|---|---|
| 31.5 | +9 | +9 | +9.5 | +10.5 | +6 | +3 | +2 |
| 40 | +12 | +12 | +12.5 | +12.5 | +8.5 | +7 | +5.5 |
| 50 | +14.5 | +14 | +14.5 | +14 | +10.5 | +10.5 | +9 |
| 63 | +15 | +14.5 | +15 | +14 | +10.5 | +12 | +10.5 |
| 80 | +13.5 | +13.5 | +14 | +13 | +9 | +12 | +10.5 |
| 100 | +11 | +11 | +11.5 | +10.5 | +7 | +10.5 | +9 |
| 125 | +8.5 | +8.5 | +9 | +8.5 | +4.5 | +9 | +7.5 |
| 160 | +7 | +7 | +7 | +7 | +3.5 | +7.5 | +6 |
| 200 | +6 | +6 | +5.5 | +6.5 | +3 | +6 | +5 |
| 250 | +4.5 | +4.5 | +3.5 | +5.5 | +2.5 | +4 | +3.5 |
| 315 | +3.5 | +3.5 | +2 | +4.5 | +2.5 | +2 | +2 |
| 400 | +2.5 | +2.5 | +1 | +3.5 | +2 | +1 | +1 |
| 500 | +2 | +2 | +0.5 | +2.5 | +2 | +0.5 | +0.5 |
| 630 | +1.5 | +1.5 | +0.5 | +1.5 | +1.5 | +0.5 | +0.5 |
| 800 | +0.5 | +0.5 | 0 | +1 | +1 | 0 | 0 |
| 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1250 | -0.5 | -1 | -0.5 | -1 | -1 | 0 | -0.5 |
| 1600 | -1.5 | -1.5 | -0.5 | -2 | -2 | -0.5 | -0.5 |
| 2000 | -2 | -2 | -1 | -3.5 | -3 | -1 | -1.5 |
| 2500 | -3 | -3 | -1.5 | -4.5 | -4 | -1.5 | -1.5 |
| 3150 | -3.5 | -3.5 | -2 | -5.5 | -5 | -1.5 | -2 |
| 4000 | -3.5 | -3.5 | -2 | -6 | -5.5 | -1.5 | -2 |
| 5000 | -3.5 | -3.5 | -1.5 | -7 | -5.5 | -1.5 | -2.5 |
| 6300 | -3 | -3 | -1.5 | -7.5 | -5 | -1.5 | -2.5 |
| 8000 | -3 | -2.5 | -2 | -8.5 | -5 | -2.5 | -3.5 |
| 10000 | -4 | -4 | -4 | -10 | -6 | -4 | -5.5 |
| 12500 | -7.5 | -7 | -7.5 | -12.5 | -9 | -7 | -8.5 |
| 16000 | -13 | -12.5 | -12 | -17.5 | -14.5 | -11.5 | -13.5 |

Target table rows:
| `techno_2015` | MusicBrainz tag `techno`, first release 2015-2021, up to 300 per year | 2015-2021 | 424 | -12.1 (-13.9 to -10.6) | `trance_2015` 7.4 dB short at 32-97 Hz, 4-4.9 dB short at 97-291 Hz, within 1.5 dB from 400 Hz to 12 kHz; `dubstep_2015` 6.8 / 5.5 / 3.7 dB short there; `hiphop_2015` 6.6 dB short at 32-97 Hz and 2.5-4 dB too dark above 4 kHz (`refcurve.py check`): the heaviest low end measured in the project |
| `techno_2018` | tag `techno`, 2018-2021, up to 300 per year (2022-2026 extrapolated) | 2018-2021 | 203 | -11.6 (-13.7 to -10.2) | `techno_2015`: within 0.5 dB everywhere |
| `techno_hard` | 16 MusicBrainz artists of the hard and industrial schools (Amelie Lens, Charlotte de Witte, I Hate Models, Dax J, Perc, Kobosil, SNTS, Paula Temple, Rebekah, Ansome, Clouds, 999999999, Chris Liebing, DJ Rush, Nico Moreno, Kwartz), up to 100 recordings each; 9% lossless | mostly 2010-2021 | 540 | -12.0 (-13.6 to -10.6) | `techno_2015`: +1 to +2 dB at 2-8 kHz, -1 to -1.5 dB at 250-500 Hz, the same sub; 16 kHz on the smoothness term |
| `techno_dub` | tag `dub techno`, 2005-2021, up to 200 per year | 2005-2021 | 792 | -15.1 (-16.9 to -12.9) | `techno_2015`: -3.5 to -5.5 dB from 5 kHz, -1.5 to -2 at 2-3 kHz |
| `techno_melodic` | tag `melodic techno`, 2005-2021 (**thin**, 92% lossless) | 2005-2021 | 51 | -11.3 (-11.7 to -10.5) | `techno_2015`: -4 to -4.5 dB at 50-160 Hz, -1.5 to -2 dB at 3-8 kHz |
| `techno_2000` | tag `techno`, 2000-2007 | 2000-2007 | 1,588 | -12.4 (-14.3 to -10.7) | `techno_2015`: -3 to -6 dB at 31.5-63 Hz, +2 dB at 3-5 kHz |
| `techno_1990` | tag `techno`, 1990-1999 | 1990-1999 | 2,206 | -14.9 (-17.5 to -12.4) | `techno_2015`: -4.5 to -7 dB at 31.5-63 Hz, +1 to +1.5 dB at 3-5 kHz |

Also measured, not targets: 2008-2014 (1,369; within 0.5-1.5 dB of `techno_2015`), minimal techno (406; within 1.5 dB below 12 kHz), acid techno (77; within 1.5 dB below 12 kHz), detroit techno (28), industrial techno (238; the tag mixes industrial bands).

## 7. Open, not sourced, not tested
- No true peak, PLR, short-term LRA or width measurement exists for techno releases; the integrated levels are untested in the engine (gap 4 of "Engine mapping": a loud master test on the brief's peak section).
- AcousticBrainz ends in 2022: every 2022-2026 tonal claim is extrapolation (`techno_2018`, `techno_hard` to 2021).
- Hypnotic, hard groove, schranz, peak-time and EBM have no usable tag data; the hard target is an artist set, not a tag.
- The rumble's numbers vary between sources (low-pass 96.6 Hz to 800 Hz); a fitted preset needs recorded references (CC0 rumble loops and hard-techno kicks from Freesound, as `refs-dubstep-*`).
