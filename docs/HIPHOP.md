# Hip hop for Spectre: a working brief

For sessions that make hip hop beats: boom-bap, hardcore and aggressive rap, and the trap-leaning end of the family. A vocabulary, not a rulebook. The craft itself (groove, drums, 808, harmony, transitions) is in docs/CRAFT.md; this file holds the researched configuration and what changes when the brief is *aggressive* hip hop rather than trap. Spectre has made six beats in this family (001-006): one boom-bap hybrid at 90 bpm (001) and five half-time trap tracks at 136-160 bpm (002-006).

## Configuration (researched 2026-11-24; engine: `--genre hiphop` in engine/genres.json)
| Setting | Value | Source |
|---|---|---|
| Length | **2:30-3:30** (no change) | Hip-hop hits in the Billboard Hot 100 top 10 averaged 2:48 in 2019 ([Billboard](https://www.billboard.com/?p=8514407); not re-verified, the page was unreachable); Spotify charting songs averaged about 3:00 in 2024, and hip-hop got 29 s shorter from 2018 to 2024, the largest drop of any genre (with Latin) ([Chartmetric](https://hmc.chartmetric.com/shorter-songs-trend-streaming-history/)); the shortest of the 2020 Billboard year-end top 30, a rap single, ran 2:35 ([Țînț & Drăgulin 2025](https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335)) |
| Form | intro 4, verse 16, hook 8, verse 16, hook 8, (bridge 8), outro 4; pre-chorus 4 optional; verses twice the hook's length; a traditional rap song is about **60-72 bars** | [eMastered, "Rap song structure"](https://emastered.com/blog/rap-song-structure). Bars are counted in the felt (half-time) bar for trap-leaning beats: Spectre's 136-160 bpm tracks ran 92-112 written bars |
| Tempo, boom-bap / hardcore pocket | **85-100 bpm**, swung 16ths; old-school East Coast 100-120, early West Coast 90-100 then 90-120 | Hip-hop catalog (1,185 tracks): median 105, middle half 92-130, 10th-90th percentile 82-147, editorial range 80-100; the median rose from 93 (2003) to 110 (2026) ([Mixgraph, hip-hop](https://www.mixgraph.io/bpm-for/hip-hop)); regional ranges from Prince Charles Alexander ([Berklee Today, 2022](https://college.berklee.edu/node/2512271)). The 85-100 window for a hard boom-bap pocket is craft (docs/CRAFT.md), inside those measured ranges |
| Tempo, trap-leaning | **130-150 bpm written, felt in half time (~70)**; median 144, middle half 140-150 | 178 trap (hip-hop) tracks ([Mixgraph, trap](https://www.mixgraph.io/bpm-for/trap-hip-hop)); Southern hip hop's double-time feel reads as 80 or 160 ([Berklee Today](https://college.berklee.edu/node/2512271)) |
| Meter and groove | 4/4; kick lands firmly on the 1 of a one- or two-bar phrase and moves around it; snare, rim or clap on the backbeat (2 and 4; on 3 in half-time trap); hats in 8ths or 16ths with a slight loose swing | [Berklee Today](https://college.berklee.edu/node/2512271); trap's half-time pocket from [Mixgraph](https://www.mixgraph.io/bpm-for/trap-hip-hop) |
| Rate of change | something changes every 4-8 bars; a section every 8 or 16 | **unsourced craft** (docs/CRAFT.md §6); the section lengths above are sourced |
| Role | the verses leave room for a rapper: a simpler beat, the 300 Hz-3 kHz zone clear; the hook is the fullest version of the beat; rap vocals sit dry and up front | section roles from [eMastered](https://emastered.com/blog/rap-song-structure); dry rap vocals ([Splice, Raman 2018](https://splice.com/blog/?p=4806)); the vocal zone is craft (docs/CRAFT.md §4) |
| Loudness of releases | hip-hop and pop masters run **-11 to -7 LUFS** integrated; 54 Billboard Global 200 top-10 songs (H1 2024) averaged -8.3 LUFS (sd 1 LU), max short-term -6; only 11 of 54 stayed under 0 dBTP, half sat between 0.00 and +0.75 dBTP; streaming normalizes to -14 (Spotify, Tidal), -16 (Apple), -13 (YouTube) | Ike Iloegbu ([Soundfly](https://flypaper.soundfly.com/produce/an-introduction-to-mastering-hip-hop-and-pop-music/)); [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends); normalization targets from [Splice](https://splice.com/blog/?p=4806). No hip-hop-only loudness survey with numbers was reachable (iZotope publishes its per-genre values only in chart images) |
| Dynamics | PLR about 9.3 dB for chart hits since 2010; LRA of the 2024 top-10 set mostly 3.7-6.8 LU; keep limiter gain reduction around 3.5 dB on average | [Țînț & Drăgulin 2025](https://webbut.unitbv.ro/index.php/Series_VIII/article/view/11335); [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends); [Splice](https://splice.com/blog/?p=4806) |
| Tonal balance | the measured hip-hop spectrum: an extended low end (the only region where genres separate clearly), about -4.8 dB/octave from 100 Hz to 4 kHz; masters lift lows and a gentle air shelf from about 9 kHz; a gentle high-pass around 30 Hz keeps 808 rumble from eating headroom | Pestana et al. 2013 (docs/MASTERING.md); [Splice](https://splice.com/blog/?p=4806) |
| Low end and width | kick and bass in the centre, the low end mono, highs can spread; hip-hop/rap is the **narrowest** genre in the 2024 top-10 set (the average across genres: -8.5 LU side minus mid) | [Soundfly](https://flypaper.soundfly.com/produce/an-introduction-to-mastering-hip-hop-and-pop-music/); [iZotope 2024](https://www.izotope.com/en/learn/mastering-trends) |
| Master | `studio.py master vNNN --genre hiphop` (= `--target hiphop --lufs -10.5 --tp -1 --eq 0.7 --translate 0.5`, mono below 120 Hz) | see "The decision" |

## The decision: `hiphop`, unchanged
- **`hiphop`, not `trap`.** Both configurations share every setting except the tonal target. `hiphop` uses the curve measured from hip-hop #1 singles (Pestana et al. 2013); `trap` uses the hand-tuned `beat` curve, which asked for 3-5 dB too much at 12.5-16 kHz and made the first releases sound hissy on phones (docs/MASTERING.md, "Top end"). `trap` stays only to reproduce sessions 001-006's first releases.
- **No new entry for aggressive hip hop.** Nothing found sets aggressive or hardcore rap apart in mastering: the only published hip-hop spectrum is the one `hiphop` already uses, and the loudness and width sources describe hip hop as a whole. Aggression lives in the mix and the arrangement (distortion, density, hard transients, cuts; docs/CRAFT.md §4-5), not in a different master. The tempo choice (boom-bap pocket or half-time trap) doesn't change the master either.
- **The entry's metadata now covers both pockets.** `tempo` in genres.json said only 130-160 half-time; it now lists both pockets, points to this file and adds `change_rate`. Only the descriptive fields changed; the `master` block, which is the only part the engine reads, is unchanged, so masters of 001-006 and running renders are unaffected.
- **Where Spectre stays off the industry, and why.** Charts sit near -8.3 LUFS with true peaks over 0 dBTP; Spectre masters hip hop at -10.5 LUFS and -1 dBTP. The ceiling is deliberate: MP3 encoding adds about 0.5 dB of true peak (docs/MANUAL.md), and streaming plays everything at -13 to -16 anyway. The loudness is kept so 001-006 and queue item 1's re-renders stay comparable; it was set when the true-peak guard stopped gaining past about -9.5 (genres.json `trap`), and later tests on trance and rock reached -9 and -8.5 (docs/MASTERING.md). **Open item:** test a louder `hiphop` master (about -9 LUFS) on one track before changing the entry. `eq` 0.7 and `translate` 0.5 stay **hand-tuned**. The hip-hop curve pools 1950-2010 records and probably has less 31-50 Hz than 2010s-2020s 808 records (docs/MASTERING.md, caveats).

## Aggressive hip hop: what changes
- **Two pockets of aggression.** Hardcore boom-bap hits with weight and a swung, head-nodding pocket: a punchy kick, a cracking snare on 2 and 4, dusty and compressed samples. The anger is controlled and close. Trap-leaning aggression (rage, drill) is faster and colder: half-time snare on 3, rolling hats, a distorted, sliding 808. Spectre's 002 "Lid Off" is the rage-trap extreme (160 bpm). Decide which anger the track is before you choose the pocket.
- **Anger in the research cues:** fast, loud, rough timbre, dissonance (docs/CRAFT.md §4). In a beat: saturation and drive on the 808 and drums, hard cuts (silence, then a slam), Phrygian or b5 colour, dense low mids, a dry and close sound (reverb = distance; anger is in your face).
- **Room for the rapper even when it's angry.** The verse beat stays simpler than the hook: the drums and the bass carry it, the melody sits low or drops out, nothing busy in 300 Hz-3 kHz. Aggression in a verse comes from the drums and the bass, not from a busy lead.
- **Distortion and the top end.** Driving snares, claps and hats adds noise at 4-12 kHz, the part that sounds like static on a phone (in 002, about 95% of the 4-12 kHz energy was the snare hits). Drive the body, then shelve or low-pass the top; run `listen --phone --genre hiphop` before mastering.
- **The low end against the measured curve.** The remasters of 001-005 still sat 7-10 dB over the hip-hop curve at 40 Hz and the master cut there at its limit (docs/MASTERING.md). Get the 808's weight from saturation and its second harmonic (`tone`), tune the kick away from the 808 (002: kick at 62 Hz, 808 notched), and vary the 808's notes so the low end is even (005).

## Mixing the voice (researched 2026-11-24)
A Spectre beat leaves the verses to a rapper who isn't there; its own voices are instruments: a sung or chanted hook fragment, ad-libs and shouts, chops, a choir pad. The principles for every genre, the choir research and the check procedure are in [docs/voice/MIXING.md](voice/MIXING.md). Values marked *(hand-tuned)* are Spectre's starting points. Reminder: the svs voices may not be used on a political subject (session 011); use the wordless `vox`/`vox2` or no voice there.

**What the research says**
- **Up front and dry-ish, the measured way:** rap leads sit 3.2 dB over the accompaniment on average, second only to country ([Gerdes & Siedenburg 2023](https://www.geidai.ac.jp/~marui/course_enshu_2024/gerdes_siedenburg_202304.pdf)). The vocal must not sit so low that the kick drowns it nor so high that the 808s lose their impact ([Evan LaRay, Sound On Sound](https://www.soundonsound.com/techniques/inside-track-cardi-b-bodak-yellow)).
- **A documented hook chain** ("Bodak Yellow"): high-pass around 100 Hz, -3 dB at 300 Hz for mud, -3 dB at 4 kHz for a piercing frequency, a fast FET compressor on peaks, a de-esser at 4.27 kHz; on the vocal bus a second de-esser, another compressor, a multiband lifting the highs and holding the lows, saturation and a limiter; a parallel bus compressed heavily with a 5 kHz boost and an exciter. The main delay is a quarter note, 9 dB down; the reverb is set "tight"; the long effect (a hall of 7 s behind 15 ms) lives on separate effect tracks with an 8th-note ping-pong delay, not on the lead (LaRay, above).
- **Hook against verse, doubles, ad-libs** (the same session): only the hook gets the stereo delay, to separate it from the verse; doubles are compressed, lose their highs and everything under 200 Hz, and get a delay that puts them in another space than the lead; ad-libs get distortion, auto-panning and reverb.
- **A lead chain a decade earlier** (Jay-Z, mixed by Young Guru): tube compression twice, a Lexicon 480 reverb and a quarter-note delay, the ad-libs treated like the lead; he leaves the stereo bus to mastering ([Sound On Sound](https://www.soundonsound.com/techniques/secrets-mix-engineers-young-guru)).
- **Voices as percussion and crowd:** a repeated "Hey" used "almost as percussion" got a high-pass and about 3 kHz of boost; a vocal swirl got delay only; crowd responses were grouped, high-passed around 100 Hz and given 8 kHz (Young Guru, above). That is how a beat treats a voice that is not the rapper.
- **Mastering:** the loudest of Spectre's vocal contexts after trance: chart hip hop sits around -8 LUFS with about 3.5 dB of limiter gain reduction (Configuration). The limiter works on every kick and 808 note, so a voice sitting on those beats is ducked by the master and its reverb comes up between them: keep sends small and check words on the master. Hip hop is the narrowest genre measured (Configuration): the hook voice lives in the centre, and width comes from doubles and ad-libs.

**Starting chains** (*hand-tuned* from the documented chains; the engine has no de-esser, parallel bus or multiband):
```json
"mix": {"reverb": {"size": 0.5, "damping": 0.6, "return_db": -8, "lpf": 6000},
        "delay":  {"beats": 1, "feedback": 0.25, "return_db": -9, "lpf": 3500}},

"hook":  {"inst": {"type": "singer", "source": "svs", "voice": "hanami", "double": 0.2, "double_pan": 0.7,
                   "inhale": 0.2, "svs_fade_in_ms": 15, "svs_fade_out_ms": 100},
          "send_reverb": 0.08, "reverb_predelay_ms": 40, "send_delay": 0.06,
          "fx": [{"type": "hpf", "hz": 100}, {"type": "eq", "hz": 300, "gain_db": -3, "q": 0.9},
                 {"type": "eq", "hz": 800, "gain_db": -2, "q": 0.9}, {"type": "comp", "threshold_db": -24, "ratio": 4},
                 {"type": "sat", "amount": 0.15}, {"type": "highshelf", "hz": 8000, "gain_db": 3},
                 {"type": "gain", "db": 8}]},

"adlib": {"inst": {"...": "hanami-power or leona-power; one word or a shout"},
          "pan": 0.5, "send_reverb": 0.25, "send_delay": 0.3,
          "fx": [{"type": "hpf", "hz": 200}, {"type": "lpf", "hz": 6000}, {"type": "drive", "db": 6},
                 {"type": "comp", "threshold_db": -24, "ratio": 5}]},

"chop":  {"inst": {"...": "any voice; short syllables, pitch or formant moved"},
          "fx": [{"type": "hpf", "hz": 200}, {"type": "eq", "hz": 3000, "gain_db": 3, "q": 0.8},
                 {"type": "comp", "threshold_db": -24, "ratio": 5}], "send_delay": 0.15}
```
- **The hook fragment:** dry and close (reverb is distance; `size` 0.5 is 1.15 s, sends under 0.1), a quarter-note delay well under the voice, 4:1 with a little saturation, the 300 Hz cut from the documented chain. Level 1-3 LU over the beat's music without the 808 and kick, and never over the kick's peaks *(hand-tuned from the measured 3.2 dB)*. If a rapper is meant to use the beat, the hook fragment is a guide: keep 300 Hz-3 kHz free in the verses (Configuration, "Role") and put the voice only where a hook would be.
- **Ad-libs and shouts:** off-centre, darker and dirtier than the hook, with the long effects; 4-8 LU under the hook.
- **Doubles:** `double` 0.2-0.3 on the hook; a separate double track gets `hpf` 200 and a high cut.
- **Chops:** percussion made of voice: high-pass, a 3 kHz bell, heavy compression, a delay for bounce; no reverb needed. Soul-sample-style pitched chops: `{"type": "pitch", "semitones": 3}` to 5 on a short phrase, low-passed.
- **Choir pads** (the dark-trap or drill choir): MIXING.md "Choir and ensemble voices": vowels only, `svs_vibrato` 0.3-0.5, `hanami-dark` and the soft voices, `hpf` 250, 8-10 LU under the 808, sidechained to the kick.
- **808 and voice:** an 808's harmonics and saturation reach into 200-600 Hz, the voice's body. Cut the voice there (the 300 Hz move), not the 808.

**How to check:** MIXING.md "Checking a voice": Whisper on the hook line in the mix and on the master, the vocal-versus-band loudness from a render with the voice tracks muted, and `listen --phone --genre hiphop` (a phone has no 808: the voice-to-beat balance changes most there, so the hook must not become shouting on a phone).

**Unsourced here:** the levels of ad-libs, chops and pads; everything about a choir in a beat; the sends.

## Layering and EQ carving (researched 2026-11-25)
The cross-genre method is in [PRODUCTION.md](PRODUCTION.md); the trance tables in docs/TRANCE.md are the worked example. Labels: **[M]** measured, **[S]** a named source, **[P]** carried over from a professional trance producer's EQ map (2026) for instruments both genres share, **[H]** hand-tuned.

**Layer roles.** A beat is few parts, each made of two or three sources:
| Part | Layers and their jobs | Label |
|---|---|---|
| **Kick and 808** | one low-end instrument made of two: the **kick** is the hit (a short body at 50-70 Hz and a click), the **808** is the sustained note under it. Keep them apart in time (shorten the kick's decay so only its punch is left), in frequency (a dynamic notch on the 808 at the kick's fundamental, 62 Hz in iZotope's example) and in level (the 808 ducked by the kick) | [S] iZotope, "How to mix 808s" |
| **808** | itself a stack: a sine for the fundamental; an octave above or added 2nd and 3rd harmonics (a little square in the oscillator, tube saturation) so it "rings out in many more types of speakers" | [S] iZotope |
| **Snare / clap** | a snare for body (150-250 Hz) and crack (2-3.5 kHz) plus a clap for width and top, the clap a few ms early (docs/CRAFT.md); in drill and trap often a rim or snap as a third colour | [S] iZotope EQ cheat sheet; CRAFT |
| **Hats** | closed hats, an open hat, sometimes a shaker or ride: different decay and tone, panned a little apart | [H] |
| **Melody / sample** | the main instrument (keys, a folk lead, a chopped phrase) plus what it lacks: an octave double, a pad or strings underneath for body, a bell or pluck on top for the attack, a texture (vinyl, tape) as the "air" | [S] the layering rules in PRODUCTION.md; choices [H] |
| **Voice** | lead, doubles, ad-libs in different spaces (this brief, "Mixing the voice") | [S] |

**EQ map** (starting ranges; "there are no specific frequencies that will always work", Mike Senior, Sound On Sound 2008; confirm on the actual sounds with the clarity analysis proposed in PRODUCTION.md):
| Instrument | High-pass | Cut / control | Emphasise | Source |
|---|---|---|---|---|
| Kick | 25-30 Hz | 200-500 Hz (boxiness); keep the tail short under an 808 | 50-80 Hz punch, 100-200 Hz knock, 1-5 kHz attack | iZotope cheat sheet; [P] |
| 808 | 20-25 Hz [H] | a dynamic notch at the kick's fundamental; 200-400 Hz if it clouds the melody | 30-60 Hz fundamental; harmonics at 100-300 Hz and 700 Hz-1.5 kHz from saturation, not from EQ | iZotope 808; ranges [H] |
| Snare | 80-120 Hz | 300-500 Hz boxiness, 400-700 Hz ring, 900 Hz-1.5 kHz papery | 150-250 Hz body, 2-3.5 kHz attack, 8 kHz up air | iZotope cheat sheet |
| Clap | 120-250 Hz | 400-800 Hz | 1-2 kHz snap, 2-8 kHz | [P]; Sound On Sound (TRANCE.md "Claps") |
| Hats, shakers | 500-2,000 Hz | 3-7 kHz harshness | 8-12 kHz | iZotope; [P] |
| Keys, piano, sample | 100-200 Hz (they must leave the 808 alone: CRAFT.md) | 200-500 Hz mud | 2-5 kHz | iZotope; [P] |
| Pads, strings, choir | 150-250 Hz | 200-500 Hz | 1-3 kHz; air above 8 kHz | [P]; iZotope |
| Lead (flute, reed, synth, fiddle) | 200-300 Hz [H] | 300-600 Hz; harsh resonances | 1-4 kHz | [P] (lead layers) |
| Plucked folk instruments (oud, cobza, kokle, cimbalom) | 100-150 Hz [H] | 200-400 Hz | 1.5-2.5 kHz presence, 8-12 kHz air | iZotope (acoustic guitar), applied [H] |
| Voice | 80-120 Hz (svs voices: 150-220 Hz, this brief) | 200-400 Hz; 5-8 kHz sibilance | 2-5 kHz; air from 10 kHz | [P]; iZotope |
| Textures (vinyl, rain, tape) | 300-500 Hz [H] | everything above about 4-6 kHz unless it is the only "air" (docs/MASTERING.md "Top end") | | [M] this repo |
| Reverb and delay returns | 200-500 Hz | 300-600 Hz | low-pass at 6-12 kHz | [P]; Houghton, Sound On Sound 2022 |

**Glue** [S]: drums on one bus with light compression and saturation; the melody stack on one bus; hip-hop masters are dense (about 3.5 dB of limiter gain reduction, this brief's Configuration), so the low end must be settled in the mix. The engine has no buses yet (PRODUCTION.md, proposals).

**Where Spectre stands** [M] (stems of session 011's last hook, rendered in memory, 2026-11-25): the snare alone supplies everything above 2 kHz (no hat, melody or texture within 10 dB of it there); the 808 is 59% masked by the kick (the kick is the loudest stem at 60-400 Hz; no notch or ducking separates them); one or two sources per band everywhere. Sessions 001-006 use one `808`, one `kick` and one melody instrument per role in the same way (their project files). Thin, as in trance, and with the kick and 808 in each other's way.

**How to build it in Spectre** (engine since 2026-11-25; parameters in docs/MANUAL.md "Production"; levels are starting points, set them by ear and by the stack view of `listen --clarity --genre hiphop`). Set `"genre": "hiphop"` so layers get the map's presets (`"eq": "auto"`).
- *Kick*: a `kick`, or a stack of `kicksub` (tuned to the key's root, 50-60 Hz, `tail` 0.06-0.09 so it stops before the 808 speaks) and `kickclick` (`tone` 2500-4000, role `kick`, `"eq": {"hp": 1500, "cut_db": 0, "own_db": 0}`); a `drums` bus with `clip` (1-2 dB).
- *808 as a stack*: `{"role": "808", "layers": [{"name": "body", "inst": {"type": "808", "decay": 1.2, "tone": 0, "glide_ms": 60}, "role": "808"}, {"name": "harm", "inst": {"type": "sub", "shape": "triangle", "harmonics": 1.0, "drive": 0.6, "glide_ms": 60}, "octave": 1, "role": "808", "eq": {"hp": 110, "cut_db": 0, "own_db": 0}, "fx": [{"type": "lpf", "hz": 1500, "slope": 12}], "gain_db": -4}], "fx": [{"type": "dyneq", "hz": <the kick's tune>, "q": 1.5, "depth_db": -8, "key": "kick", "release_ms": 90}, {"type": "mseq", "side_hpf": 120}]}`: the sine owns 30-60 Hz, the octave layer puts its harmonics where phones hear them (iZotope), the keyed notch clears the kick's fundamental only when the kick hits.
- *Snare and clap*: one stack, the clap a few ms early (CRAFT.md): `{"layers": [{"name": "snare", "inst": {"type": "snare"}, "role": "snare"}, {"name": "clap", "inst": {"type": "handclap"}, "role": "clap", "offset_ms": -6, "gain_db": -3, "width": 0.4}]}`.
- *Hats*: `metalhat` (tonal, so a brighter era target is met without hiss), role `hats` with `"eq": "auto"`, and `"humanize": {"ms": 3, "beta": 1.0, "vel": 0.05}` instead of `humanize_ms` (correlated drift; docs/PRODUCTION.md section 4).
- *Melody or sample*: the main instrument plus what it lacks, as layers of one stack: an octave double (`"octave": 1`, role `support`, 6-10 dB down), a pad body (`polysynth`, role `pad`, `"notes": "all"`), keeping everything above 100-200 Hz with the role presets so the 808 owns the low end; a `music` bus with light kick sidechain (depth 0.2-0.3).
- *Spaces*: `mix.returns` with a short `room` for drums and a `hall` for the melody and voice, the hall ducked by the voice (`"duck": {"key": "<voice track>", "depth_db": 6}`) and cut at 300-600 Hz.

## Era assessment of the master target (2026-11-25)
**What the current curves are.** `hiphop`: Pestana et al. (2013), Fig. 5 "hip-hop": UK and US number-one singles tagged hip-hop, in practice about 1990-2010, magnitude-averaged (docs/MASTERING.md). `trap` / `beat`: hand-tuned for sessions 001-006.

**Measured against the catalogue** [M] (method, validation and limits in docs/TRANCE.md, section C: MusicBrainz recordings tagged `hip hop`, up to 100 per year, with AcousticBrainz Bark-band data; 2,158 tracks 1995-2021; dB relative to each track's 510 Hz-2 kHz level; medians):
| Band (Hz, as analysed) | 1995-99 | 2000-04 | 2005-09 | 2010-14 | 2015-21 | `hiphop` curve | `beat` curve | Spectre masters 001-006, 011 (range) |
|---|---|---|---|---|---|---|---|---|
| tracks | 497 | 428 | 419 | 461 | 353 | | | |
| under 32 (reads about 1-4 dB high for curves and masters) | +2.5 | +2.4 | +3.0 | +4.8 | **+6.2** | -1.0 | +8.2 | -2.3 to +5.2 |
| 32-97 (kick and 808) | +16.2 | +15.1 | +14.5 | +14.2 | **+15.8** | **+10.8** | +14.0 | **+9.5 to +13.6** |
| 97-140 | +11.0 | +8.8 | +8.3 | +7.4 | +7.8 | +11.1 | +8.3 | +8.7 to +11.0 |
| 140-183 | +7.2 | +5.5 | +5.0 | +4.7 | **+4.4** | **+7.9** | +5.5 | +6.6 to +8.2 |
| 183-291 | +7.8 | +7.3 | +6.7 | +7.0 | +5.8 | +7.6 | +6.7 | +7.5 to +9.0 |
| 6400-7700 | -4.9 | -6.5 | -5.3 | -5.3 | -5.1 | -6.8 | -7.1 | -8.7 to -6.7 |
| 7700-9500 | -5.8 | -7.4 | -6.1 | -6.0 | -5.3 | -7.3 | -7.7 | -9.4 to -6.9 |
| 9500-12000 | -8.3 | -9.1 | -8.0 | -7.6 | -6.5 | -8.8 | -9.0 | -10.3 to -8.1 |
| 12000-15500 | -11.8 | -12.5 | -11.5 | -11.0 | -10.6 | -13.0 | -11.1 | -14.1 to -11.8 |
| est. LUFS, median (middle half) | -12.5 (-15.8 to -10.8) | -12.2 (-15.8 to -9.7) | -11.3 (-14.1 to -9.6) | -11.0 (-12.8 to -9.6) | -10.6 (-12.2 to -9.3) | | | 001-006: -11.1 to -10.1 (measured) |

- **What changed in hip hop** [M]: the band under about 32 Hz rose by nearly 4 dB between the late 1990s and 2015-21 (the 808 era; the lossless-only subset shows the same step, +2.6 to +5.5); 97-183 Hz fell by about 3 dB; the top rose 1-2 dB; estimated loudness rose about 2 dB.
- **Where the targets stand** [M]: the measured `hiphop` curve asks for 5 dB less in the kick-and-808 band than 2015-21 hip hop has, 3.5 dB more at 97-183 Hz and about 2 dB less from 6.4 kHz up. The hand-tuned `beat` curve is the closer one below 300 Hz (-1.8 dB in the kick-and-808 band, within about 1 dB from 97 to 300 Hz) and about as dark up to 12 kHz. So the 2026-11-24 remasters of 001-006 with `hiphop` corrected the top end, as intended, and moved the low end away from current hip hop: this brief's "Decision" section should be revisited with these numbers.
- **Spectre's masters** [M]: 2-6 dB short in the kick-and-808 band (001 least, 011 most), 1-4 dB heavy at 97-183 Hz, 1-4 dB dark from 6.4 kHz up.
- **A current target.** *Interim* [M, fitted as in TRANCE.md C; adopted 2026-11-25 as `hiphop_2015`, below]: 31.5 Hz +1, 40 +4.5, 50 +7, 63 +8.5, 80 +7, 100 +6, 125 +3, 160 +1.5, 200 +1, 250 +1, 315 +0.5, 400 +1.5, 500 +2, 630 +1.5, 800 0, 1k 0, 1.25k -1.5, 1.6k -2, 2k -2.5, 2.5k -3, 3.15k -4, 4k -5.5, 5k -7, 6.3k -6, 8k -6.5, 10k -7.5, 12.5k -11, 16k -18 (dB re 1 kHz; 31.5-40 Hz ±3 dB). The `hip hop` tag mixes boom-bap revival with trap; a `trap`-only curve needs its own measurement. *Definitive:* 20-30 current reference masters per pocket (boom-bap, trap), measured locally with `master.py`'s analyser, numbers only in the repo (PRODUCTION.md "Era-appropriate targets").
- **The top end has the same condition as in trance:** more top must come from tonal content, not from the noise sources that read as static on phones.
- **Adopted (2026-11-25): `hiphop_2015`**, the default target of `--genre hiphop` (347 tracks tagged hip hop, 2015-2021): against the old `hiphop` curve +6 to +12 dB at 31.5-63 Hz, -2 to -5 dB at 100-250 Hz, +1 to +3 dB from 6.3 kHz; within about 1.5 dB of the hand-tuned `beat` curve below 6 kHz, so the 2026-11-24 remasters of 001-006 with `hiphop` moved their low end away from current hip hop and a remaster with `hiphop_2015` would bring it back (the owner's call, track by track). `--genre trap` (the first-release configuration) is unchanged. It is the same measurement refit by `tools/refcurve.py` (which reproduces the medians above within 0.4 dB; curve, n, spread and validation in docs/MASTERING.md "Era targets", provenance in engine/genres.json); the released tracks keep their masters until the owner approves a remaster (`master --published` reproduces their settings).

Sources for these two sections: iZotope, EQ cheat sheet: https://izotope.com/en/learn/eq-cheat-sheet ; M. Houghton, How to achieve better separation in your mixes, Sound On Sound (2022): https://www.soundonsound.com/techniques/how-achieve-better-separation-your-mixes ; M. Senior, Q. What should I EQ to improve my muddy mixes?, Sound On Sound (2008): https://www.soundonsound.com/sound-advice/q-what-should-eq-improve-my-muddy-mixes ; a professional trance producer's EQ map (2026; docs/TRANCE.md); MusicBrainz search API and AcousticBrainz low-level data (CC0; https://acousticbrainz.org/), measured 2026-11-25; everything else in docs/PRODUCTION.md "Sources". Also: iZotope, How to mix 808s for a powerful low end: https://www.izotope.com/en/learn/how-to-mix-808s

## Unsourced in this brief
The 85-100 window for a hard boom-bap pocket (inside the measured ranges, but chosen by craft), the rate of change, the aggression cues beyond the emotion research in CRAFT.md, and the "two pockets" framing.
