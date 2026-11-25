"""Section loudness contour of a remix master against the published master, and (unless --contour-only) the
delivery files: loudness-matched A/B excerpts of the peak section(s) (ab-published.mp3, ab-remix.mp3) and
remix-candidate.mp3 = renders/<vNNN>.master.mp3, all in the session folder.

Each section's loudness is its integrated LUFS relative to the whole track's; the remix brief's guide is a change of
at most about 1 LU per section (argue anything larger in the journal).

usage: python3 deliver.py <session dir> <published mp3> <vNNN> <section[,section...]> [--contour-only]
"""
import json
import shutil
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln

SR = 44100


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    contour_only = "--contour-only" in sys.argv
    sd, pub, v, sec = args[:4]
    meta = json.load(open(f"{sd}/renders/{v}.meta.json"))
    m = pyln.Meter(SR)
    A, B = load(f"{sd}/{pub}"), load(f"{sd}/renders/{v}.master.mp3")
    IA, IB = m.integrated_loudness(A), m.integrated_loudness(B)
    print(f"integrated: published {IA:.1f}, remix {IB:.1f} LUFS")
    print(f"{'section':10s} {'pub rel':>8s} {'remix rel':>9s} {'diff':>6s}")
    mx = 0.0
    for s in meta["sections"]:
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        if b - a < SR:
            continue
        la = m.integrated_loudness(A[a:b]) - IA
        lb = m.integrated_loudness(B[a:b]) - IB
        mx = max(mx, abs(lb - la))
        print(f"{s['name']:10s} {la:+8.1f} {lb:+9.1f} {lb - la:+6.1f}" + ("   > 1 LU" if abs(lb - la) > 1.0 else ""))
    print(f"max contour change {mx:.1f} LU")
    if contour_only:
        return
    names = sec.split(",")
    ss = [x for x in meta["sections"] if x["name"] in names]
    if not ss:
        raise SystemExit(f"no section {sec!r}")
    a, b = int(ss[0]["start"] * SR), int(ss[-1]["end"] * SR)
    ea, eb = A[a:b], B[a:b]
    la, lb = m.integrated_loudness(ea), m.integrated_loudness(eb)
    tgt = min(la, lb)  # turn the louder one down; never up (no clipping)
    for name, x, lv in (("ab-published", ea, la), ("ab-remix", eb, lb)):
        y = (x * 10 ** ((tgt - lv) / 20)).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-b:a", "256k", f"{sd}/{name}.mp3"], input=y.tobytes(), check=True)
    print(f"A/B excerpt {sec} {ss[0]['start']:.1f}-{ss[-1]['end']:.1f} s, both at {tgt:.1f} LUFS "
          f"(published {la:.1f}, remix {lb:.1f})")
    shutil.copy(f"{sd}/renders/{v}.master.mp3", f"{sd}/remix-candidate.mp3")
    print(f"remix-candidate.mp3 = renders/{v}.master.mp3")


if __name__ == "__main__":
    main()
