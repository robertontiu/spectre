# 014: Lo que no supe decir

| | |
|---|---|
| Mode | Briefed. Genre: **Latin pop**. Subject: **a love letter**, intimate and specific. The producer chose the strand (a bolero-bachata), what the letter is in sound and the words |
| Producer | Spectre, run on Claude Fable 5.2 for this session |
| Feeling | The act of writing, alone and late: tender, a little afraid, quietly brave |
| Length / tempo / key | 3:31, 84 bpm, D major (the first half of the mambo in B minor) |
| Instruments | requinto stand-in (`acguitar` high, bright, dry), nylon rhythm guitar with the bachata chop, bass, bongó stand-in (`darbuka` tuned down), maracas/güira stand-in (`shaker`), one voice (`singer` `svs` `hanami-es-soft`, Spanish) |
| Words | Spectre's own, in Spanish: "te escribo" (I'm writing to you), "te escribo despacio" (I'm writing to you slowly), "lo que no supe decir" (what I never knew how to say), "siempre tuya" (always yours) |
| Iterations | 27 journal entries, 28 renders |
| Master | `studio.py master v028 --genre latinpop` (master v2, rock curve reused, hand-tuned): -11.0 LUFS, -1.05 dBTP (MP3 -0.71), PLR 10.0, LRA about 7.5 LU, laptop loss -1.5 dB, phone check clean. The EQ sits at its limit at 31-40 Hz (borrowed curve, nothing lives there) and 250-315 Hz (the engine guitar's body) |
| Credits | Vocals: Hoshino Hanami (DiffSinger voicebank by Lotte V, lottev.moe), Potluck Vocoder by tigermeat |

## How it carries the feeling
- **You hear someone writing.** The requinto is the hand: it writes a phrase, stops, and crosses it out with two dead palm-muted strokes, and the whole band holds its breath. Three cross-outs in the first minute, one in the second, none after.
- **The sentence takes four tries.** It fails in chorus 1 (the requinto stops on the 9th), nearly lands in chorus 2, is said whole by the guitars in the mambo (the loudest moment: the confession, not a party), and is written small and clean in the last chorus.
- **The hand's timing carries it too:** about 22 ms late in the verses, 8 ms in the choruses, 6 ms early in the mambo.
- **The voice is one instrument in the band:** a call at the top of verses 1 and 2 that the requinto answers, the first two bars of each chorus, the sign-off. Close, with a small late reverb (docs/LATIN_POP.md "Mixing the voice"); all 22 words read on the master (Whisper, Spanish).
- **Wrong feelings kept out:** a club reggaetón banger, a cheesy wedding-band ballad, a tourist "Latin" cliché, melodrama, a generic radio love song, background music.

## Song form (bars of 4/4)
- **Opening (1-4, 0:00):** the whole small band already mid-phrase on the ii chord; the first cross-out
- **Verse 1 (5-12, 0:11):** bolero; "te escribo"; the requinto writes, strikes through twice, starts again
- **Chorus 1 (13-20, 0:34):** majao; "lo que no supe decir"; the requinto's sentence crossed out
- **Verse 2 (21-28, 0:57):** derecho; "te escribo despacio"; one cross-out
- **Chorus 2 (29-36, 1:20):** a second requinto in sixths; the sentence reaches the 3rd
- **Mambo A (37-44, 1:43):** B minor; the hand stops stopping, running eighths ahead of the beat
- **Mambo B (45-52, 2:06):** the peak: the guitars say the whole sentence, landing on D
- **Verse 3 (53-60, 2:29):** the read-back, an octave lower, no cross-outs
- **Chorus 3 (61-68, 2:51):** the smallest: voice and guitars only
- **Signature (69-72, 3:14):** "siempre tuya" over iv-I, a ritardando, the requinto signs F♯-E-D; one last Dadd9

## Departures from Spectre's habits
It starts mid-sentence, like a letter you open; the loudest moment is the middle; the last chorus is the smallest, with no silence before it; it ends on the signature and the tonic.

## Remix (2026-11-25)
**v031 replaces v028 as the published version.** A remaster with a light remix, no compositional change: tempo, swing, seed, patterns, arrangement and the words are frozen, and every track's events are identical to v028. The voice and its reverb are untouched. The target is the dark strand of the Latin pop references (`latinpop_dark`, 66 tracks of boleros and nylon-guitar songs) instead of the borrowed rock curve; the low end the old curve had moved to 165-280 Hz was handed back to the bass (+6 dB at 62 Hz, its 165 Hz boost from +5 to +2 dB) and the segunda guitars came down 2-3 dB at 180-195 Hz. Nothing carved, brightened, bussed or compressed. `studio.py master v031 --genre latinpop --target latinpop_dark`: -11.0 LUFS, -1.06 dBTP, PLR 10.0, LRA 7.0 LU, no warnings (EQ at its limit only at 31.5-40 Hz, where nothing plays). Against the target (50-80 Hz / 100-250 / 315-400 / 2-5 kHz / 8-12.5 kHz): previously -3.4 / +3.0 / +1.2 / +2.3 / -2.5 dB, now +1.0 / +0.9 / +0.8 / 0.0 / -2.2. Every section within 0.7 LU of the previous master; words 22/22, as before. Open: the voice's inhale before verse 2 (54.6 s) measures 7.1 dB over the darker curve at 6-12 kHz on the phone check (the breath is unchanged; the curve allows less top), and 16 kHz stays about 10 dB under the curve (a dry nylon band has nothing there). Details in the journal's remix entry.

The previous release (v028) is reproduced by `project-published.json`; the table above describes it. `ear-overview.png` still shows v028's render: no overview ear was saved for the remix. `build.py` still writes v028's project: running it overwrites the remix. `remix.py` is the recipe: applied to `project-published.json` it gives `project.json` exactly (it reads `project.json`, which is now the remix, so point it at `project-published.json` before running it again).

## Files
- `lo-que-no-supe-decir-mastered.mp3`: the track
- `journal.md`: the producer's numbered moves
- `project.json`: reproduces the track exactly; generated by `build.py`
- helpers: `stems.py`, `voxcheck.py`, `words.py`, `hiss.py`, `spec.py`, `r.sh`, `z.sh`, `wait.sh`
- `ear-overview.png`, `master-tonal-balance.png`, `master-report.json`

## Spectre's note
"I didn't want to write a love song, I wanted to hear somebody writing one. So the guitar got to make mistakes: it starts a line, hates it, scratches it out, and the whole room waits. Everything else followed from that: the band only plays out once, in the middle, when the guitars finally say it, and after that the letter gets quieter until it's a voice, a guitar and a name. The hardest part was leaving the last chorus small."
