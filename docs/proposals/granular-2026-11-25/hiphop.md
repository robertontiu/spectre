# Proposal: hip hop / trap family, brought up to PRODUCTION.md section 5, item 10 (2026-11-25)

From the hip hop genre research agent. The research itself is in docs/HIPHOP.md, new section "Granularity: eras, scenes and strands" (A-H); this file holds only the changes to shared files that the orchestrator merges. Nothing here was written to a shared file.

## 1. Curve files (all made with `tools/refcurve.py catalogue ... --out`; in this folder)
`/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/hiphop_curves/`
| File | Use | Set | n | Est. LUFS (middle half) | Lossless share | Fit residual |
|---|---|---|---|---|---|---|
| `boombap_golden.json` | **new target `boombap_golden`** | tag `boom bap`, first release 1988-1999, up to 200 per year | 257 | -14.5 (-17.8 to -12.0) | 20% | max 1.0, mean 0.21 dB |
| `boombap_2010.json` | **new target `boombap_2010`** | tag `boom bap`, 2010-2021, up to 200 per year | 193 | -10.3 (-11.7 to -9.5) | 30% | max 2.3 dB (15.5-20.5 kHz only), mean 0.32 dB |
| `trap_hh_2015.json` | **new optional target, add as `trap_2015`** | tags `trap` AND `hip hop`, 2015-2021, up to 200 per year (track list in the file) | 463 | -10.4 (-12.3 to -9.3) | 47% | max 1.1, mean 0.20 dB |
| `trap_hh_2009.json` | evidence only (not a target): trap 2009-14 is within about 1.5 dB of 2015-21 | as above, 2009-2014 | 296 | -10.3 (-11.9 to -8.9) | 30% | max 1.5, mean 0.23 dB |
| `eastcoast_1990.json` | evidence only (regions) | tag `east coast hip hop`, 1990-2004, up to 100 per year | 1,276 | -12.2 (-16.0 to -10.3) | 5% | |
| `westcoast_1990.json` | evidence only (regions) | tags `west coast hip hop` OR `g-funk`, 1990-2004, up to 100 per year | 1,248 | -13.0 (-16.3 to -10.4) | 6% | |
| `south_1995.json` | evidence only (regions) | tags `southern hip hop` OR `dirty south` OR `crunk`, 1995-2009, up to 100 per year | 1,069 | -11.1 (-13.5 to -9.6) | 19% | max 1.3, mean 0.24 dB |
| `cloudrap_2012.json` | evidence only (strand) | tag `cloud rap`, 2012-2021, up to 200 per year | 142 | -10.7 (-12.7 to -9.7) | 27% | max 2.3, mean 0.32 dB |

Rejected sets (not in the folder, reported in the doc): the plain `trap` tag 2015-21 (n 732; a large share EDM trap and Latin trap: Krewella, San Holo, Marshmello, Pegboard Nerds, Anuel AA, Bad Bunny); the `drill` OR `uk drill` tag 2013-21 (n 95; mostly drill 'n' bass: Squarepusher, µ-Ziq, Venetian Snares); a combined rap-drill query (n 33, mostly unrelated: the Lucene grouping did not parse as intended). **Drill has no measurement.**

Commands to add the targets (after review):
```
python3 tools/refcurve.py add <folder>/boombap_golden.json --note "golden-age boom-bap 1988-1999; docs/HIPHOP.md Granularity C, E"
python3 tools/refcurve.py add <folder>/boombap_2010.json --note "boom-bap revival 2010-2021; docs/HIPHOP.md Granularity C, E"
python3 tools/refcurve.py add <folder>/trap_hh_2015.json --as-name trap_2015 --note "trap AND hip hop 2015-2021; optional for trap, drill, rage; docs/HIPHOP.md Granularity C, E"
```

