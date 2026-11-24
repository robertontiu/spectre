"use client";

import { cx } from "@/lib/cx";
import { useEffect, useRef, type CSSProperties, type KeyboardEvent, type PointerEvent } from "react";
import { mixWhite, rgba, tone, type RGB } from "@/lib/color";
import {
  EQ_FREQUENCIES,
  EQ_RANGE_DB,
  PRESET_CHOICES,
  bandLabel,
  type BandKey,
  type EqSettings,
  type PresetChoice,
} from "@/lib/equalizer";
import { usePlayer, usePlayerStore } from "./player-context";

const BANDS: { key: BandKey; label: string; name: string }[] = [
  { key: "pre", label: "Pre", name: "Preamp" },
  ...EQ_FREQUENCIES.map((f, i) => ({ key: i, label: bandLabel(f), name: `${bandLabel(f)}Hz` })),
];
const GREY: RGB = [140, 150, 156];
/** Slider tracks are inset 5px top and bottom. */
const INSET = 5;

const signed = (v: number) => `${v > 0 ? "+" : ""}${v}`;

/** Preamp plus ten bands, an on/off switch, presets, and the response curve drawn over the sliders. */
export function Equalizer() {
  const store = usePlayerStore();
  const eqOn = usePlayer((s) => s.eqOn);
  const preset = usePlayer((s) => s.preset);
  const eq = usePlayer((s) => s.eq);

  return (
    <div className="mt-[22px] border-t border-white/8 pt-[18px]">
      <div className="mb-3 flex flex-wrap items-center gap-2.5">
        <h3 className="m-0 mr-auto font-display text-[18px] leading-[1.2] font-semibold">Equalizer</h3>
        <button type="button" className="sw" aria-pressed={eqOn} onClick={store.toggleEq}>
          <i />
          <span>{eqOn ? "On" : "Off"}</span>
        </button>
        <select
          className="select"
          aria-label="Equalizer preset"
          value={preset}
          onChange={(e) => store.setPreset(e.target.value as PresetChoice)}
        >
          {PRESET_CHOICES.map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
      </div>
      <Bands eq={eq} on={eqOn} />
    </div>
  );
}

function Bands({ eq, on }: { eq: EqSettings; on: boolean }) {
  const store = usePlayerStore();
  const bandsRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Redraw the curve when the settings change, the layout resizes or the palette glides.
  useEffect(() => {
    const bands = bandsRef.current;
    const canvas = canvasRef.current;
    if (!bands || !canvas) return;
    const draw = () => drawCurve(bands, canvas, eq.gains, on ? store.palette.current : null);
    draw();
    const resize = new ResizeObserver(draw);
    resize.observe(bands);
    const unsubscribe = store.palette.subscribe(draw);
    return () => {
      resize.disconnect();
      unsubscribe();
    };
  }, [store, eq, on]);

  return (
    <div ref={bandsRef} className={cx("bands", !on && "off")}>
      <canvas ref={canvasRef} />
      {BANDS.map((b) => (
        <div key={b.key} className={cx("bd", b.key === "pre" && "pre")}>
          <output>{signed(b.key === "pre" ? eq.pre : eq.gains[b.key])}</output>
          <BandSlider band={b.key} name={b.name} value={b.key === "pre" ? eq.pre : eq.gains[b.key]} />
          <span>{b.label}</span>
        </div>
      ))}
    </div>
  );
}

const KEY_STEPS: Record<string, (v: number) => number> = {
  ArrowUp: (v) => v + 1,
  ArrowRight: (v) => v + 1,
  ArrowDown: (v) => v - 1,
  ArrowLeft: (v) => v - 1,
  PageUp: (v) => v + 3,
  PageDown: (v) => v - 3,
  Home: () => -EQ_RANGE_DB,
  End: () => EQ_RANGE_DB,
};

/** A vertical -12..+12 dB slider: drag, arrow keys, Page Up/Down, Home/End; double-click resets. */
function BandSlider({ band, name, value }: { band: BandKey; name: string; value: number }) {
  const store = usePlayerStore();
  const u = (value + EQ_RANGE_DB) / (2 * EQ_RANGE_DB);
  const style = {
    "--u": u,
    "--fill-top": Math.min(0, 0.5 - u),
    "--fill-height": Math.abs(0.5 - u),
  } as CSSProperties;

  const fromPointer = (e: PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    store.setBand(band, ((r.bottom - INSET - e.clientY) / (r.height - 2 * INSET)) * 2 * EQ_RANGE_DB - EQ_RANGE_DB);
  };

  return (
    <div
      className="sl"
      role="slider"
      tabIndex={0}
      aria-label={name}
      aria-valuemin={-12}
      aria-valuemax={12}
      aria-valuenow={value}
      aria-valuetext={`${signed(value)} dB`}
      style={style}
      onPointerDown={(e) => {
        e.preventDefault();
        e.currentTarget.focus();
        e.currentTarget.setPointerCapture(e.pointerId);
        fromPointer(e);
      }}
      onPointerMove={(e) => {
        if (e.currentTarget.hasPointerCapture(e.pointerId)) fromPointer(e);
      }}
      onDoubleClick={() => store.setBand(band, 0)}
      onKeyDown={(e: KeyboardEvent<HTMLDivElement>) => {
        const next = KEY_STEPS[e.key];
        if (!next) return;
        e.preventDefault();
        store.setBand(band, next(value));
      }}
    >
      <i className="f" />
      <b className="k" />
    </div>
  );
}

/** Draws a smooth response curve through the band knobs, filled toward the 0 dB line. */
function drawCurve(bands: HTMLElement, canvas: HTMLCanvasElement, gains: number[], palette: RGB[] | null) {
  const W = bands.clientWidth;
  const H = bands.clientHeight;
  const r = devicePixelRatio || 1;
  const g = canvas.getContext("2d");
  if (!W || !g) return;
  if (canvas.width !== Math.round(W * r) || canvas.height !== Math.round(H * r)) {
    canvas.width = Math.round(W * r);
    canvas.height = Math.round(H * r);
  }
  g.setTransform(r, 0, 0, r, 0, 0);
  g.clearRect(0, 0, W, H);

  const box = bands.getBoundingClientRect();
  const sliders = [...bands.querySelectorAll<HTMLElement>(".sl")].slice(1);
  if (sliders.length !== gains.length) return;
  const points = sliders.map((el, i) => {
    const s = el.getBoundingClientRect();
    const u = (gains[i] + EQ_RANGE_DB) / (2 * EQ_RANGE_DB);
    return [s.left + s.width / 2 - box.left, s.top - box.top + INSET + (1 - u) * (s.height - 2 * INSET)] as const;
  });
  const first = sliders[0].getBoundingClientRect();
  const mid = first.top - box.top + first.height / 2;

  const trace = () => {
    for (let i = 1; i < points.length; i++) {
      const [ax, ay] = points[i - 1];
      const [bx, by] = points[i];
      const mx = (ax + bx) / 2;
      g.bezierCurveTo(mx, ay, mx, by, bx, by);
    }
  };
  const c1 = palette ? tone(palette[0]) : GREY;
  const c2 = palette ? tone(palette[1]) : GREY;

  g.beginPath();
  g.moveTo(points[0][0], mid);
  g.lineTo(points[0][0], points[0][1]);
  trace();
  g.lineTo(points[points.length - 1][0], mid);
  g.closePath();
  g.fillStyle = rgba(c1, 0.16);
  g.fill();

  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  trace();
  g.strokeStyle = rgba(mixWhite(c2, 0.2), 0.55);
  g.lineWidth = 1.5;
  g.stroke();
}
