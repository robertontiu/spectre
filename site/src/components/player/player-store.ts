import { AudioEngine } from "@/lib/audio-engine";
import { paletteFrom } from "@/lib/color";
import {
  DEFAULT_PRESET,
  EQ_FREQUENCIES,
  clampDb,
  isPresetName,
  presetSettings,
  type BandKey,
  type EqSettings,
  type PresetChoice,
} from "@/lib/equalizer";
import { PaletteAnimator } from "@/lib/palette-animator";
import { IS_PREVIEW, audioPath, trackPath } from "@/lib/site";
import type { Track } from "@/lib/tracks";

export type RepeatMode = "all" | "one" | "off";

/** How long the background glides to a new track's colours (AtmosphereField). */
export const FADE_MS = 2000;
const REPEAT_MODES: readonly RepeatMode[] = ["all", "one", "off"];

export type PlayerState = {
  /** Index of the selected track. */
  current: number;
  playing: boolean;
  /** Playback position and length of the selected track, in seconds. */
  time: number;
  duration: number;
  /** A playback problem to show under the title. */
  message: string | null;
  /** Autoplay was blocked: the next tap or key press anywhere starts playback. */
  needsGesture: boolean;
  shuffle: boolean;
  repeat: RepeatMode;
  eqOn: boolean;
  preset: PresetChoice;
  eq: EqSettings;
  volume: number;
  muted: boolean;
};

const STORAGE_KEY = "spectre.v1";

/** The persisted shape (kept compatible with the static showcase). */
type Stored = {
  shuffle?: unknown;
  repeat?: unknown;
  eqOn?: unknown;
  preset?: unknown;
  eq?: { pre?: unknown; g?: unknown };
  vol?: unknown;
  muted?: unknown;
};

/**
 * The player's state and actions, outside React so that audio events, media keys and
 * the canvases always see the latest state. Components read it with `usePlayer`.
 */
export class PlayerStore {
  readonly palette: PaletteAnimator;
  engine: AudioEngine | null = null;
  private state: PlayerState;
  private listeners = new Set<() => void>();
  private audio: HTMLAudioElement | null = null;

  /**
   * @param initial index of the track to open with
   * @param autoplay try to start it at once (track links); the home page waits for play
   */
  constructor(
    readonly tracks: readonly Track[],
    readonly initial = 0,
    private readonly autoplay = false,
  ) {
    const colors = tracks[initial]?.colors ?? [];
    this.state = {
      current: initial,
      playing: false,
      time: 0,
      duration: tracks[initial]?.duration ?? 0,
      message: null,
      needsGesture: false,
      shuffle: false,
      repeat: "all",
      eqOn: true,
      preset: DEFAULT_PRESET,
      eq: presetSettings(DEFAULT_PRESET),
      volume: 0.85,
      muted: false,
    };
    this.palette = new PaletteAnimator(paletteFrom(colors));
  }

  /* ---- external store protocol ---- */

  getState = (): PlayerState => this.state;

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  private set(patch: Partial<PlayerState>, persist = false): void {
    this.state = { ...this.state, ...patch };
    this.listeners.forEach((l) => l());
    if (persist) this.save();
  }

  /* ---- lifecycle ---- */

  /** Wires the store to the page's <audio> element. Returns a cleanup function. */
  attach(audio: HTMLAudioElement): () => void {
    if (this.audio !== audio) {
      this.audio = audio;
      this.engine = new AudioEngine(audio);
    }
    this.restore();
    this.applyEq();
    this.applyVolume();
    if (this.tracks.length) this.select(this.state.current, false, { syncUrl: false });

    const on: Record<string, () => void> = {
      ended: () => this.step(1, true),
      play: () => this.set({ playing: true }),
      pause: () => this.set({ playing: false }),
      error: () => {
        if (audio.getAttribute("src")) this.set({ message: "This track could not be loaded." });
      },
      timeupdate: () => this.set({ time: audio.currentTime }),
      loadedmetadata: () => this.set({ duration: audio.duration }),
    };
    for (const [type, fn] of Object.entries(on)) audio.addEventListener(type, fn);
    const releaseMediaKeys = this.bindMediaSession();
    const releaseGesture = this.bindFirstGesture();
    if (this.autoplay) void this.play({ auto: true });

    return () => {
      for (const [type, fn] of Object.entries(on)) audio.removeEventListener(type, fn);
      releaseMediaKeys();
      releaseGesture();
    };
  }

  /* ---- playback ---- */

