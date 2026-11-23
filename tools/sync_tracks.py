"""Copy each session's mastered MP3 into site/tracks/ and player/tracks/ under the
filenames that site/tracks/tracks.json expects. The MP3 copies are gitignored; the
session folders hold the originals.

    python3 tools/sync_tracks.py

A track's id (e.g. "005") selects sessions/005-*/; the first *-mastered.mp3 there is used.
"""
import glob, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tracks = json.load(open(os.path.join(ROOT, "site", "tracks", "tracks.json")))
missing = 0
for t in tracks:
    hits = sorted(glob.glob(os.path.join(ROOT, "sessions", f"{t['id']}-*", "*-mastered.mp3")))
    if not hits:
        print(f"missing master for {t['id']} {t['title']}")
        missing += 1
        continue
    name = os.path.basename(t["src"])
    for dest in ("site/tracks", "player/tracks"):
        os.makedirs(os.path.join(ROOT, dest), exist_ok=True)
        shutil.copyfile(hits[0], os.path.join(ROOT, dest, name))
    print(f"{t['id']} {t['title']}: {os.path.relpath(hits[0], ROOT)} -> {name}")
sys.exit(1 if missing else 0)
