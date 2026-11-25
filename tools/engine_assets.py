#!/usr/bin/env python3
"""Engine files that cannot live in the repo: the singing voicebanks, the vocoder and the
reference audio. Each user installs them from their official sources, accepting each
licence themselves; nothing here redistributes them.

    python3 tools/engine_assets.py status               # what is installed, and from where to get the rest
    python3 tools/engine_assets.py install              # download what has a direct official link
    python3 tools/engine_assets.py import <file.zip>    # install a voicebank zip you downloaded yourself

Voicebanks (engine/voices.json has the licences and credits):
- Hoshino Hanami v1.0 (Lotte V): every hanami* voice. Download it yourself from the MediaFire
  link in the v1.0 release post on https://lottev.moe/ (there is no direct link a script
  can use), then `import` the zip. Terms: any creative use, credit Lotte V, do not
  redistribute the files.
- LEONA beta (Lotte V, CC BY 4.0 plus the same terms): the GitHub release in
  LEONA_RELEASE; `install` fetches it when LEONA_URL resolves, otherwise download it from
  the release page and `import` it.
- Potluck vocoder v100 (tigermeat): `install` fetches dsvocoder.zip from its GitHub release.

Whisper (faster-whisper small and small.en) downloads from Hugging Face on first use.

Owner-only private mirror (never part of a distributed package): `push` uploads the official
zips exactly as downloaded, plus the reference audio and the Whisper models, to
SPECTRE_ENGINE_BUCKET (default spectre-engine) with the SPECTRE_S3_* credentials, and `pull`
restores them, so the owner's own new environments skip the manual downloads. It is a private copy for the owner's sessions only; a plugin or any other user
must use `install` / `import` instead.
"""
import argparse
import hashlib
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

CACHE = os.path.expanduser(os.environ.get("SPECTRE_CACHE", "~/.cache/spectre"))
SVS = os.path.join(CACHE, "svs")

LEONA_RELEASE = "https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/releases/tag/v0.0.1b-leona"
LEONA_URL = os.environ.get("SPECTRE_LEONA_URL", "")  # the release's zip asset, once confirmed
POTLUCK_URL = "https://github.com/mrtigermeat/potluck-vocoder/releases/download/v100/dsvocoder.zip"

# name -> (folder under CACHE, top folder name in the official zip, where to get it)
VOICEBANKS = {
    "hanami": ("svs/hanami/bank", "Hoshino Hanami", "manual: MediaFire link in the v1.0 post on https://lottev.moe/"),
    "leona": ("svs/leona/bank", "LEONA", LEONA_RELEASE),
    "potluck": ("svs/potluck/dsvocoder", "dsvocoder", POTLUCK_URL),
}
# private mirror only: key in the bucket -> (local source, how it unpacks)
#   zip: the official download as is, restored with unpack_zip (the same path as `import`)
#   tar: a folder under CACHE (or HF_CACHE), restored in place
HF_CACHE = os.path.expanduser(os.environ.get("HF_HOME", "~/.cache/huggingface"))
MIRROR = {
    "hanami-v1.0.zip": ("zip", os.path.join(SVS, "dl/hanami-v1.0.zip"), "hanami"),
    "leona-beta.zip": ("zip", os.path.join(SVS, "dl/leona-beta.zip"), "leona"),
    "dsvocoder.zip": ("zip", os.path.join(SVS, "potluck/dsvocoder.zip"), "potluck"),
    "refs.tar": ("tar", CACHE, "refs"),  # reference audio for measurement; targets.json holds the measured curves
    "whisper.tar": ("tar", HF_CACHE, "hub"),  # faster-whisper small and small.en (also on Hugging Face)
}


def installed(rel):
    d = os.path.join(CACHE, rel)
    return os.path.isdir(d) and bool(os.listdir(d))


def unpack_zip(path, name=None):
    """Unpack an official zip into its folder: the zip's single top folder becomes the bank folder."""
    with zipfile.ZipFile(path) as z:
        tops = {n.split("/", 1)[0] for n in z.namelist() if n.strip("/")}
        if len(tops) != 1:
            sys.exit(f"{path}: expected one top folder, found {sorted(tops)[:5]}")
        top = tops.pop()
        if name is None:
            name = next((k for k, (_, prefix, _) in VOICEBANKS.items() if top.startswith(prefix)), None)
            if name is None:
                sys.exit(f"{path}: top folder {top!r} is not a known voicebank ({', '.join(VOICEBANKS)})")
        rel = VOICEBANKS[name][0]
        dst = os.path.join(CACHE, rel)
        if installed(rel):
            print(f"have  {name} ({rel}); remove it first to replace it")
            return
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with tempfile.TemporaryDirectory(dir=os.path.dirname(dst)) as tmp:
            for m in z.infolist():
                target = os.path.realpath(os.path.join(tmp, m.filename))
                if not target.startswith(os.path.realpath(tmp) + os.sep):
                    sys.exit(f"{path}: unsafe path {m.filename!r}")
            z.extractall(tmp)
            shutil.move(os.path.join(tmp, top), dst)
    print(f"ok    {name} -> {rel}")


