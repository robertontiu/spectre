# Handoff: continuing Spectre from the repo alone

Written 2026-11-25 for a fresh Claude Code session taking over from the chat orchestrator (queue item 6 in [ORCHESTRATION.md](ORCHESTRATION.md)).

> **Session files now live in the S3 bucket**, under each track's `uuid` from `site/data/tracks.json` (`<uuid>/rendition.mp3`, `journal.md`, `readme.md`, `project.json`, ...; AGENTS.md section 8). `sessions/` is a local working area; `python3 tools/upload_track.py --fetch <id>` restores a session folder. Paths like `sessions/NNN-name/...` below are kept as history. (Until the migration in ORCHESTRATION.md queue 11 is done, the folders are also still in git.) Read this first, then [AGENTS.md](../AGENTS.md) and [ORCHESTRATION.md](ORCHESTRATION.md) in full: those two stay the source of truth for rules and procedures; this file is the map and the current state.

## 1. What Spectre is

An experiment: can an AI make music the way a human producer does, starting from a feeling and shaped by listening, instead of generating audio from a prompt? Spectre is the artist (and the producer persona: one name everywhere). A producer agent writes musical intentions into `project.json`; the engine (Python, `engine/`) performs them with synthesized instruments, renders, and shows the agent its own track as pictures and numbers ("the ears"); the agent makes one decision at a time and journals it. Only sung words use neural models (DiffSinger voicebanks, approved by the owner). Results are research: report misses honestly.

Fifteen sessions so far, across hip hop and folk-fusion trap, trance, pop rock, joc țigănesc, caroling, Latin pop and cinematic chamber score. Thirteen tracks are published on spectre.robertontiu.com; two more are delivered and waiting for the owner (section 5).

## 2. How a session runs, end to end

1. **Genre research → configuration** (only for a new genre or variant). Research with sources: length, form and section lengths, tempo, meter, change rate, what the instrumental must allow, and mastering practice (loudness, true peak, dynamics, measured tonal balance, mono point, width). Write `docs/<GENRE>.md`, add the `engine/genres.json` entry and the row plus sources in ORCHESTRATION.md "Genre conventions". Unsourced values are marked hand-tuned. Build signature instruments the engine lacks, check them by spectrogram against recordings, document them in `docs/MANUAL.md`, smoke-test with `examples/engine-test.json`, commit. If a voice will sing in a language without a profile, write `docs/voice/languages/<code>.md` first. Quoted melodies are verified from scores/recordings and written as engine blocks plus a phrase table.
2. **Brief.** `sessions/NNN-name/PROMPT.md`, filled from `prompts/producer.md` (or the latest PROMPT.md, which carries the newest lessons): persona Spectre, the brief, the nearest wrong feelings and what separates them, the genre doc, the "break your own habits" step (stage 1), lessons, studio rules, the final report format. Where a brief's number contradicts the genre research, flag it and let the research decide (standing rule 11).
3. **Producer agent** on the model the owner chose for that session (recent sessions: Claude Fable 5.2, launched with model `fable`; earlier ones Claude Opus 5.5). Short prompt: "Read sessions/NNN-name/PROMPT.md in full and follow it exactly. If journal.md already exists, this is a resumed session: read the journal and helper scripts first, listen to the latest render before your next move, continue numbering. Your final reply must be the report described at the end of PROMPT.md." A session is 25-35 renders, roughly 30-90 minutes.
4. **Monitoring.** Check every ~15-20 minutes (schedule a one-shot check-in): count `renders/v*.wav` and `v*.meta.json`, newest render time, `final.mp3`. No new render for 10+ minutes and no report means the agent stopped: resume with the same short prompt. Server/container restarts kill running agents (sessions 003, 007, 008, 011, 013 were each resumed after one); forward-only versioning makes resuming seamless. Never leave a session stopped.
5. **Delivery** (ORCHESTRATION.md "Delivering a finished session"): verify the master report (genre, target LUFS, true peak at or under -1 dBTP, no warnings, `master_version` 2, phone check); rename `final.mp3` to `<title-slug>-mastered.mp3`; `master-tonal-balance.png`, `master-report.json`, `ear-overview.png`; README with table, arrangement, how it carries the feeling, files, Spectre's note, the model, and a **Credits** line from `engine/voices.json` for every svs voice; LESSONS entry plus "Across genres" after a genre switch; `site/data/tracks.json` (newest first, `model` and `file` fields), **publish** with `python3 tools/upload_track.py <id>` (uuid, upload of the session's files to the bucket, verified), `cd site && npm run build`; **clean up**: delete the session's render WAVs (keep `renders/*.json`, `*.mp3`, `*.png`), listen/zoom dumps (`*.txt`, `z_*.png`), `__pycache__`, and the agents' /tmp scratch; then commit and push.

