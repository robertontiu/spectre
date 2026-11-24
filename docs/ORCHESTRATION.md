# Orchestration: how Spectre is run

This is the operator's playbook: how the orchestrating agent (the one Robert talks to) runs producer sessions, keeps them alive, delivers results and maintains the website. A new orchestrator session should read this together with AGENTS.md before doing anything, so no working agreement is lost between sessions.

## The owner's standing rules
These were set by Robert (the repo owner) and apply until he changes them:
1. **The artist is called Spectre, everywhere.** The producer persona, the prompts, the session notes, the journals, the website. (An earlier persona name was retired; don't reintroduce it.)
2. **Never let a producer session stay stopped.** Check running sessions about every 15 minutes. If one stops without finishing, fix the cause if there is one, then resume it from its saved files. Always resume.
3. **Record lessons after every genre switch** in `docs/LESSONS.md` (session entry plus the "Across genres" section), and save new genre research as `docs/<GENRE>.md`.
4. **Keep the website's track list up to date** with every finished track, newest first.
5. **Sessions may run in parallel lanes**, one folder each.
6. **Delegate long UI work to a sub-agent** so the orchestrator's thread stays free.
7. **It's an experiment.** Report misses honestly, including in the README and lessons.

## Starting a new session
1. If the genre is new: research it (instruments, rhythms, modes, the modern reference artists, and the cultural context of the subject), write `docs/<GENRE>.md`, and build the genre's signature instruments in the engine first (generic synths can't fake them). Check them with spectrogram plots and a tiny project, document them in `docs/MANUAL.md`, smoke-test with `examples/engine-test.json`, commit. Engine edits while another session is rendering must be additive and written atomically (temp file plus rename).
2. Create `sessions/NNN-name/PROMPT.md` from `prompts/producer.md` (or from the latest session's PROMPT.md, which carries the newest lessons). Always include: the persona (Spectre), the brief, the **nearest wrong feelings** for this brief and what separates them, the genre doc to read, the lessons, the studio rules and the final report format. If Robert lets the agent choose tempo or feeling, say so and ask it to commit in its first journal entry.
3. Start a general-purpose sub-agent with a short prompt: "Read sessions/NNN-name/PROMPT.md in full and follow it exactly. If journal.md already exists, this is a resumed session: read the journal and helper scripts first, listen to the latest render before your next move, continue numbering. Your final reply must be the report described at the end of PROMPT.md." Because the full brief lives in PROMPT.md, the same short prompt resumes a stopped session.
4. Schedule a check-in (a one-shot scheduled message back into the session) for 15 minutes.

## Genre conventions (fill the producer template from these)
Lengths and forms follow the genre, not one rule. Check the genre brief in docs/<GENRE>.md, and add a row when a new genre arrives.

| Genre family | `{{LENGTH}}` | `{{FORM}}` | `{{ROLE}}` (what the instrumental must allow) | `{{MASTER}}` |
|---|---|---|---|---|
| Beats (trap, boom-bap, drill, rage, folk-fusion trap) | 2:30 to 3:30 | an intro, a real arrangement (hooks and verses) and an outro | it should feel like a real beat an artist could rap on | `studio.py master vNNN --lufs -10.5 --tp -1` |
| Trance and other club music | 5:00 to 7:00 (an extended mix; a radio edit is 3:00-4:00 and only when Robert asks) | a DJ-friendly intro and outro (16-32 bars of drums to mix with), at least one full breakdown and build into a release, and a second wave | a lead synth carries the melody a vocalist would sing | `studio.py master vNNN --target trance --lufs -10 --tp -1 --translate 0.4` |
| Pop rock and other songs | 3:00 to 4:00 | a song form (intro, verses, pre-choruses, choruses, a bridge, a final chorus, an outro) | the verses leave room for a voice; a vocal-like lead carries the sung melody | `studio.py master vNNN --target rock --lufs -10 --tp -1 --translate 0.3` |

`{{HAND}}` is 3-5 bullets naming the genre's schools and craft (see the latest session's PROMPT.md in that genre); `{{GENRE_LINE}}` says whether the genre is fixed by the brief or the producer's choice.

