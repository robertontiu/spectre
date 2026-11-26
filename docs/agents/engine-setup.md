# Engine setup: environment and third-party resources

Moved from AGENTS.md ("Engine setup: third-party resources" and section 3, "Setup"). Back to the router: [AGENTS.md](../../AGENTS.md). The step-by-step procedure, including what to do when a link fails, is [docs/ORCHESTRATION.md](../ORCHESTRATION.md) "Step 0, before any session: engine setup".

## Third-party resources (owner's rule, 2026-11-25)

Before any work on a track, the orchestrating agent makes sure everything the engine and its measurements need is installed: run `tools/setup.sh` (pip requirements, then `tools/engine_assets.py install` from the official sources, then the optional private mirror if its environment variables are set, then `status`; it exits non-zero while a required resource is missing). Every third-party resource (voicebanks, vocoder, Whisper models, reference recordings and datasets) is listed in **`engine/third_party.json`**: what needs it, required or optional, licence, official page, direct link or manual steps, size, sha256, install location and a `search_hint`. Nothing third-party is ever bundled or committed (several licences forbid redistribution).

**Reading `install`'s output:** `ok` / `have` installed; `skip` fetched on demand or only on request (TIGER); `todo` needs you, with its reason: *download interrupted* (retried with backoff already; the link works, run `install <id>` again later), *no direct link recorded yet* (the official source is the entry's `page`; find the file and record its URL: never report this as having no official link), *link dead* or a size / sha256 mismatch (the source moved; search again). Optional entries get the same treatment. Where the GitHub API answers 403 but git works, list a repository with `git clone --filter=blob:none --no-checkout` and `git ls-tree`, and record raw.githubusercontent.com links pinned to a commit.

**If a link fails:** follow ORCHESTRATION.md "Step 0", items 2-3: the official source first (the entry's `search_hint`), licence and files checked, the manifest's link updated; the optional private mirror (`engine_assets.py pull`, configured only through environment variables) is a fail-safe after that, never the first choice.

## Requirements

Python 3.11+ (developed on 3.13), ffmpeg on PATH, about 8 GB of RAM (16 GB is comfortable) and 8-10 GB of disk: 2.1 GB of required models (5 GB with the optional ones), about 1 GB of Python packages, and about 35 MB of WAVs per render per minute of track (every render is kept until the session's clean-up: a full 3-minute session writes 2.5-4 GB). The agent must be able to look at PNG images: they are its ears. Tested on Linux; macOS (setup.sh installs ffmpeg with Homebrew if it is there) and Windows (through WSL) are untested.

In a fresh clone, from the repo root:

```bash
python3 -m venv .venv && . .venv/bin/activate   # recommended: keeps the packages out of the system Python
tools/setup.sh --required                        # the required models only (about 2.1 GB); without the flag, everything (about 5 GB)
```

Measured on a clean cloud container (2026-11-26; fresh HOME, no `SPECTRE_*` variables): `tools/setup.sh --required` 2.7 minutes in all (the pip requirements 0.9 GB in the venv, the models 2.1 GB in `~/.cache/spectre`); the full `tools/setup.sh` 14.6 minutes and 5.1 GB, of which about 8 minutes was Wikimedia rate-limiting the optional `refs-anthem`. Download speed sets the time on a home connection. `pyworld` (measurement scripts in `examples/vocals/svs/` only) is installed separately and may compile from source; a failure there does not stop setup. The private mirror is skipped without its variables.

**Optional entries in your own clone.** An optional resource that ends as `todo` (for example `refs-anthem` after a rate limit, or a flaky host) does not affect producing tracks: it serves research and measurement scripts only. The Step 0 duty to resolve every `todo` is the owner's workspace rule; elsewhere, report it and carry on.

Without setup.sh: `pip install -r requirements.txt`, then `python3 tools/engine_assets.py install --required` (see "Third-party resources" above and `engine/third_party.json`).

## Voices: voicebanks, vocoder, Whisper

Sung words (`singer`) use DiffSinger voicebanks, neural models trained on singers (approved by the owner; everything else in Spectre stays synthesized). Their files are not in the repo (the voicebank terms forbid redistributing them): banks go in `~/.cache/spectre/svs/<bank>/bank/` and the Potluck vocoder in `~/.cache/spectre/svs/potluck/` (links and licences in engine/third_party.json; `SPECTRE_SVS_DIR` moves them). The Whisper models for word checks go in the Hugging Face cache at `~/.cache/spectre/svs/hf` (the scripts set `HF_HOME` to it). Rendered phrases are cached in `~/.cache/spectre/svs/phrases/`: safe to delete, they regenerate bit for bit. Only projects with a `singer` track need any of this.

## Smoke test

Smoke test (about 20 s to render, 20 s to listen, 1-2 minutes to master). In a scratch folder of your own (AGENTS.md rule 8); `<repo>` is the absolute path of the clone:

```bash
SMOKE=$(mktemp -d) && cp <repo>/examples/engine-test.json $SMOKE/project.json
cd $SMOKE && export BEAT_DIR=$PWD
python3 <repo>/engine/studio.py render && python3 <repo>/engine/studio.py listen
python3 <repo>/engine/studio.py master --genre trap   # writes renders/v001.master.{wav,mp3,png,report.json}
```
Open `ear.png` and `renders/v001.master.png` to check that the pipeline works, then delete the folder. After a change to the modern-strand tools (`acid`, the 909 drums, `shimmer`, `granular`, `suppress`, section automation of sounds), also render `examples/trance-modern-test.json` (about 10 s; it exercises all of them) and, for engine changes in general, check that an earlier project's premaster stays bit-identical.
