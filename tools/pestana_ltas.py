"""Derive the measured mastering target curves (engine/master.py MEASURED) from Pestana et al. (2013).

Source: P. D. Pestana, Z. Ma, J. D. Reiss, A. Barbosa and D. A. A. Black, "Spectral Characteristics of Popular
Commercial Recordings 1950-2010", AES 135th Convention, New York, 2013, paper 8960. Fig. 5 ("Average spectra by
genre") is vector graphics in the authors' PDF, so the curves can be read exactly instead of digitised by eye.

  # get the PDF (the author's copy): https://joshreiss.github.io/documents/2013/Pestana%20Ma%20Reiss%20-%20AES135.pdf
  pdftocairo -svg -f 5 -l 5 pestana.pdf p5.svg
  python3 tools/pestana_ltas.py p5.svg

Method (see docs/MASTERING.md, "Measured targets"):
  1. Fig. 5's seven curves are SVG paths 772-804 (one group per legend entry, in legend order). Axis calibration
     comes from the figure's own grid: decade lines at 100 Hz / 1 kHz / 10 kHz, horizontal lines at -100..-30 dB.
  2. The curves are per-FFT-bin levels (4096-point FFT, ~10.8 Hz bins, mono L+R). A 1/3-octave band holds a
     number of bins proportional to its width, so band energy = sum over the band of 10^(dB/10) per Hz.
     (Check: the extracted per-bin slope at 100-4000 Hz is about -5 dB/octave, as the paper states.)
  3. Bands are normalised to the 1 kHz band and rounded to 0.5 dB. rock target = mean of the pop and rock curves.
"""
import re
import sys
import numpy as np

THIRD = [31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
         3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]
GROUPS = {"pop": range(772, 776), "rock": range(776, 780), "electronic": range(780, 785), "hiphop": range(785, 790),
          "jazz": range(790, 795), "folk": range(795, 800), "rnb": range(800, 805)}
GRID_Y = [265.867, 244.305, 223.184, 202.063, 180.941, 159.82, 138.258, 117.137]   # -100 .. -30 dB
X100, X10K = 381.98, 521.91                                                          # 100 Hz, 10 kHz


def curves(svg):
    paths = re.findall(r"<path([^>]*)/?>", svg)
    ky, cy = np.polyfit(GRID_Y, np.arange(-100, -29, 10), 1)
    dec = (X10K - X100) / 2
    out = {}
    for g, idx in GROUPS.items():
        pts = []
        for i in idx:
            p = paths[i]
            a, b, c, d, e, f = [float(v) for v in re.search(r'transform="matrix\(([^)]*)\)"', p).group(1).split(",")]
            nums = [float(v) for v in re.findall(r"-?[\d.]+(?:e-?\d+)?", re.search(r' d="([^"]*)"', p).group(1))]
            pts += [(a * x + c * y + e, b * x + d * y + f) for x, y in zip(nums[0::2], nums[1::2])]
        pts = np.array(pts)
        x, inv = np.unique(np.round(pts[:, 0], 3), return_inverse=True)   # average levels at duplicate x
        y = np.bincount(inv, pts[:, 1]) / np.bincount(inv)
        out[g] = (10 ** (2 + (x - X100) / dec), ky * y + cy)
    return out


def bands(freq, level):
    fg = np.arange(20, 20000, 1.0)
    dens = 10 ** (np.interp(np.log10(fg), np.log10(freq), level) / 10)
    e = np.array([10 * np.log10(dens[(fg >= c / 2 ** (1 / 6)) & (fg < c * 2 ** (1 / 6))].sum()) for c in THIRD])
    return e - e[THIRD.index(1000)]


def main():
    cv = curves(open(sys.argv[1]).read())
    b = {g: bands(*cv[g]) for g in cv}
    for g, (f, v) in cv.items():
        m = (f >= 100) & (f <= 4000)
        print(f"{g:10s} per-bin slope 100-4000 Hz: {np.polyfit(np.log2(f[m]), v[m], 1)[0]:.2f} dB/oct")
    targets = {"hiphop": b["hiphop"], "trance": b["electronic"], "rock": (b["pop"] + b["rock"]) / 2}
    print("raw 1/3-octave bands (dB re 1 kHz):", *THIRD)
    for g, v in b.items():
        print(f"{g:10s}", " ".join(f"{x:6.1f}" for x in v))
    for name, v in targets.items():
        r = np.round(v * 2) / 2
        print(f'"{name}": {{' + ", ".join(f"{(c if c < 100 else int(c))}: {x + 0.0}" for c, x in zip(THIRD, r)) + "},")


if __name__ == "__main__":
    main()
