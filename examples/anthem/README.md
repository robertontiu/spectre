# Anthem melody check: "Deșteaptă-te, române!"

The verified melody of Romania's national anthem (melody attributed to Anton Pann, 1839; words Andrei Mureșanu, 1848; both public domain), checked on 2026-11-24 for Session 011. The transcription, the sources and how it was verified are in `docs/ROMANIAN.md`, "Anthem" > "Verified melody". This folder holds the material behind it.

- `project.json`: a tiny engine project that plays the verified melody (G minor, engine notation from the doc) on `piano` at 104 bpm: pickup + period a + period b (second ending). Render it in a scratch folder: `mkdir -p /tmp/anthem && cp project.json /tmp/anthem/ && cd /tmp/anthem && BEAT_DIR=$PWD python3 <repo>/engine/studio.py render`.
- `anthem-check.mp3`: that render (v001), mono 64 kbps.
- `cantorion-3849-desteapta-te-romane.pdf`: the readable score used for the transcription (E minor, voice and piano). **Licence: Creative Commons Attribution-ShareAlike 3.0** (https://creativecommons.org/licenses/by-sa/3.0/), not the repository's MIT licence. Typeset by Johan Schoone; from cantorion.org, score no. 3849 (https://cantorion.org/music/3849/). Unmodified.
- `check/`: the scripts used to verify it (need librosa; run Python with `-I` on downloaded files).
  - `melody.py`: the transcription as data (E minor, the key of the official annex and the score; the doc transposes it to G minor).
  - `midi_dump.py`: a minimal MIDI parser; `check_midi.py file.mid track`: are the melody notes in a MIDI at the right pitch and onset (the anchor is set for the MIDI named in the doc).
  - `verify_beats.py recording transpose_from_E --stanzas N --bpm B`: tracks the recording's beats, lays the melody on them and compares the energy at each expected pitch with its semitone neighbours (with `--shuffle SEED` as a control, `--seq notes.json --seq-transpose N` to test a render's tracked notes instead).
  - `check_render.py render.wav bpm out.json`: pitch-tracks a render of `project.json` and compares it with the transcription.

The MIDI file and the recording used in the check are not in the repo (see the doc for their sources and licences).
