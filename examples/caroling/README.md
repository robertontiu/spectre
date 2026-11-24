# Carol melody check

The two verified carol melodies of docs/CAROLING.md ("Verified melodies"), in engine notation on the 12-step carol grid, and the checks that verified them.

- `project.json`: piano, "It Came Upon the Midnight Clear" (tune CAROL, R. S. Willis 1850; B-flat, 6/8, 84 bpm = dotted quarter 56), then "The First Nowell" (traditional; Bramley & Stainer 1871; D, 3/4, 104 bpm). Rebuilt by `check/melodies.py`, which holds the melody strings.
- `carols-check.mp3`: its master (`studio.py master --genre caroling`; a bare piano line is nothing like a mix, so the tonal EQ sits at its limits).
- `check/check_midi.py`: the blocks against the soprano line of the Mutopia Project MIDI files (public domain; kept outside the repo in ~/.cache/spectre/refs/carols/, URLs and MD5s in the script and the doc): CAROL 65/66 (the one documented variant, line 1 "up-": C5 here, A4 in Mutopia), THE FIRST NOWELL 73/73.
- `check/check_render.py`: the engine render pitch-tracked with pYIN: 66/66 and 73/73 notes at the written pitch.

Rebuild: `python3 examples/caroling/check/melodies.py`, then `cd examples/caroling && export BEAT_DIR=$PWD && python3 ../../engine/studio.py render && python3 check/check_render.py`.
