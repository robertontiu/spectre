"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { fieldTone, fieldVars, oklabToRgb, paletteFrom, rgbToOklab, type Lab, type RGB } from "@/lib/color";
import { usePlayerStore } from "../player/player-context";
import { FADE_MS } from "../player/player-store";
import { BACK, FRONT, drawPlane, driftX, type View } from "./field-scene";

/** Frames per second of the drift (the motion is time-based, so it stays smooth). */
const FPS = 30;
/** Pixels in each low-resolution plane (about 200 x 125 on a laptop); the GPU scales it up. */
const PLANE_AREA = 25000;
/** A colour change under reduced motion: short, but not a cut. */
const REDUCED_FADE_MS = 500;

const ease = (x: number) => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2);
const fieldLab = (colors: readonly string[]): Lab[] => paletteFrom(colors).map((c) => rgbToOklab(fieldTone(c)));

/**
 * The soft half of the background: the mist and fog banks and the playing track's colour
 * field, drawn into two small canvases (under and over the apparition) that the GPU scales
 * up to the viewport. One rAF loop draws both at 30 fps, with time-based drift, and glides
 * the colours in OKLab when the track changes. Nothing in the DOM changes on a track change
 * or a tab switch, and the browser keeps two small textures instead of dozens of huge
 * animated layers (the cause of the flicker on track changes, refocus and on phones).
 *
 * Until the first frame is drawn (server render, hydration), CSS layers in the opening
 * track's colours stand in, frozen at the start of their drift; they are then removed.
 */
