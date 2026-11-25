#!/usr/bin/env python3
"""Third-party resources of the engine and its measurement tools, from engine/third_party.json.

Nothing third-party is in the repo or bundled anywhere: every user downloads each resource from
its official source and accepts its licence. The manifest lists each one: what needs it, required
or optional, licence, official page, direct link (or manual steps), size, sha256, where it goes,
and a search hint for when the link fails.

    python3 tools/engine_assets.py status [ids]           # installed or missing, and where to get the rest
    python3 tools/engine_assets.py status --verify [ids]  # also check every file's sha256 (slow on big files)
    python3 tools/engine_assets.py install [ids]          # download what has a direct link, verify, unpack
                                                          # (no ids: every entry except those marked "auto": false)
    python3 tools/engine_assets.py install --required     # only the required entries
    python3 tools/engine_assets.py import <file.zip>      # install a zip you downloaded yourself
    python3 tools/engine_assets.py pull                   # optional mirror: fetch what is still missing
    python3 tools/engine_assets.py push [--dry-run]       # optional mirror: upload the official files

`status` exits 1 while a required resource is missing. When a link fails: search for the official
source (the entry's search_hint), check that the licence and the files match (size, sha256, the
folder layout), install it (`import` for a zip), and update the entry's link in the manifest.

The optional private mirror (`push` / `pull`) is a fail-safe after the official sources. It is
configured only through environment variables: SPECTRE_MIRROR_BUCKET plus SPECTRE_S3_ENDPOINT,
SPECTRE_S3_REGION, SPECTRE_S3_ACCESS_KEY_ID and SPECTRE_S3_SECRET_ACCESS_KEY. Without them it is
skipped. It holds the official files exactly as downloaded (object names in the manifest's
"mirror" section) and is never part of a distributed package.

Locations: $SPECTRE_CACHE (default ~/.cache/spectre) and, for the Whisper models, $HF_HOME
(default ~/.cache/spectre/svs/hf, which the Whisper scripts set themselves).
Standard library only (boto3 for the mirror).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, "engine", "third_party.json")
ROOTS = {
    "cache": os.path.expanduser(os.environ.get("SPECTRE_CACHE", "~/.cache/spectre")),
    "hf": os.path.expanduser(os.environ.get("HF_HOME", "~/.cache/spectre/svs/hf")),
}
UA = "spectre-setup/1.0 (python urllib)"


def load():
    return json.load(open(MANIFEST, encoding="utf-8"))


def pick(m, ids):
    res = m["resources"]
    if not ids:
        return res
    known = {r["id"]: r for r in res}
    bad = [i for i in ids if i not in known]
    if bad:
        sys.exit(f"unknown id(s): {', '.join(bad)} (known: {', '.join(known)})")
    return [known[i] for i in ids]


def where(r, rel=None):
    return os.path.join(ROOTS[r["root"]], rel if rel is not None else r["path"])


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hf_snapshot(r):
    return os.path.join(where(r), "snapshots", r["revision"])


def file_ok(path, spec, verify):
    if not os.path.isfile(path) or os.path.getsize(path) != spec["size"]:
        return False
    return not verify or sha256(path) == spec["sha256"]


def state(r, verify=False):
    """'ok', 'missing', 'partial' or 'on demand'."""
    k = r["kind"]
    if k in ("tool", "api"):
        return "on demand"
    if k == "zip":
        d = where(r)
        return "ok" if os.path.isdir(d) and os.listdir(d) else "missing"
    if k == "hf_model":
        snaps = os.path.join(where(r), "snapshots")
        names = [f["name"] for f in r["files"]]
        for s in sorted(os.listdir(snaps)) if os.path.isdir(snaps) else []:
            if all(os.path.isfile(os.path.join(snaps, s, n)) for n in names):
                if not verify or s != r["revision"]:
                    return "ok"
                return "ok" if all(file_ok(os.path.join(snaps, s, f["name"]), f, True) for f in r["files"]) else "partial"
        return "missing"
    have = [file_ok(where(r, f["path"]), f, verify) for f in r["files"]]
    return "ok" if all(have) else "partial" if any(have) else "missing"


def source(r):
    if r["kind"] == "tool":
        return f"fetched on demand by `{r['command']}`"
    if r["kind"] == "api":
        return "queried from the APIs on demand: " + ", ".join(r["endpoints"])
    if r["kind"] == "hf_model":
        return f"Hugging Face {r['repo']}@{r['revision'][:7]}"
    if r.get("url"):
        return r["url"]
    if r["kind"] == "files" and all(f.get("url") for f in r["files"]):
        return f"{len(r['files'])} direct links ({r['page']})"
    return f"no direct link recorded yet; official source: {r['page']}"


def status(ids, verify):
    m = load()
    print(f"cache {ROOTS['cache']}   hf {ROOTS['hf']}")
    ff = shutil.which("ffmpeg")
    print(f"{'ok     ' if ff else 'MISSING'} {'ffmpeg':22} required  {ff or 'apt-get install -y ffmpeg (or brew install ffmpeg)'}")
    py = sys.version_info >= (3, 11)
    print(f"{'ok     ' if py else 'MISSING'} {'python 3.11+':22} required  {sys.version.split()[0]}")
    missing = [] if ff and py else ["system"]
    for r in pick(m, ids):
        s = state(r, verify)
        req = "required" if r["required"] else "optional"
        flag = {"ok": "ok     ", "on demand": "demand "}.get(s, "MISSING" if r["required"] else "missing")
        print(f"{flag} {r['id']:22} {req:9} {r['path'] if s == 'ok' else source(r)}")
        if s in ("missing", "partial") and r["required"]:
            missing.append(r["id"])
    if missing:
        print(f"\nrequired and missing: {', '.join(missing)}. Run `python3 tools/engine_assets.py install`; if a link "
              "fails, find the official source (search_hint in engine/third_party.json), verify it, install it and "
              "update the manifest; the optional mirror (`pull`) is the last resort.")
        return 1
    return 0


# ---- downloads -----------------------------------------------------------------------


class Transient(IOError):
    """The server was busy or unreachable (429, 5xx, timeout): the link is not known to be broken."""


class DeadLink(IOError):
    """The server answered that the file is not there (404, 410, 403): the link needs replacing."""


def _open(url, tries=5):
    """urlopen with retries for transient errors (429 / 5xx / timeouts, honouring Retry-After)."""
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120)
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 403, 401):
                raise DeadLink(f"HTTP {e.code} {e.reason}") from e
            if e.code != 429 and e.code < 500:
                raise
            why = f"HTTP {e.code} {e.reason}"
            ra = e.headers.get("Retry-After", "") if e.headers else ""
            wait = min(float(ra), 120.0) if ra.isdigit() else 10.0 * 2 ** k
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            why, wait = str(getattr(e, "reason", e)), 10.0 * 2 ** k
        if k == tries - 1:
            raise Transient(f"{why} after {tries} tries")
        print(f"      {why}: retrying in {wait:.0f} s")
        time.sleep(wait)


def fetch(url, dst, size=None, digest=None):
    """Download url to dst (via a .part file), then check size and sha256; raises on mismatch."""
    print(f"get   {url}")
    tmp = dst + ".part"
    with _open(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    got = os.path.getsize(tmp)
    if size is not None and got != size:
        os.remove(tmp)
        raise IOError(f"size {got} != {size} expected")
    if digest and sha256(tmp) != digest:
        os.remove(tmp)
        raise IOError("sha256 differs from the manifest")
    os.replace(tmp, dst)


def mediafire(page):
    """The direct link behind a MediaFire file page (it changes; the page is the stable link)."""
    with _open(page) as r:
        html = r.read().decode("utf-8", "replace")
    hits = re.findall(r'https://download\d*\.mediafire\.com/[^"\'\s<>]+', html)
    if not hits:
        raise IOError("no download link on the MediaFire page")
    return hits[0]


def unpack_zip(path, r):
    """The zip's top folder whose name starts with unpack.top becomes the entry's folder; loose files
    at the zip's root (shortcuts) are skipped."""
    dst = where(r, r["unpack"]["to"])
    if os.path.isdir(dst) and os.listdir(dst):
        print(f"have  {r['id']} ({dst}); remove it first to replace it")
        return
    with zipfile.ZipFile(path) as z:
        tops = sorted({n.split("/", 1)[0] for n in z.namelist() if "/" in n.strip("/")})
        hit = [t for t in tops if t.startswith(r["unpack"]["top"])]
        if len(hit) != 1:
            raise IOError(f"{path}: expected one top folder starting with {r['unpack']['top']!r}, found {tops[:5]}")
        top = hit[0]
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with tempfile.TemporaryDirectory(dir=os.path.dirname(dst)) as tmp:
            real = os.path.realpath(tmp)
            members = [n for n in z.namelist() if n.startswith(top + "/")]
            for n in members:
                if not os.path.realpath(os.path.join(tmp, n)).startswith(real + os.sep):
                    raise IOError(f"{path}: unsafe path {n!r}")
            z.extractall(tmp, members)
            shutil.move(os.path.join(tmp, top), dst)
    print(f"ok    {r['id']} -> {dst}")


