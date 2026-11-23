# CLAUDE.md

All agent instructions for this repository live in [AGENTS.md](AGENTS.md). Read it fully before making changes.

Quick rules:
- `docs/MANUAL.md` is the producer agent's only interface to the engine. Keep it in sync with the code.
- Never commit `renders/`, WAV files or `.secret` files.
- In blind sessions, never read or print a session's `.secret` until the listener has guessed.
- Smoke-test engine changes with `examples/engine-test.json` (render, listen, master) before committing.