### Working with sub-agents (the orchestrator's habits)
- Delegate long work (producer sessions, research, site UI) to sub-agents; keep the orchestrator's thread free. Don't interrupt your own turn while background agents run (it can take them down).
- **Commit by path only:** `git commit -m "..." -- <paths>`. Several agents share one working tree, and others' uncommitted work (sessions awaiting approval) must never be swept into a commit. Never `git add -A`.
- **Any push publishes every local commit**, including other agents' commits that weren't meant to go out yet. Check `git log origin/main..HEAD` before pushing.
- **One heavy job at a time.** The machine has about 6.8 GB of RAM; a master of a long track peaks near 5.7 GB, and masters were OOM-killed while another session rendered (007, 008). Renders of different sessions can overlap; masters should not.
- **Disk is the real limit:** `df` reports 252 GB, but only about 43 GB are usable (writes ran out at about 41 GB used, 1.8 GB free); check `df -h /` before heavy work; a session writes about 2.5 GB of WAVs. Render WAVs are deleted at delivery (every version stays reproducible from its `vNNN.project.json`: rendering is seeded and deterministic).
- **Render numbering:** since a fix (commit 60b71fb) the engine numbers the next render from all versioned files in `renders/` (json, mp3, png), not only WAVs. Before the fix, a folder with its WAVs cleaned out restarted at v001 and overwrote old metadata (it happened in 012 and 013; both renamed by hand).
- Engine edits while a session renders must be additive and atomic (write a temp file, then rename).

## 3. The owner's working preferences (project only)

The full standing rules are in ORCHESTRATION.md; these are the ones that shape day-to-day choices:
- **Genre settings come from research, with sources.** Every per-genre value cites a source or is marked hand-tuned; master like the industry does, per genre.
- **Research decides voice questions; the owner is the ear tester.** His notes are symptoms to diagnose ("it sounds like reverb" is a hypothesis to measure), not instructions. Where research disagrees with a suggestion, follow the research and tell him why. A/B renders go to him for the verdict.
- **Voices are instruments, never full songs.** Short lines, hooks, chops, calls, choir textures; no verses carried by a lead vocal.
- **Every production is unique.** Licensed (public-domain) quotes are ingredients, never covers or re-arrangements; quote whole phrases, cut at phrase boundaries.
- **Always clean up** after every task (scratch, test renders, downloads, render WAVs at delivery).
- **Website:** no autoplay, no EQ (tracks play exactly as mastered); the producer model is shown per track beside the tempo; tracks are listed newest first. Other design decisions: ORCHESTRATION.md "Website design decisions".
- **Feedback is recorded only once final.** Candidates and A/B results live in the session journal; README, LESSONS and the site change only when the owner has decided.
- **No personal details in the repo, ever.** Anything personal the owner shares is context for shaping a brief, never content: not in PROMPT.md, journals, READMEs, LESSONS, commit messages, the website or handoff notes. Translate it into the feeling and the brief, nothing more.
- Report misses honestly; the artist is called Spectre everywhere; record lessons after every genre switch.

## 4. State of every session

