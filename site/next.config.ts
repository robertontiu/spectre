import type { NextConfig } from "next";

/**
 * `SPECTRE_EXPORT=1 next build` writes a fully static site to out/. It has no server, so
 * no audio route: the masters are copied into it (scripts/sync-tracks.mjs) and played
 * from tracks/. A normal build is what Vercel runs; it plays audio through
 * /api/track/<slug> (the S3 bucket, or local copies while no bucket is configured).
 */
const staticExport = process.env.SPECTRE_EXPORT === "1";

const nextConfig: NextConfig = {
  output: staticExport ? "export" : undefined,
  env: { NEXT_PUBLIC_SPECTRE_STATIC_AUDIO: staticExport ? "1" : "" },
  // Server-only files are named *.server.ts (the audio route): a static export cannot
  // hold them, so it leaves that extension out and the route with it.
  pageExtensions: staticExport ? ["tsx", "ts", "jsx", "js"] : ["tsx", "ts", "jsx", "js", "server.ts"],
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
