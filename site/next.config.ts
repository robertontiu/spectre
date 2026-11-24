import type { NextConfig } from "next";

/**
 * `SPECTRE_EXPORT=1 next build` writes a fully static site to out/ (nothing here needs a
 * server). A normal build is what Vercel runs.
 */
const staticExport = process.env.SPECTRE_EXPORT === "1";

const nextConfig: NextConfig = {
  output: staticExport ? "export" : undefined,
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
