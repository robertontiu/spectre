#!/usr/bin/env python3
"""remix_check.py: the remix lane's measurements (2026-11-25). Run from a session folder.

  events  vOLD vNEW                   every original track's events (time, velocity, pitch) identical?
  contour OLD.mp3 NEW.mp3 vNEW        per-section loudness relative to the track, old against new
  target  FILE.mp3 TARGET [t0 t1]     a master (or a part of it) against a target curve, laid over at 500 Hz-2 kHz
  ab      OLD.mp3 NEW.mp3 t0 t1 [LUFS]  loudness-matched excerpts -> ab-published.mp3 / ab-remix.mp3
"""
import sys, os, json, subprocess
import numpy as np
sys.path.insert(0, "/home/claude/spectre/engine")
SR = 44100


def load(path, t0=None, t1=None):
    cmd = ["ffmpeg", "-loglevel", "error"]
    if t0 is not None:
        cmd += ["-ss", str(t0), "-t", str(t1 - t0)]
    raw = subprocess.run(cmd + ["-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True,
                         check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def lufs(x):
    import pyloudnorm as pyln
    try:
        return pyln.Meter(SR, block_size=0.4).integrated_loudness(x)
    except Exception:
        return float("nan")


def events(a, b):
    A = json.load(open(f"renders/{a}.meta.json"))["events"]; B = json.load(open(f"renders/{b}.meta.json"))["events"]
    ok = True
    for k in A:
        same = k in B and A[k] == B[k]
        ok &= same
        if not same:
            print("  DIFFERENT:", k, len(A[k]), len(B.get(k, [])))
    extra = [k for k in B if k not in A]
    print(f"events {a} vs {b}: {len(A)} original tracks, {'all identical' if ok else 'MISMATCH'}; new tracks: {extra}")
    return ok


def contour(old, new, v):
    S = json.load(open(f"renders/{v}.meta.json"))["sections"]
    xo, xn = load(old), load(new)
    lo, ln = lufs(xo), lufs(xn)
    print(f"integrated: old {lo:.1f}  new {ln:.1f} LUFS")
    worst = 0
    for s in S:
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        if b - a < SR:      # under 1 s: extend
            b = a + SR
        o, n = lufs(xo[a:b]) - lo, lufs(xn[a:b]) - ln
        d = n - o
        if np.isfinite(d):
            worst = max(worst, abs(d))
        print("  %-12s old %+6.1f  new %+6.1f  diff %+5.1f %s" % (s["name"], o, n, d, "<--" if abs(d) > 1 else ""))
    print("largest difference %.1f LU" % worst)


def target(path, tgt, t0=None, t1=None):
    import master as MA
    lv = MA.third_octave(load(path, t0, t1).mean(1))
    lv = np.asarray(lv, dtype=float)
    cur = MA.target_curve(MA.THIRD, tgt)
    dev = lv - cur
    dev -= dev[MA.REF_BANDS].mean()
    T = MA.THIRD
    def band(lo, hi):
        m = (T >= lo) & (T <= hi)
        return dev[m].mean()
    groups = [("50-80", 50, 80), ("100-250", 100, 250), ("315-400", 315, 400), ("2-5k", 2000, 5000), ("8-12.5k", 8000, 12500)]
    print(os.path.basename(path), "vs", tgt, " ".join("%s %+.1f" % (n, band(a, b)) for n, a, b in groups))
    print("   per third:", " ".join("%g:%+.1f" % (f, d) for f, d in zip(T, dev)))
    return dev


def ab(old, new, t0, t1, level=-12.0):
    for src, out in ((old, "ab-published.mp3"), (new, "ab-remix.mp3")):
        x = load(src, t0, t1)
        g = 10 ** ((level - lufs(x)) / 20)
        y = x * g
        n = int(0.03 * SR); r = np.linspace(0, 1, n)[:, None]
        y[:n] *= r; y[-n:] *= r[::-1]
        pk = np.abs(y).max()
        p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                              "-b:a", "320k", out], stdin=subprocess.PIPE)
        p.communicate(y.astype(np.float32).tobytes())
        print(f"{out}: {t0:.1f}-{t1:.1f} s at {lufs(y):.1f} LUFS (gain {20*np.log10(g):+.1f} dB, peak {20*np.log10(pk):.1f} dBFS)")


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    if c == "events": sys.exit(0 if events(*a) else 1)
    elif c == "contour": contour(*a)
    elif c == "target": target(a[0], a[1], *(float(v) for v in a[2:]))
    elif c == "ab": ab(a[0], a[1], float(a[2]), float(a[3]), *(float(v) for v in a[4:]))
