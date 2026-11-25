# Proposal: Romanian traditional and lăutar music brought up to PRODUCTION.md item 10 (2026-11-25)

Research agent for docs/ROMANIAN.md and docs/JOC_TIGANESC.md. Edited directly (not committed): docs/ROMANIAN.md (new section "Regions, scenes and eras: the granularity of Romanian folk music", inserted before "Anthem"; the anthem material is untouched) and docs/JOC_TIGANESC.md (new section "Where the joc sits: regions, scenes and their settings", after the era assessment). Everything below touches shared files and is for the orchestrator to merge.

Curve files written with `tools/refcurve.py catalogue --out` (under `flock /tmp/spectre-musicbrainz.lock`), in `/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/romanian_curves/`:
- `ro_fanfare.json` (proposed target): Fanfare Ciocărlia, MBID a98da524-e565-4d89-b729-17d5a5fe75e0, `--limit 300`; n 105, 1997-2016, est. -11.7 LUFS (-13.3 to -10.8); fit max residual 1.3 dB.
- `ro_fusion.json` (proposed target): Subcarpați b115f23e-c1f3-4cbe-95b5-615276ade5f9, Zdob și Zdub 06b13f0d-b1d4-4e29-8b74-d80b63813e32, Mahala Raï Banda 21cc597f-1ed6-4a00-b728-4ec0d3b811e3, Shukar Collective b629d16d-6560-4cb4-8f24-afdcc1d44803, Balkan Taksim 596d9e3e-31dc-484d-a9d4-93fbf69222fa, Dirty Shirt acc451d7-bd3c-4b09-8508-eb52133772c4, `--limit 100`; n 138, 1997-2022, est. -10.9 LUFS (-13.0 to -9.1); fit max residual 1.5 dB.
- `ro_transylvania_revival.json` (proposed **interim proxy** target): Muzsikás 7b85a62b-1d39-4580-bfcc-8668a70fcfcd, Kálmán Balogh b642bae2-eb1e-467a-8cf9-eb7f5fe4da63, `--limit 200`; n 69, 1986-2008, est. -15.1 LUFS (-17.0 to -13.5); fit max residual 4.5 dB at 15.5-20.5 kHz (the lossless subset), 0.5 dB mean. Hungarian revival musicians playing Transylvanian village music: a stand-in, to be replaced by village recordings measured locally.
- `ro_urban_vintage.json` (**not** a target, reference only): Maria Tănase, Romica Puceanu, Gabi Luncă, Toni Iordache, Fănică Luca, Dona Dumitru Siminică, Gheorghe Zamfir; n 56; band-limited period recordings (4-11 dB under the taraf above 4 kHz).
- `ro_taraf_check.json` (validation only): Taraf de Haïdouks `--limit 300`; n 103, identical to `joc_taraf` in `engine/targets.json`. Do not add.

Thin or empty sets (no file written): manele (14 tracks with data from 6 artists, none lossless; agrees with `ro_fusion` within 1-3 dB), muzică populară (17 tracks, 12 of one singer), Maramureș/Oaș, Banat, Dobrogea, Oltenia, Bukovina village bands (no artist with AcousticBrainz data found: Szászcsávás Band 0/31, Fanfara Zece Prăjini 0/77, Maria Ciobanu, Irina Loghin, Ion Dolănescu 0 each).

## 1. engine/targets.json (via `tools/refcurve.py add`)
```
python3 tools/refcurve.py add <proposals>/romanian_curves/ro_fanfare.json --note "Moldavian brass fanfare (Fanfare Ciocarlia), docs/ROMANIAN.md 'Mastering by subdivision'"
python3 tools/refcurve.py add <proposals>/romanian_curves/ro_fusion.json --note "Romanian/Moldovan folk fusion, 6 artists 1997-2022; also the nearest measured set for manele and amplified wedding bands"
python3 tools/refcurve.py add <proposals>/romanian_curves/ro_transylvania_revival.json --note "INTERIM PROXY: Hungarian revival bands playing Transylvanian village music; replace with local measurements"
```

