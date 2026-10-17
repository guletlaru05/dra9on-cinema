# YouTube Data API daily site refresh

The source catalog (`portfolio-data.json`) remains the editorial source. The
Python standard-library synchronizer fetches the official public channel and
video facts at build time. It does not call YouTube from visitors' browsers,
download videos, modify the channel, generate subtitles, or use scraping as an
API fallback. Playback continues through the existing YouTube embed.

## Activation

1. In a Google Cloud project, enable **YouTube Data API v3** and create a dedicated
   API key restricted to that API. Do not reuse Firebase's public web identifier.
2. Put that key in the repository's Actions secret named `YOUTUBE_API_KEY`. The
   secret is only passed to the synchronization step's environment. Never put it
   in `site-assets`, the source catalog, Git history, a URL, or frontend code.
3. Run the scheduled Pages workflow or dispatch it manually. The CLI reads the
   environment variable and writes `.cache/youtube-api.json`, which is ignored
   by Git and is not copied into the public output directory.

Without that secret, the synchronizer explicitly reports **inactive**. The
existing catalog remains available and unavailable API metrics remain absent.
No zeroes, guessed totals, or previous site playback numbers are substituted.

```powershell
# The key must already be set privately in the process environment.
python youtube_sync.py --require-key
python build-portfolio.py --origin https://dra9oncinema.com
python verify-site.py --origin https://dra9oncinema.com
```

## Requests, quota and caching

- `channels.list`: one call retrieves the channel ID, uploads playlist, and
  subscriber count. The initial request resolves `@dra9oncinema` with `forHandle`.
  Later requests use the cached channel ID, or an explicitly pinned `channelId`
  in `youtube-sync.json`.
- `playlistItems.list`: retrieves up to 50 uploads per call. The first successful
  synchronization paginates the bounded uploads list. Daily refreshes stop after
  reaching a fully known page, so new uploads are still discovered after gaps.
- `videos.list`: retrieves current video facts in batches of up to 50 IDs,
  including all manual videos and all automatically imported videos.
- Each method above costs 1 quota unit per request. A channel with no more than
  50 catalog videos and one newly checked uploads page normally needs **3
  requests / 3 units per day**, roughly 90 units per 30 days. The first discovery
  can need additional playlist pages. The config caps each run at 25 requests.
  The API's default allocation is 10,000 units/day for these endpoints, shared
  with other applications in the same Google Cloud project. No quota extension,
  billing activation, or paid service is requested by this code.
- The cache suppresses additional calls on the same UTC day, including normal
  code pushes. Keep this cache with Actions cache/artifact retention of at most
  7 days; do not commit generated API snapshots or maintain an API history.
  Every published count includes its retrieval timestamp. Cache data that is
  30 days old is rejected; it must be refreshed or discarded. A failed refresh
  leaves the last valid cache untouched and reports an error instead of
  publishing partially refreshed or invented statistics.
- Use `--force` only for a manual recovery. It bypasses the daily guard but not
  the per-run request cap. `--cache PATH` supports an alternate private build
  cache. `--require-key` makes missing setup an explicit failure.

## What gets imported

Existing manual records merge by **YouTube video ID**, so a video cannot appear
twice. Manual titles, summaries, thumbnails, release settings, and editorial
categories retain priority. Exact API counts are separate fields
(`apiViewCount`, `apiSubscriberCount`), never confused with site plays or likes.

A new auto-import requires an official-channel public, embeddable, completed
video and an explicit **FALL 707 / 낙하 707 + season + episode** title. The
recognizer accepts `S3 EP.2`, `Season 3 Episode 2`, and `시즌 3 2화`. Full-season
titles such as `시즌 3 몰아보기` go into full movies. Upcoming or live broadcasts,
private/non-embeddable uploads, teasers, trailers, Shorts and highlights are not
automatically added as episodes. The default 180-second minimum protects the
episode shelves from short promotional excerpts. Ambiguous uploads require an
explicit editorial entry or the `includeVideos` override; they are not guessed
into a season. The snapshot lists rejected candidate IDs for review.

`youtube-sync.json` supports:

```json
{
  "channelHandle": "@dra9oncinema",
  "channelId": "",
  "maxRequestsPerRun": 25,
  "maxPlaylistPages": 20,
  "refreshHours": 24,
  "minimumEpisodeSeconds": 180,
  "excludeVideoIds": [],
  "includeVideos": {
    "VIDEO_ID_11": {"season": 3, "episode": 2, "category": "s3"}
  }
}
```

The placeholder ID above is illustrative only. Real overrides must be valid
11-character IDs. Exclusions never delete manual editorial records. Add a
manual record if a new original film needs a custom editorial category or copy.

New English pages use official English localization when available; otherwise
an existing English segment of the upload title and a clearly factual channel,
season and episode description. Existing hand-authored English translations
remain authoritative. No paid AI translation API is used.

## Important subscriber-count limitation

YouTube's official `statistics.subscriberCount` is itself rounded **down to three
significant figures**. The site displays that returned decimal string unchanged
(for example, `13800`), without estimating hidden digits or abbreviating it as
`1.38만`. A hidden subscriber count remains absent. Per-video `viewCount` is
likewise the exact returned decimal string, including a genuine `0`.

## Build integration and verification

```python
from youtube_sync import load_snapshot, merge_portfolio_data
data = merge_portfolio_data(data, load_snapshot())
```

Pass `apiViewCount`, `apiStatisticsUpdatedAt`, `nameEn`, `summaryEn`, explicit
`episode`, and `source` into the rendered work records. For newly imported
videos without an editorial thumbnail file, use the API's returned thumbnail
URL unchanged. Use `latest_episode()` for the newest episode by public upload
date, and generate season shelves/filters dynamically. Keep raw API metrics
separate from any site's engagement counters. English metadata must allow new
IDs instead of requiring a fixed translation dictionary.

```powershell
python -m unittest -v test_youtube_sync.py
```

These tests use deterministic fake responses, including new-season imports,
manual deduplication, exact large/zero counts, hidden subscribers, private or
foreign-channel rejection, pagination, 50-ID batches, daily cache suppression,
stale data, API-key isolation, error sanitization, and request caps. No real API
key is needed for tests.

## Primary references (checked 2026-10-17)

- [channels.list and forHandle](https://developers.google.com/youtube/data/reference/rest/v3/channels/list)
- [playlistItems.list: uploads and 50-item pagination](https://developers.google.com/youtube/data/reference/rest/v3/playlistItems/list)
- [videos.list](https://developers.google.com/youtube/data/reference/rest/v3/videos/list)
- [Quota calculator](https://developers.google.com/youtube/data/determine_quota_cost)
- [Channel subscriber count rounding](https://developers.google.com/youtube/data/reference/rest/v3/channels#statistics.subscriberCount)
- [API-key header transport](https://docs.cloud.google.com/docs/authentication/api-keys-use)
- [YouTube API data retention](https://developers.google.com/youtube/terms/developer-policies)
