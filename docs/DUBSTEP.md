# Dubstep for Spectre: a working brief

For sessions that make dubstep in its modern era (2015-2026) and its strands. A vocabulary, not a rulebook. Spectre has made trap-family beats (half-time, 808-led) and trance (four on the floor, a long arc); dubstep shares trap's half-time body and trance's build-and-drop dramaturgy, but its centre is different from both: **the bass is the lead instrument**, and most of the composition happens in the sound design of one or two bass voices and in the dialogue between them. Researched 2026-11-25 for queue item 12 (docs/ORCHESTRATION.md). Artists and labels are named only as craft schools, never as tracks to copy (standing rule 13).

Labels as in docs/PRODUCTION.md: **[M]** measured (a published measurement, or one made here from open data, method stated), **[S]** a named source, **[H]** hand-tuned or a judgement of this brief.

## Configuration (researched 2026-11-25; engine: `--genre dubstep` proposed to the orchestrator, not yet in engine/genres.json)
| Setting | Value | Source |
|---|---|---|
| Length and cut | **3:30-4:30, aim about 3:50-4:00** (the original mix; dubstep has no extended-mix habit: DJs play the original) | [M] catalogue (tag `dubstep`, "Catalogue measurements"): median 4:06 in 2014-16, 4:02 in 2017-19, **3:42 in 2020-21** (middle half 3:15-4:21), against 4:33-4:36 in 2008-13; riddim 3:39, melodic 4:18; EDMProd's riddim map sums to 98 bars = 2:48 at 140 before an outro ([EDMProd, riddim](https://www.edmprod.com/how-to-make-riddim/)) [S] |
| Form (bars) | intro 8-32 (the drop near bar 32: "often after the 16th or 32nd measure", "near 55 seconds"), build 8, (false drop 4), **drop 1: 16-32 bars in 8-bar halves (1A, 1B) with a switch at the half**, breakdown or mid-section 8-16, build 8, **drop 2: 16-32 bars, never a copy of drop 1** (new drums, a new bass, or a different bass "genre"), outro 8-16 | Wikipedia "Dubstep" (structure, drop at bar 16/32 "a trope rather than a rule"); EDMProd riddim and dubstep guides (8-bar blocks; drop 1A/1B, 2A/2B; false drops); [Cymatics](https://cymatics.fm/blogs/production/how-to-make-dubstep) (vary the second drop) [S] |
| Tempo | **140-150 bpm, felt in half time (70-75)**; 140 for deep / 140; 140-150 for colour bass (its tag: 150, 21 tracks); 145-150 for riddim, tearout and much melodic dubstep; default 140 for the deep frame, 145 for a heavy-strand brief | [M] catalogue: median 140 every year 2006-2018, then **148 (2019), 145 (2020, 2021)**, the middle half opening to 150 from 2014; riddim 145 (144-150) [M]; Mixgraph, 10,108 tracks: median 145, middle half 140-150, highest yearly median 150 in 2017, editorial range 138-142 ([Mixgraph](https://www.mixgraph.io/bpm-for/dubstep)) [M]; Wikipedia 132-142 [S] |
| Meter and groove | 4/4 written at 140, felt at 70: kick on 1, snare (or clap + snare) on **3** of the half-time bar (beat 3 of a 140-bpm bar = the backbeat of the 70-bpm feel); 16ths swung or shuffled in the UK strands, triplet percussion in riddim, straight and mechanical in tearout | Mixgraph ("written at 140 BPM but felt at 70"); [Cymatics](https://cymatics.fm/blogs/production/how-to-make-dubstep); Wikipedia (snare every third beat, swung, tuplets); riddim's "triplet percussion" (Wikipedia, Riddim) [S] |
| Rate of change | something every 4-8 bars; in the drop a switch every 4 bars is common in brostep and tearout, while riddim holds **one** motif for the whole drop and changes it only by modulation | EDMProd (8-bar blocks), Computer Music via [MusicRadar 2008](https://www.musicradar.com/tuition/tech/14-dubstep-production-tips-178489) (a flourish at the end of each 4- or 8-bar section); Futureproof Genre Explorer, riddim: "Repetition is the point, not a bug" [S] |
| Role of the instrumental | **the bass is the lead**: a mid-bass voice (or two in call and response) carries the hook; the melody, if any, lives in the breakdowns and intros; voices are chopped, pitched phrases and pre-drop calls (standing rule 15 fits the genre) | Futureproof Genre Explorer, dubstep ("bass as the lead instrument"); [Output](https://output.com/samples/dubstep-vocal-samples) (chopped, pitched phrases) [S] |
| Loudness of releases | **the loudest club genre measured**: store previews (the loud part) median **-6 LUFS** (middle half -6.5 to -4), against Drum & Bass -6.5, Hard Techno -7.3, Trance Main Floor -7.5, Trap / Future Bass -9.2; **whole tracks** est. -10.3 (2015-21; middle half -12.3 to -8.5), -9.9 in 2020-21, riddim -7.6, brostep -8.7, melodic -9.3, 2005-10 -12.2 | [Mixgraph LUFS meter](https://www.mixgraph.io/tools/lufs-meter) (29 dubstep previews, 120 s, 2026-08-11) [M]; catalogue (ReplayGain, ±1-2 dB) [M] |
| How the loudness is reached | **clip first, then a gentle limiter**: drum groups clipped in the mix, a clipper on the master | [Infekt masterclass](https://infektdubstep.com/masterclass/mastering/loudness/) ("Most of the time I clip heavily first, then apply a very gentle limiter"); [Futureproof](https://futureproofmusicschool.com/blog/mixing-mastering-dubstep-easy) (master bus: one soft clipper; a drop "sitting at -3 LUFS", the mix "at least -6 LUFS on the short-term meter"); EDMProd riddim (clap and hat groups clipped) [S] |
| Low end | a clean sine sub, fundamental about **40-60 Hz**, mono; the mid-bass high-passed near **100 Hz**; the sides cut below **150-180 Hz**; widening only well above the sub (Skrillex: above 7 kHz) | [Cymatics](https://cymatics.fm/blogs/production/how-to-make-dubstep) (sine sub; high-pass the main sound under 100 Hz); Futureproof (sides cut at 150-180 Hz); [iZotope, Skrillex 2011](https://izotope.com/en/learn/skrillex) (widen above 7 kHz, lower "you get phasing"); MusicRadar sub guide via search (sub fundamental 40-60 Hz) [S] |
| Master | `studio.py master vNNN --genre dubstep` (proposed: target **`dubstep_2015`**, `--lufs -8`, `--tp -1`, `mono_below 150`, `eq 0.7`, `translate 0.4`); per strand and era in "Mastering per subdivision" | target measured here: 927 tracks tagged dubstep, first released 2015-2021 (`refcurve.py catalogue`) [M]; -8 is a choice between the whole-track median (-10.3) and the loud previews (-6) and is **untested in the engine** [H]; `eq`, `translate` as trance [H] |

**Unsourced or hand-tuned in this table:** the default tempos (choices inside the measured range), the -8 LUFS integrated target (no engine test; the master's clipper has reached about -7.5 only in a stacked-kick trance drop), `eq` and `translate`, and the change rate inside drops (craft sources, not measurement).

## The tradition and the timeline
Dubstep began in South London around 2000-2002 as a darker, sparser offshoot of UK garage and 2-step, with dub's sound-system weight and time-based effects: Forward>> (from 2001), Big Apple Records in Croydon, Tempa (the name is attributed to its co-founder in 2002), DMZ (Mala, Coki, Loefah, 2004-05), Deep Medi (2006), Rinse FM (Wikipedia, "Dubstep"; Futureproof Genre Explorer, "Deep dubstep") [S]. Around 2009-2011 it crossed the Atlantic and **moved out of the sub into the middle register** ("distorted riffs" in "the register of heavy metal guitar", Simon Reynolds via Wikipedia): brostep, Skrillex's *Scary Monsters and Nice Sprites* (2010), "Bass Cannon" and "Bangarang" (2011), "Centipede" (2012) (Futureproof, "Brostep / tearout") [S]. Mainstream dubstep declined from mid-2014, especially in the US (Wikipedia) [S]. What followed is the modern era of this brief.

**The timeline, split where the evidence changes** (and why there):
| Period | Why the boundary is here | What defines it | Label |
|---|---|---|---|
| **2002-2009, UK roots (deep, "140")** | the scene's own institutions (Forward>>, DMZ, Deep Medi, Tempa) | 140 bpm (Mixgraph's 2007 median: 140), sub-bass as "the whole conversation", sparse half-time drums, "dread-heavy space", "almost no mid-range noise or metallic distortion"; wobble as an LFO on a sustained note | [M] Mixgraph; [S] Futureproof "Deep dubstep", Wikipedia |
| **2010-2014, brostep** | Skrillex's 2010 EP; the mainstream turn ends mid-2014 | the mid-range growl that "behaves more like a metal guitar riff than a dub bassline", "hard, mechanical drops" with constant section changes, "built to cut through a festival PA rather than fill a soundsystem's low end"; LFO wobbles, FM growls, resampled "talking" basses | [S] Futureproof "Brostep / tearout"; Wikipedia |
| **2015-2018, the riddim and tearout years** | riddim's breakthrough "around 2015"; colour bass coined (Rushdown, 2016); tearout absorbs deathstep, riddim and brostep (2016-2019); melodic dubstep's chart years (Illenium ft. Nevve 2017, Excision & Illenium 2018); **measured**: the tempo spread opens upward (middle half 128-150 against 137-140 before; Mixgraph's highest yearly median, 150, in 2017) while the catalogue median stays 140; tracks shorten from about 4:35 (2008-2013) to about 4:05 | the US scene splits into the strands below | [M] catalogue ("Catalogue measurements"), Mixgraph; [S] Wikipedia "Riddim (genre)", Futureproof |
| **2019-2022, the faster, shorter cut; colour bass and precision** | **measured**: the catalogue median tempo moves to **145-148** (2019: 148, 2020-21: 145; Mixgraph's series ends at 142) and tracks to **3:30-3:59** (2020-21: 3:42); the loudest years in the open data (2019 est. -8.7 LUFS); Monstercat promotes colour bass "in the early 2020s"; the pandemic gap in club playback | colour bass and melodic riddim (chords in the bass); "surgical precision with clean metallic textures, where the silence between phrases carries as much impact as the phrases" (on Ray Volpe, 2022) | [M] catalogue; [S] Wikipedia; [Ticketfairy 2026](https://www.ticketfairy.com/word/2026/03/18/dubstep-drops-then-vs-now) |
| **2023-2026, the resurgence** | no open tonal or length data after 2021 (AcousticBrainz ends in 2022); the sources: "a massive, rapid resurgence of the genre over the last three years" (2026); both "the deep, wobbly sound and the aggressive, heavy bass scene are back in the spotlight" | UK 140 revival (Skream & Benga back together, "patience, weight, and system culture"; Tempa's comeback releases); tearout fused with metal and deathcore (2025-26); hyper-clean, wide melodic records with vocal chops; resampled, glitch-switched drops whose "character" keeps changing; dubstep producers crossing to 170-174 D&B and back (2023) | [S] Ticketfairy 2025, 2026; [UKF 2023](https://ukf.com/read/dubstep-goes-db/); [EDM.com 2026](https://edm.com/music-releases/svdden-death-yvm3-dissent/); [Trench 2024](https://trenchtrenchtrench.com/features/10-acts-pushing-dubstep-fwd-in-2024) |

**The shared core** (holds in every subdivision; lose it and the track stops being dubstep) [S, as above]:
1. Written at 138-150, felt at half time: kick on 1, the snare's weight on 3.
2. A sub-bass that is felt, mono, clean, separate from everything above it.
3. The bass (or bass voices) carries the identity of the track; the drop is where it speaks.
4. Build-and-drop dramaturgy with space: silence and gaps before and inside drops are part of the impact.
5. Loud, dense masters reached by clipping in stages.

## Sound design: the bass in depth
The modern bass is not a patch but a chain: a synthesis core with moving timbre, then distortion, then compression, often printed to audio and processed again (resampling), then split from a clean sub. Sources: Attack Magazine, MusicRadar / Computer Music, EDMProd, Cymatics, Futureproof Genre Explorer (each row).

| Element | What producers do | Numbers | Source |
|---|---|---|---|
| **Wobble** | an LFO on filter cutoff (also volume or distortion) of a sustained note, synced to the tempo; the rhythm of the wobble *is* the riff: the rate changes from note to note (1/4, 1/8, 1/8 triplet, 1/16...) | MusicRadar: LFO synced at **1/8 triplet**, triangle, on a low-pass 6 dB/oct filter, plus an envelope on a second filter and on phase distortion; Sound On Sound 2010: synced **1/8**, 24 dB filter, mono; EDMProd: cutoff LFO at **1/8 dotted**; Mixgraph: "sync wobbles and movement to 16th-note subdivisions" | [S] [MusicRadar](https://musicradar.com/how-to/lfo-wobble-bass), [SOS 2010](https://www.soundonsound.com/techniques/dubstep-secrets), [EDMProd](https://www.edmprod.com/how-to-make-dubstep/), [Mixgraph](https://www.mixgraph.io/bpm-for/dubstep) |
| **FM growl** | one operator modulating another, the modulation index moved by an envelope or LFO (the "honk"), operator feedback for a vocal timbre, unison; FM is "probably the most common technique" for growls | Attack: modulation **100**, a looping envelope on the modulator level as the wobble, bit resolution as grit (under the DX7's 12 bits gets harsher); EDMProd: Serum osc A Warp "FM (from B)", osc B **+2 octaves**; a sound from two sines **31 semitones** apart driven into distortion (Vital forum) | [S] [Attack](https://www.attackmagazine.com/technique/tutorials/dirty-fm-bass/), [EDMProd](https://www.edmprod.com/how-to-make-dubstep/), MusicRadar FM growl; [S, forum] Vital |
| **Wavetable morph** | an LFO or envelope sweeps the wavetable position; warp modes (mirror, sync, FM, bend) | Computer Music's Serum neuro bass: WT position 42, LFO to WT position **55**, LFO "2 bars", retriggered per note, envelope to warp +100 over 1.7 s | [S] [MusicRadar / CM 2016](https://www.musicradar.com/tuition/tech/how-to-create-a-neurofunk-bass-sound-in-xfer-records-serum-640465) |
| **Formant / vowel, the "talking" bass** | a formant (vowel) filter, or a band-pass or low-pass with resonance whose cutoff steps between vowel positions, driven by a stepped LFO; mid-range only ("don't leave too much low end in the sound"); two LFOs at different rates make it "speak" | vowel targets "ah" about 300 and 1,000 Hz, "ee" about 500 and 2,200 Hz (Unison); FM growls are tighter than bitcrushed formants (THE ONE) | [S] [Splice](https://splice.com/blog/creating-talking-wobble-bass-sounds-ableton-live), [Ask.audio](https://ask.audio/articles/how-to-talking-bass-ni-massive), [Unison](https://unison.audio/formant-filters/), Dubspot |
| **Reese** | two or more detuned saws whose phasing beats slowly; from Kevin Saunderson's 1988 "Reese" bassline (made by phase distortion on a Casio CZ-1000) through jungle and D&B into dubstep's deep and neuro sides | LFO on the oscillators' shape at 1/16 dotted to make it drift (Avid reese guide, via search) | [S] [Wikipedia, Reese bass](https://en.wikipedia.org/wiki/Reese_bass); Avid |
| **Neuro** | the D&B-derived technique: a moving wavetable or FM core, then resampling and band-splitting; "extremely difficult - if not impossible" to get "straight out of a synth without further processing and resampling" | the high band takes the modulation, width and distortion while the low stays solid | [S] MusicRadar / Computer Music neurofunk |
| **Resampling** | render the bass to audio, then chop, re-pitch, warp, distort and re-render, serially; tearout's "serial resampling" | none given | [S] Cymatics; Futureproof "Tearout"; Ticketfairy 2026 ("layered resampling") |
| **Distortion and multiband** | bright overdrive so it "cuts harder"; multiband distortion (Ohmicide, Trash, "heavy multiband distortion" in tearout); parallel distortion keeps the bass "without weakening the bass area"; comb filters, flangers and chorus for metallic screeches and the "robotic slap-back" | none given | [S] MusicRadar; MusicRadar on Skrillex and Ohmicide; Futureproof "Tearout"; Cymatics; SOS 2010 |
| **OTT and compression** | heavy compression ("many dubstep examples sit very high in the mix"); multiband OTT on the bass; OTT "for crunch" in riddim | none given | [S] MusicRadar; Futureproof "Tearout"; EDMProd riddim |
| **Pitch movement** | pitch envelopes (dives, rises) on bass notes, portamento between notes (250 ms in the neuro example), octave flourishes at the end of each 4 or 8 bars, sub drops into a section | 250 ms glide; "play the last bar of every four or eight an octave higher" | [S] CM neuro; MusicRadar 2008 |
| **Riddim's motif** | "one tightly sculpted metallic bass motif that loops", square-wave LFO shapes, wide delays, flanger and chorus, "super dark textures" and "space"; the sub follows the motif's envelope; chops of a bass loop pitched to a melody, each faded around the kick and clap | sub level LFO at **1/4** (EDMProd) | [S] Futureproof "Riddim"; Wikipedia "Riddim (genre)"; [EDMProd riddim](https://www.edmprod.com/how-to-make-riddim/) |
| **Colour bass** | heavy growls made to **ring as chords**: through vocoders, resonators, granular processing and pitch-mapping, or written as chords on the growl patch; major-leaning, extended chords (add9, maj7) | none given | [S] [Futureproof "Colour bass"](https://genreexplorer.futureproofmusicschool.com/genre/colour-bass); search summary of genre guides |
| **Call and response** | two (or more) bass voices answer each other inside a drop: a stab or growl phrase, then a contrasting voice (screech, reese, talking bass) in the gap; drums thin out when the bass is busy and fill in when it rests | "Keep beats sparse when the bass is busy" | [S] MusicRadar 2008 (tip 12); the call-and-response naming is craft [H] |

**Mid-bass versus sub, the mono point** [S]: a sine sub duplicated from the bass line, no filters or effects, sidechained to the kick (Cymatics) and following the mid-bass's envelope (EDMProd); everything else high-passed at about 100 Hz (Cymatics) and the sides cut at 150-180 Hz (Futureproof); widening only high up (Skrillex: above 7 kHz). Sub fundamental 40-60 Hz (sub-bass guides). **For Spectre:** sub mono and clean (`sub`), mid-bass layers high-passed 100-150 Hz with `mseq` `side_hpf` 150-180, the master's `mono_below` 150 [H, inside the sourced range].

## Drums
| Part | Practice | Source |
|---|---|---|
| Pattern | kick on 1, snare / clap on 3 of the 140-bpm bar (half-time), ghosted kicks and shuffled 16th hats in UK strands; riddim: a quieter kick also on 2 and 4 "creates the whack"; kick often layered on the snare in riddim ("marching, stomping"); tearout: "a chest-thumping sub kick on beat one", a pan snare on three | EDMProd riddim; Futureproof "Riddim", "Tearout"; Cymatics [S] |
| Snare | the dubstep snare is a **body near 200 Hz** with a sharp transient and a tail: "start with a 909 and compress it to get the harmonics of that 200-hertz note", "tune it at about 200, and shelve off a lot of that stuff above 200", one or two layers that don't clash, a clap or china shelved high with reverb on top, printed and recompressed; tearout's "sharp, metallic pan snare" with a "long white-noise tail"; gated reverb on the snare | [iZotope, Skrillex 2011](https://izotope.com/en/learn/skrillex); Futureproof "Tearout"; Cymatics [S] |
| Clap | a bright clap with reverb plus a thicker layer with a short tail and a snare for weight, the group clipped; melodic riddim uses kick and clap rather than a single snare | EDMProd riddim; Wikipedia "Riddim (genre)" [S] |
| Kick | layered, high-passed and limited so transients don't poke through; tuned layers ("out-of-phase kicks sound thin"); boxy 300-500 Hz scooped, a little at 1 kHz for click | EDMProd riddim; Cymatics; Futureproof mixing [S] |
| Hats and percussion | offbeat hats with a second layer, clipped, below kick and clap; swung, syncopated hats in colour bass; trap hats in hybrid and 140 revival acts; triplet percussion in riddim; "broken drums" and breakbeat chops (jungle) in the 140 scene | EDMProd; Futureproof; Trench 2024 [S] |
| Timing | UK roots: snares "slightly late" for a "lazily syncopated" feel; heavy US strands: grid-tight | MusicRadar 2008 [S]; the contrast [H] |
| Build | a clap on every beat, kick rolls that double after 4 bars and again after 2, drum elements removed before the drop "to create a silence gap", reverse sweeps, a bass tease, a pre-drop vocal | EDMProd riddim and dubstep guides [S] |

## Layering and EQ carving (PRODUCTION.md checklist items 1-3, 5)
**Layer roles** [S where cited, else H]:
| Part | Layers and what each supplies | Must *not* |
|---|---|---|
| Sub | one sine (or a sine with a little 2nd/3rd harmonic for phones), mono, 40-60 Hz fundamental, following the bass's notes and envelope, sidechained to kick and snare | carry distortion, width or the riff's timbre |
| Mid-bass (the lead) | 1-3 voices per sound: a body (FM or wavetable growl, 100 Hz-1 kHz), a bite (distorted upper layer, 1-4 kHz), optionally a screech or noise top (4-10 kHz, comb or flanger), each high-passed at about 100 Hz; a second sound for the response | reach under 100 Hz; be wide below 150-180 Hz |
| Kick | sub layer (tuned near the key, 45-60 Hz), punch (100-200 Hz), click (2-5 kHz) | fight the sub: tune and sidechain |
| Snare / clap | body near 200 Hz (909-style), crack 2-5 kHz, a clap or china top shelved high, a tail (room or gated reverb) | a boxy 300-600 Hz |
| Hats, percussion | metallic tones above 6-8 kHz, sparse | a hiss bed |
| Atmosphere | pads, choirs, drones, foley, granular textures in intros and breakdowns, dark and filtered | sit in the drop's mid-bass range |
| Voice | chopped, pitched phrases, a pre-drop call, a hook in melodic strands | a sung song (standing rule 15) |
| FX | risers, reverse sweeps, impacts, sub drops, downlifters, silence | stack all at once on every build |

**EQ map** (proposed `dubstep` entry for engine/eqmaps.json in the proposal; ranges are starting points):
| Role | High-pass | Cut or control | Owns | Source / cross-check |
|---|---|---|---|---|
| kick | 25-30 Hz | 300-500 Hz | 45-80 Hz, 100-200 Hz, 1-5 kHz | Futureproof mixing (scoop 300-500, a little at 1 kHz); the trance and hip-hop maps (engine/eqmaps.json) agree on 200-500 cut |
| sub | 20-25 Hz | above 100-150 Hz (low-pass) | 30-80 Hz | Cymatics (sine, the main sound high-passed at 100); sub guides 40-60 Hz |
| upper-bass (mid-bass) | 90-150 Hz | 200-300 Hz narrowly against kick and snare | 300 Hz-3 kHz | EDMProd (narrow cuts 100-300 Hz, a boost at 1-3 kHz if it doesn't cut); Cymatics (high-pass at 100) |
| snare | 100-150 Hz | 300-700 Hz | 180-250 Hz, 2-5 kHz, 8-12 kHz | iZotope / Skrillex (body at 200 Hz, shelve above it); hip-hop map (150-250 Hz owned) |
| clap | 150-250 Hz | 400-800 Hz | 1-8 kHz | EDMProd (EQ out the lows); hip-hop map |
| hats | 500-2000 Hz | 3-6 kHz | 8-14 kHz | Futureproof (low-cut hats); hip-hop map |
| pad, choir, strings | 200-300 Hz | 200-500 Hz | 1-3 kHz, 8-16 kHz | Mixgraph (high-pass mid-range elements, separation below 200 Hz); trance map |
| lead, pluck | 200-300 Hz | 300-600 Hz | 1-4 kHz | trance and hip-hop maps (no dubstep-specific source) [H] |
| vocal | 100-150 Hz | 200-400 Hz | 2-5 kHz | docs/voice/MIXING.md; hip-hop map |
| return | 200-500 Hz | 300-600 Hz | (low-pass 6-12 kHz) | Futureproof ("cut the low end from the send"); trance map |
Disagreements kept: Cymatics high-passes the mid-bass at 100 Hz, Futureproof cuts only the sides at 150-180; both are compatible (mid below 100 Hz is the sub's; 100-180 Hz is mono mid-bass) [H, reading].

**Glue** [S]: drum groups (claps, hats, kick) clipped (EDMProd riddim); the bass group through OTT or multiband compression and saturation (EDMProd, Futureproof "Tearout"); the sub sidechained to kick (and snare) with a release of about 200-400 ms at 140 bpm (Mixgraph) or chopped around the hits; transient shaping on drums; a clipper rather than a hard limiter on the master (Futureproof, Infekt). Reverb and delay are composition tools in the UK strands (dub's legacy: Futureproof "Dubstep"), short and controlled in the heavy US strands.

**Low end and top end facts** (checklist item 5) [S]: kick fundamental 45-60 Hz; sub 40-60 Hz, mono; the snare's body at 200 Hz; the top from metallic mid-bass harmonics, screeches and hats (tonal content), not hiss; widening above 7 kHz.

**Characteristic imperfection** (item 6) [S, H]: UK strands: lazy, late snares, swing, degraded samples (lower sample rate and bit depth, "deliberately lower quality" time-stretching: MusicRadar 2008); heavy strands: grid-tight, with the imperfection in the sound (distortion, digital artefacts, resampling glitches). Wrong in every strand: a sub that wanders in level or phase, a wide sub, clipping that crackles on the sub's waveform (as opposed to shaved transients).

**Census of a reference arrangement** (item 8): no published multitrack breakdown of a modern dubstep record was found; EDMProd's riddim walk-through (a reference-based map: one bass chop group plus its sub, a kick group, a clap group, hats, an atmosphere bed of pad, choir and foley) is the nearest, about 6-8 sources at once in a drop [S, counted from the article]. **Remix table** (item 9): no earlier Spectre track is dubstep; the hip-hop tracks share the half-time body but nothing in them changes with this brief.

## Strands of the modern era (2015-2026)
| Strand (craft schools; when) | Tempo | Drums | Bass | Form | Mastering | Source |
|---|---|---|---|---|---|---|
| **Deep / 140 (UK; DMZ, Deep Medi, Tempa, Encrypted Audio, Crucial; revived 2023-26)** | 140 ("138-142 or slower") | minimal half-time, swing, "broken drums", breakbeat chops, garage hats | "cavernous sub-bass" as "the whole conversation", Coki- and Benga-style wobbles, "almost no mid-range noise or metallic distortion" | DJ-led, patient, "dread-heavy space", reverb and delay as composition | sound-system weight over level: see the measurements | [S] Futureproof "Deep dubstep"; Trench 2024; Ticketfairy 2025 |
| **Riddim** (and briddim, liquid riddim; Croydon early 2010s, US breakthrough about 2015) | 140-150 | triplet / tuplet percussion, kick on the snare, a quieter kick on 2 and 4 | one looping metallic motif, square LFOs, wide delays, flanger and chorus; briddim adds brostep sound design to riddim's heavy kick and snare | 8-bar drop halves (1A/1B), false drops; the motif changes by processing, not new sections | loudest end | [S] Wikipedia "Riddim (genre)"; Futureproof; EDMProd |
| **Tearout / deathstep** (deathstep named 2011; tearout early-mid 2010s, absorbing deathstep, riddim, brostep 2016-19; metal and deathcore crossover 2025-26) | 138-150 | sub kick on 1, metallic pan snare with a long noise tail on 3 | FM and wavetable in Serum, serial resampling, heavy multiband distortion, machine-gun stabs, comb-filtered screeches, multiband OTT | "hard, mechanical drops", switches every few bars | loudest end | [S] Futureproof "Tearout", "Brostep / tearout"; EDM.com 2026; Ticketfairy 2025 |
| **Melodic dubstep** (US, early 2010s; Seven Lions, Illenium; chart years 2017-18; hyper-clean 2023) | 135-150 | half-time skeleton, not trap | heavy sub and "aggressive mid-range FM growls" under supersaw stacks, cinematic pads, plucky arpeggios | a real vocal hook; vocal and chords set up "beauty and brutality" in one drop | wide, clean | [S] Futureproof "Melodic dubstep"; Ticketfairy 2026 |
| **Colour bass / melodic riddim** (Chime's Rushdown 2016; Monstercat early 2020s) | 140-150 | kick and clap, swung syncopated hats | growls that ring as chords (vocoders, resonators, granular, pitch-mapping), bright, detuned | riddim-like drops with harmony | | [S] Wikipedia; Futureproof "Colour bass" |
| **Hybrid / trap crossover** (EDM trap from 2012; trap hats in the 140 revival) | about 140 | 808s, hat rolls, trap snares beside half-time dubstep drops | 808 sub plus dubstep mid-bass | build-and-drop, drops alternating trap and dubstep | | [S] Wikipedia "EDM trap"; Trench 2024 |
| **D&B-switch hybrids** (2023-) | 140-150 switching to 170-174 | half-time to D&B breaks within a track ("a big switch at the 2:15 mark") | neuro and reese | tempo-switch drops | | [S] UKF 2023 |
| **Experimental / "wook" bass** | | | | | | **not sourced**: no source found that defines it as a strand with checkable elements (searched 2026-11-25); left out of the recommendations |

**Elements, shared or varying** (2015-2026):
| Element | Shared | Varies | Label |
|---|---|---|---|
| Tempo | half-time feel; 138-150 | 140 in deep / 140 and colour bass; up to 150 in riddim, tearout, melodic; the catalogue median 140 to 2018, 145-148 since 2019 (riddim 145); Mixgraph's yearly peak 150 in 2017 | [M] catalogue, Mixgraph; [S] strands |
| Length | the original mix, no extended habit | shorter since 2018 (3:42 in 2020-21 against 4:06 in 2014-16); riddim shortest (3:39), melodic longest (4:18) | [M] catalogue |
| Sub | clean, mono, 40-60 Hz | its share of the mix: dominant in deep, under the mid-bass in heavy strands | [S]; the measured low end in "Catalogue measurements" [M] |
| Mid-bass | the lead | absent or a soft wobble (deep) / one motif (riddim) / many switching voices (tearout) / chords (colour bass) / under supersaws (melodic) | [S] |
| Drop length | 8-bar halves | 16 bars in EDMProd's riddim map; 16-32 elsewhere [S, H] | [S] |
| Second drop | differs from the first | how much: new drums, new bass, or a different strand ("switching to a different bass genre") | [S] Cymatics |
| Voice | chops, calls | a real vocal hook only in melodic dubstep; mostly instrumental in UK roots ("vocals stripped out") | [S] Futureproof |
| Loudness | loud | see "Mastering per subdivision" | [M] |

## Arrangement, length and versions
- **Intro**: 8-32 bars: atmosphere (pads, foley, choir, a vocal chop with delay and reverb), a theme, or for DJs a beat; the drop typically near bar 32 (about 55 s at 140) [S: Wikipedia; EDMProd].
- **Build**: 8 bars (16 with a synth and a drum build), with a clap on every beat, kick rolls doubling, a reverse sweep, a pre-drop vocal, often a **false drop** of 4 bars before the real one [S: EDMProd riddim and dubstep].
- **Drops**: 16 bars in two 8-bar halves (1A, 1B) with a switch at the half, sometimes 24-32 (1A-1C) [S: EDMProd]; the switch changes the bass voice, the drum loop or the rhythm.
- **Mid-section**: 8-16 bars of breakdown or a melodic section, then a build [S: Wikipedia's intro, main, midsection, second main, outro].
- **Second drop**: varies the first: "keeping the first bass pattern but changing the drum loops, or moving into a different bass style entirely" [S: Cymatics]; a **VIP** is a later reworked version of a track (a new drop, new bass) released as its own version (craft usage; see "Catalogue measurements" for how often the word appears).
- **Outro**: 8-16 bars [S: EDMProd]; DJs blend dubstep over 16-32 bars at the 70-bpm feel (Mixgraph) [S].
- **Length and versions**: one version, the original (extended mixes and radio edits under 0.5% of tagged releases; remixes 11%); measured in "Catalogue measurements".

## Vocals (standing rule 15: voices are instruments)
Dubstep vocals are chopped, pitched phrases that "give a track its edge" (Output) [S]; UK roots inherited garage's habit of stripping vocals out (Futureproof) [S]; the build carries a "pre-drop vocal" (EDMProd) [S]; melodic dubstep is vocal-led ("a real vocal hook") [S]; the 2023 melodic sound has "vocal chopping floating over the rhythm" (Ticketfairy) [S]; formant-shifted voices (a voice moved "a little more female", or a "low, pitched-down, formant-shift character": Virtual Riot on his vocal processing, [Antares](https://www.antarestech.com/blog/virtual-riot-interview)) [S]. For Spectre: `singer` or `vox2` phrases of a few words, pitched and chopped (`gate`, `pitch` fx), a pre-drop call, a wordless choir in intros; formant shifting is a gap (Engine mapping).

## Catalogue measurements
Measured 2026-11-25 for this brief from the open catalogue (method: docs/MASTERING.md "Era targets"; `tools/catalogue_stats.py tag` and `tools/refcurve.py catalogue`, MusicBrainz tag and first-release year joined to AcousticBrainz; no audio downloaded). Lengths are AcousticBrainz's file lengths of tracks of 90 s and more; tempo is Essentia's estimate folded into 100-200 bpm (it often reads half or double time); loudness is estimated from ReplayGain (LUFS ≈ -23.7 - RG, ±1-2 dB) and is **whole-track** loudness, not the loudness of the drop. Data ends in 2021; tags are user-applied and broad.

**By era** (tag `dubstep`, up to 300 recordings per year; tracks with AcousticBrainz data in brackets) [M]:
| Years | Tracks | Length, median (middle half) | Tempo, median (middle half) | Est. LUFS, median (middle half) |
|---|---|---|---|---|
| 2005-2007 | 680 (625) | 4:21 (3:06-5:07) | 140 (139-144) | -12.7 (-15.0 to -10.9) |
| 2008-2010 | 835 (652) | 4:36 (3:38-5:23) | 140 (138-142) | -11.8 (-13.8 to -10.1) |
| 2011-2013 | 796 (622) | 4:33 (3:53-5:09) | 140 (138-140) | -10.3 (-12.3 to -8.9) |
| 2014-2016 | 847 (710) | 4:06 (3:31-4:46) | 140 (130-150) | -10.5 (-12.5 to -8.7) |
| 2017-2019 | 579 (306) | 4:02 (3:30-4:50) | 140 (128-150) | -9.8 (-12.0 to -8.4) |
| 2020-2021 | 340 (155) | **3:42** (3:15-4:21) | **145** (140-150) | -9.9 (-11.9 to -8.3) |
Year by year (same source): the median tempo is 140 every year from 2006 to 2018, then 148 (2019), 145 (2020), 145 (2021); the median length falls from 4:31-4:40 (2007-2012) to 4:03-4:08 (2014-2017) and 3:30-3:59 (2018-2021); the loudest year is 2019 (-8.7). This is why the modern era is split at 2019 above.

**By strand tag** (first release 2008-2021, up to 200 per year; the tags are thin and partly overlapping; `riddim` could include reggae riddims, but its tempo and loudness are dubstep's) [M]:
| Tag | Tracks | Length | Tempo | Est. LUFS | Reading |
|---|---|---|---|---|---|
| `riddim` | 361 (81) | **3:39** (3:10-4:10) | **145** (144-150) | **-7.6** (-8.8 to -6.3) | the loudest and shortest |
| `brostep` | 1,169 (614) | 4:09 (3:36-4:47) | 140 (140-150) | -8.7 (-10.3 to -7.4) | |
| `melodic dubstep` | 387 (237) | 4:18 (3:47-5:09) | 140 (140-150) | -9.3 (-10.6 to -8.1) | longer, quieter |
| `tearout` | 105 (76) | 3:52 (3:07-4:46) | 140 (140-140) | -10.6 (-13.1 to -8.3) | the tag mixes the early-2010s "tear-out" usage with the modern strand: weak |
| `deathstep` | 29 (13) | 4:41 | 140 | -9.3 | too few to use |
| `future garage` (the UK neighbour) | 279 (202) | 4:32 (3:55-5:19) | 132 (126-139) | -12.4 (-13.8 to -10.8) | the quiet, slower UK side |
| `colour bass` | 53 (21) | 4:20 (3:44-5:20) | **150** (145-150) | -9.7 (-10.2 to -9.0) | thin (21 tracks); `color bass` failed (MusicBrainz 503 twice) |
| `deep dubstep` | (4 with data) | | | about -12 | too few tagged recordings with AcousticBrainz data; the stats run failed (503); the roots era (2005-10, -12.2) and `future garage` (-12.4) stand in |

**Tonal balance** (1/3-octave target curves fitted to the Bark medians, dB re 1 kHz; files in the proposal) [M]:
| Hz | `dubstep_2005` (2005-10, 1,277) | `dubstep_2011` (2011-14, 866) | **`dubstep_2015`** (2015-21, **927**) | `dubstep_2018` (2018-21, 346) | riddim (81) | brostep (605) | melodic (237) |
|---|---|---|---|---|---|---|---|
| 31.5 | +7.5 | +6 | +5 | +6 | +8.5 | +5.5 | +2 |
| 40 | +9.5 | +8 | +6.5 | +7 | +8 | +7 | +4 |
| 50 | +11 | +9.5 | +8 | +8 | +7.5 | +8 | +5.5 |
| 63 | +11 | +9.5 | +8 | +8 | +6 | +7.5 | +5.5 |
| 80 | +9 | +7.5 | +6.5 | +6.5 | +4.5 | +6 | +4.5 |
| 100 | +6.5 | +5.5 | +4.5 | +4.5 | +3 | +3.5 | +2.5 |
| 125 | +4.5 | +3.5 | +2.5 | +2.5 | +2 | +2 | +1 |
| 160 | +3.5 | +2.5 | +2 | +2 | +1 | +1.5 | +0.5 |
| 250 | +1.5 | +1.5 | +1 | +1 | -0.5 | +0.5 | 0 |
| 500 | +0.5 | 0 | +1 | +1 | -1 | -0.5 | 0 |
| 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2000 | -1 | -1.5 | -2 | -2 | -0.5 | -1 | -2 |
| 3150 | -2.5 | -2.5 | -3.5 | -3 | -1 | -1.5 | -3.5 |
| 5000 | -3.5 | -2.5 | -4.5 | -4 | -1 | -2 | -4 |
| 8000 | -4.5 | -3 | -5 | -4.5 | -1.5 | -2 | -4 |
| 10000 | -6 | -4 | -6 | -5.5 | -2.5 | -2.5 | -5 |
| 12500 | -8.5 | -6.5 | -8 | -7.5 | -4 | -5 | -7 |
| 16000 | -12.5 | -10 | -12.5 | -12 | -7 | -8.5 | -11 |
| Est. LUFS | -12.2 | -10.2 | **-10.3** (-12.3 to -8.5) | -9.6 | -7.6 | -8.7 | -9.3 |
Fit residuals 0.13-0.19 dB mean, at most 0.8-1.2 dB per band; lossless share 18-19% (2005-14), 53-60% (2015-21 and the strands).

Reading it:
1. **The roots carry the most sub** (+11 dB at 50-63 Hz over 1 kHz in 2005-10), the **brostep years the brightest top** (2011-14: 1-2 dB more at 3-10 kHz than 2015-21), and the modern catalogue sits between: about 3 dB less sub than the roots and a darker top than brostep. The sub-to-mid story of the sources ("from sub-bass to the middle register", Reynolds) is visible as a falling 50-63 Hz band, 2005-10 to 2015-21.
2. **2018-21 against 2015-21: within 1 dB in every band** (+1 at 31.5 Hz, +0.5 at 2.5-10 kHz). The 2019 turn shows in tempo, length and loudness, not in the tonal balance.
3. **The strands differ more than the years**: riddim is the flattest and brightest (3.5-5.5 dB more at 5-16 kHz than `dubstep_2015`, 2 dB less at 63-100 Hz, more under 40 Hz) and the loudest; melodic dubstep has 2.5-3 dB less sub at 31.5-63 Hz; brostep is 2-3.5 dB brighter at 3-10 kHz.
4. **Against the engine's targets**: `trance_2015` reads within 1.2 dB of the dubstep catalogue in every band (mean 0.4 dB; 1.1-1.2 dB too bright at 7.7-12 kHz, 1.1 dB short at 32-97 Hz); `hiphop_2015` is 1-2 dB too dark at 3-12 kHz and 4 dB at 12-15.5 kHz (`refcurve.py check`). So the catalogue's electronic genres share a spectrum; a dubstep master on `trance_2015` would miss by about 1 dB, but the genre gets its own measured curve (PRODUCTION.md checklist item 4).

**Versions** [M] (MusicBrainz, 12,472 recordings tagged `dubstep`, counted 2026-11-25; lengths from MusicBrainz): titles with "VIP" 97 (0.8%; median 3:55, middle half 2:34-4:59), "Original Mix" 34 (0.3%; 4:27), "Extended Mix" 15 (0.1%; 5:05), "Radio Edit" 43 (0.3%; 3:33), "Remix" 1,406 (11.3%; 4:22 over 293). So dubstep releases **one version**, the original, at the lengths above; extended mixes and radio edits are rare (against trance, where extended mixes are a fifth of releases), remixes are common (one in nine), and a VIP is about as long as an original. The brief's length is therefore the original mix's.

## Mastering per subdivision (PRODUCTION.md section 5, item 10)
**What was measured and what was not.** Whole-track loudness and the tonal balance per era and strand come from the catalogue above (to 2021); the loudness of the loud section from Mixgraph's store previews (current catalogue, years not stated); true peak, PLR, LRA and width have **no dubstep-specific measurement** (AcousticBrainz has no true peak; previews are lossy). Where a value below is a source's practice rather than a measurement it says so.

| Subdivision | Whole track, est. LUFS | Loud section | How the loudness is reached | Low end, width | Top end | Playback | Label |
|---|---|---|---|---|---|---|---|
| **UK roots (2005-10) and deep / 140** | -12.7 to -11.8 (2005-10); the UK neighbour `future garage` -12.4 | no deep-only preview figure; deep dubstep on Beatport sits in other genres | weight over level: sound-system playback, "on the right system, very loudly"; reverb and delay tails kept | the most sub of any period (+11 dB at 50-63 Hz over 1 kHz), mono | `dubstep_2005`: about 1 dB brighter than 2015-21 at 2-6 kHz, the same above 10 kHz | sound systems, dubplates, pirate radio | [M] catalogue; [S] Trench 2024, Futureproof |
| **Brostep (2011-14)** | -10.3 (2011-13; `brostep` tag across 2008-21: -8.7) | | the festival PA; "sit very high in the mix", heavy compression | sub 1.5 dB under the roots | the brightest era (`dubstep_2011`) | festival PA, downloads | [M]; [S] MusicRadar wobble |
| **Modern, 2015-18** | -10.5 (2014-16) | Dubstep previews **-6** (-6.5 to -4), the loudest club genre | clip first, a gentle limiter after; clipped drum groups | mono sub; sides cut at 150-180 Hz; width above | `dubstep_2015` | clubs and festivals (no normalisation), streaming turns it down to -14 | [M] catalogue, Mixgraph; [S] Infekt, Futureproof, EDMProd |
| **Modern, 2019-22** | -9.9 (2020-21; 2019: -8.7) | as above | as above | as above | `dubstep_2018` (within 1 dB of `dubstep_2015`) | as above | [M] |
| **2023-26** | not measured | as above (current catalogue) | as above; "surgical precision", silence as impact | not measured | not measured: `dubstep_2018` extrapolated | as above | [M] Mixgraph; [S] Ticketfairy |
| **Riddim (and the loudest heavy strands)** | **-7.6** (-8.8 to -6.3) | as above | heavier clipping; one motif, flat and dense | 2 dB less at 63-100 Hz, more under 40 Hz | 3.5-5.5 dB brighter at 5-16 kHz than `dubstep_2015` | clubs | [M] (81 tracks: about ±1 dB) |
| **Tearout / deathstep** | not usable (thin, mixed tags); nearest: `brostep` -8.7, riddim -7.6 | as above | "multiband OTT compression", multiband distortion in the mix | | brighter than the modern median (as brostep) [inferred] | festival PA | [S] Futureproof; [M] weak |
| **Melodic dubstep, colour bass** | -9.3 (-10.6 to -8.1); colour bass -9.7 (21 tracks) | | as the modern strands, clean and wide | 2.5-3 dB less sub at 31.5-63 Hz | as `dubstep_2015` | festivals, streaming | [M] (237 tracks) |
| **D&B-switch hybrids** | not measured; D&B previews -6.5 | | | | | | [M] Mixgraph |

**Shared, varying:** loudness varies **by strand** (riddim -7.6 to melodic -9.3 to the UK side -12) and rose with the era (-12.7 to -9.9 from 2005-07 to 2020-21); the tonal balance varies by strand (riddim brighter and flatter, melodic lighter in the sub) more than by year since 2015; the method (clipping before limiting, clipped groups, a mono sub) is shared by every heavy strand [S]; true peak: club masters commonly exceed 0 dBTP (100 top-label Beatport tracks: +0.01 to +5.5 dBTP, Dance Music NW 2018, docs/TRANCE.md "Mastering"), Spotify asks -1 dBTP (-2 above -14 LUFS) [M, S]; one master serves club and streaming as far as any source shows (no separate streaming master found) [S, not sourced further].

**Settings per kind of brief** (proposed for `engine/genres.json`, `master_by_strand`):
| Brief | Flags with `--genre dubstep` | Why |
|---|---|---|
| modern, no strand named (default) | `--target dubstep_2015 --lufs -8 --tp -1` | target measured on 927 tracks 2015-21; -8 integrated is a choice between the measured whole-track median (-10.3; upper quartile -8.5) and the loud previews (-6), assuming a drop 1.5-2 dB above the integrated level [H; untested in the engine] |
| newest sound (2019-26, bleeding edge) | `--target dubstep_2018 --lufs -8 --tp -1` | 2018-21 within 1 dB; 2022-26 extrapolated |
| riddim, tearout, briddim | `--target dubstep_riddim --lufs -7 --tp -1` (only with clipped drum and bass buses) | riddim whole tracks -7.6 [M, thin]; -7 is [H] |
| melodic dubstep, colour bass | `--target dubstep_melodic --lufs -8.5 --tp -1` | melodic whole tracks -9.3 [M] |
| deep / 140, UK roots | `--target dubstep_2005 --lufs -10 --tp -1` | 2005-10 whole tracks -12.2, future garage -12.4; the newer 140 scene unmeasured; -10 [H] |
| this brief (deep frame, heavy drops, absence) | `--target dubstep_2015 --lufs -8.5 --tp -1`; read the loudest 2 minutes, aim about -6.5 to -6 short-term in drop 1 | a long near-silent outro lowers the integrated level, so a fixed integrated target would push the drops harder: check the drop's short-term loudness and lower `--lufs` rather than let the master crush the fight [H] |
`eq` 0.7 and `translate` 0.4 as in trance [H]; `mono_below` 150 Hz (sides cut at 150-180 Hz, Futureproof; the trance master uses 120) [S, H].

## Bleeding edge (2024-2026): a checklist
| # | Element | Source | Engine today |
|---|---|---|---|
| 1 | **Tempo 145-150** for the US strands (catalogue median 145-148 since 2019), **140** for the UK revival; half-time | [M] catalogue, Mixgraph; [S] Trench 2024 | yes |
| 1b | **Length 3:30-4:00** (2020-21 median 3:42) | [M] catalogue | yes |
| 2 | **Drops whose character keeps changing**: layered resampling, complex modulation, glitch-like transitions inside a drop | [S] Ticketfairy 2026 (on a 2025 record) | **partly**: switches by layers and patterns; no resampling, no tempo-synced modulation |
| 3 | **Precision and silence**: "clean metallic textures", "the silence between phrases carries as much impact as the phrases" | [S] Ticketfairy 2026 | yes (`exit` `silence`, `cut`, gaps in patterns) |
| 4 | **Control and minimalism** in the UK revival: "patience, weight, and system culture"; minimal against pop aesthetics | [S] Ticketfairy 2025, 2026 | yes (`sub`, sparse drums) |
| 5 | **Metal and deathcore fusion** in tearout (2025-26): distorted bass that "contorts and convulses between punishing drums", "ominous tension" before the drops | [S] EDM.com 2026; Ticketfairy 2025 (a "metal-infused dubstep album") | **partly**: `eguitar` exists; the bass side needs the gaps below |
| 6 | **Hyper-clean, wide melodic** records with vocal chops floating over the rhythm | [S] Ticketfairy 2026 (on a 2023 record) | yes (`supersaw` model 2, `singer`, `vox2`, `gate`) |
| 7 | **Warping bass stabs, abstract percussion, textures panning across the stereo field** instead of one screech | [S] Ticketfairy 2026 (on a 2025 record) | partly (`lfo` pan on `polysynth`; no warp) |
| 8 | **Tempo switches** to 170-174 inside dubstep tracks | [S] UKF 2023 | yes (section `bpm`) |
| 9 | **Sound design as an "immersive, high-art experience"** (Thys's VIER, 2025) | [S] Ticketfairy 2025 | no (needs FM / wavetable / resampling) |
| 10 | **Loud masters by clipping**: loud sections about -6 LUFS (-6.5 to -4); whole tracks louder since 2019 (-8.7 to -9.9) | [M] Mixgraph, catalogue; [S] Infekt, Futureproof | **untested**: the engine's master has reached about -7.5 in a trance drop |
| 11 | **Tonal target** `dubstep_2018` (346 tracks 2018-2021, within 1 dB of `dubstep_2015`; 2022-26 extrapolated) | [M] catalogue | proposed |

## The strand for this brief: "a soul taken and held captive"
The brief: *the feeling of your soul being taken and held captive against your own will: the fight, the panic, and eventually the cold acceptance and finally the absence the struggle brings with it.*

**Recommendation: a deep / 140 frame (tempo, space, the sub as the subject) that carries two heavy strands inside it, tearout for the fight and riddim for the acceptance, with the absence returning to the deep strand's emptiness; 140 bpm.** [H, reasoned from the strands above]
- *The fight* needs two forces: call and response between two bass voices (the captor and the soul) in drop 1, tearout's switching voices and machine-gun stabs, the answers cut off before they finish. Tearout's "hard, mechanical drops" and metal-adjacent aggression carry struggle better than any other strand; the deep frame keeps it from turning into festival spectacle.
- *The panic* is a rise in rate, not in tempo: the same 140, but the subdivision climbs (the wobble from 1/4 to 1/8 triplet to 1/16, the stabs to 1/16 triplets, hats doubling), and the bass's modulation is pushed up into the **roughness range, 30-150 Hz amplitude modulation**, the acoustic niche human screams occupy and that listeners rate as most alarming (Arnal et al., *Current Biology* 2015: screams "occupy a privileged niche" between about 30 and 150 Hz modulation rates; speech sits at 4-5 Hz; roughness tracked how "disturbing" sounds were rated and amygdala activity) [S]. A wobble LFO run up into that range stops being a wobble and becomes a scream inside the bass. A brief D&B-style switch (section `bpm` to 170-174 for 4-8 bars, a 2023-26 device: UKF) is the alternative panic device [S, H].
- *Cold acceptance* is riddim's principle: **one motif that loops** and changes only by modulation ("Repetition is the point, not a bug"). In drop 2 the struggle is gone: one voice, no response, the same phrase over and over, narrower, the roughness drained out of it, a darker filter, a steady sub. Captivity accepted is the motif that no longer tries to change. Not the melodic strand: its "beauty and brutality" and vocal hook resolve into hope and catharsis, which the brief does not ask for.
- *Absence* is the deep strand's "dread-heavy space" taken to its end: the mid-bass leaves first, then the drums, then the sub; what is left is the reverb and a frozen grain cloud of the motif (`granular` with `scan` 0), and finally silence. The sub's absence is felt as a physical loss on a system, the genre's own way to say "gone".

**Arc of drops and breakdowns** (128-144 bars = 3:39-4:07 at 140; counts [H] inside the sourced form):
| Section | Bars | Feeling | What happens |
|---|---|---|---|
| Intro | 16 | the soul before | a sparse deep-140 beat or no beat, a pad or choir fragment, a short vocal phrase (the soul's own), the sub's first notes; the motif heard once, clean |
| Build 1 | 8 | the taking | the captor's voice appears (a low growl under the pad), the vocal phrase cut short, a false drop of 2-4 bars |
| Drop 1 (A+B+C) | 24 (8+8+8) | **the fight** | call and response between two bass voices, tearout weight; at 1B the response gets shorter, the captor's calls longer; at 1C the response is cut off mid-phrase |
| Switch / panic | 8 | **the panic** | subdivisions climb, the modulation goes rough (30-150 Hz), hats double, optionally 4-8 bars switched to 170-174; ends in a hard cut to silence |
| Breakdown | 16 | exhaustion | the vocal phrase returns pitched down and formant-darkened, alone with the sub; the motif in slow motion (granular `scan` 0.25) |
| Build 2 | 8 | resignation | no riser, no roll: the build *loses* energy (the opposite of a festival build), a filter closing; one beat of silence |
| Drop 2 (A+B+C) | 24-32 | **cold acceptance** | riddim: one motif looping, mono, darker, no response voice, kick and snare only, the sub steady; the motif slowly loses harmonics across the drop (section `auto` of `cutoff`, `drive`) |
| Outro | 24-32 | **absence** | the mid-bass stops; drums stop; the sub holds, then stops; a frozen grain cloud of the motif and the room fade; the last bars are silence or near-silence |

**Nearest wrong feelings** (editorial [H]; what separates each from the brief):
| Wrong feeling | What it sounds like | What separates the brief |
|---|---|---|
| **A horror trailer** | braams, shrieks, jump-scare hits, a low drone with no groove, a ticking clock, a final stinger | the struggle has a body: a half-time groove and riffs that fight back; dread comes from inside the music (the motif that stops answering), not from illustration; no stingers, no jump scares |
| **Generic festival brostep aggression** | every drop at maximum, "bro" shouts and air horns, triumphant riffs, the second drop a copy of the first and louder | energy *falls* across the track: drop 2 is colder and simpler than drop 1, the build into it loses energy; aggression is a fight that is lost, not a celebration |
| **A video-game boss-fight cliché** | orchestral hits and choir "aah" stabs on the downbeats, a heroic minor-key lead, 8-bit bleeps, a phase-two escalation that ends in victory | no hero and no victory: no heroic lead melody, no escalation into triumph; the "second phase" is surrender |
| **Sad ambient** | beatless, warm minor pads, piano, tears | acceptance is *cold*, not sad: no warm pads or piano in the drops, the beat and the motif carry on mechanically; absence is a removal heard against weight, not a lament |
| **Edgy shock value without feeling** | screams and gore samples, random violence, harsh noise for its own sake, distortion everywhere all the time | every harsh sound has a place in the arc and is taken away later; the roughness peaks once (the panic) and drains; the voice is the soul's, not a scream sample |
| also: **melodic-dubstep catharsis** | supersaw chords and a vocal hook that lift into release | the brief ends in absence, not hope: no major lift, no sung resolution |

**Nearest wrong sounds** (checklist item 7) [H, from the sections above]: the 2010-era LFO wobble on a filtered saw as the main bass (reads 2011 brostep); a constant noise riser plus snare roll plus "drop" vocal shout on every build (festival EDM); a wide or distorted sub (reads amateur, collapses on a club system); orchestral hits and choir stabs (game or trailer); trap hats throughout (hybrid trap, another strand); a supersaw chord wash in the drops (melodic dubstep).

**Settings for this brief** (inside `--genre dubstep`):
| Setting | Value | Source |
|---|---|---|
| Length | **3:40-4:10, aim about 3:55** (inside the modern range; the long absence needs its upper half) | the measured medians ("Catalogue measurements") [M]; the arc above [H] |
| Tempo | **140** (the deep/140, riddim and colour-bass tempo; the 2007 median and the editorial range); panic by subdivision, not tempo | [M] Mixgraph; [S] strands; [H] choice |
| Form | the arc above, 128-144 bars | [S] form sources; [H] counts |
| Rate of change | every 4-8 bars in drop 1 and the panic; **none** inside drop 2 except slow modulation (the point of the section) | [S] riddim; [H] |
| Role | two bass voices in call and response (drop 1), one motif (drop 2); a voice as a short phrase, never a song | [S]; standing rule 15 |
| Master | `--genre dubstep --lufs -8.5` (target `dubstep_2015`); the loudest 2 minutes about -6.5 to -6 LUFS short-term only if the engine reaches it cleanly (untested); the outro's absence must not be pulled up, and a long quiet outro must not make the master push the drops harder (check the drop's short-term loudness) | [M] Mixgraph, catalogue; [H] |

## Engine mapping
What modern dubstep needs, against what the engine has (docs/MANUAL.md "Production" and "Modern strands"; engine/synth.py, engine/mixbus.py, engine/instruments.py, engine/studio.py, read 2026-11-25). The engineering agent's current work (shimmer, granular / freeze, the `acid` voice, 909 snare / clap / ride, section automation of instrument parameters, the resonance suppressor) is already in MANUAL "Modern strands"; where it covers a dubstep need it is marked **(new)**.

**What the engine has, by role:**
| Need | Engine |
|---|---|
| Sub (sine, mono, 40-60 Hz, glides, follows the bass) | `sub` (phase-continuous sine, `~` glides, `harmonics` for phones), role `sub`; sidechain from kick and snare tracks |
| Kick | `kicksub` + `kickpunch` + `kickclick` stacked, `clip` on the drum bus |
| The 200 Hz snare | **(new)** `snare909` (body near 181 Hz, `tune` to 200, `bend`), layered with `clap909` / `handclap` and `kitsnare`, a `room` or a short reverb return, `comp`, `clip`; gated reverb only approximated (a short `room`, or a reverb return with a `gate` fx in its chain) |
| Hats, percussion, triplets | `metalhat`, **(new)** `ride909`, drum steps with 12/24-character bars for triplets |
| Mid-bass body | `polysynth` (saw, square, pulse, supersaw oscillators, unison, sub, noise; lp/hp/bp filter with `reso`, `env`, `keytrack`; `lfo` on cutoff / pitch / level / pan / pw / detune with `phase: "retrig"`; `env2` on pitch or cutoff; `glide_ms` with `~`; `accent`) |
| Distortion, grit | `drive`, `sat`, `clip`, `bitcrush`, `srr`, `lofi`; **(new)** `suppress` after them (tames the whistles distortion makes) |
| Compression, OTT | `ott` (three bands), `comp`, `dyneq` |
| Sub/mid split, mono low end | stacks (`"layers"`): a `sub` layer plus mid layers with `"eq": {"hp": 100-150}`; `mseq` `side_hpf` 150-180; master `mono_below` |
| Reese | `polysynth` two or more saws, `detune`, `drift`, an `lfo` on `detune`; filter |
| Wobble on volume, synced | `gate` fx (a step pattern on the project grid) and sidechain shapes |
| Pitch dives, sub drops | `env2` with `dest: "pitch"`, `~` glides (`polysynth`, `sub`, `808`), section `exit` `tapestop`, `enter` `downlifter` |
| Builds and silence | `exit` (`riser`, `rise`, `reverse`, `cut`, `lpf`, `tapestop`, `silence`), `enter` (`impact`, `crash`, `downlifter`), snare-roll patterns with `roll_pitch` |
| Movement across the arrangement | **(new)** section `auto` of instrument params (`cutoff`, `drive`, `lfo.0.depth`, `lfo.0.rate`, ...) taken at each note's onset; `lpf`/`hpf`/`gain_db` ramps |
| Freeze, granular textures, absence | **(new)** `granular` return or fx (`scan` 0 = freeze), **(new)** `shimmer` |
| Tempo switch (D&B section) | section `bpm` (the `gate` fx and the shared delay stay on the project tempo) |
| Voice | `singer` (svs), `vox2`, `vox` (a 5-formant tract, wordless); `pitch` fx (shifts formants with the pitch), `gate`, returns |
| Master | `--genre dubstep` (proposed), clipper then true-peak limiter |

**What is missing**, ranked (what a producer would do without each):
| # | Gap | Rank | Why (source) | Without it |
|---|---|---|---|---|
| 1 | **A growl voice with an FM core** (2-4 operators with ratio, index and feedback; the index driven by envelopes and LFOs; unison) | **essential** | FM is "probably the most common technique" for growls; the "honk" of a modulator moved by a looping envelope (Attack); tearout's "FM and wavetable synthesis in Serum" (Futureproof); melodic dubstep's "aggressive mid-range FM growls" | `polysynth` saws or squares through a resonant filter with a fast cutoff LFO, then `drive`/`bitcrush`/`ott`: reads as a 2011 wobble, not a modern growl; no metallic inharmonic partials |
| 2 | **Tempo-synced, per-note modulation**: LFO and envelope rates in note values (1/4, 1/8, 1/8T, 1/16, dotted), retriggered per note, and **a rate that can change from note to note** (a per-note token, e.g. `"0:F1:8/r=1/8t"`, or a rate lane in the pattern); destinations including FM index, wavetable position, formant, distortion amount | **essential** | the wobble's rhythm *is* the riff (1/8 triplet, 1/8, 1/8 dotted, 16th subdivisions: MusicRadar, SOS, EDMProd, Mixgraph); LFO "2 bars", retriggered (CM) | rates computed by hand in Hz (`bpm/60 x 2` for 1/8), `phase: "retrig"`; one rate per track, so each rhythm needs its own layer or track switched by patterns; section `auto` of `lfo.0.rate` changes it only per section; no modulation of anything but cutoff, pitch, level, pan, pw, detune |
| 3 | **A formant (vowel) filter** with a morphable vowel position (ah-eh-ee-oh-oo, 2-3 formants), modulatable (LFO, envelope, steps) | **essential** | the "talking" bass and vowel growls (Splice, Ask.audio, Unison: "ah" 300/1,000 Hz, "ee" 500/2,200 Hz); Virtual Riot's growl "built from a formant-ready wavetable" (Arturia) | a `bp` filter with `reso` and a cutoff LFO: one formant, reads as a filter sweep, not a vowel |
| 4 | **Wavetable oscillator with position morph** (a small set of tables: basic shapes, formant-ready vocal tables, harsh digital tables; warp modes: sync, bend, mirror, FM-from) | **important** | Serum-based neuro and tearout (CM, Futureproof); riddim chops built from Serum presets (EDMProd) | FM (gap 1) plus `pw` modulation on pulse covers part of it |
| 5 | **Resampling**: render a track or stack to audio and use it as a new instrument (a sampler voice: re-pitch, reverse, chop to steps, time-stretch, process, re-render), serially | **important** | "extremely difficult - if not impossible ... without further processing and resampling" (MusicRadar on neuro); tearout's "serial resampling" (Futureproof); "layered resampling" in 2025 drops (Ticketfairy) | build the chain in real time as stacked fx on one track; no chopping of a rendered phrase, no re-pitched bounces, no second pass of processing on a printed sound |
| 6 | **Multiband fx container**: split a track or bus at 1-3 crossovers and run an fx chain per band (multiband distortion, multiband OTT with depths per band, band widths) | **important** | "heavy multiband distortion" (Futureproof, tearout), Ohmicide (MusicRadar on Skrillex), the high band carries the distortion and width while the low stays solid (CM neuro) | split by stack layers with `hp`/`lp` per layer: works for the sub/mid split, costs a layer per band and loses the coherence of one source |
| 7 | **More distortion types**: wavefolder, asymmetric / rectifier, hard clip with drive, downsampler with modulated rate, and a **comb filter / flanger** with feedback (tuned to the note, modulatable) | **important** | "comb-filtered screeches" (Futureproof, tearout), flanger and chorus in riddim (Wikipedia), poly flanger and resonators in colour bass (Minimal Audio; Futureproof), "a robotic slap-back" via chorus, delay or flanger (Cymatics) | `drive` (tanh), `sat`, `bitcrush`, `srr`, `chorus`, `phaser`: no metallic comb resonance, no fold harmonics |
| 8 | **Master capable of a clip-first loud master** (a clipper stage before the limiter with its own drive, so drops land at -6.5 to -6 LUFS short-term without pumping), and a test of how loud the engine gets cleanly on a dubstep drop | **important** | loud sections of released dubstep at -6 (Mixgraph), "clip heavily first, then a very gentle limiter" (Infekt), a soft clipper alone on the master (Futureproof) | `--lufs -7.5` with `clip` on the drum and bass buses; report what the drop reaches |
| 9 | **Formant shift on voices** (shift formants without pitch, and pitch without formants) | **nice to have** | Virtual Riot's "low, pitched-down, formant-shift character" (Antares); colour-bass and melodic chops | `pitch` fx (formants move with pitch) or `singer` sung lower |
| 10 | **Vocoder / resonator to make a growl ring as chords** | **nice to have** | colour bass (Futureproof) | write the growl as chords on a polyphonic voice (gap 1's voice should be polyphonic); a `granular` return with `intervals` for a chord cloud |
| 11 | **Gated reverb** (a reverb whose tail is cut by a gate keyed by its source) | **nice to have** | "gated reverb on the snare" (Cymatics) | `room` plus a short reverb return, `duck`, or a `gate` fx on the return |
| 12 | **LFO-synced filter and pan as fx** on any track (auto-filter, auto-pan with note-value rates, envelope-follower filter) | **nice to have** | riddim's Auto Filter in envelope mode before distortion (EDMProd); textures panning (Ticketfairy) | on `polysynth` voices only, rates in Hz; `tremolo` and `phaser` take Hz |

**Covered by the engineering agent's current work:** the 909 snare (gap of the 200 Hz snare body: closed), the resonance suppressor after distortion (the harshness control every heavy chain needs), granular freeze (the absence section, colour-bass grain clouds), shimmer (melodic breakdowns), section automation of instrument parameters (slow change across drop 2; it does not reach *per-note* rates, gap 2), and the `acid` voice (its accent-coupled resonant filter and slide are a usable "squelch" bass layer, not a growl).

**Minimum for this brief** (standing rule 19): gaps 1, 2 and 3 (the growl, synced per-note modulation, the vowel), then 8 (the loud master test); 5, 6 and 7 make it current; 9-12 can wait.

## Sources
- **Tempo and loudness data:** Mixgraph, What BPM is dubstep? (10,108 tracks; year medians; read 2026-11-25): https://www.mixgraph.io/bpm-for/dubstep ; Mixgraph, brostep (editorial range only, not measured): https://www.mixgraph.io/bpm-for/brostep ; Mixgraph LUFS meter (900 store previews, 120 s, by genre, measured 2026-08-11): https://www.mixgraph.io/tools/lufs-meter
- **Catalogue measurements (this brief):** MusicBrainz search API (recordings by tag and first-release year): https://musicbrainz.org/doc/MusicBrainz_API/Search ; AcousticBrainz low-level data (CC0; Essentia Bark bands, ReplayGain, BPM, length; collection ended 2022): https://acousticbrainz.org/ ; `tools/refcurve.py catalogue`, `tools/catalogue_stats.py tag` (docs/MASTERING.md "Era targets" for the method)
- **History and strands:** Wikipedia, Dubstep: https://en.wikipedia.org/wiki/Dubstep ; Wikipedia, Riddim (genre): https://en.wikipedia.org/wiki/Riddim_(genre) ; Wikipedia, EDM trap: https://en.wikipedia.org/wiki/Hybrid_trap ; Wikipedia, Reese bass: https://en.wikipedia.org/wiki/Reese_bass ; Splice, What is dubstep music? History, artists, and subgenres: https://splice.com/blog/what-is-dubstep-music ; Futureproof Music School, Genre Explorer (dubstep, deep dubstep, brostep / tearout, tearout, riddim, colour bass, melodic dubstep; read 2026-11-25): https://genreexplorer.futureproofmusicschool.com/genre/dubstep , https://genreexplorer.futureproofmusicschool.com/genre/deep-dubstep , https://genreexplorer.futureproofmusicschool.com/genre/brostep-tearout , https://genreexplorer.futureproofmusicschool.com/genre/tearout , https://genreexplorer.futureproofmusicschool.com/genre/riddim , https://genreexplorer.futureproofmusicschool.com/genre/colour-bass , https://genreexplorer.futureproofmusicschool.com/genre/melodic-dubstep ; Mixmag (2017), Beatport adds three new genre categories (deep dubstep under Leftfield Bass; the main category "populated by brasher material"): https://mixmag.net/read/beatport-updates-platform-by-adding-three-new-genre-categories-news/
- **The modern era and the resurgence:** Ticketfairy (2026-03-18), Dubstep drops then vs now: https://www.ticketfairy.com/word/2026/03/18/dubstep-drops-then-vs-now ; Ticketfairy (2025-12-31), The bass music yearbook: stories that defined 2025: https://www.ticketfairy.com/word/2025/12/31/the-bass-music-yearbook-stories-that-defined-2025 ; Trench (2024), 10 acts pushing dubstep FWD>> in 2024: https://trenchtrenchtrench.com/features/10-acts-pushing-dubstep-fwd-in-2024 ; UKF (late 2023), Dubstep goes D&B: https://ukf.com/read/dubstep-goes-db/ ; EDM.com (2026-07-24), SVDDEN DEATH and yvm3, "Dissent": https://edm.com/music-releases/svdden-death-yvm3-dissent/
- **Sound design:** MusicRadar, How to build an LFO wobble bass: https://musicradar.com/how-to/lfo-wobble-bass ; G. Smith, Dubstep secrets (Logic ES2 wobble), Sound On Sound (2010): https://www.soundonsound.com/techniques/dubstep-secrets ; Attack Magazine, Dirty FM bass: https://www.attackmagazine.com/technique/tutorials/dirty-fm-bass/ ; MusicRadar, How to make a growling bass sound using FM synthesis: https://www.musicradar.com/tuition/tech/how-to-make-a-growling-bass-sound-using-fm-synthesis-606919 ; Computer Music via MusicRadar (2016), How to create a neurofunk bass sound in Serum: https://www.musicradar.com/tuition/tech/how-to-create-a-neurofunk-bass-sound-in-xfer-records-serum-640465 ; Splice, Creating "talking" wobble bass sounds in Ableton Live: https://splice.com/blog/creating-talking-wobble-bass-sounds-ableton-live ; Ask.audio, Talking bass in NI Massive: https://ask.audio/articles/how-to-talking-bass-ni-massive ; Unison, Formant filters: https://unison.audio/formant-filters/ ; Minimal Audio, Creating colour bass with Poly Flanger: https://blog.minimal.audio/tutorial-creating-color-ass-with-poly-flanger/ ; Arturia, Virtual Riot story: https://www.arturia.com/stories/virtual-riot ; Antares, Virtual Riot on making dubstep and bass music with Auto-Tune: https://www.antarestech.com/blog/virtual-riot-interview
- **Production guides (drums, arrangement, mixing):** EDMProd, How to make riddim: https://www.edmprod.com/how-to-make-riddim/ ; EDMProd, How to make dubstep: https://www.edmprod.com/how-to-make-dubstep/ ; Cymatics, How to make dubstep: https://cymatics.fm/blogs/production/how-to-make-dubstep ; Computer Music via MusicRadar (2008), 14 dubstep production tips: https://www.musicradar.com/tuition/tech/14-dubstep-production-tips-178489 ; iZotope (2011), Stories from a pro: Skrillex: https://izotope.com/en/learn/skrillex ; MusicRadar, Skrillex on his early production (a 2011 interview): https://www.musicradar.com/artists/in-the-past-what-i-do-would-not-have-been-considered-production-it-would-have-been-considered-noise-when-a-young-skrillex-explained-how-he-made-his-early-dubstep-bangers ; Output, Dubstep vocal samples: https://output.com/samples/dubstep-vocal-samples
- **Mixing and mastering:** Futureproof Music School, Mixing and mastering dubstep: https://futureproofmusicschool.com/blog/mixing-mastering-dubstep-easy ; Infekt, Masterclass: loudness (the public part and the author's replies): https://infektdubstep.com/masterclass/mastering/loudness/ ; MusicRadar, The ultimate guide to sub bass: https://musicradar.com/news/ultimate-guide-to-sub-bass ; N. Young, Mastering with Nihil Young, Native Instruments: https://blog.native-instruments.com/mastering-with-nihil-young/ ; Spotify, Loudness normalization: https://support.spotify.com/artists/article/loudness-normalization/ ; iZotope, dance/electronic analysis (2025): https://www.izotope.com/en/learn/dance-electronic-analysis
- **Feeling:** L. H. Arnal, A. Flinker, A. Kleinschmidt, A.-L. Giraud and D. Poeppel (2015), Human screams occupy a privileged niche in the communication soundscape, Current Biology 25(15), 2051-2056: https://pmc.ncbi.nlm.nih.gov/articles/PMC4562283 ; the expectation research in docs/PRODUCTION.md section 4
- **Not used (thin):** "wook" / experimental bass (no defining source found); Beatport's dubstep sub-genres: dubstep listed since 2010 and deep dubstep under Leftfield Bass from August 2017 ([Resident Advisor, 2017](https://ra.co/news/39747)); a "140 / Deep Dubstep / Grime" genre exists today (Beatport's "Best New 140" chart, https://www.beatport.com/bnt-140), its 2021 launch date only from a search summary of a press release that could not be opened; no Beatport riddim or melodic-dubstep sub-genre was found.
