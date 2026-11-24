# AGENTS.md: guide for AI agents taking over Spectre

Read this file fully before touching anything. It is the single source of truth for how this project works and how to continue it. If you are the **orchestrator** (the agent the owner talks to, who starts and monitors producer sessions and maintains the website), also read [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md): it holds the owner's standing rules, the delivery procedure and the website setup.

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
                  ebass, vox: a wordless formant voice); handclap (several hands out of time; replaces the old clap)
  singer.py       voices: `singer` (sings words: words from eSpeak NG or, with `source: "tts"`, sampled from a local
                  TTS, then laid on the melody with the WORLD vocoder) and `vox2` (improved wordless voice: LF glottal
                  source, consonant onsets for chops); see docs/MANUAL.md "Voices"
  tts_words.py    the word sampler for `singer` `source: "tts"`: Kokoro TTS (local, Apache 2.0) speaks each word
                  neutrally into a cache (~/.cache/spectre/words), WORLD analysis, syllable segmentation
  hand.py         the hand: step/note/chord notation parser, swing, humanization, voicing, rolls, arps
  studio.py       project loader, arrangement scheduler, track rendering, fx, sends, sidechain, section
                  automation and transitions, quick master, CLI (render / listen / master)
  ear.py          the ears: arrangement lanes, mel spectrogram, band energy, loudness, per-section stats,
                  warnings; zoom view with onset grid and timing roll
  master.py       the release mastering stage (see docs/MASTERING.md)
  genres.json     genre configurations (target curve, loudness and mastering settings, length, form, tempo, sources);
                  `studio.py master --genre <name>`, no default genre
  gallery.py      dev tool: spectrogram gallery of every instrument (sanity-check sound design)
  solos.sh        diagnostic: per-track RMS and band levels via solo renders (written by the producer in session 002)
docs/
  MANUAL.md       the studio manual the producer agent reads (project format, commands, how to read the ears)
  CRAFT.md        beat craft brief: groove, drums, 808, harmony, timbre, arrangement, transitions, mix
  MASTERING.md    mastering research brief and how master.py implements it
  LESSONS.md      what each session taught us; read before changing the agent prompt or engine
prompts/
  producer.md     the producer agent prompt template (persona, brief, studio, stages, loop, finish)
site/             the website (Next.js; Vercel, spectre.robertontiu.com); data/tracks.json is the canonical track list
tools/
  sync_tracks.py  copies each session's mastered MP3 into site/public/tracks
  pestana_ltas.py derives the measured mastering curves from Pestana et al. (2013), Fig. 5 (see docs/MASTERING.md)
sessions/
  NNN-name/       one folder per session: project.json, journal.md, mastered mp3, ear and master images,
                  README.md with the result
models/
  tts/kokoro/     Kokoro v1.0 TTS model files for `singer` `source: "tts"` (the .onnx split in 7 parts; README with source,
                  licence, size, checksums); may move out of the repo later (SPECTRE_TTS_DIR)
examples/
  vocals/         voice A/B renders (diagnostic/: the eSpeak singer; tts/: sampled words autotuned, with build.py)
  engine-test.json  a small project that exercises most engine features (render it to smoke-test changes)
  trance-test.json, poprock-test.json  small projects that exercise the trance and pop rock sounds
