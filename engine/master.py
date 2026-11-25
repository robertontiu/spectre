"""Mastering stage. Takes a premaster (the raw mix bus) and makes a release master.

Chain (each stage measured, every move bounded):
  0. Analyse      loudness, true peak, 1/3-octave tonal balance vs a genre target, low-end stereo, crest
  1. Clean-up     steep sub-sonic high-pass, mono below the crossover (side channel high-passed)
  2. Tonal EQ     linear-phase EQ that nudges the long-term spectrum toward the target (max +/- 4 dB, smooth)
  3. Multiband    4 linear-phase bands; gentle compression that only rides peaks (low band tames 808 spikes,
                  high-mid band tames harshness)
  4. Translation  harmonics generated from the bass (60-150 Hz) so the low end reads on laptop/phone speakers
  5. Glue         2:1 slow-attack bus compression, about 1-2 dB of reduction
  6. Clip + limit soft clipper then a true-peak limiter running 4x oversampled; ceiling in dBTP
  7. Loudness     the limiter's drive is solved so integrated loudness hits the target
  8. QC           LUFS, true peak, PLR, loudness range, tonal deviation, mono-bass check, laptop simulation,
                  before/after picture

  python3 master.py renders/v027.premaster.wav --genre trap [--lufs ..] [--tp ..] [--out renders/v027.master.wav]
  python3 master.py ... --legacy-master   # master version 1: reproduces the masters released before 2026-11-24

Version 2 (default) lays the target over the mix at its level around 1 kHz, cuts excess top end at full strength and
closes the loop on the finished master (see the comment above MASTER_VERSION and docs/MASTERING.md, "Top end").
The report also carries a phone-speaker check (`phone`; see phone_check).

A genre (engine/genres.json) sets the target curve and every mastering setting; explicit flags override it.
There is no default genre: give --genre (or, for old commands, --target, which picks the matching genre).
"""
import sys, os, json, argparse
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 44100
THIRD = np.array([31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
                  2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000])
# Long-term 1/3-octave energy target for modern 808-driven beats, relative to 1 kHz (dB). Sub-forward but
# not sub-dominated; falls ~3 dB/oct above 2 kHz. Interpolated between anchors.
TARGET_ANCHORS = {31.5: 3.0, 40: 5.5, 50: 6.5, 63: 6.5, 80: 6.0, 100: 5.0, 160: 3.0, 250: 1.5, 500: 1.0,
                  1000: 0.0, 2000: -2.0, 4000: -5.0, 8000: -8.5, 12500: -12.0, 16000: -16.0}


def db(x):
    return 10 ** (x / 20)


# Tonal target curves (dB relative to 1 kHz per 1/3 octave; see docs/MASTERING.md for each derivation).
# Only the shape matters: the EQ aligns each curve to the mix on 200 Hz-5 kHz.
# beat / trap: hand-tuned for 808 beats; the curve of sessions 001-006, kept exactly so their masters reproduce.
# hiphop, trance, rock: measured. Average spectra of 772 US/UK #1 singles 1950-2010 by genre (Pestana, Ma, Reiss,
#   Barbosa & Black 2013, AES 135, Fig. 5: hip-hop, electronic, and the mean of pop and rock), converted from
#   per-FFT-bin levels to 1/3-octave band energy and rounded to 0.5 dB.
# trance_handtuned, rock_handtuned: the earlier hand-tuned curves, kept for comparison.
MEASURED = {
    "hiphop": {31.5: -7.5, 40: -4.0, 50: -0.5, 63: 2.5, 80: 5.5, 100: 8.0, 125: 8.0, 160: 5.0, 200: 3.5, 250: 2.5,
               315: 1.0, 400: 1.5, 500: 2.0, 630: 1.5, 800: 0.0, 1000: 0.0, 1250: -1.0, 1600: -1.5, 2000: -1.5,
               2500: -2.0, 3150: -3.0, 4000: -4.5, 5000: -7.0, 6300: -7.0, 8000: -8.0, 10000: -9.5, 12500: -13.0,
               16000: -20.0},
    "trance": {31.5: -11.0, 40: -7.5, 50: -3.0, 63: 0.5, 80: 4.5, 100: 7.5, 125: 9.0, 160: 6.5, 200: 5.0, 250: 4.0,
               315: 3.0, 400: 2.0, 500: 1.5, 630: 1.0, 800: 0.5, 1000: 0.0, 1250: -0.5, 1600: -1.0, 2000: -2.0,
               2500: -2.5, 3150: -3.0, 4000: -3.0, 5000: -4.0, 6300: -4.0, 8000: -6.0, 10000: -8.0, 12500: -11.5,
               16000: -18.0},
    "rock": {31.5: -15.0, 40: -11.5, 50: -7.0, 63: -3.0, 80: 1.5, 100: 5.0, 125: 7.0, 160: 6.5, 200: 5.5, 250: 5.0,
             315: 4.0, 400: 3.0, 500: 2.5, 630: 2.0, 800: 1.0, 1000: 0.0, 1250: -0.5, 1600: -0.5, 2000: -1.5,
             2500: -2.0, 3150: -3.0, 4000: -4.5, 5000: -6.5, 6300: -8.0, 8000: -9.5, 10000: -12.5, 12500: -16.0,
             16000: -23.0},
}

TARGETS = {
    "beat": TARGET_ANCHORS,
    "trap": TARGET_ANCHORS,
    "hiphop": MEASURED["hiphop"],
    "trance": MEASURED["trance"],
    "rock": MEASURED["rock"],
    "trance_handtuned": {31.5: -4.0, 40: 1.5, 50: 5.0, 63: 5.5, 80: 5.0, 100: 4.0, 160: 2.0, 250: 1.0, 500: 0.5,
                         1000: 0.0, 2000: -1.5, 4000: -3.5, 8000: -6.5, 12500: -9.5, 16000: -13.0},
    "rock_handtuned": {31.5: -7.0, 40: -3.0, 50: 0.5, 63: 2.5, 80: 3.5, 100: 3.5, 160: 3.0, 250: 2.0, 500: 1.0,
                       1000: 0.0, 2000: -1.0, 4000: -3.5, 8000: -7.0, 12500: -10.5, 16000: -15.0},
}

