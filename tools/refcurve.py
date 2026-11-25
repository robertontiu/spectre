"""refcurve: era-appropriate master target curves, measured.

Two sources, one output format (a 1/3-octave target curve, dB re 1 kHz, on the bands of engine/master.py, with n,
per-band spread and provenance):

  catalogue  The open catalogue: MusicBrainz recordings chosen by tag and first-release year, by artist or by release,
             joined to AcousticBrainz low-level data (Essentia analysis of users' own files, CC0; collection ended in
             2022). No audio is downloaded. Per track: the mean energy per Bark band (Essentia `barkbands`, 2048-point
             frames, no equal-loudness filter) in dB relative to the track's level over 510 Hz-2 kHz; then medians and
             interquartile ranges per band. A smooth 1/3-octave curve is then fitted so that the curve, read through
             the same Bark analysis (`bark_of_curve`: the expected Hann-windowed spectrum of noise shaped like the
             curve after the master's 28 Hz clean-up filter), reproduces the medians (least squares, smoothness
             penalty, bands 32 Hz-15.5 kHz; the band under 32 Hz reads high and is not fitted). This is the method of
             docs/TRANCE.md, section C, rebuilt as a tool.
               python3 tools/refcurve.py catalogue --tag trance --years 2015-2021 --per-year 300 --name trance_2015
               python3 tools/refcurve.py catalogue --artist "Taraf de Haïdouks" --limit 100 --name joc_taraf
               python3 tools/refcurve.py catalogue --release <mbid> --release <mbid> ... --name caroling_albums
  measure    Local reference masters (lossless files the owner bought; analysis only, the audio never enters the repo:
             keep it in ~/.cache/spectre/refs/<genre>/). Per file, with engine/master.py's own analyser: the gated
             1/3-octave spectrum of the mid channel (and of the side), integrated and short-term loudness, true peak,
             PLR, loudness range, side-minus-mid width, low-end L/R correlation, crest per region, and the same Bark
             reading as the catalogue; then medians and spreads.
               python3 tools/refcurve.py measure ~/.cache/spectre/refs/trance/*.flac --name trance_2025 --era 2023-2026
  check      Read a target curve (from engine/master.py, or a curve file) through the Bark analysis and compare it,
             band by band, with a catalogue file's medians (the tables in the genre docs' "Era assessment").
               python3 tools/refcurve.py check trance --against out/trance_2015.json
  add        Put a curve file into engine/targets.json (the era targets engine/master.py loads; atomic write).
               python3 tools/refcurve.py add out/trance_2015.json [--note "..."]

Only aggregates leave this tool (medians and spreads over many tracks, plus the list of titles measured): no per-track
spectrum is written to a curve file (docs/PRODUCTION.md, "The legal and ethical position"). Downloads (MusicBrainz
searches, the AcousticBrainz features used) are cached in ~/.cache/spectre/refs/catalogue (outside git).
Data: MusicBrainz (https://musicbrainz.org/doc/MusicBrainz_API), AcousticBrainz (https://acousticbrainz.org/, CC0).
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "engine")
sys.path.insert(0, ENGINE)
import master as M  # noqa: E402

SR = 44100
THIRD = M.THIRD
CACHE = os.path.expanduser("~/.cache/spectre/refs/catalogue")
UA = "spectre-refcurve/1.0 ( https://github.com/robertontiu/spectre )"
MB = "https://musicbrainz.org/ws/2/"
AB = "https://acousticbrainz.org/api/v1/low-level"

# Essentia's BarkBands (27 bands; the defaults of the extractor AcousticBrainz ran). Its FrequencyBands sums the
# power of FFT bins from int(lo/df + 0.5) up to (not including) int(hi/df + 0.5), so with 2048-point frames at
# 44.1 kHz (df = 21.5 Hz) the nominal 50-100 Hz band really covers about 32-97 Hz: `bark_edges_real` gives the
# ranges as analysed, which is how every table in the docs labels them.
BARK = [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 510.0, 630.0, 770.0, 920.0, 1080.0, 1270.0, 1480.0, 1720.0,
        2000.0, 2320.0, 2700.0, 3150.0, 3700.0, 4400.0, 5300.0, 6400.0, 7700.0, 9500.0, 12000.0, 15500.0, 20500.0]
NFFT, HOP = 2048, 1024
DF = SR / NFFT
BIN_LO = [int(BARK[i] / DF + 0.5) for i in range(27)]
BIN_HI = [int(BARK[i + 1] / DF + 0.5) for i in range(27)]
REF_BANDS = list(range(7, 15))      # 510-2000 Hz: the reference level (bands 510-630 ... 1720-2000)
FIT_BANDS = list(range(0, 27))
# Under 32 Hz the Bark reading is unreliable (a re-implementation read 1-4.5 dB high there; docs/TRANCE.md C), so it
# enters the fit at half weight: enough to stop the curve's slope running on below the kick, not enough to set it.
# 15.5-20.5 kHz: lossy files are cut there, so that band is fitted (at half weight) to the median of the lossless
# files only, when there are at least 20 of them; otherwise it is left out and 16 kHz follows the smoothness term.
FIT_WEIGHTS = np.array([0.5] + [1.0] * 25 + [0.5])
REGIONS = {"sub": (20, 60), "bass": (60, 150), "lowmid": (150, 400), "mid": (400, 2000), "presence": (2000, 6000),
           "air": (6000, 18000)}


def bark_edges_real():
    return [(round(BIN_LO[i] * DF - DF / 2 if BIN_LO[i] else 0), round(BIN_HI[i] * DF - DF / 2)) for i in range(27)]


def bark_labels():
    out = []
    for lo, hi in bark_edges_real():
        out.append(f"under {hi}" if lo == 0 else f"{lo}-{hi}")
    return out


def rel_ref(e):
    """Bark energies (linear, any scale) to dB relative to the track's level over 510 Hz-2 kHz (the mean of the dB
    values of those eight bands: the definition that reproduces the research tables within 0.1-0.2 dB)."""
    d = 10 * np.log10(np.asarray(e, dtype=float) + 1e-30)
    return d - d[REF_BANDS].mean()


# ------------------------------------------------------------------ the Bark reading of a curve and of audio

_K = None


def _hann_kernel(os_=8, span=24):
    """|W(x)|^2 of a 2048-point periodic Hann window at offsets x (in bins) -span..span, step 1/os_."""
    global _K
    if _K is None:
        w = np.hanning(NFFT + 1)[:-1]
        x = np.arange(-span * os_, span * os_ + 1) / os_
        n = np.arange(NFFT)
        W = np.exp(-2j * np.pi * np.outer(x, n) / NFFT) @ w
        _K = (np.abs(W) ** 2) / (np.abs(W) ** 2).max(), os_
    return _K


def curve_psd(anchors, f):
    """Power spectral density of noise shaped like a 1/3-octave curve (band energies interpolated in log frequency
    as engine/master.py does), after the master's 28 Hz 8th-order clean-up high-pass."""
    fa = np.array(sorted(anchors), dtype=float)
    va = np.array([anchors[k] for k in sorted(anchors)], dtype=float)
    ff = np.maximum(f, 1.0)
    c = np.interp(np.log10(ff), np.log10(fa), va)
    top = ff > fa[-1]  # above the last band: continue the slope of the last third-octave (records keep falling)
    c[top] = va[-1] + (va[-1] - va[-2]) * np.log2(ff[top] / fa[-1]) * 3
    psd = 10 ** (c / 10) / ff  # energy per 1/3 octave is psd * bandwidth, bandwidth proportional to f
    from scipy import signal
    _, h = signal.sosfreqz(signal.butter(8, 28, "high", fs=SR, output="sos"), worN=ff, fs=SR)
    return psd * np.abs(h) ** 2 * (f > 0)


