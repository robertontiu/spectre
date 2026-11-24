#!/usr/bin/env node
/**
 * Prepares a static export (out/) for preview hosts that serve the files under a
 * sub-path and reserve names starting with "_" (such as a claude.ai artifact):
 *
 *  - moves out/_next/ to out/assets/ and rewrites the root-relative /_next/ and icon
 *    URLs in the HTML and RSC payloads to relative ./assets/ and ./ URLs;
 *  - points Turbopack's chunk loader (TURBOPACK_CHUNK_BASE_PATH) at ./assets/;
 *  - keeps only the home page: drops the track pages (their links need the real
 *    domain), the RSC payloads for client-side navigation, the 404 route, robots,
 *    sitemap and the build-id manifests.
 *
 * Run it through `npm run export:preview`, which also builds with
 * NEXT_PUBLIC_SPECTRE_PREVIEW=1 (relative audio URLs, no address-bar updates).
 *
 * Not needed on Vercel or any host that serves the site at its domain root.
 *
 *   npm run export:preview
 */
import { readdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ASSETS = "assets";
const out = path.join(path.dirname(path.dirname(fileURLToPath(import.meta.url))), "out");

const routeOnly = (entry) =>
  (entry.startsWith("_") && entry !== "_next") ||
  ["404.html", "track", "robots.txt", "sitemap.xml"].includes(entry) ||
  entry.endsWith(".txt");
for (const entry of await readdir(out)) {
  if (routeOnly(entry)) await rm(path.join(out, entry), { recursive: true });
}
await rm(path.join(out, ASSETS), { recursive: true, force: true });
await rename(path.join(out, "_next"), path.join(out, ASSETS));
/* Build-id manifests serve the Pages Router; nothing on this App Router page loads them. */
for (const entry of await readdir(path.join(out, ASSETS, "static"))) {
  if (entry !== "chunks" && entry !== "media") await rm(path.join(out, ASSETS, "static", entry), { recursive: true });
}

/* Root-relative URLs in attributes ("/x) and inside the escaped RSC payload (\"/x). */
const rootRelative = /(["'(]|\\")\/(_next\/|icon\.svg|apple-icon\.png|favicon\.ico)/g;
const chunkBase = `<script>TURBOPACK_CHUNK_BASE_PATH="./${ASSETS}/"</script>`;

const html = path.join(out, "index.html");
const page = (await readFile(html, "utf8"))
  .replace(rootRelative, (_, quote, target) => `${quote}./${target === "_next/" ? `${ASSETS}/` : target}`)
  .replace("<head>", `<head>${chunkBase}`);
await writeFile(html, page);
console.log(`preview-export: out/ is ready to serve from any path (assets in out/${ASSETS}/)`);
