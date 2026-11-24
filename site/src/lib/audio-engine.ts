import { EQ_FREQUENCIES, type EqSettings } from "./equalizer";

type AudioContextCtor = typeof AudioContext;

/**
 * The Web Audio graph behind the <audio> element:
 * source -> preamp -> 10 biquads -> analyser -> volume -> speakers.
 *
 * The graph is created lazily on the first user-initiated play, because browsers only
 * let an AudioContext start after a gesture, and a media element can be wired to a
 * context only once.
 */
export class AudioEngine {
  readonly analyserSize = 4096;
  private ctx: AudioContext | null = null;
  private preamp: GainNode | null = null;
  private filters: BiquadFilterNode[] = [];
  private volumeNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private bins: Uint8Array<ArrayBuffer> | null = null;
  private eq: { on: boolean; settings: EqSettings } | null = null;
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
    const preamp = ctx.createGain();
    const filters = EQ_FREQUENCIES.map((frequency, i) => {
      const b = ctx.createBiquadFilter();
      b.type = i === 0 ? "lowshelf" : i === EQ_FREQUENCIES.length - 1 ? "highshelf" : "peaking";
      b.frequency.value = frequency;
      b.Q.value = 1.1;
      return b;
    });
    const analyser = ctx.createAnalyser();
    analyser.fftSize = this.analyserSize;
    analyser.smoothingTimeConstant = 0.62;
    analyser.minDecibels = -86;
    analyser.maxDecibels = -18;
    const volume = ctx.createGain();

    let node: AudioNode = source.connect(preamp);
    for (const f of filters) node = node.connect(f);
    node.connect(analyser).connect(volume).connect(ctx.destination);

    this.ctx = ctx;
    this.preamp = preamp;
    this.filters = filters;
    this.analyserNode = analyser;
    this.volumeNode = volume;
    this.bins = new Uint8Array(analyser.frequencyBinCount);
    this.element.volume = 1;
    if (this.eq) this.setEq(this.eq.on, this.eq.settings);
    this.setVolume(this.gain);
    return true;
  }

  async resume(): Promise<void> {
    if (this.ctx && this.ctx.state !== "running") await this.ctx.resume();
  }

  setEq(on: boolean, settings: EqSettings): void {
    this.eq = { on, settings };
    if (!this.ctx || !this.preamp) return;
    const t = this.ctx.currentTime;
    this.preamp.gain.setTargetAtTime(on ? 10 ** (settings.pre / 20) : 1, t, 0.02);
    this.filters.forEach((b, i) => b.gain.setTargetAtTime(on ? settings.gains[i] : 0, t, 0.02));
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
