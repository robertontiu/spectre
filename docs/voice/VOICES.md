# Voice catalogue: `singer` `"source": "svs"`

The voices the producer can choose for sung words (docs/MANUAL.md "Voices"). Pick one with `"voice": "<id>"`. The same data is machine-readable in `engine/voices.json`: tags, range, licence and credit. Auditions are in `examples/vocals/svs/voices/<id>.mp3`. Each audition is the same two bars, dry: "here you are, round and round", F#4-B4 at 100 bpm. `examples/vocals/svs/voices.py` rebuilds the auditions and the measurements.

**Voices are instruments** (standing rule 12): short lines, hooks, calls, refrain fragments and choir textures, never a sung song.

## Licences and credit (read before using a voice)

| bank | licence | credit line (put it in the session README's **Credits** and the site notes) |
|---|---|---|
| Hoshino Hanami ~AI❤dol~ v1.0, by Lotte V | Team L❤VE Voicebank License and Terms of Use. Any creative use is allowed, commercial included, without asking. Conditions: credit Lotte V; don't redistribute or sell the files; don't claim the voice as your own; no political, hateful or illegal use. Religious works are allowed without asking as long as they aren't for proselytizing (ToU_EN.md in Lotte V's lottev-voicebank-update-repo, read 2026-11-24): a carol quoted in a secular track is fine. | Vocals: Hoshino Hanami (DiffSinger voicebank by Lotte V, lottev.moe), Potluck Vocoder by tigermeat |
| LEONA -Ubasti- v0.0.1b (beta), by Lotte V | The voicebank is CC BY 4.0, plus the same Terms of Use as Hanami. | Vocals: LEONA (DiffSinger voicebank by Lotte V, lottev.moe, CC BY 4.0), Potluck Vocoder by tigermeat |
| Potluck Vocoder (lite) v100, by tigermeat | The engine uses this vocoder for every voice, because both banks' own vocoders are CC BY-NC-SA. Commercial use is allowed only with DiffSinger models. Credit it with a link to its licence (https://github.com/mrtigermeat/potluck-vocoder). Its output may not be used to train generative models. | (included in the lines above) |

**Never use a Lotte V voice in a track with a political subject** (for example session 011, "Corruption" / "Deșteaptă-te, române!"). Their terms forbid political use. For such a track, use `vox`/`vox2` or the `tts` singer.

## The voices

How to read the measurements: they are taken on the dry audition (pyworld analysis).
- **tilt**: energy at 2-5 kHz relative to 0.2-1 kHz. Higher means brighter.
- **breath**: aperiodicity at 1-4 kHz. 0 is pure harmonics; higher is breathier.
- **F1/F2**: formants of the long "are" vowel, from LPC.
- **vib**: vibrato depth in cents (sd on long notes).
- **Whisper**: whether Whisper small.en transcribed the dry audition correctly.

| id | bank / mode | sound (tags) | suits (emotions; genres) | bad at | tilt dB | breath | F1/F2 Hz | vib | Whisper |
|---|---|---|---|---|---|---|---|---|---|
| `hanami` (default) | Hanami / Root | female, warm, clear, natural | tender, hopeful, nostalgic, sincere; pop rock, ballad, lo-fi, folk, carol choir, hip-hop hooks | grit, belting, menace, male parts | -8.6 | 0.06 | 617/987 | 32 | correct |
| `hanami-power` | Hanami / Fragrance | bright, firm, open, forward | joyful, anthemic, confident; pop rock choruses, trance/EDM hooks, calls over dense mixes | intimacy, whisper | -5.7 | 0.06 | 958/1501 | 27 | correct |
| `hanami-soft` | Hanami / Nectar | soft, dark, airy | intimate, melancholy, dreamy, longing; lo-fi, ambient, ballad, dream pop, choir pads | cutting through guitars or saws; energy | -19.3 | 0.10 | 511/1024 | 39 | correct |
| `hanami-dark` | Hanami / Root, gender -0.5 | dark, rounded, covered (formants lowered) | solemn, mournful, mysterious, reverent; folk lament, dark ambient, choir alto, cinematic | bright pop; diction in dense mixes | -28.4 | 0.10 | 498/1009 | 32 | wrong ("here's a round-and-down") |
| `leona` | LEONA / Core (beta) | bright, light, youthful, character/cute | playful, cheeky, sunny, excited; anime-style hooks, hyperpop, chiptune, trance | mature, serious or sad lines; natural adult pop | -3.2 | 0.05 | 801/1397 | 18 | correct |
| `leona-power` | LEONA / CatNip (beta) | brightest, hard, edgy | energetic, excited, bratty, triumphant; EDM/trance drops, hyperpop, rock calls | tenderness, warmth | +1.6 | 0.05 | 906/1318 | 18 | slurred ("hear you around") |
| `leona-soft` | LEONA / CatNap (beta) | soft, breathy, airy, dark | wistful, tender, fragile; lo-fi, dream pop, ambient, choir pads | dense mixes, energy | -17.0 | 0.18 | 526/1030 | 33 | slurred ("hear you around") |