| # | Title | Genre | Model | Published version | Open issues |
|---|---|---|---|---|---|
| 001 | Bleachers | boom-bap / 808-trap hybrid | Claude Opus 5.5 | v028 (handclap, remastered `--genre hiphop --eq 0.9 --lufs -11`) | came across as longing rather than defiance (documented miss) |
| 002 | Lid Off | rage trap / industrial | Claude Opus 5.5 | v033 | none |
| 003 | Throw It Back | oriental trap | Claude Opus 5.5 | v026 | none |
| 004 | Tura | Romanian folk trap | Claude Opus 5.5 | v027 | none |
| 005 | Fuck Every War | Ukrainian folk trap | Claude Opus 5.5 | v026 | none |
| 006 | Līdz rītam | Latvian folk trap | Claude Opus 5.5 | v027 | none |
| 007 | First Light | trance, extended mix | Claude Opus 5.5 | v030 (handclap model 2) | master EQ at +4 dB at 3.15-4 kHz |
| 008 | Anyway | pop rock | Claude Opus 5.5 | v028 | wordless `vox` barely reads as a voice; owner chose to keep it |
| 009 | Here You Are | pop rock | Claude Fable 5.2 | v026 (wordless) | candidate v034 with sung chorus words awaiting approval: decision (a) |
| 010 | Unison | joc țigănesc | Claude Opus 5.5 | v024 | top end 5-6.6 dB under the borrowed curve (dry band, accepted) |
| 011 | Din somnul cel de moarte | aggressive boom-bap on the Romanian anthem | Claude Opus 5.5 | v022 | none |
| 012 | The Note She Kept | American caroling | Claude Fable 5.2 | v031 (voice remix) | owner hasn't confirmed the remix: decision (e) |
| 013 | Half of Me | trance radio edit | Claude Fable 5.2 | v026 | v032 uncommitted pending approval: decision (b) |
| 014 | (title open) | Latin pop, bolero-bachata, 84 bpm, D major, 3:31 | Claude Fable 5.2 | not published | delivered as `final.mp3` (v028), uncommitted: decision (c) |
| 015 | Again, Again | cinematic chamber score, waltz at 172, D major, 3:44 | Claude Fable 5.2 | not published | delivered (v028), uncommitted: decision (d) |

Sessions 001-006 were re-rendered on 2026-11-24 with `handclap` model 2 (the old `clap` took `spread` in seconds and fired off-beat bursts) and remastered on the measured hip-hop curve; details in each README. **Do not touch the folders of 009, 013, 014 and 015** until the owner decides: they hold uncommitted work.

## 5. Open decisions waiting on the owner

**(a) 009 "Here You Are".** Resolved 2026-11-25: v034 (sung chorus words, Hanami) approved and published.

**(b) 013 "Half of Me".** Resolved 2026-11-25: v032 approved and published; "light" stays as it is.

**(c) 014 love letter.** Resolved 2026-11-25: the owner approved it as is ("siempre tuya", title "Lo que no supe decir"); published.

**(d) 015 "Again, Again".** Resolved 2026-11-25: approved and published as is. The 4 kHz master note stays a lesson (casting, not EQ).

**(e) 012 carol remix.** Resolved 2026-11-25: v031 approved.

**(f) Choir vibrato and the default blend.** The vibrato A/B (`examples/vocals/svs/choir-vibrato-1.mp3` vs `choir-vibrato-0.3.mp3`, opt-in `svs_vibrato`) and the default voice blend (`examples/vocals/svs/blend-*.mp3`; blend-d recommended) await his ear. Also waiting on a listener: a native ear on the Romanian experiment (`examples/vocals/svs/romanian-hanami-experiment.mp3`).

## 6. Engine and knowledge map

