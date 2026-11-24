"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { fieldTone, fieldVars, oklabToRgb, paletteFrom, rgbToOklab, type Lab } from "@/lib/color";
import { usePlayerStore } from "../player/player-context";
import { FADE_MS } from "../player/player-store";
import {
  FieldRenderer,
  MAX_SCALE,
  epoch,
  labAt,
  type FieldColors,
  type FieldMessage,
  type FieldReport,
} from "./field-renderer";
import type { View } from "./field-scene";

/** A colour change under reduced motion: short, but not a cut. */
const REDUCED_FADE_MS = 500;

const fieldLab = (colors: readonly string[]): Lab[] => paletteFrom(colors).map((c) => rgbToOklab(fieldTone(c)));

/** A running renderer for a pair of canvases: in a worker, or on the page. */
type Connection = {
  send: (m: FieldMessage) => void;
  /** Called once messages can be sent (at once if they already can). */
  onReady: (c: Connection) => void;
  ready: boolean;
  onReport: (r: FieldReport) => void;
  dispose: () => void;
};
/**
 * Connections outlive a component's effect by a tick, so a remount of the same canvases
 * (React's development double effects) reuses one instead of transferring them twice.
 */
const connections = new WeakMap<
  HTMLCanvasElement,
  { connection: Connection; disposal?: ReturnType<typeof setTimeout> }
>();

/**
 * Starts the renderer for two canvases: in a worker on OffscreenCanvases where the browser
 * can (the page's main thread then does none of the drawing), otherwise on the page.
 */
function connect(back: HTMLCanvasElement, front: HTMLCanvasElement, probe: boolean): Connection {
  const connection: Connection = {
    send: () => {},
    onReady: () => {},
    ready: false,
    onReport: () => {},
    dispose: () => {},
  };
  const ready = () => {
    connection.ready = true;
    connection.onReady(connection);
  };
  const report = (r: FieldReport) => connection.onReport(r);
  const onPage = () => {
    const renderer = new FieldRenderer(back, front, performance.timeOrigin, !probe, report, probe);
    connection.send = (m) => renderer.handle(m);
    ready();
  };
  if (
    typeof Worker === "undefined" ||
    !("transferControlToOffscreen" in back) ||
    typeof OffscreenCanvas === "undefined"
  ) {
    onPage();
    return connection;
  }
  let worker: Worker | null = null;
  let transferred = false;
  const giveUp = () => {
    worker?.terminate();
    worker = null;
    if (!transferred) onPage();
  };
  const timeout = setTimeout(giveUp, 3000);
  try {
    worker = new Worker(new URL("./field-worker.ts", import.meta.url), { type: "module" });
  } catch {
    clearTimeout(timeout);
    onPage();
    return connection;
  }
  worker.onerror = () => {
    clearTimeout(timeout);
    giveUp();
  };
  worker.onmessage = (e: MessageEvent<FieldReport>) => {
    if (e.data.type !== "hello") return report(e.data);
    clearTimeout(timeout);
    if (!worker || transferred) return;
    const b = back.transferControlToOffscreen();
    const f = front.transferControlToOffscreen();
    transferred = true;
    const init: FieldMessage = {
      type: "init",
      back: b,
      front: f,
      origin: performance.timeOrigin,
      adaptive: !probe,
      probe,
    };
    worker.postMessage(init, [b, f]);
    const w = worker;
    connection.send = (m) => w.postMessage(m);
    ready();
  };
  connection.dispose = () => {
    clearTimeout(timeout);
    worker?.terminate();
  };
  return connection;
}