**Range.**
- Hanami: the training data sits at G3-D5 (most of it C4-A#4, peak G4; `midi_distribution.jpg` in the bank). Write A3-D5. A fifth lower (B3-E4) and a fifth higher (C#5-F#5) both still transcribe correctly (`ctl-hanami-low`, `ctl-hanami-high`). The engine warns outside G3-F5.
- LEONA: trained together with Hanami's data. The range is assumed to be the same, not measured; the engine warns outside A3-F5.
- Both are female voices. Writing them an octave lower does not make a male voice.

## Controls (what they can and can't fake)

These banks expose:
- **vocal modes** (the voice ids above),
- **`gender`** (-1..1, formant shift),
- **`velocity`** (consonant speed),
- **mode mixes** (in voices.json, `"mix": {"Root": 0.5, "Nectar": 0.5}` instead of `"mode"`: the speaker embeddings are interpolated).

They have **no** breathiness, tension, voicing or energy controls: their models were trained without them.

| demo (`examples/vocals/svs/voices/`) | setting | measured | verdict |
|---|---|---|---|
| `ctl-hanami-gender-dark` | gender -0.5 | F1/F2 617/987 -> 498/1009 Hz, tilt -8.6 -> -28.4 dB | darker and rounder, but less intelligible. This is the `hanami-dark` voice. |
| `ctl-hanami-gender-bright` | gender +0.5 | F2 987 -> 1342 Hz | brighter vowels, more youthful |
| `ctl-hanami-male-fake` | gender -1, line an octave down (F#3-B3) | F1 350 Hz, vibrato 47 cents | **Not a male voice.** Below the trained range it wobbles and Whisper hears other words ("I don't know what to do"). Don't use it. |
| `ctl-hanami-velocity-slow` / `-fast` | velocity 0.6 / 1.6 | nearly identical spectra | a small effect on these banks |
| `ctl-hanami-low` / `-high` | the line a fifth down / up | both still transcribe correctly | the usable range edges |
| `ctl-leona-soft-dark` | leona-soft, gender -0.5 | tilt -22.9 dB, breath 0.21 | the darkest, breathiest texture available |

**For choirs and doubles:** combine voices. Different modes and banks, a third or sixth apart, separate takes (each phrase has its own seeded pitch and noise; `seed` changes them). See `examples/vocals/svs/choir-line-dry.mp3`, which uses Hanami Root + Nectar and LEONA Core + CatNap. A real SATB is not possible yet: there is no tenor or bass voice.

## What is missing: male and hard voices (searched 2026-11-24)

No licence-clean English male DiffSinger voicebank was found. Every male or hard voice found fails on terms or unknown status:

| bank | voice | why not |
|---|---|---|
| TIGER (tigermeat) | male, English | CC BY-NC-ND + Commons Clause: commercial use needs a paid licence; CC BY tracks can be reused commercially by others |
| Nishiren Gard (Gardanana) | contralto with Power and Screamo modes, tension/breathiness controls (the hardest range found) | commercial use needs individual approval; its terms forbid use with "unethically AI generated ... music" and political or religious content |
| Aurelian Silva DS (AlexFloareaVT) | young male, British | no terms of use published (so no licence); its vocoder is fine-tuned on mixed data |
| Apollo DS (KAISKE) | male baritone, English among its languages | Google Drive release with no stated terms |
| Albus Korde (LUNAI), Miyo, No.7 (SEVEN) | various | non-commercial |

Options:
1. Ask a voicebank author for permission (TIGER sells commercial licences; Gardanana approves case by case, but the AI-music clause probably rules Spectre out).
2. Train a male bank from licensed singing (DiffSinger needs about 1-2 h of clean data and a GPU).
3. Keep male voices on the `tts` singer (Kokoro `am_michael` / `am_adam`) until then.
