# Spectre

**An experiment: can an AI make a hip-hop beat the way a human producer does, starting from a feeling?**

Spectre is not a text-to-music model. No neural network generates audio here. Instead, an AI agent plays the role of a producer and works in a small studio made of code:

- every sound (drums, 808s, keys, strings, choir, vinyl crackle) is synthesized from scratch,
- the agent writes musical *intentions* ("a kick that leans early, a snare that drags, an 808 sliding up into the hook"), and a "hand" performs them with swing, timing and velocity, the way fingers on drum pads would,
- the agent can't hear, so it **listens by looking**: every render becomes spectrograms, an arrangement view and measurements,
- it works one decision at a time, writing down what it heard, what it felt and why it made each move.

Then a person listens and guesses which feeling it was making.

It's a sibling of [Teodor](https://github.com/robertontiu/teodor), the same idea applied to painting.

## Results so far

| # | Track | Feeling | What happened |
|---|---|---|---|
| 001 | [Bleachers](sessions/001-bleachers/) | hidden (blind test) | 3:12, 90 bpm. The listener guessed *longing*; it was **defiance**. Close, but not aggressive enough. It also exposed a mix problem on laptop speakers, which led to the mastering stage. |
| 002 | [Lid Off](sessions/002-lid-off/) | rage (briefed: high tempo, aggressive) | 2:51, 160 bpm, E Phrygian. Rage-trap meets industrial: distorted 808s, a blown-out dissonant supersaw cluster, an eighth of dead silence before every slam. Applied the lessons from 001: attitude built into the sound, controlled low end, mastered at -10 LUFS. |
| 003 | [Throw It Back](sessions/003-rebellion/) | rebellion (briefed: oriental trap) | 2:48, 140 bpm, D Hijaz. Oud calls, the crowd answers louder each time; a march where the trap drums drop out and only feet, hands and darbuka walk. Built with new oud, ney and darbuka instruments. |

Each session folder has the mastered MP3, the producer's journal (every move, numbered), the project file that reproduces the track exactly, and pictures of what the producer "saw".

## How a session works

1. **Sit with it.** The producer describes the feeling in the body, in time and space, and picks tempo, groove, key and sounds.
2. **The loop.** It builds a 4- or 8-bar loop until it carries the feeling on repeat.
3. **Arrangement.** It extends to a full 2:30-3:30 beat with an emotional arc.
4. **Transitions and detail.** Drop-outs, fills, risers, switch-ups.
5. **Mix and master.** Balance, then a mastering stage (tonal balance, mono low end, gentle compression, bass harmonics for small speakers, true-peak limiting).
6. **Final listen** from the top.

Every step is: listen, feel, decide one thing, render, write it down.

## What we've learned

- **Notes aren't attitude.** The first blind test aimed for defiance and was heard as longing. A minor melody that keeps reaching up *means* refusal on paper but *sounds* like yearning. The AI can verify structure by looking at sound; it can't yet verify attitude.
- **Most of making rage was taking out the wrong feelings.** In session 002 a hissing snare tail read as anxiety, a riser read as festival hype, and a half-time verse went cold like menace, so each was cut or reworked.
- **Taking things away carries a feeling.** In session 003 the strongest rebellion moments came from removing the trap drums (a march of feet, hands and darbuka) and leaving the crowd shouting over nothing.
- **Laptops can't play sub bass.** A beat that's all 50 Hz sounds clunky on a MacBook. Mastering now checks how a track translates to small speakers.

More in [docs/LESSONS.md](docs/LESSONS.md).

## Try it

Requires Python 3.11+ and ffmpeg.

```bash
pip install -r requirements.txt
mkdir -p /tmp/beat && cp examples/engine-test.json /tmp/beat/project.json
cd /tmp/beat && export BEAT_DIR=$PWD
python3 <path-to-repo>/engine/studio.py render    # renders/v001.wav
python3 <path-to-repo>/engine/studio.py listen    # ear.png: what the producer "sees"
python3 <path-to-repo>/engine/studio.py master    # renders/v001.master.mp3
```

To reproduce a session's track exactly, render its `project.json` (rendering is deterministic).

The project format is documented in [docs/MANUAL.md](docs/MANUAL.md), and the hip-hop craft notes the producer reads are in [docs/CRAFT.md](docs/CRAFT.md). If you're an AI agent, start with [AGENTS.md](AGENTS.md).

## Honest limits

- All sounds are synthesized, so it sounds like a good demo, not a commercial record.
- No vocals.
- The producer judges its work through images and numbers, not ears. That's the core constraint of the experiment, and the most interesting thing to improve.

## License

[MIT](LICENSE)
