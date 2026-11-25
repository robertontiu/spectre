#!/usr/bin/env bash
# Vercel "Ignored Build Step" (vercel.json ignoreCommand; runs in site/, the Root Directory).
# Exit 0 skips the deployment, exit 1 builds it.
# Builds only when something the site uses changed since the last deployed commit: anything under site/,
# or a session master (../sessions/*/*-mastered.mp3, which the prebuild copies as a local fallback).
# Engine, docs, tools and journal commits on main then no longer redeploy the site.
# Builds whenever it can't tell (first deploy, or the previous commit isn't in Vercel's shallow clone).
prev="${VERCEL_GIT_PREVIOUS_SHA:-}"
if [ -z "$prev" ]; then
  echo "ignore-build: no previous deployment commit, building"; exit 1
fi
if ! git cat-file -e "$prev^{commit}" 2>/dev/null; then
  git fetch -q --depth=1 origin "$prev" 2>/dev/null || { echo "ignore-build: $prev not available, building"; exit 1; }
fi
if git diff --quiet "$prev" HEAD -- . ':(glob)../sessions/*/*-mastered.mp3'; then
  echo "ignore-build: nothing the site uses changed since ${prev:0:7}, skipping"; exit 0
fi
echo "ignore-build: site changes since ${prev:0:7}, building"; exit 1
