/** Centre frequencies of the ten bands (Hz); the first is a low shelf, the last a high shelf. */
export const EQ_FREQUENCIES = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000] as const;
export const EQ_RANGE_DB = 12;

export type EqSettings = {
  /** Preamp gain in dB. */
  pre: number;
  /** Band gains in dB, one per entry of EQ_FREQUENCIES. */
  gains: number[];
};

export const EQ_PRESETS = {
  Spectre: { pre: -3, gains: [3, 2, -1, -2, -1, 1, 2, 2, 1, 0] },
  Flat: { pre: 0, gains: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] },
  "Laptop speakers": { pre: -2, gains: [-6, 3, 3, 1, 0, 1, 1, 0, -1, -2] },
  Headphones: { pre: -3, gains: [2, 1, 0, -1, 0, 1, 2, 3, 2, 1] },
  "Late night": { pre: 0, gains: [1, 1, 0, 0, -1, -2, -3, -4, -5, -6] },
} as const satisfies Record<string, { pre: number; gains: readonly number[] }>;

export type PresetName = keyof typeof EQ_PRESETS;
export type PresetChoice = PresetName | "Custom";

export const DEFAULT_PRESET: PresetName = "Spectre";
export const PRESET_CHOICES = [...(Object.keys(EQ_PRESETS) as PresetName[]), "Custom"] as const;

export const isPresetName = (v: unknown): v is PresetName => typeof v === "string" && Object.hasOwn(EQ_PRESETS, v);

export function presetSettings(name: PresetName): EqSettings {
  const p = EQ_PRESETS[name];
  return { pre: p.pre, gains: [...p.gains] };
}

/** "pre" for the preamp, or a band index. */
export type BandKey = "pre" | number;

export const clampDb = (v: number) => Math.max(-EQ_RANGE_DB, Math.min(EQ_RANGE_DB, Math.round(v)));

export const bandLabel = (f: number) => (f >= 1000 ? `${f / 1000}k` : String(f));