## 2. engine/genres.json: two new entries (the existing `hiphop` and `trap` entries stay as they are)
```json
"hiphop_golden": {
  "name": "Golden-age boom-bap and 1990s hip hop (East Coast boom-bap, West Coast G-funk), era-authentic master",
  "doc": "docs/HIPHOP.md",
  "status": "new 2026-11-25 (research agent proposal): for briefs that name the 1990s, the golden age or a 1990s region; modern boom-bap uses `boombap`, everything else `hiphop`",
  "master": {"target": "boombap_golden", "lufs": -14.0, "tp": -1.0, "eq": 0.7, "translate": 0.5, "mono_below": 150.0},
  "target_source": "MusicBrainz tag boom bap, first release 1988-1999, up to 200 per year; AcousticBrainz low-level Bark bands (CC0)",
  "target_era": "1988-1999",
  "target_tracks": 257,
  "target_method": "catalogue (tools/refcurve.py; docs/MASTERING.md 'Era targets')",
  "target_date": "2026-11-25",
  "length": "3:40-4:30 (catalogue: boom-bap 1988-93 median 4:19, 1994-99 4:05)",
  "form": "intro, three verses of 16 with 8-bar hooks, outro; built from 4-bar units",
  "tempo": "85-100 bpm, swung 16ths (catalogue: boom-bap median 97 in 1988-93, 91 in 1994-99); G-funk 90-100",
  "meter": "4/4, backbeat on 2 and 4",
  "change_rate": "something changes every 4-8 bars; sections of 8 or 16 bars",
  "role": "it should feel like a real beat an artist could rap on",
  "hand_tuned": ["lufs -14 (measured median -14.5, middle half -17.8 to -12.0; -14 also matches streaming normalisation)", "mono_below 150 (vinyl-era practice of mono bass; one cutting walkthrough sums to mono up to about 200 Hz)", "eq 0.7", "translate 0.5"],
  "sources": ["target curve, length, tempo, loudness: tools/refcurve.py and tools/catalogue_stats.py on MusicBrainz + AcousticBrainz (CC0), 2026-11-25; docs/HIPHOP.md 'Granularity' C and E", "vinyl mono bass: iZotope, 'Mastering for vinyl'; Emil Berliner Studios, vinyl mastering", "G-funk tempo: Wikipedia 'G-funk'"]
},
"boombap": {
  "name": "Modern boom-bap: the 2010s-2020s revival, drumless and sample-led beats",
  "doc": "docs/HIPHOP.md",
  "status": "new 2026-11-25 (research agent proposal): loud like trap, but with boom-bap's balance (no long 808 sub, more 100-300 Hz, a darker top)",
  "master": {"target": "boombap_2010", "lufs": -10.5, "tp": -1.0, "eq": 0.7, "translate": 0.5, "mono_below": 120.0},
  "target_source": "MusicBrainz tag boom bap, first release 2010-2021, up to 200 per year; AcousticBrainz low-level Bark bands (CC0)",
  "target_era": "2010-2021",
  "target_tracks": 193,
  "target_method": "catalogue (tools/refcurve.py; docs/MASTERING.md 'Era targets')",
  "target_date": "2026-11-25",
  "length": "2:30-3:45 (catalogue: boom-bap 2012-17 median 3:42, 2018-21 2:49)",
  "form": "as `hiphop`; drumless beats run the loop under the verse with few or no drums",
  "tempo": "80-95 bpm, swung (catalogue: boom-bap median 90 in 2012-17, 85 in 2018-21)",
  "meter": "4/4, backbeat on 2 and 4",
  "change_rate": "something changes every 4-8 bars; sections of 8 or 16 bars",
  "role": "it should feel like a real beat an artist could rap on",
  "hand_tuned": ["eq 0.7", "translate 0.5", "lufs -10.5 kept equal to `hiphop` (measured median -10.3)"],
  "sources": ["target curve, length, tempo, loudness: tools/refcurve.py and tools/catalogue_stats.py on MusicBrainz + AcousticBrainz (CC0), 2026-11-25; docs/HIPHOP.md 'Granularity' C and E"]
}
```
Optional, descriptive only (the engine does not read it): add to the existing `hiphop` entry
```json
"subdivisions": "docs/HIPHOP.md 'Granularity' (A-H): streaming trap is the default; `--target trap_2015` for a pure trap, drill or rage brief; `hiphop_golden` and `boombap` for boom-bap by era"
```
The `master` blocks of `hiphop` and `trap` do not change (released tracks and running sessions unaffected).

## 3. data/catalogue_references.json, `targets` additions
```json
"boombap_golden": {"tag": ["boom bap"], "years": "1988-1999", "per_year": 200},
"boombap_2010": {"tag": ["boom bap"], "years": "2010-2021", "per_year": 200},
"trap_2015": {"tag": ["trap\" AND tag:\"hip hop"], "years": "2015-2021", "per_year": 200, "note": "the tag string is a Lucene AND inside refcurve's tag query: (tag:\"trap\" AND tag:\"hip hop\"); the plain trap tag is mostly EDM and Latin trap"}
```
(`catalogue_stats.py targets` passes each tag as one argument, so the AND survives; `target_commands()` ignores the `note` key.)

