# Engine setup: environment and third-party resources

Moved from AGENTS.md ("Engine setup: third-party resources" and section 3, "Setup"). Back to the router: [AGENTS.md](../../AGENTS.md). The step-by-step procedure, including what to do when a link fails, is [docs/ORCHESTRATION.md](../ORCHESTRATION.md) "Step 0, before any session: engine setup".

## Third-party resources (owner's rule, 2026-11-25)

Before any work on a track, the orchestrating agent makes sure everything the engine and its measurements need is installed: run `tools/setup.sh` (pip requirements, then `tools/engine_assets.py install` from the official sources, then the optional private mirror if its environment variables are set, then `status`; it exits non-zero while a required resource is missing). Every third-party resource (voicebanks, vocoder, Whisper models, reference recordings and datasets) is listed in **`engine/third_party.json`**: what needs it, required or optional, licence, official page, direct link or manual steps, size, sha256, install location and a `search_hint`. Nothing third-party is ever bundled or committed (several licences forbid redistribution).

**If a link fails:** follow ORCHESTRATION.md "Step 0", items 2-3: the official source first (the entry's `search_hint`), licence and files checked, the manifest's link updated; the optional private mirror (`engine_assets.py pull`, configured only through environment variables) is a fail-safe after that, never the first choice.

## Requirements

Python 3.11+ (developed on 3.13) and ffmpeg on PATH.

```bash
pip install -r requirements.txt
```

Then install the third-party resources: `tools/setup.sh` (or `python3 tools/engine_assets.py install`; see "Third-party resources" above and `engine/third_party.json`).

## Voices: voicebanks, vocoder, Whisper

Sung words (`singer`) use DiffSinger voicebanks, neural models trained on singers (approved by the owner; everything else in Spectre stays synthesized). Their files are not in the repo (the voicebank terms forbid redistributing them): banks go in `~/.cache/spectre/svs/<bank>/bank/` and the Potluck vocoder in `~/.cache/spectre/svs/potluck/` (links and licences in engine/third_party.json; `SPECTRE_SVS_DIR` moves them). The Whisper models for word checks go in the Hugging Face cache at `~/.cache/spectre/svs/hf` (the scripts set `HF_HOME` to it). Rendered phrases are cached in `~/.cache/spectre/svs/phrases/`: safe to delete, they regenerate bit for bit. Only projects with a `singer` track need any of this.

## Smoke test

Smoke test (about 20 s to render, 25 s to listen):

```bash
mkdir -p /tmp/smoke && cp examples/engine-test.json /tmp/smoke/project.json
cd /tmp/smoke && export BEAT_DIR=$PWD
python3 <repo>/engine/studio.py render && python3 <repo>/engine/studio.py listen
python3 <repo>/engine/studio.py master --genre trap   # writes renders/v001.master.{wav,mp3,png,report.json}
```
Open `ear.png` and `renders/v001.master.png` to check that the pipeline works.
