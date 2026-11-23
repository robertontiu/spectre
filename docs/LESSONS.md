# Lessons log

What each session taught us. Read this before changing the producer prompt or the engine, and add an entry after every session. **After every genre switch, update the "Across genres" section too.**

## Across genres (updated after each switch)
Genres so far: boom-bap/trap hybrid (001), rage-trap/industrial (002), oriental trap (003), Romanian folk trap (004, running), Ukrainian folk trap (005, running).
- **What transfers everywhere:** the feel-listen-decide loop; naming the nearest wrong feelings in the brief; subtraction (drop-outs, sections where the beat leaves) as the strongest emotional tool; mixing low end before mastering; one session folder plus journal so a session can be resumed by a fresh agent.
- **Folk-fusion genres need three things before the session starts:** (1) research saved as a `docs/<GENRE>.md` brief (instruments, rhythms, modes, the modern reference artists), (2) the genre's signature instruments built and checked in the engine (generic synths can't fake them), (3) a warning against "postcard" use: the folk elements must carry the feeling, not decorate it. Session 003 showed it works: the listener's favourite moments were the oud and darbuka sitting inside the beat.
- **Each genre has its own trap:** briefed rage drifted toward hype and anxiety; rebellion toward triumph; the hustle toward celebration or nostalgia; anti-war toward a battle anthem. Name the trap in the brief.
- **Shared modes:** Ukrainian Dorian, Romanian minor and the klezmer "Misheberak" scale are the same Dorian #4; Hijaz / Phrygian dominant links oriental, Romanian and Ukrainian material. The key detector in the ears misreads these modes; ignore it there.

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

## Session 003: "Throw It Back" (briefed: oriental trap, rebellion)
- **Result:** 2:48, 140 bpm half-time, D Hijaz. Call and response (an oud or ney call, crowd sections answering) as the core idea of rebellion: many voices, growing. Mastered at -10.5 LUFS, -1.02 dBTP, no warnings.
- **What worked:** the brief listed the nearest wrong feelings (rage, defiance, triumph, menace, exotic tourism), and the producer explicitly kept the hype out: no risers, no major lift. The strongest sections are subtractions: the march with no kick or 808, and the standoff where the crowd shouts over nothing.
- **Mixing loop again:** the first trial master (v018) cut 40 Hz by 4.8 dB and boosted 50-100 Hz; notching the 808's sub after its drive, lifting its 52/85 Hz body and cutting the stomp at 170 Hz got the final EQ moves under 4.1 dB.
- **Process:** the session was interrupted at iteration 12 (an interrupted operator turn took the background agent down) and resumed by a fresh agent from `project.json` and `journal.md`. Forward-only versioning and the journal made the hand-over seamless. Operators: check long sessions periodically and resume them if they stop.
- **Engine changes:** new instruments `oud`, `ney`, `darbuka`. Fixes: `listen --wav vNNN.master.wav` now finds the render's meta; `listen` piped into `head` no longer crashes. Known: the key detector reads Hijaz as major (its raised third dominates); ignore it for maqam-based tracks.
