#!/usr/bin/env bash
# Prepare a fresh environment for Spectre (Claude Code cloud environment setup script, or by hand).
# Hanami has no direct download link: download it from https://lottev.moe/ and run
# `python3 tools/engine_assets.py import <zip>` (or, for the owner, the private mirror via SPECTRE_S3_*). See docs/HANDOFF.md, "New environment".
# In a Claude Code cloud environment the variables are only set once the session runs (not in the
# environment's setup script), so run this at the start of the session; it skips what is already there.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null; then
  (apt-get update -qq && apt-get install -y -qq ffmpeg) || echo "setup: install ffmpeg by hand (mp3 export)"
fi

pip install -q --break-system-packages -r requirements.txt

# Voicebanks from their official sources (each user accepts their licences); the owner's private
# mirror fills in what has no direct link (Hanami) when its credentials are set.
python3 tools/engine_assets.py install
if [ -n "${SPECTRE_S3_ACCESS_KEY_ID:-}" ]; then
  python3 tools/engine_assets.py pull || echo "setup: private mirror not reachable"
fi
python3 tools/engine_assets.py status
