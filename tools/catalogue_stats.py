"""catalogue_stats: the genre docs' catalogue numbers (lengths, tempos, keys, loudness), measured on open data.

The genre research (docs/<GENRE>.md, "Catalogue measurements" and "Radio edit"; engine/genres.json) sets each genre's
length, tempo and loudness from what released records do. This tool reproduces those tables from MusicBrainz and
AcousticBrainz (CC0; Essentia low-level data submitted by users until 2022; no audio is downloaded) and keeps the
command lines of the era targets in engine/targets.json. The reference lists (which albums, which strands) are in
data/catalogue_references.json; the downloads are cached in ~/.cache/spectre/refs/catalogue (outside git), shared
with tools/refcurve.py.

  albums <genre> [--since YEAR]   per-album table and strand summaries for a reference list in
                                  data/catalogue_references.json (caroling, latinpop, chamberscore): tracks (with
                                  AcousticBrainz data), median length (middle half), tracks under 2:00, tempo median
                                  (range; octave-folded into the strand's range), est. LUFS median (range), minor keys
  tag --tag T --years Y0-Y1 [--per-year N] [--fold LO-HI]
                                  length, tempo and est. LUFS medians of a MusicBrainz tag by first-release year
                                  (the era tables, e.g. docs/TRANCE.md section C)
  versions --tag T                radio edits against extended and original mixes (docs/TRANCE.md "Radio edit"):
                                  lengths, pairs, era, loudness difference of the pairs, featured-singer credits
  calibrate [mp3 ...]             the ReplayGain-to-LUFS constant (LUFS ~ C - RG): Essentia's ReplayGain (the
                                  algorithm AcousticBrainz ran) against integrated loudness (pyloudnorm) on Spectre's
                                  own masters; needs `pip install essentia` (not in requirements.txt); ported from
                                  the 2026-11-24 calibration script, not re-run since (essentia was not installed)
  targets [--run]                 the tools/refcurve.py commands that rebuild every era target in engine/targets.json
                                  (printed; with --run, executed and added)

Conventions (as the research used them): MusicBrainz track or recording length; a track counted once per release;
est. LUFS = C - ReplayGain with C = -23.7 (docs/CAROLING.md, about +-1-2 dB); "middle half" = 25th-75th percentile
(Python's statistics.quantiles; the method each doc table used is recorded with its list); tempo folded by doubling or halving into [lo, hi] because Essentia often reports half or double time.
MusicBrainz search results drift, so counts can differ from the docs by a few percent.
"""
import argparse
import glob
import json
import os
import re
import statistics as st
import subprocess
import sys
import urllib.parse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import refcurve as RC  # noqa: E402  (shares its MusicBrainz client, rate limit and cache)

REFS = os.path.join(REPO, "data", "catalogue_references.json")
META = os.path.join(RC.CACHE, "acousticbrainz_meta.jsonl")
RG_TO_LUFS = -23.7
FEATURES = ("rhythm.bpm;tonal.key_key;tonal.key_scale;metadata.audio_properties.replay_gain;"
            "metadata.audio_properties.length;metadata.audio_properties.lossless")


# ------------------------------------------------------------------ data

def ab_meta(mbids):
    """{mbid: dict(bpm, key, scale, rg, length, lossless) or None}; only these numbers are cached."""
    os.makedirs(RC.CACHE, exist_ok=True)
    have = {}
    if os.path.exists(META):
        for line in open(META):
            k, v = json.loads(line)
            have[k] = v
    need = [m for m in dict.fromkeys(mbids) if m not in have]
    with open(META, "a") as fh:
        for i in range(0, len(need), 25):
            chunk = need[i:i + 25]
            d = RC._get(RC.AB + "?" + urllib.parse.urlencode(dict(recording_ids=";".join(chunk), features=FEATURES)))
            for m in chunk:
                x = (d.get(m) or {}).get("0")
                v = None
                if x:
                    ap = x.get("metadata", {}).get("audio_properties", {})
                    tn = x.get("tonal", {})
                    v = dict(bpm=x.get("rhythm", {}).get("bpm"), key=tn.get("key_key"), scale=tn.get("key_scale"),
                             rg=ap.get("replay_gain"), length=ap.get("length"), lossless=ap.get("lossless"))
                have[m] = v
                fh.write(json.dumps([m, v]) + "\n")
            fh.flush()
    return {m: have.get(m) for m in mbids}


def release_tracks(mbid):
    d = RC.mb("release/" + mbid, dict(inc="recordings artist-credits"))
    tr = [t for med in d.get("media", []) for t in med.get("tracks", [])]
    return d, [dict(title=t.get("title"), length=(t.get("length") or t["recording"].get("length") or 0) / 1000,
                    rec=t["recording"]["id"]) for t in tr]


# ------------------------------------------------------------------ helpers