def bark_of_curve(anchors):
    """The 27 Bark-band energies (linear) AcousticBrainz would report for long noise shaped like the curve."""
    K, os_ = _hann_kernel()
    f = np.arange(0, (NFFT // 2 + 1) * os_) * DF / os_
    p = np.convolve(curve_psd(anchors, f), K, mode="same")[::os_]  # expected periodogram per bin
    return np.array([p[BIN_LO[i]:BIN_HI[i]].sum() for i in range(27)])


def bark_of_audio(x):
    """Essentia-style Bark reading of a mono signal at 44.1 kHz: Hann frames of 2048, hop 1024, mean band energy."""
    w = np.hanning(NFFT + 1)[:-1].astype(np.float32)
    n = (len(x) - NFFT) // HOP + 1
    acc = np.zeros(27)
    for s in range(0, n, 512):
        idx = np.arange(s, min(n, s + 512))[:, None] * HOP + np.arange(NFFT)[None, :]
        P = np.abs(np.fft.rfft(x[idx] * w, axis=1)) ** 2
        for i in range(27):
            acc[i] += P[:, BIN_LO[i]:BIN_HI[i]].sum()
    return acc / max(n, 1)


def fit_curve(target_rel, weights=None, smooth=0.6, fix_1k=True):
    """1/3-octave curve (dB re 1 kHz, 28 bands) whose Bark reading matches `target_rel` (27 values, dB re 510-2k) on
    FIT_BANDS. Least squares with a second-difference smoothness penalty (`smooth`, dB per dB of curvature)."""
    from scipy.optimize import least_squares
    tr = np.asarray(target_rel, dtype=float)
    wts = FIT_WEIGHTS if weights is None else np.asarray(weights, dtype=float)
    i1k = list(THIRD).index(1000)

    def model(c):
        return rel_ref(bark_of_curve(dict(zip(THIRD, c))))

    def resid(c):
        r = (model(c) - tr)[FIT_BANDS] * wts
        d2 = np.diff(c, 2) * smooth
        out = [r, d2]
        if fix_1k:
            out.append([c[i1k] * 10])
        return np.concatenate(out)
    # start: a smooth pink-ish guess
    c0 = np.interp(np.log10(THIRD), np.log10([31.5, 100, 1000, 10000, 16000]), [0, 4, 0, -6, -12])
    sol = least_squares(resid, c0, method="trf", x_scale=3.0, max_nfev=400)
    c = sol.x - sol.x[i1k]
    res = (model(c) - tr)[FIT_BANDS]
    return c, res


# ------------------------------------------------------------------ network (cached)

def _get(url, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                rem = r.headers.get("X-RateLimit-Remaining")
                if rem is not None and int(rem) < 3:
                    time.sleep(float(r.headers.get("X-RateLimit-Reset-In", 5)) + 0.5)
                return json.load(r)
        except Exception:  # rate limits (503 at MusicBrainz, 429 at AcousticBrainz) and timeouts: back off
            if k == tries - 1:
                raise
            time.sleep(2 + 3 * k)


def _cached(key, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, key + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    v = fn()
    tmp = p + ".tmp"
    json.dump(v, open(tmp, "w"))
    os.replace(tmp, p)
    return v


_last_mb = [0.0]


def mb(path, params):
    def go():
        wait = 1.1 - (time.time() - _last_mb[0])
        if wait > 0:
            time.sleep(wait)  # MusicBrainz: at most one request per second
        _last_mb[0] = time.time()
        return _get(MB + path + "?" + urllib.parse.urlencode(dict(params, fmt="json")))
    key = "mb_" + path.replace("/", "_") + "_" + urllib.parse.quote(json.dumps(params, sort_keys=True), safe="")[:150]
    return _cached(key, go)


def search_recordings(query, limit):
    out, off = [], 0
    while len(out) < limit:
        d = mb("recording/", dict(query=query, limit=min(100, limit - len(out)), offset=off))
        recs = d.get("recordings", [])
        if not recs:
            break
        out += recs
        off += len(recs)
        if off >= d.get("count", 0):
            break
    return out


def recordings_for(args):
    """[(mbid, label, year)] chosen by tag+years, artist or release."""
    recs = []
    if args.tag:
        y0, y1 = (int(v) for v in args.years.split("-")) if args.years else (None, None)
        tagq = " OR ".join(f'tag:"{t}"' for t in args.tag)
        years = range(y0, y1 + 1) if y0 else [None]
        for y in years:
            q = f"({tagq})" + (f" AND firstreleasedate:[{y} TO {y}]" if y else "")
            for r in search_recordings(q, args.per_year):
                recs.append((r["id"], _label(r), y))
    for a in args.artist or []:
        aid = a if _is_mbid(a) else mb("artist/", dict(query=f'artist:"{a}"', limit=1))["artists"][0]["id"]
        for r in search_recordings(f"arid:{aid}", args.limit):
            recs.append((r["id"], _label(r), (r.get("first-release-date") or "")[:4] or None))
    for rel in args.release or []:
        d = mb("release/" + rel, dict(inc="recordings artist-credits"))
        y = (d.get("date") or "")[:4] or None
        for med in d.get("media", []):
            for t in med.get("tracks", []):
                r = t["recording"]
                recs.append((r["id"], _label(r, d), y))
    seen, out = set(), []
    for m, lab, y in recs:
        if m not in seen:
            seen.add(m)
            out.append((m, lab, y))
    return out


def _is_mbid(s):
    return len(s) == 36 and s.count("-") == 4


def _label(r, release=None):
    ac = r.get("artist-credit") or (release or {}).get("artist-credit") or []
    who = "".join(a.get("name", "") + a.get("joinphrase", "") for a in ac)
    return f"{who} - {r.get('title', '')}"


def ab_features(mbids):
    """{mbid: dict(bark, length, rg, lossless, bpm) or None}. Only these few numbers are cached, never the full data."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "acousticbrainz.jsonl")
    have = {}
    if os.path.exists(p):
        for line in open(p):
            k, v = json.loads(line)
            have[k] = v
    need = [m for m in mbids if m not in have]
    with open(p, "a") as fh:
        for i in range(0, len(need), 25):
            chunk = need[i:i + 25]
            d = _get(AB + "?" + urllib.parse.urlencode(dict(recording_ids=";".join(chunk))))
            for m in chunk:
                v = None
                sub = (d.get(m) or {}).get("0")
                if sub:
                    ap = sub["metadata"]["audio_properties"]
                    v = dict(bark=sub["lowlevel"]["barkbands"]["mean"], length=ap.get("length"),
                             rg=ap.get("replay_gain"), lossless=ap.get("lossless"),
                             bpm=(sub.get("rhythm") or {}).get("bpm"))
                have[m] = v
                fh.write(json.dumps([m, v]) + "\n")
            fh.flush()
            if i and i % 500 == 0:
                print(f"  acousticbrainz: {i + len(chunk)}/{len(need)}", file=sys.stderr)
            time.sleep(0.12)
    return {m: have.get(m) for m in mbids}


# ------------------------------------------------------------------ outputs

def _q(v):
    return round(float(v), 1)


def aggregate(rel):
    """rel: (n_tracks, 27) dB. Medians and interquartile ranges per band."""
    med = np.median(rel, 0)
    q1, q3 = np.percentile(rel, [25, 75], axis=0)
    return med, q3 - q1


def third_spread(iqr_bark):
    """Spread per 1/3-octave band: the IQR of the Bark band holding the band's centre."""
    out = {}
    edges = bark_edges_real()
    for f in THIRD:
        k = next((i for i, (lo, hi) in enumerate(edges) if lo <= f < hi), 26)
        out[_hz(f)] = _q(iqr_bark[k])
    return out


def _hz(f):
    return str(int(f)) if f >= 100 or float(f).is_integer() else str(f)


def curve_dict(c):
    return {_hz(f): float(np.round(v * 2) / 2) for f, v in zip(THIRD, c)}


def cmd_catalogue(args):
    recs = recordings_for(args)
    print(f"{len(recs)} recordings from MusicBrainz", file=sys.stderr)
    feats = ab_features([m for m, _, _ in recs])
    rows, labels, rgs, years, lossless = [], [], [], [], []
    for m, lab, y in recs:
        v = feats.get(m)
        if not v or not v.get("bark") or (v.get("length") or 0) < args.min_length:
            continue
        rows.append(rel_ref(v["bark"]))
        labels.append(lab)
        years.append(y)
        lossless.append(bool(v.get("lossless")))
        if v.get("rg") is not None:
            rgs.append(-23.7 - v["rg"])  # LUFS ~ -23.7 - ReplayGain (fitted on Spectre's masters, docs/CAROLING.md)
    if not rows:
        raise SystemExit("no tracks with AcousticBrainz data")
    rel = np.array(rows)
    med, iqr = aggregate(rel)
    lo = np.array(lossless)
    sub = aggregate(rel[lo])[0] if lo.sum() >= 20 else None
    tgt, wts = med.copy(), FIT_WEIGHTS.copy()
    if sub is not None:
        tgt[26] = sub[26]
    else:
        wts[26] = 0.0
    c, res = fit_curve(tgt, weights=wts, smooth=args.smooth)
    src = []
    if args.tag:
        src.append("MusicBrainz tag " + " OR ".join(args.tag) + (f", first release {args.years}" if args.years else "")
                   + f", up to {args.per_year} per year")
    if args.artist:
        src.append("MusicBrainz artist " + ", ".join(args.artist) + f", up to {args.limit} recordings")
    if args.release:
        src.append(f"{len(args.release)} MusicBrainz releases")
    out = dict(
        name=args.name, method="catalogue",
        source="; ".join(src) + "; AcousticBrainz low-level Bark bands (CC0)",
        era=args.era or args.years or _span(years), n=len(rows), date=datetime.date.today().isoformat(),
        curve=curve_dict(c), spread_db=third_spread(iqr),
        bark=dict(bands=bark_labels(), median=[_q(v) for v in med], iqr=[_q(v) for v in iqr],
                  lossless_only_median=[_q(v) for v in sub] if sub is not None else None,
                  fit_residual=[_q(r) for r in res]),
        fit=dict(max_abs_residual_db=_q(np.abs(res).max()), mean_abs_residual_db=round(float(np.abs(res).mean()), 2),
                 smooth=args.smooth, bands_fitted="0-20.5 kHz (Bark bands 1-27; under 32 Hz at half weight; 15.5-20.5 kHz at half weight on the "
                                  "lossless files' median, or not fitted when fewer than 20 are lossless)",
                 note="31.5-40 Hz rest on one Bark band (32-97 Hz), the unreliable band under 32 Hz and the smoothness "
                      "term (about +-3 dB); 16 kHz rests on the lossless files (about +-2 dB)"),
        loudness=dict(est_lufs_median=_q(np.median(rgs)) if rgs else None,
                      est_lufs_middle_half=[_q(v) for v in np.percentile(rgs, [25, 75])] if rgs else None,
                      method="LUFS ~ -23.7 - ReplayGain, +-1-2 dB"),
        lossless_share=round(float(lo.mean()), 2),
        tracks=sorted(set(labels)) if args.list_tracks else None,
        note=args.note)
    out = {k: v for k, v in out.items() if v is not None}
    _write(out, args.out)
    _print_summary(out)


def _span(years):
    ys = sorted(int(y) for y in years if y)
    return f"{ys[0]}-{ys[-1]}" if ys else None


def _decode(path):
    """Any audio file to float64 stereo at 44.1 kHz (ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.astype(np.float64)


def measure_file(path):
    import pyloudnorm as pyln
    from scipy import signal
    x = _decode(path)
    meter = pyln.Meter(SR)
    mid, side = x.mean(0), (x[0] - x[1]) / 2
    tm = M.third_octave(mid)
    ts = M.third_octave(side)  # the side channel's own shape (dB re its 1 kHz band)
    L = meter.integrated_loudness(x.T)
    tp = M.true_peak_db(x)
    st = M.short_term_lufs(x, meter)
    Lm = meter.integrated_loudness(mid[:, None])
    Ls = meter.integrated_loudness(side[:, None])
    low = M.lin_lowpass(x, 120.0, 8193)
    crest = {}
    for name, (lo, hi) in REGIONS.items():
        b = signal.sosfilt(signal.butter(4, [lo, min(hi, SR / 2 - 100)], "band", fs=SR, output="sos"), mid)
        env = np.sqrt(np.convolve(b ** 2, np.ones(441) / 441, mode="valid")[::441] + 1e-20)
        crest[name] = 20 * np.log10(env.max() / np.sqrt((env ** 2).mean()))
    v1k = np.mean(tm[M.REF_BANDS])
    return dict(third=tm - v1k, side=ts, lufs=L, tp=tp, plr=tp - L,
                lra=float(np.percentile(st, 95) - np.percentile(st, 10)) if len(st) else None,
                st_max=float(st.max()) if len(st) else None, width=Ls - Lm,
                low_corr=float(np.corrcoef(low[0], low[1])[0, 1]), crest=crest, bark=rel_ref(bark_of_audio(mid)))


def cmd_measure(args):
    res, names = [], []
    for p in args.files:
        print("measuring", os.path.basename(p), file=sys.stderr)
        res.append(measure_file(p))
        names.append(os.path.splitext(os.path.basename(p))[0])
    third = np.array([r["third"] for r in res])
    med = np.median(third, 0)
    med -= med[list(THIRD).index(1000)]
    q1, q3 = np.percentile(third, [25, 75], axis=0)
    side = np.median([r["side"] for r in res], 0)

    def stat(k):
        v = np.array([r[k] for r in res if r[k] is not None and np.isfinite(r[k])])
        return dict(median=_q(np.median(v)), middle_half=[_q(a) for a in np.percentile(v, [25, 75])]) if len(v) else None
    bark = np.array([r["bark"] for r in res])
    bm, bi = aggregate(bark)
    out = dict(
        name=args.name, method="measure",
        source=args.source or f"{len(res)} reference masters measured locally with engine/master.py's analyser",
        era=args.era, n=len(res), date=datetime.date.today().isoformat(),
        curve=curve_dict(med), spread_db={_hz(f): _q(v) for f, v in zip(THIRD, q3 - q1)},
        side_curve={_hz(f): _q(v) for f, v in zip(THIRD, side)},
        loudness=dict(lufs=stat("lufs"), true_peak=stat("tp"), plr=stat("plr"), lra=stat("lra"),
                      short_term_max=stat("st_max"), width_side_minus_mid_lu=stat("width"),
                      low_end_corr=stat("low_corr")),
        crest_db={k: _q(np.median([r["crest"][k] for r in res])) for k in REGIONS},
        bark=dict(bands=bark_labels(), median=[_q(v) for v in bm], iqr=[_q(v) for v in bi]),
        tracks=sorted(names), note=args.note)
    out = {k: v for k, v in out.items() if v is not None}
    _write(out, args.out)
    _print_summary(out)


def load_curve(name_or_path):
    if os.path.exists(name_or_path):
        d = json.load(open(name_or_path))
        return {float(k): v for k, v in d["curve"].items()}, d
    if name_or_path in M.TARGETS:
        return dict(M.TARGETS[name_or_path]), None
    raise SystemExit(f"no curve {name_or_path!r}: give a target name ({', '.join(sorted(M.TARGETS))}) or a file")


def cmd_check(args):
    anchors, _ = load_curve(args.curve)
    rd = rel_ref(bark_of_curve(anchors))
    ref = json.load(open(args.against))
    med = np.array(ref["bark"]["median"])
    print(f"{args.curve} read through the Bark analysis, against {ref['name']} (n {ref['n']}, {ref.get('era')}):")
    print(f"{'band (Hz, as analysed)':24s} {'catalogue':>9s} {'curve':>7s} {'diff':>6s}")
    for i, lab in enumerate(bark_labels()):
        if i == 26:
            continue
        print(f"{lab:24s} {med[i]:+9.1f} {rd[i]:+7.1f} {rd[i] - med[i]:+6.1f}" + ("   (unreliable)" if i == 0 else ""))
    d = (rd - med)[1:26]
    print(f"max |diff| 32 Hz-15.5 kHz: {np.abs(d).max():.1f} dB, mean {np.abs(d).mean():.1f} dB")


def cmd_add(args):
    d = json.load(open(args.file))
    path = os.path.join(ENGINE, "targets.json")
    cur = json.load(open(path)) if os.path.exists(path) else {}
    name = args.as_name or d["name"]
    if name in M.MEASURED or name in ("beat", "trap", "trance_handtuned", "rock_handtuned") and name not in cur:
        raise SystemExit(f"{name!r} is a built-in curve; old targets are never replaced (forward only)")
    keep = ("method", "source", "era", "n", "date", "curve", "spread_db", "fit", "loudness", "lossless_share", "note")
    entry = {k: d[k] for k in keep if k in d}
    if args.note:
        entry["note"] = args.note
    if d.get("bark"):
        entry["bark_median"] = d["bark"]["median"]
    cur[name] = entry
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(cur, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)
    print(f"added {name} to {path}")


def _write(out, path):
    s = json.dumps(out, indent=1, ensure_ascii=False)
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        open(path, "w").write(s + "\n")
        print("wrote", path, file=sys.stderr)
    else:
        print(s)


def _print_summary(out):
    print(f"{out['name']}: n {out['n']}, era {out.get('era')}, method {out['method']}", file=sys.stderr)
    print("curve (dB re 1 kHz): " + ", ".join(f"{k} {v:+g}" for k, v in out["curve"].items()), file=sys.stderr)
    if out.get("fit"):
        print(f"fit residual: max {out['fit']['max_abs_residual_db']} dB, mean {out['fit']['mean_abs_residual_db']} dB",
              file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("catalogue", help="target curve from MusicBrainz + AcousticBrainz")
    c.add_argument("--tag", action="append", help="MusicBrainz tag (repeat for OR)")
    c.add_argument("--years", help="first-release years, e.g. 2015-2021 (with --tag)")
    c.add_argument("--per-year", type=int, default=100, help="recordings per year from the search (default 100)")
    c.add_argument("--artist", action="append", help="artist name or MBID (repeat)")
    c.add_argument("--release", action="append", help="release MBID (repeat)")
    c.add_argument("--limit", type=int, default=100, help="recordings per artist (default 100)")
    c.add_argument("--min-length", type=float, default=90.0, help="skip tracks shorter than this (s)")
    c.add_argument("--smooth", type=float, default=0.4, help="smoothness weight of the fit")
    c.add_argument("--name", required=True)
    c.add_argument("--era", help="era label (default: --years or the years found)")
    c.add_argument("--note")
    c.add_argument("--list-tracks", action="store_true", help="include the list of titles (artist - title)")
    c.add_argument("--out")
    m = sub.add_parser("measure", help="target curve from local reference masters (never committed)")
    m.add_argument("files", nargs="+")
    m.add_argument("--name", required=True)
    m.add_argument("--era")
    m.add_argument("--source")
    m.add_argument("--note")
    m.add_argument("--out")
    k = sub.add_parser("check", help="a curve read through the Bark analysis against a catalogue file")
    k.add_argument("curve", help="target name or curve file")
    k.add_argument("--against", required=True)
    a = sub.add_parser("add", help="add a curve file to engine/targets.json")
    a.add_argument("file")
    a.add_argument("--as-name")
    a.add_argument("--note")
    args = ap.parse_args()
    {"catalogue": cmd_catalogue, "measure": cmd_measure, "check": cmd_check, "add": cmd_add}[args.cmd](args)


if __name__ == "__main__":
    main()
