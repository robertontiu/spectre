# data/

Small derived data the tools need to reproduce the numbers the docs and the engine use. No audio, no downloaded pages or API dumps (those stay in `~/.cache/spectre/refs/`, outside git).

- `catalogue_references.json`: which records the genre research measured, as identifiers. `albums`: the reference albums of docs/CAROLING.md, docs/LATIN_POP.md, docs/CHAMBER_SCORE.md and docs/CINEMATIC_HYBRID.md (`cinematic`, 2026-11-26) ("Catalogue measurements"), as MusicBrainz release MBIDs with artist, title and strand, plus the tempo folds and quantile conventions those tables used. `targets`: the tag, years, artist or release subset of every era target in `engine/targets.json`.
  - Used by `tools/catalogue_stats.py` (`albums <genre>` reproduces the tables, `targets` prints or runs the `tools/refcurve.py` commands for the era targets).
  - Provenance: chosen during the genre research of 2026-11-24 and the era targets of 2026-11-25; extracted from the docs' tables (every MBID matches the releases cached by `refcurve.py`). Re-running the targets from it reproduces `engine/targets.json` exactly (checked for five of the nine, 2026-11-25).
  - Licence: MusicBrainz identifiers and titles are MusicBrainz core data (CC0); AcousticBrainz data is CC0. The selection is this project's (MIT, like the repo).
