# Proposal: caroling brought up to PRODUCTION.md item 10 (strands, eras, current practice, masters per strand)

From the caroling research agent, 2026-11-25. The research itself is in **docs/CAROLING.md, "Granularity: strands, eras and the current carol"** (edited in the working tree, not committed). Everything below changes shared files I was told not to edit; the orchestrator decides and merges.

Files next to this proposal (folder `proposals/caroling/`):
- `caroling_choir.json`: refcurve catalogue curve, 23 choir albums (UK cathedral/collegiate + US concert choirs), 1986-2012, n 106, 64% lossless, residual ≤2.5 dB, est. -22.3 LUFS (-24.3 to -19.7). Track list included.
- `caroling_acappella.json`: 8 a cappella Christmas albums (Pentatonix 2014-2018, Straight No Chaser 2008-2016, Take 6 1991; Home Free 2010 listed but has no data), 1991-2018, n 87, 29% lossless (25 files, so 16 kHz is fitted), residual ≤1.9 dB, est. -12.5 LUFS (-14.4 to -10.2). Track list included.
- `catalogue_references_additions.json`: the album lists (artist, album, year, MBID) for both, for data/catalogue_references.json.
- `caroling_stats.json`: per-strand and per-album aggregates (est. LUFS, Essentia dynamic complexity, low and air bands, length).

Both curves were produced by `flock /tmp/spectre-musicbrainz.lock python3 tools/refcurve.py catalogue --release ... --list-tracks --out ...` (the exact release lists are in the additions file); `refcurve.py check caroling_ref --against caroling_choir.json` loads them fine (max difference 14.9 dB, mean 4.1 dB against the current target).

## The finding in one paragraph
`caroling_ref` (the five albums) averages two different masters. Choir records (B) and a cappella records (D) differ by 20-25 dB at 50-100 Hz, 16-20 dB at 6.3-10 kHz, 9-10 dB in loudness (-22 vs -12.5 LUFS) and by a factor of two in dynamics (Essentia dynamic complexity 7.7-8.3 vs 4.0). UK and US choirs measure the same (within 3.5 dB per band, -22.5 vs -21.6 LUFS), so region is not a separate target. Crooner reissues (-14.1) and the mid-century choral reissues (-18.5, thin) sit near `caroling_ref`; brass (-18.1) is as dark as the choirs. Session 012 was mastered at dynamic complexity 2.9 (-14.0 LUFS, LRA 5.2 LU, PLR 12.9): a pop-carol master. 

## 1. engine/targets.json (add two curves)
```
python3 tools/refcurve.py add <proposals>/caroling/caroling_choir.json --note "choir carols, 23 albums 1986-2012 (docs/CAROLING.md, Granularity)"
python3 tools/refcurve.py add <proposals>/caroling/caroling_acappella.json --note "a cappella Christmas, 8 albums 1991-2018 (docs/CAROLING.md, Granularity)"
```
`caroling_ref` stays (the default).

## 2. engine/genres.json, `caroling`
Keep `master` as it is (caroling_ref, -14, eq 0.3, max_low_boost_db 0): it stays the default for a brief that names no strand. Add a strand block (or whatever form the engine uses for per-strand settings; today a producer would pass the flags by hand):
```json
"master_strands": {
  "_about": "docs/CAROLING.md 'Granularity': a brief names its strand; no strand = `master` above. Measured 2026-11-25 (AcousticBrainz via tools/refcurve.py); loudness values marked hand_tuned are choices inside the measured ranges.",
  "choir":     {"target": "caroling_choir",     "lufs": -18.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0},
  "acappella": {"target": "caroling_acappella", "lufs": -12.0, "tp": -1.0, "eq": 0.5, "translate": 0.3, "mono_below": 120.0},
  "brass":     {"target": "caroling_choir",     "lufs": -18.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0},
  "street":    {"target": "caroling_ref",       "lufs": -16.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0},
  "handbells": {"target": "caroling_ref",       "lufs": -16.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0},
  "crooner":   {"target": "caroling_ref",       "lufs": -14.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0},
  "midcentury_era": {"target": "caroling_ref",  "lufs": -16.0, "tp": -1.0, "eq": 0.3, "translate": 0.2, "mono_below": 120.0, "max_low_boost_db": 0.0}
}
```
Add to `hand_tuned`:
- "strand choir lufs -18: inside the classical guidance -16 to -20 (Sage Audio, Violet Recording, AES panel) and 4 dB over the measured choir median (-22.3), because Spotify raises a quiet track only up to its true-peak headroom (a -22 LUFS choir at -1 dBTP plays 8 dB under its playlist neighbours; -18 halves that)"
- "strand acappella lufs -12: measured median -12.5 (8 albums), Holiday 100 average -12.9; eq 0.5 because the curve's middle-half spread is 1.5-6 dB (choir 3-12 dB); translate 0.3: the vocal bass leads"
- "strands street and handbells lufs -16: no measured masters (strand A has no recordings, the handbell set is 18 mostly secular tracks); between the default and the choir"
- "strand brass: the choir target and loudness; the brass set (44 tracks, 6 of 8 albums Canadian Brass) measured -18.1 LUFS and as dark as the choirs (-28 dB at 6.4-15.5 kHz) but is too one-ensemble for its own curve"
- "midcentury_era lufs -16: the mid-century recordings as streamed today span -10.5 to -23.3 (iZotope 2025); choral-pop reissues -18.5 (thin), crooner reissues -14.1"