def install_zip(r):
    url = mediafire(r["url"]) if r.get("resolve") == "mediafire" else r["url"]
    with tempfile.TemporaryDirectory(dir=ROOTS["cache"]) as tmp:
        z = os.path.join(tmp, r["file"])
        fetch(url, z, r.get("size"), r.get("sha256"))
        unpack_zip(z, r)


def install_files(r):
    todo = [f for f in r["files"] if not file_ok(where(r, f["path"]), f, False)]
    if any(not f.get("url") for f in todo):
        raise LookupError("manual")
    for f in todo:
        dst = where(r, f["path"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for k, url in enumerate([f["url"]] + f.get("urls", [])):
            try:
                fetch(url, dst, f["size"], f["sha256"])
                break
            except Exception as e:
                if k == len(f.get("urls", [])):
                    raise
                print(f"      {e}; trying the next link")
    print(f"ok    {r['id']} ({len(r['files'])} files in {where(r)})")


def install_hf(r):
    """Hugging Face cache layout (snapshots/<revision>/<file> plus refs/main), so faster-whisper finds the model."""
    snap = hf_snapshot(r)
    os.makedirs(snap, exist_ok=True)
    for f in r["files"]:
        dst = os.path.join(snap, f["name"])
        if not file_ok(dst, f, False):
            fetch(f"https://huggingface.co/{r['repo']}/resolve/{r['revision']}/{f['name']}", dst, f["size"], f["sha256"])
    os.makedirs(os.path.join(where(r), "refs"), exist_ok=True)
    with open(os.path.join(where(r), "refs", "main"), "w") as fh:
        fh.write(r["revision"])
    print(f"ok    {r['id']} -> {snap}")


def explain(r, why, what):
    """what: 'transient' (retry later), 'nolink' (find and record the link), 'dead' or 'changed' (find the source again)."""
    print(f"todo  {r['id']}: {why}")
    if what == "transient":
        print("        the link is not broken, the server was busy or unreachable: run "
              f"`engine_assets.py install {r['id']}` again later before searching for another source")
    else:
        print(f"        official source: {r.get('page', r.get('repo', '?'))}. This entry has an official source; "
              "find the file there (search_hint), check licence, size and sha256, install it and record the link "
              "in engine/third_party.json, optional entries included. The mirror is only a fallback.")
    for i, step in enumerate(r.get("manual", []), 1):
        print(f"        {i}. {step}")
    print(f"        search_hint: {r['search_hint']}")


def install(ids, required_only):
    m = load()
    os.makedirs(ROOTS["cache"], exist_ok=True)
    failed = []
    for r in pick(m, ids):
        if required_only and not r["required"]:
            continue
        if not ids and r.get("auto") is False:
            print(f"skip  {r['id']} (only on request: engine_assets.py install {r['id']})")
            continue
        if state(r) in ("ok", "on demand"):
            print(f"{'have ' if r['kind'] not in ('tool', 'api') else 'skip '} {r['id']}"
                  + (f" ({r['note']})" if r["kind"] in ("tool", "api") else ""))
            continue
        try:
            {"zip": install_zip, "files": install_files, "hf_model": install_hf}[r["kind"]](r)
        except LookupError:
            explain(r, "no direct link recorded yet", "nolink")
            failed.append(r["id"])
        except Transient as e:
            explain(r, f"download interrupted ({e})", "transient")
            failed.append(r["id"])
        except DeadLink as e:
            explain(r, f"link dead ({e})", "dead")
            failed.append(r["id"])
        except Exception as e:
            explain(r, f"download failed ({e})", "changed" if "sha256" in str(e) or "size" in str(e) else "dead")
            failed.append(r["id"])
    if failed:
        print(f"\nnot installed: {', '.join(failed)}")
        print("Every entry has an official source (its page). Report each as: installed, retried, link found and "
              "recorded, or not found after searching (say where you looked). Never as 'no official link'.")
    return 0


def import_zip(path):
    m = load()
    if not zipfile.is_zipfile(path):
        sys.exit(f"{path}: not a zip file")
    with zipfile.ZipFile(path) as z:
        tops = {n.split("/", 1)[0] for n in z.namelist() if "/" in n.strip("/")}
    hits = [r for r in m["resources"] if r["kind"] == "zip" and any(t.startswith(r["unpack"]["top"]) for t in tops)]
    if len(hits) != 1:
        sys.exit(f"{path}: not a known zip (top folders {sorted(tops)[:5]}; known: "
                 + ", ".join(r["id"] for r in m["resources"] if r["kind"] == "zip") + ")")
    r = hits[0]
    if r.get("sha256") and sha256(path) != r["sha256"]:
        print(f"note  {path} differs from the version in the manifest ({r['file']}, {r['size']} bytes): if it is a newer "
              "official release with the same licence, record its link, size and sha256 in engine/third_party.json")
    unpack_zip(path, r)


# ---- optional private mirror (environment variables only) -----------------------------

MIRROR_VARS = ("SPECTRE_MIRROR_BUCKET", "SPECTRE_S3_ENDPOINT", "SPECTRE_S3_REGION",
               "SPECTRE_S3_ACCESS_KEY_ID", "SPECTRE_S3_SECRET_ACCESS_KEY")


def mirror_client():
    missing = [v for v in MIRROR_VARS if not os.environ.get(v, "").strip()]
    if missing:
        return None, missing
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from upload_track import client

    cfg = {"endpoint": os.environ["SPECTRE_S3_ENDPOINT"].strip().rstrip("/"),
           "region": os.environ["SPECTRE_S3_REGION"].strip(),
           "bucket": os.environ["SPECTRE_MIRROR_BUCKET"].strip(),
           "key_id": os.environ["SPECTRE_S3_ACCESS_KEY_ID"].strip(),
           "secret": os.environ["SPECTRE_S3_SECRET_ACCESS_KEY"].strip()}
    return (client(cfg), cfg), []


def head(s3, cfg, key):
    try:
        return s3.head_object(Bucket=cfg["bucket"], Key=key)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def mirror_objects(m):
    res = {r["id"]: r for r in m["resources"]}
    return [(key, o, [res[i] for i in o["ids"]]) for key, o in m["mirror"]["objects"].items()]


def push(dry_run):
    m = load()
    conn, missing = mirror_client()
    if not conn:
        print(f"push: no mirror configured ({', '.join(missing)} not set)")
        return 2
    s3, cfg = conn
    for key, o, rs in mirror_objects(m):
        with tempfile.TemporaryDirectory() as tmp:
            if o["type"] == "zip":
                src = os.path.join(ROOTS["cache"], o["local"])
                if not os.path.isfile(src):
                    print(f"skip  {key}: {src} not here (keep the official zip there to mirror it)")
                    continue
            else:
                folder = os.path.join(ROOTS[o["root"]], o["folder"])
                if not os.path.isdir(folder) or not os.listdir(folder):
                    print(f"skip  {key}: {folder} not here")
                    continue
                src = os.path.join(tmp, key)
                with tarfile.open(src, "w") as t:
                    t.add(folder, arcname=o["folder"])
            digest, size = sha256(src), os.path.getsize(src)
            h = head(s3, cfg, key)
            if h and h.get("Metadata", {}).get("sha256") == digest:
                print(f"same  {key} ({size / 1e6:.0f} MB)")
                continue
            print(f"{'would put' if dry_run else 'put  '} {key} ({size / 1e6:.0f} MB)")
            if not dry_run:
                s3.upload_file(src, cfg["bucket"], key, ExtraArgs={"Metadata": {"sha256": digest}})
                h = head(s3, cfg, key)
                if not h or h["ContentLength"] != size:
                    sys.exit(f"upload of {key} did not verify")
    return 0


def pull(ids):
    m = load()
    conn, missing = mirror_client()
    if not conn:
        print(f"pull: no mirror configured ({', '.join(missing)} not set): skipped")
        return 0
    s3, cfg = conn
    want = set(ids) if ids else None
    for key, o, rs in mirror_objects(m):
        need = [r for r in rs if state(r) in ("missing", "partial") and (want is None or r["id"] in want)]
        if not need:
            continue
        try:
            h = head(s3, cfg, key)
        except Exception as e:  # unreachable or refused: the mirror is only a fail-safe
            print(f"mirror: {key}: {e}")
            continue
        if not h:
            print(f"not in the mirror: {key}")
            continue
        base = ROOTS["cache"] if o["type"] == "zip" else ROOTS[o["root"]]
        os.makedirs(base, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as tmp:
            f = os.path.join(tmp, key)
            print(f"get   {key} ({h['ContentLength'] / 1e6:.0f} MB) for {', '.join(r['id'] for r in need)}")
            s3.download_file(cfg["bucket"], key, f)
            got = sha256(f)
            if h.get("Metadata", {}).get("sha256") not in (None, got):
                sys.exit(f"{key}: checksum mismatch")
            if o["type"] == "zip":
                r = rs[0]
                if r.get("sha256") and got != r["sha256"]:
                    print(f"note  {key} is not the version in the manifest")
                unpack_zip(f, r)
            else:
                with tarfile.open(f) as t:  # existing files are overwritten with the mirror's copy
                    t.extractall(base, filter="data")
                print(f"ok    {key} -> {os.path.join(base, o['folder'])}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["status", "install", "import", "push", "pull"])
    ap.add_argument("args", nargs="*", help="ids from engine/third_party.json (import: the zip file)")
    ap.add_argument("--required", action="store_true", help="install: only the required entries")
    ap.add_argument("--verify", action="store_true", help="status: check sha256 of every file")
    ap.add_argument("--dry-run", action="store_true", help="push: say what would be uploaded")
    a = ap.parse_args()
    if a.action == "status":
        return status(a.args, a.verify)
    if a.action == "install":
        return install(a.args, a.required)
    if a.action == "import":
        if len(a.args) != 1:
            ap.error("import needs one zip file")
        import_zip(a.args[0])
        return 0
    if a.action == "push":
        return push(a.dry_run)
    return pull(a.args)


if __name__ == "__main__":
    sys.exit(main())