export function AtmosphereField() {
  const store = usePlayerStore();
  const backRef = useRef<HTMLCanvasElement>(null);
  const frontRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  const [initialVars] = useState(
    () => fieldVars(paletteFrom(store.tracks[store.initial]?.colors ?? [])) as CSSProperties,
  );

  useEffect(() => {
    const back = backRef.current;
    const front = frontRef.current;
    const atmos = back?.closest<HTMLElement>(".atmos");
    const banner = atmos?.querySelector<HTMLElement>(".atop");
    const bctx = back?.getContext("2d");
    const fctx = front?.getContext("2d");
    const scratch = document.createElement("canvas").getContext("2d");
    if (!back || !front || !atmos || !banner || !bctx || !fctx || !scratch) return;

    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    let view: View | null = null;
    let scale = 1;
    let raf = 0;
    let lastDraw = -Infinity;
    let stableW = 0;
    let stableH = 0;

    // Colours: a glide from `from` to `to` (OKLab) starting at `fadeStart`.
    let current = store.getState().current;
    let to = fieldLab(store.tracks[current]?.colors ?? []);
    let from = to;
    let fadeStart = -Infinity;
    let fadeMs = FADE_MS;
    const labAt = (now: number): Lab[] => {
      const k = ease(Math.min(1, Math.max(0, (now - fadeStart) / fadeMs)));
      return to.map((c, i) => c.map((v, j) => from[i][j] + (v - from[i][j]) * k) as Lab);
    };
    const fading = (now: number) => now - fadeStart < fadeMs;

    /**
     * Measures the viewport. Its height only follows real changes (a new width, or more than
     * a phone's address bar), so the background never resizes while a phone scrolls.
     */
    const measure = () => {
      const w = document.documentElement.clientWidth;
      // The first time, the CSS height (100lvh: the viewport with the address bar hidden).
      const h = Math.round(
        Math.max(window.innerHeight, document.documentElement.clientHeight, stableH ? 0 : atmos.offsetHeight),
      );
      if (w !== stableW || h > stableH || stableH - h > 160) {
        stableW = w;
        stableH = h;
        atmos.style.height = `${h}px`;
      }
      const top = banner.offsetHeight;
      view = {
        w: stableW,
        h: stableH,
        top,
        vw: stableW,
        vh: stableH,
        vmin: Math.min(stableW, stableH),
        vmax: Math.max(stableW, stableH),
      };
      scale = Math.sqrt(PLANE_AREA / (stableW * stableH));
      const pw = Math.max(1, Math.round(stableW * scale));
      const ph = Math.max(1, Math.round(stableH * scale));
      for (const c of [back, front, scratch.canvas]) {
        if (c.width !== pw || c.height !== ph) {
          c.width = pw;
          c.height = ph;
        }
      }
    };

    let draw = (now: number) => {
      if (!view) measure();
      if (!view) return;
      lastDraw = now;
      const fields = labAt(now).map(oklabToRgb) as RGB[];
      const t = reduced.matches ? null : now / 1000;
      drawPlane(bctx, scratch, BACK, view, scale, fields, t);
      drawPlane(fctx, scratch, FRONT, view, scale, fields, t);
    };

    const loop = (now: number) => {
      raf = 0;
      if (document.hidden) return;
      if (now - lastDraw >= 1000 / FPS - 4) draw(now);
      if (!reduced.matches || fading(now)) raf = requestAnimationFrame(loop);
    };
    const start = () => {
      if (!raf && !document.hidden) raf = requestAnimationFrame(loop);
    };

    // The first frame, synchronously, before the stand-in layers go.
    measure();
    draw(performance.now());
    setReady(true);
    start();

    const onStore = () => {
      const next = store.getState().current;
      if (next === current) return;
      current = next;
      const now = performance.now();
      from = labAt(now);
      to = fieldLab(store.tracks[next]?.colors ?? []);
      fadeStart = now;
      fadeMs = reduced.matches ? REDUCED_FADE_MS : FADE_MS;
      start();
    };
    // Back from a hidden tab: draw the current state at once (the glide keeps its clock).
    const onVisibility = () => {
      if (document.hidden) return;
      draw(performance.now());
      start();
    };
    const onResize = () => {
      measure();
      draw(performance.now());
      start();
    };
    const resize = new ResizeObserver(onResize);
    resize.observe(banner);
    window.addEventListener("resize", onResize);
    const unsubscribe = store.subscribe(onStore);
    document.addEventListener("visibilitychange", onVisibility);
    reduced.addEventListener("change", onResize);

    if (new URLSearchParams(location.search).has("field-probe")) {
      // Test hook (?field-probe): the drift of the first mist bank as last drawn, and the colours.
      let drawnAt = 0;
      const cost = { frames: 0, ms: 0 };
      const drawn = draw;
      draw = (now: number) => {
        drawnAt = now;
        const t0 = performance.now();
        drawn(now);
        cost.frames++;
        cost.ms += performance.now() - t0;
      };
      (window as unknown as { __spectreField?: unknown }).__spectreField = {
        cost,
        probe: () => (view ? driftX(view, drawnAt / 1000) : 0),
        fields: () => labAt(performance.now()).map(oklabToRgb),
      };
    }

    return () => {
      cancelAnimationFrame(raf);
      resize.disconnect();
      window.removeEventListener("resize", onResize);
      unsubscribe();
      document.removeEventListener("visibilitychange", onVisibility);
      reduced.removeEventListener("change", onResize);
    };
  }, [store]);

  return (
    <>
      <div className="plane plane-back" aria-hidden="true">
        {!ready && (
          <div className="stand-in" style={initialVars}>
            <div className="atop">
              <Layers names={["tint t1", "tint t2", "tint t3", "fg fg6", "fg fg1 fg1-c", "fg fg1 fg1-n"]} />
              <Layers names={["fg fg2 fg2-n", "fg fg2 fg2-c"]} />
            </div>
          </div>
        )}
        <canvas ref={backRef} className="field" width={1} height={1} />
      </div>
      <div className="plane plane-front" aria-hidden="true">
        {!ready && (
          <div className="stand-in" style={initialVars}>
            <div className="atop">
              <Layers names={["mist m1", "mist m2", "mist m3", "fg fg3 fg3-c", "fg fg3 fg3-n", "fg fg4 fg4-c"]} />
              <Layers names={["fg fg4 fg4-n", "wisp", "wisp w2", "wisp w3", "rise"]} />
            </div>
            <div className="abot">
              <div className="blobs">
                <Layers names={["blob b1", "blob b2", "blob b3"]} />
              </div>
              <Layers names={["sink", "bf bf1 bf1-c", "bf bf1 bf1-n", "bf bf2 bf2-n", "bf bf2 bf2-c"]} />
              <Layers names={["bf bf3 bf3-n", "bf bf3 bf3-c"]} />
            </div>
            <div className="atop">
              <Layers names={["fg fg5 fg5-c", "fg fg5 fg5-n"]} />
            </div>
          </div>
        )}
        <canvas ref={frontRef} className="field" width={1} height={1} />
      </div>
    </>
  );
}

const Layers = ({ names }: { names: string[] }) => names.map((n) => <div key={n} className={n} />);
