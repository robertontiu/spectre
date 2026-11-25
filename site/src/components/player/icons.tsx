/* Transport icons (24x24). Stroked icons sit in buttons with the `st` class. */

export const ShuffleIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M3 7h3c4.5 0 6.5 10 11 10h3M3 17h3c1.6 0 2.8-1.3 3.8-3M13.6 10C14.6 8.4 15.6 7 17 7h3M17.5 4l3 3-3 3M17.5 14l3 3-3 3" />
  </svg>
);

export const RepeatIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M4 12V9.5A3.5 3.5 0 0 1 7.5 6H19m0 0l-3-3m3 3l-3 3M20 12v2.5a3.5 3.5 0 0 1-3.5 3.5H5m0 0l3-3m-3 3l3 3" />
  </svg>
);

export const PreviousIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 5h2.2v14H6zM19.5 5.5v13L9.5 12z" />
  </svg>
);

export const NextIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M15.8 5H18v14h-2.2zM4.5 5.5v13L14.5 12z" />
  </svg>
);

export const PlayPauseIcon = ({ playing }: { playing: boolean }) => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d={playing ? "M7 5h3.6v14H7zm6.4 0H17v14h-3.6z" : "M8 5.5v13l10.5-6.5z"} />
  </svg>
);

/** Speaker with waves, or with a cross when the button has the `muted` class. */
export const SpeakerIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z" />
    <path className="w" d="M15.5 9.5a3.5 3.5 0 0 1 0 5M18 7a7 7 0 0 1 0 10" />
    <path className="x" d="M16 10l4 4m0-4l-4 4" />
  </svg>
);

export const ShareIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 14.5V3.5M7.5 8 12 3.5 16.5 8M6 11.5H5v8.5h14v-8.5h-1" />
  </svg>
);

/** A circled "i" for the track info button. */
export const InfoIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 11v5.5M12 7.6v.1" />
  </svg>
);

export const CloseIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
);
