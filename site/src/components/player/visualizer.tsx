"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { mixWhite, paletteFrom, rgba, tone, type RGB } from "@/lib/color";
import { usePlayerStore } from "./player-context";

const LOW_HZ = 32;
const HIGH_HZ = 15000;
/** Backing-store pixels per CSS px at most (phones report 3). */
const MAX_DPR = 2;
/** Frame budget: the spectrum at up to 60 fps (30 on touch screens, to spare phones), the idle hump at 30. */
const IDLE_MS = 1000 / 30;

const NIGHT: RGB = [11, 13, 18];
/** The well's glow: color-mix(in srgb, c3 45%, #0b0d12). */
const glow = (c3: RGB): RGB => c3.map((v, i) => v * 0.45 + NIGHT[i] * 0.55) as RGB;
const glowCss = (c: RGB) => `radial-gradient(120% 90% at 50% 100%, ${rgba(c)}, rgb(${NIGHT.join(",")}) 70%)`;

/**
 * Log-spaced bars from the analyser (32 Hz-15 kHz), with a soft envelope, a reflection
 * and falling peak caps, in the track's colours, over a glow in the track's deep colour.
 * While paused it breathes as a slow idle hump (still under reduced motion).
 *
 * The frame loop never reads layout or writes styles: the canvas size comes from a
 * ResizeObserver, drawing pauses while the canvas is off screen, and gradients are reused
 * until the colours or the size change.
 */
