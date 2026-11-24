import type { RGB } from "@/lib/color";

/*
 * The soft layers of the background (the mist and fog banks and the track-coloured field),
 * described as data and drawn into a low-resolution canvas each frame. The geometry,
 * colours and drift mirror the CSS of the first-paint layers in atmosphere.css (which the
 * canvas replaces once it has drawn): same boxes, same radial gradients, same keyframes
 * and timing, so the two look the same.
 *
 * Two planes keep the original stacking: `back` lies under the apparition (tints, the high
 * fog), `front` over it (mist, low fog, wisps and the whole bottom field).
 */

/**
 * Viewport measures in CSS px: `vw`, `vh`, `vmin`, `vmax` are 100 of each unit (the viewport's
 * width, height and so on); `top` is the height of the brand banner region (.atop).
 */
export type View = { w: number; h: number; top: number; vw: number; vh: number; vmin: number; vmax: number };
type Box = [x: number, y: number, w: number, h: number];
type Region = { w: number; h: number };

/** A colour: one of the track's three field tones, or a fixed neutral one. */
type Ink = { f: 0 | 1 | 2; a: number } | { rgb: RGB; a: number };
/** An elliptical radial gradient: radii and centre as fractions of the box, colour fading out at `stop`. */
type Grad = { rx: number; ry: number; cx: number; cy: number; stop: number; ink: Ink };

/* Keyframes: transform as [offset, translateX (vw), translateY (vh), rotate (deg), scaleX, scaleY]. */
type TKey = [number, number, number, number, number, number];
type OKey = [number, number];
type Dir = "normal" | "alternate" | "alternate-reverse";
type Timing<K> = { keys: K[]; dur: number; dir: Dir; delay?: number };

type Layer = {
  region: "top" | "bot";
  box: (v: View, r: Region) => Box;
  /** Gradients bottom first (CSS lists backgrounds top first). */
  grads?: Grad[];
  /** A vertical linear gradient across the box: [position in px from the top, rgba]. */
  linear?: (v: View, r: Region) => [number, [number, number, number, number]][];
  /** Vertical alpha mask: [position in px from the top, alpha]. */
  mask?: (v: View, r: Region) => [number, number][];
  opacity?: number;
  move?: Timing<TKey>;
  fade?: Timing<OKey>;
  /** Hidden under reduced motion (the wisps). */
  motionOnly?: boolean;
};

const N = (r: number, g: number, b: number, a: number): Ink => ({ rgb: [r, g, b], a });
const F = (f: 0 | 1 | 2, a: number): Ink => ({ f, a });
const g = (rx: number, ry: number, cx: number, cy: number, ink: Ink, stop = 0.7): Grad => ({
  rx,
  ry,
  cx,
  cy,
  stop,
  ink,
});
/** radial-gradient(closest-side, ink, transparent) */
const closest = (ink: Ink): Grad => g(0.5, 0.5, 0.5, 0.5, ink, 1);

/* The CSS keyframes. */
const fgA: TKey[] = [
  [0, -20, 1, -3, 1, 1],
  [1, 24, -4, 3, 1.15, 1.15],
];
const fgB: TKey[] = [
  [0, 22, 3, 2.5, 1.1, 1.1],
  [1, -24, -3, -3, 0.94, 0.94],
];
const fgC: TKey[] = [
  [0, -6, 4, -1, 1, 1],
  [0.5, 18, -3, 4, 1.14, 1.14],
  [1, -20, 2, -3, 1.04, 1.04],
];
const fgO: OKey[] = [
  [0, 0.28],
  [1, 1],
];
const to = (x: number, y: number, s = 1): TKey[] => [
  [0, 0, 0, 0, 1, 1],
  [1, x, y, 0, s, s],
];
const rise: TKey[] = [
  [0, 0, 12, 0, 0.7, 0.6],
  [1, 0, -36, 0, 1.4, 1.6],
];
const riseO: OKey[] = [
  [0, 0],
  [0.35, 1],
  [1, 0],
];

/** A wide fog bank (.fg / .bf): box from vw and region percentages. */
const bank = (
  region: "top" | "bot",
  left: number,
  top: (r: Region, v: View) => number,
  width: number,
  height: (r: Region, v: View) => number,
  move: Timing<TKey>,
  fade: Timing<OKey>,
  grads: Grad[],
): Layer => ({
  region,
  box: (v, r) => [left * v.vw, top(r, v), width * v.vw, height(r, v)],
  move,
  fade,
  grads,
});
const pct = (p: number) => (r: Region) => r.h * p;

