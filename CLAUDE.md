# CLAUDE.md

All agent instructions for this repository live in [AGENTS.md](AGENTS.md). Read it fully before making changes. If you orchestrate sessions or maintain the players, also read [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md).

Quick rules:
- `docs/MANUAL.md` is the producer agent's only interface to the engine. Keep it in sync with the code.
- Never commit `renders/`, WAV files or `.secret` files.
- In blind sessions, never read or print a session's `.secret` until the listener has guessed.
- Smoke-test engine changes with `examples/engine-test.json` (render, listen, master) before committing.
- The artist is called Spectre everywhere.
- Never leave a producer session stopped: check every ~15 minutes and resume from its PROMPT.md and journal.
- Record lessons in docs/LESSONS.md after every genre switch.