def fold(bpm, lo, hi):
    if not bpm or bpm <= 0:
        return None
    while bpm < lo:
        bpm *= 2
    while bpm > hi:
        bpm /= 2
    return bpm


STYLE = dict(quantiles="inclusive", floor=False)  # per reference list: how its doc table was computed


def mmss(s):
    s = int(s) if STYLE["floor"] else int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def mid(v, fmt=mmss):
    if not v:
        return "no data"
    if len(v) == 1:
        return fmt(v[0])
    q1, _, q3 = st.quantiles(v, n=4, method=STYLE["quantiles"])
    return f"{fmt(st.median(v))} ({fmt(q1)} to {fmt(q3)})"


def rng(v, fmt):
    if not v:
        return "no data"
    return f"{fmt(st.median(v))} ({fmt(min(v))} to {fmt(max(v))})"


def lufs_fmt(x):
    return f"{x:.1f}"


def bpm_fmt(x):
    return f"{x:.0f}"


def track_rows(tracks, meta, fold_range):
    rows = []
    for t in tracks:
        a = meta.get(t["rec"])
        rows.append(dict(length=t["length"], has=bool(a),
                         bpm=fold(a["bpm"], *fold_range) if a and fold_range else (a or {}).get("bpm"),
                         lufs=RG_TO_LUFS - a["rg"] if a and a.get("rg") is not None else None,
                         minor=(a.get("scale") == "minor") if a and a.get("scale") else None))
    return rows


def summary(rows):
    L = [r["length"] for r in rows if r["length"]]
    b = [r["bpm"] for r in rows if r["bpm"]]
    lu = [r["lufs"] for r in rows if r["lufs"] is not None]
    mk = [r["minor"] for r in rows if r["minor"] is not None]
    return L, b, lu, mk


# ------------------------------------------------------------------ commands

def cmd_albums(args):
    cfg = json.load(open(REFS))["albums"][args.genre]
    STYLE.update(cfg.get("style", {}))
    args.since = args.since or cfg.get("since")
    folds = cfg.get("fold", {})
    pooled = {}
    print(f"| strand | album (MusicBrainz release) | tracks (with AcousticBrainz data) | median length (middle half) "
          f"| under 2:00 | tempo median (range) | est. LUFS median (range) | minor keys |")
    print("|---|---|---|---|---|---|---|---|")
    for a in cfg["releases"]:
        d, tracks = release_tracks(a["release"])
        meta = ab_meta([t["rec"] for t in tracks])
        strand = a.get("strand", args.genre)
        fr = folds.get(strand) or folds.get("*")
        rows = track_rows(tracks, meta, fr)
        year = (d.get("date") or "")[:4]
        for r in rows:
            r["year"] = int(year) if year else None
        pooled.setdefault(strand, []).extend(rows)
        L, b, lu, mk = summary(rows)
        n_ab = sum(r["has"] for r in rows)
        print(f"| {strand} | {a['artist']}, *{a['album']}* ({year}, {a['release'][:8]}) | {len(rows)} ({n_ab}) "
              f"| {mid(L)} | {sum(x < 120 for x in L)}/{len(L)} | {rng(b, bpm_fmt)} | {rng(lu, lufs_fmt)} "
              f"| {sum(mk)}/{len(mk) if mk else 0} |")
    print("\nStrand summaries (median, middle half):")
    groups = list(pooled.items()) + [("all", [r for v in pooled.values() for r in v])]
    for strand, rows in groups:
        for label, sel in [("all years", rows)] + ([(f"since {args.since}",
                                                       [r for r in rows if r["year"] and r["year"] >= args.since])]
                                                     if args.since else []):
            L, b, lu, mk = summary(sel)
            print(f"  {strand:22s} {label:11s} {len(sel):4d} tracks  length {mid(L)}  tempo {mid(b, bpm_fmt)}  "
                  f"est. LUFS {mid(lu, lufs_fmt)}  minor {sum(mk)}/{len(mk)}")
        L = [r["length"] for r in rows if r["length"] and r["length"] >= 120]
        if L and args.genre == "chamberscore":
            print(f"  {strand:22s} 2:00+       {len(L):4d} tracks  length {mid(L)}")