/**
 * The soft half of the background: the mist and fog banks and the playing track's colour
 * field, composited into two canvases (under and over the apparition). Each layer is
 * pre-rendered once, as its CSS gradient was, and every frame the layers are drawn with
 * their keyframed drift and opacity, as the browser composited the CSS layers. One loop
 * (FieldRenderer, in a worker where the browser can draw there) draws both planes at
 * 30 fps, with time-based drift, and glides the colours in OKLab when the track changes. Nothing in the DOM changes on a track change or a tab switch, and the
 * browser keeps two textures instead of dozens of huge animated layers (the cause of the
 * flicker on track changes, refocus and on phones).
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
    if (!back || !front || !atmos || !banner) return;

    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    const params = new URLSearchParams(location.search);
    // Test hooks (?field-probe): freeze the drift, read costs; ?field-scale=: another resolution.
    const probe = params.has("field-probe");
    const maxScale = (probe && Number(params.get("field-scale"))) || MAX_SCALE;
    let stableW = 0;
    let stableH = 0;
    let send: (m: FieldMessage) => void = () => {};

    // Colours: a glide in OKLab, restarted from wherever it is on each track change.
    let current = store.getState().current;
    const opening = fieldLab(store.tracks[current]?.colors ?? []);
    let colors: FieldColors = { from: opening, to: opening, start: 0, ms: FADE_MS };

    /**
     * Measures the viewport. Its height only follows real changes (a new width, or more than
     * a phone's address bar), so the background never resizes while a phone scrolls.
     */
    const viewMessage = (): FieldMessage => {
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
      const view: View = {
        w: stableW,
        h: stableH,
        top: banner.offsetHeight,
        vw: stableW,
        vh: stableH,
        vmin: Math.min(stableW, stableH),
        vmax: Math.max(stableW, stableH),
      };
      return { type: "view", view, maxScale };
    };
    const stateMessage = (): FieldMessage => ({ type: "state", hidden: document.hidden, reduced: reduced.matches });

    const probeState = { cost: { frames: 0, ms: 0 }, drift: 0 };
    const onReport = (r: FieldReport) => {
      if (r.type === "drawn") setReady(true);
      if (r.type === "cost") {
        probeState.cost.frames = r.frames;
        probeState.cost.ms = r.ms;
        probeState.drift = r.drift;
      }
    };
    const start = (c: Connection) => {
      c.onReport = onReport;
      send = c.send;
      send(viewMessage());
      send({ type: "colors", colors });
      send(stateMessage());
    };
    const held = connections.get(back);
    if (held) clearTimeout(held.disposal);
    const connection = held?.connection ?? connect(back, front, probe);
    if (!held) connections.set(back, { connection });
    connection.onReady = start;
    if (connection.ready) start(connection);

    const onStore = () => {
      const next = store.getState().current;
      if (next === current) return;
      current = next;
      const now = epoch();
      colors = {
        from: labAt(colors, now),
        to: fieldLab(store.tracks[next]?.colors ?? []),
        start: now,
        ms: reduced.matches ? REDUCED_FADE_MS : FADE_MS,
      };
      send({ type: "colors", colors });
    };
    const onState = () => send(stateMessage());
    // Only tell the renderer about real changes; a re-layout that leaves the view as it was
    // (e.g. the logotype's glitch) must not trigger a redraw of the sprites.
    let lastView = "";
    const onResize = () => {
      const msg = viewMessage();
      const key = JSON.stringify(msg.type === "view" ? msg.view : msg);
      if (key === lastView) return;
      lastView = key;
      send(msg);
    };
    const resize = new ResizeObserver(onResize);
    resize.observe(banner);
    window.addEventListener("resize", onResize);
    const unsubscribe = store.subscribe(onStore);
    document.addEventListener("visibilitychange", onState);
    reduced.addEventListener("change", onState);

    if (probe) {
      (window as unknown as { __spectreField?: unknown }).__spectreField = {
        cost: probeState.cost,
        /** Freezes the drift at `ms` (as a CSS animation's currentTime), or resumes with null. */
        freeze: (ms: number | null) => send({ type: "freeze", ms }),
        probe: () => probeState.drift,
        fields: () => labAt(colors, epoch()).map(oklabToRgb),
      };
    }

    return () => {
      resize.disconnect();
      window.removeEventListener("resize", onResize);
      unsubscribe();
      document.removeEventListener("visibilitychange", onState);
      reduced.removeEventListener("change", onState);
      connection.onReport = () => {};
      connection.onReady = () => {};
      const entry = connections.get(back);
      if (entry)
        entry.disposal = setTimeout(() => {
          connections.delete(back);
          connection.dispose();
        });
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