const tints: Layer[] = [
  { region: "top", box: (v, r) => [0.4 * v.vw, -0.3 * r.h, 0.85 * v.vw, 0.85 * r.h], grads: [closest(F(1, 0.16))] },
  { region: "top", box: (v, r) => [-0.3 * v.vw, 0.28 * r.h, 0.8 * v.vw, 0.7 * r.h], grads: [closest(F(0, 0.18))] },
  { region: "top", box: (v, r) => [0.1 * v.vw, 0.72 * r.h, 0.8 * v.vw, 0.5 * r.h], grads: [closest(F(0, 0.14))] },
];

const fg1 = (grads: Grad[]) =>
  bank(
    "top",
    -0.45,
    pct(0.02),
    1.9,
    pct(0.7),
    { keys: fgA, dur: 18, dir: "alternate" },
    { keys: fgO, dur: 7, dir: "alternate" },
    grads,
  );
const fg2 = (grads: Grad[]) =>
  bank(
    "top",
    -0.5,
    pct(0.22),
    2,
    pct(0.66),
    { keys: fgB, dur: 24, dir: "alternate" },
    { keys: fgO, dur: 9, dir: "alternate-reverse" },
    grads,
  );
const fg3 = (grads: Grad[]) =>
  bank(
    "top",
    -0.4,
    pct(0.3),
    1.8,
    pct(0.52),
    { keys: fgC, dur: 14, dir: "alternate" },
    { keys: fgO, dur: 6, dir: "alternate" },
    grads,
  );
const fg4 = (grads: Grad[]) =>
  bank(
    "top",
    -0.55,
    pct(0.5),
    2.1,
    pct(0.58),
    { keys: fgB, dur: 12, dir: "alternate-reverse" },
    { keys: fgO, dur: 8, dir: "alternate" },
    grads,
  );
/* The header's low fog (it lay over the logotype's feet); the header has the banner's height. */
const fg5 = (grads: Grad[]) =>
  bank(
    "top",
    -0.45,
    pct(0.66),
    1.9,
    pct(0.4),
    { keys: fgA, dur: 16, dir: "alternate-reverse" },
    { keys: fgO, dur: 8, dir: "alternate" },
    grads,
  );
const fg6 = bank(
  "top",
  -0.4,
  pct(-0.12),
  1.8,
  pct(0.42),
  { keys: fgC, dur: 28, dir: "alternate-reverse" },
  { keys: fgO, dur: 11, dir: "alternate" },
  [g(0.24, 0.34, 0.78, 0.44, N(150, 160, 195, 0.112)), g(0.3, 0.4, 0.35, 0.5, N(160, 180, 200, 0.14))],
);
const bf1 = (grads: Grad[]) =>
  bank(
    "bot",
    -0.5,
    (_r, v) => -0.24 * v.vh,
    2,
    (_r, v) => 0.72 * v.vh,
    { keys: fgB, dur: 20, dir: "alternate" },
    { keys: fgO, dur: 8, dir: "alternate" },
    grads,
  );
const bf2 = (grads: Grad[]) =>
  bank(
    "bot",
    -0.45,
    pct(0.28),
    1.9,
    pct(0.62),
    { keys: fgA, dur: 26, dir: "alternate-reverse" },
    { keys: fgO, dur: 10, dir: "alternate" },
    grads,
  );
const bf3 = (grads: Grad[]) =>
  bank(
    "bot",
    -0.55,
    pct(0.54),
    2.1,
    pct(0.56),
    { keys: fgC, dur: 30, dir: "alternate" },
    { keys: fgO, dur: 12, dir: "alternate-reverse" },
    grads,
  );

const mist = (box: (v: View, r: Region) => Box, ink: Ink, move: Timing<TKey>): Layer => ({
  region: "top",
  box,
  grads: [closest(ink)],
  move,
});

const wisp = (marginVmin: number, dur: number, delay: number): Layer => ({
  region: "top",
  box: (v, r) => [v.w / 2 + marginVmin * v.vmin, 0.7 * r.h - 0.34 * v.vmin, 0.16 * v.vmin, 0.34 * v.vmin],
  grads: [closest(N(215, 240, 255, 0.12))],
  move: { keys: rise, dur, dir: "normal", delay },
  fade: { keys: riseO, dur, dir: "normal", delay },
  motionOnly: true,
});

