# 010: Unison

| | |
|---|---|
| Mode | Briefed (an engine test set by a violinist and music teacher). Genre: **joc țigănesc**, Romanian lăutar wedding dance. Subject: **a wedding, the climax of two souls becoming one**. G minor, 2/4, quarter = 50 in the brief, guitar, bass, violin and essential percussion, a "cold" (*rece*) sound. The producer chose the feeling, the tempo plan and how the climax works |
| Producer | Spectre (Claude Opus) |
| Feeling | 3 a.m. at the banquet: the band and the room lifting each other; joy with the minor mode's seriousness of two families becoming one |
| Length / tempo / key | 3:16, quarter = 50 (slow-dance door) rising in steps and ramps to 140, G minor (harmonic minor, raised 4th colours), 2/4 |
| Instruments | violin (the primaș), nylon acoustic guitar (afterbeat chop and 16th push), bass, toba with cinel and rim, snare, handclaps, finger snaps |
| Iterations | 26 journal entries, 24 renders |
| Master | `studio.py master v024 --genre joc` (master v2, measured rock curve reused): -11.0 LUFS, -1.07 dBTP (MP3 -0.88), PLR 10.0, LRA 7.1 LU, width -15.1 LU, laptop loss -1.5 dB, phone check clean, no warnings. The top end sits 5-6.6 dB under the curve at 10-12.5 kHz: a dry acoustic band's natural decay, left as is rather than faked |

## How it carries the feeling
- **Two souls in one violin:** "his" strain climbs on the low strings through the augmented second (G A Bb C# D); "her" strain falls on the high strings through the other (A G F# Eb D). Both land on the same D5, but apart, in separate strains through the slow dance and rounds 1-2.
- **They turn to each other:** in round 3 they trade bar by bar, and he climbs into her register.
- **They fuse:** in round 4 one bow plays both at once as contrary-motion double stops (octave G4/G5, sixth A4/F#5, fourth Bb4/Eb5); his leading tone C#5 and hers Eb5 press together and each moves a semitone into a unison D5 on two strings. The first pass is held back (no drummer, no push) so the converging lines are heard; then the whole room holds the unison over D7, the claps locked into the guitar's push, and everyone lands on the G octave.
- **A staircase, not a song with a valley:** the tempo steps up round by round (100, 112, 124, then 126 → 140) as a band lifts the room at a wedding; percussion joins piece by piece (toba, snare ghosts, snare, cinel, snaps, the room's claps). The guitar's afterbeat chop never changes its job, so the violin can go anywhere.
- **"Rece" (cold):** not an established Romanian musical term (see docs/JOC_TIGANESC.md); read as dry, close, unprocessed acoustic sound: no reverb wash, no synth, a clear, slightly metallic violin (`cold` 0.45). Warmest at the slow door, colder and more biting as the dance heats.
- **Wrong feelings kept out:** a tourist csárdás (no presto for effect, vibrato only on long notes), the kitsch wedding band (dry, minor, no synth), a doina (the slow opening is a metred dance), chaos (bass and chop never waver), Balkan brass, a march (the downbeat lighter than the afterbeat).

## Song form (bars of 2/4)
- **Prelude (4), quarter = 50:** the primaș over a held D7
- **Rar A, rar B (8 + 8):** the tune as a stately slow dance; rar B lifts 50 → 72
- **Ridicare (4):** false trill and a run while the tempo ramps to 100
- **Round 1 (A A' B B', 8 each), 100:** his strain and her strain, percussion joining
- **Interlude 1 (4), 106 · Round 2 (8 each), 112:** double stops on the open strings, snaps, the guitar's 16th push, the room's claps
- **Interlude 2 (4), 118 · Round 3 (8 each), 124:** strain C trades climb and fall bar by bar; he plays his strain in her register; her strain in double stops
- **Interlude 3 (4), 126:** the primaș dares alone over bass, chop and claps
- **Union (8), 126 → 132:** the fused strain, the band held back
- **Union 2 (8), 132 → 136:** the drummer, snaps and push return
- **Peak A, Peak B (4 + 4), 136 → 140:** the whole room; the unison D5 held two bars over D7, landing on Gm. The band stops
- **End (4), 140:** the primaș runs alone, the band answers, the last V-i hit together; a 2-bar ring

## Departures from Spectre's habits
No mid-track valley (the arc only climbs), no wind-down outro (it ends at its peak), no lone filtered intro (the whole band is in the room for the slow dance).

## Remix (2026-11-25)
**v026 replaces v024 as the published version.** A remaster with a light remix, no compositional change: tempo maps, swing, seed, patterns and arrangement are frozen, and every track's events are identical to v024. The target is the genre's own curve, measured on 103 Taraf de Haïdouks recordings (`joc_taraf`), instead of the borrowed rock curve; two moves made for that curve were partly undone: the guitar's body boost at 175 Hz from +5 to +2 dB, and the tobă's notch at its 54 Hz from -5 to -2 dB. No stacks, no buses: an acoustic band. `studio.py master v026 --genre joc`: -11.0 LUFS, -1.03 dBTP, PLR 10.0, LRA 6.7 LU, top end within 1.2 dB of the curve, no warnings (EQ at its limit only at 31.5-40 Hz: a string band has no sub); mean gap to the taraf recordings 1.46 dB (the previous master 2.67). Every section within 0.35 LU of the previous master except the prelude (+0.85 LU); the climb round by round is intact. Details in journal entry 27.

The previous release (v024) is reproduced by `project-published.json`; the table above describes it. `ear-overview.png` still shows v024's render: no overview ear was saved for the remix. `build.py` still writes v024's project: running it overwrites the remix.

## Files
- `unison-mastered.mp3`: the track
- `journal.md`: the producer's numbered moves
- `project.json`: reproduces the track exactly; generated by `build.py full`
- `build.py`, `stems.py`: the producer's helpers
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"This one was a staircase, not a song with a valley. Every round had to earn its step, and the hardest work was keeping the slow door warm without letting it weep. The moment I'm proudest of is the union strain's first pass with the drummer sitting out: you can hear the two lines walk toward each other and close into one D, and then the room comes back in to hold it. The guitar chop never changed once, and that's why the violin could go anywhere."