def cmd_tag(args):
    y0, y1 = (int(v) for v in args.years.split("-"))
    fr = [float(v) for v in args.fold.split("-")] if args.fold else None
    print("| years | tracks (with data) | length, median (middle half) | tempo, median (middle half) | est. LUFS |")
    print("|---|---|---|---|---|")
    spans = [(y, y) for y in range(y0, y1 + 1)] if args.by_year else \
        [(a, min(a + args.span - 1, y1)) for a in range(y0, y1 + 1, args.span)]
    for a, b in spans:
        ns = argparse.Namespace(tag=args.tag, years=f"{a}-{b}", per_year=args.per_year, artist=None, release=None)
        recs = RC.recordings_for(ns)
        meta = RC.ab_features([m for m, _, _ in recs])
        L, bp, lu, n = [], [], [], 0
        for m, _, _ in recs:
            v = meta.get(m)
            if not v or (v.get("length") or 0) < args.min_length:
                continue
            n += 1
            L.append(v["length"])
            if v.get("bpm"):
                bp.append(fold(v["bpm"], *fr) if fr else v["bpm"])
            if v.get("rg") is not None:
                lu.append(RG_TO_LUFS - v["rg"])
        print(f"| {a}-{b} | {len(recs)} ({n}) | {mid(L)} | {mid(bp, bpm_fmt)} | {mid(lu, lufs_fmt)} |")


VERSIONS = [("radio", "radio edit"), ("extended", "extended mix"), ("original", "original mix")]
DUR_BINS = [0, 150, 180, 195, 210, 225, 240, 270, 300, 360, 420, 480, 600, 3600]  # s; keeps each search under 500
FEAT = re.compile(r"\b(feat\.?|ft\.?|featuring)\b", re.I)


def _qi(v, p):
    """The quantile as the radio-edit count took it: the sorted value at index int(p * n)."""
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def _base(t):
    return re.sub(r"\s*[\(\[].*$", "", t).strip().lower()


def _versions(tag, label):
    recs = {}
    for lo, hi in zip(DUR_BINS, DUR_BINS[1:]):
        # the duration first: refcurve's cache key keeps only the first 150 characters of the quoted query
        q = f'dur:[{lo * 1000} TO {hi * 1000 - 1}] AND recording:"{label}" AND tag:"{tag}"'
        for r in RC.search_recordings(q, 2000):
            if r.get("length") and label in r.get("title", "").lower():
                recs[r["id"]] = r
    groups = {}
    for r in recs.values():
        who = "".join(a.get("name", "") + a.get("joinphrase", "") for a in r.get("artist-credit", []))
        k = (who.lower(), _base(r["title"]))
        groups.setdefault(k, []).append(r)
    return groups


def cmd_versions(args):
    G = {name: _versions(args.tag, label) for name, label in VERSIONS}
    med = {name: {k: st.median(r["length"] / 1000 for r in v) for k, v in g.items()} for name, g in G.items()}
    print("| Set | Tracks | Median | Middle half | 10th-90th percentile |\n|---|---|---|---|---|")
    for name, _ in VERSIONS:
        v = list(med[name].values())
        if not v:
            print(f"| {name} | 0 | | | |")
            continue
        p = [_qi(v, x) for x in (0.1, 0.25, 0.5, 0.75, 0.9)]
        p[2] = st.median(v)
        print(f"| {name} | {len(v)} | {mmss(p[2])} | {mmss(p[1])}-{mmss(p[3])} | {mmss(p[0])}-{mmss(p[4])} |")
    rv = list(med["radio"].values())
    edges = [0, 150, 180, 210, 240, 270, 1e9]
    print("radio edits by length: " + ", ".join(
        f"{mmss(a) if a else '0'}-{mmss(b) if b < 1e9 else 'longer'} {100 * sum(a <= x < b for x in rv) / len(rv):.0f}%"
        for a, b in zip(edges, edges[1:])))
    pairs = []
    for k, r in med["radio"].items():
        long_ = med["extended"].get(k) or med["original"].get(k)
        if long_ and long_ > r + 30:
            pairs.append((k, r, long_))
    if pairs:
        print(f"pairs: {len(pairs)}; radio median {mmss(st.median(p[1] for p in pairs))}, long median "
              f"{mmss(st.median(p[2] for p in pairs))}, kept {st.median(p[1] / p[2] for p in pairs):.0%}, cut "
              f"{mmss(st.median(p[2] - p[1] for p in pairs))}")
    eras = {}
    for k, v in G["radio"].items():
        ys = [int(r["first-release-date"][:4]) for r in v if (r.get("first-release-date") or "")[:4].isdigit()]
        if ys:
            y = min(ys)
            e = "before 2000" if y < 2000 else "2000s" if y < 2010 else "2010s" if y < 2020 else "2020s"
            eras.setdefault(e, []).append(med["radio"][k])
    print("by era (first release): " + ", ".join(f"{e} {mmss(st.median(v))} ({len(v)})" for e, v in sorted(eras.items())))
    for name, _ in VERSIONS:
        g = G[name]
        f = sum(any(FEAT.search(r["title"] + " " + "".join(a.get("name", "") + a.get("joinphrase", "")
                                                           for a in r.get("artist-credit", []))) for r in v)
                for v in g.values())
        print(f"featured singer credited: {name} {100 * f / len(g):.0f}% of {len(g)}")
    ids = [r["id"] for k, _, _ in pairs for name in ("radio", "extended", "original") for r in G[name].get(k, [])]
    meta = ab_meta(ids)
    diffs = []
    for k, _, _ in pairs:
        ra = [meta[r["id"]]["rg"] for r in G["radio"][k] if meta.get(r["id"]) and meta[r["id"]].get("rg") is not None]
        lg = G["extended"].get(k) or G["original"].get(k)
        rb = [meta[r["id"]]["rg"] for r in lg if meta.get(r["id"]) and meta[r["id"]].get("rg") is not None]
        if ra and rb:
            diffs.append(st.median(rb) - st.median(ra))  # LUFS radio minus long = RG long minus RG radio
    if diffs:
        q1, q3 = _qi(diffs, 0.25), _qi(diffs, 0.75)
        print(f"loudness, radio edit minus long version ({len(diffs)} pairs with ReplayGain): median "
              f"{st.median(diffs):+.1f} dB, mean {st.mean(diffs):+.2f}, middle half {q1:+.1f} to {q3:+.1f}")


