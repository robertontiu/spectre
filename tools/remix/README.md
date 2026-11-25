# tools/remix: helpers for remixing and remastering published tracks

Cross-track helpers for the remix pass (prompts/remix.md, docs/PRODUCTION.md "Remixing and remastering the 15
published tracks"). They were written for the trap-family tracks (001-006, mastered with `--genre hiphop` against
the `hiphop_2015` catalogue target) and work for any session folder. Run them from anywhere; they find the repo from
their own path. Scratch (master logs, the trap comparison master, clarity text) goes to `$REMIX_SCRATCH`, default
`/tmp/remix-scratch/<session>`, never into the session folder.

| File | What it does |
|---|---|
| `waitfree.sh` | Waits until no other lane renders or masters. Matches real python processes running `studio.py` or `master.py` by process name, so other lanes' waiting shell wrappers never count (two waiting lanes cannot block each other). Also waits for at least `$MIN_FREE_MB` (3000) MB available memory. Polls every second. |
| `stage1.sh <session> <pub vNNN> [master flags]` | Remaster step: re-renders the published project unchanged as a new version, checks events, masters with `--genre trap` (to scratch) and `--genre hiphop` (to `renders/`), reads both masters and the published one in Bark bands, then runs `listen --clarity --genre hiphop` on the loudest section. |
| `stage2.sh <session> <pub vNNN> <section> [master flags]` | One remix move: renders the edited `project.json`, checks events, runs clarity on one section and masters with `--genre hiphop` (`NOMASTER=1` skips the master). |
| `evcmp.py <pub meta> <new meta>` | Every original track's events (time, velocity, pitch) must be identical in the new render; lists added tracks; exit code 1 on any difference. |
| `barkcmp.py [--against NAME] files...` | Masters in Bark bands against a catalogue target's median, read through `tools/refcurve.py` (`catalogue_median`, from `engine/targets.json`), plus the target curves themselves; the last column is the mean gap from 32 Hz to 15.5 kHz. |
| `deliver.py <session> <pub mp3> <vNNN> <section[,section]> [--contour-only]` | The section loudness contour (each section relative to the whole track, remix against published; flags changes over 1 LU). Without `--contour-only` it also writes the loudness-matched `ab-published.mp3` / `ab-remix.mp3` of the peak section(s) and `remix-candidate.mp3`. |
| `remixlib.py` | Python helpers for editing a project: turn a track into a stack with its original sound as the first layer, add doubling layers, and `check_frozen` (bpm, swing, seed, patterns, arrangement and track names unchanged). |

## Status (2026-11-25)

Finished and used on 004 and 005: `waitfree.sh` (python-only match plus the free-memory check), `stage2.sh`,
`evcmp.py`, `barkcmp.py` (reads the median through `refcurve.catalogue_median`), `deliver.py`.
`stage1.sh` ran once (005) and worked. Not finished: `remixlib.py` is the previous agent's helper copied as it was
(no tests, `as_stack` only handles plain tracks); the scripts assume the `hiphop` genre and the `hiphop_2015` target
(pass other flags yourself for other genres); nothing reruns a master the OOM killer stopped (check the log for
SIGKILL and rerun `studio.py master vNNN` alone). Session 006 has not been remixed with them.

Typical run (pass the published master's own flags, from its `master-report.json` settings, wherever they differ
from the genre's defaults):

```bash
R=tools/remix
$R/stage1.sh sessions/005-fuck-war v026                    # remaster; read the Bark table and the clarity flags
# edit sessions/005-fuck-war/project.json (tracks and mix only), one move at a time, then:
$R/stage2.sh sessions/005-fuck-war v026 hook3b
python3 $R/deliver.py sessions/005-fuck-war fuck-every-war-mastered.mp3 v029 hook3b --contour-only
# the chosen version:
python3 $R/deliver.py sessions/005-fuck-war fuck-every-war-mastered.mp3 v029 hook3,hook3b
```

What the 001-006 remixes taught (details in docs/LESSONS.md and each session's "REMASTER AND REMIX" journal entry):
look first for EQ fixes made for the old Pestana curve in the 808 and kick fx chains (a fixed notch at the 808's
fundamental, a kick notched at its own fundamental, a kick boost around 100 Hz); reduce them in steps and re-master
each time. Separate kick and 808 with a keyed `dyneq` on the 808 at the kick's tune, and raise the 808 with its
post-drive `gain` fx. Check the section contour after every master.
