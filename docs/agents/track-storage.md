# Track files in S3

Moved from AGENTS.md (section 8). Back to the router: [AGENTS.md](../../AGENTS.md). The delivery procedure around publishing is [docs/ORCHESTRATION.md](../ORCHESTRATION.md), "Delivering a finished session".

Every published track's files live in an S3-compatible bucket configured through environment variables, not in the repo. `site/data/tracks.json` is the showcase list: each track has a fixed `uuid` (v4, made once when it is first published, never changed), and that uuid is the key prefix of all its files. The names are the same for every track and defined once, in `tools/upload_track.py` (`RENDITION`, `NAMED`, `TOOLS`; the site's audio route reads `TRACK_OBJECTS` in `site/src/lib/s3.ts`):

| Object | From the session folder |
|---|---|
| `<uuid>/rendition.mp3` | `<title-slug>-mastered.mp3` (the published master; the site plays it) |
| `<uuid>/journal.md` | `journal.md` |
| `<uuid>/readme.md` | `README.md` |
| `<uuid>/prompt.md` | `PROMPT.md` |
| `<uuid>/project.json` | `project.json` |
| `<uuid>/master-report.json` | `master-report.json` |
| `<uuid>/master-tonal-balance.png` | `master-tonal-balance.png` |
| `<uuid>/ear-overview.png` | `ear-overview.png` |
| `<uuid>/tools/<path>` | every other published file (build and helper scripts), its path in the folder kept |

**What is published, and nothing else:** the files git tracks in the session folder (the sessions from before the move), plus the named files above and helper scripts (`*.py`, `*.sh`) anywhere in the folder. Never `renders/`, WAVs, `__pycache__`, listen dumps, trial masters, A/B excerpts or other scratch: they stay local and are cleaned up (ORCHESTRATION.md, standing rule 12). A session must have exactly one `*-mastered.mp3`, `journal.md`, `README.md` and `project.json`. The tool takes tracks by id, slug or uuid from `tracks.json`, never by file path, and refuses anything else.

## Workflow

Work happens locally in `sessions/<id>-<name>/`. Publishing a track, or a new version of one (a remix, a remaster), is one step:

```bash
python3 tools/upload_track.py <id>        # 1. a uuid in tracks.json if the track is new
                                          # 2. upload every new or changed file (MD5 compared; unchanged skipped)
                                          # 3. verify (Content-MD5 on upload, then size and ETag)
python3 tools/upload_track.py --check     # the bucket against tracks.json and the local sessions
python3 tools/upload_track.py --fetch <id>   # restore sessions/<folder>/ from the bucket (to remix it);
                                             # refuses to overwrite local changes without --force
```

Committing `tracks.json` and pushing stay in the normal delivery step (ORCHESTRATION.md, "Delivering a finished session"). Every object is private; the site reaches the master only through short-lived presigned URLs ([site/README.md](../../site/README.md), "Audio").

## Environment

Values never committed; in the workspace's shell, not in any file in the repo:

| Variable | Workspace (upload) | Vercel (site) |
|---|---|---|
| `SPECTRE_S3_ENDPOINT` | e.g. `https://s3.<region>.example.com` | same |
| `SPECTRE_S3_REGION` | e.g. `<region>` | same |
| `SPECTRE_S3_BUCKET` | e.g. `<your-bucket>` | same |
| `SPECTRE_S3_ACCESS_KEY_ID` / `SPECTRE_S3_SECRET_ACCESS_KEY` | a **read-write** key | a **read-only** key |
| `SPECTRE_SIGNED_URL_TTL` | | optional, default 3600 s |
| `SPECTRE_S3_CORS_ORIGINS` | optional, replaces the default CORS origins for `--cors` | |

`--cors` sets the bucket's CORS rules for the player (needed once; the key must be allowed to set bucket CORS). Requires `boto3` (in requirements.txt). The S3 settings and keys come from the environment only; ask the owner for them.

## Without a bucket

None of the `SPECTRE_S3_*` variables set (a fork, a fresh clone, or a workspace without the keys): the workflow still works. `python3 tools/upload_track.py <id>` uploads nothing and does not fail: it runs every local check (uuid in `tracks.json`, the publish set, the required files, the MP3), then prints "No S3 bucket configured: nothing uploaded. Deliver these files to the user in the chat:" with the mastered MP3 and the other publishable files and their paths, and exits 0. The publish step then means sending those files to the user in the chat (SendUserFile or the platform's equivalent), and the session folders stay local (they are the only copy: don't delete them). `--all`, `--check`, `--cors` and `--fetch` say that they need the bucket and are skipped (exit 0). A partial set of the variables is refused (set all five, or none). The site plays the local masters without a bucket ([site/README.md](../../site/README.md), "Audio").