## 2. engine/genres.json, entry `joc`
(a) **Loudness, a flagged contradiction**: `master.lufs` -11 is marked hand-tuned ("a choice inside the sourced folk range"); the measured taraf records the target is built on sit at -13.1 (middle half -15.5 to -12.1, n 103), so -11 is louder than three quarters of them. Research decides: propose `"lufs": -13.0`, and replace the hand_tuned line `"lufs -11: a choice inside the sourced folk range of -14 to -10"` with a source line `"lufs -13: the median estimated loudness of the 103 Taraf de Haidouks recordings behind joc_taraf (middle half -15.5 to -12.1; docs/ROMANIAN.md 'Mastering by subdivision'); -12 at most for a dance-floor version"`. `master_published` unchanged (010 keeps its master until a remaster is approved).

(b) Add a `subdivisions` object (read by people and the orchestrator, not by the engine; `--target`, `--lufs`, `--eq` on the command line apply them):
```json
"subdivisions": {
  "_about": "Which master settings each kind of Romanian folk brief uses (docs/ROMANIAN.md 'Regions, scenes and eras', 'Mastering by subdivision'). Region and scene are named in the brief; a brief that names none takes 'fusion'. eq values are hand-tuned to each set's size and spread.",
  "taraf":        {"target": "joc_taraf", "eq": 0.4, "lufs": -13.0, "tp": -1.0, "basis": "measured: 103 Taraf de Haidouks recordings 1993-2015"},
  "fanfare":      {"target": "ro_fanfare", "eq": 0.5, "lufs": -12.0, "tp": -1.0, "basis": "measured: 105 Fanfare Ciocarlia recordings 1997-2016 (one band)"},
  "transylvania_strings": {"target": "ro_transylvania_revival", "eq": 0.3, "lufs": -15.0, "tp": -1.0, "basis": "interim proxy: 69 recordings of Hungarian revival bands 1986-2008"},
  "acoustic_unmeasured": {"target": "joc_taraf", "eq": 0.3, "lufs": -14.0, "tp": -1.0, "basis": "no data: Maramures, Bihor, Banat, Dobrogea, peasant/pastoral; the nearest acoustic set, hand-tuned lighter and quieter"},
  "urban_period":  {"target": "joc_taraf", "eq": 0.3, "lufs": -13.5, "tp": -1.0, "basis": "period recordings (56, band-limited) are not a target; loudness = their median; period colour is sound design"},
  "wedding_band":  {"target": "ro_fusion", "eq": 0.5, "lufs": -11.0, "tp": -1.0, "basis": "no wedding recordings measured; nearest measured amplified band (Mahala Rai Banda, in ro_fusion)"},
  "manele":        {"target": "ro_fusion", "eq": 0.5, "lufs": -11.0, "tp": -1.0, "basis": "14 recordings (thin) agree with ro_fusion within 1-3 dB; with an 808 trap beat use the host genre (trap or hiphop_2015)"},
  "fusion":        {"target": "ro_fusion", "eq": 0.6, "lufs": -11.0, "tp": -1.0, "basis": "measured: 138 recordings, 6 artists, 1997-2022; 2023-2026 not measured; with a dominant 808 use hiphop_2015"}
}
```
All subdivisions keep `translate` 0.3 and `mono_below` 120 (no scene-specific source; AcousticBrainz has no width data).

(c) `status` append: `"; 2026-11-25: regions and scenes researched (docs/ROMANIAN.md), per-subdivision settings in 'subdivisions'"`.

(d) Optional, if the orchestrator wants a genre for Romanian folk fusion briefs (sessions 004 and 011 used `trap`/`hiphop`): no new genre entry is proposed. The fusion briefs take their host genre's configuration (length, form, tempo) plus docs/ROMANIAN.md for the folk material, and master with `--target ro_fusion --eq 0.6 --lufs -11` unless the 808 dominates.

## 3. data/catalogue_references.json, `targets`
```json
"ro_fanfare": {"artist": ["a98da524-e565-4d89-b729-17d5a5fe75e0"], "limit": 300, "names": ["Fanfare Ciocărlia"]},
"ro_fusion": {"artist": ["b115f23e-c1f3-4cbe-95b5-615276ade5f9", "06b13f0d-b1d4-4e29-8b74-d80b63813e32", "21cc597f-1ed6-4a00-b728-4ec0d3b811e3", "b629d16d-6560-4cb4-8f24-afdcc1d44803", "596d9e3e-31dc-484d-a9d4-93fbf69222fa", "acc451d7-bd3c-4b09-8508-eb52133772c4"], "limit": 100, "names": ["Subcarpați", "Zdob și Zdub", "Mahala Raï Banda", "Shukar Collective", "Balkan Taksim", "Dirty Shirt"]},
"ro_transylvania_revival": {"artist": ["7b85a62b-1d39-4580-bfcc-8668a70fcfcd", "b642bae2-eb1e-467a-8cf9-eb7f5fe4da63"], "limit": 200, "names": ["Muzsikás", "Kálmán Balogh"]}
```
MBIDs, not names: `refcurve.py` resolves a name to the first search hit, and several names here have ambiguous hits ("Téka" resolves to a German reggae producer; "Paulina" to a Galician singer). If `catalogue_stats.py targets` cannot take a `names` key, drop it.

