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

/** The CSS custom properties (--c1..3 accents, --f1..3 fields) for a palette. */
export function paletteVars(p: Palette): Record<string, string> {
  const vars: Record<string, string> = {};
  p.forEach((c, i) => {
    vars[`--c${i + 1}`] = rgbCss(tone(c));
    vars[`--f${i + 1}`] = rgbCss(fieldTone(c));
  });
  return vars;
}