/* The masks that dissolve the banner's coloured floor and the bottom field's ceiling. */
const zOf = (v: View) => Math.min(0.25 * v.vh, 200);
const riseMask = (v: View, r: Region): [number, number][] => {
  const z = zOf(v);
  const H = 0.62 * r.h + z;
  return [
    [H - 2 * z, 1],
    [H - 1.5 * z, 0.85],
    [H - z, 0.5],
    [H - 0.5 * z, 0.15],
    [H, 0],
  ];
};
const sinkMask = (v: View): [number, number][] => {
  const z = zOf(v);
  return [
    [0, 0],
    [0.5 * z, 0.15],
    [z, 0.5],
    [1.5 * z, 0.85],
    [2 * z, 1],
  ];
};

const blob = (box: (v: View, r: Region) => Box, f: 0 | 1 | 2, opacity: number, move: Timing<TKey>): Layer => ({
  region: "bot",
  box,
  grads: [closest(F(f, 1))],
  opacity,
  move,
});

export const BACK: Layer[] = [
  ...tints,
  fg6,
  fg1([g(0.3, 0.44, 0.84, 0.6, F(1, 0.25))]),
  fg1([g(0.22, 0.34, 0.52, 0.38, N(150, 165, 205, 0.182)), g(0.26, 0.4, 0.18, 0.5, N(170, 195, 215, 0.224))]),
  fg2([g(0.28, 0.4, 0.7, 0.45, N(160, 185, 205, 0.196))]),
  fg2([g(0.24, 0.38, 0.3, 0.55, F(0, 0.28))]),
];

export const FRONT: Layer[] = [
  mist((v, r) => [-0.4 * v.vw, 0.34 * r.h, 1.3 * v.vw, 0.46 * r.h], N(150, 140, 215, 0.3), {
    keys: to(26, 0),
    dur: 46,
    dir: "alternate",
  }),
  mist((v, r) => [v.w + 0.5 * v.vw - 1.2 * v.vw, 0.06 * r.h, 1.2 * v.vw, 0.42 * r.h], N(150, 190, 178, 0.24), {
    keys: to(-30, 0),
    dur: 58,
    dir: "alternate",
  }),
  mist((v, r) => [-0.3 * v.vw, 0.68 * r.h, 1.6 * v.vw, 0.4 * r.h], N(195, 228, 245, 0.2), {
    keys: to(26, 0),
    dur: 64,
    dir: "alternate-reverse",
  }),
  fg3([g(0.22, 0.34, 0.9, 0.56, F(0, 0.2))]),
  fg3([g(0.18, 0.3, 0.62, 0.46, N(170, 190, 220, 0.154)), g(0.2, 0.36, 0.26, 0.5, N(185, 210, 228, 0.182))]),
  fg4([g(0.26, 0.3, 0.75, 0.55, F(1, 0.22))]),
  fg4([g(0.3, 0.34, 0.4, 0.5, N(175, 198, 218, 0.21))]),
  wisp(-0.08, 16, 0),
  wisp(-0.24, 19, -6),
  wisp(0.08, 22, -13),
  {
    region: "top",
    box: (v, r) => [0, 0.38 * r.h, v.w, 0.62 * r.h + zOf(v)],
    grads: [
      g(0.9, 0.6, 0.5, 1, F(2, 0.4), 0.75),
      g(0.6, 0.9, 0.8, 1, F(1, 0.24)),
      g(0.7, 1, 0.25, 1, F(0, 0.34), 0.72),
    ],
    mask: riseMask,
  },
  blob((v, r) => [-0.3 * v.vmax, 0.12 * r.h, 0.9 * v.vmax, 0.9 * v.vmax], 0, 0.64, {
    keys: to(8, -4, 1.12),
    dur: 28,
    dir: "alternate",
  }),
  blob((v, r) => [v.w + 0.34 * v.vmax - 0.9 * v.vmax, 0.3 * r.h, 0.9 * v.vmax, 0.9 * v.vmax], 1, 0.5, {
    keys: to(-10, 6, 0.9),
    dur: 34,
    dir: "alternate",
  }),
  blob((v, r) => [0.1 * v.w, r.h + 0.4 * v.vmax - 0.9 * v.vmax, 0.9 * v.vmax, 0.9 * v.vmax], 2, 0.85, {
    keys: to(6, -8, 1.1),
    dur: 40,
    dir: "alternate",
  }),
  {
    // The shade over the blobs (.blobs::after).
    region: "bot",
    box: (v, r) => [0, 0, v.w, r.h],
    linear: (_v, r) => [
      [0, [5, 7, 13, 0]],
      [70, [5, 7, 13, 0.03]],
      [150, [5, 7, 13, 0.07]],
      [250, [5, 7, 13, 0.11]],
      [400, [5, 7, 13, 0.12]],
      [0.55 * r.h, [5, 7, 13, 0.1]],
      [r.h, [5, 7, 13, 0.45]],
    ],
  },
  {
    region: "bot",
    box: (v) => [0, -zOf(v), v.w, Math.min(0.7 * v.vh, 560) + zOf(v)],
    grads: [
      g(0.9, 0.6, 0.5, 0, F(2, 0.4), 0.75),
      g(0.6, 0.9, 0.8, 0, F(1, 0.24)),
      g(0.7, 1, 0.25, 0, F(0, 0.34), 0.72),
    ],
    mask: (v) => sinkMask(v),
  },
  bf1([g(0.24, 0.36, 0.7, 0.55, F(0, 0.18))]),
  bf1([g(0.26, 0.4, 0.25, 0.45, N(170, 195, 215, 0.1))]),
  bf2([g(0.28, 0.38, 0.78, 0.45, N(165, 190, 210, 0.07))]),
  bf2([g(0.24, 0.4, 0.35, 0.5, F(1, 0.16))]),
  bf3([g(0.22, 0.34, 0.15, 0.4, N(170, 190, 210, 0.07))]),
  bf3([g(0.3, 0.4, 0.5, 0.5, F(2, 0.24))]),
  fg5([g(0.22, 0.36, 0.68, 0.5, F(0, 0.12))]),
  fg5([g(0.24, 0.4, 0.3, 0.55, N(190, 212, 230, 0.103))]),
];

