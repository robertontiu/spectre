"""Copy each session's mastered MP3 to where the website expects it.

site/data/tracks.json is the canonical track list (newest first). For every track
there, the first sessions/<id>-*/*-mastered.mp3 is copied to site/public/tracks/
under the file name the track's "src" expects. The MP3 copies
are gitignored; the session folders hold the originals.

    python3 tools/sync_tracks.py

(The Next.js site also copies its MP3s itself before every dev run and build:
site/scripts/sync-tracks.mjs.)
"""
import glob, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL = os.path.join(ROOT, "site", "data", "tracks.json")
DESTS = ("site/public/tracks",)

tracks = json.load(open(CANONICAL, encoding="utf-8"))
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
