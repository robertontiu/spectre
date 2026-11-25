# Proposal: Latin pop brought up to PRODUCTION.md section 5, item 10 (2026-11-25)

From the Latin pop research agent, for the orchestrator to merge. The research itself is in **docs/LATIN_POP.md, new section "Granularity: strands, regions and eras"** (A-F, inserted before "Sources"), plus one superseded-in-part note appended to the "Test" paragraph of "The mastering decision". Nothing below has been applied to a shared file. No render, no master, no commit.

Curve files ready for `tools/refcurve.py add` (aggregates only: medians, spreads, n, provenance; no per-track data, no titles):
- `proposals/latinpop_curves/latinpop_urbano.json`
- `proposals/latinpop_curves/latinpop_mexicano.json`

## Summary of what the measurements changed
- **Two new strand targets are justified by data; three existing ones stay.** Urbano (reggaetón 2015-2021, 262 tracks) has 3.5-8 dB more than `latinpop_ref` at 40-63 Hz and 1-1.5 dB more at 2-5 kHz; banda and norteño (75 tracks, thin) have 6-9 dB less at 31.5-50 Hz and are 3-3.5 dB darker at 6.3-10 kHz. Tropical (salsa, cumbia, merengue, 473 tracks) and the ballad albums (72) fit `latinpop_ref` within the spread: no new target for them.
- **Contradiction flagged (docs/LATIN_POP.md "The mastering decision"):** the soft reggaetón-pop / romantic dembow strand was given the default curve. Its own reference albums (60 tracks) match the reggaetón tag within 1 dB from 50 Hz up and are 3.5-7 dB heavier than `latinpop_ref` at 31.5-63 Hz. Research decides: romantic dembow masters toward `latinpop_urbano` (or `hiphop_2015` until it is adopted, about 3 dB heavier again at 40-63 Hz).
- **Loudness differs less than expected** (whole-track estimates to 2021, ±1-2 dB): bolero -12.7; balada -10.2; acoustic -11.0; bachata -9.7 since 2010; reggaetón -10.0 to -10.8; Latin trap artists -9.6; banda and norteño -9.6; tropical -11.6. Urbano is not measurably louder than bachata or banda before 2022. Dynamics (Essentia dynamic complexity): bolero 4.3 and balada 4.4 dB vs bachata 3.0-3.4 (trance 3.2).
- **Not measurable from open data:** loudest-section loudness, true peak, PLR/LRA, width and low-end correlation for any strand; anything after 2021; corridos tumbados at all (3 tracks); Dominican dembow; Latin trap by tag (8 tracks; measured by artist instead).

## 1. engine/targets.json (add, forward only)
```
python3 tools/refcurve.py add <proposals>/latinpop_curves/latinpop_urbano.json
python3 tools/refcurve.py add <proposals>/latinpop_curves/latinpop_mexicano.json
```
Curves (dB re 1 kHz), for review:
| Hz | 31.5 | 40 | 50 | 63 | 80 | 100 | 125 | 160 | 200 | 250 | 315 | 400 | 500 | 630 | 800 | 1k | 1.25k | 1.6k | 2k | 2.5k | 3.15k | 4k | 5k | 6.3k | 8k | 10k | 12.5k | 16k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `latinpop_urbano` | +1.5 | +4 | +5.5 | +6 | +5.5 | +3.5 | +2 | +2 | +2 | +2 | +1 | +1 | +2 | +2.5 | +1 | 0 | -0.5 | -1 | -2 | -3 | -4 | -5 | -6 | -6 | -6.5 | -7.5 | -10.5 | -17 |
| `latinpop_mexicano` | -17.5 | -11.5 | -6 | -1.5 | +0.5 | +0.5 | -0.5 | -1 | -0.5 | +0.5 | 0 | 0 | +1 | +2 | +1 | 0 | -0.5 | -1 | -2.5 | -4.5 | -6 | -7.5 | -8.5 | -9.5 | -10 | -10.5 | -12.5 | -15 |
| `latinpop_ref` (for comparison) | -8.5 | -4 | 0 | +2.5 | +3.5 | +3 | +2 | +1.5 | +2 | +2 | +2 | +2 | +2.5 | +2.5 | +1.5 | 0 | -1 | -2 | -3 | -4 | -5.5 | -6.5 | -7.5 | -6.5 | -6.5 | -7.5 | -11.5 | -17.5 |
| `hiphop_2015` (for comparison) | +4.5 | +7 | +8.5 | +8.5 | +7.5 | +5.5 | +3.5 | +2.5 | +1.5 | +1 | +1 | +1.5 | +2.5 | +2 | +0.5 | 0 | -0.5 | -1 | -2 | -3 | -4 | -5 | -6 | -5.5 | -5.5 | -7 | -11 | -16.5 |

