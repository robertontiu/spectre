"""Sync the track list and the mastered MP3s to every player.

web/data/tracks.json is the canonical track list (newest first). This script

  - writes site/tracks/tracks.json from it (the static showcase artifact fetches that copy),
  - copies each session's mastered MP3 into site/tracks/, player/tracks/ and
    web/public/tracks/ under the file name the track's "src" expects.

    python3 tools/sync_tracks.py

A track's id (e.g. "005") selects sessions/005-*/; the first *-mastered.mp3 there is used.
The MP3 copies are gitignored; the session folders hold the originals. (The Next.js site
also copies its MP3s itself before every build: web/scripts/sync-tracks.mjs.)
"""
import glob, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL = os.path.join(ROOT, "web", "data", "tracks.json")
DESTS = ("site/tracks", "player/tracks", "web/public/tracks")

with open(CANONICAL, encoding="utf-8") as f:
    tracks = json.load(f)

# Same layout as the canonical file: one track per line.
site_json = os.path.join(ROOT, "site", "tracks", "tracks.json")
os.makedirs(os.path.dirname(site_json), exist_ok=True)
with open(site_json, "w", encoding="utf-8") as f:
    f.write("[\n" + ",\n".join(json.dumps(t, ensure_ascii=False, separators=(",", ":")) for t in tracks) + "\n]\n")
print(f"site/tracks/tracks.json: {len(tracks)} tracks from web/data/tracks.json")

missing = 0
for t in tracks:
    hits = sorted(glob.glob(os.path.join(ROOT, "sessions", f"{t['id']}-*", "*-mastered.mp3")))
    if not hits:
        print(f"missing master for {t['id']} {t['title']}")
        missing += 1
        continue
    name = os.path.basename(t["src"])
    for dest in DESTS:
        os.makedirs(os.path.join(ROOT, dest), exist_ok=True)
        shutil.copyfile(hits[0], os.path.join(ROOT, dest, name))
    print(f"{t['id']} {t['title']}: {os.path.relpath(hits[0], ROOT)} -> {name}")
sys.exit(1 if missing else 0)
