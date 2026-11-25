# Proposal: dubstep (queue item 12), for the orchestrator to review and commit

Written 2026-11-25 by the genre research agent. The genre brief is **docs/DUBSTEP.md** (new, uncommitted). Nothing below has been applied: engine/genres.json, engine/targets.json, engine/eqmaps.json, data/catalogue_references.json, docs/ORCHESTRATION.md and docs/MASTERING.md are unchanged. No render or master was made.

## 1. Target curve files (written with `tools/refcurve.py catalogue ... --out`, in this folder)
| Proposed target name | File | Source | n | Era | Est. LUFS (middle half) |
|---|---|---|---|---|---|
| `dubstep_2015` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_2015.json` | tag `dubstep`, 2015-2021, up to 300/year | 927 | 2015-2021 | -10.3 (-12.3 to -8.5) |
| `dubstep_2018` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_2018.json` | tag `dubstep`, 2018-2021, up to 300/year | 346 | 2018-2021 | -9.6 (-11.8 to -8.2) |
| `dubstep_2005` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_2005.json` | tag `dubstep`, 2005-2010, up to 300/year | 1277 | 2005-2010 | -12.2 (-14.5 to -10.5) |
| `dubstep_2011` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_2011.json` | tag `dubstep`, 2011-2014, up to 300/year | 866 | 2011-2014 | -10.2 (-12.2 to -8.9) |
| `dubstep_riddim` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_sub_riddim.json` | tag `riddim`, 2010-2021, up to 200/year | 81 | 2010-2021 | -7.6 (-8.8 to -6.3) |
| `dubstep_melodic` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_sub_melodic_dubstep.json` | tag `melodic dubstep`, 2010-2021, up to 200/year | 237 | 2010-2021 | -9.3 (-10.6 to -8.1) |
| `dubstep_brostep` | `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_sub_brostep.json` | tag `brostep`, 2010-2021, up to 200/year | 605 | 2010-2021 | -8.7 (-10.3 to -7.4) |

Also written, **not proposed as a target** (13 tracks): `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/dubstep_sub_deathstep.json`.

