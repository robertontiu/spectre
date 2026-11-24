# SVS trial: a singing voice synthesizer instead of bent TTS speech (2026-11-24)

**Question:** does a model trained on singing (DiffSinger) sing Spectre's short vocal lines better than `singer` `source: "tts"` (Kokoro speech bent onto the melody with WORLD)? Scope: voices as an instrument (hooks, calls, refrain fragments, choir textures), not full songs. Nothing here changes the engine; `engine/singer.py` is untouched.

## Listen

| file | what |
|---|---|
| `hanami-line-dry.mp3` | "here you are, round and round", dry: Hoshino Hanami (female, "natural pop soprano"), own vocoder |
| `hanami-potluck-line-dry.mp3` | the same with the commercial-friendly Potluck vocoder (the chain that is licence-clean, see below) |
| `leona-line-dry.mp3`, `leona-potluck-line-dry.mp3` | LEONA (female, cuter character soprano), own vocoder / Potluck |
| `tiger-line-dry.mp3` | TIGER (male), **non-commercial licence**: for comparison only. Sung at the written notes (F#4-B4), high for a male voice |
| `hanami-potluck-chorus.mp3` | the c1 chorus (pre-chorus + chorus of session 009) with Hanami + Potluck as the lead: same backing, vocal chain, level, double, sends and `master --genre rock` as `../tts/c1-natural.mp3` |
| `choir-line-dry.mp3` | a few-voice texture: four separate takes (Hanami Root + Nectar, LEONA Core + CatNap), melody plus a third below, panned, dry |

Compare with `../tts/b1-natural-dry.mp3` / `../tts/b3-stage4-timing.mp3` (same line, current engine) and `../tts/c1-natural.mp3` (same chorus).

## What was installed

- **DiffSinger, OpenVPI ONNX format** (what OpenUtau runs), driven headless by `dsinger.py` (about 350 lines, numpy + onnxruntime 1.29, CPU). It is a port of OpenUtau's code path (`OpenUtau.Core/DiffSinger`: `DiffSingerBasePhonemizer.ProcessPart`, `DiffSingerPitch.Process`, `DiffSingerRenderer`): words to ARPAbet (the bank's `dsdict-en*.yaml`, then CMUdict via `pip install cmudict`), phonemes grouped per note from the vowel on (a note's onset consonants belong to the previous group, so they are sung before the note and the vowel lands on it), the bank's **duration model** predicts every phoneme's length, each group is stretched to its note span, the **pitch model** draws the f0 (auto-pitch), the **acoustic model** makes the mel, the **vocoder** the wave. OpenUtau defaults: 20 acoustic steps, 10 pitch steps, depth = the bank's max depth, gender 0, velocity 1.
- Two deviations from a bare OpenUtau render, both small: a 300 ms closing `SP` token after each phrase (DiffSinger's training phrases end in `SP`; without it Hanami held the final "d" of "round" for 590 ms and Whisper heard "brown"), and 5 ms fades at phrase edges (TIGER clicked at its first frame). Renders are deterministic: onnxruntime is seeded before the sessions are made.
- `pip install faster-whisper` (small.en) only as a rough intelligibility check; not needed to render.
- Model files live in `~/.cache/spectre/svs/<bank>/bank/` (500-560 MB per bank, plus `potluck/`), never in git.

## Voicebanks and licences

| bank | voice | source | licence (summary) | for Spectre (CC BY 4.0 tracks)? |
|---|---|---|---|---|
| **Hoshino Hanami ~AI❤dol~ v1.0** by Lotte V | female, "natural pop soprano", ~2 h English data (3 h 53 min total, 8 languages), 3 modes (Root, Fragrance = power, Nectar = soft) | <https://lottev.moe/> (MediaFire link in the v1.0 release post); terms also in <https://github.com/lottev1991/LotteV-Voicebank-Update-Repo> | Team L❤VE Voicebank License + Terms of Use: use "for any creative purpose, even commercially", no permission needed; credit Lotte V; don't redistribute/sell the files or claim the voice; no political, hateful or illegal use; derivative voices only through synth settings. **Its vocoder AI❤dolGAN is fine-tuned from OpenVPI NSF-HiFiGAN: CC BY-NC-SA 4.0** | yes **with the Potluck vocoder** (credit "Hoshino Hanami by Lotte V"). Note the "no political applications" clause |
| **LEONA -Ubasti- AI for DiffSinger** v0.0.1b (beta) by Lotte V | female, "cute, character-style" soprano, ~2 h English, trained multispeaker with Hanami's data; modes Core, CatNip, CatNap | <https://github.com/lottev1991/LotteV-Voicebank-Update-Repo/releases/tag/v0.0.1b-leona> | voicebank **CC BY 4.0** (`__license/LICENSE_voicebank.txt`) + the same Terms of Use as Hanami; **vocoder "meowcoder" CC BY-NC-SA 4.0** | yes with the Potluck vocoder; but it is a beta and the less natural, more anime-styled of the two |
| **TIGER** v102 by tigermeat | male, English | <https://github.com/spicytigermeat/tiger_diffsinger/releases/tag/v102> | **CC BY-NC-ND 4.0 + Commons Clause**: non-commercial only, commercial use needs a purchased licence; no redistribution or derivatives | **no** (only to hear a male DiffSinger voice). CC BY tracks may be reused commercially by others, which this licence forbids |
| **Potluck Vocoder** (lite, PC-NSF-HiFiGAN) v100 by tigermeat | vocoder, community data | <https://github.com/mrtigermeat/potluck-vocoder/releases/tag/v100> (`dsvocoder.zip`) | adapted from CC BY 4.0: free to use, share, adapt; **commercial use allowed only with DiffSinger models**; attribution with a link to the licence; outputs/weights may not be used to train other generative models | yes (we use it with DiffSinger). Credit "Potluck Vocoder by tigermeat" |

Not used: No.7 (SEVEN) and Miyo (non-commercial), Albus Korde/LUNAI (non-commercial), the OpenVPI NSF-HiFiGAN vocoders (CC BY-NC-SA). English DiffSinger banks with clean commercial terms are rare, and almost all are character voices (idol, cute, anime-adjacent); Hanami is the most natural-sounding adult one found within the time box. GitHub release pages of unlisted repos are blocked in the sandbox (assets download fine when the name is known); the community wiki (diffsinger.miraheze.org) is blocked too.

## Reproduce

```bash
# banks (see the table for sources) unpacked so that ~/.cache/spectre/svs/<bank>/bank/dsconfig.yaml exists,
# Potluck's dsvocoder.zip unpacked into ~/.cache/spectre/svs/potluck/
pip install cmudict
python3 examples/vocals/svs/build.py line                  # <bank>-line-dry.mp3 for hanami leona tiger + timing tables
python3 examples/vocals/svs/build.py line hanami-potluck leona-potluck
python3 examples/vocals/svs/build.py timing hanami-potluck # dry chorus timing table
python3 examples/vocals/svs/build.py chorus hanami-potluck # mixed + mastered like c1 (runs studio.py in-process with singer.sing swapped)
python3 examples/vocals/svs/build.py choir
```

## CPU cost (2 threads, this sandbox)

The 6.2 s line renders in 5-6 s once the models are loaded (about 1 s more on first load): acoustic model 3.2-3.9 s, vocoder 1.5-1.9 s, pitch 0.6 s, durations under 0.1 s. The 15 s dry chorus: 17-20 s. The whole c1 chorus (two SVS takes for the double, the backing, mix and master): 61 s. Peak RAM for a line is about 1.2 GB. So roughly real time: usable for hooks and short lines in a producer loop, if renders are cached per phrase.

## Timing (same metrics as `tools/joincheck.py --timing`)

Perceived onset (P-centre, the "maxD" fastest 300-3000 Hz energy rise) against the score; for the SVS the syllable boundaries are its own phoneme boundaries. Current engine = `joincheck.py --timing` on the same line, and `/tmp/tts-joins-ready.txt` ("timing fix, final") for the chorus.

| | P-centre mean | sd | max \|dev\| | IOI error sd | beyond JND | beyond 3x JND | consonant start vs beat | vowel vs beat | lead |
|---|---|---|---|---|---|---|---|---|---|
| **line**, current engine | +23 ms | 35 | 75 | 56 | 5/6 | 2 | | | |
| line, Hanami | -24 | 52 | 135 | 64 | 2/6 | 1 | -76 | 0 | 76 |
| line, Hanami + Potluck | -27 | 50 | 135 | 61 | 2/6 | 1 | -76 | 0 | 76 |
| line, LEONA | -18 | 60 | 150 | 63 | 2/6 | 1 | -76 | 0 | 76 |
| line, TIGER | +2 | 49 | 80 | 49 | 5/6 | 3 | -102 | 0 | 102 |
| **chorus**, current engine | +23 | 40 | 124 | 61 | 16/24 | 5 | -12 | +72 | 78 |
| chorus, Hanami + Potluck | -25 | 39 | 115 | 57 | 13/24 | 9 | -63 | 0 | 63 |
| chorus, LEONA | -19 | 33 | 110 | 48 | 11/24 | 8 | -65 | 0 | 65 |
| chorus, TIGER | -20 | 31 | 90 | 50 | 10/24 | 7 | -78 | 0 | 78 |
| human singers (GTSinger, docs/voice/GENERAL.md) | | | | | | | +1 | +106 | 91 |

Reading it:
- **On these numbers it is a draw.** Spread and inter-onset regularity are about the same as the engine's after its timing fix (sd 31-39 vs 40 ms on the chorus, IOI sd 48-57 vs 61), with fewer onsets beyond the JND but more beyond 3x the JND. Between takes of the same bank the line's P-centre numbers move by 10-20 ms (the pitch model samples a new curve each time), so differences that size mean nothing.
- **DiffSinger, as OpenUtau drives it, puts the vowel exactly on the note and the consonants before it** (63-102 ms lead). That is the classical rule (VOCALOID, Saino 2006), not what the GTSinger singers do (consonant on the beat, vowel about 100 ms later), and it is a labelling convention of DiffSinger datasets (a note starts at its vowel), not something the model learned. What the model does learn is the consonant lengths in context (hh 105-140 ms, y 60-85, r 40-70, st 193) and how the phonemes flow into each other. The worst flags are the phrase-initial words ("here", "hold": P-centre 100-145 ms early, on the /h/), the same words the engine used to rush.
- Intelligibility (Whisper small.en, a rough proxy): all three dry SVS choruses transcribe word-perfect. On the short line the engine's renders also transcribe perfectly (they are speech underneath); the SVS lines mostly do, with the last "round" sometimes heard as "band"/"bend" (LEONA).
- What the metrics do not capture is what the SVS is for: the joins, coarticulation, vibrato, pitch transitions and breath come from one model of a singing voice, so there is nothing to stitch. In the spectrograms the SVS lines show continuous formant transitions at every join and singer-like vibrato and scoops; the engine's line shows the speech-derived consonant bursts (e.g. the "d" of "round and").

## Verdict (by measurement and spectrograms; it needs Robert's ears)

- **It works**: free, local, CPU, about real time, deterministic, intelligible, and it removes the whole class of join, cadence and stitching problems the `tts` path keeps hitting, because the sung voice is made in one piece by a model of a singer. For Spectre's use (short lines, hooks, refrain fragments) that is the right shape of tool, and the four-take choir test shows it can make a few-voice texture from separate takes and modes cheaply.
- **Timing is not better by the numbers**, only different: the model's "vowel on the note" convention gives consonants 60-100 ms ahead of the beat. If that sounds early by ear, the fix is one parameter (shift each note group so the onset consonant starts on the beat), not a pile of rules.
- **The real limit is voices and licences.** Commercial-clean English banks are few and mostly character voices; Hanami ("natural pop soprano") is the best candidate found, and only with the Potluck vocoder (her own vocoder is non-commercial). No commercial-clean male English bank was found in the time box (TIGER is non-commercial). The Potluck "lite" vocoder is a general model; its author recommends fine-tuning it per voice.
- **Recommendation:** if the Hanami + Potluck chorus sounds more like singing than `c1-natural` to Robert, this is the better path for sung hooks: integrate it as a `singer` source (`source: "svs"`) that renders each phrase with the bank and caches it, keeping the existing vocal chain (fx, double, sends). If the voice character is wrong for Spectre, the next step is not more rules but a different or self-trained bank (DiffSinger training needs about 1-2 h of clean, licensed singing and a GPU).
