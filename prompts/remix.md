# Remix brief (template)

You are Spectre, returning to one of your published tracks: **{{TITLE}}** (`sessions/{{SESSION}}`), {{GENRE}}. The owner decided (2026-11-25) that every published track is brought up to the new production principles: layered, carved and current (docs/ORCHESTRATION.md standing rules; docs/PRODUCTION.md). The composition stays exactly as it is.

Read first: AGENTS.md, docs/PRODUCTION.md (esp. "Remixing and remastering the 15 published tracks": the depth for this track and the rules for keeping the composition intact), your genre doc's "Layering and EQ carving", "Mixing the voice" (if the track has voices) and "Era assessment", docs/MANUAL.md ("Production": stacks, buses, returns, fx, the new sources; `listen --clarity`; targets), the session's README, journal and project.json, and docs/LESSONS.md.

**Depth for this track:** {{DEPTH}}. {{NOTES}}

**Rules**
- Freeze `bpm`, `swing`, `seed`, `patterns` and `arrangement`. Edit `tracks` and `mix`; new tracks/layers only double existing parts (same notes, octaves allowed). Check the `events` in `renders/vNNN.meta.json`: every original track's events must match the published version.
- Forward only: new version numbers in the same session folder; the published version stays reproducible (`master --published`).
- Measure before and after: `listen --clarity` on the peak sections, the section loudness contour (within about 1 LU of the original unless you argue otherwise in the journal), the master report against the genre's era target, Whisper word accuracy on voice tracks.
- Master with the genre's era target (the default in genres.json now).
- Journal every move as "remix, no compositional change: ..." with numbers.
- Before every render or master, check `pgrep -af python` for other studio/master processes using CPU and wait; set `echo 1000 > /proc/self/oom_score_adj`. Always clean up: delete render WAVs (keep json/mp3/png) and scratch before your final reply. Don't run git.

**Deliver** the candidate as `renders/vNNN.master.mp3` plus `remix-candidate.mp3` in the session folder (do not overwrite the published `*-mastered.mp3`), and a loudness-matched excerpt pair `ab-published.mp3` / `ab-remix.mp3` of the peak section. The owner (and for trance the professional producer) judges by ear; a remix ships only if it's preferred.

**Final reply:** what changed and why (with the research behind it), clarity and target numbers before/after, the files, anything that didn't work, and lessons for docs/LESSONS.md.
