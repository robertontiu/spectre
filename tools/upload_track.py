"""Publish a Spectre track: its session files go to an S3-compatible bucket under the track's uuid.

Work happens locally in sessions/<id>-<name>/; publishing a track (or a new version of
it) is the one step that sends everything new to the bucket configured in the
environment. The repo keeps only cross-track files; site/data/tracks.json is the
showcase list and carries each track's uuid.

Without a bucket (none of the SPECTRE_S3_* variables set: a fork or a fresh clone),
publishing uploads nothing and does not fail: it still runs every local check (uuid,
the publish set, the required files, the MP3), then lists the files to send to the user
in the chat instead, and exits 0. --all, --cors, --check and --fetch need the bucket;
without one they say so and are skipped (exit 0).

    python3 tools/upload_track.py 016        # publish: uuid if new, upload what changed, verify

Publishing a track (by session id, slug or uuid from tracks.json):
  1. gives it a uuid (v4) in site/data/tracks.json if it has none (made once, never
     changed; commit tracks.json in the normal delivery step);
  2. uploads every new or changed publishable file of its session to <uuid>/... (MD5
     compared with the bucket; unchanged files are skipped);
  3. verifies each upload (Content-MD5 on the way in, then size and ETag).

Bucket layout, the same names for every track (defined once here; the site's audio
route uses RENDITION too: site/src/lib/s3.ts, TRACK_OBJECTS):

    <uuid>/rendition.mp3            the published master (<title>-mastered.mp3)
    <uuid>/journal.md               journal.md
    <uuid>/readme.md                README.md
    <uuid>/prompt.md                PROMPT.md
    <uuid>/project.json             project.json
    <uuid>/master-report.json       master-report.json
    <uuid>/master-tonal-balance.png master-tonal-balance.png
    <uuid>/ear-overview.png         ear-overview.png
    <uuid>/tools/<path>             build and helper scripts, path in the folder kept

What is publishable (only what belongs in the showcase, as the repo used to hold it):
the files git tracks in the session folder (the sessions from before the move), plus
the named files above and the helper scripts (*.py, *.sh) anywhere in the folder.
Never renders/, WAVs, __pycache__, listen dumps or other scratch (they stay local and
are cleaned up). A session needs exactly one *-mastered.mp3, journal.md, README.md and
project.json. Tracks are named by id, slug or uuid, never by file path. Every object
is private and carries its MD5 and its path in the session folder, so --fetch restores
the folder exactly.

Configuration comes only from environment variables (never commit their values):

    SPECTRE_S3_ENDPOINT           e.g. https://s3.<region>.example.com
    SPECTRE_S3_REGION             e.g. <region>
    SPECTRE_S3_BUCKET             e.g. <your-bucket>
    SPECTRE_S3_ACCESS_KEY_ID      the workspace's read-write key (the site gets a read-only one)
    SPECTRE_S3_SECRET_ACCESS_KEY
    SPECTRE_S3_CORS_ORIGINS       optional, comma-separated, replaces the default CORS origins

Usage:

    python3 tools/upload_track.py 015 016         # publish these tracks
    python3 tools/upload_track.py --all           # publish every track in tracks.json
    python3 tools/upload_track.py --cors          # the bucket's CORS rules for the player
    python3 tools/upload_track.py --check         # the bucket against tracks.json and sessions/
    python3 tools/upload_track.py --fetch 007     # restore sessions/007-ecstasy/ from the bucket
    python3 tools/upload_track.py --all --dry-run # what would be uploaded (no uuid is written)

The whole migration is `python3 tools/upload_track.py --cors --all --check`.
"""
import argparse, base64, glob, hashlib, json, mimetypes, os, re, subprocess, sys, uuid
from urllib.parse import quote, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS = os.path.join(ROOT, "sessions")
CANONICAL = os.path.join(ROOT, "site", "data", "tracks.json")