## 4. docs/MASTERING.md, "Era targets"
Add to the per-target provenance table:
```
| `ro_fanfare` | MusicBrainz artist Fanfare Ciocărlia (MBID; docs/ROMANIAN.md "Mastering by subdivision") | releases 1997-2016 | 105 | -11.7 (-13.3 to -10.8) | `joc_taraf`: 4-8 dB brighter at 5-15 kHz, as heavy at 32-97 Hz, 1-2 dB lighter at 100-160 Hz |
| `ro_fusion` | MusicBrainz artists Subcarpați, Zdob și Zdub, Mahala Raï Banda, Shukar Collective, Balkan Taksim, Dirty Shirt (MBIDs) | releases 1997-2022 | 138 | -10.9 (-13.0 to -9.1) | `joc_taraf`: 7-12 dB brighter at 5-15 kHz, 3-7.5 dB heavier at 50-80 Hz; `hiphop_2015`: within 2 dB from 160 Hz up, 1.5-8.5 dB less at 31.5-80 Hz |
| `ro_transylvania_revival` (interim proxy) | MusicBrainz artists Muzsikás, Kálmán Balogh (MBIDs): Hungarian revival musicians playing Transylvanian village music | releases 1986-2008 | 69 | -15.1 (-17.0 to -13.5) | `joc_taraf`: 2-3.5 dB lighter at 50-183 Hz, 2.5-3.5 dB brighter at 5-10 kHz, 2 dB darker above 12 kHz |
```
and the curves (dB re 1 kHz) as a new small table "Romanian folk scenes (2026-11-25, docs/ROMANIAN.md)":
| Hz | `ro_fanfare` | `ro_fusion` | `ro_transylvania_revival` |
|---|---|---|---|
| 31.5 | -20.5 | -4 | -20.5 |
| 40 | -13 | -0.5 | -14 |
| 50 | -5.5 | +3 | -8 |
| 63 | 0 | +5 | -3 |
| 80 | +2.5 | +6 | 0 |
| 100 | +2 | +5 | +1 |
| 125 | +0.5 | +4 | -0.5 |
| 160 | 0 | +2.5 | -2 |
| 200 | +0.5 | +2 | -1 |
| 250 | +1 | +1.5 | +0.5 |
| 315 | +1 | +1 | +1.5 |
| 400 | +1 | +1 | +1.5 |
| 500 | +0.5 | +2 | +1 |
| 630 | 0 | +2 | +0.5 |
| 800 | -0.5 | +1 | +0.5 |
| 1000 | 0 | 0 | 0 |
| 1250 | 0 | 0 | -0.5 |
| 1600 | -1 | -0.5 | -1.5 |
| 2000 | -2 | -1.5 | -2 |
| 2500 | -2.5 | -1.5 | -2.5 |
| 3150 | -3.5 | -2 | -3.5 |
| 4000 | -5 | -3 | -5 |
| 5000 | -7.5 | -4.5 | -8.5 |
| 6300 | -9 | -5.5 | -11.5 |
| 8000 | -10.5 | -6.5 | -14 |
| 10000 | -13 | -8.5 | -17 |
| 12500 | -17 | -11.5 | -22.5 |
| 16000 | -23 | -16.5 | -29 |

Caveat line: "16 kHz rests on the smoothness term for all three (fewer than 20 lossless files in the fanfare and Transylvanian sets; 29% lossless in fusion); the fanfare set is one band; the Transylvanian set is a proxy. Period recordings of urban lăutari (56 tracks) were measured and rejected as a target: band-limited."
Also in the `joc` row of the genre table: LUFS -11 → -13 if 2(a) is accepted.