Add to `sources`:
- "strands and eras (2026-11-25): docs/CAROLING.md 'Granularity': 23 choir albums (UK cathedral/collegiate and US concert choirs, 1986-2012, 106 tracks), 8 a cappella albums (1991-2018, 87), 7 crooner albums (CD reissues, 55), 8 brass albums (44), mid-century choral reissues (20, thin), handbells (18, thin); AcousticBrainz Bark bands, ReplayGain and dynamic_complexity via tools/refcurve.py; Holiday 100 per-song loudness, LRA and true peak (iZotope 2025); Spotify loudness normalisation (https://support.spotify.com/us/artists/article/loudness-normalization/)"

Change `status` to append: "; strands and eras added 2026-11-25 (docs/CAROLING.md 'Granularity'): per-strand targets `caroling_choir` and `caroling_acappella`".

## 3. docs/MASTERING.md
- **Genre table**, `caroling` row, target column: "`caroling_ref` (5 albums), no low-end boosts; by strand `caroling_choir` (-18 LUFS) or `caroling_acappella` (-12 LUFS)".
- **The curves table**: two new columns (values in docs/CAROLING.md "Tonal curves", or `refcurve.py` prints them):
  - `caroling_choir`: 31.5 -22.5, 40 -24, 50 -25, 63 -24.5, 80 -22, 100 -17.5, 125 -13, 160 -9.5, 200 -7, 250 -4.5, 315 -1.5, 400 +1.5, 500 +4, 630 +4, 800 +1.5, 1k 0, 1.25k -2, 1.6k -6.5, 2k -10, 2.5k -10, 3.15k -12, 4k -20, 5k -26.5, 6.3k -27, 8k -27, 10k -30, 12.5k -35, 16k -41
  - `caroling_acappella`: 31.5 -14, 40 -8.5, 50 -3.5, 63 +0.5, 80 +3, 100 +3.5, 125 +2, 160 +0.5, 200 0, 250 +0.5, 315 +1, 400 +1, 500 +1.5, 630 +2, 800 +1.5, 1k 0, 1.25k -1.5, 1.6k -2.5, 2k -4.5, 2.5k -6.5, 3.15k -7.5, 4k -10, 5k -11.5, 6.3k -11, 8k -10, 10k -10.5, 12.5k -15, 16k -22.5
- **Provenance table**, two rows:
  - `caroling_choir` | 23 choir albums of docs/CAROLING.md "Granularity" (King's, St John's, Cambridge Singers, Tenebrae, VOCES8, Tallis Scholars; Chanticleer, Robert Shaw Chorale, Tabernacle Choir) | 1986-2012 | 106 | -22.3 (-24.3 to -19.7) | `caroling_ref`: -13.5 to -18 dB at 50-100 Hz, -7 to -9.5 dB at 4-12.5 kHz
  - `caroling_acappella` | 8 a cappella Christmas albums (Pentatonix, Straight No Chaser, Take 6) | 1991-2018 | 87 | -12.5 (-14.4 to -10.2) | `caroling_ref`: +6.5 to +7.5 dB at 63-125 Hz, +0.5 to +2 dB at 2-3.15 kHz, +3 to +13 dB from 4 kHz up