def cmd_calibrate(args):
    try:
        import essentia.standard as es
        import pyloudnorm as pyln
    except ImportError as e:
        raise SystemExit(f"calibrate needs essentia and pyloudnorm ({e}); pip install essentia pyloudnorm")
    files = args.files or sorted(glob.glob(os.path.join(REPO, "sessions", "*", "*-mastered.mp3")))
    sums = []
    for f in files:
        mono = es.MonoLoader(filename=f, sampleRate=44100)()
        rg = float(es.ReplayGain()(mono))
        x = es.AudioLoader(filename=f)()[0].astype(np.float64)
        lufs = pyln.Meter(44100).integrated_loudness(x)
        sums.append(lufs + rg)
        print(f"{os.path.relpath(f, REPO):60s} RG {rg:+6.2f}  LUFS {lufs:6.2f}  LUFS+RG {lufs + rg:6.2f}")
    if sums:
        print(f"C = median(LUFS + RG) = {st.median(sums):.2f} (spread {min(sums):.2f} to {max(sums):.2f}, n={len(sums)})")


def target_commands():
    cfg = json.load(open(REFS))
    T = json.load(open(os.path.join(REPO, "engine", "targets.json")))
    out = []
    for name, spec in cfg["targets"].items():
        a = ["python3", "tools/refcurve.py", "catalogue", "--name", name, "--out", f"/tmp/refcurve/{name}.json"]
        for t in spec.get("tag", []):
            a += ["--tag", t]
        if "years" in spec:
            a += ["--years", spec["years"]]
        if "per_year" in spec:
            a += ["--per-year", str(spec["per_year"])]
        for ar in spec.get("artist", []):
            a += ["--artist", ar]
        if "limit" in spec:
            a += ["--limit", str(spec["limit"])]
        if "albums" in spec:
            g = cfg["albums"][spec["albums"]]["releases"]
            want = spec.get("strands")
            pick = spec.get("releases")
            for r in g:
                if (not want or r.get("strand") in want) and (not pick or r["release"] in pick):
                    a += ["--release", r["release"]]
            a += ["--min-length", "30"]
        out.append((name, a, (T.get(name) or {}).get("note")))
    return out


def cmd_targets(args):
    for name, a, note in target_commands():
        print(" ".join(map(_sh, a)))
        if args.run:
            os.makedirs("/tmp/refcurve", exist_ok=True)
            subprocess.run(a, cwd=REPO, check=True)
            add = ["python3", "tools/refcurve.py", "add", f"/tmp/refcurve/{name}.json"] + (["--note", note] if note else [])
            subprocess.run(add, cwd=REPO, check=True)


def _sh(s):
    return s if re.fullmatch(r"[\w./:=-]+", s) else "'" + s.replace("'", "'\\''") + "'"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("albums")
    a.add_argument("genre")
    a.add_argument("--since", type=int, help="also summarise releases from this year on")
    t = sub.add_parser("tag")
    t.add_argument("--tag", action="append", required=True)
    t.add_argument("--years", required=True)
    t.add_argument("--per-year", type=int, default=300)
    t.add_argument("--span", type=int, default=5, help="years per row (default 5)")
    t.add_argument("--by-year", action="store_true")
    t.add_argument("--fold", help="tempo range to fold into, e.g. 100-200")
    t.add_argument("--min-length", type=float, default=90.0)
    v = sub.add_parser("versions")
    v.add_argument("--tag", default="trance")
    c = sub.add_parser("calibrate")
    c.add_argument("files", nargs="*")
    g = sub.add_parser("targets")
    g.add_argument("--run", action="store_true", help="run refcurve catalogue + add for every target")
    args = ap.parse_args()
    dict(albums=cmd_albums, tag=cmd_tag, versions=cmd_versions, calibrate=cmd_calibrate, targets=cmd_targets)[args.cmd](args)


if __name__ == "__main__":
    main()
