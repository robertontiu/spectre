type AudioContextCtor = typeof AudioContext;

/**
 * The Web Audio graph behind the <audio> element:
 * source -> analyser -> volume -> speakers.
 *
 * The tracks are mastered, so nothing in the graph colours them: the analyser only reads
 * them for the visualizer, and the volume gain is 1 at full volume (the element's own
 * volume stays at 1), so the level matches the raw element.
 *
 * The graph is created lazily on the first user-initiated play, because browsers only
 * let an AudioContext start after a gesture, and a media element can be wired to a
 * context only once.
 */
export class AudioEngine {
  readonly analyserSize = 4096;
  private ctx: AudioContext | null = null;
  private volumeNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private bins: Uint8Array<ArrayBuffer> | null = null;
  private gain = 1;

  constructor(readonly element: HTMLAudioElement) {}

  /** Builds the graph if needed. Returns false where Web Audio is unavailable. */
  ensureGraph(): boolean {
    if (this.ctx) return true;
    const Ctor: AudioContextCtor | undefined =
      window.AudioContext ?? (window as unknown as { webkitAudioContext?: AudioContextCtor }).webkitAudioContext;
    if (!Ctor) return false;

    const ctx = new Ctor();
    const source = ctx.createMediaElementSource(this.element);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = this.analyserSize;
    analyser.smoothingTimeConstant = 0.62;
    analyser.minDecibels = -86;
    analyser.maxDecibels = -18;
    const volume = ctx.createGain();

    source.connect(analyser).connect(volume).connect(ctx.destination);

    this.ctx = ctx;
    this.analyserNode = analyser;
    this.volumeNode = volume;
    this.bins = new Uint8Array(analyser.frequencyBinCount);
    this.element.volume = 1;
    this.setVolume(this.gain);
    return true;
  }

  async resume(): Promise<void> {
    if (this.ctx && this.ctx.state !== "running") await this.ctx.resume();
  }

  setVolume(gain: number): void {
    this.gain = gain;
    if (this.ctx && this.volumeNode) this.volumeNode.gain.setTargetAtTime(gain, this.ctx.currentTime, 0.02);
    // Before the graph exists (an autoplayed track link), the element's own volume applies.
    else this.element.volume = gain;
  }

  /** Hz covered by one analyser bin (a 44.1 kHz guess until the graph exists). */
  get binHz(): number {
    return (this.ctx?.sampleRate ?? 44100) / this.analyserSize;
  }

  /** Fills and returns the current frequency data, or null before the graph exists. */
  frequencyData(): Uint8Array | null {
    if (!this.analyserNode || !this.bins) return null;
    this.analyserNode.getByteFrequencyData(this.bins);
    return this.bins;
  }
}
