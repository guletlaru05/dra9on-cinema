# Owner-only board notifications (review draft)

The public episode-alert database and owner-only board subscriptions are separate.
Visitors do not get an owner-subscription button. The backend verifies a signed
Firebase ID token (issuer, audience, RSA signature, expiry, verified email and
Google sign-in provider). A supplied email, nickname or DOM flag grants nothing.

Existing Firestore `communityPosts`, `communityArchive` and `communityLimits`
stay in place. The only rules change adds `character` to the existing topic enum.
It does not change text limits, the ten-minute posting rule or owner-only replies.

## Event source and privacy

After a real Firestore commit the browser submits only the post ID, with its
normal Firebase ID token and App Check proof. The Worker re-reads that exact
document through the existing Firestore security checks, verifies author/owner,
and copies only the public nickname, title, topic, timestamps and answered flag.
It never accepts client-supplied post metadata and never stores either token.
Failed event submissions are retried from a bounded local queue of public IDs.
The source post remains safely stored if notification delivery fails.

Owner sign-in reconciles the existing board in ten-document pages (up to 1,000
per pass). Until this finishes, summaries explicitly say the baseline is
incomplete rather than claiming an exact unanswered count. Replies update the
mirror after source verification; hiding a post removes it from the mirror only
after an authenticated source read confirms HTTP 404. Hidden posts remain in
the original owner archive, and no migration deletes public or archived data.

Important limitation: this is a browser-commit event bridge, not a Firestore
server trigger. Closing the browser or losing connectivity between the source
commit and the event acknowledgement can delay an alert until retry or owner
reconciliation. If guaranteed independent source monitoring is required, a
separate least-privilege server integration is still needed; do not bypass App
Check or export an owner's browser tokens to implement it.

## Dispatch

The first new post opens a ten-minute window. Concurrent posts share one open
window through an atomic conditional D1 insert. A single-post notification shows
nickname/title/topic and opens `#post-ID`; a multi-post notification says “N new
posts” and opens `#board`. Only `board_owner_subscriptions` is queried for delivery.
At 22:00 KST a single date-keyed digest lists today's posts and the unanswered
count; it cannot be replayed by another minute of the scheduler. Large OS push
payloads are shortened, with the full list available on the owner board panel.
Delivery retries are bounded to three attempts; expired endpoints are removed.
Notification bookkeeping is kept for seven days, with no click/open tracking.

## Not deployed yet

`OWNER_BOARD_ENABLED` must equal the literal string `true`; unset or `false`
keeps the feature off. The new D1 migration is `0005_owner_board.sql`.
After content review and explicit secret-storage approval:

1. Apply the D1 migration on the existing free-plan database.
2. Reuse the existing VAPID public key. Add the matching existing VAPID private
   key as a Cloudflare Worker encrypted secret named `VAPID_PRIVATE_KEY`.
   Never put the private key in source, command arguments, browser code or logs.
3. Enable the flag and a once-per-minute Worker Cron Trigger. `scheduled()` is
   implemented, but neither the flag, key transfer nor live cron was enabled.
4. Deploy the one-enum Firestore rule change with the rest of the existing rules.
5. From the owner's installed app, use the existing creator sign-in, then select
   the owner-alert button. Check an actual owner-device receipt, a signed-out
   visitor's rejection, grouped new posts and the 22:00 KST summary.

Expected additional service fee: $0 while within the existing Cloudflare free
quotas. No paid plan, Firebase Functions/Blaze upgrade or paid AI API is enabled.
At most ten owner devices are accepted. Quota exhaustion fails closed rather
than activating billing. Node/D1 fixture tests do not prove a real device receipt.

References: https://developers.cloudflare.com/workers/platform/limits/
and https://firebase.google.com/docs/auth/admin/verify-id-tokens