```

## 3. Setup

Python 3.11+ (developed on 3.13), ffmpeg on PATH, and eSpeak NG for the `singer` voice's eSpeak sources (`apt install espeak-ng`; only projects that use them need it).

```bash
pip install -r requirements.txt   # includes kokoro-onnx (onnxruntime, phonemizer, espeakng-loader) for singer "tts"
```

Sung words (`singer` with `"source": "tts"`) use a local neural text-to-speech, Kokoro v1.0 (Apache 2.0), as a **word sampler only** (approved by the owner; everything else in Spectre stays synthesized). Its model files are versioned in `models/tts/kokoro/` (the 325 MB `kokoro-v1.0.onnx` split into seven parts under 50 MB, `kokoro-v1.0.onnx.part00`-`part06`, which the engine joins and checksum-verifies on first use into the gitignored `kokoro-v1.0.onnx`; `voices-v1.0.bin`, 28 MB; source URL, licence and checksums in `models/tts/kokoro/README.md`); `SPECTRE_TTS_DIR` points the engine elsewhere if they move out of the repo. Generated words are cached in `~/.cache/spectre/words/` (`SPECTRE_WORDS_DIR` to move it): outside the repo, never committed, safe to delete (they regenerate deterministically on the next render). Only projects that use `"source": "tts"` need any of this.

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
7. Commit the session folder **without** `renders/` (the WAVs are large and reproducible from `project.json`, because rendering is seeded and deterministic).

## 5. Engine conventions

- Sample rate 44.1 kHz, float32 internally, stereo `(2, n)` arrays.
- Rendering is **deterministic** for a given `project.json` (the seed is in the project). Re-rendering an old project reproduces it bit-for-bit; that's how `renders/` can stay out of git.
- `DEFAULT_GAIN` in `studio.py` sets per-instrument starting levels; a track's `gain_db` is relative to that.
- Every render writes `vNNN.wav` (quick master, for listening while working), `vNNN.premaster.wav` (the raw mix bus, float), `vNNN.meta.json` (sections, events, per-track level envelopes) and `vNNN.project.json`.
- `master.py` only ever reads a premaster. It never touches the mix.
- New instruments go in `instruments.py`: register them in `DRUMS`, `TONAL`, `MONO` or `TEXTURES`, add a default gain in `studio.py`, document them in `docs/MANUAL.md`, and check them with `engine/gallery.py`.
- New effects go in `apply_fx` in `studio.py`; document them in `docs/MANUAL.md`.
- Keep `docs/MANUAL.md` in sync with the code. It's the only interface the producer agent sees.

## 6. Known limits and open directions (in priority order)

1. **The ears can't hear attitude.** Structure reads well on spectrograms; timbre and emotional "bite" don't. Session 001 aimed for defiance and came across as longing. Ideas: an audio-capable model as a critic ("describe what you hear, without naming emotions"), CLAP-style embeddings as a weak signal, or a human checkpoint ear after the loop stage.
2. **Synth timbres lean soft.** No real samples. Real drum one-shots or sample packs (the user would provide them; the sandbox network is restricted) would raise quality a lot.
3. **Vocals are new and unproven.** `singer` with `source: "tts"` sings words sampled from a local TTS and autotuned (2026-11-24; awaiting the owner's listening verdict, A/B in `examples/vocals/tts/`); the eSpeak sources sound robotic. A generative model as a "session musician" (stems on demand) is the planned v2 for metal and pop.
4. **Mastering targets** are per-genre configurations (`engine/genres.json`, `--genre trap|hiphop|trance|rock`, no default). The `hiphop`, `trance` and `rock` curves are measured from published genre spectra (Pestana et al. 2013; docs/MASTERING.md) but pool 1950-2010 records; the `trap` curve (`beat`, sessions 001-006) is hand-tuned. Measuring modern reference tracks per genre would help.
5. **Speed.** A full-length render takes 20-45 s. Per-track caching would make the loop faster.

## 7. Git

- Default branch `main`. Commit engine changes separately from session results.
- Don't commit `renders/`, WAVs, `__pycache__`, or the TTS word cache (`~/.cache/spectre/words`). Model files go under `models/` with a README (source, licence, size, checksum); GitHub refuses files over 100 MB and git LFS uploads are blocked from the sandbox, so split larger files into parts under 50 MB (`split -b 48000000 -d -a 2 <file> <file>.part`) and join them in the loader, checksum-verified (see `engine/tts_words.py`).
- MIT licensed (see `LICENSE`).
