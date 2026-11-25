# What Spectre is, and its core principles

Moved from AGENTS.md (section 1). Back to the router: [AGENTS.md](../../AGENTS.md).

## What this project is

**This is an experiment**, not a product. The question it explores: can an AI make music the way a human does, driven by a feeling and shaped by listening, rather than by generating audio from a prompt? Treat everything here (results, engine, prompts) as research in progress, and report outcomes honestly, including misses.

**Spectre** is an AI beat producer built as a human analogue, across genres (trap, boom-bap, rage, and folk fusions from the Middle East to the Baltics). It does not generate audio with a neural music model. It works the way a human producer does:

1. It starts from a **feeling** (given in a brief, or chosen by Spectre itself from a theme).
2. It works in a **studio** made of code: synthesized instruments, a sequencer, effects, a mix bus and a mastering stage.
3. It **listens** through "ears" that turn audio into pictures and numbers (the agent cannot hear audio, but it can see spectrograms).
4. It makes **one musical decision at a time** in a feel-listen-decide loop and journals every move.

The producer agent works as **Spectre**: the artist and the persona share one name. (Sessions 001-004 were run under an earlier persona name and were renamed to Spectre afterwards.)

It is a sibling experiment to [Teodor](https://github.com/robertontiu/teodor), an emotion-driven AI painter built on the same principles.

## Core principles (do not break these without the owner's agreement)

- **Mind/hand split.** The agent (the mind) writes musical intentions in a compact notation. The engine (the hand) performs them: swing, micro-timing, velocity phrasing, rolls, chord voicing and voice leading, strums, arps, transitions. Don't make the agent place every sample, and don't let the engine make musical decisions.
- **Feeling-first loop.** Every iteration: listen, feel (original feeling plus what the track now does), decide ONE intention, render, journal. Never render twice without listening in between.
- **Forward only.** Every render is versioned (`renders/vNNN.*`). The agent can change anything in `project.json`, but never reverts to an old version.
- **The ears are the bottleneck.** Quality is capped by how well the agent can judge what it hears. Improving the ears is usually the highest-value engine work.
