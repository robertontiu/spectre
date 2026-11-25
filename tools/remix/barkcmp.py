"""Read masters in Bark bands against a catalogue target's median (default hiphop_2015), plus the target curves
themselves read through the same analysis. Levels are relative to 510 Hz-2 kHz (tools/refcurve.py); the last column
is the mean |gap| from 32 Hz to 15.5 kHz, the number used to choose between targets.

usage: python3 barkcmp.py [--against hiphop_2015] [--curves hiphop_2015,beat,hiphop] file.mp3 [file ...]
"""
import argparse
import os
import subprocess
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "engine"))
import refcurve as R  # noqa: E402

GROUPS = [("<32", [0]), ("32-97", [1]), ("97-140", [2]), ("140-183", [3]), ("183-291", [4]), ("291-506", [5, 6]),
          ("2.3-6.4k", [16, 17, 18, 19, 20, 21]), ("6.4-7.7k", [22]), ("7.7-9.5k", [23]), ("9.5-12k", [24]),
          ("12-15.5k", [25])]


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", "44100", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--against", default="hiphop_2015", help="catalogue target name (engine/targets.json) or file")
    ap.add_argument("--curves", default="hiphop_2015,beat,hiphop", help="target curves to list too ('' for none)")
    a = ap.parse_args()
    med = R.catalogue_median(a.against)

    def line(label, rel):
        cells = " ".join(f"{float(np.mean(rel[i]) - np.mean(med[i])):+8.1f}" for _, i in GROUPS)
        print(f"{label[-42:]:42s} {cells}   {np.abs(rel - med)[1:26].mean():.2f}")

    print(f"against {a.against} median (dB)")
    print(f"{'file':42s} " + " ".join(f"{g:>8s}" for g, _ in GROUPS) + "   mean|d| 32-15.5k")
    for name in filter(None, a.curves.split(",")):
        anchors, _ = R.load_curve(name)
        line("curve " + name, R.rel_ref(R.bark_of_curve(anchors)))
    for p in a.files:
        line(p, R.rel_ref(R.bark_of_audio(load(p))))


if __name__ == "__main__":
    main()