Provenance: `latinpop_urbano`: MusicBrainz tag `reggaeton`, first release 2015-2021, up to 150 per year, 262 tracks with AcousticBrainz data, 35% lossless, fit residual max 2.2 dB (16 kHz), mean 0.36; est. -10.3 LUFS (-13.0 to -8.7). `latinpop_mexicano`: artists Banda El Recodo, Los Tigres del Norte, Calibre 50, Christian Nodal, Grupo Firme (up to 80 recordings each), 75 tracks with data, mostly 2000-2019, 8% lossless (16 kHz rests on the smoothness term), est. -9.6 LUFS (-12.7 to -7.8). Both notes say what they do not cover (dembow, tumbados).

## 2. data/catalogue_references.json, "targets" (so `catalogue_stats.py targets --run` rebuilds them)
```json
"latinpop_urbano": {"tag": ["reggaeton"], "years": "2015-2021", "per_year": 150},
"latinpop_mexicano": {"artist": ["Banda El Recodo", "Los Tigres del Norte", "Calibre 50", "Christian Nodal", "Grupo Firme"], "limit": 80}
```
Other selections used in the doc (not targets; for reproduction, optional under a new "latinpop_granularity" key or just in the doc): tag `reggaeton` 2004-2014 per_year 60 (257 tracks); tags `salsa`, `cumbia`, `merengue` 2005-2021 per_year 60 (473); tag `bachata` 1995-2021 per_year 30 (90); Latin trap artists Anuel AA, Bryant Myers, Brytiago, Noriel, Eladio Carrión, Lary Over, Darell, Arcángel, limit 80 (100). Warning for whoever extends the trap list: the artist search for "Almighty" returns the British rock band The Almighty (57 contaminating tracks in a first run); it was dropped.

## 3. engine/genres.json, "latinpop"
Keep `master` as is (default `latinpop_ref`, -11, -1, 0.6, 0.3, mono 120): a brief that names no strand still gets it. Proposed changes:
- `"name"`: "Latin pop: bachata, bolero / balada, Latin pop ballad, acoustic pop, reggaetón and romantic dembow, Latin trap and dembow, música mexicana, tropical (strand targets in docs/LATIN_POP.md 'Granularity', D)".
- New key (documentation for the producer brief and the orchestrator; `master.py` does not read it unless the engine adds a `--strand` flag, proposed below):
```json
"strands": {
  "bolero":        {"target": "latinpop_dark",     "lufs": -12.5, "eq": 0.6, "translate": 0.3},
  "acoustic":      {"target": "latinpop_dark",     "lufs": -11.5, "eq": 0.6, "translate": 0.3},
  "ballad":        {"target": "latinpop_ref",      "lufs": -10.5, "eq": 0.6, "translate": 0.3},
  "bachata":       {"target": "latinpop_bright",   "lufs": -10.0, "eq": 0.6, "translate": 0.3},
  "urbano":        {"target": "latinpop_urbano",   "lufs": -10.5, "eq": 0.7, "translate": 0.5, "covers": "reggaeton, romantic dembow / reggaeton-pop, Latin trap, Dominican dembow (extrapolated)"},
  "mexicano":      {"target": "latinpop_mexicano", "lufs": -10.0, "eq": 0.5, "translate": 0.3, "covers": "banda, norteno; corridos tumbados and sierreno extrapolated", "data": "thin"},
  "tropical":      {"target": "latinpop_ref",      "lufs": -11.5, "eq": 0.6, "translate": 0.3, "covers": "salsa, cumbia, merengue"}
}
```
  Evidence per row: docs/LATIN_POP.md "Granularity" D (measured loudness per strand; `eq` 0.7 for urbano as for `hiphop` because n = 262 on one tag; 0.5 for mexicano because the data is thin [H]; `translate` 0.5 for urbano as for `hiphop`/`trap`, an 808 that must survive phones [S: docs/MASTERING.md]). True peak -1 dBTP and mono below 120 Hz for all: no strand evidence to differ.
