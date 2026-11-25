# Pop rock: proposals for the shared files (genre research, 2026-11-25)

Research written into docs/POP_ROCK.md, new section "Eras, strands and the bleeding edge" (A-I), plus three corrected rows in its Configuration (tempo measured; Master row and "Mixing and loudness" said -10 LUFS / `rock`, now the -8.5 / `rock_2015` that engine/genres.json already holds). Nothing below has been applied; the shared files are untouched. Not committed.

Curve files (all `tools/refcurve.py catalogue ... --out`, run under `flock /tmp/spectre-musicbrainz.lock`, 2026-11-25), in
`/tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/poprock_curves/`:

| File | Set | n | Use |
|---|---|---|---|
| `rock_punk.json` | tag `pop punk`, 2013-2021, 100/year (= `poppunk_2013.json` renamed, `name` and `note` set) | 490 | **add** to engine/targets.json |
| `rock_altpop.json` | tags `alt-pop` OR `bedroom pop` OR `indie pop`, 2015-2021, 100/year (= `altpop_2015.json` renamed) | 464 | **add** to engine/targets.json |
| `poprock_1990/1995/2000/2005/2010/2018.json`, `poprock_2000s.json` | tag `pop rock` by period | 207-478 | reference only (the timeline table in POP_ROCK.md B); **not** for targets.json |
| `poppunk_1997.json`, `britpop_1993.json`, `postgrunge_1995.json` | strand tags of the 1990s-2000s | 633-1,305 | reference only |

## 1. engine/targets.json

```
python3 tools/refcurve.py add /tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/poprock_curves/rock_punk.json --note "pop-punk and emo, any period, and the heavier radio rock; pop punk 1997-2012 measures within 1 dB of 2013-2021 (docs/POP_ROCK.md 'Eras, strands and the bleeding edge' B, H)"
python3 tools/refcurve.py add /tmp/claude-0/-home-user-spectre/c782847d-e9b8-545c-b902-83e8e2b1b59b/scratchpad/proposals/poprock_curves/rock_altpop.json --note "the alt-pop / bedroom crossover strand of pop rock; the tag set includes indie pop (dilution); 2022-2026 extrapolated (docs/POP_ROCK.md 'Eras, strands and the bleeding edge' B, H)"
```
Curves (dB re 1 kHz):
- `rock_punk`: 31.5 -5.5, 40 -2.5, 50 +0.5, 63 +3, 80 +4, 100 +4, 125 +3.5, 160 +3, 200 +2, 250 +1.5, 315 +0.5, 400 0, 500 +0.5, 630 +1, 800 +1, 1k 0, 1.25k -0.5, 1.6k -0.5, 2k -0.5, 2.5k -1, 3.15k -2, 4k -3.5, 5k -5.5, 6.3k -6.5, 8k -7.5, 10k -9.5, 12.5k -13.5, 16k -19.5. Fit residual max 1.1 dB, mean 0.24; 40% lossless.
- `rock_altpop`: 31.5 -4.5, 40 -1, 50 +2.5, 63 +4.5, 80 +4.5, 100 +3.5, 125 +2.5, 160 +2, 200 +1.5, 250-400 +2, 500 +1.5, 630 +2, 800 +1.5, 1k 0, 1.25k -1.5, 1.6k -2.5, 2k -3.5, 2.5k -5, 3.15k -6.5, 4k -7.5, 5k -9, 6.3k -9.5, 8k -10, 10k -11.5, 12.5k -15.5, 16k -21.5. Fit residual max 1.4 dB, mean 0.25; 34% lossless.

