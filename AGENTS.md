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
  hand.py         the hand: step/note/chord notation parser, swing, humanization, voicing, rolls, arps
  studio.py       project loader, arrangement scheduler, track rendering, fx, sends, sidechain, section
                  automation and transitions, quick master, CLI (render / listen / master)
  ear.py          the ears: arrangement lanes, mel spectrogram, band energy, loudness, per-section stats,
                  warnings; zoom view with onset grid and timing roll
  clarity.py      ears for stems (`listen --clarity`): a section re-rendered in memory, layer census, masked and own
                  share per stem, occupancy, low-mid build-up, crest, flags against the genre's EQ map
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
tools/
  sync_tracks.py  copies each session's mastered MP3 into site/public/tracks
  pestana_ltas.py derives the measured mastering curves from Pestana et al. (2013), Fig. 5 (see docs/MASTERING.md)
  refcurve.py     era target curves: from the open catalogue (MusicBrainz + AcousticBrainz, no audio) or from local
                  reference masters (analysis only); n, spread, provenance (docs/MASTERING.md "Era targets")
  humanref.py     measures how human singers time English syllables in the GTSinger corpus (the evidence in
                  docs/voice/GENERAL.md "Timing"; data cached in ~/.cache/spectre/refs, never committed)
sessions/
  NNN-name/       one folder per session: project.json, journal.md, mastered mp3, ear and master images,
                  README.md with the result
examples/
  anthem/         the verified melody of Romania's anthem: a piano check render, the CC BY-SA score it was read
                  from, the check scripts (transcription in docs/ROMANIAN.md, "Verified melody")
  chamberscore/   chamber-score instruments A/B (old stand-ins vs celesta, glockenspiel, vibraphone, cello, viola,
                  strings_section) and spectrograms against reference recordings (build.py)
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

Sung words (`singer`) use DiffSinger voicebanks, neural models trained on singers (approved by the owner; everything else in Spectre stays synthesized). Their files are not in the repo (the voicebank terms forbid redistributing them): banks go in `~/.cache/spectre/svs/<bank>/bank/` and the Potluck vocoder in `~/.cache/spectre/svs/potluck/` (download links in docs/voice/VOICES.md; `SPECTRE_SVS_DIR` moves them). Rendered phrases are cached in `~/.cache/spectre/svs/phrases/`: safe to delete, they regenerate bit for bit. Only projects with a `singer` track need any of this.

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
- Don't commit `renders/`, WAVs, `__pycache__`, or voice model files and caches (`~/.cache/spectre/`). If a model ever has to be versioned, put it under `models/` with a README (source, licence, size, checksum); GitHub refuses files over 100 MB and git LFS uploads are blocked from the sandbox, so split larger files into parts under 50 MB (`split -b 48000000 -d -a 2 <file> <file>.part`) and join them in the loader, checksum-verified.
- MIT licensed (see `LICENSE`).
