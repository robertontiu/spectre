# AGENTS.md: guide for AI agents taking over Spectre

Read this file fully before touching anything. It is the single source of truth for how this project works and how to continue it. If you are the **orchestrator** (the agent the owner talks to, who starts and monitors producer sessions and maintains the website), also read [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md): it holds the owner's standing rules, the delivery procedure and the website setup.

## Engine setup: third-party resources (owner's rule, 2026-11-25)

Before any work on a track, the orchestrating agent makes sure everything the engine and its measurements need is installed: run `tools/setup.sh` (pip requirements, then `tools/engine_assets.py install` from the official sources, then the optional private mirror if its environment variables are set, then `status`; it exits non-zero while a required resource is missing). Every third-party resource (voicebanks, vocoder, Whisper models, reference recordings and datasets) is listed in **`engine/third_party.json`**: what needs it, required or optional, licence, official page, direct link or manual steps, size, sha256, install location and a `search_hint`. Nothing third-party is ever bundled or committed (several licences forbid redistribution).

**If a link fails:** search the internet for the official source first (the entry's `search_hint`), check that the licence and the files match (size, sha256, folder layout), install it (`engine_assets.py import <zip>` for a zip), and update the link in the manifest. The optional private mirror (`engine_assets.py pull`, configured only through environment variables) is a fail-safe after that, never the first choice.

## 1. What this project is

**This is an experiment**, not a product. The question it explores: can an AI make music the way a human does, driven by a feeling and shaped by listening, rather than by generating audio from a prompt? Treat everything here (results, engine, prompts) as research in progress, and report outcomes honestly, including misses.

**Spectre** is an AI beat producer built as a human analogue, across genres (trap, boom-bap, rage, and folk fusions from the Middle East to the Baltics). It does not generate audio with a neural music model. It works the way a human producer does:

1. It starts from a **feeling** (given in a brief, or chosen by Spectre itself from a theme).
2. It works in a **studio** made of code: synthesized instruments, a sequencer, effects, a mix bus and a mastering stage.
3. It **listens** through "ears" that turn audio into pictures and numbers (the agent cannot hear audio, but it can see spectrograms).
4. It makes **one musical decision at a time** in a feel-listen-decide loop and journals every move.

The producer agent works as **Spectre**: the artist and the persona share one name. (Sessions 001-004 were run under an earlier persona name and were renamed to Spectre afterwards.)

It is a sibling experiment to [Teodor](https://github.com/robertontiu/teodor), an emotion-driven AI painter built on the same principles.

### Core principles (do not break these without the owner's agreement)
- **Mind/hand split.** The agent (the mind) writes musical intentions in a compact notation. The engine (the hand) performs them: swing, micro-timing, velocity phrasing, rolls, chord voicing and voice leading, strums, arps, transitions. Don't make the agent place every sample, and don't let the engine make musical decisions.
- **Feeling-first loop.** Every iteration: listen, feel (original feeling plus what the track now does), decide ONE intention, render, journal. Never render twice without listening in between.
- **Forward only.** Every render is versioned (`renders/vNNN.*`). The agent can change anything in `project.json`, but never reverts to an old version.
- **The ears are the bottleneck.** Quality is capped by how well the agent can judge what it hears. Improving the ears is usually the highest-value engine work.

## 2. Repository map

```
engine/
  instruments.py  synthesized instruments: drums, 808/bass/lead (mono, glide), keys, pads, strings, choir, bells,
                  plucks, organ, folk instruments, textures (vinyl, tape, rain), transition fx (riser, impact, reverse cymbal,
                  pitch riser); trance (clubkick, supersaw, trancebass); pop rock (acoustic kit, eguitar, cleanguitar,
                  ebass, vox: a wordless formant voice); handclap (several hands out of time; replaces the old clap);
                  lăutar band (acguitar: dry acoustic guitar with a modal body; toba: bass drum with a cymbal on top)
  chamber.py      chamber-score instruments modelled on measured recordings: `celesta`, `glockenspiel`, `vibraphone`,
                  `cello`, `viola` (the violin's waveguide with measured bodies), `strings_section` (several bowed players
                  per line), `bell` `"clean"` (docs/MANUAL.md "Chamber score instruments", examples/chamberscore/)
  violin.py       the bowed violin (`violin`): a waveguide string bowed through a friction curve (numba), a modal violin
                  body, articulations written after the note length (grace, mordent, trill, slides, double stops...)
  singer.py       voices: `singer` (sings words; parses the lyrics and hands the line to svs.py, its only source) and
                  `vox2` (improved wordless voice: LF glottal source, consonant onsets for chops); see docs/MANUAL.md "Voices"
  svs.py          `singer`'s singing voice synthesizer (`"source": "svs"`, the default): DiffSinger voicebanks, ONNX, CPU;
                  OpenUtau's code path, seeded and phrase-cached, deterministic; banks in ~/.cache/spectre/svs (never in git);
                  the male voices (`sing_up`): Hanami sung an octave up and moved down inside the synthesizer
  lang_es.py      Spanish letters to DiffSinger phonemes for svs voices with `"lang": "es"` (Hanami; docs/voice/languages/es.md)
  voices.json     the svs voice catalogue: ids, banks, licences and credit lines, tags (docs/voice/VOICES.md)
  third_party.json  every third-party resource (voicebanks, vocoder, Whisper models, reference recordings): licence,
                  official link or manual steps, size, sha256, install location, search hint (tools/engine_assets.py)
  hand.py         the hand: step/note/chord notation parser, swing, humanization, voicing, rolls, arps
  studio.py       project loader, arrangement scheduler, track rendering, fx, sends, sidechain, section
                  automation and transitions, quick master, CLI (render / listen / master)
  ear.py          the ears: arrangement lanes, mel spectrogram, band energy, loudness, per-section stats,
                  warnings; zoom view with onset grid and timing roll
  clarity.py      ears for stems (`listen --clarity`): a section re-rendered in memory, layer census, masked and own
                  share per stem, occupancy, low-mid build-up, crest, flags against the genre's EQ map, stack view
  mixbus.py       production (opt-in): stacks (`layers`), role EQ presets from eqmaps.json, group buses, named returns
                  (several reverbs/delays, filtered, ducked), fx ott / dyneq / clip / mseq, correlated humanizing
  synth.py        production sounds: `supersaw` model 2 (Szabo), `polysynth` (LFOs, envelopes, drift), `sub`, kick
                  layers (`kicksub`, `kickpunch`, `kickclick`), `metalhat` (tonal hats), `air`
  eqmaps.json     the genre EQ maps as data (per role: high-pass, cut and owned regions; core roles), from the genre docs
  master.py       the release mastering stage (see docs/MASTERING.md)
  genres.json     genre configurations (target curve, loudness and mastering settings, length, form, tempo, sources);
                  `studio.py master --genre <name>`, no default genre
  targets.json    the era target curves with provenance (written by tools/refcurve.py; docs/MASTERING.md "Era targets")
  gallery.py      dev tool: spectrogram gallery of every instrument (sanity-check sound design)
  solos.sh        diagnostic: per-track RMS and band levels via solo renders (written by the producer in session 002)
docs/
  MANUAL.md       the studio manual the producer agent reads (project format, commands, how to read the ears)
  CRAFT.md        beat craft brief: groove, drums, 808, harmony, timbre, arrangement, transitions, mix
  MASTERING.md    mastering research brief and how master.py implements it
  LESSONS.md      what each session taught us; read before changing the agent prompt or engine
  voice/          voice research: VOICES.md (the svs voice catalogue, licences, what is missing), MIXING.md (mixing a
                  voice), GENERAL.md (speech and singing science, timing, intelligibility), languages/<code>.md
prompts/
  producer.md     the producer agent prompt template (persona, brief, studio, stages, loop, finish)
site/             the website (Next.js; Vercel, spectre.robertontiu.com); data/tracks.json is the canonical track list
                  (the showcase: one line per published track, with its fixed uuid)
tools/
  setup.sh        engine setup for a new environment: requirements, third-party resources, status (fails if one is missing)
  engine_assets.py  status / install / import of engine/third_party.json; push / pull of an optional private mirror
  upload_track.py publishes a track: its uuid in tracks.json, its session files to the S3 bucket under that uuid,
                  verified; --check compares the bucket with tracks.json, --fetch restores a session folder (section 8)
  pestana_ltas.py derives the measured mastering curves from Pestana et al. (2013), Fig. 5 (see docs/MASTERING.md)
  refcurve.py     era target curves: from the open catalogue (MusicBrainz + AcousticBrainz, no audio) or from local
                  reference masters (analysis only); n, spread, provenance (docs/MASTERING.md "Era targets")
  catalogue_stats.py  the genre docs' catalogue numbers (album lengths, tempos, keys, est. loudness; trance radio
                  edits; era rows; the ReplayGain-to-LUFS calibration) and the commands that rebuild engine/targets.json
  humanref.py     measures how human singers time English syllables in the GTSinger corpus (the evidence in
                  docs/voice/GENERAL.md "Timing"; data cached in ~/.cache/spectre/refs, never committed)
data/
  catalogue_references.json  the reference lists behind the catalogue numbers and the era targets (MusicBrainz
                  release ids per genre and strand, tags and years; identifiers only, no audio; data/README.md)
sessions/
  NNN-name/       one folder per session: project.json, journal.md, mastered mp3, ear and master images,
                  README.md with the result. A local working area: published sessions live in the S3 bucket
                  under their track's uuid (section 8); the folders still in git leave it after the migration
examples/
  anthem/         the verified melody of Romania's anthem: a piano check render, the CC BY-SA score it was read
                  from, the check scripts (transcription in docs/ROMANIAN.md, "Verified melody")
  chamberscore/   chamber-score instruments A/B (old stand-ins vs celesta, glockenspiel, vibraphone, cello, viola,
                  strings_section) and spectrograms against reference recordings (build.py)
  production/     the production upgrade A/B: First Light and Half of Me excerpts as published vs rebuilt with stacks
                  (mp3, clarity numbers, spectrograms; build.py)
  joc/            lăutar band A/B (old fiddle vs violin, the violin's articulations, acguitar, toba, a tempo ramp; build.py)
  vocals/         svs/: the singer's voices (auditions in voices/, voices.py; male.py for the male ones), the DiffSinger trial (dsinger.py, build.py),
                  the mix study (blend.py), choir and vibrato tests (vibrato.py), Spanish and Romanian checks; the
                  wordless vox and vox2 on a trance hook and session 009's hook (mp3 only)
  engine-test.json  a small project that exercises most engine features (render it to smoke-test changes)
  trance-test.json, poprock-test.json  small projects that exercise the trance and pop rock sounds
```

## 3. Setup

Python 3.11+ (developed on 3.13) and ffmpeg on PATH.

```bash
pip install -r requirements.txt
```

Then install the third-party resources: `tools/setup.sh` (or `python3 tools/engine_assets.py install`; see "Engine setup: third-party resources" above and `engine/third_party.json`).

Sung words (`singer`) use DiffSinger voicebanks, neural models trained on singers (approved by the owner; everything else in Spectre stays synthesized). Their files are not in the repo (the voicebank terms forbid redistributing them): banks go in `~/.cache/spectre/svs/<bank>/bank/` and the Potluck vocoder in `~/.cache/spectre/svs/potluck/` (links and licences in engine/third_party.json; `SPECTRE_SVS_DIR` moves them). The Whisper models for word checks go in the Hugging Face cache at `~/.cache/spectre/svs/hf` (the scripts set `HF_HOME` to it). Rendered phrases are cached in `~/.cache/spectre/svs/phrases/`: safe to delete, they regenerate bit for bit. Only projects with a `singer` track need any of this.

Smoke test (about 20 s to render, 25 s to listen):

```bash
mkdir -p /tmp/smoke && cp examples/engine-test.json /tmp/smoke/project.json
cd /tmp/smoke && export BEAT_DIR=$PWD
python3 <repo>/engine/studio.py render && python3 <repo>/engine/studio.py listen
python3 <repo>/engine/studio.py master --genre trap   # writes renders/v001.master.{wav,mp3,png,report.json}
```
Open `ear.png` and `renders/v001.master.png` to check that the pipeline works.

## 4. Running a producer session

1. Create `sessions/NNN-shortname/` and write the brief into `PROMPT.md` there (see `docs/ORCHESTRATION.md`).
2. Fill in `prompts/producer.md` (placeholders in `{{...}}`) and run it as a sub-agent with file, shell and image-reading tools. A full session is 25-45 iterations, about 30-60 minutes.
3. When it finishes: check the master report (genre, LUFS, true peak under -1 dBTP, no warnings), check the length against the genre (see "Genre conventions" in docs/ORCHESTRATION.md), copy `final.mp3`, and write the session `README.md` (see `sessions/001-bleachers/README.md` for the format).
4. Long sessions can be interrupted (for example when the operator's own turn is interrupted). Check on them periodically; to resume, start a fresh producer agent with the same prompt plus "read journal.md and the helper scripts, listen to the latest render, continue numbering". Forward-only versioning makes this seamless.
5. **After every genre switch, record lessons in the repo** (owner's standing rule): add the session entry to `docs/LESSONS.md` and update its "Across genres" section with what transferred and what didn't. If the new genre needed research, save it as a `docs/<GENRE>.md` brief (see `docs/ROMANIAN.md`, `docs/UKRAINIAN.md`). Commit these with the session.
6. Sessions can run in parallel (one folder each). Engine changes made while another session is rendering must be additive and written atomically (write a temp file, then rename), so a running render never imports a half-written module.
7. **Publish** the session with `python3 tools/upload_track.py <id>` (section 8) once its line is in `site/data/tracks.json`: the session's files go to the S3 bucket, not into git (without a bucket: the tool uploads nothing, lists the files and you send them to the user in the chat; section 8) (renders never leave the workspace; they are reproducible from `project.json`, because rendering is seeded and deterministic). Commit `site/data/tracks.json` (it now carries the track's uuid) and the cross-track files (docs, engine, lessons).

## 5. Engine conventions

- Sample rate 44.1 kHz, float32 internally, stereo `(2, n)` arrays.
- Rendering is **deterministic** for a given `project.json` (the seed is in the project). Re-rendering an old project reproduces it bit-for-bit; that's how `renders/` can stay out of git. New projects set `"seeds": "per-track"` (each track its own random streams, so adding a track leaves the others sample-identical); without it (every project before 2026-11-25) tracks share one stream in order.
- `DEFAULT_GAIN` in `studio.py` sets per-instrument starting levels; a track's `gain_db` is relative to that.
- Every render writes `vNNN.wav` (quick master, for listening while working), `vNNN.premaster.wav` (the raw mix bus, float), `vNNN.meta.json` (sections, events, per-track level envelopes) and `vNNN.project.json`.
- `master.py` only ever reads a premaster. It never touches the mix.
- New instruments go in `instruments.py`: register them in `DRUMS`, `TONAL`, `MONO` or `TEXTURES`, add a default gain in `studio.py`, document them in `docs/MANUAL.md`, and check them with `engine/gallery.py`.
- New effects go in `apply_fx` in `studio.py`; document them in `docs/MANUAL.md`.
- Keep `docs/MANUAL.md` in sync with the code. It's the only interface the producer agent sees.

## 6. Known limits and open directions (in priority order)

1. **The ears can't hear attitude.** Structure reads well on spectrograms; timbre and emotional "bite" don't. Session 001 aimed for defiance and came across as longing. Ideas: an audio-capable model as a critic ("describe what you hear, without naming emotions"), CLAP-style embeddings as a weak signal, or a human checkpoint ear after the loop stage.
2. **Synth timbres lean soft.** No real samples. Real drum one-shots or sample packs (the user would provide them; the sandbox network is restricted) would raise quality a lot.
3. **Vocals are new.** `singer` sings with DiffSinger voices (approved by the owner by ear, 2026-11-24), English and Spanish. Male voices: `hanami-male` and `hanami-male-es` (Hanami sung an octave up and moved down inside the synthesizer; approved by the owner by ear, 2026-11-25; docs/voice/VOICES.md "Male voices"). No Romanian voice. A generative model as a "session musician" (stems on demand) is the planned v2 for metal and pop.
4. **Mastering targets** are per-genre configurations (`engine/genres.json`, `--genre <name>`, no default). Since 2026-11-25 every genre except `trap` masters toward an era target measured from open catalogue data (trance, hip hop, pop rock: 2015-2021) or from the reference records its genre doc chose (joc, caroling, Latin pop, chamber score), with provenance (`tools/refcurve.py`, docs/MASTERING.md "Era targets"); the older Pestana-derived curves stay available and `--published` reproduces the released masters' settings. Still open: the data end in 2021-2022, so the definitive targets are 20-30 current reference masters per genre measured locally (`refcurve.py measure`), with the owner.
5. **Speed.** A full-length render takes 20-45 s. Per-track caching would make the loop faster.

## 7. Git

- Default branch `main`. Commit engine changes separately from session results.
- Don't commit `renders/`, WAVs, `__pycache__`, or voice model files and caches (`~/.cache/spectre/`). Track files (masters, journals, project files, session images and scripts) go to the S3 bucket, not into git (section 8); the repo keeps only cross-track files: engine, tools, docs, prompts, examples and the site. If a model ever has to be versioned, put it under `models/` with a README (source, licence, size, checksum); GitHub refuses files over 100 MB and git LFS uploads are blocked from the sandbox, so split larger files into parts under 50 MB (`split -b 48000000 -d -a 2 <file> <file>.part`) and join them in the loader, checksum-verified.
- MIT licensed (see `LICENSE`).

## 8. Track files in S3

Every published track's files live in an S3-compatible bucket configured through environment variables, not in the repo. `site/data/tracks.json` is the showcase list: each track has a fixed `uuid` (v4, made once when it is first published, never changed), and that uuid is the key prefix of all its files. The names are the same for every track and defined once, in `tools/upload_track.py` (`RENDITION`, `NAMED`, `TOOLS`; the site's audio route reads `TRACK_OBJECTS` in `site/src/lib/s3.ts`):

| Object | From the session folder |
|---|---|
| `<uuid>/rendition.mp3` | `<title-slug>-mastered.mp3` (the published master; the site plays it) |
| `<uuid>/journal.md` | `journal.md` |
| `<uuid>/readme.md` | `README.md` |
| `<uuid>/prompt.md` | `PROMPT.md` |
| `<uuid>/project.json` | `project.json` |
| `<uuid>/master-report.json` | `master-report.json` |
| `<uuid>/master-tonal-balance.png` | `master-tonal-balance.png` |
| `<uuid>/ear-overview.png` | `ear-overview.png` |
| `<uuid>/tools/<path>` | every other published file (build and helper scripts), its path in the folder kept |

**What is published, and nothing else:** the files git tracks in the session folder (the sessions from before the move), plus the named files above and helper scripts (`*.py`, `*.sh`) anywhere in the folder. Never `renders/`, WAVs, `__pycache__`, listen dumps, trial masters, A/B excerpts or other scratch: they stay local and are cleaned up (ORCHESTRATION.md, standing rule 12). A session must have exactly one `*-mastered.mp3`, `journal.md`, `README.md` and `project.json`. The tool takes tracks by id, slug or uuid from `tracks.json`, never by file path, and refuses anything else.

**Workflow.** Work happens locally in `sessions/<id>-<name>/`. Publishing a track, or a new version of one (a remix, a remaster), is one step:

```bash
python3 tools/upload_track.py <id>        # 1. a uuid in tracks.json if the track is new
                                          # 2. upload every new or changed file (MD5 compared; unchanged skipped)
                                          # 3. verify (Content-MD5 on upload, then size and ETag)
python3 tools/upload_track.py --check     # the bucket against tracks.json and the local sessions
python3 tools/upload_track.py --fetch <id>   # restore sessions/<folder>/ from the bucket (to remix it);
                                             # refuses to overwrite local changes without --force
```

Committing `tracks.json` and pushing stay in the normal delivery step (ORCHESTRATION.md, "Delivering a finished session"). Every object is private; the site reaches the master only through short-lived presigned URLs (site/README.md, "Audio").

**Environment** (values never committed; in the workspace's shell, not in any file in the repo):

| Variable | Workspace (upload) | Vercel (site) |
|---|---|---|
| `SPECTRE_S3_ENDPOINT` | e.g. `https://s3.<region>.example.com` | same |
| `SPECTRE_S3_REGION` | e.g. `<region>` | same |
| `SPECTRE_S3_BUCKET` | e.g. `<your-bucket>` | same |
| `SPECTRE_S3_ACCESS_KEY_ID` / `SPECTRE_S3_SECRET_ACCESS_KEY` | a **read-write** key | a **read-only** key |
| `SPECTRE_SIGNED_URL_TTL` | | optional, default 3600 s |
| `SPECTRE_S3_CORS_ORIGINS` | optional, replaces the default CORS origins for `--cors` | |

`--cors` sets the bucket's CORS rules for the player (needed once; the key must be allowed to set bucket CORS). Requires `boto3` (in requirements.txt). The S3 settings and keys come from the environment only; ask the owner for them.

**Without a bucket** (none of the `SPECTRE_S3_*` variables set: a fork, a fresh clone, or a workspace without the keys), the workflow still works. `python3 tools/upload_track.py <id>` uploads nothing and does not fail: it runs every local check (uuid in `tracks.json`, the publish set, the required files, the MP3), then prints "No S3 bucket configured: nothing uploaded. Deliver these files to the user in the chat:" with the mastered MP3 and the other publishable files and their paths, and exits 0. The publish step then means sending those files to the user in the chat (SendUserFile or the platform's equivalent), and the session folders stay local (they are the only copy: don't delete them). `--all`, `--check`, `--cors` and `--fetch` say that they need the bucket and are skipped (exit 0). A partial set of the variables is refused (set all five, or none). The site plays the local masters without a bucket (site/README.md, "Audio").