def download(url, dst):
    print(f"get   {url}")
    with urllib.request.urlopen(url) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)


def status():
    for name, (rel, _, src) in VOICEBANKS.items():
        print(f"{'ok     ' if installed(rel) else 'MISSING'} {name:8} {rel:24} {src}")
    print(f"{'ok     ' if installed('refs') else 'missing'} refs     {'refs':24} reference audio (only for new measurements)")


def install():
    for name, (rel, _, src) in VOICEBANKS.items():
        if installed(rel):
            print(f"have  {name}")
            continue
        url = POTLUCK_URL if name == "potluck" else LEONA_URL if name == "leona" else ""
        if not url:
            print(f"todo  {name}: download it from {src}, then: python3 tools/engine_assets.py import <zip>")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            z = os.path.join(tmp, f"{name}.zip")
            download(url, z)
            unpack_zip(z, name)


# ---- owner-only private mirror ---------------------------------------------------------


def mirror_client():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from upload_track import client, env

    cfg = {
        "endpoint": env("SPECTRE_S3_ENDPOINT").rstrip("/"),
        "region": env("SPECTRE_S3_REGION"),
        "bucket": env("SPECTRE_ENGINE_BUCKET", "spectre-engine"),
        "key_id": env("SPECTRE_S3_ACCESS_KEY_ID"),
        "secret": env("SPECTRE_S3_SECRET_ACCESS_KEY"),
    }
    return client(cfg), cfg


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def head(s3, cfg, key):
    try:
        return s3.head_object(Bucket=cfg["bucket"], Key=key)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return None
        raise


def mirror_installed(kind, base, what):
    return installed(VOICEBANKS[what][0]) if kind == "zip" else os.path.isdir(os.path.join(base, what)) and bool(os.listdir(os.path.join(base, what)))


def push(dry_run):
    s3, cfg = mirror_client()
    for key, (kind, base, what) in MIRROR.items():
        with tempfile.TemporaryDirectory() as tmp:
            if kind == "zip":
                src = base
                if not os.path.isfile(src):
                    print(f"skip  {key}: {src} not here")
                    continue
            else:
                if not mirror_installed(kind, base, what):
                    print(f"skip  {key}: {os.path.join(base, what)} not here")
                    continue
                src = os.path.join(tmp, key)
                with tarfile.open(src, "w") as t:
                    t.add(os.path.join(base, what), arcname=what)
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


def pull():
    s3, cfg = mirror_client()
    for key, (kind, base, what) in MIRROR.items():
        if mirror_installed(kind, base, what):
            print(f"have  {what}")
            continue
        h = head(s3, cfg, key)
        if not h:
            print(f"not in the mirror: {key}")
            continue
        os.makedirs(base if kind == "tar" else CACHE, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=CACHE if kind == "zip" else base) as tmp:
            f = os.path.join(tmp, key)
            print(f"get   {key} ({h['ContentLength'] / 1e6:.0f} MB)")
            s3.download_file(cfg["bucket"], key, f)
            want = h.get("Metadata", {}).get("sha256")
            if want and sha256(f) != want:
                sys.exit(f"{key}: checksum mismatch")
            if kind == "zip":
                unpack_zip(f, what)
            else:
                with tarfile.open(f) as t:
                    t.extractall(base, filter="data")
        print(f"ok    {what}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["status", "install", "import", "push", "pull"])
    ap.add_argument("file", nargs="?", help="import: the voicebank zip")
    ap.add_argument("--dry-run", action="store_true", help="push: say what would be uploaded")
    a = ap.parse_args()
    if a.action == "status":
        status()
    elif a.action == "install":
        install()
    elif a.action == "import":
        if not a.file:
            ap.error("import needs the zip file")
        unpack_zip(a.file)
    elif a.action == "push":
        push(a.dry_run)
    else:
        pull()


if __name__ == "__main__":
    main()
