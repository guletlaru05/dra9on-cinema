# Anonymous tutorial and public-page aggregates

This Cloudflare Worker stores **numbers grouped by Korea calendar day and
canonical public page** in D1. It has no account, login, cookie, browser ID,
fingerprint, raw event table, IP, user-agent, query-string or full-referrer
storage. It never logs request bodies or upstream errors. Worker invocation
logs, persisted logs and traces are explicitly disabled in `wrangler.toml`.
Cloudflare still necessarily processes network requests at its infrastructure;
this application does not receive and persist identity data for analytics.

## Deployment requirements

Production setup was completed on **2026-10-17** using Workers Free and D1:
`https://dra9on-tutorial-metrics.tutorial-metrics.workers.dev`. The real database
binding is configured, migrations are applied, and a live `/summary` GET returned
200 with the empty database's real zero totals. The first-event `startedAt`
remains null until an event is accepted; no historical Firebase totals are
imported. The current generated registry contains **86 public routes**.

For another environment, source files alone do not activate analytics. It still
requires an authorized Cloudflare account, a **Workers Free** Worker, a real D1
binding and migrations, and the generated public-path registry. Do not upgrade
to a paid plan or add payment details to complete this setup. The setup commands
below describe a new environment; do not create a duplicate production database.

From this directory, using a locally installed/current Wrangler CLI:

```text
wrangler login
wrangler d1 create dra9on-tutorial-metrics
```

Copy the actual returned `database_id` into `wrangler.toml`, then:

```text
wrangler d1 migrations apply dra9on-tutorial-metrics --remote
wrangler deploy
```

Before deploying, regenerate `registry.json` from the build's public pages. It is
an object keyed by exact request path, containing canonical paths and types:

```json
{
  "/": {"canonicalPath": "/", "type": "page"},
  "/en/": {"canonicalPath": "/", "type": "page"},
  "/tutorials/example/": {
    "canonicalPath": "/tutorials/example/", "type": "tutorial"
  },
  "/en/tutorials/example/": {
    "canonicalPath": "/tutorials/example/", "type": "tutorial"
  }
}
```

Include home, public watch pages, tutorial list/details and other public pages;
exclude private library, sign-in pages, unpublished routes and personal tools.
Korean and English aliases share the Korean canonical path, so tutorial
popularity reflects both languages. An unregistered path is rejected. The
current registry is generated from the real site and contains 86 public routes;
each build regenerates it before the Pages workflow deploys the Worker. An empty
or incomplete registry remains fail-closed and must never be filled with invented
or private routes just to make an event pass.

Put the actual deployed Worker origin into the site's analytics configuration.
Never put a Cloudflare API token or database credentials into frontend code.
The public collector URL and public numerical summaries require no token.
Production deployment uses the encrypted GitHub Actions secret
`CLOUDFLARE_API_TOKEN`; only the public collector origin and Web Analytics beacon
identifier belong in site configuration. No API-token value is committed.

## HTTP contract

Only these production origins can send events:

- `https://dra9oncinema.com`
- `https://www.dra9oncinema.com`

POST requires an exact allowed `Origin`; CORS never allows credentials, wildcard
origins or arbitrary preview domains. CORS is a browser boundary, **not** an
anti-bot system: a script can imitate the Origin header. There are no individual
identifiers with which to deduplicate people or block a particular person.

### `POST /event`

`Content-Type: application/json`, body at most 1024 UTF-8 bytes, no query string.
Only the following fields are accepted; extra fields fail validation:

```json
{
  "kind": "pageview",
  "path": "/tutorials/example/",
  "referrer": "google",
  "entry": true
}
```

`kind` is `pageview` or `copy`. `path` must exactly match the registry. The client
classifies referrers locally as `direct`, `google`, `naver`, `youtube`,
`instagram`, `x` or `other`, and sends only the bucket. It must discard the
complete referrer URL and any query string before calling this collector.

`entry` is a boolean, true for an initial landing from an external or absent
referrer, false for navigation within this site. An entry is a **landing/page
entry event**, not a unique person, session ID or verified visitor. Reloads and
bots may affect these anonymous counts. Pageviews count page loads; prompt
copies count successful copy actions rather than mere button clicks.

A copy event is allowed only for a `type: tutorial` page:

```json
{
  "kind": "copy",
  "path": "/tutorials/example/",
  "card": "prompt-1",
  "referrer": "direct",
  "entry": false
}
```

`card` is required for copies and must match `prompt-1` through `prompt-999`.
The identifier is validated and discarded; the copy count is aggregated for the
tutorial. Prompt text, clipboards, link text, scene descriptions and form values
must never be sent. A pageview must not have a `card` field. A copy cannot be an
entry.

Successful events return 204 with `Cache-Control: no-store`, no response body and
no `Set-Cookie`. Invalid requests return 400/403; the daily event cap returns
429; unavailable storage returns 503. Do not retry events in a loop or present a
failed write as a counted event.

### `GET /summary`

Public numerical summary, cached at the edge for 60 seconds:

```json
{
  "startedAt": "2026-10-17T15:01:02.000Z",
  "updatedAt": "2026-10-17T15:01:02.000Z",
  "timezone": "Asia/Seoul",
  "day": "2026-10-18",
  "today": {"pageviews": 3, "entries": 1},
  "total": {"pageviews": 3, "entries": 1},
  "referrers": {
    "today": {"direct": 0, "google": 1, "naver": 0, "youtube": 0,
      "instagram": 0, "x": 0, "other": 0},
    "total": {"direct": 0, "google": 1, "naver": 0, "youtube": 0,
      "instagram": 0, "x": 0, "other": 0}
  },
  "tutorials": {"/tutorials/example/": {"views": 2, "copies": 1}},
  "pages": {
    "/tutorials/example/": {"views": 2, "copies": 1},
    "/watch/example/": {"views": 1, "copies": 0}
  }
}
```

The dates and numbers above illustrate the schema, not live site metrics.
`startedAt` is the actual first accepted event timestamp and remains null until
the first event. It is never copied from an old counter or backdated. Counts for
all registered tutorials are returned, including genuine zeroes. On D1 failure,
the endpoint responds with a clear 503 error instead of fabricated zero totals.

GET without an Origin header is permitted for an owner's report script. A GET
with an unapproved Origin is rejected; approved origins receive exact-origin
CORS headers. No endpoint accepts cookies as authentication or returns private
identities. Public summaries reveal only numerical public-page popularity.

### `GET /daily`

Returns a fixed **last 30 Korea calendar days**, including today. There are no
free-form date parameters or arbitrary SQL inputs. The response contains
`timezone`, `startDate`, `endDate`, `periodDays: 30`, the real `startedAt`, `days`
and `pages`. Each recorded day has `{day, pageviews, entries, copies, referrers}`.
`pages` maps registered canonical public paths to `{views, copies, entries}` for
that 30-day period. Both watch pages and tutorials are included. Days with no
stored aggregates are absent; days before collection began are not presented
as measured zero traffic. The edge cache is 60 seconds. Daily records contain
only numbers and allowlisted page paths, never individual visits.

### `GET /weekly`

Returns `timezone`, `startDate`, `endDate`, `days: 7`, `topViews` and `topCopies`.
Each top array has at most five `{path, views, copies}` entries. The range is the
current Korea calendar day and the preceding six days, inclusive. Sorting uses
the selected count descending, canonical path as a deterministic tie-break.
Non-tutorial pages never enter the tutorial rankings. Edge cache is one hour.
The owner's Sunday report can map these canonical paths to the current tutorial
titles and state the actual date range. No emails or third-party messages are
sent by this Worker.

## Free limits and write cap

As checked in the official documentation on 2026-10-17, Cloudflare Workers Free
includes **100,000 requests/day**, shared across Workers in the account. D1 Free
includes **5 million rows read/day, 100,000 rows written/day and 5 GB storage**.
Those limits reset at 00:00 UTC. Other applications in the same account also
consume these allowances. Retain the Free plan: exceeding its limits results in
rejected/failed collection, rather than silently buying extra capacity.

`MAX_DAILY_EVENTS` can lower but never raise the hard maximum of **20,000
accepted events per UTC day**. Every accepted event atomically updates three
rows: UTC budget, KST daily canonical-page aggregate and lifetime canonical-page
aggregate. There are no secondary indexes; the tables use `WITHOUT ROWID`.
`startedAt` inserts one row only for the first accepted event. This targets about
60,001 written rows on the first full-cap day, below the D1 free write limit.
SQLite/D1 metering and schema changes must still be checked in D1 Row Metrics;
extra indexes or other apps can consume the remaining allowance.

The budget check and aggregate changes are a single ordered D1 batch
transaction. `changes()` gates subsequent inserts/updates, so an event rejected
at the cap does not increment pageviews or copies. Failed transactions roll
back all changes. The budget follows UTC specifically to avoid two KST days
accidentally consuming more than one UTC free allowance. Public dates remain
KST.

Lifetime totals avoid scanning the entire daily history on each summary.
Sixty-second edge caching further reduces reads, but high traffic, many edge
locations or automated requests can still exhaust free read/request limits.
The service is intentionally aggregate-only and is not resistant to all
anonymous count manipulation. Do not treat these numbers as audited unique
users or billable ad impressions.

## Local tests

Node.js 24 or later provides the built-in SQLite adapter used by these tests;
there is no third-party test dependency and no Cloudflare credential is needed.

```text
node --test workers/tutorial-metrics/test/worker.test.mjs
```

The suite executes the real schema and SQL in SQLite, including atomic caps,
deduplication of language aliases, genuine zero/start timestamps, KST midnight,
weekly ranking, strict schema/MIME/size checks, production Origin restrictions,
copy validation, storage failure and the absence of identity/clipboard storage.

## Primary documentation

- [D1 Free limits and metering](https://developers.cloudflare.com/d1/platform/pricing/)
- [D1 atomic batch behavior](https://developers.cloudflare.com/d1/worker-api/d1-database/#batch)
- [Workers Free pricing](https://developers.cloudflare.com/workers/platform/pricing/)
- [Disable Worker invocation logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/)
- [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