# The bucket layout, defined once (documented in docs/agents/track-storage.md).
RENDITION = "rendition.mp3"
NAMED = {  # session file -> object name under <uuid>/
    "journal.md": "journal.md",
    "README.md": "readme.md",
    "PROMPT.md": "prompt.md",
    "project.json": "project.json",
    "master-report.json": "master-report.json",
    "master-tonal-balance.png": "master-tonal-balance.png",
    "ear-overview.png": "ear-overview.png",
}
TOOLS = "tools/"
REQUIRED = (RENDITION, "journal.md", "readme.md", "project.json")
HELPERS = (".py", ".sh")
NEVER = re.compile(r"(^|/)(renders|__pycache__)/|\.wav$", re.I)

# Objects are only ever reached through presigned URLs, which change with every signing
# window, so a replaced master is fetched fresh under its next URL; within one URL the
# bytes never change, so browsers may keep them as long as they like.
RENDITION_CACHE = "public, max-age=31536000, immutable"
OTHER_CACHE = "no-cache"
TYPES = {
    ".mp3": "audio/mpeg",
    ".md": "text/markdown; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
    ".py": "text/x-python; charset=utf-8",
    ".sh": "text/x-shellscript; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}
DEFAULT_CORS_ORIGINS = (
    "https://spectre.robertontiu.com",
    "https://spectre-*.vercel.app",  # Vercel preview deployments of the "spectre" project
    "http://localhost:3000",  # next dev / next start
)
# What the player's <audio> needs to read across origins: ranges for seeking and the
# length for the duration; Range itself is sent by the browser without a preflight.
CORS_RULE = {
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["Range"],
    "ExposeHeaders": ["Accept-Ranges", "Content-Range", "Content-Length"],
    "MaxAgeSeconds": 86400,
}
UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


class Refused(Exception):
    pass


# ---- configuration -------------------------------------------------------------------


def env(name, default=None, required=True):
    value = os.environ.get(name, "").strip() or default
    if required and not value:
        raise Refused(f"{name} is not set (see docs/agents/track-storage.md)")
    return value


S3_VARS = ("SPECTRE_S3_ENDPOINT", "SPECTRE_S3_REGION", "SPECTRE_S3_BUCKET",
           "SPECTRE_S3_ACCESS_KEY_ID", "SPECTRE_S3_SECRET_ACCESS_KEY")


def bucket_configured():
    """False when none of the S3 variables is set (no bucket: local delivery); refuses a partial set."""
    have = [v for v in S3_VARS if os.environ.get(v, "").strip()]
    if not have:
        return False
    missing = [v for v in S3_VARS if v not in have]
    if missing:
        raise Refused(f"the bucket is partly configured: {', '.join(missing)} not set (set all five, or none)")
    return True


def deliver_locally(t):
    """No bucket: the files that would be published, to send to the user in the chat."""
    folder, files = publishable(t)
    order = [RENDITION] + sorted(n for n in files if n != RENDITION)
    print(f"  {t['id']} {t['title']} (uuid {t.get('uuid', 'assigned on a real run')}): {os.path.relpath(folder, ROOT)}/")
    for n in order:
        path, rel = files[n]
        note = "  (the master)" if n == RENDITION else ""
        print(f"    {os.path.abspath(path)}{note}")


def config():
    return {
        "endpoint": env("SPECTRE_S3_ENDPOINT").rstrip("/"),
        "region": env("SPECTRE_S3_REGION"),
        "bucket": env("SPECTRE_S3_BUCKET"),
        "key_id": env("SPECTRE_S3_ACCESS_KEY_ID"),
        "secret": env("SPECTRE_S3_SECRET_ACCESS_KEY"),
    }


def client(cfg):
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=cfg["endpoint"],
        region_name=cfg["region"],
        aws_access_key_id=cfg["key_id"],
        aws_secret_access_key=cfg["secret"],
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            # Recent boto3 adds CRC checksums and aws-chunked bodies by default, which
            # S3-compatible stores do not all accept; Content-MD5 does the same job.
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            retries={"max_attempts": 5, "mode": "standard"},
        ),
    )


