import type { Palette } from "./color";

const clone = (p: Palette): Palette => p.map((c) => [...c]) as Palette;

/**
 * Glides the player's accent palette toward the current track's colours for the card's
 * canvases (the visualizer reads `current` in its frame loop; the equalizer curve
 * subscribes). It touches no DOM: the card's own accent colours are CSS custom properties
 * that the browser transitions (PlayerCard), and the page background glides in its own
 * canvas loop (AtmosphereField).
 */
export class PaletteAnimator {
  current: Palette;
  private target: Palette;
  private frame = 0;
  private last = 0;
  private listeners = new Set<() => void>();

  constructor(initial: Palette) {
    this.current = clone(initial);
    this.target = clone(initial);
  }

  /** Called on every animated step, so canvases can redraw. */
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  setTarget(target: Palette): void {
    this.target = clone(target);
    if (!this.frame && typeof window !== "undefined") {
      this.last = 0;
      this.frame = requestAnimationFrame(this.step);
    }
  }

  private step = (t: number) => {
    const dt = Math.min(64, t - (this.last || t));
    this.last = t;
    const k = 1 - Math.exp(-dt / 320);
    let delta = 0;
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const v = this.current[i][j] + (this.target[i][j] - this.current[i][j]) * k;
        delta = Math.max(delta, Math.abs(this.target[i][j] - v));
        this.current[i][j] = v;
      }
    }
    const done = delta < 0.6;
    if (done) this.current = clone(this.target);
    this.listeners.forEach((l) => l());
    this.frame = done ? 0 : requestAnimationFrame(this.step);
  };
}
