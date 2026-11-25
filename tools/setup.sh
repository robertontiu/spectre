#!/usr/bin/env bash
# Engine setup: everything the engine, the producer and the measurement tools need, before any work on a track.
# Every third-party resource is listed in engine/third_party.json (official link or manual steps, licence,
# size, sha256, install location, search hint) and installed from its official source; nothing is bundled.
#   1. system tools and the pip requirements
#   2. tools/engine_assets.py install       (official sources)
#   3. tools/engine_assets.py pull          (an optional private mirror, only if its environment variables are
#                                            set: SPECTRE_MIRROR_BUCKET and SPECTRE_S3_*; fills in what is still missing)
#   4. tools/engine_assets.py status        (exits non-zero while a required resource is missing)
# In a Claude Code cloud environment the variables are only set once the session runs (not in the
# environment's setup script), so run this at the start of the session; it skips what is already there.
# If a required resource is still missing at the end: search for its official source (search_hint in the
# manifest), verify licence, size and sha256, install it (`engine_assets.py import <zip>` for a zip) and
# update the manifest's link (docs/agents/engine-setup.md; docs/ORCHESTRATION.md, "Step 0").
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null; then
  (apt-get update -qq && apt-get install -y -qq ffmpeg) || echo "setup: install ffmpeg by hand (mp3 export)"
fi

pip install -q --break-system-packages -r requirements.txt

python3 tools/engine_assets.py install

if [ -n "${SPECTRE_MIRROR_BUCKET:-}" ] && [ -n "${SPECTRE_S3_ACCESS_KEY_ID:-}" ]; then
  python3 tools/engine_assets.py pull || echo "setup: the mirror did not answer"
fi

if ! python3 tools/engine_assets.py status; then
  echo
  echo "setup: FAILED: a required third-party resource is still missing (see above)." >&2
  echo "setup: find its official source (search_hint in engine/third_party.json), verify it, install it, update the manifest." >&2
  exit 1
fi
echo "setup: ok, every required resource is installed"