GENRES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genres.json")
SETTINGS = ("target", "lufs", "tp", "eq", "translate", "mono_below", "max_low_boost_db")

# Era targets (2026-11-25): measured curves with their provenance, written by tools/refcurve.py into
# engine/targets.json (`refcurve.py add`). They are added next to the curves above, never in place of one: a name
# that already exists here keeps its built-in curve (forward only), so every earlier master still reproduces.
TARGETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "targets.json")
PROVENANCE = {
    "beat": dict(method="hand-tuned", source="by ear for sessions 001-006 (2026)", era=None, n=None),
    "trap": dict(method="hand-tuned", source="alias of beat", era=None, n=None),
    "hiphop": dict(method="published average spectrum", source="Pestana et al. 2013, Fig. 5 hip-hop: UK/US #1 singles",
                   era="about 1990-2010", n=None),
    "trance": dict(method="published average spectrum", source="Pestana et al. 2013, Fig. 5 electronic: UK/US #1 "
                   "singles tagged electronic (dance-pop, house-pop), not trance", era="1950-2010", n=None),
    "rock": dict(method="published average spectrum", source="Pestana et al. 2013, Fig. 5: mean of pop and rock "
                 "UK/US #1 singles", era="1950-2010, leaning on the 1960s-1980s", n=None),
    "trance_handtuned": dict(method="hand-tuned", source="the earlier trance curve, kept for comparison", era=None, n=None),
    "rock_handtuned": dict(method="hand-tuned", source="the earlier rock curve, kept for comparison", era=None, n=None),
}


def _load_era_targets():
    if not os.path.exists(TARGETS_PATH):
        return
    with open(TARGETS_PATH) as fh:
        era = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    for name, e in era.items():
        if name in TARGETS:
            continue  # built-in curves are never replaced
        TARGETS[name] = {float(f): float(v) for f, v in e["curve"].items()}
        PROVENANCE[name] = {k: e.get(k) for k in ("method", "source", "era", "n", "date")}


_load_era_targets()


def load_genres():
    with open(GENRES_PATH) as fh:
        return {k: v for k, v in json.load(fh).items() if not k.startswith("_")}


def genre_for_target(target, genres):
    """The genre whose config an old `--target`-only command maps to (beat -> trap, trance_handtuned -> trance)."""
    base = {"beat": "trap"}.get(target, target.replace("_handtuned", ""))
    if base in genres:
        return base
    for name, g in genres.items():
        if g["master"]["target"] == target:
            return name
    return None


def resolve_settings(genre=None, target=None, published=False, **overrides):
    """Settings for one master: the genre's config, then explicit overrides (None = not given). `published` takes
    the genre's settings as they were before its era target (`master_published` in genres.json): what the tracks
    already released in that genre were mastered with."""
    genres = load_genres()
    if genre is None and target is None:
        raise SystemExit("master: no genre given. Use --genre " + "|".join(genres) +
                         " (see engine/genres.json and docs/ORCHESTRATION.md, Genre conventions).")
    if genre is None:
        genre = genre_for_target(target, genres)
        if genre is None:
            raise SystemExit(f"master: target {target!r} belongs to no genre; also give --genre " + "|".join(genres))
    if genre not in genres:
        raise SystemExit(f"master: unknown genre {genre!r}; choose one of " + ", ".join(genres))
    s = dict(genres[genre]["master"])
    if published:
        pub = genres[genre].get("master_published")
        if pub is None:
            raise SystemExit(f"master: genre {genre!r} has no `master_published` block: its settings never changed")
        s = {k: v for k, v in pub.items() if k in SETTINGS}
    if target is not None:
        s["target"] = target
    for k, v in overrides.items():
        if v is not None:
            s[k] = v
    if s["target"] not in TARGETS:
        raise SystemExit(f"master: unknown target {s['target']!r}; choose one of " + ", ".join(sorted(TARGETS)))
    return genre, s


def target_curve(freqs, target="beat"):
    anchors = TARGETS[target]
    f = np.array(sorted(anchors))
    v = np.array([anchors[k] for k in f])
    return np.interp(np.log10(freqs), np.log10(f), v)


