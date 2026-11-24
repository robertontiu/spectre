"use client";

import { cx } from "@/lib/cx";
import { useEffect, useRef, type ComponentProps, type CSSProperties, type Ref } from "react";

type RangeInputProps = Omit<ComponentProps<"input">, "type" | "style" | "ref"> & {
  /** Filled part of the track, 0-1 (drawn by WebKit; Firefox uses ::-moz-range-progress). */
  progress: number;
  ref?: Ref<HTMLInputElement>;
};

/** Thumb width in px (player.css): the value runs between the thumb's centres at both ends. */
const THUMB = 14;
/** Finger travel (px) before a gesture counts as a drag, and how horizontal it must be. */
const SLOP = 8;
const HORIZONTAL = 1.5;

const setNativeValue = Object.getOwnPropertyDescriptor(
  typeof HTMLInputElement === "undefined" ? Object.prototype : HTMLInputElement.prototype,
  "value",
)?.set;

/**
 * A slim horizontal range slider whose filled part takes the track's accent colour.
 *
 * It stays a native <input type="range"> for the keyboard and assistive tech, but pointers
 * go to a wrapper: a mouse or pen drags from anywhere at once (as the native control), while
 * a finger only drags once the gesture is clearly horizontal, so vertical swipes scroll the
 * page and leave the value alone. A tap without movement still sets the value. Changes reach
 * React as ordinary input and change events.
 */
export function RangeInput({ progress, className, ref, ...props }: RangeInputProps) {
  const wrapRef = useRef<HTMLSpanElement>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const style = { "--p": `${(progress * 100).toFixed(2)}%` } as CSSProperties;

  useEffect(() => {
    const wrap = wrapRef.current;
    const input = inputRef.current;
    if (!wrap || !input) return;
    let gesture: { id: number; x: number; y: number; touch: boolean; dragging: boolean } | null = null;

    const valueAt = (clientX: number) => {
      const r = input.getBoundingClientRect();
      const min = Number(input.min || 0);
      const max = Number(input.max || 100);
      const step = Number(input.step || 1);
      const f = Math.min(1, Math.max(0, (clientX - r.left - THUMB / 2) / Math.max(1, r.width - THUMB)));
      const v = min + Math.round((f * (max - min)) / step) * step;
      return Math.min(max, Math.max(min, Number(v.toFixed(6))));
    };
    const set = (clientX: number) => {
      const v = String(valueAt(clientX));
      if (input.value === v) return;
      setNativeValue?.call(input, v);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    };
    const commit = () => input.dispatchEvent(new Event("change", { bubbles: true }));

    const onDown = (e: PointerEvent) => {
      if (input.disabled || (e.pointerType === "mouse" && e.button !== 0)) return;
      const touch = e.pointerType === "touch";
      gesture = { id: e.pointerId, x: e.clientX, y: e.clientY, touch, dragging: !touch };
      if (!touch) {
        e.preventDefault();
        input.focus({ preventScroll: true });
        wrap.setPointerCapture(e.pointerId);
        set(e.clientX);
      }
    };
    const onMove = (e: PointerEvent) => {
      if (!gesture || e.pointerId !== gesture.id) return;
      if (!gesture.dragging) {
        const dx = Math.abs(e.clientX - gesture.x);
        const dy = Math.abs(e.clientY - gesture.y);
        if (dx > SLOP && dx > HORIZONTAL * dy) {
          gesture.dragging = true;
          wrap.setPointerCapture(e.pointerId);
        } else if (dx > SLOP || dy > SLOP) {
          gesture = null; // a scroll (or a diagonal): leave it to the browser
          return;
        } else return;
      }
      set(e.clientX);
    };
    const onUp = (e: PointerEvent) => {
      if (!gesture || e.pointerId !== gesture.id) return;
      if (gesture.touch && !gesture.dragging) set(e.clientX); // a tap
      commit();
      gesture = null;
    };
    const onCancel = (e: PointerEvent) => {
      if (!gesture || e.pointerId !== gesture.id) return;
      if (gesture.dragging) commit();
      gesture = null;
    };

    wrap.addEventListener("pointerdown", onDown);
    wrap.addEventListener("pointermove", onMove);
    wrap.addEventListener("pointerup", onUp);
    wrap.addEventListener("pointercancel", onCancel);
    return () => {
      wrap.removeEventListener("pointerdown", onDown);
      wrap.removeEventListener("pointermove", onMove);
      wrap.removeEventListener("pointerup", onUp);
      wrap.removeEventListener("pointercancel", onCancel);
    };
  }, []);

  return (
    <span ref={wrapRef} className="range-wrap">
      <input
        ref={(el) => {
          inputRef.current = el;
          if (typeof ref === "function") return ref(el);
          if (ref) ref.current = el;
        }}
        type="range"
        className={cx("range", className)}
        style={style}
        {...props}
      />
    </span>
  );
}