## Keeping sessions alive
- At each check: count `renders/v*.wav` (excluding master, premaster and solo files), note the newest render's time, look for `final.mp3`.
- Progressing: schedule the next check in 15 minutes. With several sessions running, one combined check is fine.
- No final report and no new render for 10+ minutes, or the agent is reported stopped: start a fresh agent with the resume prompt above.
- A known cause of stops: interrupting the orchestrator's own turn mid-work can take background agents down. New messages queued while the orchestrator works are safe.

## Delivering a finished session
1. **Verify:** final.mp3 exists and has the expected length; `project.json` equals `renders/vNNN.project.json`; the master report (`renders/vNNN.master.report.json`) shows about the target LUFS, true peak at or under -1 dBTP, no warnings.
2. **Send** the track (named after its title) and `journal.md` to Robert.
3. **Tidy the session folder:** rename final.mp3 to `<title-slug>-mastered.mp3`; copy `renders/vNNN.master.png` to `master-tonal-balance.png` and the report to `master-report.json`; save the overview ear as `ear-overview.png`; remove `__pycache__`; write `README.md` (table, arrangement, how it carries the feeling, files, Spectre's note; see earlier sessions).
4. **Repo docs:** add the row to the README results table, the session entry to `docs/LESSONS.md` and update "Across genres"; fix or document any engine quirks the producer reported (smoke-test fixes).
5. **Website:** add the track to `site/data/tracks.json`, the canonical list (newest first; `id`, `artist: "Spectre"`, `title`, `src: "tracks/NNN-slug.mp3"`, `duration` from ffprobe, `bpm`, `genre` (short, e.g. "Latvian folk trap"), `style`, `feeling`, 2-3 `colors` that fit the track; the page mutes them automatically). Run `python3 tools/sync_tracks.py` to copy the masters into `site/public/tracks/` and check that `cd site && npm run build` passes; the website picks the track up on its next deploy.
6. **Commit and push** (end commit messages with the session's attribution lines).

## The website
- Source: `site/` (Next.js app; see site/README.md). Canonical track list: `site/data/tracks.json`.
- Hosting: spectre.robertontiu.com on Vercel (Root Directory `site`, "Include files outside the root directory" on, normal build). It rebuilds from the repo; there is nothing to publish by hand.
- The earlier single-file showcase, the retro "Spectre Amp" player and their artifacts were retired once the Next.js site replaced them.

### Website design decisions (agreed with Robert, keep unless he changes them)
- Dark, ghostly world: near-black blue, cold moonlight, a hooded apparition in mist, ice-cyan glow. Tones and haze, not crisp texture.
- Badge: a tonal hooded wraith carved out by cold backlight, eye glints, eclipse-like corona; also the favicon. No cartoon features, no line drawing.
- Title: SPECTRE as dark smoky letters against the same backlight, faded (~80% opacity), with an occasional horror-film blur-and-shake glitch every 8-20 s.
- No descriptions on the page: no tagline, no track style line, no footer prose. Allowed: the GitHub badge top right, the footer line "© 2026 Robert Ontiu", "BPM · genre" under each track, and a share button next to the playing title.
- Layout: top half brand banner; bottom half a blurred field of the playing track's colours; the player in the middle, raised over the top, dissolving into the bottom. Inside the player: bar visualizer, controls, EQ ("Spectre" preset default), playlist ("Spectre - Title", duration, BPM below), newest first.
- Track colours lead in the bottom field (moderately muted), bleed lightly into the top, and tint the mist. Fuck Every War uses the Ukrainian flag colours.
- Mist: several fog layers moving visibly (12-28 s passes) across both halves, denser at the top.
- One fixed full-viewport background stack (no section backgrounds, no clipping), so there are no seams; verify seams with a row-by-row luminance script, not by eye.
- Performance: never animate filters or blur; move pre-rendered layers with transform and opacity only; everything off under prefers-reduced-motion.