export function Visualizer() {
  const store = usePlayerStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // The glow under the canvas for the first paint (the canvas paints over it from then on).
  const [wellStyle] = useState((): CSSProperties => ({
    background: glowCss(glow(tone(paletteFrom(store.tracks[store.initial]?.colors ?? [])[2]))),
  }));

  useEffect(() => {
    const canvas = canvasRef.current;
    const g = canvas?.getContext("2d");
    if (!canvas || !g) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    const playingMs = matchMedia("(pointer: coarse)").matches ? 1000 / 30 : 1000 / 60;
    const smooth = new Float32Array(128);
    const peaks = new Float32Array(128);
    let lastT = 0;
    let lastN = 0;
    let raf = 0;
    let W = 0;
    let H = 0;
    let r = 1;
    let onScreen = true;
    let cacheKey = "";
    let fills: { well: CanvasGradient; bars: CanvasGradient; refl: CanvasGradient; cap: string } | null = null;

    const resize = new ResizeObserver(([entry]) => {
      W = entry.contentRect.width;
      H = entry.contentRect.height;
      r = Math.min(MAX_DPR, devicePixelRatio || 1);
      canvas.width = Math.round(W * r);
      canvas.height = Math.round(H * r);
      cacheKey = "";
    });
    resize.observe(canvas);
    const visibility = new IntersectionObserver(([entry]) => {
      onScreen = entry.isIntersecting;
    });
    visibility.observe(canvas);

    const frame = (t: number) => {
      raf = requestAnimationFrame(frame);
      if (!W || !onScreen) return;
      const playing = store.getState().playing;
      if (t - lastT < (playing ? playingMs : IDLE_MS) - 2) return;
      const dt = Math.min(64, t - (lastT || t));
      lastT = t;
      g.setTransform(r, 0, 0, r, 0, 0);

      const n = W < 420 ? 32 : W < 640 ? 48 : 64;
      if (n !== lastN) {
        smooth.fill(0);
        peaks.fill(0);
        lastN = n;
      }
      const engine = store.engine;
      const bins = playing ? (engine?.frequencyData() ?? null) : null;
      const binHz = engine?.binHz ?? 44100 / 4096;
      const tt = reduced.matches ? 0 : t;

      for (let i = 0; i < n; i++) {
        let v: number;
        if (bins) {
          const fa = LOW_HZ * Math.pow(HIGH_HZ / LOW_HZ, i / n);
          const fb = LOW_HZ * Math.pow(HIGH_HZ / LOW_HZ, (i + 1) / n);
          const a = Math.floor(fa / binHz);
          const b = Math.max(a + 1, Math.ceil(fb / binHz));
          let m = 0;
          for (let k = a; k < b && k < bins.length; k++) if (bins[k] > m) m = bins[k];
          v = Math.min(1, Math.pow(m / 255, 1.45) * (0.92 + (0.3 * i) / n));
        } else {
          const hump = Math.pow(Math.sin((Math.PI * (i + 0.5)) / n), 1.6);
          v = 0.04 + 0.12 * hump * (0.55 + 0.45 * Math.sin(i * 0.42 - tt * 0.0014));
        }
        smooth[i] += (v - smooth[i]) * (v > smooth[i] ? 0.55 : 0.14);
        peaks[i] = Math.max(peaks[i] - (0.0045 * dt) / 16, smooth[i]);
      }

      const top = H * 0.08;
      const base = H * 0.8;
      const mh = base - top;
      const bw = W / n;
      const gap = Math.max(2, bw * 0.26);
      const w = bw - gap;
      const rad = Math.min(w / 2, 4);
      const [p1, p2, p3] = store.palette.current;
      const c1 = tone(p1);
      const c2 = tone(p2);
      const key = `${rgba(c1)}${rgba(c2)}${rgba(tone(p3))}${W}x${H}`;
      if (key !== cacheKey || !fills) {
        cacheKey = key;
        const well = g.createRadialGradient(0, 0, 0, 0, 0, 1);
        well.addColorStop(0, rgba(glow(tone(p3))));
        well.addColorStop(0.7, rgba(NIGHT));
        well.addColorStop(1, rgba(NIGHT));
        const bars = g.createLinearGradient(0, base, 0, top);
        bars.addColorStop(0, rgba(c1));
        bars.addColorStop(0.62, rgba(c2));
        bars.addColorStop(1, rgba(mixWhite(c2, 0.55)));
        const refl = g.createLinearGradient(0, base, 0, H);
        refl.addColorStop(0, rgba(c1, 0.32));
        refl.addColorStop(1, rgba(c1, 0));
        fills = { well, bars, refl, cap: rgba(mixWhite(c2, 0.6), 0.9) };
      }
      const grad = fills.bars;

      // The well's glow (an ellipse 120% x 90% of the box, centred on its bottom edge).
      g.save();
      g.translate(W / 2, H);
      g.scale(1.2 * W, 0.9 * H);
      g.fillStyle = fills.well;
      g.fillRect(-W / 2 / (1.2 * W), -1 / 0.9, 1 / 1.2, 1 / 0.9);
      g.restore();

      // Envelope behind the bars.
      g.globalAlpha = 0.2;
      g.fillStyle = grad;
      g.beginPath();
      g.moveTo(0, base);
      for (let i = 0; i < n; i++) g.lineTo(i * bw + bw / 2, base - smooth[i] * mh * 1.08 - 6);
      g.lineTo(W, base);
      g.closePath();
      g.fill();
      g.globalAlpha = 1;

      // Bars.
      for (let i = 0; i < n; i++) {
        const h = Math.max(3, smooth[i] * mh);
        const x = i * bw + gap / 2;
        g.beginPath();
        if (g.roundRect) g.roundRect(x, base - h, w, h, [rad, rad, 1, 1]);
        else g.rect(x, base - h, w, h);
        g.fill();
      }

      // Reflection.
      g.fillStyle = fills.refl;
      for (let i = 0; i < n; i++) g.fillRect(i * bw + gap / 2, base + 3, w, Math.max(2, smooth[i] * mh * 0.32));

      // Peak caps and the floor line.
      g.fillStyle = fills.cap;
      for (let i = 0; i < n; i++) if (peaks[i] > 0.03) g.fillRect(i * bw + gap / 2, base - peaks[i] * mh - 6, w, 2);
      g.fillStyle = "rgba(255,255,255,.12)";
      g.fillRect(0, base + 1, W, 1);
    };

    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      resize.disconnect();
      visibility.disconnect();
    };
  }, [store]);

  return (
    <div className="viz" style={wellStyle}>
      <canvas ref={canvasRef} aria-label="Spectrum visualizer" />
    </div>
  );
}