  select = (index: number, autoplay: boolean, { syncUrl = true } = {}): void => {
    const track = this.tracks[index];
    if (!track || !this.audio) return;
    this.audio.src = audioPath(track);
    this.set({ current: index, time: 0, duration: track.duration, message: null });
    this.palette.setTarget(paletteFrom(track.colors));
    // Keep the address bar on the playing track without a navigation (no remount, no scroll).
    if (syncUrl && !IS_PREVIEW && location.pathname !== trackPath(track)) {
      history.replaceState(history.state, "", trackPath(track));
    }
    if ("mediaSession" in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({ title: track.title, artist: track.artist });
      } catch {
        /* Media Session metadata is optional. */
      }
    }
    if (autoplay) void this.play();
  };

  /**
   * Starts playback. An automatic start (a track link opening) skips the Web Audio graph,
   * whose AudioContext could only start muted without a gesture; the graph is wired on the
   * visitor's first tap or key press instead. If the browser blocks it, the play button
   * asks for a tap.
   */
  play = async ({ auto = false } = {}): Promise<void> => {
    const audio = this.audio;
    if (!audio || !this.tracks.length) return;
    if (!auto) this.engine?.ensureGraph();
    try {
      if (!auto) await this.engine?.resume();
      await audio.play();
      if (this.state.needsGesture) this.set({ needsGesture: false });
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      if (auto) this.set({ needsGesture: true });
      else this.set({ message: "Playback was blocked. Press play again." });
    }
  };

  pause = (): void => this.audio?.pause();

  togglePlay = (): void => {
    if (this.audio?.paused) void this.play();
    else this.pause();
  };

  next = (): void => this.step(1, false);

  /** Restarts the track if it has played for more than 3 s, otherwise goes back one. */
  previous = (): void => {
    if (this.audio && this.audio.currentTime > 3) this.audio.currentTime = 0;
    else this.step(-1, false);
  };

  private step(direction: 1 | -1, auto: boolean): void {
    const { current, repeat, shuffle } = this.state;
    const n = this.tracks.length;
    if (!n || !this.audio) return;
    if (auto && repeat === "one") {
      this.audio.currentTime = 0;
      void this.play();
      return;
    }
    if (shuffle) {
      this.select(this.randomOther(), true);
      return;
    }
    let j = current + direction;
    if (j >= n) {
      if (auto && repeat === "off") {
        this.audio.pause();
        this.select(0, false);
        return;
      }
      j = 0;
    }
    if (j < 0) j = n - 1;
    this.select(j, true);
  }

  private randomOther(): number {
    const n = this.tracks.length;
    if (n < 2) return 0;
    let j: number;
    do j = Math.floor(Math.random() * n);
    while (j === this.state.current);
    return j;
  }

  /** The best known length of the selected track. */
  get trackLength(): number {
    const d = this.audio?.duration;
    return d && Number.isFinite(d) ? d : (this.tracks[this.state.current]?.duration ?? 0);
  }

  seekToFraction = (fraction: number): void => {
    const d = this.trackLength;
    if (this.audio && d) this.audio.currentTime = fraction * d;
  };

  seekBy = (seconds: number): void => {
    if (!this.audio) return;
    this.audio.currentTime = Math.max(0, Math.min(this.trackLength, this.audio.currentTime + seconds));
  };

  /* ---- modes ---- */

  toggleShuffle = (): void => this.set({ shuffle: !this.state.shuffle }, true);

  cycleRepeat = (): void => {
    const next: Record<RepeatMode, RepeatMode> = { all: "one", one: "off", off: "all" };
    this.set({ repeat: next[this.state.repeat] }, true);
  };

  /* ---- volume ---- */

  setVolume = (volume: number): void => {
    this.set({ volume, muted: false }, true);
    this.applyVolume();
  };

  toggleMute = (): void => {
    this.set({ muted: !this.state.muted }, true);
    this.applyVolume();
  };

  private applyVolume(): void {
    const { muted, volume } = this.state;
    this.engine?.setVolume(muted ? 0 : volume);
  }

  /* ---- equalizer ---- */

  setBand = (band: BandKey, value: number): void => {
    const v = clampDb(value);
    const { eq } = this.state;
    if ((band === "pre" ? eq.pre : eq.gains[band]) === v) return;
    const next: EqSettings =
      band === "pre" ? { ...eq, pre: v } : { ...eq, gains: eq.gains.map((g, i) => (i === band ? v : g)) };
    this.set({ eq: next, preset: "Custom" }, true);
    this.applyEq();
  };

  setPreset = (preset: PresetChoice): void => {
    this.set({ preset, eq: isPresetName(preset) ? presetSettings(preset) : this.state.eq }, true);
    this.applyEq();
  };

  toggleEq = (): void => {
    this.set({ eqOn: !this.state.eqOn }, true);
    this.applyEq();
  };

  private applyEq(): void {
    this.engine?.setEq(this.state.eqOn, this.state.eq);
  }

  /* ---- keyboard and media keys ---- */

  /** Space plays or pauses, left and right arrows seek 5 s (outside form controls). */
  handleKey = (e: KeyboardEvent): void => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const target = e.target instanceof Element ? e.target : null;
    const inField = !!target?.closest("input,select,textarea,[role=slider]");
    if (e.key === " " && !inField && !target?.closest("button")) {
      e.preventDefault();
      this.togglePlay();
    } else if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && !inField) {
      e.preventDefault();
      this.seekBy(e.key === "ArrowRight" ? 5 : -5);
    }
  };

  /**
   * The first tap or key press anywhere wires the Web Audio graph (the equalizer, volume
   * and visualizer need it), and starts playback if autoplay was blocked. Controls handle
   * their own taps, so only the graph is wired for those.
   */
  private bindFirstGesture(): () => void {
    const onGesture = (e: Event) => {
      if (e instanceof KeyboardEvent && ["Tab", "Shift", "Control", "Alt", "Meta"].includes(e.key)) return;
      release();
      const target = e.target instanceof Element ? e.target : null;
      const onControl = !!target?.closest("button,a,input,select,textarea,[role=slider]");
      const isSpace = e instanceof KeyboardEvent && e.key === " ";
      if (this.state.needsGesture && !onControl && !isSpace) {
        void this.play();
        return;
      }
      if (this.engine?.ensureGraph()) void this.engine.resume().catch(() => {});
    };
    const release = () => {
      document.removeEventListener("pointerdown", onGesture, true);
      document.removeEventListener("keydown", onGesture, true);
    };
    document.addEventListener("pointerdown", onGesture, true);
    document.addEventListener("keydown", onGesture, true);
    return release;
  }

  private bindMediaSession(): () => void {
    if (!("mediaSession" in navigator)) return () => {};
    const handlers: [MediaSessionAction, MediaSessionActionHandler][] = [
      ["play", () => void this.play()],
      ["pause", this.pause],
      ["previoustrack", this.previous],
      ["nexttrack", this.next],
    ];
    const bind = (h: MediaSessionActionHandler | null) => (action: MediaSessionAction) => {
      try {
        navigator.mediaSession.setActionHandler(action, h);
      } catch {
        /* Unsupported action. */
      }
    };
    handlers.forEach(([action, h]) => bind(h)(action));
    return () => handlers.forEach(([action]) => bind(null)(action));
  }

  /* ---- persistence ---- */

  private restore(): void {
    let st: Stored = {};
    try {
      st = (JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") as Stored) || {};
    } catch {
      st = {};
    }
    // "Spectre (hip-hop)" was the default preset's earlier name.
    const storedPreset = st.preset === "Spectre (hip-hop)" ? "Spectre" : st.preset;
    const preset: PresetChoice =
      storedPreset === "Custom" || isPresetName(storedPreset) ? storedPreset : DEFAULT_PRESET;
    const storedGains = st.eq && Array.isArray(st.eq.g) ? (st.eq.g as unknown[]) : null;
    const eq: EqSettings =
      preset === "Custom" && storedGains
        ? {
            pre: Number(st.eq?.pre) || 0,
            gains: EQ_FREQUENCIES.map((_, i) => clampDb(Number(storedGains[i]) || 0)),
          }
        : presetSettings(isPresetName(preset) ? preset : DEFAULT_PRESET);
    this.set({
      shuffle: !!st.shuffle,
      repeat: REPEAT_MODES.includes(st.repeat as RepeatMode) ? (st.repeat as RepeatMode) : "all",
      eqOn: st.eqOn !== false,
      preset,
      eq,
      volume: typeof st.vol === "number" ? Math.min(1, Math.max(0, st.vol)) : 0.85,
      muted: !!st.muted,
    });
  }

  private save(): void {
    const { shuffle, repeat, eqOn, preset, eq, volume, muted } = this.state;
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ shuffle, repeat, eqOn, preset, eq: { pre: eq.pre, g: eq.gains }, vol: volume, muted }),
      );
    } catch {
      /* Storage may be unavailable (private mode, sandboxed frames). */
    }
  }
}
