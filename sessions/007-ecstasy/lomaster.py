#!/usr/bin/env python3
"""lomaster.py vNNN: the engine's release master (engine/master.py, --genre trance), unchanged in its math, but with
the three 4x-oversampled stages (true-peak meter, soft clipper, true-peak limiter) run in overlapping blocks so a
7-minute track fits in this sandbox's 6 GiB memory limit (the stock master.py peaks at ~1.2 GB per minute of audio and
is OOM-killed on an extended mix). Writes the same files as `studio.py master`: renders/vNNN.master.{wav,mp3,png,report.json}.
"""
import os, sys, subprocess
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "engine")
sys.path.insert(0, ENGINE)
import master as M  # noqa: E402

BLK = 1 << 20   # samples per block at 1x
PAD = 512       # overlap at 1x (resample_poly's filter is ~40 taps at 4x)


def _blocks(n):
    for a in range(0, n, BLK):
        b = min(n, a + BLK)
        a0, b0 = max(0, a - PAD), min(n, b + PAD)
        yield a, b, a0, b0


def true_peak_db(x):
    x = np.atleast_2d(x)
    n = x.shape[-1]
    pk = 0.0
    for a, b, a0, b0 in _blocks(n):
        up = signal.resample_poly(x[:, a0:b0], 4, 1, axis=-1)[:, 4 * (a - a0):4 * (a - a0) + 4 * (b - a)]
        pk = max(pk, float(np.abs(up).max()))
    return 20 * np.log10(pk + 1e-12)


def soft_clip(x, ceiling_db=-0.5, amount=0.5):
    n = x.shape[1]
    c = M.db(ceiling_db)
    knee = c * (1 - 0.35 * amount)
    out = np.empty_like(x)
    for a, b, a0, b0 in _blocks(n):
        up = signal.resample_poly(x[:, a0:b0], 4, 1, axis=1)
        aa = np.abs(up)
        over = aa > knee
        y = up.copy()
        y[over] = np.sign(up[over]) * (knee + (c - knee) * np.tanh((aa[over] - knee) / (c - knee)))
        dn = signal.resample_poly(y, 1, 4, axis=1)
        out[:, a:b] = dn[:, a - a0:a - a0 + (b - a)]
    return out


def tp_limit(x, ceiling_db, look_ms=1.5, release_ms=80):
    n = x.shape[1]
    SR = M.SR
    sr4 = SR * 4
    c = M.db(ceiling_db)
    need = np.empty(4 * n, dtype=np.float32)
    for a, b, a0, b0 in _blocks(n):
        up = signal.resample_poly(x[:, a0:b0], 4, 1, axis=1)[:, 4 * (a - a0):4 * (a - a0) + 4 * (b - a)]
        need[4 * a:4 * b] = np.minimum(1.0, c / (np.abs(up).max(0) + 1e-12))
    w = max(1, int(look_ms / 1000 * sr4))
    g = minimum_filter1d(need, 2 * w + 1)
    del need
    D = 64
    gd = g[::D].astype(np.float64)
    a_ = np.exp(-D / (release_ms / 1000 * sr4))
    cur = 1.0
    for i in range(len(gd)):
        v = gd[i]
        cur = v if v < cur else v + (cur - v) * a_
        gd[i] = cur
    g2 = np.minimum(np.repeat(gd.astype(np.float32), D)[:len(g)], g)
    del g
    g2 = uniform_filter1d(g2, w)
    out = np.empty_like(x)
    for a, b, a0, b0 in _blocks(n):
        up = signal.resample_poly(x[:, a0:b0], 4, 1, axis=1)
        dn = signal.resample_poly(up * g2[4 * a0:4 * b0], 1, 4, axis=1)
        out[:, a:b] = dn[:, a - a0:a - a0 + (b - a)]
    return out, float(20 * np.log10(float(g2.min()) + 1e-12))