- **Caveats** paragraph: add "the caroling strands differ more from each other than any other genre's (20-25 dB at 50-100 Hz between choir and a cappella), which is why `caroling_ref` had its 15-18 dB spread; dynamics per strand rest on Essentia's dynamic_complexity, a loose proxy for LRA (r 0.44 on Spectre's masters)".
- A note on playback for quiet genres (useful beyond caroling; chamber score too): Spotify normalises per track to -14 but raises a quiet master only up to its true-peak headroom minus 1 dB (Spotify's own example: -20 LUFS with a -5 dBTP peak is raised to -16), so a classical-level master stays quieter than its playlist neighbours.

## 4. data/catalogue_references.json
Add `albums.caroling_choir` and `albums.caroling_acappella` from `catalogue_references_additions.json` (each with `"source": "docs/CAROLING.md 'Granularity'"`), and `targets.caroling_choir: {"albums": "caroling_choir"}`, `targets.caroling_acappella: {"albums": "caroling_acappella"}`. The other strand sets (crooner, mid-century, brass, handbells) are listed by MBID in docs/CAROLING.md "How the strands were measured"; add them only if the orchestrator wants them reproducible by catalogue_stats.py.

## 5. docs/LESSONS.md (caroling, 012)
- "A genre that spans a church choir and Pentatonix has two masters. `caroling_ref` averaged them (spread 15-18 dB); measured apart (2026-11-25) choir carols sit at -22 LUFS with twice the dynamics, no low end and a top 27-30 dB under 1 kHz, a cappella carols at -12.5 with a vocal-bass low end and a bright top. 012 was mastered like the pop end (-14 LUFS, dynamic complexity 2.9, LRA 5.2). The brief must name the strand."

## 6. docs/PRODUCTION.md, item 9 (remix table)
- 012 *The Note She Kept*: a parlour/door carol (strand A with an organ and an svs choir). If it is remastered, its strand settings are `street` (caroling_ref, -16) or, if the owner hears it as a church carol, `choir` (caroling_choir, -18). Not urgent: the current master is inside the measured range of the pop-leaning strands. Owner's decision.

## 7. docs/ORCHESTRATION.md, "Genre conventions" / starting a session
- A caroling brief names its strand: street/door, choir (cathedral, church, concert), crooner/mid-century, a cappella, handbells or brass; and optionally an era (mid-century, CD era, a cappella/streaming era, current). No strand = current practice (docs/CAROLING.md checklist) with the default master.

## Contradictions with existing docs (flagged, research followed)
- docs/CAROLING.md's own Configuration table said the master was `--target rock --eq 0.5` after the engine had moved to `caroling_ref` (eq 0.3): corrected in CAROLING.md.
- docs/CAROLING.md's "Engine mapping" listed glockenspiel and celesta as "approximate (`musicbox`, `bell`)": `glockenspiel`, `celesta` and `vibraphone` exist since 2026-11-24 (engine/chamber.py): corrected.
- The 2026-11-25 era assessment called `caroling_ref` "a loose guard" because of its spread; the strand measurements explain the spread (two masters in one set) and replace the guard with two tight targets for briefs that name B or D.
- The genre's -14 LUFS default contradicts neither strand's measurements but matches neither: kept as the default (between, and Spotify's level) and marked hand-tuned, as before.

## Not sourced / thin (also in the doc)
Strand A (street) has no recordings; handbells 18 secular tracks, no lossless; no true peak, LRA, PLR or width per strand (AcousticBrainz has none); nothing after 2022; the mid-century set is 20 tracks; no count of key lifts in a cappella carols.

## Engine gaps (for the queue)
1. Brass (quartet, trombone choir, quintet, big-band section): missing; needed by strands C, F and the current-practice retro-orchestral sound.
2. A modal handbell (twelfth-tuned English handbell, LV, damping, martellato, shake), measured like `glockenspiel`.
3. A pipe organ (chiff, mixtures, reeds).
4. An SATB svs choir test with `hanami-male`; nothing reaches a vocal bass's E2-G2.
5. De-esser. 6. Vocal percussion. 7. Harp. 8. Per-strand master settings in genres.json (section 2) if the engine should apply them from a brief keyword rather than by hand.
