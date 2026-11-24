"use client";

import { useEffect, useRef, useState } from "react";
import { trackUrl } from "@/lib/site";
import type { Track } from "@/lib/tracks";
import { ShareIcon } from "./icons";

/**
 * Shares the track's link with the system share sheet where there is one, otherwise
 * copies it and says so in a small toast.
 */
export function ShareButton({ track }: { track: Track }) {
  const [toast, setToast] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  const show = (text: string) => {
    setToast(text);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setToast(null), 2200);
  };

  const share = async () => {
    const url = trackUrl(track);
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({ title: `Spectre – ${track.title}`, url });
        return;
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return;
        /* No share sheet after all (e.g. a sandboxed frame): fall back to copying. */
      }
    }
    try {
      await navigator.clipboard.writeText(url);
      show("Link copied");
    } catch {
      show("Could not copy the link");
    }
  };

  return (
    <span className="share">
      <button
        type="button"
        className="ib st"
        aria-label={`Share ${track.title}`}
        title="Share"
        onClick={() => void share()}
      >
        <ShareIcon />
      </button>
      <span className="toast" role="status" aria-live="polite" data-shown={toast ? "" : undefined}>
        {toast}
      </span>
    </span>
  );
}
