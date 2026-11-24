import { oklabToRgb, type Lab, type RGB } from "@/lib/color";
import { BACK, FRONT, Plane, driftX, type Ctx2D, type View } from "./field-scene";

/*
 * The background field's frame loop, with no DOM access, so it can run in a worker (on an
 * OffscreenCanvas, off the page's main thread) or, where workers can't draw, on the page.
 * Times are epoch ms (performance.timeOrigin + performance.now()), the same on both sides.
 */

/** Frames per second of the drift (the motion is time-based, so it stays smooth). */
const FPS = 30;
/** Canvas pixels per CSS px (the layers are soft; the crisp apparition stays SVG)... */
export const MAX_SCALE = 0.75;
/** ...within this many pixels per plane (about 1280 x 800 at 0.75). */
const PLANE_BUDGET = 720_000;
/** Pre-rendered layers: pixels per CSS px. */
const MAX_SPRITE_RES = 0.5;
/**
 * A safety net for devices that draw canvases without a GPU: if the drift cannot hold about
 * 20 fps for two seconds, the planes step down in resolution (never below 0.4).
 */
const SLOW_FRAME_MS = 48;
const MIN_SCALE = 0.4;

export const epoch = () => performance.timeOrigin + performance.now();

/** A colour glide: from `from` to `to` (OKLab field tones), starting at `start` (epoch ms). */
export type FieldColors = { from: Lab[]; to: Lab[]; start: number; ms: number };
const ease = (x: number) => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2);
export function labAt(c: FieldColors, at: number): Lab[] {
  const k = ease(Math.min(1, Math.max(0, (at - c.start) / c.ms)));
  return c.to.map((v, i) => v.map((x, j) => c.from[i][j] + (x - c.from[i][j]) * k) as Lab);
}
const fading = (c: FieldColors, at: number) => at - c.start < c.ms;

type Canvas = HTMLCanvasElement | OffscreenCanvas;

/** Messages from the page to the renderer. */
export type FieldMessage =
  | { type: "init"; back: OffscreenCanvas; front: OffscreenCanvas; origin: number; adaptive: boolean; probe: boolean }
  | { type: "view"; view: View; maxScale: number }
  | { type: "colors"; colors: FieldColors }
  | { type: "state"; hidden: boolean; reduced: boolean }
  | { type: "freeze"; ms: number | null };

/** Messages from the renderer: the first frame is up; test probes. */
export type FieldReport =
  { type: "hello" } | { type: "drawn" } | { type: "cost"; frames: number; ms: number; drift: number };

type Raf = (cb: () => void) => number;
const scheduleFrame: Raf =
  typeof requestAnimationFrame === "function"
    ? (cb) => requestAnimationFrame(cb)
    : (cb) => setTimeout(cb, 1000 / 60) as unknown as number;

export class FieldRenderer {
  private backPlane = new Plane(BACK);
  private frontPlane = new Plane(FRONT);
  private bctx: Ctx2D | null;
  private fctx: Ctx2D | null;
  private view: View | null = null;
  private maxScale = MAX_SCALE;
  private scale = MAX_SCALE;
  private spriteRes = MAX_SPRITE_RES;
  private colors: FieldColors | null = null;
  private hidden = false;
  private reduced = false;
  private frozen: number | null = null;
  private raf = 0;
  private lastDraw = -Infinity;
  private lastTick = 0;
  private intervals: number[] = [];
  private drawn = false;
  private cost = { frames: 0, ms: 0 };

  /**
   * @param origin the page's performance.timeOrigin: drift time is measured from it, as the
   *   CSS animations of the first-paint stand-in were
   */
  constructor(
    private readonly back: Canvas,
    private readonly front: Canvas,
    private readonly origin: number,
    private readonly adaptive: boolean,
    private readonly report: (r: FieldReport) => void,
    private readonly probe = false,
  ) {
    this.bctx = back.getContext("2d") as Ctx2D | null;
    this.fctx = front.getContext("2d") as Ctx2D | null;
  }

  handle(m: FieldMessage): void {
    if (m.type === "view") {
      this.view = m.view;
      this.maxScale = m.maxScale;
      this.resize();
    } else if (m.type === "colors") {
      this.colors = m.colors;
    } else if (m.type === "state") {
      const shown = this.hidden && !m.hidden;
      this.hidden = m.hidden;
      this.reduced = m.reduced;
      if (shown) {
        // Back from a hidden tab: the current state at once (the glide keeps its clock).
        this.intervals = [];
        this.lastTick = 0;
      }
    } else if (m.type === "freeze") {
      this.frozen = m.ms === null ? null : m.ms / 1000;
    }
    this.draw(epoch());
    this.schedule();
  }

  private resize(): void {
    const v = this.view;
    if (!v) return;
    this.scale = Math.min(this.maxScale, Math.sqrt(PLANE_BUDGET / (v.w * v.h)));
    this.spriteRes = Math.min(MAX_SPRITE_RES, this.scale);
    const pw = Math.max(1, Math.round(v.w * this.scale));
    const ph = Math.max(1, Math.round(v.h * this.scale));
    for (const c of [this.back, this.front]) {
      if (c.width !== pw || c.height !== ph) {
        c.width = pw;
        c.height = ph;
      }
    }
  }

  private draw(now: number): void {
    const { view, colors, bctx, fctx } = this;
    if (!view || !colors || !bctx || !fctx || this.hidden) return;
    const t0 = performance.now();
    this.lastDraw = now;
    const fields = labAt(colors, now).map(oklabToRgb) as RGB[];
    const key = fields.map((c) => c.map(Math.round).join()).join(";");
    const t = this.reduced ? null : (this.frozen ?? (now - this.origin) / 1000);
    this.backPlane.draw(bctx, view, this.scale, this.spriteRes, fields, key, t);
    this.frontPlane.draw(fctx, view, this.scale, this.spriteRes, fields, key, t);
    if (!this.drawn) {
      this.drawn = true;
      this.report({ type: "drawn" });
    }
    if (this.probe) {
      this.cost.frames++;
      this.cost.ms += performance.now() - t0;
      this.report({ type: "cost", ...this.cost, drift: t === null ? 0 : driftX(view, t) });
    }
  }

  private schedule(): void {
    if (!this.raf && !this.hidden) this.raf = scheduleFrame(this.tick);
  }

  private tick = () => {
    this.raf = 0;
    if (this.hidden || !this.colors) return;
    const now = epoch();
    if (now - this.lastDraw >= 1000 / FPS - 4) {
      if (this.adaptive && this.lastTick && !this.reduced) this.adapt(now - this.lastTick);
      this.lastTick = now;
      this.draw(now);
    }
    if (!this.reduced || fading(this.colors, now)) this.schedule();
  };

  private adapt(interval: number): void {
    this.intervals.push(interval);
    if (this.intervals.length < 60) return;
    const median = [...this.intervals].sort((a, b) => a - b)[30];
    this.intervals = [];
    if (median > SLOW_FRAME_MS && this.scale > MIN_SCALE) {
      this.maxScale = Math.max(MIN_SCALE, this.scale * 0.7);
      this.resize();
    }
  }
}
