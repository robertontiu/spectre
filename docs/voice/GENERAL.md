# Voice: general knowledge (all languages)

**First pass, to be expanded.** Written while fixing the `singer` `tts` word joins (2026-11-24) from a handful of sources; a thorough research pass from the scientific literature is planned (docs/ORCHESTRATION.md, standing rule 10). Each engine choice below names the finding it rests on; the measurements come from `tools/joincheck.py` (docs/MANUAL.md, "Voices").

## Speech to song: what changes

### Timing: consonants before the beat, the vowel on it
- Singers start consonants early: "human singing voice has a tendency to start consonants a little earlier than the timing of musical note", so the HMM singing synthesizer of Saino et al. models a time-lag per note that can be negative ([Saino, Zen, Nankaku, Lee & Tokuda, Interspeech 2006](https://www.isca-archive.org/interspeech_2006/saino06_interspeech.pdf)). In choral recordings, initial consonants are "nearly always anticipated" before their beat, with exceptions for some plosives and the second consonant of a cluster, and the anticipation depends on how lengthenable the consonant is ([Hauck 2020, Music Performance Research 10](https://boris.unibe.ch/149910)).
- VOCALOID places the vowel onset "strictly on the NoteOn position", with the consonant material before it ([Kenmochi & Ohshita, Interspeech 2007](https://www.isca-archive.org/interspeech_2007/kenmochi07_interspeech.pdf)).
- In the engine: onsets go before the note and the vowel starts on it (since the first `singer`); `keep_joins` (2026-11-24) ends a syllable exactly where the next onset starts, so the consonants at a join keep their spoken length instead of being overwritten.

### Sustaining: stretch the steady vowel, keep the transitions
- "Unlike speaking, we sustain vowels for singing ... the vowel shape must be held for the duration of the tone"; in a diphthong the emphasis falls on the first vowel ([K-State Vocal Techniques, "Articulation"](https://kstatelibraries.pressbooks.pub/vocal-techniques/chapter/articulation/)).
- Concatenative singing synthesis keeps phoneme transitions as recorded (diphone samples) and builds the sustained vowel from stored sustained-vowel samples, interpolating spectral envelopes ([Kenmochi & Ohshita 2007](https://www.isca-archive.org/interspeech_2007/kenmochi07_interspeech.pdf); background: [Bonada & Serra, IEEE Signal Processing Magazine 24, 2007](https://mtg.upf.edu/node/512)). Statistical synthesis distributes extra note length across model states by their variance (Saino et al. 2006), i.e. mostly into the variable (steady) parts.
- In the engine: `stretch: "core"` keeps the first and last `trans_ms` (40) of each vowel at spoken speed and stretches only the steady core (lingering on its first part, as for the first element of a diphthong). Measured on the "Here You Are" chorus: the next vowel's first 30 ms were played 2.5-9.5x slower than spoken before (mean |log2 warp| 2.28), 1.0x on most joins after (mean 0.71).

### Pitch at a join
- Note transitions sit near note boundaries; data-driven singing F0 models align them to within tens of ms of the note onset ([Hua, "Modeling Singing F0 With Neural Network Driven Transition-Sustain Models"](https://arxiv.org/pdf/1803.04030)).
- Measured: with the pitch move starting at the onset consonant, 75-100% of it happened after the next vowel had begun (a slide inside the vowel, heard as forced). Since the vowel should start on its note (VOCALOID's rule above), the engine now starts the move earlier (`glide_early` 0.8 of the transition time), so most of it passes through the consonants: on the chorus, the share inside the vowel fell from 0.80 to about 0.3 on average.

### Stress: let the melody set the emphasis
- Stress in speech is cued by duration, intensity, pitch and spectral balance; in Campbell's measurements "relative energy in the higher spectral regions proved the best correlate of prominence" (energy 2-8 kHz), loudness at the fundamental the weakest ([Campbell, ICPhS 1995](https://www.coli.uni-saarland.de/Phonetics/icphs/ICPhS1995/13_ICPhS_1995_Vol_3/p13.3_676.pdf)).
- In a song the note placement and length carry the emphasis; a spoken phrase's own stress pattern sung over a melody puts accents where the music has none (Robert's "each 'round' seems emphasised").
- Measured: the engine already evens vowel loudness per syllable, but the spoken spectral tilt survived intact (correlation spoken/sung 0.97, spread 7.0 dB across the chorus's syllables). `prosody` (0.7) moves each syllable's tilt and onset force toward the same syllable spoken alone (its citation form) and leaves spoken pitch accents out of `micro`: the tilt spread fell to 4.9 dB and the onset-force spread from 3.2 to 2.8 dB. A vowel-initial word's onset in a phrase is the previous word's linking consonant, which its citation form lacks, so it is not corrected.

### Speaking rate of the sampled phrase
- Singers keep consonants short and put them before the beat (above); slower TTS speech mainly lengthens consonants (Kokoro at speed 0.8 instead of 0.9: the /h/ of "here" 135 -> 215 ms), so the engine keeps `tts_speed` 0.9 and gets vowel length from the notes.

## Still open (for the research pass)
- Speech rhythm in general (stress- vs syllable-timing, phrase-final lengthening: Klatt 1976, "Linguistic uses of segmental duration in English", JASA 59; not re-read in this pass), coarticulation and what sung legato keeps of it, vowel modification by register, consonant duration models in singing synthesis, F0 overshoot and preparation at note transitions.
- The remaining measured gaps: consonant dips about 3 dB deeper sung than spoken, and joins on notes too short for their spoken consonants (e.g. "round|and" on an 8th).
