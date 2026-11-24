# Kokoro v1.0 (ONNX): the word sampler for `singer` `"source": "tts"`

These are the model files the engine loads to speak lyric words neutrally (engine/tts_words.py). They are versioned here so a fresh session doesn't have to download them; they may move out of the repo later (then point `SPECTRE_TTS_DIR` at their new folder).

| File | Size | SHA-256 | Storage |
|---|---|---|---|
| `kokoro-v1.0.onnx` | 325,532,387 bytes (325 MB) | `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5` | git LFS (over GitHub's 100 MB limit; `git lfs pull` after cloning) |
| `voices-v1.0.bin` | 28,214,398 bytes (28 MB) | `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d` | plain git |

- **Source:** https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 (`kokoro-v1.0.onnx`, `voices-v1.0.bin`), the ONNX export of Kokoro-82M by hexgrad. `voices-v1.0.bin` is a NumPy archive with all 54 Kokoro voices (style vectors); Spectre uses `af_heart` (`voice: "female"`), `am_michael` (`"male"`), `af_bella` (`"female2"`) and `am_adam` (`"male2"`), and any other by name with `tts_voice`.
- **Licence:** Kokoro model weights: Apache License 2.0 (per the kokoro-onnx README; the `kokoro-onnx` Python package is MIT). Apache 2.0 places no restriction on the audio the model produces, so the sampled words can be used in released music. The Kokoro-82M model card (on Hugging Face, not reachable from the sandbox to re-check) states it was trained on permissively licensed and non-copyrighted audio.
- **Runtime:** `pip install kokoro-onnx` (onnxruntime on CPU; it phonemizes with eSpeak NG through `phonemizer` and `espeakng-loader`, for pronunciation only). A word takes about 0.1-0.5 s to generate on CPU; each is generated once and cached in `~/.cache/spectre/words/` (outside the repo).
- **Why Kokoro:** of the free local TTS engines reachable from the sandbox, it had the cleanest licence and the most natural voices. Piper (`pip install piper-tts`, GPL-3.0 package) was reachable too, but the Piper voices on GitHub release assets (rhasspy/piper v0.0.2: lessac, ryan, amy, ...) were trained on datasets with research-only or non-commercial licences (ryan: CC BY-NC-SA 4.0; lessac: the Blizzard 2013 research licence), and its permissively licensed voices are hosted on Hugging Face, which the sandbox can't reach.
- **What it's for:** a neural TTS used only as a word sampler, approved by the owner. It speaks each word flatly; the engine does all the singing (pitch, timing, vowel stretch, breath, doubling, effects). The rest of Spectre stays synthesized.