/* ---- timing ---- */

/** CSS ease-in-out, cubic-bezier(.42, 0, .58, 1). */
function easeInOut(x: number): number {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bx = (t: number) => 3 * 0.42 * t * (1 - t) ** 2 + 3 * 0.58 * t * t * (1 - t) + t ** 3;
  let lo = 0;
  let hi = 1;
  let t = x;
  for (let i = 0; i < 20; i++) {
    const v = bx(t);
    if (Math.abs(v - x) < 1e-5) break;
    if (v < x) lo = t;
    else hi = t;
    t = (lo + hi) / 2;
  }
  return 3 * t * t * (1 - t) + t ** 3;
}

/** Samples keyframes at time `t` (s), as a CSS animation with ease-in-out per keyframe segment. */
function sample<K extends number[]>(tm: Timing<K>, t: number): K {
  const elapsed = Math.max(0, t - (tm.delay ?? 0));
  const iter = Math.floor(elapsed / tm.dur);
  let p = elapsed / tm.dur - iter;
  if ((tm.dir === "alternate" && iter % 2 === 1) || (tm.dir === "alternate-reverse" && iter % 2 === 0)) p = 1 - p;
  const keys = tm.keys;
  let i = 0;
  while (i < keys.length - 2 && p > keys[i + 1][0]) i++;
  const a = keys[i];
  const b = keys[i + 1];
  const k = easeInOut((p - a[0]) / (b[0] - a[0]));
  return a.map((v, j) => v + (b[j] - v) * k) as K;
}

/* ---- drawing ---- */

const maskCache = new WeakMap<Layer, { key: string; canvas: HTMLCanvasElement }>();

const css = (c: RGB, a: number) => `rgba(${Math.round(c[0])},${Math.round(c[1])},${Math.round(c[2])},${a})`;

/**
 * Draws one plane. `ctx` is the plane's canvas, `scale` its pixels per CSS px, `fields` the
 * three field tones, `t` the time in seconds (null: static, as under reduced motion),
 * `scratch` a canvas of the same size for masked layers.
 */
