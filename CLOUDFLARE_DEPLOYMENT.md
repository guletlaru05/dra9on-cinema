# Cloudflare deployment preparation

Stage 2 deploys the public site to `https://dra9on-cinema.pages.dev` through
the selected-repository Cloudflare Workers and Pages GitHub App. It does not
change DNS, the production domain, Firebase rules, subscriptions, or R2.

## Build settings

- Production branch: `main`; framework: None.
- Build command: `bash scripts/cloudflare-build.sh`; output directory: `dist`.
- `SITE_ORIGIN=https://dra9on-cinema.pages.dev`
- `D9_DEPLOYMENT_STAGE=preview`, `PYTHON_VERSION=3.11`, `NODE_VERSION=24`.
- Disable branch previews. Do not authorize arbitrary deployment hostnames for
  Firebase or API access. The fixed temporary hostname is reviewed separately.
- Do not copy GitHub Secrets into the Cloudflare build. Public builds consume
  only `build-assets/youtube-public.json`, validated against the owner's channel.
- `CF_PAGES_COMMIT_SHA` becomes the episode feed and deployment revision.
- Preview HTML and robots.txt exclude indexing. Preview analytics collection is
  disabled so verification traffic does not enter production counters.

## Automations

`youtube-snapshot.yml` refreshes metadata daily at 05:00 KST and supports manual
dispatch. Only the validated public JSON is committed, and only when changed.
Cloudflare's Git integration builds the resulting main commit automatically.
The server API key remains in GitHub Secrets. A failed refresh preserves the
last good public metadata and fails the workflow visibly.

`cloudflare-preview-check.yml` waits for the exact revision and checks the four
language episode feed. Its notification dry run reads the preview only; it
cannot send or lease production notifications. Commits made by GITHUB_TOKEN
do not start other GitHub workflows, so this independent check is run on normal
human pushes or manually; Cloudflare Git deployment is checked in its own UI.

`weekly-site-check-backup.yml` runs Mondays at 08:30 KST and manually. It checks
privacy/access invariants, builds the public site, verifies a full Git bundle,
and stores that bundle plus the public build and SHA-256 manifest for 7 days.
No Firestore/D1 rows, private-library corpus, credentials or PC originals are
included. Private database backups still need a separate secure destination.

The existing GitHub Pages workflow remains enabled as the live site and
fallback. It reads the same metadata snapshot and still deploys the existing
two API Workers. Production episode notifications continue to read only
`https://dra9oncinema.com`, verify revisions and deduplicate releases. The
public domain does not change at cutover, so subscription keys stay unchanged.

## Cutover checklist

- Preview Firebase/App Check/API origin authorization and real browser checks.
- Stage 3 security response headers applied and verified on the temporary deployment.
- Owner-authorized nameserver change, certificate readiness and applicable email verification.
- Production-origin build settings and canonical SEO checks at Stage 5.
- Keep GitHub Pages for at least a week; do not make this GitHub Free repository
  private until the owner decides how to preserve branch protection/fallback.

## Required temporary-access cleanup after Stage 5

2026-10-21 cutover authorization: continue Stages 3-5 without stage gates;
stop for owner authentication, payment, removal of existing DNS/data, or a
production outage lasting 30 minutes. Preserve GitHub Pages for at least 7 days.
Do not change repository visibility or activate R2.

Cloudflare builds now emit response headers in `_headers`, retain existing meta
CSP, and protect Firebase helper responses directly in the Worker. Public HTML
uses DENY / frame-ancestors none; same-origin Firebase helpers use SAMEORIGIN /
frame-ancestors self. The canonical Cloudflare build uses the same tested login
flow with its authDomain fixed to dra9oncinema.com. GitHub fallback keeps its
existing authentication flow. Add the canonical OAuth redirect handler before
switching the Pages build to production; preserve the original Firebase handler.

When switching Pages variables to SITE_ORIGIN=https://dra9oncinema.com and
D9_DEPLOYMENT_STAGE=production, set GitHub repository variables CF_SITE_ORIGIN
and CF_DEPLOYMENT_STAGE to matching values. Keep preview-only workflow reads and
notification dry runs until the final canonical checks, then revise/disable
temporary preview checks. Owner-library metrics API connectivity is explicitly
allowed by library CSP independently of the analytics collection configuration.

Owner approved ONLY `dra9on-cinema.pages.dev` for validation. After nameservers
have propagated and `dra9oncinema.com` works on the new deployment, remove:

1. Firebase Authentication `authorizedDomains`: `dra9on-cinema.pages.dev`.
2. reCAPTCHA Enterprise key allowed domains: `dra9on-cinema.pages.dev`.
3. Firebase browser API key HTTP referrers: `https://dra9on-cinema.pages.dev/*`.
4. Tutorial metrics/private-reader Worker `PROD_ORIGINS` and `ALLOWED_ORIGINS`:
   `https://dra9on-cinema.pages.dev`.
5. Episode push Worker `ORIGINS`: `https://dra9on-cinema.pages.dev`.
6. Google OAuth web client authorized redirect URI:
   `https://dra9on-cinema.pages.dev/__/auth/handler`.

The Cloudflare library build uses Firebase's documented same-origin helper
proxy, routed only at `/__/auth/*` and `/__/firebase/init.json`. Preview uses
the fixed temporary hostname; canonical production uses `dra9oncinema.com`.
Keep the hardened bootstrap and helper routing on canonical Cloudflare hosting.
Only the temporary hostname and its OAuth redirect/allowlist entries are removed.
GitHub Pages fallback scripts, owner checks and Firestore rules are unchanged.
No auth request bodies or tokens are logged, cached or stored by the proxy;
static requests do not invoke it.

An initially unloaded login button starts the explicit Firebase preparation and
shows progress; a second click after readiness starts sign-in. On iPhone/iPad,
use same-window redirect; on desktop, popup opens directly in the click stack.
Blocked popup/storage, module timeout and a missing redirect result show an
accessible on-screen reason. Actual iPhone Safari and standalone PC Chrome sign-in remain owner device
checks; the latest owner instruction permits Stages 3-5 to continue autonomously.
Record untested devices explicitly instead of claiming an actual device test.

Preserve all previous production domains, API restrictions, owner authentication
and Firestore rules. Verify the fixed preview origin is then rejected again.
Revise/disable preview-only checks and notification dry-run allowlist, switch
the Pages origin/stage to production, and repeat canonical-domain smoke tests.
