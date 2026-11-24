/** An sRGB colour as [r, g, b], channels 0-255 (may be fractional while animating). */
export type RGB = [number, number, number];
/** The three colours of a track: accent, support, deep. */
export type Palette = [RGB, RGB, RGB];

export function hexToRgb(hex: string): RGB {
  let h = String(hex || "#888").replace("#", "");
  if (h.length === 3) h = h.replace(/./g, "$&$&");
  const n = parseInt(h, 16) || 0;
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/** Builds a full three-colour palette from a track's 2-3 colours. */
export function paletteFrom(colors: readonly string[]): Palette {
  const c = colors.map(hexToRgb);
  if (c.length < 2) c.push([200, 210, 220]);
  if (c.length < 3) c.push(c[0].map((v) => Math.round(v * 0.3)) as RGB);
  return [c[0], c[1], c[2]];
}

export const rgba = (c: RGB, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const rgbCss = (c: RGB) => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;

/** Mixes toward white by k (0-1). */
export const mixWhite = (c: RGB, k: number): RGB => c.map((v) => v + (255 - v) * k) as RGB;

/* The track colours are muted into the night: accents a notch down,
   fields much further (toward the cold base). */
const BASE: RGB = [8, 12, 22];
const desaturate = (c: RGB, f: number): RGB => {
  const g = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2];
  return c.map((v) => v + (g - v) * f) as RGB;
};
const toward = (c: RGB, t: RGB, k: number): RGB => c.map((v, i) => v + (t[i] - v) * k) as RGB;

/** Accent tone, used by the controls and the visualizer. */
export const tone = (c: RGB): RGB => toward(desaturate(c, 0.3), BASE, 0.16);
/** Field tone, used by the background stack. */
export const fieldTone = (c: RGB): RGB => toward(desaturate(c, 0.26), BASE, 0.25);

/** The accent CSS custom properties (--c1..3) for a palette, used by the player card. */
export function paletteVars(p: Palette): Record<string, string> {
  const vars: Record<string, string> = {};
  p.forEach((c, i) => {
    vars[`--c${i + 1}`] = rgbCss(tone(c));
  });
  return vars;
}

/** The field CSS custom properties (--f1..3), used only by the background's first paint. */
export function fieldVars(p: Palette): Record<string, string> {
  const vars: Record<string, string> = {};
  p.forEach((c, i) => {
    vars[`--f${i + 1}`] = rgbCss(fieldTone(c));
  });
  return vars;
}

/* OKLab, for perceptually even colour glides (no dark or grey midpoint). */
export type Lab = [number, number, number];
const toLinear = (v: number) => {
  const c = v / 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
};
const fromLinear = (v: number) => {
  const c = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(Math.max(0, v), 1 / 2.4) - 0.055;
  return Math.min(255, Math.max(0, c * 255));
};

export function rgbToOklab(c: RGB): Lab {
  const [r, g, b] = c.map(toLinear);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [
    0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
  ];
}

export function oklabToRgb([L, a, b]: Lab): RGB {
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [
    fromLinear(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    fromLinear(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    fromLinear(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
  ];
}
