# The dynamic master path: 015 "Again, Again" both ways

2026-11-26. Session 015's premaster went through `master.py --genre chamberscore` twice, at the same target (`chamberscore_ref`, -15 LUFS, -1 dBTP):

- **A**: `--dynamics normal`, the chain every master had until now: multiband peak riding, 2:1 glue and a soft clipper before the true-peak limiter. It is identical, sample for sample, to the HEAD master.
- **B**: `--dynamics keep`, the chamberscore default since 2026-11-26: no multiband, a light 1.5:1 glue from the loudest 5%, no clipper, and the true-peak limiter only.

Listen to [015-A-normal.mp3](015-A-normal.mp3) and [015-B-keep.mp3](015-B-keep.mp3). Each is 45 s (2:02-2:47: M4's quiet end into T's climax) at its mastered level. [dynamics.png](dynamics.png) shows the short-term loudness of both whole masters.

| | A normal | B keep |
|---|---|---|
| Essentia dynamic complexity (whole master) | 3.92 (the released MP3: 3.96) | **4.77** |
| LRA (report) | 8.2 LU | **10.6 LU** |
| short-term loudness, 95th minus 10th percentile | 8.2 dB | **10.6 dB** |
| short-term range inside the excerpt | 10.6 dB | **13.8 dB** |
| integrated / PLR / true peak | -15.0 / 13.9 / -1.08 dBTP | -15.0 / 13.9 / -1.09 dBTP |
| short-term max | -11.2 | -9.7 |
| glue gain reduction, mean / max | 0.8 / 4.1 dB | 0.4 / 2.6 dB |
| limiter, max gain reduction | 0.6 dB | 6.2 dB (on the loudest transients; the clipper did that work in A) |

The quiet passages stay quiet and the climax comes up, but the dynamic complexity (4.77) is still under the 5.6-6.8 of chamber-score records. As the research expected, the rest has to come from the arrangement, not the master.

Rebuild:

1. Render `sessions/015-childhood/project-published.json`.
2. Run `engine/master.py renders/v001.premaster.wav --genre chamberscore --dynamics normal --out .../m_normal.master.wav`, then the same with `keep`.
3. Run `python3 examples/production/dynamics/build.py m_normal.master.wav m_keep.master.wav renders/v001.meta.json 122`.
