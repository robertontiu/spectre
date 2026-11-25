import { AudioEngine } from "@/lib/audio-engine";
import { paletteFrom } from "@/lib/color";
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
  volume: number;
  muted: boolean;
};

const STORAGE_KEY = "spectre.v1";

/**
 * The persisted shape. Older saves also hold equalizer fields (eqOn, preset, eq); they are
 * ignored, and dropped on the next save.
 */
type Stored = {
  shuffle?: unknown;
  repeat?: unknown;
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
  /** When the audio was last reloaded after an error or a stall (at most once a minute). */
  private recoveredAt = 0;
  /** When the current source was resolved (the audio route's signed URL was handed out). */
  private loadedAt = 0;
  private stallTimer: ReturnType<typeof setTimeout> | undefined;

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
    this.applyVolume();
    if (this.tracks.length) this.select(this.state.current, false, { syncUrl: false });

    const on: Record<string, () => void> = {
      ended: () => this.step(1, true),
      play: () => this.set({ playing: true }),
      pause: () => {
        this.clearStall();
        this.set({ playing: false });
      },
      error: () => {
        if (!audio.getAttribute("src")) return;
        if (this.recover(audio)) return;
        this.set({ message: "This track could not be loaded." });
      },
      timeupdate: () => {
        this.clearStall();
        this.set({ time: audio.currentTime });
      },
      waiting: () => this.watchStall(audio),
      stalled: () => this.watchStall(audio),
      playing: () => this.clearStall(),
      emptied: () => this.clearStall(),
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

  /* ---- signed URLs ----
   * The audio route hands out signed URLs that expire (SPECTRE_SIGNED_URL_TTL, an hour by
   * default, and always at least that long after they are handed out). The element keeps
   * using the URL it was given for every later range request, so a seek or a re-buffer
   * after a long pause can hit an expired one. Browsers do not always report that as an
   * error (Chrome just stalls), so the player
   *  - re-resolves the source before resuming or seeking once it is older than
   *    SOURCE_MAX_AGE (well inside the TTL),
   *  - and reloads after an error, or a stall of STALL_MS while playing,
   * carrying on from the same spot. Error and stall reloads happen at most once a minute,
   * so a track that really is missing still reports the error.
   */

  private static readonly SOURCE_MAX_AGE = 25 * 60_000;
  private static readonly STALL_MS = 8_000;

  private stale(audio: HTMLAudioElement): boolean {
    return !IS_PREVIEW && Date.now() - this.loadedAt > PlayerStore.SOURCE_MAX_AGE && !!audio.getAttribute("src");
  }

  /** Loads the same track again (a fresh signed URL), then seeks to `at` and resumes if asked. */
  private reload(audio: HTMLAudioElement, at: number, resume: boolean): void {
    this.clearStall();
    this.loadedAt = Date.now();
    audio.addEventListener(
      "loadedmetadata",
      () => {
        if (at > 0) audio.currentTime = Math.min(at, audio.duration || at);
        if (resume) void audio.play().catch(() => this.set({ playing: false }));
      },
      { once: true },
    );
    audio.load();
  }

  private recover(audio: HTMLAudioElement): boolean {
    const now = Date.now();
    if (now - this.recoveredAt < 60_000 || audio.error?.code === MediaError.MEDIA_ERR_ABORTED) return false;
    this.recoveredAt = now;
    this.reload(audio, audio.currentTime, this.state.playing);
    return true;
  }

  private watchStall(audio: HTMLAudioElement): void {
    if (audio.paused || this.stallTimer) return;
    this.stallTimer = setTimeout(() => {
      this.stallTimer = undefined;
      if (!audio.paused && audio.readyState < HTMLMediaElement.HAVE_FUTURE_DATA) this.recover(audio);
    }, PlayerStore.STALL_MS);
  }

  private clearStall(): void {
    clearTimeout(this.stallTimer);
    this.stallTimer = undefined;
  }

  /** Seeks, re-resolving an old source first. */
  private seekTo(seconds: number): void {
    const audio = this.audio;
    if (!audio) return;
    if (this.stale(audio)) this.reload(audio, seconds, !audio.paused);
    else audio.currentTime = seconds;
  }

  /* ---- playback ---- */

  select = (index: number, autoplay: boolean, { syncUrl = true } = {}): void => {
    const track = this.tracks[index];
    if (!track || !this.audio) return;
    this.audio.src = audioPath(track);
    this.loadedAt = Date.now();
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
    if (audio.currentTime > 0 && this.stale(audio)) {
      if (!auto) await this.engine?.resume();
      this.reload(audio, audio.currentTime, true);
      return;
    }
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
    if (this.audio && this.audio.currentTime > 3) this.seekTo(0);
    else this.step(-1, false);
  };

  private step(direction: 1 | -1, auto: boolean): void {
    const { current, repeat, shuffle } = this.state;
    const n = this.tracks.length;
    if (!n || !this.audio) return;
    if (auto && repeat === "one") {
      this.seekTo(0);
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
    if (d) this.seekTo(fraction * d);
  };

  seekBy = (seconds: number): void => {
    if (!this.audio) return;
    this.seekTo(Math.max(0, Math.min(this.trackLength, this.audio.currentTime + seconds)));
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
   * The first tap or key press anywhere wires the Web Audio graph (the volume and the
   * visualizer need it), and starts playback if autoplay was blocked. Controls handle
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
      const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) st = parsed as Stored;
    } catch {
      st = {};
    }
    this.set({
      shuffle: !!st.shuffle,
      repeat: REPEAT_MODES.includes(st.repeat as RepeatMode) ? (st.repeat as RepeatMode) : "all",
      volume: typeof st.vol === "number" && Number.isFinite(st.vol) ? Math.min(1, Math.max(0, st.vol)) : 0.85,
      muted: !!st.muted,
    });
  }

  private save(): void {
    const { shuffle, repeat, volume, muted } = this.state;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ shuffle, repeat, vol: volume, muted }));
    } catch {
      /* Storage may be unavailable (private mode, sandboxed frames). */
    }
  }
}
