#!/usr/bin/env python3
"""Back up session folders that are still in progress, so a container restart can't lose unpublished work.

sessions/ is a local working area and out of git (published sessions live in the showcase bucket,
docs/agents/track-storage.md). A session being produced exists only on this machine until it is
published, and a cloud container is reclaimed after a period of inactivity. This tool copies
session folders to the PRIVATE mirror bucket (SPECTRE_MIRROR_BUCKET, the one that holds the engine
assets) under sessions-wip/<folder>/. The site never reads that bucket, so a backup is never a
release (standing rule 21 is untouched).

What is copied: every file in the folder except WAVs (every render is reproducible from its
renders/vNNN.project.json: rendering is seeded and deterministic), __pycache__ and *.part files.
Unchanged files are skipped (MD5 compared). Nothing is ever deleted in the bucket.

    python3 tools/backup_sessions.py push                 # every folder in sessions/
    python3 tools/backup_sessions.py push 016-captive     # one or more folders (name or NNN)
    python3 tools/backup_sessions.py list                 # what the bucket holds
    python3 tools/backup_sessions.py pull 016-captive     # restore into sessions/ (never overwrites a
                                                          # differing local file without --force;
                                                          # --to <dir> restores elsewhere)

Settings come only from the environment (SPECTRE_MIRROR_BUCKET plus SPECTRE_S3_ENDPOINT, _REGION,
_ACCESS_KEY_ID, _SECRET_ACCESS_KEY); without them it says so and exits 0. The orchestrator runs
`push` at every check-in on a running session (docs/ORCHESTRATION.md, "Keeping sessions alive").
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upload_track import client, head, md5_of, remote_md5  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS = os.path.join(ROOT, "sessions")
PREFIX = "sessions-wip/"
VARS = ("SPECTRE_MIRROR_BUCKET", "SPECTRE_S3_ENDPOINT", "SPECTRE_S3_REGION",
        "SPECTRE_S3_ACCESS_KEY_ID", "SPECTRE_S3_SECRET_ACCESS_KEY")


def config():
    missing = [v for v in VARS if not os.environ.get(v, "").strip()]
    if missing:
        return None, missing
    e = lambda v: os.environ[v].strip()  # noqa: E731
    return {"endpoint": e("SPECTRE_S3_ENDPOINT").rstrip("/"), "region": e("SPECTRE_S3_REGION"),
            "bucket": e("SPECTRE_MIRROR_BUCKET"), "key_id": e("SPECTRE_S3_ACCESS_KEY_ID"),
            "secret": e("SPECTRE_S3_SECRET_ACCESS_KEY")}, []


def folders(names):
    have = sorted(d for d in os.listdir(SESSIONS) if os.path.isdir(os.path.join(SESSIONS, d))) \
        if os.path.isdir(SESSIONS) else []
    if not names:
        return have
    out = []
    for n in names:
        hit = [d for d in have if d == n or d.split("-", 1)[0] == n]
        if len(hit) != 1:
            sys.exit(f"backup_sessions: {n!r} matches {hit or 'no folder'} in sessions/")
        out += hit
    return out


def skip(rel):
    parts = rel.split("/")
    return rel.lower().endswith((".wav", ".part", ".pyc")) or "__pycache__" in parts


def push(s3, cfg, names):
    for d in folders(names):
        base = os.path.join(SESSIONS, d)
        sent = same = 0
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for f in files:
                path = os.path.join(dirpath, f)
                rel = os.path.relpath(path, base).replace(os.sep, "/")
                if skip(rel) or not os.path.isfile(path):
                    continue
                key = f"{PREFIX}{d}/{rel}"
                md5 = md5_of(path).hexdigest()
                if remote_md5(head(s3, cfg, key)) == md5:
                    same += 1
                    continue
                with open(path, "rb") as fh:
                    s3.put_object(Bucket=cfg["bucket"], Key=key, Body=fh, Metadata={"md5": md5})
                sent += 1
        print(f"  {d}: {sent} sent, {same} unchanged")


def listing(s3, cfg, prefix=PREFIX):
    keys, token = {}, None
    while True:
        kw = {"Bucket": cfg["bucket"], "Prefix": prefix}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            keys[o["Key"]] = o
        if not r.get("IsTruncated"):
            return keys
        token = r["NextContinuationToken"]


def cmd_list(s3, cfg):
    by = {}
    for k, o in listing(s3, cfg).items():
        d = k[len(PREFIX):].split("/", 1)[0]
        n, size, last = by.get(d, (0, 0, None))
        by[d] = (n + 1, size + o["Size"], max(last, o["LastModified"]) if last else o["LastModified"])
    for d, (n, size, last) in sorted(by.items()):
        print(f"  {d}: {n} files, {size / 1e6:.1f} MB, last backup {last:%Y-%m-%d %H:%M} UTC")
    if not by:
        print("  (no session backups)")


def pull(s3, cfg, names, force, dest=SESSIONS):
    for n in names:
        keys = {k: o for k, o in listing(s3, cfg).items()
                if k[len(PREFIX):].split("/", 1)[0] in (n,) or k[len(PREFIX):].split("-", 1)[0] == n}
        if not keys:
            sys.exit(f"backup_sessions: no backup for {n!r}")
        got = kept = 0
        for k in sorted(keys):
            rel = k[len(PREFIX):]
            dst = os.path.join(dest, *rel.split("/"))
            if not os.path.realpath(dst).startswith(os.path.realpath(dest) + os.sep):
                sys.exit(f"backup_sessions: unsafe key {k}")
            if os.path.exists(dst):
                if remote_md5(head(s3, cfg, k)) == md5_of(dst).hexdigest():
                    continue
                if not force:
                    print(f"  kept local {rel} (differs from the backup; --force replaces it)")
                    kept += 1
                    continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            s3.download_file(cfg["bucket"], k, dst + ".part")
            os.replace(dst + ".part", dst)
            got += 1
        print(f"  {n}: {got} restored, {kept} kept local")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("push", "pull", "list"))
    ap.add_argument("folders", nargs="*", help="session folder names or numbers (push: default all)")
    ap.add_argument("--force", action="store_true", help="pull: replace local files that differ")
    ap.add_argument("--to", default=SESSIONS, help="pull: restore into this folder instead of sessions/")
    a = ap.parse_args()
    cfg, missing = config()
    if not cfg:
        print(f"backup_sessions: no private bucket configured ({', '.join(missing)} not set): skipped")
        return 0
    s3 = client(cfg)
    if a.action == "push":
        push(s3, cfg, a.folders)
    elif a.action == "list":
        cmd_list(s3, cfg)
    else:
        if not a.folders:
            ap.error("pull needs a session folder")
        pull(s3, cfg, a.folders, a.force, os.path.abspath(a.to))
    return 0


if __name__ == "__main__":
    sys.exit(main())