- `"status"` append: "; 2026-11-25: granularity research (strands, regions, eras), two strand targets proposed (`latinpop_urbano`, `latinpop_mexicano`) and per-strand loudness from the catalogue".
- `"target_change"` append: "; romantic dembow / reggaetón-pop should use `latinpop_urbano` (its albums are 3.5-7 dB heavier at 31.5-63 Hz than `latinpop_ref`)".
- `"tempo"` append: "; wider strands: reggaetón 93-96 (2024 median 98, Mixgraph), Dominican dembow 115-140 [S], banda and norteño about 105, tropical about 113 (pooled)".
- `"length"` append: "; urbano singles 3:13-3:36 and shrinking (2021: 3:13), banda and norteño about 3:06, tropical about 4:00-4:25".

## 4. docs/MASTERING.md
- Genre table, `latinpop` row, "Target curve" cell: "`latinpop_ref` (24 albums); by strand `latinpop_dark` (bolero, acoustic), `latinpop_bright` (bachata), `latinpop_urbano` (reggaetón, romantic dembow, Latin trap), `latinpop_mexicano` (banda, norteño; tumbados extrapolated, thin); per-strand loudness -12.5 to -10 (docs/LATIN_POP.md 'Granularity' D)".
- "Era targets" provenance table, two new rows:
  | `latinpop_urbano` | MusicBrainz tag `reggaeton`, 2015-2021 (also fits the romantic dembow albums and a Latin trap artist set) | 2015-2021 | 262 | -10.3 (-13.0 to -8.7) | against `latinpop_ref`: +5.5 to +10 dB at 31.5-50 Hz, +3.5 at 63, +1 to +1.5 dB at 2-5 kHz; against `hiphop_2015`: about 3 dB less at 40-63 Hz, the same top |
  | `latinpop_mexicano` | banda and norteño by artist (Banda El Recodo, Los Tigres del Norte, Calibre 50, Christian Nodal, Grupo Firme); **thin**, 8% lossless; tumbados extrapolated | mostly 2000-2019 | 75 | -9.6 (-12.7 to -7.8) | against `latinpop_ref`: -9 to -6 dB at 31.5-50 Hz, -3 to -3.5 dB at 6.3-10 kHz, 2.5 dB brighter at 16 kHz |
- The curve comparison table (line ~124): add the two columns from section 1 above.
- A sentence under "Era targets": "Mastering beyond the curve, per strand (loudness, dynamics, low end, top, playback; what open data can and cannot measure): docs/LATIN_POP.md 'Granularity' D. Loudness differs little between Latin strands before 2022 (-9.6 to -11.6 LUFS, bolero -12.7); the low end differs by 12-20 dB at 31.5-50 Hz."

## 5. docs/MANUAL.md (engine docs; when 1-3 are adopted)
In the `--genre` paragraph, `latinpop` entry: after "for bachata `--target latinpop_bright`" add "for reggaetón, romantic dembow and Latin trap `--target latinpop_urbano --lufs -10.5 --translate 0.5`, for banda, norteño and corridos tumbados `--target latinpop_mexicano` (thin data); loudness per strand in docs/LATIN_POP.md 'Granularity' D".

