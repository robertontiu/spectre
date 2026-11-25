# AGENTS.md: start here

**Spectre** is an experiment, not a product: can an AI make music the way a human producer does, starting from a feeling and shaped by listening, instead of generating audio from a prompt? A producer agent, working as the artist Spectre, writes musical intentions into `project.json`; the engine (`engine/`, Python) performs them with synthesized instruments, renders, and shows the agent its own track as pictures and numbers ("the ears"); the agent makes one decision at a time and journals it. Only sung words use neural models (DiffSinger voicebanks, approved by the owner). More: [docs/agents/project.md](docs/agents/project.md).

This file holds only what every request needs. Read the rules, then the route for your role.

## Always-on rules (every agent, every request)

1. **The artist is called Spectre, everywhere**: persona, prompts, notes, journals, website. Don't reintroduce the earlier persona name.
2. **Never commit** `renders/`, WAVs, `__pycache__`, or voice model files and caches (`~/.cache/spectre/`). Track files go to the bucket, not into git ([docs/agents/git.md](docs/agents/git.md)).
3. **Commit by path only** (`git commit -m "..." -- <paths>`), never `git add -A`: several agents share one working tree. **A push publishes every local commit**, other agents' included, and redeploys the site: check `git log origin/main..HEAD` first.
4. **No personal details in versioned files.** Anything personal the owner shares is context for a brief, never content: not in PROMPT.md, journals, READMEs, LESSONS, commit messages, the website or handoff notes.
5. **Bucket settings come from environment variables, never the repo**: names, endpoints, regions and keys alike, in no file, commit or log. Ask the owner ([docs/agents/track-storage.md](docs/agents/track-storage.md)).
6. **Engine setup before any track work** (a new session, a resume, a remix, a master): run `tools/setup.sh` until `engine_assets.py status` shows no missing required resource ([docs/ORCHESTRATION.md](docs/ORCHESTRATION.md) "Step 0"; [docs/agents/engine-setup.md](docs/agents/engine-setup.md)).
7. **One heavy job at a time.** The machine has about 8 GB of RAM. Before a render or master: wait for a free slot, no other render or master running and at least 3 GB free (`tools/remix/waitfree.sh` waits for both); before Whisper: 5 GB free and no other Whisper process. Check `df -h /` before heavy work (about 40 GB usable; a session writes about 2.5 GB of WAVs).
8. **Clean up after yourself**: delete your scratch (/tmp, test renders, downloads) when your task ends ([ORCHESTRATION.md](docs/ORCHESTRATION.md) standing rule 12).
9. **Research decides over hand-picked numbers.** Genre values, mastering targets and voice decisions rest on sources and measurement; unsourced values are marked hand-tuned. Where a brief's or the owner's suggestion contradicts the research, flag it, follow the research and say why (standing rules 7, 10, 11).
10. **It's an experiment**: report misses honestly.

## Routes by role

**Orchestrator** (the root agent the owner talks to):
- [docs/HANDOFF.md](docs/HANDOFF.md) at the start of a fresh session: current state, open decisions.
- [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md) in full: standing rules, Step 0, starting a session, genre conventions, the queue, keeping sessions alive, delivery, the website.
- [docs/agents/session-workflow.md](docs/agents/session-workflow.md): the short session lifecycle.
- [docs/agents/track-storage.md](docs/agents/track-storage.md) when publishing or restoring a track.
- `prompts/producer.md` or `prompts/remix.md` when writing a brief; [docs/LESSONS.md](docs/LESSONS.md) after every genre switch.

**Producer** (Spectre, a track session):
- Your `sessions/NNN-name/PROMPT.md` is your whole brief; it names what to read: [docs/MANUAL.md](docs/MANUAL.md), the genre doc, [docs/CRAFT.md](docs/CRAFT.md) for beats, [docs/LESSONS.md](docs/LESSONS.md), [docs/PRODUCTION.md](docs/PRODUCTION.md).
- [docs/agents/project.md](docs/agents/project.md), "Core principles": the loop you work in.
- [docs/voice/](docs/voice/) (VOICES.md, MIXING.md, languages/) when a track uses a voice.

**Remix agent:** the filled `prompts/remix.md`; [docs/PRODUCTION.md](docs/PRODUCTION.md) "Remixing and remastering"; `tools/remix/README.md`; `upload_track.py --fetch` if the session folder is missing ([track-storage.md](docs/agents/track-storage.md)).

**Genre / voice research agent:**
- [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md) "Starting a new session" (steps 0-1), "Genre conventions" and standing rules 7, 8, 10, 13, 14, 16.
- [docs/PRODUCTION.md](docs/PRODUCTION.md) section 5 (the checklist a new genre must produce); [docs/MASTERING.md](docs/MASTERING.md) "Era targets"; an existing genre doc as the model.
- `tools/refcurve.py`, `tools/catalogue_stats.py`, [data/README.md](data/README.md) for catalogue measurements.
- Voices: [docs/voice/GENERAL.md](docs/voice/GENERAL.md), [VOICES.md](docs/voice/VOICES.md), [MIXING.md](docs/voice/MIXING.md), `docs/voice/languages/<code>.md`.

**Site / engineering agent** (site, engine code, tools):
- Engine: [docs/agents/engine-rules.md](docs/agents/engine-rules.md), [repo-map.md](docs/agents/repo-map.md), [known-limits.md](docs/agents/known-limits.md); keep [docs/MANUAL.md](docs/MANUAL.md) in sync; smoke test in [engine-setup.md](docs/agents/engine-setup.md).
- Site: [site/README.md](site/README.md), [site/AGENTS.md](site/AGENTS.md) (Next.js rules), [ORCHESTRATION.md](docs/ORCHESTRATION.md) "The website" and its design decisions.
- Tools: their docstrings; [track-storage.md](docs/agents/track-storage.md) for `upload_track.py`; [git.md](docs/agents/git.md).

**Setup** (third-party resources, environment): [docs/agents/engine-setup.md](docs/agents/engine-setup.md); [ORCHESTRATION.md](docs/ORCHESTRATION.md) "Step 0"; `engine/third_party.json`; [track-storage.md](docs/agents/track-storage.md) "Environment"; hosts to allow in [HANDOFF.md](docs/HANDOFF.md) section 0.

## Where things are

| Folder | What |
|---|---|
| `engine/` | the studio: instruments, the hand, the ears, mix, master, genre and voice catalogues |
| `docs/` | manual, genre briefs, production, mastering, lessons, orchestration, handoff |
| `docs/agents/` | the agent handbook this file routes to |
| `docs/voice/` | voice research: catalogue, mixing, general science, one profile per language |
| `prompts/` | producer and remix brief templates |
| `tools/` | setup, third-party assets, publishing, measurement scripts; `tools/remix/` |
| `site/` | the website (Next.js); `site/data/tracks.json` is the canonical track list |
| `data/` | reference lists behind the catalogue numbers (identifiers only) |
| `examples/` | test projects (`engine-test.json`) and A/B studies |
| `sessions/` | local working area, one folder per track; historical records, published to the bucket |
| `assets/` | badge and README images |

Full map: [docs/agents/repo-map.md](docs/agents/repo-map.md).
