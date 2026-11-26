#!/usr/bin/env python3
"""A/B of the dynamic mastering path (`dynamics` keep, 2026-11-26; docs/MASTERING.md "Dynamics") on session 015
"Again, Again": the same premaster through `master.py --genre chamberscore` with `--dynamics normal` (the glue,
multiband and soft clipper every master had) and `--dynamics keep` (the chamberscore default since 2026-11-26),
same target, loudness and true peak. Writes a 45 s excerpt of each (mp3) and the short-term loudness of both whole
masters (dynamics.png).

    python3 examples/production/dynamics/build.py <normal.master.wav> <keep.master.wav> <meta.json> [start_s]

The masters come from a render of sessions/015-childhood/project-published.json (sessions/ is local; restore it with
`tools/upload_track.py --fetch`) mastered twice; see README.md for the commands and numbers."""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "engine"))
import master as M  # noqa: E402
import pyloudnorm as pyln  # noqa: E402

SR = 44100


def main():
    a, b, meta = sys.argv[1:4]
    t0 = float(sys.argv[4]) if len(sys.argv) > 4 else None
    secs = json.load(open(meta))["sections"]
    xs = [sf.read(p)[0].T for p in (a, b)]
    m = pyln.Meter(SR)
    st = [M.short_term_lufs(x, m) for x in xs]
    if t0 is None:  # the 45 s where the two differ most in loudness movement
        d = np.abs(np.diff(st[1])) - np.abs(np.diff(st[0]))
        k = int(np.argmax(np.convolve(d, np.ones(40), mode="valid")))
        t0 = float(k)
    for x, name in zip(xs, ("A-normal", "B-keep")):
        seg = x[:, int(t0 * SR):int((t0 + 45) * SR)].copy()
        fo = int(0.5 * SR)
        seg[:, :fo] *= np.linspace(0, 1, fo)
        seg[:, -fo:] *= np.linspace(1, 0, fo)
        with tempfile.TemporaryDirectory() as td:
            w = os.path.join(td, "x.wav")
            sf.write(w, seg.T, SR, subtype="PCM_16")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", w, "-b:a", "192k",
                            os.path.join(HERE, f"015-{name}.mp3")], check=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 3.6))
    for v, lab in zip(st, ("A: dynamics normal (glue, multiband, clipper)", "B: dynamics keep (light glue, limiter only)")):
        ax.plot(np.arange(len(v)), v, label=lab)
    for S in secs:
        ax.axvline(S["start"], color="0.85", lw=0.8)
        ax.text(S["start"], ax.get_ylim()[1] if False else -8.5, S["name"], fontsize=6, rotation=90, va="top")
    ax.axvspan(t0, t0 + 45, color="0.9", zorder=0, label="excerpt")
    ax.set_xlabel("s")
    ax.set_ylabel("short-term LUFS (3 s)")
    ax.set_ylim(-35, -8)
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "dynamics.png"), dpi=70)
    print("excerpt start", t0)


if __name__ == "__main__":
    main()
