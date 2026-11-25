import { renditionKey, s3Config, signedTrackUrl } from "@/lib/s3";
import { SITE_URL, localAudioPath, trackSlug } from "@/lib/site";
import { tracks } from "@/lib/tracks";

/**
 * GET /api/track/<slug>: a 302 to the track's audio.
 *
 * Named route.server.ts so static exports leave it out (next.config.ts, pageExtensions).
 *
 * With the bucket configured (SPECTRE_S3_* variables), the target is a short-lived
 * presigned GET of `<uuid>/rendition.mp3`, signed with the site's read-only key. No audio
 * passes through the function: it only signs (a few ms, no streaming, well inside
 * Vercel Hobby's function limits). Without the bucket (or with SPECTRE_LOCAL_AUDIO=1) it
 * redirects to the local copy in public/tracks/, so the site keeps working until the
 * bucket is set up.
 *
 * Hotlinking is deterred where it is cheap and cannot break playback: a request whose
 * Origin is another site, or that another site's page makes for an <audio>/<video> or
 * a fetch (Sec-Fetch-Site: cross-site), gets a 403. Requests without those headers
 * (address bar, crawlers reading og:audio, curl) pass: a missing Referer or Origin is
 * normal for <audio>, and downloading can only be deterred, never prevented.
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Below the URL's minimum life (TTL), so a cached redirect never points at an expired URL. */
const REDIRECT_MAX_AGE = 300;

const ownOrigins = (request: Request) => {
  const origins = new Set([SITE_URL, new URL(request.url).origin]);
  const host = request.headers.get("x-forwarded-host") ?? request.headers.get("host");
  if (host) origins.add(`${request.headers.get("x-forwarded-proto") ?? "https"}://${host}`);
  return origins;
};

function isForeign(request: Request): boolean {
  const origin = request.headers.get("origin");
  if (origin && !ownOrigins(request).has(origin)) return true;
  const site = request.headers.get("sec-fetch-site");
  const dest = request.headers.get("sec-fetch-dest");
  // Navigations (someone opening the og:audio link) are fine; embedding from elsewhere is not.
  return site === "cross-site" && dest !== "document";
}

const redirect = (location: string, maxAge: number) =>
  new Response(null, {
    status: 302,
    headers: { Location: location, "Cache-Control": `private, max-age=${maxAge}`, Vary: "Origin" },
  });

export async function GET(request: Request, ctx: { params: Promise<{ slug: string }> }) {
  const { slug } = await ctx.params;
  const track = tracks.find((t) => trackSlug(t) === slug);
  if (!track) return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
  if (isForeign(request)) return new Response("Forbidden", { status: 403, headers: { "Cache-Control": "no-store" } });

  // `npm run dev:local` (SPECTRE_LOCAL_AUDIO=1) plays the local copies even with a bucket configured.
  const cfg = process.env.SPECTRE_LOCAL_AUDIO === "1" ? null : s3Config();
  if (!cfg) return redirect(localAudioPath(track), REDIRECT_MAX_AGE);
  const { url, validFor } = signedTrackUrl(cfg, renditionKey(track.uuid));
  return redirect(url, Math.max(0, Math.min(REDIRECT_MAX_AGE, validFor - cfg.ttl)));
}
