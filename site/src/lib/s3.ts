import { createHash, createHmac } from "node:crypto";

/**
 * Presigned GET URLs for the track bucket (any S3-compatible store, configured through
 * environment variables), signed with AWS Signature Version 4 in the query string.
 *
 * Hand-written on purpose: the route only ever signs one kind of request (a GET of one
 * object, path-style, host the only signed header, unsigned payload), which is about 40
 * lines of SigV4, against @aws-sdk/client-s3 + @aws-sdk/s3-request-presigner (several MB
 * of dependencies and a heavier serverless bundle and cold start for the same string).
 * It is checked against botocore's presigner (the reference implementation) in tests.
 *
 * Server only: it reads the secret key from the environment.
 */

export type S3Config = {
  /** e.g. https://s3.<region>.example.com (path-style URLs: <endpoint>/<bucket>/<key>). */
  endpoint: URL;
  region: string;
  bucket: string;
  accessKeyId: string;
  secretAccessKey: string;
  /** Seconds a signed URL stays valid at least (SPECTRE_SIGNED_URL_TTL, default 3600). */
  ttl: number;
};

/**
 * The bucket layout, the same for every showcased track: its objects live under its
 * fixed `uuid` (tracks.json). Same names as RENDITION and JOURNAL in
 * tools/upload_track.py; documented in docs/agents/track-storage.md.
 */
export const TRACK_OBJECTS = { rendition: "rendition.mp3", journal: "journal.md" } as const;
export const renditionKey = (uuid: string) => `${uuid}/${TRACK_OBJECTS.rendition}`;

/** S3's limit for a SigV4 presigned URL (7 days). */
const MAX_EXPIRES = 604_800;
export const DEFAULT_TTL = 3600;

/**
 * The bucket configuration from the environment, or null when any required variable is
 * missing (the site then serves local copies; see site/README.md, "Audio").
 */
export function s3Config(env: NodeJS.ProcessEnv = process.env): S3Config | null {
  const get = (name: string) => env[name]?.trim() || "";
  const endpoint = get("SPECTRE_S3_ENDPOINT");
  const region = get("SPECTRE_S3_REGION");
  const bucket = get("SPECTRE_S3_BUCKET");
  const accessKeyId = get("SPECTRE_S3_ACCESS_KEY_ID");
  const secretAccessKey = get("SPECTRE_S3_SECRET_ACCESS_KEY");
  if (!endpoint || !region || !bucket || !accessKeyId || !secretAccessKey) return null;
  const ttl = Number(get("SPECTRE_SIGNED_URL_TTL") || DEFAULT_TTL);
  return {
    endpoint: new URL(endpoint),
    region,
    bucket,
    accessKeyId,
    secretAccessKey,
    ttl: Number.isFinite(ttl) && ttl >= 60 ? Math.floor(ttl) : DEFAULT_TTL,
  };
}

/** RFC 3986 encoding as SigV4 wants it: everything but A-Z a-z 0-9 - _ . ~ is escaped. */
const uriEncode = (s: string) =>
  encodeURIComponent(s).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);

const sha256 = (s: string) => createHash("sha256").update(s, "utf8").digest("hex");
const hmac = (key: Buffer | string, s: string) => createHmac("sha256", key).update(s, "utf8").digest();

/** "20261125T132900Z" */
const amzDate = (d: Date) =>
  d
    .toISOString()
    .replace(/[-:]/g, "")
    .replace(/\.\d{3}/, "");

/**
 * Signs a GET of `key` at `signedAt`, valid for `expires` seconds from then.
 * Path-style: <endpoint path>/<bucket>/<key>, each segment encoded once (S3 does not
 * double-encode the path).
 */
export function presignGet(cfg: S3Config, key: string, signedAt: Date, expires: number): string {
  const datetime = amzDate(signedAt);
  const date = datetime.slice(0, 8);
  const scope = `${date}/${cfg.region}/s3/aws4_request`;
  const base = cfg.endpoint.pathname.replace(/\/+$/, "");
  const path = `${base}/${[cfg.bucket, ...key.split("/")].map(uriEncode).join("/")}`;
  const params: [string, string][] = [
    ["X-Amz-Algorithm", "AWS4-HMAC-SHA256"],
    ["X-Amz-Credential", `${cfg.accessKeyId}/${scope}`],
    ["X-Amz-Date", datetime],
    ["X-Amz-Expires", String(Math.min(MAX_EXPIRES, Math.max(1, Math.floor(expires))))],
    ["X-Amz-SignedHeaders", "host"],
  ];
  const query = params
    .map(([k, v]) => [uriEncode(k), uriEncode(v)])
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([k, v]) => `${k}=${v}`)
    .join("&");
  const canonical = ["GET", path, query, `host:${cfg.endpoint.host}`, "", "host", "UNSIGNED-PAYLOAD"].join("\n");
  const toSign = ["AWS4-HMAC-SHA256", datetime, scope, sha256(canonical)].join("\n");
  const signingKey = hmac(hmac(hmac(hmac(`AWS4${cfg.secretAccessKey}`, date), cfg.region), "s3"), "aws4_request");
  const signature = createHmac("sha256", signingKey).update(toSign, "utf8").digest("hex");
  return `${cfg.endpoint.protocol}//${cfg.endpoint.host}${path}?${query}&X-Amz-Signature=${signature}`;
}

/**
 * Signing windows: every request within the same window gets the same URL, so a
 * browser's HTTP cache can reuse the bytes across plays and revisits (a fresh signature
 * per request would make every play a new download). The window start is the signing
 * time and the URL lives for window + TTL, so it is always valid for at least TTL
 * seconds after it is handed out.
 */
export function signedTrackUrl(cfg: S3Config, key: string, now = Date.now()): { url: string; validFor: number } {
  const window = Math.min(600, cfg.ttl);
  const start = Math.floor(now / 1000 / window) * window;
  const expires = Math.min(MAX_EXPIRES, cfg.ttl + window);
  return {
    url: presignGet(cfg, key, new Date(start * 1000), expires),
    validFor: start + expires - Math.floor(now / 1000),
  };
}
