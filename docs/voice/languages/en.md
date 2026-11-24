# Voice: English

**First pass, to be expanded** (docs/ORCHESTRATION.md, standing rule 10). General findings and their sources are in [../GENERAL.md](../GENERAL.md).

## TTS voice
- Kokoro v1.0 (Apache 2.0), `af_heart` (female, default), `am_michael` (male); model files and licence in `models/tts/kokoro/README.md`. Kokoro phonemizes English with eSpeak NG (US English; voices starting with `b` speak British English).
- Speaking rate `tts_speed` 0.9: phrases come out at about 3-4.5 syllables a second ("here you are" 660 ms, "and you stay on the ride" 1085 ms).

## Stress and linking as the TTS speaks them (measured on the "Here You Are" chorus)
- Kokoro puts phrase stress where English speech does: content words get the pitch accent and the bright, high-energy spectrum (the first "round" of "round and round": +3.1 semitones; the second, phrase-final one: 4 dB more 2-8 kHz energy). Sung, that stress pattern fights the melody; `prosody` evens it out (GENERAL.md, "Stress").
- Connected speech links across word boundaries: a final consonant becomes the onset of a following vowel-initial word ("round-and": the /d/ release starts "and"; "hold on": /l/ 20 ms, /d/ closure 10 ms, release 15 ms, then the vowel). Phrase mode keeps these links; `keep_joins` keeps their spoken lengths.
- Function words are short and reduced in the phrase ("and" with a 35 ms vowel); on their own note the core-stretch method holds their vowel without slowing their transitions.
- Final voiced stops (d, b, g) end in a long aspirated burst when Kokoro speaks a word alone; sung, the engine keeps them voiced with a short soft release ("round", not "rount").

## Still open
- English phonology for singing: vowel modification at high pitch, diphthong timing on long notes (first element held), r-coloured vowels, flapping, glottal onsets before vowel-initial words, schwa in unstressed syllables, stress-timed rhythm against the note grid.