## 4. docs/MASTERING.md, "Era targets": rows to add
Three columns for the curve table (dB re 1 kHz):
| Hz | `boombap_golden` | `boombap_2010` | `trap_2015` |
|---|---|---|---|
| 31.5 | +4 | +0.5 | +6.5 |
| 40 | +6 | +3.5 | +7.5 |
| 50 | +8 | +6.5 | +8.5 |
| 63 | +9.5 | +8 | +8 |
| 80 | +9.5 | +8 | +6.5 |
| 100 | +8.5 | +7 | +4.5 |
| 125 | +6.5 | +5.5 | +2.5 |
| 160 | +5 | +4 | +1 |
| 200 | +3.5 | +3 | +0.5 |
| 250 | +2.5 | +2.5 | 0 |
| 315 | +1.5 | +1.5 | +0.5 |
| 400 | +1.5 | +2.5 | +1 |
| 500 | +2 | +3 | +1.5 |
| 630 | +1.5 | +2 | +1.5 |
| 800 | +0.5 | +1 | +0.5 |
| 1000 | 0 | 0 | 0 |
| 1250 | -0.5 | -0.5 | -0.5 |
| 1600 | -1 | -1 | -1 |
| 2000 | -1.5 | -2 | -2 |
| 2500 | -2.5 | -2.5 | -3 |
| 3150 | -3 | -3.5 | -3.5 |
| 4000 | -4 | -4.5 | -4.5 |
| 5000 | -5.5 | -5.5 | -5 |
| 6300 | -7 | -6 | -4.5 |
| 8000 | -9 | -7 | -5 |
| 10000 | -11.5 | -9 | -6.5 |
| 12500 | -14.5 | -13 | -10 |
| 16000 | -19 | -20.5 | -15 |
And one line under the table: "`boombap_golden`: 257 tracks tagged boom bap, 1988-1999; 80% lossy files, whose top is 1.5-3 dB darker at 6.4-12 kHz than the 51 lossless files', so its top is uncertain by that much. `boombap_2010`: 193 tracks, 2010-2021. `trap_2015`: 463 tracks tagged trap and hip hop, 2015-2021, within 1-1.5 dB of `hiphop_2015` (optional, not a default). Drill and the 2022-2026 strands: not measured (docs/HIPHOP.md 'Granularity' E)."

## 5. docs/ORCHESTRATION.md, "Genre conventions": replacement for the hip hop row's first cell and `{{MASTER}}` cell
First cell: `Hip hop / beats (trap, boom-bap, drill, rage, aggressive rap, folk-fusion trap); briefs: docs/CRAFT.md (craft), docs/HIPHOP.md (configuration; by wave, scene and strand: "Granularity" A-H, a bleeding-edge checklist in F, which configuration each brief uses in H)`
`{{MASTER}}` cell: `studio.py master vNNN --genre hiphop` (default: streaming trap, drill, rage, folk-fusion trap; `hiphop_2015`, -10.5 LUFS, -1 dBTP; `--target trap_2015` for a pure trap/drill/rage brief); `--genre boombap` for modern boom-bap or drumless (`boombap_2010`, -10.5 LUFS); `--genre hiphop_golden` for a 1990s or golden-age brief (`boombap_golden`, -14 LUFS, mono below 150 Hz); released 001-006 and 011: `--published`. The brief names its subdivision; none named = streaming trap.
Tempo text in the `{{FORM}}` cell, if it is touched: "two pockets: boom-bap 85-100 bpm swung (measured median 91-97 in the 1990s, 85 in 2018-21), or trap 140-150 written (median 143), felt in half time".

## 6. Contradictions with existing docs (flagged, not edited)
- docs/HIPHOP.md "The decision" says the tempo choice (boom-bap pocket or half-time trap) "doesn't change the master". The measurements say it does when the pocket comes with its era or strand: golden-age boom-bap is about 4 dB quieter, 3-4 dB heavier at 97-183 Hz and 3-6 dB darker above 6.4 kHz than trap; modern boom-bap has 5 dB less under 32 Hz and is 2-3.5 dB darker above 6.4 kHz. Trap against `hiphop_2015`: no meaningful change. (Noted in HIPHOP.md itself; the orchestrator may want the genres.json `hiphop` status text to point to it.)
- docs/CRAFT.md §2 gives drill one tempo and pattern (140-145, sliding 808s): that is the UK and Brooklyn branch; Chicago drill has no 808 slides (HIPHOP.md "Granularity" D). Left in CRAFT unchanged; HIPHOP.md D says so.
- The genres.json `trap` entry's name lists boom-bap among "808-driven" styles; boom-bap is sample-driven (measured: the least sub of any wave). Descriptive only; suggest renaming to "Trap / beats (first releases of 001-006)".
- None of the measured values contradicts the -10.5 LUFS of `hiphop`: the catalogue's trap median is -10.4, the 2024 charts -8.3 (the open item to test -9 stands).