# ---- tracks.json -------------------------------------------------------------------


def load_tracks():
    tracks = json.load(open(CANONICAL, encoding="utf-8"))
    for t in tracks:
        f = t.get("file", "")
        if not f.endswith(".mp3") or "/" in f or f.startswith("."):
            raise Refused(f"tracks.json: track {t.get('id')} has no valid 'file' ({f!r})")
        if "uuid" in t and not UUID4.match(t["uuid"]):
            raise Refused(f"tracks.json: track {t.get('id')} has an invalid 'uuid' (a UUID v4, lower case)")
    ids = [t["uuid"] for t in tracks if "uuid" in t]
    if len(set(ids)) != len(ids):
        raise Refused("tracks.json: two tracks share a uuid")
    return tracks


def slug(t):
    return t["file"][: -len(".mp3")]


def find_track(tracks, name):
    hits = [t for t in tracks if name in (t["id"], slug(t), t["file"], t.get("uuid"))]
    if len(hits) != 1:
        raise Refused(
            f"{name!r} is not a track in site/data/tracks.json "
            "(add the track's entry first, then name it by session id, slug or uuid)"
        )
    return hits[0]


def need_uuid(t):
    if "uuid" not in t:
        raise Refused(f"{t['id']} {t['title']} has no uuid yet: publish it first (upload_track.py {t['id']})")
    return t["uuid"]


def assign_uuids(tracks, chosen):
    """Gives the chosen tracks without a uuid a new one, written into tracks.json in place
    (one line per track, the new field right after "id"; temp file plus rename)."""
    new = [t for t in chosen if "uuid" not in t]
    if not new:
        return
    text = open(CANONICAL, encoding="utf-8").read()
    taken = {t["uuid"] for t in tracks if "uuid" in t}
    for t in new:
        u = str(uuid.uuid4())
        while u in taken:
            u = str(uuid.uuid4())
        pattern = re.compile(r'(\{\s*"id"\s*:\s*"%s"\s*,)' % re.escape(t["id"]))
        if len(pattern.findall(text)) != 1:
            raise Refused(f"tracks.json: cannot place a uuid for {t['id']} (expected one line starting with its id)")
        text = pattern.sub(lambda m: f'{m.group(1)}"uuid":"{u}",', text)
        t["uuid"] = u
        taken.add(u)
        print(f"  {t['id']} {t['title']}: new uuid {u} (written to site/data/tracks.json; commit it)")
    by_id = {x["id"]: x.get("uuid") for x in json.loads(text)}
    if any(by_id.get(t["id"]) != t["uuid"] for t in new):
        raise Refused("tracks.json: the uuid did not land where expected; nothing written")
    tmp = CANONICAL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, CANONICAL)


# ---- session folders ---------------------------------------------------------------


def session_dir(t):
    dirs = sorted(d for d in glob.glob(os.path.join(SESSIONS, f"{t['id']}-*")) if os.path.isdir(d))
    if len(dirs) != 1:
        raise Refused(f"{t['id']} {t['title']}: expected one sessions/{t['id']}-*/ folder, found {len(dirs)}")
    return dirs[0]


def git_tracked(folder):
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "ls-files", "-z", "--", os.path.relpath(folder, ROOT)],
            capture_output=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [os.path.relpath(os.path.join(ROOT, p), folder).replace(os.sep, "/") for p in out.decode().split("\0") if p]


def object_name(rel):
    """The object name under <uuid>/ for a file in the session folder."""
    if "/" not in rel and rel.endswith("-mastered.mp3"):
        return RENDITION
    return NAMED.get(rel, TOOLS + rel)