To install (after review; `add` never overwrites a built-in curve):
```bash
P=/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals
python3 tools/refcurve.py add $P/dubstep_2015.json
python3 tools/refcurve.py add $P/dubstep_2018.json --note "2018-2021 measured; 2022-2026 extrapolated; within 1 dB of dubstep_2015"
python3 tools/refcurve.py add $P/dubstep_2005.json --note "UK roots and deep / 140"
python3 tools/refcurve.py add $P/dubstep_2011.json --note "brostep years"
python3 tools/refcurve.py add $P/dubstep_sub_riddim.json --as-name dubstep_riddim --note "tag riddim 2010-2021, 81 tracks: thin, about +-1 dB"
python3 tools/refcurve.py add $P/dubstep_sub_melodic_dubstep.json --as-name dubstep_melodic
python3 tools/refcurve.py add $P/dubstep_sub_brostep.json --as-name dubstep_brostep   # optional: tag spans 2010-2021, superseded for era use by dubstep_2011
```
Exact commands that made them (each run under `flock /tmp/spectre-musicbrainz.lock`):
```bash
python3 tools/refcurve.py catalogue --tag dubstep --years 2015-2021 --per-year 300 --name dubstep_2015 --out $P/dubstep_2015.json
python3 tools/refcurve.py catalogue --tag dubstep --years 2018-2021 --per-year 300 --name dubstep_2018 --out $P/dubstep_2018.json
python3 tools/refcurve.py catalogue --tag dubstep --years 2005-2010 --per-year 300 --name dubstep_2005 --out $P/dubstep_2005.json
python3 tools/refcurve.py catalogue --tag dubstep --years 2011-2014 --per-year 300 --name dubstep_2011 --out $P/dubstep_2011.json
python3 tools/refcurve.py catalogue --tag riddim --years 2010-2021 --per-year 200 --name dubstep_sub_riddim --out $P/dubstep_sub_riddim.json
python3 tools/refcurve.py catalogue --tag "melodic dubstep" --years 2010-2021 --per-year 200 --name dubstep_sub_melodic_dubstep --out $P/dubstep_sub_melodic_dubstep.json
python3 tools/refcurve.py catalogue --tag brostep --years 2010-2021 --per-year 200 --name dubstep_sub_brostep --out $P/dubstep_sub_brostep.json
python3 tools/catalogue_stats.py tag --tag dubstep --years 2005-2021 --per-year 300 --by-year --fold 100-200
python3 tools/catalogue_stats.py tag --tag dubstep --years 2005-2021 --per-year 300 --span 3 --fold 100-200
python3 tools/catalogue_stats.py tag --tag <riddim|brostep|melodic dubstep|tearout|deathstep|future garage> --years 2008-2021 --per-year 200 --span 14 --fold 100-200
```
Note: the per-strand `refcurve` runs used `--per-year 200` over 2010-2021; the `tag` tables used 2008-2021. The `riddim` tag may include a few reggae riddims (its median tempo 145 and loudness -7.6 are dubstep's).

## 2. engine/genres.json: new entry `dubstep`
```json
"dubstep": {
 "name": "Dubstep, modern (2015-2026), original mix",
 "doc": "docs/DUBSTEP.md",
 "status": "researched 2026-11-25 (queue item 12); target measured from the open catalogue; loudness untested in the engine",
 "master": {
  "target": "dubstep_2015",
  "lufs": -8.0,
  "tp": -1.0,
  "eq": 0.7,
  "translate": 0.4,
  "mono_below": 150.0
 },
 "target_source": "MusicBrainz tag dubstep, first release 2015-2021, up to 300 per year; AcousticBrainz low-level Bark bands (CC0)",
 "target_era": "2015-2021",
 "target_tracks": 927,
 "target_method": "catalogue (tools/refcurve.py; docs/MASTERING.md 'Era targets')",
 "target_date": "2026-11-25",
 "era_targets": {
  "2015-2021 (the modern period pooled; default)": "dubstep_2015",
  "2019-2026, the newest sound (measured 2018-2021, 346 tracks; within 1 dB of dubstep_2015; 2022-2026 extrapolated)": "dubstep_2018",
  "UK roots and deep / 140 (2005-2010, 1,277 tracks)": "dubstep_2005",
  "brostep years (2011-2014, 866 tracks)": "dubstep_2011",
  "note": "the master uses `target`; a brief aimed at an era or strand passes `--target` (docs/DUBSTEP.md 'Mastering per subdivision')"
 },
 "master_by_strand": {
  "note": "loudness varies by strand more than by year since 2015 (whole tracks: riddim -7.6, brostep -8.7, melodic -9.3, all dubstep 2015-21 -10.3; loud sections of current releases -6, Mixgraph previews); pass the flags with --genre dubstep and check the loudest 2 minutes; none of these levels has been tested in the engine",
  "modern default": "--target dubstep_2015 --lufs -8 --tp -1",
  "newest sound (2019-2026)": "--target dubstep_2018 --lufs -8 --tp -1",
  "riddim, tearout, briddim": "--target dubstep_riddim --lufs -7 --tp -1 (only with clipped drum and bass buses; riddim curve from 81 tracks)",
  "melodic dubstep, colour bass": "--target dubstep_melodic --lufs -8.5 --tp -1",
  "deep / 140, UK roots": "--target dubstep_2005 --lufs -10 --tp -1",
  "a brief with a long quiet section (e.g. queue 12)": "--lufs -8.5, then read the drop's short-term loudness; lower --lufs rather than let a quiet outro push the drops harder"
 },
 "length": "3:30-4:30, aim about 3:50-4:00 (original mix; measured: tag dubstep median 4:06 in 2014-16, 4:02 in 2017-19, 3:42 in 2020-21 (middle half 3:15-4:21), 4:33-4:36 in 2008-13; riddim 3:39, melodic dubstep 4:18)",
 "form": "intro 8-32 bars (the drop near bar 32), build 8 (a 4-bar false drop optional), drop 1 16-32 bars in 8-bar halves with a switch at the half, breakdown or mid-section 8-16, build 8, drop 2 16-32 bars that differs from drop 1 (new drums, new bass or another strand), outro 8-16",
 "tempo": "140-150 bpm felt in half time (70-75); catalogue median 140 every year 2006-2018, 148 in 2019, 145 in 2020-21; riddim 145; Mixgraph median 145 (140-150), peak 150 in 2017; 140 for deep / 140 and colour bass, 145-150 for riddim, tearout and much melodic dubstep",
 "meter": "4/4 written at 140-150, kick on 1, snare (clap + snare) on 3; swung 16ths in the UK strands, triplet percussion in riddim, grid-tight in tearout",
 "change_rate": "something every 4-8 bars; a switch at the half of each drop (8 bars) in brostep and tearout; riddim holds one motif through a drop and changes it only by modulation",
 "role": "the bass is the lead: a mid-bass voice (or two in call and response) carries the hook; voices as chopped, pitched phrases and pre-drop calls",
 "hand_tuned": [
  "lufs -8 (and the strand levels -7 / -8.5 / -10): choices between measured whole-track medians and the -6 loud previews; untested in the engine",
  "translate 0.4",
  "eq 0.7",
  "mono_below 150 (inside the sourced 150-180 Hz side cut)"
 ],
 "sources": "docs/DUBSTEP.md 'Configuration', 'Catalogue measurements' and 'Mastering per subdivision' (Mixgraph dubstep BPM https://www.mixgraph.io/bpm-for/dubstep ; Mixgraph loudness by genre https://www.mixgraph.io/tools/lufs-meter ; catalogue lengths, tempo, loudness and curves by Spectre from MusicBrainz + AcousticBrainz, 2026-11-25; EDMProd, Cymatics, Futureproof, Infekt, iZotope/Skrillex 2011 for form, drums and mixing)"
}
```

## 3. data/catalogue_references.json: additions to `targets`
```json
{
 "dubstep_2015": {
  "tag": [
   "dubstep"
  ],
  "years": "2015-2021",
  "per_year": 300
 },
 "dubstep_2018": {
  "tag": [
   "dubstep"
  ],
  "years": "2018-2021",
  "per_year": 300
 },
 "dubstep_2005": {
  "tag": [
   "dubstep"
  ],
  "years": "2005-2010",
  "per_year": 300
 },
 "dubstep_2011": {
  "tag": [
   "dubstep"
  ],
  "years": "2011-2014",
  "per_year": 300
 },
 "dubstep_riddim": {
  "tag": [
   "riddim"
  ],
  "years": "2010-2021",
  "per_year": 200
 },
 "dubstep_melodic": {
  "tag": [
   "melodic dubstep"
  ],
  "years": "2010-2021",
  "per_year": 200
 },
 "dubstep_brostep": {
  "tag": [
   "brostep"
  ],
  "years": "2010-2021",
  "per_year": 200
 }
}
```
(`dubstep_brostep` only if that curve is added.) `tools/catalogue_stats.py targets` will then print the commands; it maps names to `--name`, so run it with the final names (`dubstep_riddim`, `dubstep_melodic`) rather than the file names used above.

## 4. engine/eqmaps.json: new entry `dubstep` (so `"genre": "dubstep"` projects get role presets and `listen --clarity --genre dubstep` works)
```json
"dubstep": {
 "source": "docs/DUBSTEP.md 'Layering and EQ carving': Cymatics, EDMProd, Futureproof mixing, iZotope (Skrillex 2011), Mixgraph; lead/pluck/pad rows from the trance and hip-hop maps [H]",
 "tolerance_db": 6,
 "inherit": "hiphop",
 "core": [
  "kick",
  "sub|808",
  "upper-bass|bass",
  "snare|clap",
  "hats|cymbals|perc"
 ],
 "roles": {
  "kick": {
   "hp": [
    25,
    30
   ],
   "cut": [
    [
     300,
     500
    ]
   ],
   "own": [
    [
     45,
     80
    ],
    [
     100,
     200
    ],
    [
     1000,
     5000
    ]
   ]
  },
  "sub": {
   "hp": [
    20,
    25
   ],
   "lp": [
    100,
    150
   ],
   "cut": [
    [
     200,
     400
    ]
   ],
   "own": [
    [
     30,
     80
    ]
   ]
  },
  "bass": {
   "hp": [
    90,
    150
   ],
   "cut": [
    [
     200,
     300
    ]
   ],
   "own": [
    [
     300,
     3000
    ]
   ]
  },
  "upper-bass": {
   "hp": [
    90,
    150
   ],
   "cut": [
    [
     200,
     300
    ]
   ],
   "own": [
    [
     300,
     3000
    ]
   ]
  },
  "snare": {
   "hp": [
    100,
    150
   ],
   "cut": [
    [
     300,
     700
    ]
   ],
   "own": [
    [
     180,
     250
    ],
    [
     2000,
     5000
    ],
    [
     8000,
     12000
    ]
   ]
  },
  "clap": {
   "hp": [
    150,
    250
   ],
   "cut": [
    [
     400,
     800
    ]
   ],
   "own": [
    [
     1000,
     8000
    ]
   ]
  },
  "hats": {
   "hp": [
    500,
    2000
   ],
   "cut": [
    [
     3000,
     6000
    ]
   ],
   "own": [
    [
     8000,
     14000
    ]
   ]
  },
  "pad": {
   "hp": [
    200,
    300
   ],
   "cut": [
    [
     200,
     500
    ]
   ],
   "own": [
    [
     1000,
     3000
    ],
    [
     8000,
     16000
    ]
   ]
  },
  "choir": {
   "hp": [
    200,
    300
   ],
   "cut": [
    [
     200,
     500
    ]
   ],
   "own": [
    [
     1000,
     3000
    ],
    [
     8000,
     16000
    ]
   ]
  },
  "lead": {
   "hp": [
    200,
    300
   ],
   "cut": [
    [
     300,
     600
    ]
   ],
   "own": [
    [
     1000,
     4000
    ]
   ]
  },
  "vocal": {
   "hp": [
    100,
    150
   ],
   "cut": [
    [
     200,
     400
    ]
   ],
   "own": [
    [
     2000,
     5000
    ]
   ]
  },
  "return": {
   "hp": [
    200,
    500
   ],
   "lp": [
    6000,
    12000
   ],
   "cut": [
    [
     300,
     600
    ]
   ]
  }
 }
}
```
Rows and their sources: docs/DUBSTEP.md "Layering and EQ carving". Roles not listed inherit from `hiphop`.

## 5. docs/ORCHESTRATION.md "Genre conventions": row and sources
Row:
```
| Dubstep, modern (2015-2026; strands: deep / 140, riddim, tearout, melodic, colour bass, hybrid); brief: docs/DUBSTEP.md (timeline 2005-10 / 2011-14 / 2015-18 / 2019-22 / 2023-26 and strands; a bleeding-edge checklist; engine gaps in "Engine mapping") | 3:30 to 4:30 (original mix; measured median 3:42 in 2020-21, 4:02-4:06 in 2014-19; riddim 3:39, melodic 4:18) | intro 8-32 bars (the drop near bar 32), build 8 (false drop optional), drop 1 16-32 in 8-bar halves with a switch at the half, breakdown 8-16, build 8, drop 2 16-32 that differs from drop 1, outro 8-16; something changes every 4-8 bars (riddim holds one motif through a drop); 140-150 bpm felt in half time (kick on 1, snare on 3): 140 for deep / 140 and colour bass, 145-150 for riddim, tearout, melodic (catalogue median 140 to 2018, 145-148 since 2019) | the bass is the lead: one or two mid-bass voices over a clean mono sub carry the hook; voices as chopped phrases and calls | `studio.py master vNNN --genre dubstep` (target `dubstep_2015`, -8 LUFS (untested), -1 dBTP, mono below 150 Hz); strands and eras pass `--target dubstep_2018 / dubstep_riddim / dubstep_melodic / dubstep_2005` and their levels (docs/DUBSTEP.md "Mastering per subdivision") |
```
Sources bullet:
```
- Dubstep (full table, catalogue and the mastering decision in docs/DUBSTEP.md, researched 2026-11-25): lengths, tempo and whole-track loudness by year and strand tag from the open catalogue (MusicBrainz + AcousticBrainz, `tools/catalogue_stats.py tag`: tag dubstep median 3:42 and 145 bpm in 2020-21, 140 bpm every year 2006-2018; riddim -7.6 est. LUFS, melodic dubstep -9.3); median 145 bpm, middle half 140-150 over 10,108 tracks ([Mixgraph](https://www.mixgraph.io/bpm-for/dubstep)); loud sections of releases -6 LUFS, the loudest club genre measured ([Mixgraph](https://www.mixgraph.io/tools/lufs-meter)); form from EDMProd ([riddim](https://www.edmprod.com/how-to-make-riddim/), [dubstep](https://www.edmprod.com/how-to-make-dubstep/)), [Cymatics](https://cymatics.fm/blogs/production/how-to-make-dubstep) and [Wikipedia](https://en.wikipedia.org/wiki/Dubstep); clip-first mastering ([Infekt](https://infektdubstep.com/masterclass/mastering/loudness/), [Futureproof](https://futureproofmusicschool.com/blog/mixing-mastering-dubstep-easy)); `dubstep_2015` from `tools/refcurve.py catalogue --tag dubstep --years 2015-2021` (927 tracks). **Hand-tuned:** -8 LUFS and the strand levels (untested in the engine), `eq` 0.7, `translate` 0.4, mono below 150 Hz, the 4-8-bar change rate (craft sources).
```
Also suggested for the "Master targets since 2026-11-25" paragraph: add `dubstep_2015` (plus `dubstep_2018`, `dubstep_riddim`, `dubstep_melodic`, `dubstep_2005`) to the list.

## 6. docs/MASTERING.md "Era targets": rows
Curve columns (dB re 1 kHz per 1/3 octave), to add to the curves table or as a second table:

| Hz | `dubstep_2015` | `dubstep_2018` | `dubstep_2005` | `dubstep_2011` | `dubstep_riddim` | `dubstep_melodic` | `dubstep_brostep` |
|---|---|---|---|---|---|---|---|
| 31.5 | +5 | +6 | +7.5 | +6 | +8.5 | +2 | +5.5 |
| 40 | +6.5 | +7 | +9.5 | +8 | +8 | +4 | +7 |
| 50 | +8 | +8 | +11 | +9.5 | +7.5 | +5.5 | +8 |
| 63 | +8 | +8 | +11 | +9.5 | +6 | +5.5 | +7.5 |
| 80 | +6.5 | +6.5 | +9 | +7.5 | +4.5 | +4.5 | +6 |
| 100 | +4.5 | +4.5 | +6.5 | +5.5 | +3 | +2.5 | +3.5 |
| 125 | +2.5 | +2.5 | +4.5 | +3.5 | +2 | +1 | +2 |
| 160 | +2 | +2 | +3.5 | +2.5 | +1 | +0.5 | +1.5 |
| 200 | +1.5 | +1.5 | +2.5 | +2 | 0 | +0.5 | +1.5 |
| 250 | +1 | +1 | +1.5 | +1.5 | -0.5 | 0 | +0.5 |
| 315 | +1 | +1 | +1 | +1 | -1 | 0 | 0 |
| 400 | +1 | +1 | +0.5 | +0.5 | -1 | 0 | -0.5 |
| 500 | +1 | +1 | +0.5 | 0 | -1 | 0 | -0.5 |
| 630 | +0.5 | +1 | +0.5 | 0 | -0.5 | +0.5 | 0 |
| 800 | +0.5 | +0.5 | 0 | 0 | 0 | +0.5 | 0 |
| 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1250 | -0.5 | -1 | -0.5 | -0.5 | 0 | -1 | -0.5 |
| 1600 | -1.5 | -1.5 | -0.5 | -1 | 0 | -1.5 | -0.5 |
| 2000 | -2 | -2 | -1 | -1.5 | -0.5 | -2 | -1 |
| 2500 | -3 | -2.5 | -1.5 | -1.5 | -0.5 | -3 | -1.5 |
| 3150 | -3.5 | -3 | -2.5 | -2.5 | -1 | -3.5 | -1.5 |
| 4000 | -4 | -3.5 | -3 | -2.5 | -1 | -4 | -2 |
| 5000 | -4.5 | -4 | -3.5 | -2.5 | -1 | -4 | -2 |
| 6300 | -4.5 | -4 | -3.5 | -2.5 | -1.5 | -4 | -2 |
| 8000 | -5 | -4.5 | -4.5 | -3 | -1.5 | -4 | -2 |
| 10000 | -6 | -5.5 | -6 | -4 | -2.5 | -5 | -2.5 |
| 12500 | -8 | -7.5 | -8.5 | -6.5 | -4 | -7 | -5 |
| 16000 | -12.5 | -12 | -12.5 | -10 | -7 | -11 | -8.5 |

Provenance rows:
| Target | Source (provenance) | Era | n | Est. loudness, median (middle half) | Against the nearest existing curve |
|---|---|---|---|---|---|
| `dubstep_2015` | MusicBrainz tag `dubstep`, first release 2015-2021, up to 300 per year | 2015-2021 | 927 | -10.3 (-12.3 to -8.5) | `trance_2015` reads within 1.2 dB of its Bark medians (mean 0.4 dB; 1 dB too bright at 7.7-12 kHz, 1 dB short at 32-97 Hz); `hiphop_2015` is 1-2 dB too dark at 3-12 kHz and 4 dB at 12-15.5 kHz (`refcurve.py check`) |
| `dubstep_2018` | tag `dubstep`, 2018-2021, up to 300 per year (2022-2026 extrapolated) | 2018-2021 | 346 | -9.6 (-11.8 to -8.2) | `dubstep_2015`: within 1 dB everywhere (+1 at 31.5 Hz, +0.5 at 2.5-10 kHz) |
| `dubstep_2005` | tag `dubstep`, 2005-2010 | 2005-2010 | 1,277 | -12.2 (-14.5 to -10.5) | `dubstep_2015`: +2.5 to +3 dB at 31.5-80 Hz, about +1 dB at 2-6 kHz |
| `dubstep_2011` | tag `dubstep`, 2011-2014 | 2011-2014 | 866 | -10.2 (-12.2 to -8.9) | `dubstep_2015`: +1.5 dB at 50-63 Hz, +1 to +2 dB at 3-10 kHz |
| `dubstep_riddim` | tag `riddim`, 2010-2021, up to 200 per year | 2010-2021 | 81 | -7.6 (-8.8 to -6.3) | `dubstep_2015`: +3.5 at 31.5 Hz, -2 dB at 63-100 Hz, -1.5 to -2 at 250-500 Hz, +3.5 to +5.5 dB at 5-16 kHz (thin: ±1 dB) |
| `dubstep_melodic` | tag `melodic dubstep`, 2010-2021 | 2010-2021 | 237 | -9.3 (-10.6 to -8.1) | `dubstep_2015`: -2.5 to -3 dB at 31.5-63 Hz, -1 dB at 250-500 Hz, +0.5 to +1.5 dB at 8-16 kHz |
| `dubstep_brostep` (optional) | tag `brostep`, 2010-2021 | 2010-2021 | 605 | -8.7 (-10.3 to -7.4) | `dubstep_2015`: -1 dB at 80-125 Hz, +2 to +3.5 dB at 3-10 kHz |
Caveats as for the other catalogue targets (user files, mono, Bark bands, ends 2021; lossless share 18-19% for 2005-14, 55-62% for the 2015-21 and strand sets).

## 7. Engine gaps (standing rule 19; details and workarounds in docs/DUBSTEP.md "Engine mapping")
Essential for queue item 12: (1) an FM growl voice (operators, ratio, index, feedback, unison; polyphonic); (2) tempo-synced, per-note modulation (rates in note values, retriggered, changeable per note; destinations incl. FM index, wavetable position, formant, drive); (3) a formant / vowel filter with a modulatable vowel position. Important: (4) wavetable oscillator with position morph and warp; (5) resampling (render a track or stack to audio and play it as a sampler voice, serially); (6) a multiband fx container; (7) more distortion types (wavefolder, asymmetric, hard clip with drive, modulated downsampler) and a tuned comb filter / flanger with feedback; (8) a clip-first loud master test (drops at -6.5 to -6 LUFS short-term). Nice to have: (9) formant shift on voices; (10) vocoder / resonator (chords from a growl); (11) gated reverb; (12) tempo-synced auto-filter and auto-pan fx. Already covered by the current engineering work: 909 snare (the 200 Hz dubstep snare body), resonance suppressor, granular freeze, shimmer, section automation of instrument parameters (per section, not per note), acid voice.

## 8. Also measured (in docs/DUBSTEP.md "Catalogue measurements")
Versions: of 12,472 MusicBrainz recordings tagged dubstep, "VIP" 0.8% (median 3:55), "Original Mix" 0.3% (4:27), "Extended Mix" 0.1% (5:05), "Radio Edit" 0.3% (3:33), "Remix" 11.3% (4:22): dubstep has one version, the original, so no `dubstep_radio`/extended variant is proposed. Colour bass tag: 21 tracks with data, 150 bpm, est. -9.7 LUFS. Deep dubstep: 4 tagged tracks with data (curve discarded); `color bass` and `deep dubstep` stats runs failed on MusicBrainz 503s.

## 9. Not measured / not sourced
True peak, PLR, LRA and width of dubstep releases (no open measurement); the loudness of deep / 140 and colour-bass releases (thin or failed tags: see docs/DUBSTEP.md); anything tonal after 2021 (extrapolated); the "wook" / experimental-bass strand (no defining source found); Beatport's dubstep sub-genres after 2017 beyond the "140 / Deep Dubstep / Grime" chart page; the drop-level loudness the engine can reach (no render allowed for this task).
