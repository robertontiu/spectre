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

  python3 master.py renders/v027.premaster.wav [--lufs -11] [--tp -1.0] [--out renders/v027.master.wav]
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


# Genre targets (hand-tuned, not measured from references; see docs/MASTERING.md). Only the shape matters:
# the EQ aligns each curve to the mix on 200 Hz-5 kHz.
# trance: a short club kick and rolling bass instead of a sustained 808, so less sub at 31-40 Hz; dense bright
#         supersaws, hats and long reverbs, so the top falls more slowly.
# rock:   kick and bass guitar live at 60-250 Hz, little true sub; guitars fill 200 Hz-5 kHz; cymbals keep the top open.
TARGETS = {
    "beat": TARGET_ANCHORS,
    "trance": {31.5: -4.0, 40: 1.5, 50: 5.0, 63: 5.5, 80: 5.0, 100: 4.0, 160: 2.0, 250: 1.0, 500: 0.5,
               1000: 0.0, 2000: -1.5, 4000: -3.5, 8000: -6.5, 12500: -9.5, 16000: -13.0},
    "rock": {31.5: -7.0, 40: -3.0, 50: 0.5, 63: 2.5, 80: 3.5, 100: 3.5, 160: 3.0, 250: 2.0, 500: 1.0,
             1000: 0.0, 2000: -1.0, 4000: -3.5, 8000: -7.0, 12500: -10.5, 16000: -15.0},
}


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
    up = signal.resample_poly(x, 4, 1, axis=-1)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


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


def tp_limit(x, ceiling_db, look_ms=1.5, release_ms=80):
    """True-peak limiter: detect and apply gain at 4x, then return to SR."""
    up = signal.resample_poly(x, 4, 1, axis=1)
    sr4 = SR * 4
    c = db(ceiling_db)
    need = np.minimum(1.0, c / (np.abs(up).max(0) + 1e-12))
    w = max(1, int(look_ms / 1000 * sr4))
    g = minimum_filter1d(need, 2 * w + 1)
    D = 64
    gd = g[::D].copy()
    a = np.exp(-D / (release_ms / 1000 * sr4))
    cur = 1.0
    for i in range(len(gd)):
        v = gd[i]
        cur = v if v < cur else v + (cur - v) * a
        gd[i] = cur
    g2 = np.minimum(np.repeat(gd, D)[:len(g)], g)
    g2 = uniform_filter1d(g2, w)
    y = signal.resample_poly(up * g2, 1, 4, axis=1)[:, :x.shape[1]]
    return y, float(20 * np.log10(g2.min() + 1e-12))


def soft_clip(x, ceiling_db=-0.5, amount=0.5):
    """Gentle oversampled clipper that shaves the top few dB of transients."""
    up = signal.resample_poly(x, 4, 1, axis=1)
    c = db(ceiling_db)
    knee = c * (1 - 0.35 * amount)
    a = np.abs(up)
    over = a > knee
    y = up.copy()
    y[over] = np.sign(up[over]) * (knee + (c - knee) * np.tanh((a[over] - knee) / (c - knee)))
    return signal.resample_poly(y, 1, 4, axis=1)[:, :x.shape[1]]


def master(x, lufs=-11.0, tp=-1.0, mono_below=120.0, eq_strength=0.7, translate=0.5, report=None, target="beat"):
    rep = report if report is not None else {}
    rep["target"] = target
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

    # 2. tonal EQ toward target (relative shape only; level is handled later). Two passes, because
    #    a narrow 808 fundamental needs a second look after the broad correction.
    tgt = target_curve(THIRD, target)
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
    x = out

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
    pre = x.copy()
    L0 = meter.integrated_loudness(pre.T)
    drive = lufs - L0
    for it in range(6):
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
    rep["out"] = dict(lufs=round(Lfull, 1), true_peak=round(true_peak_db(y), 2),
                      plr=round(true_peak_db(y) - Lfull, 1),
                      short_term_max=round(float(st.max()), 1) if len(st) else None,
                      loudness_range=round(float(np.percentile(st, 95) - np.percentile(st, 10)), 1) if len(st) else None,
                      low_end_corr=round(corr_low, 3),
                      laptop_loss_db=round(meter.integrated_loudness(lap.T) - Lfull, 1),
                      tonal=[round(v, 1) for v in tb1])
    rep["in"]["laptop_loss_db"] = round(meter.integrated_loudness(signal.sosfilt(sos, np.asarray(rep.get("_src")), axis=1).T) - rep["in"]["lufs"], 1) if rep.get("_src") is not None else None
    rep["tonal_dev_in"] = [round(float(a), 1) for a in (tb0 - target_curve(THIRD, target))]
    rep["tonal_dev_out"] = [round(float(a), 1) for a in (tb1 - target_curve(THIRD, target))]
    return y.astype(np.float32), rep


