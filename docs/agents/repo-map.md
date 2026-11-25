# Repository map

Moved from AGENTS.md (section 2). Back to the router: [AGENTS.md](../../AGENTS.md); the agent handbook files are in `docs/agents/`.

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
  acid.py         `acid`: a 303-style monophonic line (accent coupled to filter envelope and level, slide, resonant
                  18/24 dB zero-delay ladder, drive); numba
  tr909.py        `snare909`, `clap909`, `ride909`: TR-909-style drums fitted to a recorded TR-909
                  (examples/production/modern/measure909.py)
  spacefx.py      `shimmer` (pitch-shifted feedback reverb), `granular` (grain cloud / freeze / stretch) as fx and return
                  types, `suppress` (dynamic resonance suppressor); numba; section automation curves come from studio.py
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
                  verified; --check compares the bucket with tracks.json, --fetch restores a session folder
                  (docs/agents/track-storage.md)
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
                  under their track's uuid (docs/agents/track-storage.md); out of git since 2026-11-25
                  (.gitignore); `upload_track.py --fetch <id>` restores one
examples/
  anthem/         the verified melody of Romania's anthem: a piano check render, the CC BY-SA score it was read
                  from, the check scripts (transcription in docs/ROMANIAN.md, "Verified melody")
  chamberscore/   chamber-score instruments A/B (old stand-ins vs celesta, glockenspiel, vibraphone, cello, viola,
                  strings_section) and spectrograms against reference recordings (build.py)
  production/     the production upgrade A/B: First Light and Half of Me excerpts as published vs rebuilt with stacks
                  (mp3, clarity numbers, spectrograms; build.py); modern/: the modern-strand tools (shimmer, granular,
                  acid, 909, slide and accent, automated sounds, suppress) as short A/Bs (build.py) and the 909 fit
                  (measure909.py)
  joc/            lăutar band A/B (old fiddle vs violin, the violin's articulations, acguitar, toba, a tempo ramp; build.py)
  vocals/         svs/: the singer's voices (auditions in voices/, voices.py; male.py for the male ones), the DiffSinger trial (dsinger.py, build.py),
                  the mix study (blend.py), choir and vibrato tests (vibrato.py), Spanish and Romanian checks; the
                  wordless vox and vox2 on a trance hook and session 009's hook (mp3 only)
  engine-test.json  a small project that exercises most engine features (render it to smoke-test changes)
  trance-test.json, poprock-test.json  small projects that exercise the trance and pop rock sounds
  trance-modern-test.json  a small project that exercises acid, the 909 drums, shimmer and granular returns, suppress,
                  polysynth slide and accent, and section automation of instrument, fx and return parameters
```
