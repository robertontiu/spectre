/* Static geometry for the apparition, computed once on the server. */

export type HarmonicLine = { d: string; opacity: string; width: string };
export type Mote = { cx: string; cy: string; r: string; opacity: string };

const smoothstep = (a: number, b: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

/* The bend of each harmonic across the body: lifts at the shoulders, dips at the hem,
   with a small tremor in the middle. */
const bend = (t: number) =>
  0.3 * smoothstep(0.06, 0.32, t) -
  0.24 * smoothstep(0.74, 0.98, t) +
  0.018 * Math.sin(t * 34) * smoothstep(0.36, 0.5, t) * (1 - smoothstep(0.66, 0.74, t));

/**
 * 22 harmonic lines stacked up the ghost's body like a spectrogram, with formant-like
 * bright regions, split into three groups that shimmer out of phase.
 */
export function harmonicGroups(): HarmonicLine[][] {
  const groups: HarmonicLine[][] = [[], [], []];
  for (let k = 1; k <= 22; k++) {
    let d = "";
    for (let i = 0; i <= 80; i++) {
      const t = i / 80;
      const x = 380 + t * 440;
      const y = 640 - k * 24 * (1 + bend(t));
      d += `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    const formant = 1 + 0.9 * Math.exp(-((k - 4) ** 2) / 3) + 0.6 * Math.exp(-((k - 11) ** 2) / 5);
    const a = Math.min(1, 0.9 * Math.exp(-k / 10) * formant);
    groups[k % 3].push({ d, opacity: a.toFixed(2), width: (2.8 - k * 0.08).toFixed(2) });
  }
  return groups;
}

/** Two fields of 30 dust motes from a seeded generator, so every render matches. */
export function moteFields(): [Mote[], Mote[]] {
  let s = 7;
  const r = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const field = () =>
    Array.from({ length: 30 }, () => ({
      cx: (r() * 1200).toFixed(0),
      cy: (r() * 700).toFixed(0),
      r: (r() * 1.6 + 0.4).toFixed(1),
      opacity: (r() * 0.3 + 0.05).toFixed(2),
    }));
  return [field(), field()];
}