def publishable(t):
    """(folder, {object name: (absolute path, path in the session folder)})."""
    folder = session_dir(t)
    rels = set(git_tracked(folder))
    for base, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ("renders", "__pycache__") and not d.startswith(".")]
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), folder).replace(os.sep, "/")
            if rel in NAMED or ("/" not in rel and rel.endswith("-mastered.mp3")) or rel.endswith(HELPERS):
                rels.add(rel)
    files = {}
    for rel in sorted(rels):
        if NEVER.search(rel):
            raise Refused(f"{t['id']}: {rel} is a render or cache file and is never uploaded")
        path = os.path.join(folder, rel)
        real = os.path.realpath(path)
        if os.path.commonpath([real, os.path.realpath(folder)]) != os.path.realpath(folder) or not os.path.isfile(real):
            raise Refused(f"{t['id']}: {rel} is missing or not a file inside the session folder")
        name = object_name(rel)
        if name in files:
            raise Refused(f"{t['id']}: {rel} and {files[name][1]} would both be {name} (one *-mastered.mp3 per session)")
        files[name] = (path, rel)
    missing = [n for n in REQUIRED if n not in files]
    if missing:
        raise Refused(f"{t['id']}: the session has no {', '.join(missing)} (see the delivery checklist)")
    with open(files[RENDITION][0], "rb") as fh:
        magic = fh.read(3)
    if not (magic == b"ID3" or (len(magic) >= 2 and magic[0] == 0xFF and magic[1] & 0xE0 == 0xE0)):
        raise Refused(f"{t['id']}: {files[RENDITION][1]} is not an MP3")
    return folder, files


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h


# ---- bucket --------------------------------------------------------------------------


def head(s3, cfg, key):
    from botocore.exceptions import ClientError

    try:
        return s3.head_object(Bucket=cfg["bucket"], Key=key)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def remote_md5(h):
    """The MD5 an object was uploaded with: our metadata, else a single-part ETag."""
    if not h:
        return None
    meta = (h.get("Metadata") or {}).get("md5")
    if meta:
        return meta
    etag = h.get("ETag", "").strip('"')
    return etag if len(etag) == 32 and "-" not in etag else None


def listing(s3, cfg, prefix=""):
    keys = {}
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=cfg["bucket"], Prefix=prefix):
        for o in page.get("Contents", []):
            keys[o["Key"]] = o
    return keys


def put(s3, cfg, t, folder, path, rel, name, dry_run):
    key = f"{t['uuid']}/{name}"
    ext = os.path.splitext(path)[1].lower()
    content_type = TYPES.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"
    cache = RENDITION_CACHE if name == RENDITION else OTHER_CACHE
    digest = md5_of(path)
    local = digest.hexdigest()
    size = os.path.getsize(path)
    meta = {"md5": local, "session": t["id"], "folder": quote(os.path.basename(folder)), "path": quote(rel)}
    h = head(s3, cfg, key)
    if (
        h
        and remote_md5(h) == local
        and h.get("ContentLength") == size
        and h.get("ContentType") == content_type
        and h.get("CacheControl") == cache
        and (h.get("Metadata") or {}).get("path") == meta["path"]
    ):
        return "unchanged"
    verb = "replaced" if h else "uploaded"
    if dry_run:
        print(f"    would be {verb}: {rel} -> {key} ({size / 1e6:.2f} MB)")
        return f"to be {verb}"
    with open(path, "rb") as body:
        s3.put_object(
            Bucket=cfg["bucket"],
            Key=key,
            Body=body,
            ContentLength=size,
            ContentType=content_type,
            CacheControl=cache,
            ContentMD5=base64.b64encode(digest.digest()).decode(),
            ACL="private",
            Metadata=meta,
        )
    h = head(s3, cfg, key)
    etag = (h or {}).get("ETag", "").strip('"')
    if not h or h.get("ContentLength") != size or (len(etag) == 32 and etag != local) or remote_md5(h) != local:
        raise Refused(f"{key}: verification failed after upload (size or MD5 differs)")
    print(f"    {verb} {rel} -> {key} ({size / 1e6:.2f} MB, MD5 verified)")
    return verb


