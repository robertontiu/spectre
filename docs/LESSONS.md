# Lessons log

What each session taught us. Read this before changing the producer prompt or the engine, and add an entry after every session.

## Session 001: "Bleachers" (blind, hidden feeling: defiance)
- **Outcome:** the listener guessed *longing* (and said defiance was his second thought, but "it didn't feel aggressive enough"). A near miss.
- **Why:** the core idea was "minor melodies that climb back up every time the chords pull them down". The producer meant it as refusal, but upward-reaching minor melodies are the textbook shape of yearning. The bridge's strings sinking by half-steps pushed further toward ache. The synthesized brass and organ lacked bite.
- **Lesson 1:** attitude lives in the sound (distortion, roughness, hard transients, density), not only in the notes. The ears can verify structure but not attitude.
- **Lesson 2:** at every stage, ask what the nearest wrong feeling is and what separates the two.
- **Lesson 3 (mix and master):** the 808 fundamental sat about 17 dB above the midrange; on MacBook speakers this sounded "clunky". This led to the mastering stage (`docs/MASTERING.md`) and the rule "get weight from saturation and mids, not sub; if the master has to cut near 8 dB, fix the mix."
- **Engine changes after this session:** premaster export, `master.py`, the `master` CLI command, manual updates.

## Session 002: "Lid Off" (briefed: rage, high tempo, aggressive)
- **Result:** 2:51, 160 bpm, E Phrygian with a flat 5, lifting a semitone for the last hook. Rage-trap crossed with industrial. Mastered at -10.1 LUFS, -1.04 dBTP, laptop loss -2.1 dB, no warnings.
- **What worked:** the "nearest wrong feeling" check from 001 drove most decisions. The producer removed elements that told the wrong story: a hissing snare tail read as anxiety, a riser read as festival hype, a half-time verse went cold like menace until a muted chug went under it. Hard cuts (an eighth of silence before the slam) replaced risers.
- **Low end:** the first trial master showed a +16 dB spike at 50 Hz because a kick tuned to 52 Hz was fighting the 808. Moving the kick to 62 Hz, notching the 808 and sidechaining it fixed this in the mix, so the final master's EQ moves stayed under 4.5 dB. Mastering as a feedback loop works.
- **Engine fix after this session:** hits pushed before 0:00 (negative `push_ms` on step 0) used to be dropped; they now play at 0:00. Added `engine/solos.sh` (the producer's own per-track level helper).
