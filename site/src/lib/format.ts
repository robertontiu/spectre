/** Formats seconds as m:ss. */
export function formatTime(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

/** The one-paragraph description of a track used in link previews and the info dialog. */
export function trackDescription(t: {
  genre: string;
  model: string;
  bpm: number;
  duration: number;
  feeling: string;
  style: string;
}): string {
  return `${t.genre} by Spectre (produced on ${t.model}), ${t.bpm} BPM, ${formatTime(Math.round(t.duration))}. Feeling: ${t.feeling}. ${t.style}.`;
}