def picture(rep, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(11, 4.5))
    tgt = target_curve(THIRD, rep.get("target", "beat"))
    ax.semilogx(THIRD, tgt, "k--", lw=1.5, label=f"target ({rep.get('target', 'beat')})")
    ax.semilogx(THIRD, rep["in"]["tonal"], color="tab:red", lw=1.2, label=f"premaster ({rep['in']['lufs']} LUFS)")
    ax.semilogx(THIRD, rep["out"]["tonal"], color="tab:blue", lw=1.8, label=f"master ({rep['out']['lufs']} LUFS, {rep['out']['true_peak']} dBTP)")
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
    ap.add_argument("--lufs", type=float, default=-11.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--mono-below", type=float, default=120.0)
    ap.add_argument("--eq", type=float, default=0.7, help="how strongly to move toward the tonal target (0-1)")
    ap.add_argument("--translate", type=float, default=0.5, help="bass harmonics for small speakers (0-1)")
    ap.add_argument("--target", default="beat", choices=sorted(TARGETS),
                    help="tonal target curve: beat (808 beats, default), trance, rock")
    ap.add_argument("--out")
    a = ap.parse_args()
    x, sr = sf.read(a.premaster, always_2d=True)
    assert sr == SR
    x = x.T.astype(np.float64)
    rep = {"_src": x}
    y, rep = master(x, a.lufs, a.tp, a.mono_below, a.eq, a.translate, rep, a.target)
    rep.pop("_src", None)
    out = a.out or a.premaster.replace(".premaster.wav", ".master.wav")
    sf.write(out, y.T, SR, subtype="PCM_24")
    json.dump(rep, open(out.replace(".wav", ".report.json"), "w"), indent=1)
    picture(rep, out.replace(".wav", ".png"))
    i, o = rep["in"], rep["out"]
    print(f"IN   {i['lufs']} LUFS  TP {i['true_peak']} dBTP  laptop loss {i.get('laptop_loss_db')} dB")
    print(f"OUT  {o['lufs']} LUFS  TP {o['true_peak']} dBTP  PLR {o['plr']}  LRA~{o['loudness_range']} LU  "
          f"short-term max {o['short_term_max']}  low-end L/R corr {o['low_end_corr']}  laptop loss {o['laptop_loss_db']} dB")
    print("tonal EQ moves (dB):", rep["eq_db"])
    for k, v in rep["multiband"].items():
        print(f"  multiband {k:16s} thr {v['threshold_db']:6.1f}  ratio {v['ratio']}  GR mean {v['gr_mean']} / max {v['gr_max']} dB")
    print(f"  glue GR mean {rep['glue']['gr_mean']} / max {rep['glue']['gr_max']} dB   limiter max GR {rep['limiter_max_gr_db']} dB")
    dev_o = np.array(rep["tonal_dev_out"])
    dev_o -= np.median(dev_o[(THIRD >= 200) & (THIRD <= 5000)])
    worst = sorted(zip(THIRD, dev_o), key=lambda t: -abs(t[1]))[:4]
    print("largest remaining tonal deviations:", [(f, round(d, 1)) for f, d in worst])
    warns = []
    if o["true_peak"] > a.tp + 0.05:
        warns.append(f"true peak {o['true_peak']} above ceiling {a.tp}")
    if rep["limiter_max_gr_db"] > 6:
        warns.append(f"limiter peaks at {rep['limiter_max_gr_db']} dB of reduction: mix too spiky or target too loud")
    if o["plr"] < 7:
        warns.append("PLR under 7 dB: heavily squashed")
    if o["low_end_corr"] < 0.95:
        warns.append("low end not mono")
    for w in warns:
        print("WARN:", w)
    print("wrote", out)


if __name__ == "__main__":
    main()