## 5. docs/ORCHESTRATION.md, "Genre conventions"
(a) Replace the Master cell of the joc row (it still names the borrowed `rock` curve) with:
`studio.py master vNNN --genre joc` (`joc_taraf`, eq 0.4, -13 LUFS if proposal 2(a) is accepted, else -11; -1 dBTP); **the brief names its region and scene** (docs/ROMANIAN.md "Regions, scenes and eras"): fanfare `--target ro_fanfare --eq 0.5 --lufs -12`, Transylvanian string band `--target ro_transylvania_revival --eq 0.3 --lufs -15`, amplified wedding band or manele `--target ro_fusion --eq 0.5 --lufs -11`

(b) New row after the joc row:
`| Romanian folk by region and scene (folk fusion over hip hop or electronics: the current-practice default; any regional village style; fanfare; manele); brief: docs/ROMANIAN.md "Regions, scenes and eras" (and docs/JOC_TIGANESC.md for the Muntenian taraf) | the host genre's length for fusion; village dance tracks by the dance (catalogue medians: taraf 4:35, fanfare 3:18, fusion 3:51) | by region: dance cycles slow to fast; 2/4 almost everywhere with regional asymmetric meters (Dobrogea 7/16 and 9/16, Banat 7/8, south Transylvania 10/16); the brief names region and scene, or takes current practice (folk material over a current beat) | one lead over an afterbeat and a bass; strigături except in Banat; no Romanian singing voice yet | per subdivision, see genres.json `joc.subdivisions` (fusion: --target ro_fusion --eq 0.6 --lufs -11) |`

(c) Sources paragraph line: "Romanian regions and scenes (docs/ROMANIAN.md, researched 2026-11-25): dialects after Bartók and Brăiloiu (Wikipedia, 'Romanian traditional music'); instrumentation, dances and meters by region (eliznik.org.uk); Maramureș (Rădulescu & Bouët, Smithsonian Folkways UNES 08310); the Transylvanian Plain (Kotansky; Fonó's *Buza*); manele (RomArchive); current listening (Europa Liberă / INSCOP 2023); loudness and spectra per scene measured on AcousticBrainz (n 56-138 per scene; manele and muzică populară too thin). **Hand-tuned:** eq per subdivision; the settings of the unmeasured regions."

## 6. docs/PRODUCTION.md, remix table (item 9)
- 010 Unison (joc): if remastered, the target is `joc_taraf` (as already planned) and the loudness **-13** (measured), not -11; owner's approval as for every remaster.
- 004 (Romanian folk trap): no remaster implication; note for a remix that its "geampara feel" used a 3-3-2 layout, which is long-long-short, not geampara's short-short-long (docs/ROMANIAN.md "Rhythm cells").
- 011 (anthem hip hop): unaffected (its folk content is the anthem, not a regional style).

## 7. docs/LESSONS.md (principle, optional)
"Romanian folk is a set of dialects, not a scale: a brief names the region and the scene (or takes current practice), and the brief's meter, ensemble and master follow that cell (docs/ROMANIAN.md). The 'Romanian minor' #4 and the augmented second are southern/Bihor/lăutar colours, not national defaults."

## 8. Engine gaps (for the queue; no shared file needed)
Missing, by how many subdivisions need them: accordion; clarinet/taragot/saxophone; brass (trumpet, tenor and baritone horn, tuba, trombone); acoustic double bass (plucked, short-bowed, struck gordon); contră/braci (bowed triads, two pulses per stroke); zongoră (a `acguitar` tuning preset might do); fluier/caval/tilincă and bucium/tulnic; an arranger keyboard ("orgă"); a Romanian singing voice; melodic notes on aksak grids (melodic tokens are fixed to 16ths of a four-beat bar, so 7/16, 9/16, 10/16 melodies only fit approximately; drums and chord stabs already take any grid).

## 9. What could not be sourced or measured
- Tempo per region (no survey; AcousticBrainz scene medians 115-129 bpm don't separate scenes); the manea rhythm pattern; how loudness is reached (limiting, clipping) in any scene; true peak, PLR, width and the loudest section for any scene; anything 2023-2026 (AcousticBrainz ends in 2022); village recordings of Maramureș, Banat, Bihor, Dobrogea, Oltenia, Bukovina; muzică populară and manele in usable numbers; the Serbian kolo's direct influence on Banat Romanian music; the 2026 Subcarpați album listed on Wikipedia.
- Read only through citing sources: Bartók's Romanian volumes, Garfias 1981, Miller 1986, *Manele in Romania* (2016).
