# Engine conventions

Moved from AGENTS.md (section 5). Back to the router: [AGENTS.md](../../AGENTS.md). Where each module lives: [repo-map.md](repo-map.md). Smoke-test every engine change with `examples/engine-test.json` ([engine-setup.md](engine-setup.md), "Smoke test"). Engine edits while a session renders must be additive and atomic ([session-workflow.md](session-workflow.md), step 6).

- Sample rate 44.1 kHz, float32 internally, stereo `(2, n)` arrays.
- Rendering is **deterministic** for a given `project.json` (the seed is in the project). Re-rendering an old project reproduces it bit-for-bit; that's how `renders/` can stay out of git. New projects set `"seeds": "per-track"` (each track its own random streams, so adding a track leaves the others sample-identical); without it (every project before 2026-11-25) tracks share one stream in order.
- `DEFAULT_GAIN` in `studio.py` sets per-instrument starting levels; a track's `gain_db` is relative to that.
- Every render writes `vNNN.wav` (quick master, for listening while working), `vNNN.premaster.wav` (the raw mix bus, float), `vNNN.meta.json` (sections, events, per-track level envelopes) and `vNNN.project.json`.
- `master.py` only ever reads a premaster. It never touches the mix.
- New instruments go in `instruments.py`: register them in `DRUMS`, `TONAL`, `MONO` or `TEXTURES`, add a default gain in `studio.py`, document them in `docs/MANUAL.md`, and check them with `engine/gallery.py`.
- New effects go in `apply_fx` in `studio.py`; document them in `docs/MANUAL.md`.
- Keep `docs/MANUAL.md` in sync with the code. It's the only interface the producer agent sees.
