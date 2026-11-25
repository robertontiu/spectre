#!/usr/bin/env node
/**
 * Local copies of the masters, for when the site plays audio without the S3 bucket:
 * copies each track's master from ../sessions/<id>-*\/*-mastered.mp3 into public/tracks/
 * under its `file` name from data/tracks.json.
 *
 * Production plays audio from the bucket (/api/track/<slug> redirects to a signed URL),
 * so this only runs where local files are needed:
 *  - `npm run dev:local` (offline development) and static exports (`npm run export`,
 *    `export:preview`), which have no audio route: always;
 *  - `npm run build` (prebuild, the transition): only while no bucket is configured
 *    (any SPECTRE_S3_* variable missing), so the deployed site keeps playing the old
 *    local files until the owner sets the bucket up; with the bucket configured it copies
 *    nothing and the deployment carries no audio. Remove the prebuild step when the
 *    session folders leave the repo (docs/ORCHESTRATION.md, queue 11).
 *
 *   node scripts/sync-tracks.mjs            copy unless the bucket is configured
 *   node scripts/sync-tracks.mjs --force    copy regardless
 *
 * Sessions missing from this checkout can be restored with
 * `python3 ../tools/upload_track.py --fetch <id>`.
 */
import { copyFile, mkdir, readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import nextEnv from "@next/env";

const web = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const sessions = path.join(web, "..", "sessions");
const outDir = path.join(web, "public", "tracks");

nextEnv.loadEnvConfig(web, false, { info: () => {}, error: console.error });
const S3_VARS = [
  "SPECTRE_S3_ENDPOINT",
  "SPECTRE_S3_REGION",
  "SPECTRE_S3_BUCKET",
  "SPECTRE_S3_ACCESS_KEY_ID",
  "SPECTRE_S3_SECRET_ACCESS_KEY",
];
const bucket = S3_VARS.every((v) => process.env[v]?.trim());
const force = process.argv.includes("--force") || process.env.SPECTRE_EXPORT === "1";
if (bucket && !force) {
  console.log("sync-tracks: the S3 bucket is configured; audio plays from it, no local copies needed");
  process.exit(0);
}

const tracks = JSON.parse(await readFile(path.join(web, "data", "tracks.json"), "utf8"));
const sessionDirs = (await readdir(sessions, { withFileTypes: true }).catch(() => []))
  .filter((d) => d.isDirectory())
  .map((d) => d.name);
await mkdir(outDir, { recursive: true });

const sameFile = async (a, b) => {
  try {
    const [sa, sb] = await Promise.all([stat(a), stat(b)]);
    return sa.size === sb.size && sa.mtimeMs <= sb.mtimeMs;
  } catch {
    return false;
  }
};

let missing = 0;
for (const t of tracks) {
  const masters = [];
  for (const dir of sessionDirs.filter((d) => d.startsWith(`${t.id}-`)).sort()) {
    const files = await readdir(path.join(sessions, dir));
    masters.push(
      ...files
        .filter((f) => f.endsWith("-mastered.mp3"))
        .sort()
        .map((f) => path.join(sessions, dir, f)),
    );
  }
  if (!masters.length) {
    console.error(`sync-tracks: missing master for ${t.id} ${t.title} (upload_track.py --fetch ${t.id})`);
    missing++;
    continue;
  }
  const dest = path.join(outDir, t.file);
  if (await sameFile(masters[0], dest)) continue;
  await copyFile(masters[0], dest);
  console.log(`sync-tracks: ${t.id} ${t.title}: ${path.relative(web, masters[0])} -> public/tracks/${t.file}`);
}
if (missing) process.exit(1);
console.log(`sync-tracks: ${tracks.length} tracks copied to public/tracks/ (local audio)`);