def publish(s3, cfg, t, dry_run=False):
    folder, files = publishable(t)
    u = t.get("uuid", "<new uuid>")
    print(f"  {t['id']} {t['title']}: {os.path.relpath(folder, ROOT)}/ -> {u}/ ({len(files)} files)")
    if "uuid" not in t:  # dry run of a new track: everything would be uploaded
        for name, (_, rel) in files.items():
            print(f"    would be uploaded: {rel} -> {u}/{name}")
        return
    counts = {}
    for name, (path, rel) in files.items():
        r = put(s3, cfg, t, folder, path, rel, name, dry_run)
        counts[r] = counts.get(r, 0) + 1
    print("    " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())))


def fetch(s3, cfg, t, force=False, dry_run=False):
    """Restores sessions/<folder>/ from <uuid>/, every file under its original path."""
    u = need_uuid(t)
    keys = listing(s3, cfg, f"{u}/")
    if f"{u}/{RENDITION}" not in keys:
        raise Refused(f"{t['id']}: nothing under {u}/ in the bucket")
    reverse = {v: k for k, v in NAMED.items()}
    short = slug(t)[len(t["id"]) + 1 :]
    restored = same = 0
    for key in sorted(keys):
        name = key[len(u) + 1 :]
        meta = (head(s3, cfg, key) or {}).get("Metadata") or {}
        folder = unquote(meta.get("folder", "")) or f"{t['id']}-{short}"
        if name == RENDITION:
            fallback = f"{short}-mastered.mp3"
        else:
            fallback = reverse.get(name) or (name[len(TOOLS) :] if name.startswith(TOOLS) else name)
        rel = unquote(meta.get("path", "")) or fallback
        base = os.path.realpath(os.path.join(SESSIONS, folder))
        dest = os.path.realpath(os.path.join(base, rel))
        if os.path.dirname(base) != os.path.realpath(SESSIONS) or os.path.commonpath([dest, base]) != base:
            raise Refused(f"{key}: unsafe path {folder}/{rel}")
        want = meta.get("md5") or remote_md5({"ETag": keys[key].get("ETag", "")})
        if os.path.isfile(dest):
            if md5_of(dest).hexdigest() == want:
                same += 1
                continue
            if not force:
                raise Refused(f"{os.path.relpath(dest, ROOT)} exists and differs from {key} (--force replaces it)")
        print(f"    {key} -> {os.path.relpath(dest, ROOT)}")
        if dry_run:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        tmp = dest + ".part"
        s3.download_file(cfg["bucket"], key, tmp)
        if want and md5_of(tmp).hexdigest() != want:
            os.remove(tmp)
            raise Refused(f"{key}: download does not match its MD5")
        os.replace(tmp, dest)
        restored += 1
    print(f"  {t['id']} {t['title']}: {restored} restored, {same} already there")


def set_cors(s3, cfg, dry_run=False):
    raw = env("SPECTRE_S3_CORS_ORIGINS", required=False)
    origins = [o.strip() for o in raw.split(",") if o.strip()] if raw else list(DEFAULT_CORS_ORIGINS)
    rule = {**CORS_RULE, "AllowedOrigins": origins}
    print(f"  CORS on {cfg['bucket']}: {', '.join(rule['AllowedMethods'])} from {', '.join(origins)}")
    if dry_run:
        return
    s3.put_bucket_cors(Bucket=cfg["bucket"], CORSConfiguration={"CORSRules": [rule]})
    got = s3.get_bucket_cors(Bucket=cfg["bucket"]).get("CORSRules", [])
    if not any(sorted(r.get("AllowedOrigins", [])) == sorted(origins) for r in got):
        raise Refused("CORS: the bucket did not keep the rule")
    print("    verified")