**Not proposed:** a `rock_2018` (pop rock 2018-2021 refits within 1.5 dB of `rock_2015` in every 1/3 octave, mostly within 1 dB: below the "separate only where measurements differ" bar), period targets for the 1990s or 2000s (the `pop rock` tag's darker 1995-2014 plateau is what the tag held: the strand tags of those years measure like today, and pop punk 1997-2012 is within 1 dB of 2013-2021), a Britpop target (within 1.7 dB of `rock_2015`).

## 2. data/catalogue_references.json, under "targets"

```json
"rock_punk": {"tag": ["pop punk"], "years": "2013-2021", "per_year": 100},
"rock_altpop": {"tag": ["alt-pop", "bedroom pop", "indie pop"], "years": "2015-2021", "per_year": 100}
```

## 3. engine/genres.json, entry "rock"

Add (same shape as trance's `master_by_strand` / `era_targets`):
```json
"master_by_strand": {
  "note": "tonal targets differ by strand, not by period (docs/POP_ROCK.md 'Eras, strands and the bleeding edge', B and H): within pop punk 1997-2012 and 2013-2021 measure within 1 dB, and the strand tags of 1993-2009 measure like 2015-2021 pop rock; pass the flags with --genre rock. Loudness: 2020-2026 band records -8.2 to -7.7 LUFS, alt-pop crossover singles -5.1 to -6.8 (iZotope 2025); 1990 year-end hits -12.5 (Țînț & Drăgulin 2025)",
  "arena / radio, indie, folk-pop, ballad, and briefs that name no strand (current practice)": "--target rock_2015 --lufs -8.5 --tp -1 (2022-2026 extrapolated)",
  "pop-punk, emo, 2000s post-grunge / heavy radio rock (any period)": "--target rock_punk --lufs -8.5 --tp -1",
  "alt-pop / bedroom crossover": "--target rock_altpop --lufs -8.5 --tp -1 (denser, to about -7.5, only after an engine test; untested)",
  "1990s briefs (Britpop, alt-rock radio)": "--target rock_2015 --lufs -11 --tp -1 (the -11 is hand-tuned between 1990's -12.5 and the late-decade ramp)"
},
"era_targets": {
  "note": "no separate period curve: a 2018-2021 refit is within 1.5 dB of rock_2015; the period sets loudness (master_by_strand) and production (docs/POP_ROCK.md D), not the tonal target"
}
```
Change:
- `"tempo"`: `"115-130 bpm typical (partly sourced; ballad builders start slower)"` → `"pop rock catalogue median 115-122 bpm in every period 1995-2021 (middle half about 95-133; AcousticBrainz, folded into 80-160); pop punk about 150 (123-173); ballad builders far slower"`.
- `"hand_tuned"`: remove `"lufs -10 is an engine-limited choice, quieter than the charts (-8.1)"` (stale: `master.lufs` is -8.5); add `"lufs -11 for 1990s briefs (between measured values)"`.
- `"length"`: append `"; measured medians 2024-25: pop rock 3:36, pop punk 3:08, indie rock 3:20 (MusicBrainz)"`.

## 4. docs/ORCHESTRATION.md, the pop-rock row of the genre table

**Contradiction:** the row says `(-10 LUFS, -1 dBTP, translate 0.3)`; engine/genres.json has had -8.5 and `rock_2015` since 2026-11-24/25. Proposed row:

| Pop rock and other songs (strands: arena / radio, pop-punk and emo, indie, alt-pop / bedroom crossover, folk-pop, ballad; brief: docs/POP_ROCK.md, "Eras, strands and the bleeding edge") | 3:00 to 4:00 (pop punk about 3:10, indie about 3:20 today) | a song form (intro, verses, pre-choruses, choruses, a bridge, a final chorus, an outro) in 8-bar sections, first chorus by about 0:45-1:00; pop rock median 115-122 bpm (middle half about 95-133), pop punk about 150 with a double-time beat | the verses leave room for a voice; a vocal-like lead carries the sung melody | `studio.py master vNNN --genre rock` (`rock_2015`, -8.5 LUFS, -1 dBTP, translate 0.3); pop-punk briefs `--target rock_punk`, alt-pop briefs `--target rock_altpop`; 1990s briefs `--lufs -11` |

Also line 61 ("the tempo range is only partly sourced (no pop-rock dataset)") → "tempo measured on the catalogue: pop rock median 115-122 bpm, pop punk about 150 (docs/POP_ROCK.md B)". Line 66 ("Spectre's -10/-10.5 is an engine-limited choice") is stale for rock (-8.5).

## 5. docs/MASTERING.md, "Era targets"

Rows for the per-genre table (line ~37) and the provenance table (line ~160):
```
| `rock_punk` | tag `pop punk`, 2013-2021, up to 100 per year | 2013-2021 | 490 | -9.8 (-12.6 to -8.6) | `rock_2015`: +1 to +2 dB at 2-5 kHz, -1 to -1.5 dB at 315-500 Hz, +2 to +3.5 dB at 31.5-40 Hz |
| `rock_altpop` | tags `alt-pop`, `bedroom pop`, `indie pop`, 2015-2021, up to 100 per year | 2015-2021 | 464 | -10.6 (-12.2 to -9.5) | `rock_2015`: +2 to +4.5 dB at 31.5-63 Hz, -1.5 to -2.5 dB at 1.6-8 kHz |
```
And under "Era targets" a sentence: "For pop rock the measured differences are between strands, not periods (docs/POP_ROCK.md 'Eras, strands and the bleeding edge' B): `rock_punk` and `rock_altpop` beside `rock_2015`; no period curve."

## 6. docs/PRODUCTION.md / docs/LESSONS.md

No change required. A candidate lesson for LESSONS.md (orchestrator's call): "A catalogue tag can change meaning over the years: before trusting an era shift in one tag, measure the strand tags of the same years. For pop rock the apparent 1995-2014 'dark era' was the tag's content; pop punk did not change in 25 years."

## Flags (contradictions and weak points)
- docs/POP_ROCK.md "Mastering (industry practice)" still says "genres.json not yet changed" and proposes an unmeasured `rock_modern`; superseded by `rock_2015` (left in place as history; the orchestrator may trim it).
- The 2025 Hot Rock & Alternative loudness (-8.1 average) that the brief and genres.json cite is mostly the alt-pop crossover (Billie Eilish, sombr, Myles Smith, Hozier, The Marías), not band pop rock; the band records in that set are -8.2 and -7.7.
- Tempo from AcousticBrainz is folded (80-160 / 100-200): an assumption.
- 2022-2026: no tonal or catalogue-loudness data (AcousticBrainz ends); lengths alone reach 2025 (MusicBrainz).
- The alt-pop tag set is diluted by `indie pop`; Britpop's 58% lossless share suggests remasters.
