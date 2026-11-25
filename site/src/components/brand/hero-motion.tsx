"use client";

import { useEffect, useRef, type ReactNode } from "react";

/** The transition starts when the badge's top edge is this far below the viewport's top, in px. */
const START_MARGIN = 20;
/** Scroll share of the way down to the card at which the badge lands (the rest the card rises). */
const LAND_AT = 0.55;
/** The badge's largest size once it sits on the card's edge, in px. */
const END_SIZE = 84;
/** The title is gone by this share of the transition. */
const TITLE_FADE = 0.7;

/**
 * The scroll-linked hero. The page first scrolls normally, badge and title untransformed;
 * once the badge's top edge comes within START_MARGIN of the viewport's top, the SPECTRE
 * title fades out and drifts up, and the badge travels (and shrinks on wide screens) onto the player card's top edge,
 * centred, the edge through its middle; from there it scrolls with the card. Scrubbed by
 * the scroll position, reversible, transform and opacity only.
 *
 * One rAF-throttled scroll handler writes two transforms; it reads only `scrollY`. The
 * geometry (where the badge starts, where the card's edge is) is measured on mount and
 * whenever the header, the card or the viewport resize, from layout positions, so the end
 * point holds at every viewport size. The offset is in page coordinates, so once the
 * badge has landed it moves with the card, not with the viewport.
 * Under prefers-reduced-motion nothing moves: the title only fades with the scroll.
 */
export function HeroMotion({ badge, title }: { badge: ReactNode; title: ReactNode }) {
  const badgeWrap = useRef<HTMLDivElement>(null);
  const titleWrap = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const badgeEl = badgeWrap.current?.firstElementChild as HTMLElement | null;
    const titleEl = titleWrap.current;
    const card = document.querySelector<HTMLElement>(".player");
    if (!badgeEl || !titleEl || !card) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");

    // What is applied now, so measurements can take it back out.
    let applied = { x: 0, y: 0 };
    // Geometry: the badge's travel (page px), its end scale, and the scroll range it runs over.
    let geo = { dx: 0, dy: 0, scale: 1, start: 0, span: 1 };
    let frame = 0;

    const measure = () => {
      const b = badgeEl.getBoundingClientRect();
      const c = card.getBoundingClientRect();
      const size = badgeEl.offsetWidth || 1;
      // Layout centre of the badge (its transform's translation removed; scale keeps the centre).
      const bx = b.left + b.width / 2 - applied.x;
      const by = b.top + b.height / 2 - applied.y;
      const dx = c.left + c.width / 2 - bx;
      const dy = c.top - by;
      // Page coordinates of the badge's (untransformed) top edge, and the scroll where it
      // reaches START_MARGIN below the viewport's top: the transition starts there, at 0.
      const top = by + scrollY - (badgeEl.offsetHeight || size) / 2;
      const start = Math.max(0, top - START_MARGIN);
      const room = document.documentElement.scrollHeight - innerHeight;
      geo = {
        dx,
        dy,
        scale: Math.min(1, END_SIZE / size),
        start,
        span: Math.max(1, Math.min(dy * LAND_AT, room - start)),
      };
    };

    const render = () => {
      frame = 0;
      const into = Math.min(geo.span, Math.max(0, scrollY - geo.start));
      const p = into / geo.span;
      const fade = Math.max(0, 1 - p / TITLE_FADE);
      titleEl.style.opacity = String(fade);
      if (reduced.matches) {
        applied = { x: 0, y: 0 };
        badgeEl.style.transform = "";
        titleEl.style.transform = "";
        return;
      }
      applied = { x: geo.dx * p, y: geo.dy * p };
      const s = 1 + (geo.scale - 1) * p;
      badgeEl.style.transform = `translate3d(${applied.x}px, ${applied.y}px, 0) scale(${s})`;
      titleEl.style.transform = `translate3d(0, ${-0.4 * into}px, 0)`;
    };

    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(render);
    };
    const remeasure = () => {
      measure();
      schedule();
    };

    remeasure();
    addEventListener("scroll", schedule, { passive: true });
    addEventListener("resize", remeasure);
    reduced.addEventListener("change", remeasure);
    const observer = new ResizeObserver(remeasure);
    observer.observe(card);
    if (badgeWrap.current?.parentElement) observer.observe(badgeWrap.current.parentElement);
    return () => {
      cancelAnimationFrame(frame);
      removeEventListener("scroll", schedule);
      removeEventListener("resize", remeasure);
      reduced.removeEventListener("change", remeasure);
      observer.disconnect();
      badgeEl.style.transform = "";
      titleEl.style.transform = "";
      titleEl.style.opacity = "";
    };
  }, []);

  return (
    <>
      <div ref={badgeWrap} className="hero-badge">
        {badge}
      </div>
      <div ref={titleWrap} className="hero-title">
        {title}
      </div>
    </>
  );
}