- **Engine:** `engine/studio.py` (render / listen / master CLI, mix, fx, sections), `hand.py` (notation), `ear.py` (the ears; `listen --phone`), `master.py` (master v2, per-genre configs from `genres.json`: trap, hiphop, trance, trance_radio, rock, joc, caroling, latinpop, chamberscore; no default), `instruments.py`, `violin.py` (bowed waveguide), `chamber.py` (celesta, glockenspiel, vibraphone, cello, viola, strings_section, `bell` "clean"; modelled on measured recordings, A/B in `examples/chamberscore/`), `clarity.py` (`listen --clarity`: stems, masking, EQ map, stack view), `mixbus.py` (stacks, group buses, named returns, role EQ presets, `ott`/`dyneq`/`clip`/`mseq`, correlated humanizing), `synth.py` (`supersaw` model 2, `polysynth`, `sub`, kick layers, `metalhat`, `air`; A/B in `examples/production/`, docs/MANUAL.md "Production").
- **Voice stack:** `engine/singer.py` (`singer`, which dispatches to svs, its only source; `vox2`), `engine/svs.py` (`source: "svs"`, DiffSinger voicebanks via ONNX on CPU, seeded and phrase-cached; banks in `~/.cache/spectre/svs`, never in git; the male voices through a voice's `sing_up`), `engine/lang_es.py` (Spanish), `engine/voices.json` (catalogue, licences, credit lines). Docs: `docs/voice/VOICES.md` (catalogue, licences, what's missing), `docs/voice/MIXING.md` (voice mixing and mastering, choirs, measured engine controls, engine recommendations), `docs/voice/GENERAL.md` (literature, prioritized svs improvements), `docs/voice/languages/{en,es,ro}.md`. Each genre doc has a "Mixing the voice" section. Lotte V voices: never in a track with a political subject.
- **Genre docs:** `docs/HIPHOP.md`, `CRAFT.md`, `TRANCE.md` (incl. "Radio edit", "Vocals"), `POP_ROCK.md`, `JOC_TIGANESC.md`, `CAROLING.md`, `LATIN_POP.md`, `CHAMBER_SCORE.md`, culture briefs `ROMANIAN.md` (verified anthem melody), `UKRAINIAN.md`, `LATVIAN.md`; mastering in `MASTERING.md`; lessons in `LESSONS.md`; the producer's interface is `MANUAL.md`.
- **Known engine gaps:** no de-esser (MIXING.md recommendation 1; producers fake it with dips and low-passes); no trained male singer's voice (the male voices `hanami-male` / `hanami-male-es` are Hanami made male inside her synthesizer: soft and covered, no ring or grit; VOICES.md "Male voices"); no Romanian singing voice; master curves borrowed from rock for caroling, joc, Latin pop and chamber score (no measured choral, folk, Latin or orchestral curve); the piano has no top end (nothing above its 13th partial, nothing at 4 kHz under its top octave); no brass, no orchestral woodwinds, no toy piano; `bell` clicks at its cut and clanks above velocity 0.6; svs voices have a 4 kHz ridge and hollows at 2.5 and 5-6 kHz; a held svs note ends early; changing timing re-synthesises every svs phrase (minutes); returns can be ducked by any track or bus, but a track only by a drum's hits (sidechain) or a keyed `dyneq`; the ears' "no contrast" ignores melodic and rhythmic change and the key detector misreads modes; some renders run 3-6x slower than usual (cause unknown). Per-session quirks are in LESSONS.md.
- **Tried and rejected:** consonant-length scaling in svs, master v1 (OOM on long tracks), the old `clap` and the first `handclap` (replaced by model 2, fitted to recorded claps), male and hard DiffSinger banks found online (licence terms; VOICES.md), and for the male voice: zero-shot cloning of recorded singers (consent) and voice conversion of Hanami's phrase (less clear by ear); both removed from the repo.
- **Website:** Next.js in `site/` (see `site/README.md`), canonical list `site/data/tracks.json`. Vercel project with Root Directory `site` and "Include files outside the root directory" on; audio plays from the S3 bucket through `/api/track/<slug>` (presigned URLs, read-only key in Vercel's environment; site/README.md "Audio"); until the bucket is configured there, the prebuild (`site/scripts/sync-tracks.mjs`) copies the masters into `public/tracks/` and the route falls back to them. It redeploys on push to `main`: a push is a publish.

## 7. The queue

From ORCHESTRATION.md "Queued work":
- **Done:** 1 (off-beat audit and re-render of the released tracks), 2 (handclap fitted to real claps), 3 (sung vocals: `svs`), 4 (break your own habits), 5 (Corruption, session 011), 5b (voice research), 5c (caroling, 012), 5d (trance radio edit, 013), 5e (Latin pop, 014: produced, delivery pending decision (c)), 5f (chamber score, 015: produced, delivery pending decision (d)), 6 (this handoff), 8 (a male voice: `hanami-male` / `hanami-male-es`, approved by ear 2026-11-25).
- **Left:** the owner's decisions in section 5 and the deliveries that follow them.
- **7, plugin packaging:** later, not scheduled.