export function drawPlane(
  ctx: CanvasRenderingContext2D,
  scratch: CanvasRenderingContext2D,
  layers: Layer[],
  view: View,
  scale: number,
  fields: readonly RGB[],
  t: number | null,
): void {
  const W = ctx.canvas.width;
  const H = ctx.canvas.height;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.clearRect(0, 0, W, H);
  const regions = { top: { w: view.w, h: view.top }, bot: { w: view.w, h: Math.max(0, view.h - view.top) } };

  for (const layer of layers) {
    if (t === null && layer.motionOnly) continue;
    const r = regions[layer.region];
    const oy = layer.region === "top" ? 0 : view.top;
    const [bx, by, bw, bh] = layer.box(view, r);
    if (bw <= 0 || bh <= 0) continue;
    let alpha = layer.opacity ?? 1;
    if (t !== null && layer.fade) alpha *= sample(layer.fade, t)[1];
    if (alpha <= 0.001) continue;

    // Masked layers are static: drawn once per colour and size, then reused.
    let cache: HTMLCanvasElement | undefined;
    if (layer.mask) {
      const key = `${W}x${H}:${view.top}:${fields.map((c) => c.map(Math.round).join()).join(";")}`;
      const hit = maskCache.get(layer);
      if (hit && hit.key === key) {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.globalAlpha = alpha;
        ctx.drawImage(hit.canvas, 0, 0);
        continue;
      }
      cache = hit?.canvas ?? document.createElement("canvas");
      cache.width = W;
      cache.height = H;
      maskCache.set(layer, { key, canvas: cache });
    }

    const target = layer.mask ? scratch : ctx;
    if (layer.mask) {
      scratch.setTransform(1, 0, 0, 1, 0, 0);
      scratch.globalCompositeOperation = "source-over";
      scratch.globalAlpha = 1;
      scratch.clearRect(0, 0, W, H);
    }
    // The element's transform, about its centre (transform-origin: 50% 50%).
    target.setTransform(scale, 0, 0, scale, 0, scale * oy);
    if (t !== null && layer.move) {
      const [, tx, ty, rot, sx, sy] = sample(layer.move, t);
      const cx = bx + bw / 2;
      const cy = by + bh / 2;
      target.translate(cx + (tx / 100) * view.vw, cy + (ty / 100) * view.vh);
      target.rotate((rot * Math.PI) / 180);
      target.scale(sx, sy);
      target.translate(-cx, -cy);
    }
    target.globalAlpha = layer.mask ? 1 : alpha;

    for (const gr of layer.grads ?? []) {
      const color = "f" in gr.ink ? fields[gr.ink.f] : gr.ink.rgb;
      const ex = bx + gr.cx * bw;
      const ey = by + gr.cy * bh;
      const rx = gr.rx * bw;
      const ry = gr.ry * bh;
      if (rx <= 0 || ry <= 0) continue;
      target.save();
      target.translate(ex, ey);
      target.scale(rx, ry);
      const grad = target.createRadialGradient(0, 0, 0, 0, 0, gr.stop);
      grad.addColorStop(0, css(color, gr.ink.a));
      grad.addColorStop(1, css(color, 0));
      target.fillStyle = grad;
      // The part of the box the ellipse covers, in the ellipse's unit space.
      const x0 = Math.max((bx - ex) / rx, -gr.stop);
      const x1 = Math.min((bx + bw - ex) / rx, gr.stop);
      const y0 = Math.max((by - ey) / ry, -gr.stop);
      const y1 = Math.min((by + bh - ey) / ry, gr.stop);
      if (x1 > x0 && y1 > y0) target.fillRect(x0, y0, x1 - x0, y1 - y0);
      target.restore();
    }

    if (layer.linear) {
      const stops = layer.linear(view, r);
      const end = Math.max(bh, ...stops.map((s) => s[0]));
      const grad = target.createLinearGradient(0, by, 0, by + end);
      let last = 0;
      for (const [pos, [cr, cg, cb, ca]] of stops) {
        last = Math.max(last, Math.min(1, Math.max(0, pos / end)));
        grad.addColorStop(last, `rgba(${cr},${cg},${cb},${ca})`);
      }
      target.fillStyle = grad;
      target.fillRect(bx, by, bw, bh);
    }

    if (layer.mask) {
      const stops = layer.mask(view, r);
      const end = Math.max(bh, ...stops.map((s) => s[0]));
      const grad = scratch.createLinearGradient(0, by, 0, by + end);
      let last = 0;
      for (const [pos, a] of stops) {
        last = Math.max(last, Math.min(1, Math.max(0, pos / end)));
        grad.addColorStop(last, `rgba(0,0,0,${a})`);
      }
      scratch.setTransform(scale, 0, 0, scale, 0, scale * oy);
      scratch.globalCompositeOperation = "destination-in";
      scratch.fillStyle = grad;
      scratch.fillRect(bx - view.w, by - view.h, bw + 2 * view.w, end + view.h);
      scratch.globalCompositeOperation = "source-over";
      cache?.getContext("2d")?.drawImage(scratch.canvas, 0, 0);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = alpha;
      ctx.drawImage(scratch.canvas, 0, 0);
    }
  }
  ctx.globalAlpha = 1;
}

/** The horizontal drift (px) of the first mist bank at time `t` (s); a test probe for smooth motion. */
export function driftX(view: View, t: number): number {
  const move = FRONT[0].move;
  return move ? (sample(move, t)[1] / 100) * view.vw : 0;
}
