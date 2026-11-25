# Git

Moved from AGENTS.md (section 7). Back to the router: [AGENTS.md](../../AGENTS.md), which holds the always-on git rules (what never to commit, commit by path, a push publishes every local commit).

- Default branch `main`. Commit engine changes separately from session results.
- Track files (masters, journals, project files, session images and scripts) go to the S3 bucket, not into git ([track-storage.md](track-storage.md)); the repo keeps only cross-track files: engine, tools, docs, prompts, examples and the site.
- If a model ever has to be versioned, put it under `models/` with a README (source, licence, size, checksum); GitHub refuses files over 100 MB and git LFS uploads are blocked from the sandbox, so split larger files into parts under 50 MB (`split -b 48000000 -d -a 2 <file> <file>.part`) and join them in the loader, checksum-verified.
- MIT licensed (see `LICENSE`).
