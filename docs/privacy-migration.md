# Cookie-free analytics and optional external services

The active analytics tag and the old per-browser Firebase visit identity are
removed from the consent manager. `consent.js` does not create `gtag`, a data
layer, analytics requests, or analytics identifiers. It does not load Firebase,
App Check or reCAPTCHA while simply displaying a public page.

Cloudflare Web Analytics is the selected cookie-free provider. It must remain
unloaded until the actual site token is configured; this remains the rule for
new environments and any later reset to blank configuration. On 2026-10-17 the
production site's real public Web Analytics token was configured, and its
separate anonymous collector was deployed at
`https://dra9on-tutorial-metrics.tutorial-metrics.workers.dev`. D1 migrations were
applied and a live `/summary` GET returned 200 with the genuinely empty database's
zero totals. This records completed provider setup, not a claim of historical
traffic or a completed first visitor event. The real `startedAt` remains null
until the first accepted event. Tutorial view/copy reporting uses anonymous numeric
event totals; separate server integration must not introduce client identifiers,
cookies, prompt content, or personal browsing histories.

The production registry currently contains 86 allowlisted public routes. Each
site build regenerates that registry, and the Pages workflow deploys the Worker
using the encrypted `CLOUDFLARE_API_TOKEN` secret. API tokens never go into public
HTML or JavaScript. Existing Firebase visit totals were not imported, and the
old browser-day collection was not reactivated. Live YouTube Data API sync is a
separate pending setup; prepared synchronization code is not evidence of a
working API key or accepted API terms.

## Build and player integration contract

- Every YouTube embed must use `https://www.youtube-nocookie.com/embed/VIDEO_ID`.
- Initial HTML must have **no `src`** on external iframes. Put the intended URL
  into `data-external-src`. Removing `src` after page load is too late.
- Instagram is allowed only at the existing exact URL
  `https://www.instagram.com/reel/DelRHYDunY-/embed/`. Keep its existing narrow
  per-page CSP exception; do not add a global Instagram script exception.
- Retain the original external watch links in generated HTML for users with
  JavaScript disabled or media permission denied.
- Dynamic players follow the same no-src/data-external-src contract, then call
  `window.D9ExternalConsent?.prepare(container)`. An added-node observer also
  prepares newly inserted frames.
- Do not load the YouTube iframe API until
  `window.D9ExternalConsent?.canLoadMedia()` returns true. React to
  `d9:external-consent` for changes; its detail contains `value` and
  `canLoadMedia`. Media permission never permits analytics.
- Public pages must stop loading the previous Firebase visit/player counters.
  Official YouTube counts come from the server/build API snapshot. Historical
  values must not be relabelled as new anonymous counts or YouTube figures.

## Explicit protected-service loading

Replace the initial `src` of the existing same-origin `type="module"` scripts
for `community.js` and `library/library.js` with `data-service-src`, retaining
the intended version query. Include the shared consent script/CSS on the
library as well. The loader derives exact accepted local paths from its own
asset directory, including GitHub project base paths.

The consent manager inserts a first-main panel explaining Firebase and
reCAPTCHA processing, with **Load board** or **Enable library sign-in**. Only
that explicit button inserts a new executable module script. It does not grant
media permission, grant analytics, or remove authentication, App Check,
server authorization or posting-rate protections. Module errors permit a
retry. User sign-in or posting remains a separate action in the existing UI.

The privacy policy describes protected services as explicit functional
connections. Do not ship that claim while any of these external modules still
loads automatically. If a different protected module is used by a new page,
add its reviewed exact local path and meaningful explicit action before
using it; arbitrary data-service-src values are not accepted.

## User-facing choices and cleanup

The old corner popup becomes a slim, full-width bottom bar for **external
media**, with equal visible allow/block actions and a privacy link. Footer
`data-cookie-settings` buttons should be labelled **외부 영상 설정 / External
media settings**. The original selector remains for compatibility.

`d9-external-media-choice-v1` is a necessary local preference containing only
the choice and expiry (180 days), not a visitor identity. Withdrawal removes
iframe sources, notifies player integrations, and reloads the page to stop
already loaded third-party player code. Other tabs update on storage changes.

Cleanup deletes only known legacy `_ga` / `_ga_*` and `d9-consent` cookies
reachable from the current domain, plus old analytics-choice and site-visit
storage keys. Favorites and unrelated storage are preserved. It cannot delete
other domains' cookies or old server records. Existing Firebase authorization
storage is not indiscriminately erased, because the owner library and board
still need their protected sign-in functions.

`D9AnalyticsConsent.get()` is retained only as a compatibility guard and always
returns `denied`. Its event always reports denied, regardless of media choices.
New code must use `D9ExternalConsent` for optional external media.

## Verification

Run `node test-consent.cjs`, build both languages, and run the site verifier.
In the browser, test a fresh profile, block, grant, withdraw, malformed/expired
choice, and an explicitly loaded board/library. Before permission, there should
be no YouTube/Instagram iframe request or YouTube player API request, and no
Firebase/reCAPTCHA request on ordinary public pages. Test mobile placeholders
and the bottom bar without overflow. Also verify the Instagram original prose
and narrow CSP remain unchanged.

Provider references reviewed for this migration:

- [Cloudflare Web Analytics](https://www.cloudflare.com/web-analytics/): does
  not use cookies/localStorage for analytics and does not fingerprint visitors.
- [Cloudflare data origin and collection](https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/)
- [YouTube embedding and privacy-enhanced mode](https://support.google.com/youtube/answer/171780)

Privacy-enhanced YouTube is not treated as a guarantee that loading or playing
external content never processes cookies, storage, or network/device data.
