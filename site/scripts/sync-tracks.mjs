#!/usr/bin/env node
/**
 * Copies each track's mastered MP3 from its session folder into public/tracks/, under
 * the file name its `src` in data/tracks.json expects. Runs before `next dev` and
 * `next build` (predev/prebuild). The MP3s are not committed under site/; the session
 * folders hold the originals.
 *
 *   A track with id "005" uses the first *-mastered.mp3 in ../sessions/005-*\/.
 */
import { copyFile, mkdir, readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const web = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const sessions = path.join(web, "..", "sessions");
const outDir = path.join(web, "public", "tracks");

const tracks = JSON.parse(await readFile(path.join(web, "data", "tracks.json"), "utf8"));
const sessionDirs = (await readdir(sessions, { withFileTypes: true }))
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
    console.error(`sync-tracks: missing master for ${t.id} ${t.title}`);
    missing++;
    continue;
  }
  const dest = path.join(outDir, path.basename(t.src));
  if (await sameFile(masters[0], dest)) continue;
  await copyFile(masters[0], dest);
  console.log(
    `sync-tracks: ${t.id} ${t.title}: ${path.relative(web, masters[0])} -> public/tracks/${path.basename(dest)}`,
  );
}
if (missing) process.exit(1);
console.log(`sync-tracks: ${tracks.length - missing} tracks ready in public/tracks/`);