## 6. docs/PRODUCTION.md
- Section 3, the measurement table's Latin row, add after the row (or in "Reading it", item 5 caveats): "The `latin` tags pool strands that differ by 12-20 dB at 31.5-50 Hz (urbano vs banda and norteño) and by up to 13 dB at 12.5-16 kHz (bachata vs bolero): docs/LATIN_POP.md 'Granularity' splits them."
- Section 6, engine item 1 "[BUILT ...]": the list of era targets gains `latinpop_urbano`, `latinpop_mexicano` once added ("nine" becomes "eleven", counting `trance_2018` if it is already there: check the current count).

## 7. docs/ORCHESTRATION.md
- Genre conventions row for Latin pop (line ~53): the name "Latin pop, intimate strands (...)" becomes "Latin pop (strands: bachata, bolero / balada, acoustic, reggaetón and romantic dembow, Latin trap and dembow, música mexicana, tropical; docs/LATIN_POP.md 'Granularity')"; add to its master cell: "the brief names its strand; `{{MASTER}}` = `--genre latinpop` plus the strand's `--target` and `--lufs` from 'Granularity' D; no strand named = the default".
- When briefing a Latin session: the brief must name strand (and optionally era and region); for "the newest sound" point the producer at the checklist in E and mark the tonal target as extrapolated (no data after 2021).

## 8. docs/LESSONS.md (one line, optional)
- "Latin pop is several low ends: measure the strand before choosing the curve. The romantic dembow albums are 3.5-7 dB heavier at 31.5-63 Hz than the default `latinpop_ref`; banda and norteño 6-9 dB lighter (2026-11-25, catalogue)."

## 9. Engine proposals (for an engineering agent; none blocks a session)
Ranked by how many strands they unlock [H]:
1. **Latin percussion models**: congas, timbales (with cáscara and rolls), bongó (open, slap, martillo), güira (a brush on a metal grater, long-scrape envelope), güiro, tambora. Unlocks bachata, tropical and classic reggaetón (timbal rolls); the existing doc already lists them.
2. **A pitch-correction ("tune") fx on `svs` voices**: snap the pitch curve to the scale with a retune speed, for the Auto-Tune sound of urbano, Latin trap and tumbados (Wikipedia: Latin trap "often with autotune"; tumbados "auto-tuned vocals").
3. **Low brass and bass for música mexicana**: tuba, tololoche (upright bass), charcheta, trumpet, trombone; a 12-string course doubling on `acguitar`.
4. **Accordion** (cumbia, norteño, vallenato).
5. **A rhythmic speech or chant voice** for chanteo, rap and dembow call-and-response (none exists; consent and licence questions as for any new voice: standing rule 10).
6. **`--strand` on the master** reading the `strands` map of genres.json, so `{{MASTER}}` can be `--genre latinpop --strand urbano` instead of three flags.
7. **Caribbean and Castilian Spanish in `lang_es.py`** (s-aspiration, Castilian `th`), already "Still open" in docs/voice/languages/es.md.

## What could not be sourced or measured (say so in briefs)
- Loudest-section loudness, true peak, PLR, LRA, stereo width and low-end mono point for any Latin strand (no open data; no published figures found; only `refcurve.py measure` on bought references can supply them).
- Any tonal or loudness figure after 2021: every 2022-2026 statement in the doc is from sources, and the targets are extrapolated for current briefs.
- Corridos tumbados (no open data; tempo only as "fast 6/8"; tuba vs no tuba disagrees between sources: Wikipedia and Soundtrap's lineups differ), Dominican dembow (tempo from TIDAL and Orphiq only), salsa, cumbia and merengue separately (pooled), guaracha's tempo.
- No engineer's mix account for bachata, bolero, reggaetón (beyond the Despacito remix vocal bus already in the doc) or corridos; Bad Bunny's mastering engineer is quoted on goals only, no settings.
- Region inside a strand (e.g. Medellín vs Puerto Rico reggaetón) is sourced descriptively only; not measured.