def third_octave(x):
    """1/3-octave band energy (dB) of a mono signal, gated to the loud parts."""
    w = int(0.4 * SR)
    rms = np.sqrt(np.maximum(uniform_filter1d(x ** 2, w)[::w // 2], 0) + 1e-12)
    loud = rms > np.percentile(rms, 30)
    idx = np.repeat(loud, w // 2)[:len(x)]
    xs = x[:len(idx)][idx] if idx.sum() > SR else x
    f, P = signal.welch(xs, SR, nperseg=32768)
    out = []
    for c in THIRD:
        lo, hi = c / 2 ** (1 / 6), c * 2 ** (1 / 6)
        m = (f >= lo) & (f < hi)
        out.append(10 * np.log10(P[m].sum() + 1e-20))
    out = np.array(out)
    return out - out[list(THIRD).index(1000)]


def lin_lowpass(x, fc, taps=4097):
    h = signal.firwin(taps, fc, fs=SR)
    return signal.fftconvolve(x, h[None, :] if x.ndim == 2 else h, mode="same")


def split_bands(x, xovers):
    """Linear-phase complementary split: bands sum back to x exactly."""
    bands = []
    rest = x
    for fc in xovers:
        low = lin_lowpass(rest, fc, 8193 if fc < 200 else 4097)
        bands.append(low)
        rest = rest - low
    bands.append(rest)
    return bands


def true_peak_db(x):
    if x.ndim == 2:
        return max(true_peak_db(ch) for ch in x)
    return 20 * np.log10(np.abs(signal.resample_poly(x, 4, 1)).max() + 1e-12)


def env_follow(level_db, attack_ms, release_ms, D):
    """One-pole attack/release smoothing on a decimated level track (dB, higher = louder)."""
    a = np.exp(-D / (attack_ms / 1000 * SR))
    r = np.exp(-D / (release_ms / 1000 * SR))
    out = np.empty_like(level_db)
    cur = level_db[0]
    for i, v in enumerate(level_db):
        k = a if v > cur else r
        cur = v + (cur - v) * k
        out[i] = cur
    return out


def compress(x, thr_db, ratio, attack_ms, release_ms, knee=6.0, D=64):
    """Stereo-linked feed-forward compressor. Returns processed x and mean/peak gain reduction."""
    lvl = np.sqrt(np.maximum(uniform_filter1d((x ** 2).max(0), int(0.005 * SR))[::D], 0) + 1e-12)
    ldb = 20 * np.log10(lvl)
    sm = env_follow(ldb, attack_ms, release_ms, D)
    over = sm - thr_db
    gr = np.where(over <= -knee / 2, 0.0,
                  np.where(over >= knee / 2, over * (1 - 1 / ratio),
                           (1 - 1 / ratio) * (over + knee / 2) ** 2 / (2 * knee)))
    g = np.repeat(db(-gr), D)[:x.shape[1]]
    if len(g) < x.shape[1]:
        g = np.pad(g, (0, x.shape[1] - len(g)), mode="edge")
    active = gr[gr > 0.05]
    return x * g, (float(active.mean()) if len(active) else 0.0), float(gr.max())


def short_term_lufs(x, meter):
    w, h = int(3 * SR), int(1 * SR)
    vals = []
    for s in range(0, x.shape[1] - w, h):
        try:
            v = meter.integrated_loudness(x[:, s:s + w].T)
        except Exception:
            continue
        if np.isfinite(v):
            vals.append(v)
    return np.array(vals)


def _up4(ch):
    return signal.resample_poly(ch, 4, 1)


def tp_limit(x, ceiling_db, look_ms=1.5, release_ms=80):
    """True-peak limiter: detect and apply gain at 4x, then return to SR. Channels are oversampled one at a time
    (identical numbers to a 2-D resample, about half the peak memory)."""
    n = x.shape[1]
    sr4 = SR * 4
    c = db(ceiling_db)
    u0 = _up4(x[0])
    pk = np.abs(u0)
    del u0
    u1 = _up4(x[1])
    np.maximum(pk, np.abs(u1), out=pk)
    del u1
    need = np.minimum(1.0, c / (pk + 1e-12))
    del pk
    w = max(1, int(look_ms / 1000 * sr4))
    g = minimum_filter1d(need, 2 * w + 1)
    del need
    D = 64
    gd = g[::D].copy()
    a = np.exp(-D / (release_ms / 1000 * sr4))
    cur = 1.0
    for i in range(len(gd)):
        v = gd[i]
        cur = v if v < cur else v + (cur - v) * a
        gd[i] = cur
    g2 = np.minimum(np.repeat(gd, D)[:len(g)], g)
    del g
    g2 = uniform_filter1d(g2, w)
    y = np.empty((2, n))
    for i in range(2):
        u = _up4(x[i])
        u *= g2
        y[i] = signal.resample_poly(u, 1, 4)[:n]
        del u
    return y, float(20 * np.log10(g2.min() + 1e-12))


def soft_clip(x, ceiling_db=-0.5, amount=0.5):
    """Gentle oversampled clipper that shaves the top few dB of transients (one channel at a time)."""
    c = db(ceiling_db)
    knee = c * (1 - 0.35 * amount)
    y = np.empty_like(x)
    for i in range(x.shape[0]):
        up = _up4(x[i])
        a = np.abs(up)
        over = a > knee
        vals = np.sign(up[over]) * (knee + (c - knee) * np.tanh((a[over] - knee) / (c - knee)))
        del a
        up[over] = vals
        del vals, over
        y[i] = signal.resample_poly(up, 1, 4)[:x.shape[1]]
        del up
    return y


# ---------------------------------------------------------------- master version 2 (2026-11-24)
# Version 1 (sessions 001-006 as first released) aligned the target on the median deviation over 200 Hz-5 kHz and
# moved every band by `eq` (0.7) of its deviation, with a [1/4, 1/2, 1/4] smoothing over the bands. Measured on the
# released masters, that left the top octaves 1-5 dB above the target (docs/MASTERING.md, "Top end"). Version 2:
#   - reference level: the mean deviation over 500 Hz-2 kHz (the mix's level around 1 kHz, where every curve is
#     normalised), so a dip or a note peak in one band no longer shifts the whole curve, and the presence region that
#     is being judged no longer sets its own reference;
#   - from 2 kHz up, cuts are made at full strength (excess top-end energy is what reads as harsh "static" on small
#     speakers); boosts keep `eq` and are capped at +2 dB from 5 kHz up (boosting a dull top end only adds hiss);
#     the 12.5 and 16 kHz bands may be cut by up to 12 dB in total (8 elsewhere);
#   - closed loop: the finished master is measured, and any band from 1 kHz to 16 kHz still more than 1 dB off the
#     curve is corrected and the dynamics stages re-run (at most 4 runs), so whatever the later stages do, the output
#     lands on the curve.
MASTER_VERSION = 2
REF_BANDS = (THIRD >= 500) & (THIRD <= 2000)
CHECK_BANDS = THIRD >= 1000


def ref_offset(dev, version=MASTER_VERSION):
    """The level at which the target is laid over a measured spectrum (dB, added to the target)."""
    if version == 1:
        return float(np.median(dev[(THIRD >= 200) & (THIRD <= 5000)]))
    return float(np.mean(dev[REF_BANDS]))


def eq_filter(x, gains_db):
    fpts = np.concatenate([[0], THIRD, [SR / 2]])
    gpts = db(np.concatenate([[gains_db[0]], gains_db, [gains_db[-1]]]))
    h = signal.firwin2(16385, fpts, gpts, fs=SR)
    return signal.fftconvolve(x, h[None, :], mode="same")


# Version 2 lets the top octave (12.5-16 kHz) be cut by up to 12 dB instead of 8: synthesized hats and noise run
# flat up there while records fall steeply (the measured curves drop 3.5-7 dB per third-octave above 10 kHz).
V2_MAX_CUT = np.where(THIRD >= 12500, -12.0, -8.0)


def _v2_limits(total, max_low_boost=None):
    total = np.clip(total, V2_MAX_CUT, 4.0)  # never more than -8 (-12 at 12.5-16 kHz) / +4 dB in total per band
    if max_low_boost is not None:  # optional (genres.json `max_low_boost_db`): cap boosts below 200 Hz
        total = np.where(THIRD < 200, np.minimum(total, max_low_boost), total)
    return np.where(THIRD >= 5000, np.minimum(total, 2.0), total)


def _master_v2(x, rep, meter, tgt, lufs, tp, translate, eq_strength, max_low_boost=None):
    hf = THIRD >= 2000
    total = np.zeros(len(THIRD))
    xe = x
    for _pass in range(2):  # open-loop passes on the premaster (as in version 1, with the new reference and HF rule)
        dev = third_octave(xe.mean(0)) - tgt
        dev -= ref_offset(dev, 2)
        corr = -dev * eq_strength
        cut = hf & (dev > 0)
        corr[cut] = -dev[cut]
        corr = np.clip(corr, -6.0, 4.0)
        sm = np.convolve(np.pad(corr, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")
        mids = (THIRD >= 100) & (THIRD < 2000)
        corr[mids] = sm[mids]
        new = _v2_limits(total + corr, max_low_boost)
        if np.abs(new - total).max() < 0.5:
            break
        total = new
        xe = eq_filter(x, total)
    loops = []
    for run in range(4):  # closed loop on the finished master
        rep.pop("tp_guard_db", None)
        y, pre = _dynamics(xe, rep, meter, lufs, tp, translate)
        dev = third_octave(y.mean(0)) - tgt
        dev -= ref_offset(dev, 2)
        res = np.where(CHECK_BANDS, dev, 0.0)
        loops.append(round(float(np.abs(res).max()), 2))
        if np.abs(res).max() <= 1.25 or run == 3:
            break
        step = -np.sign(res) * np.maximum(np.abs(res) - 1.0, 0.0)
        new = _v2_limits(total + np.clip(step, -4.0, 4.0), max_low_boost)
        if np.abs(new - total).max() < 0.1:
            break
        total = new
        xe = eq_filter(x, total)
    rep["eq_db"] = {f"{int(f) if f >= 100 else f}": round(float(g), 1) for f, g in zip(THIRD, total) if abs(g) >= 0.5}
    rep["closed_loop_max_dev_db"] = loops
    return y, pre


# ---------------------------------------------------------------- phone-speaker check
# A small-speaker model (approximate, hand-tuned): phone micro-speakers play almost nothing below ~300 Hz, have a
# presence peak around 2-5 kHz and roll off at the very top. 4th-order high-pass at 280 Hz, +4 dB peak at 3 kHz (Q 0.7),
# 2nd-order low-pass at 12 kHz. The check compares the master's top end with the genre target heard through the same
# speaker, and measures how noise-like the 4-16 kHz content is (`flatness_4_16k`, plain spectral flatness, which is
# low for tones and for steeply sloped noise; `noise_likeness_4_16k`, the same with the slope divided out).
PHONE_HP, PHONE_PEAK_HZ, PHONE_PEAK_DB, PHONE_PEAK_Q, PHONE_LP = 280.0, 3000.0, 4.0, 0.7, 12000.0
MID_BANDS = (THIRD >= 1000) & (THIRD <= 2500)    # 0.9-2.8 kHz
AIR_BANDS = (THIRD >= 6300) & (THIRD <= 10000)   # 5.6-11.2 kHz
TOP_BANDS = THIRD >= 5000                        # 4.5-17.8 kHz


def _peaking_sos(f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def phone_sos():
    return np.vstack([signal.butter(4, PHONE_HP, "high", fs=SR, output="sos"),
                      _peaking_sos(PHONE_PEAK_HZ, PHONE_PEAK_DB, PHONE_PEAK_Q),
                      signal.butter(2, PHONE_LP, "low", fs=SR, output="sos")])


def phone_gain_db(freqs):
    _, h = signal.sosfreqz(phone_sos(), worN=np.asarray(freqs, dtype=float), fs=SR)
    return 20 * np.log10(np.abs(h) + 1e-12)


def _ratio_db(levels_db, num, den):
    e = 10 ** (np.asarray(levels_db) / 10)
    return float(10 * np.log10(e[num].sum() / e[den].sum()))


def phone_check(x, target=None, sections=None, win_s=3.0):
    """Small-speaker view of a mix or master (stereo (2, n) or mono). Returns a dict of numbers (see MANUAL.md)."""
    m = x.mean(0) if x.ndim == 2 else x
    p = signal.sosfilt(phone_sos(), m).astype(np.float32)
    tb = third_octave(p.astype(np.float64))
    r = dict(model=f"HP {PHONE_HP:.0f} Hz, +{PHONE_PEAK_DB:.0f} dB at {PHONE_PEAK_HZ / 1000:.0f} kHz, LP {PHONE_LP / 1000:.0f} kHz")
    r["air_6_12k_vs_mid_db"] = round(_ratio_db(tb, AIR_BANDS, MID_BANDS), 1)
    r["top_5_16k_vs_mid_db"] = round(_ratio_db(tb, TOP_BANDS, MID_BANDS), 1)
    air_t = None
    if target is not None:
        tc = target_curve(THIRD, target) + phone_gain_db(THIRD)
        air_t = _ratio_db(tc, AIR_BANDS, MID_BANDS)
        r["air_excess_db"] = round(r["air_6_12k_vs_mid_db"] - air_t, 1)
        r["top_excess_db"] = round(r["top_5_16k_vs_mid_db"] - _ratio_db(tc, TOP_BANDS, MID_BANDS), 1)
    # frame-wise: spectral flatness of 4-16 kHz (1 = white noise, 0 = pure tones; a single noise frame reads ~0.56)
    n, hop = 4096, 2048
    f, t, Z = signal.stft(p, SR, nperseg=n, noverlap=n - hop, boundary=None, padded=False)
    P = (np.abs(Z) ** 2).astype(np.float64)
    del Z
    fr_tot = P.sum(0)
    loud = fr_tot > np.percentile(fr_tot, 30)
    hb = (f >= 4000) & (f <= 16000)
    Ph = P[hb] + 1e-20
    flat = np.exp(np.log(Ph).mean(0)) / Ph.mean(0)
    wts = Ph.sum(0) * loud
    r["flatness_4_16k"] = round(float((flat * wts).sum() / (wts.sum() + 1e-20)), 2)
    # flatness drops for a steeply sloped noise as well as for tones; with the slope divided out (spectrum over its
    # own 31-bin moving average) it measures only the fine structure: 1 = as noise-like as white noise, 0 = tones
    Pw = Ph / (uniform_filter1d(Ph, 31, axis=0) + 1e-20)
    wfl = np.exp(np.log(Pw).mean(0)) / Pw.mean(0) / 0.58
    del Pw
    r["noise_likeness_4_16k"] = round(float((wfl * wts).sum() / (wts.sum() + 1e-20)), 2)

    def band_rows(mask_bands):
        lo = THIRD[mask_bands].min() / 2 ** (1 / 6)
        hi = THIRD[mask_bands].max() * 2 ** (1 / 6)
        return (f >= lo) & (f < hi)
    air_f, mid_f = band_rows(AIR_BANDS), band_rows(MID_BANDS)
    ea, em = P[air_f].sum(0), P[mid_f].sum(0)
    fps = SR / hop
    w = max(1, int(win_s * fps))
    ca, cm, ct = (np.concatenate([[0], np.cumsum(v)]) for v in (ea, em, fr_tot))
    cf = np.concatenate([[0], np.cumsum(flat * Ph.sum(0))]), np.concatenate([[0], np.cumsum(Ph.sum(0))])
    starts = np.arange(0, max(1, len(ea) - w + 1), max(1, int(fps)))
    wa, wm, wt = (c[starts + w] - c[starts] for c in (ca, cm, ct))
    wf = (cf[0][starts + w] - cf[0][starts]) / (cf[1][starts + w] - cf[1][starts] + 1e-20)
    ok = wt > wt.max() * 10 ** (-20 / 10)  # windows within 20 dB of the loudest
    ratio = 10 * np.log10((wa + 1e-20) / (wm + 1e-20))
    ref = air_t if air_t is not None else r["air_6_12k_vs_mid_db"]
    exc = np.where(ok, ratio - ref, -np.inf)
    i = int(np.argmax(exc))
    r["worst_window"] = dict(start_s=round(float(starts[i] * hop / SR), 1), air_vs_mid_db=round(float(ratio[i]), 1),
                             air_excess_db=round(float(exc[i]), 1) if air_t is not None else None,
                             flatness_4_16k=round(float(wf[i]), 2))
    if sections:
        rows = []
        for s in sections:
            a0, a1 = int(s["start"] * fps), int(s["end"] * fps)
            a1 = min(a1, len(ea))
            if a1 - a0 < 2:
                continue
            sa, sm_, st_ = ea[a0:a1].sum(), em[a0:a1].sum(), fr_tot[a0:a1].sum()
            hsum = Ph[:, a0:a1].sum(0)
            sf_ = float((flat[a0:a1] * hsum).sum() / (hsum.sum() + 1e-20))
            rv = 10 * np.log10((sa + 1e-20) / (sm_ + 1e-20))
            rows.append(dict(name=s["name"], start_s=round(float(s["start"]), 1),
                             level_db=round(float(10 * np.log10(st_ / max(1, a1 - a0) + 1e-20)), 1),
                             air_vs_mid_db=round(float(rv), 1),
                             air_excess_db=round(float(rv - air_t), 1) if air_t is not None else None,
                             flatness_4_16k=round(sf_, 2)))
        top = max(x_["level_db"] for x_ in rows) if rows else 0
        for x_ in rows:
            x_["level_db"] = round(x_["level_db"] - top, 1)
        r["sections"] = rows
    notes = []
    if air_t is not None and r["air_excess_db"] > 2:
        notes.append(f"top end {r['air_excess_db']:+.1f} dB above the target on a phone (6-12 kHz vs 1-2.8 kHz)")
    if air_t is not None and r["worst_window"]["air_excess_db"] > PHONE_WORST_NOTE_DB:
        ww = r["worst_window"]
        notes.append(f"loudest-hiss moment at {ww['start_s']} s: 6-12 kHz {ww['air_excess_db']:+.1f} dB above the target "
                     f"(flatness {ww['flatness_4_16k']})")
    if r["flatness_4_16k"] > PHONE_FLAT_NOTE:
        notes.append(f"4-16 kHz is mostly noise (flatness {r['flatness_4_16k']}): hats, rain or hiss dominate the top")
    r["notes"] = notes
    return r


PHONE_WORST_NOTE_DB = 6.0
PHONE_FLAT_NOTE = 0.35



def _dynamics(x, rep, meter, lufs, tp, translate):
    """Stages 3-7 (multiband, translation, glue, clip + limit, loudness). Returns the master and the
    pre-limiter signal. Shared by every master version."""
    # 3. multiband: ride the peaks only (thresholds set from each band's own level distribution)
    xo = [120.0, 600.0, 4000.0]
    bands = split_bands(x, xo)
    cfg = [("low <120", 3.0, 15, 160, 2.0), ("lowmid 120-600", 2.0, 20, 180, 3.0),
           ("mid 600-4k", 1.6, 15, 150, 4.0), ("high >4k", 2.5, 3, 80, 3.0)]
    out = np.zeros_like(x)
    rep["multiband"] = {}
    for b, (name, ratio, att, rel, headroom) in zip(bands, cfg):
        lv = 20 * np.log10(np.sqrt(np.maximum(uniform_filter1d((b ** 2).max(0), int(0.05 * SR))[::512], 0)) + 1e-9)
        lv = lv[lv > lv.max() - 40]
        thr = np.percentile(lv, 95) - headroom
        y, gr_mean, gr_max = compress(b, thr, ratio, att, rel)
        out += y
        rep["multiband"][name] = dict(threshold_db=round(float(thr), 1), ratio=ratio, gr_mean=round(gr_mean, 1), gr_max=round(gr_max, 1))
    del bands, b, y  # free the band copies before the oversampled stages
    x = out
    del out

    # 4. translation: harmonics from the bass body so small speakers imply the fundamental
    if translate > 0:
        bass = lin_lowpass(x.mean(0), 150, 8193)
        bass = bass - lin_lowpass(bass, 55, 8193)
        pk = np.abs(bass).max() + 1e-9
        harm = np.tanh(bass / pk * 4) * pk
        sos = signal.butter(4, [160, 700], "band", fs=SR, output="sos")
        harm = signal.sosfiltfilt(sos, harm)
        x = x + np.stack([harm, harm]) * translate * 0.35

    # 5. glue
    import pedalboard as pb
    lv = 20 * np.log10(np.sqrt(np.maximum(uniform_filter1d((x ** 2).max(0), int(0.05 * SR))[::512], 0)) + 1e-9)
    lv = lv[lv > lv.max() - 40]
    thr = float(np.percentile(lv, 85) - 1.0)
    x, gr_mean, gr_max = compress(x, thr, 2.0, 30, 200, knee=8)
    rep["glue"] = dict(threshold_db=round(thr, 1), gr_mean=round(gr_mean, 1), gr_max=round(gr_max, 1))

    # 6-7. solve drive so clip + true-peak limiter lands on the loudness target
    pre = x  # never modified below
    del x
    L0 = meter.integrated_loudness(pre.T)
    drive = lufs - L0
    y = None
    for it in range(6):
        del y
        y = pre * db(drive)
        y = soft_clip(y, tp + 0.5, 0.5)
        y, lim_gr = tp_limit(y, tp - 0.1)
        L = meter.integrated_loudness(y.T)
        if abs(L - lufs) < 0.15:
            break
        drive += lufs - L
    rep["limiter_max_gr_db"] = round(-lim_gr, 1)
    rep["drive_db"] = round(drive, 1)
    y = np.clip(y, -1, 1)
    over = true_peak_db(y) - tp
    if over > 0:  # safety: inter-sample overs recreated by the 4x down-sampling (only acts when over the ceiling)
        y = y * db(-over - 0.03)
        rep["tp_guard_db"] = round(-over - 0.03, 2)

    return y, pre


def master(x, lufs=-11.0, tp=-1.0, mono_below=120.0, eq_strength=0.7, translate=0.5, report=None, target="beat",
           genre=None, version=MASTER_VERSION, phone=True, max_low_boost=None):
    """version 1 reproduces the masters released before 2026-11-24 sample for sample; version 2 is the default."""
    rep = report if report is not None else {}
    rep["master_version"] = version
    rep["genre"] = genre
    rep["target"] = target
    rep["settings"] = dict(target=target, lufs=lufs, tp=tp, eq=eq_strength, translate=translate, mono_below=mono_below)
    if max_low_boost is not None:
        rep["settings"]["max_low_boost_db"] = max_low_boost
    if target in PROVENANCE:
        rep["target_provenance"] = PROVENANCE[target]
    meter = pyln.Meter(SR)
    rep["in"] = dict(lufs=round(meter.integrated_loudness(x.T), 1), true_peak=round(true_peak_db(x), 1))
    mid0 = x.mean(0)
    tb0 = third_octave(mid0)
    rep["in"]["tonal"] = [round(v, 1) for v in tb0]

    # 1. clean-up: sub-sonic HPF (steep) + mono low end via side-channel high-pass
    sos = signal.butter(8, 28, "high", fs=SR, output="sos")
    x = signal.sosfiltfilt(sos, x, axis=1)
    M, S = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
    S = S - lin_lowpass(S, mono_below, 8193)
    x = np.stack([M + S, M - S])

    tgt = target_curve(THIRD, target)
    if version == 1:
        # 2. tonal EQ toward target (relative shape only; level is handled later). Two passes, because
        #    a narrow 808 fundamental needs a second look after the broad correction.
        total = np.zeros(len(THIRD))
        for _pass in range(2):
            tb = third_octave(x.mean(0))
            dev = tb - tgt
            dev -= np.median(dev[(THIRD >= 200) & (THIRD <= 5000)])  # align on the midrange
            corr = -np.clip(dev * eq_strength, -6.0, 4.0)
            corr[THIRD >= 100] = np.convolve(np.pad(corr, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")[THIRD >= 100]
            corr = np.clip(total + corr, -8.0, 4.0) - total  # never more than -8/+4 dB in total per band
            if np.abs(corr).max() < 0.5:
                break
            total += corr
            fpts = np.concatenate([[0], THIRD, [SR / 2]])
            gpts = db(np.concatenate([[corr[0]], corr, [corr[-1]]]))
            h = signal.firwin2(16385, fpts, gpts, fs=SR)
            x = signal.fftconvolve(x, h[None, :], mode="same")
        rep["eq_db"] = {f"{int(f) if f >= 100 else f}": round(float(g), 1) for f, g in zip(THIRD, total) if abs(g) >= 0.5}
        y, pre = _dynamics(x, rep, meter, lufs, tp, translate)
    else:
        y, pre = _master_v2(x, rep, meter, tgt, lufs, tp, translate, eq_strength, max_low_boost)

    # 8. QC
    st = short_term_lufs(y, meter)
    mid = y.mean(0)
    tb1 = third_octave(mid)
    lowL = lin_lowpass(y, mono_below, 8193)
    corr_low = float(np.corrcoef(lowL[0], lowL[1])[0, 1])
    sos = signal.butter(4, 180, "high", fs=SR, output="sos")
    lap_in = signal.sosfilt(sos, x * 0 + pre, axis=1)
    lap = signal.sosfilt(sos, y, axis=1)
    Lfull = meter.integrated_loudness(y.T)
    # stereo width as integrated side minus mid loudness (LU; 0 = as wide as mono-compatible gets, lower = narrower)
    Lm = meter.integrated_loudness(((y[0] + y[1]) / 2)[:, None])
    Ls = meter.integrated_loudness(((y[0] - y[1]) / 2)[:, None])
    width = round(float(Ls - Lm), 1) if np.isfinite(Ls) and np.isfinite(Lm) else None
    rep["out"] = dict(width_side_minus_mid_lu=width,lufs=round(Lfull, 1), true_peak=round(true_peak_db(y), 2),
                      plr=round(true_peak_db(y) - Lfull, 1),
                      short_term_max=round(float(st.max()), 1) if len(st) else None,
                      loudness_range=round(float(np.percentile(st, 95) - np.percentile(st, 10)), 1) if len(st) else None,
                      low_end_corr=round(corr_low, 3),
                      laptop_loss_db=round(meter.integrated_loudness(lap.T) - Lfull, 1),
                      tonal=[round(v, 1) for v in tb1])
    rep["in"]["laptop_loss_db"] = round(meter.integrated_loudness(signal.sosfilt(sos, np.asarray(rep.get("_src")), axis=1).T) - rep["in"]["lufs"], 1) if rep.get("_src") is not None else None
    rep["tonal_dev_in"] = [round(float(a), 1) for a in (tb0 - target_curve(THIRD, target))]
    rep["tonal_dev_out"] = [round(float(a), 1) for a in (tb1 - target_curve(THIRD, target))]
    # the same deviations laid over the mix at its level around 1 kHz (mean of 500 Hz-2 kHz; version 2's reference),
    # so masters of either version compare on one scale; `top_end` is the 1-16 kHz part of it
    d_out = tb1 - target_curve(THIRD, target)
    off = ref_offset(d_out, 2)
    rep["tonal_ref_offset_db"] = round(off, 1)
    rep["tonal_dev_out_ref"] = [round(float(a - off), 1) for a in d_out]
    rep["top_end"] = {f"{int(f)}": round(float(a - off), 1) for f, a in zip(THIRD, d_out) if f >= 1000}
    rep["top_end_max_abs_dev_db"] = round(float(np.abs(d_out[CHECK_BANDS] - off).max()), 1)
    if phone:
        rep["phone"] = dict(out=phone_check(y, target))
        if rep.get("_src") is not None:
            rep["phone"]["in"] = phone_check(np.asarray(rep["_src"]), target)
    return y.astype(np.float32), rep


def picture(rep, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(11, 4.5))
    tgt = target_curve(THIRD, rep.get("target", "beat"))
    ax.semilogx(THIRD, tgt, "k--", lw=1.5, label=f"target ({rep.get('target', 'beat')}; genre {rep.get('genre')})")
    ax.semilogx(THIRD, rep["in"]["tonal"], color="tab:red", lw=1.2, label=f"premaster ({rep['in']['lufs']} LUFS)")
    ax.semilogx(THIRD, rep["out"]["tonal"], color="tab:blue", lw=1.8, label=f"master ({rep['out']['lufs']} LUFS, {rep['out']['true_peak']} dBTP)")
    if rep.get("tonal_ref_offset_db") is not None:
        ax.semilogx(THIRD, tgt + rep["tonal_ref_offset_db"], color="0.5", ls=":", lw=1.2,
                    label=f"target at the master's level around 1 kHz (master v{rep.get('master_version', 1)})")
    ax.axvspan(20, 150, color="0.9", zorder=0)
    ax.text(40, ax.get_ylim()[0] + 1, "laptop speakers\ncan't play this", fontsize=8, color="0.4")
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB rel. 1 kHz (1/3 octave)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both")
    ax.set_title("tonal balance: premaster vs master vs target", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("premaster")
    ap.add_argument("--genre", help="genre configuration from engine/genres.json (sets every setting below): "
                    + ", ".join(load_genres()))
    ap.add_argument("--target", choices=sorted(TARGETS),
                    help="tonal target curve (default: the genre's); beat is the trap curve; era targets (measured, "
                    "with provenance) are listed in engine/targets.json and docs/MASTERING.md")
    ap.add_argument("--published", action="store_true",
                    help="the genre's settings from before its era target (genres.json `master_published`): what its "
                    "already released tracks were mastered with")
    ap.add_argument("--lufs", type=float, help="integrated loudness target (default: the genre's)")
    ap.add_argument("--tp", type=float, help="true-peak ceiling dBTP (default: the genre's)")
    ap.add_argument("--mono-below", type=float)
    ap.add_argument("--eq", type=float, help="how strongly to move toward the tonal target (0-1)")
    ap.add_argument("--translate", type=float, help="bass harmonics for small speakers (0-1)")
    ap.add_argument("--master-version", type=int, choices=(1, 2), default=MASTER_VERSION,
                    help="mastering chain version (default %(default)s); 1 reproduces the masters released before 2026-11-24")
    ap.add_argument("--legacy-master", action="store_true", help="same as --master-version 1")
    ap.add_argument("--out")
    a = ap.parse_args()
    version = 1 if a.legacy_master else a.master_version
    genre, s = resolve_settings(a.genre, a.target, a.published, lufs=a.lufs, tp=a.tp, eq=a.eq, translate=a.translate,
                                mono_below=a.mono_below)
    print(f"genre {genre}: target {s['target']}, lufs {s['lufs']}, tp {s['tp']}, eq {s['eq']}, "
          f"translate {s['translate']}, mono below {s['mono_below']} Hz, master version {version}"
          + (f", low boosts capped at {s['max_low_boost_db']:+g} dB" if s.get("max_low_boost_db") is not None else ""))
    pv = PROVENANCE.get(s["target"])
    if pv:
        print(f"target {s['target']}: {pv.get('method')}; {pv.get('source')}"
              + (f"; era {pv['era']}" if pv.get("era") else "") + (f"; n {pv['n']}" if pv.get("n") else ""))
    pub = load_genres()[genre].get("master_published")
    if pub and not a.published:
        print(f"NOTE: genre {genre}'s default master changed on {pub.get('until')} (target {pub['target']} -> "
              f"{load_genres()[genre]['master']['target']}). Tracks released before that were mastered with "
              f"{pub['target']}; reproduce or compare with --published. Re-mastering a released track is the owner's "
              "call, track by track.")
    x, sr = sf.read(a.premaster, always_2d=True)
    assert sr == SR
    x = x.T.astype(np.float64)
    rep = {"_src": x}
    y, rep = master(x, s["lufs"], s["tp"], s["mono_below"], s["eq"], s["translate"], rep, s["target"], genre, version,
                    max_low_boost=s.get("max_low_boost_db"))
    if a.published:
        rep["settings_from"] = "master_published"
    rep.pop("_src", None)
    out = a.out or a.premaster.replace(".premaster.wav", ".master.wav")
    sf.write(out, y.T, SR, subtype="PCM_24")
    i, o = rep["in"], rep["out"]
    print(f"IN   {i['lufs']} LUFS  TP {i['true_peak']} dBTP  laptop loss {i.get('laptop_loss_db')} dB")
    print(f"OUT  {o['lufs']} LUFS  TP {o['true_peak']} dBTP  PLR {o['plr']}  LRA~{o['loudness_range']} LU  "
          f"short-term max {o['short_term_max']}  low-end L/R corr {o['low_end_corr']}  laptop loss {o['laptop_loss_db']} dB  "
          f"width (side-mid) {o['width_side_minus_mid_lu']} LU")
    print("tonal EQ moves (dB):", rep["eq_db"])
    cut_lim = {f"{int(f) if f >= 100 else f}": (V2_MAX_CUT[i] if version >= 2 else -8.0) for i, f in enumerate(THIRD)}
    at_limit = [k for k, v in rep["eq_db"].items() if v <= cut_lim[k] + 0.05 or v >= 3.95]
    rep["eq_at_limit"] = at_limit
    if at_limit:
        print("NOTE: tonal EQ at its limit (-8/+4 dB; -12 at 12.5-16 kHz in version 2) at", ", ".join(at_limit), "Hz: the mix and the target disagree there")
    for k, v in rep["multiband"].items():
        print(f"  multiband {k:16s} thr {v['threshold_db']:6.1f}  ratio {v['ratio']}  GR mean {v['gr_mean']} / max {v['gr_max']} dB")
    print(f"  glue GR mean {rep['glue']['gr_mean']} / max {rep['glue']['gr_max']} dB   limiter max GR {rep['limiter_max_gr_db']} dB")
    dev_o = np.array(rep["tonal_dev_out"])
    dev_o -= ref_offset(dev_o, version)
    worst = sorted(zip(THIRD, dev_o), key=lambda t: -abs(t[1]))[:4]
    print("largest remaining tonal deviations:", [(float(f), round(float(d), 1)) for f, d in worst])
    print(f"top end vs target (1-16 kHz, dB, at the mix's level around 1 kHz; max |dev| {rep['top_end_max_abs_dev_db']}):",
          rep["top_end"])
    if rep.get("closed_loop_max_dev_db"):
        print("closed loop, max |dev| 1-16 kHz per run:", rep["closed_loop_max_dev_db"])
    for k in ("in", "out"):
        ph = rep.get("phone", {}).get(k)
        if ph:
            ww = ph["worst_window"]
            print(f"PHONE {k:3s} 6-12k vs 1-3k {ph['air_6_12k_vs_mid_db']} dB ({ph.get("air_excess_db"):+} vs target)  "
                  f"5-16k {ph.get('top_excess_db'):+} dB vs target  flatness 4-16k {ph['flatness_4_16k']}  "
                  f"worst 3 s at {ww['start_s']} s: {ww['air_excess_db']:+} dB, flatness {ww['flatness_4_16k']}")
    for n_ in rep.get("phone", {}).get("out", {}).get("notes", []):
        print("PHONE NOTE:", n_)
    warns = []
    if o["true_peak"] > s["tp"] + 0.05:
        warns.append(f"true peak {o['true_peak']} above ceiling {s['tp']}")
    if rep["limiter_max_gr_db"] > 6:
        warns.append(f"limiter peaks at {rep['limiter_max_gr_db']} dB of reduction: mix too spiky or target too loud")
    if o["plr"] < 7:
        warns.append("PLR under 7 dB: heavily squashed")
    if o["low_end_corr"] < 0.95:
        warns.append("low end not mono")
    for w in warns:
        print("WARN:", w)
    rep["warnings"] = warns
    json.dump(rep, open(out.replace(".wav", ".report.json"), "w"), indent=1)
    picture(rep, out.replace(".wav", ".png"))
    print("wrote", out)


if __name__ == "__main__":
    main()
    if os.environ.get("MASTER_MEM"):
        print("peak memory", open("/proc/self/status").read().split("VmHWM:")[1].split("\n")[0].strip())