# overlap-add convolution: the same result as fftconvolve (to float precision) without one giant FFT
_oa = signal.oaconvolve
signal.fftconvolve = lambda a, b, mode="full", axes=None: _oa(a, b, mode=mode, axes=axes)



def lean_master(x, lufs=-11.0, tp=-1.0, mono_below=120.0, eq_strength=0.7, translate=0.5, report=None, target="beat",
                genre=None):
    """engine/master.py master(), step for step, with intermediates freed as soon as they are used."""
    import gc
    if isinstance(x, list):  # handed over in a list so the caller holds no reference
        x = x.pop()
    db, SR, THIRD, third_octave, lin_lowpass, compress = M.db, M.SR, M.THIRD, M.third_octave, M.lin_lowpass, M.compress
    pyln = M.pyln
    rep = report if report is not None else {}
    rep["genre"] = genre
    rep["target"] = target
    rep["settings"] = dict(target=target, lufs=lufs, tp=tp, eq=eq_strength, translate=translate, mono_below=mono_below)
    meter = pyln.Meter(SR)
    rep["in"] = dict(lufs=round(meter.integrated_loudness(x.T), 1), true_peak=round(M.true_peak_db(x), 1))
    tb0 = third_octave(x.mean(0))
    rep["in"]["tonal"] = [round(v, 1) for v in tb0]
    sos180 = signal.butter(4, 180, "high", fs=SR, output="sos")
    src = rep.pop("_src", None)
    if src is x:
        src = None
        in_lap = round(meter.integrated_loudness(signal.sosfilt(sos180, x, axis=1).T) - rep["in"]["lufs"], 1)
    if src is not None:  # input laptop loss, computed now so the source can be freed
        in_lap = round(meter.integrated_loudness(signal.sosfilt(sos180, np.asarray(src), axis=1).T) - rep["in"]["lufs"], 1)
        del src
    # 1
    sos = signal.butter(8, 28, "high", fs=SR, output="sos")
    x = signal.sosfiltfilt(sos, x, axis=1)
    Mid, S = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2
    del x
    S = S - lin_lowpass(S, mono_below, 8193)
    x = np.stack([Mid + S, Mid - S])
    del Mid, S
    gc.collect()
    # 2
    tgt = M.target_curve(THIRD, target)
    total = np.zeros(len(THIRD))
    for _pass in range(2):
        tb = third_octave(x.mean(0))
        dev = tb - tgt
        dev -= np.median(dev[(THIRD >= 200) & (THIRD <= 5000)])
        corr = -np.clip(dev * eq_strength, -6.0, 4.0)
        corr[THIRD >= 100] = np.convolve(np.pad(corr, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")[THIRD >= 100]
        corr = np.clip(total + corr, -8.0, 4.0) - total
        if np.abs(corr).max() < 0.5:
            break
        total += corr
        fpts = np.concatenate([[0], THIRD, [SR / 2]])
        gpts = db(np.concatenate([[corr[0]], corr, [corr[-1]]]))
        h = signal.firwin2(16385, fpts, gpts, fs=SR)
        x = signal.fftconvolve(x, h[None, :], mode="same")
        gc.collect()
    rep["eq_db"] = {f"{int(f) if f >= 100 else f}": round(float(g), 1) for f, g in zip(THIRD, total) if abs(g) >= 0.5}
    # 3 (bands split and compressed one at a time; same complementary split)
    xo = [120.0, 600.0, 4000.0]
    cfg = [("low <120", 3.0, 15, 160, 2.0), ("lowmid 120-600", 2.0, 20, 180, 3.0),
           ("mid 600-4k", 1.6, 15, 150, 4.0), ("high >4k", 2.5, 3, 80, 3.0)]
    out = np.zeros_like(x)
    rep["multiband"] = {}
    rest = x
    for i, (name, ratio, att, rel, headroom) in enumerate(cfg):
        if i < len(xo):
            fc = xo[i]
            b = lin_lowpass(rest, fc, 8193 if fc < 200 else 4097)
            rest = rest - b
        else:
            b = rest
        lv = 20 * np.log10(np.sqrt(np.maximum(uniform_filter1d((b ** 2).max(0), int(0.05 * SR))[::512], 0)) + 1e-9)
        lv = lv[lv > lv.max() - 40]
        thr = np.percentile(lv, 95) - headroom
        y, gr_mean, gr_max = compress(b, thr, ratio, att, rel)
        out += y
        del y, b
        gc.collect()
        rep["multiband"][name] = dict(threshold_db=round(float(thr), 1), ratio=ratio, gr_mean=round(gr_mean, 1), gr_max=round(gr_max, 1))
    del rest
    x = out
    del out
    gc.collect()
    # 4
    if translate > 0:
        bass = lin_lowpass(x.mean(0), 150, 8193)
        bass = bass - lin_lowpass(bass, 55, 8193)
        pk = np.abs(bass).max() + 1e-9
        harm = np.tanh(bass / pk * 4) * pk
        del bass
        sos = signal.butter(4, [160, 700], "band", fs=SR, output="sos")
        harm = signal.sosfiltfilt(sos, harm)
        x = x + np.stack([harm, harm]) * translate * 0.35
        del harm
        gc.collect()
    # 5
    lv = 20 * np.log10(np.sqrt(np.maximum(uniform_filter1d((x ** 2).max(0), int(0.05 * SR))[::512], 0)) + 1e-9)
    lv = lv[lv > lv.max() - 40]
    thr = float(np.percentile(lv, 85) - 1.0)
    x, gr_mean, gr_max = compress(x, thr, 2.0, 30, 200, knee=8)
    rep["glue"] = dict(threshold_db=round(thr, 1), gr_mean=round(gr_mean, 1), gr_max=round(gr_max, 1))
    gc.collect()
    # 6-7
    pre = x
    del x
    L0 = meter.integrated_loudness(pre.T)
    drive = lufs - L0
    for it in range(6):
        y = pre * db(drive)
        y = M.soft_clip(y, tp + 0.5, 0.5)
        y, lim_gr = M.tp_limit(y, tp - 0.1)
        gc.collect()
        L = meter.integrated_loudness(y.T)
        if abs(L - lufs) < 0.15:
            break
        drive += lufs - L
        del y
    del pre
    gc.collect()
    rep["limiter_max_gr_db"] = round(-lim_gr, 1)
    rep["drive_db"] = round(drive, 1)
    y = np.clip(y, -1, 1)
    over = M.true_peak_db(y) - tp
    if over > 0:
        y = y * db(-over - 0.03)
        rep["tp_guard_db"] = round(-over - 0.03, 2)
    # 8
    st = M.short_term_lufs(y, meter)
    tb1 = third_octave(y.mean(0))
    lowL = lin_lowpass(y, mono_below, 8193)
    corr_low = float(np.corrcoef(lowL[0], lowL[1])[0, 1])
    del lowL
    lap = signal.sosfilt(sos180, y, axis=1)
    Lfull = meter.integrated_loudness(y.T)
    lap_loss = round(meter.integrated_loudness(lap.T) - Lfull, 1)
    del lap
    Lm = meter.integrated_loudness(((y[0] + y[1]) / 2)[:, None])
    Ls = meter.integrated_loudness(((y[0] - y[1]) / 2)[:, None])
    width = round(float(Ls - Lm), 1) if np.isfinite(Ls) and np.isfinite(Lm) else None
    tpk = M.true_peak_db(y)
    rep["out"] = dict(width_side_minus_mid_lu=width, lufs=round(Lfull, 1), true_peak=round(tpk, 2),
                      plr=round(tpk - Lfull, 1),
                      short_term_max=round(float(st.max()), 1) if len(st) else None,
                      loudness_range=round(float(np.percentile(st, 95) - np.percentile(st, 10)), 1) if len(st) else None,
                      low_end_corr=round(corr_low, 3),
                      laptop_loss_db=lap_loss,
                      tonal=[round(v, 1) for v in tb1])
    rep["in"]["laptop_loss_db"] = in_lap
    rep["tonal_dev_in"] = [round(float(a), 1) for a in (tb0 - M.target_curve(THIRD, target))]
    rep["tonal_dev_out"] = [round(float(a), 1) for a in (tb1 - M.target_curve(THIRD, target))]
    return y.astype(np.float32), rep

M.true_peak_db = true_peak_db
M.master = lean_master
M.soft_clip = soft_clip
M.tp_limit = tp_limit

def run(pre, lufs=None):
    import json
    s = M.resolve_settings("trance", None, lufs=lufs)[1]
    print(f"genre trance: target {s['target']}, lufs {s['lufs']}, tp {s['tp']}, eq {s['eq']}, "
          f"translate {s['translate']}, mono below {s['mono_below']} Hz (lean memory copy of master.py)")
    x, sr = M.sf.read(pre, always_2d=True)
    assert sr == M.SR
    hold = [x.T.astype(np.float64)]
    del x
    rep = {"_src": hold[0]}
    y, rep = lean_master(hold, s["lufs"], s["tp"], s["mono_below"], s["eq"], s["translate"], rep, s["target"], "trance")
    out = pre.replace(".premaster.wav", ".master.wav")
    M.sf.write(out, y.T, M.SR, subtype="PCM_24")
    i, o = rep["in"], rep["out"]
    print(f"IN   {i['lufs']} LUFS  TP {i['true_peak']} dBTP  laptop loss {i.get('laptop_loss_db')} dB")
    print(f"OUT  {o['lufs']} LUFS  TP {o['true_peak']} dBTP  PLR {o['plr']}  LRA~{o['loudness_range']} LU  "
          f"short-term max {o['short_term_max']}  low-end L/R corr {o['low_end_corr']}  laptop loss {o['laptop_loss_db']} dB  "
          f"width (side-mid) {o['width_side_minus_mid_lu']} LU")
    print("tonal EQ moves (dB):", rep["eq_db"])
    at_limit = [k for k, v in rep["eq_db"].items() if v <= -7.95 or v >= 3.95]
    rep["eq_at_limit"] = at_limit
    if at_limit:
        print("NOTE: tonal EQ at its limit (-8/+4 dB) at", ", ".join(at_limit), "Hz: the mix and the target disagree there")
    for k, v in rep["multiband"].items():
        print(f"  multiband {k:16s} thr {v['threshold_db']:6.1f}  ratio {v['ratio']}  GR mean {v['gr_mean']} / max {v['gr_max']} dB")
    print(f"  glue GR mean {rep['glue']['gr_mean']} / max {rep['glue']['gr_max']} dB   limiter max GR {rep['limiter_max_gr_db']} dB")
    dev_o = np.array(rep["tonal_dev_out"])
    dev_o -= np.median(dev_o[(M.THIRD >= 200) & (M.THIRD <= 5000)])
    worst = sorted(zip(M.THIRD, dev_o), key=lambda t: -abs(t[1]))[:4]
    print("largest remaining tonal deviations:", [(float(f), round(float(d), 1)) for f, d in worst])
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
    if "tp_guard_db" in rep:
        print("tp_guard_db", rep["tp_guard_db"])
    rep["warnings"] = warns
    json.dump(rep, open(out.replace(".wav", ".report.json"), "w"), indent=1)
    M.picture(rep, out.replace(".wav", ".png"))
    print("wrote", out)
    return out


if __name__ == "__main__":
    v = sys.argv[1]
    pre = v if v.endswith(".wav") else os.path.join(HERE, "renders", f"{v}.premaster.wav")
    lufs = float(sys.argv[sys.argv.index("--lufs") + 1]) if "--lufs" in sys.argv else None
    out = run(pre, lufs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-b:a", "320k", out.replace(".wav", ".mp3")], check=True)
    print("mp3:", out.replace(".wav", ".mp3"))
