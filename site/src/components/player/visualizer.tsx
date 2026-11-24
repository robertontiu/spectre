"use client";

import { useEffect, useRef } from "react";
import { mixWhite, rgba, tone } from "@/lib/color";
import { usePlayerStore } from "./player-context";

const LOW_HZ = 32;
const HIGH_HZ = 15000;

/**
 * Log-spaced bars from the analyser (32 Hz-15 kHz), with a soft envelope, a reflection
 * and falling peak caps, in the track's colours. While paused it breathes as a slow
 * idle hump (still under reduced motion).
 */
export function Visualizer() {
  const store = usePlayerStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const g = canvas?.getContext("2d");
    if (!canvas || !g) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    const smooth = new Float32Array(128);
    const peaks = new Float32Array(128);
    let lastT = 0;
    let lastN = 0;
    let raf = 0;

    const frame = (t: number) => {
      raf = requestAnimationFrame(frame);
      const dt = Math.min(64, t - (lastT || t));
      lastT = t;

      const W = canvas.clientWidth;
      const H = canvas.clientHeight;
      const r = devicePixelRatio || 1;
      if (!W) return;
      if (canvas.width !== Math.round(W * r) || canvas.height !== Math.round(H * r)) {
        canvas.width = Math.round(W * r);
        canvas.height = Math.round(H * r);
      }
      g.setTransform(r, 0, 0, r, 0, 0);
      g.clearRect(0, 0, W, H);

      const n = W < 420 ? 32 : W < 640 ? 48 : 64;
      if (n !== lastN) {
        smooth.fill(0);
        peaks.fill(0);
        lastN = n;
      }
      const engine = store.engine;
      const bins = store.getState().playing ? (engine?.frequencyData() ?? null) : null;
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
      const [p1, p2] = store.palette.current;
      const c1 = tone(p1);
      const c2 = tone(p2);

      const grad = g.createLinearGradient(0, base, 0, top);
      grad.addColorStop(0, rgba(c1));
      grad.addColorStop(0.62, rgba(c2));
      grad.addColorStop(1, rgba(mixWhite(c2, 0.55)));

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
      const refl = g.createLinearGradient(0, base, 0, H);
      refl.addColorStop(0, rgba(c1, 0.32));
      refl.addColorStop(1, rgba(c1, 0));
      g.fillStyle = refl;
      for (let i = 0; i < n; i++) g.fillRect(i * bw + gap / 2, base + 3, w, Math.max(2, smooth[i] * mh * 0.32));

      // Peak caps and the floor line.
      g.fillStyle = rgba(mixWhite(c2, 0.6), 0.9);
      for (let i = 0; i < n; i++) if (peaks[i] > 0.03) g.fillRect(i * bw + gap / 2, base - peaks[i] * mh - 6, w, 2);
      g.fillStyle = "rgba(255,255,255,.12)";
      g.fillRect(0, base + 1, W, 1);
    };

    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [store]);

  return (
    <div className="viz">
      <canvas ref={canvasRef} aria-label="Spectrum visualizer" />
    </div>
  );
}
