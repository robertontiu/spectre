"use client";

import { useEffect, useRef, type ReactNode } from "react";

const SHORT_GLITCHES = ["j1", "j2", "j3"] as const;

/**
 * Wraps the logotype and, every 8-20 s, plays a horror-film glitch on it: a short
 * blur-and-shake (j1-j3, 250-600 ms) or, one time in five, a slow 2.6 s haunt. The
 * classes only swap opacity and transform on pre-blurred layers. Off when the tab is
 * hidden or the visitor prefers reduced motion.
 */
export function GlitchFrame({ label, children }: { label: string; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    let timer: ReturnType<typeof setTimeout> | undefined;
    let ending: ReturnType<typeof setTimeout> | undefined;

    const schedule = () => {
      clearTimeout(timer);
      if (reduced.matches || document.hidden) return;
      timer = setTimeout(fire, 8000 + Math.random() * 12000);
    };
    const fire = () => {
      if (reduced.matches || document.hidden) return;
      const haunt = Math.random() < 0.2;
      const cls = haunt ? "haunt" : SHORT_GLITCHES[Math.floor(Math.random() * 3)];
      const ms = haunt ? 2600 : 250 + Math.random() * 350;
      el.style.setProperty("--gd", `${ms}ms`);
      el.classList.add(cls);
      ending = setTimeout(() => {
        el.classList.remove(cls);
        schedule();
      }, ms + 30);
    };

    document.addEventListener("visibilitychange", schedule);
    reduced.addEventListener("change", schedule);
    schedule();
    return () => {
      clearTimeout(timer);
      clearTimeout(ending);
      el.classList.remove("haunt", ...SHORT_GLITCHES);
      document.removeEventListener("visibilitychange", schedule);
      reduced.removeEventListener("change", schedule);
    };
  }, []);

  return (
    <div ref={ref} className="logo-wrap" role="img" aria-label={label}>
      {children}
    </div>
  );
}