def check(s3, cfg, tracks):
    present = listing(s3, cfg)
    problems = 0
    for t in tracks:
        if "uuid" not in t:
            print(f"  PROBLEM  {t['id']} has no uuid (not published)")
            problems += 1
            continue
        u = t["uuid"]
        names = {k[len(u) + 1 :] for k in present if k.startswith(u + "/")}
        if not names:
            print(f"  MISSING  {t['id']} {u} (nothing in the bucket: publish it)")
            problems += 1
            continue
        notes = [f"no {n}" for n in REQUIRED if n not in names]
        try:
            _, files = publishable(t)
        except Refused:
            files = {}  # the session is not in this checkout: only the required names are checked
        for name, (path, rel) in files.items():
            if name not in names:
                notes.append(f"not uploaded: {rel}")
            elif remote_md5(head(s3, cfg, f"{u}/{name}")) != md5_of(path).hexdigest():
                notes.append(f"changed since upload: {rel}")
        extra = sorted(names - set(files)) if files else []
        problems += bool(notes)
        size = present.get(f"{u}/{RENDITION}", {}).get("Size", 0)
        local = f", {len(files)} publishable local files" if files else ", no local session"
        more = f", {len(extra)} objects no longer in the local session" if extra else ""
        print(f"  {'PROBLEM ' if notes else 'ok      '} {t['id']} {u} ({len(names)} objects, rendition {size / 1e6:.1f} MB{local}{more})")
        for n in notes:
            print(f"             {n}")
    known = {t["uuid"] for t in tracks if "uuid" in t}
    stray = sorted({k.split("/", 1)[0] for k in present} - known)
    for p in stray:
        print(f"  EXTRA    {p} (not a uuid in tracks.json)")
    print(f"  {len(tracks)} tracks, {problems} with problems, {len(stray)} stray prefixes")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracks", nargs="*", help="tracks to publish: session ids, slugs or uuids from tracks.json")
    ap.add_argument("--all", action="store_true", help="publish every track in site/data/tracks.json")
    ap.add_argument("--cors", action="store_true", help="set the bucket's CORS rules for the player")
    ap.add_argument("--check", action="store_true", help="compare the bucket with tracks.json and sessions/")
    ap.add_argument("--fetch", metavar="TRACK", action="append", default=[], help="restore a session folder")
    ap.add_argument("--force", action="store_true", help="with --fetch: replace local files that differ")
    ap.add_argument("--dry-run", action="store_true", help="say what would happen, change nothing")
    a = ap.parse_args()
    if not (a.tracks or a.all or a.cors or a.check or a.fetch):
        ap.error("name tracks to publish, or use --all, --cors, --check or --fetch")
    try:
        tracks = load_tracks()
        if not bucket_configured():
            for flag, on in (("--all", a.all), ("--cors", a.cors), ("--check", a.check), ("--fetch", bool(a.fetch))):
                if on:
                    print(f"upload_track: {flag} needs an S3 bucket (the SPECTRE_S3_* variables, docs/agents/track-storage.md); "
                          "none is configured: skipped")
            chosen = [find_track(tracks, n) for n in a.tracks]
            for t in chosen:
                publishable(t)  # every local check, before tracks.json is touched
            if not chosen:
                return 0
            if not a.dry_run:
                assign_uuids(tracks, chosen)
            print("No S3 bucket configured: nothing uploaded. Deliver these files to the user in the chat:")
            for t in chosen:
                deliver_locally(t)
            return 0
        chosen = tracks if a.all else [find_track(tracks, n) for n in a.tracks]
        fetching = [find_track(tracks, n) for n in a.fetch]
        for t in chosen:
            publishable(t)  # refuse before touching tracks.json or the bucket
        cfg = config()
        s3 = client(cfg)
        if a.cors:
            set_cors(s3, cfg, a.dry_run)
        if not a.dry_run:
            assign_uuids(tracks, chosen)
        for t in chosen:
            publish(s3, cfg, t, a.dry_run)
        for t in fetching:
            fetch(s3, cfg, t, a.force, a.dry_run)
        if a.check and check(s3, cfg, tracks):
            return 1
    except Refused as e:
        print(f"upload_track: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
