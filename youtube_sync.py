"""Build-time YouTube Data API synchronization; no browser credentials or dependencies.

The source portfolio remains editorially authoritative. API-derived counts are
decimal strings exactly as returned, never estimates, rounded abbreviations, or
site playback counters. Generated cache files must not be committed.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_CACHE = ROOT / '.cache' / 'youtube-api.json'
API_ROOT = 'https://www.googleapis.com/youtube/v3/'
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')
CHANNEL_ID = re.compile(r'^UC[A-Za-z0-9_-]{22}$')
COUNT = re.compile(r'^(?:0|[1-9][0-9]*)$')
MAX_AGE = timedelta(days=30)
SERIES = re.compile(r'(?:FALL\s*707|낙하\s*707)', re.I)
SEASON = re.compile(r'(?:\bS(?:EASON)?\s*\.?\s*(\d+)|시즌\s*(\d+))', re.I)
EPISODE = re.compile(r'(?:\bEP(?:ISODE)?\s*\.?\s*(\d+)|(\d+)\s*화)', re.I)
PROMO = re.compile(r'\b(?:TRAILER|TEASER|HIGHLIGHTS?|SHORTS?|REELS?)\b|예고편|티저|하이라이트|쇼츠', re.I)
FULL = re.compile(r'FULL\s*(?:MOVIE|VERSION|SEASON)|COMPLETE\s*SEASON|몰아보기|풀버전|전체보기|합본', re.I)


class SyncError(RuntimeError):
    """An intentionally sanitized error safe to print in CI logs."""


def utc_now():
    return datetime.now(timezone.utc)


def parse_date(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def timestamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def exact_count(value):
    """Accept only API decimal strings; preserve every digit, including zero."""
    return value if isinstance(value, str) and COUNT.fullmatch(value) else None


def read_json(path, default=None):
    path = Path(path)
    if not path.is_file():
        return deepcopy(default)
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError) as error:
        raise SyncError(f'Cannot read valid JSON: {path.name}') from error


def load_config(path=ROOT / 'youtube-sync.json'):
    config = read_json(path, {})
    handle = config.get('channelHandle', '')
    if not re.fullmatch(r'@[A-Za-z0-9_.-]+', handle):
        raise SyncError('channelHandle must be an explicit YouTube handle.')
    channel_id = config.get('channelId', '')
    if channel_id and not CHANNEL_ID.fullmatch(channel_id):
        raise SyncError('channelId must be a valid UC channel ID or empty.')
    for key, default, lower, upper in [('maxRequestsPerRun', 25, 3, 100),
                                       ('maxPlaylistPages', 20, 1, 50),
                                       ('refreshHours', 24, 24, 168),
                                       ('minimumEpisodeSeconds', 180, 0, 3600)]:
        value = config.get(key, default)
        if type(value) is not int or not lower <= value <= upper:
            raise SyncError(f'Invalid YouTube sync limit: {key}')
        config[key] = value
    for video_id in [*config.get('excludeVideoIds', []), *config.get('includeVideos', {})]:
        if not VIDEO_ID.fullmatch(video_id):
            raise SyncError('YouTube overrides must use valid video IDs.')
    return config


def fresh_snapshot(snapshot, now=None):
    now = now or utc_now()
    fetched = parse_date((snapshot or {}).get('fetchedAt'))
    return bool(snapshot and snapshot.get('schemaVersion') == 1 and snapshot.get('status') == 'ready'
                and fetched and timedelta(0) <= now - fetched < MAX_AGE)


def load_snapshot(path=None, now=None):
    path = path or os.environ.get('YOUTUBE_SNAPSHOT_PATH') or DEFAULT_CACHE
    snapshot = read_json(path, {})
    return snapshot if fresh_snapshot(snapshot, now) else {}


class YouTubeClient:
    def __init__(self, api_key, max_requests=25, opener=urlopen):
        if not isinstance(api_key, str) or not api_key.strip():
            raise SyncError('YOUTUBE_API_KEY is not configured.')
        self._api_key = api_key.strip()
        self.max_requests = max_requests
        self.calls = 0
        self._opener = opener

    def list(self, resource, **parameters):
        if resource not in {'channels', 'playlistItems', 'videos'}:
            raise SyncError('This synchronizer only supports read-only list methods.')
        if self.calls >= self.max_requests:
            raise SyncError('YouTube sync reached its configured daily request cap.')
        self.calls += 1
        url = API_ROOT + resource + '?' + urlencode(parameters)
        request = Request(url, headers={'X-Goog-Api-Key': self._api_key,
                                       'Accept': 'application/json',
                                       'User-Agent': 'DRA9ON-CINEMA-YouTube-sync/1.0'})
        try:
            with self._opener(request, timeout=30) as response:
                data = json.loads(response.read(8 * 1024 * 1024).decode('utf-8'))
        except HTTPError as error:
            # Never echo the URL, response body, credentials, or upstream message.
            raise SyncError(f'YouTube {resource}.list failed (HTTP {error.code}); previous cache retained.') from None
        except (URLError, TimeoutError, OSError, ValueError) as error:
            raise SyncError(f'YouTube {resource}.list could not complete; previous cache retained.') from None
        if not isinstance(data, dict) or not isinstance(data.get('items'), list):
            raise SyncError(f'YouTube {resource}.list returned an invalid response.')
        return data


def duration_seconds(value):
    match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', str(value))
    if not match:
        return None
    days, hours, minutes, seconds = (int(item or 0) for item in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def duration_label(seconds):
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f'{hours}:{minutes:02}:{seconds:02}' if hours else f'{minutes}:{seconds:02}'


def thumbnail_url(snippet):
    thumbnails = snippet.get('thumbnails', {})
    for quality in ['maxres', 'standard', 'high', 'medium', 'default']:
        url = thumbnails.get(quality, {}).get('url', '')
        parsed = urlsplit(url)
        if parsed.scheme == 'https' and parsed.hostname in {'i.ytimg.com', 'img.youtube.com'}:
            return url  # Use the original API URL, not a constructed resolution.
    return None


def classify_video(title, seconds, config, video_id):
    """Conservative automatic season routing; ambiguous uploads await an override."""
    override = config.get('includeVideos', {}).get(video_id)
    if override:
        season = override.get('season')
        episode = override.get('episode', 0)
        category = override.get('category', f's{season}')
        if type(season) is not int or season < 1 or type(episode) is not int or episode < 0:
            raise SyncError('includeVideos requires integer season and episode values.')
        if category != 'full' and category != f's{season}':
            raise SyncError('includeVideos category must match its season, or be full.')
        return {'season': season, 'episode': episode, 'category': category}
    if not SERIES.search(title) or PROMO.search(title):
        return None
    season_match = SEASON.search(title)
    if not season_match:
        return None
    season = int(next(value for value in season_match.groups() if value))
    if not 1 <= season <= 99:
        return None
    if FULL.search(title):
        return {'season': season, 'episode': 0, 'category': 'full'}
    episode_match = EPISODE.search(title)
    if not episode_match or seconds is None or seconds < config['minimumEpisodeSeconds']:
        return None
    episode = int(next(value for value in episode_match.groups() if value))
    return {'season': season, 'episode': episode, 'category': f's{season}'} if episode >= 1 else None


def english_metadata(item, classification):
    localized = item.get('localizations', {})
    english = next((localized[key] for key in ['en', 'en-US', 'en-GB'] if localized.get(key)), {})
    title = english.get('title', '')
    if not title or re.search('[가-힣]', title):
        parts = [part.strip() for part in item['snippet']['title'].split('|')]
        candidates = [part for part in parts if re.search('[A-Za-z]', part) and not re.search('[가-힣]', part)]
        title = candidates[-1] if candidates else ''
    fallback = f'FALL 707: REBOOT · Season {classification["season"]}'
    if classification['category'] != 'full':
        fallback += f' · Episode {classification["episode"]}'
    else:
        fallback += ' · Full Movie'
    description = english.get('description', '')
    if not description or re.search('[가-힣]', description):
        description = f'Watch {fallback} on the official DRA9ON CINEMA YouTube channel.'
    return {'nameEn': title or fallback, 'summaryEn': description.split('\n\n')[0][:420]}


def normalize_video(item, channel_id, config, existing=False):
    video_id = item.get('id', '')
    snippet = item.get('snippet', {})
    status = item.get('status', {})
    if (not VIDEO_ID.fullmatch(video_id) or snippet.get('channelId') != channel_id
            or status.get('privacyStatus') != 'public' or status.get('embeddable') is not True
            or snippet.get('liveBroadcastContent') in {'upcoming', 'live'}):
        return None
    published = parse_date(snippet.get('publishedAt'))
    seconds = duration_seconds(item.get('contentDetails', {}).get('duration'))
    thumbnail = thumbnail_url(snippet)
    if not published or seconds is None or seconds <= 0 or not thumbnail:
        return None
    classification = classify_video(snippet.get('title', ''), seconds, config, video_id)
    if not existing and not classification:
        return None
    record = {'id': video_id, 'title': snippet.get('title', ''),
              'description': snippet.get('description', ''), 'uploadDate': snippet['publishedAt'],
              'thumbnail': thumbnail, 'seconds': seconds, 'duration': duration_label(seconds),
              'isEmbeddable': True, 'apiViewCount': exact_count(item.get('statistics', {}).get('viewCount'))}
    if classification:
        record.update(classification)
        record.update(english_metadata(item, classification))
    return record


def synchronize(client, manual, previous, config, now=None, force=False):
    now = now or utc_now()
    previous = previous if fresh_snapshot(previous, now) else {}
    fetched = parse_date(previous.get('fetchedAt'))
    # A daily Actions job can start seconds earlier than yesterday's run. Using
    # the UTC calendar day avoids accidentally skipping every other daily run.
    cached_for_period = (fetched and (now.date() == fetched.date() if config['refreshHours'] == 24
                                    else now - fetched < timedelta(hours=config['refreshHours'])))
    if cached_for_period and not force:
        return previous
    manual_ids = {video['id'] for video in manual.get('videos', [])}
    cached_channel = previous.get('channel', {})
    channel_id = config.get('channelId') or cached_channel.get('id')
    channel_filter = {'id': channel_id} if channel_id else {'forHandle': config['channelHandle']}
    channel_result = client.list('channels', part='snippet,contentDetails,statistics',
                                 fields='items(id,snippet(title,customUrl),contentDetails(relatedPlaylists/uploads),statistics(subscriberCount,hiddenSubscriberCount))',
                                 **channel_filter)
    channels = channel_result['items']
    if len(channels) != 1 or not CHANNEL_ID.fullmatch(channels[0].get('id', '')):
        raise SyncError('The configured YouTube channel could not be resolved uniquely.')
    channel = channels[0]
    channel_id = channel['id']
    if config.get('channelId') and channel_id != config['channelId']:
        raise SyncError('YouTube returned a different channel than the configured channel ID.')
    playlist_id = channel.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
    if not isinstance(playlist_id, str) or not playlist_id.startswith('UU'):
        raise SyncError('The channel has no valid uploads playlist.')
    known_ids = set(previous.get('seenVideoIds', []))
    seen_ids = set(known_ids)
    candidates = set()
    page_token = None
    complete = False
    for _ in range(config['maxPlaylistPages']):
        params = {'part': 'snippet,contentDetails', 'playlistId': playlist_id, 'maxResults': 50,
                  'fields': 'nextPageToken,items(contentDetails/videoId,snippet(title))'}
        if page_token:
            params['pageToken'] = page_token
        result = client.list('playlistItems', **params)
        page_ids = []
        for item in result['items']:
            video_id = item.get('contentDetails', {}).get('videoId', '')
            if not VIDEO_ID.fullmatch(video_id):
                continue
            page_ids.append(video_id)
            seen_ids.add(video_id)
            title = item.get('snippet', {}).get('title', '')
            # Recheck series uploads visible on the scanned page even if their
            # ID was already seen: a scheduled premiere can become public, and
            # a creator can correct the season/episode title after uploading.
            if (SERIES.search(title) and not PROMO.search(title)) or video_id in config.get('includeVideos', {}):
                candidates.add(video_id)
        page_token = result.get('nextPageToken')
        if not page_token or (previous.get('discoveryComplete') and page_ids and all(video_id in known_ids for video_id in page_ids)):
            complete = True
            break
    if not complete:
        # Do not save a false discovery watermark; next run can retry safely.
        raise SyncError('Uploads exceeded maxPlaylistPages; increase the bounded limit before syncing.')
    previous_ids = set(previous.get('videos', {}))
    excluded = set(config.get('excludeVideoIds', []))
    requested = sorted((manual_ids | previous_ids | candidates | set(config.get('includeVideos', {}))) - excluded)
    videos = {}
    rejected = []
    for offset in range(0, len(requested), 50):
        batch = requested[offset:offset + 50]
        result = client.list('videos', part='snippet,contentDetails,status,statistics,localizations',
                             id=','.join(batch), maxResults=50,
                             fields='items(id,snippet(channelId,title,description,publishedAt,thumbnails,liveBroadcastContent),contentDetails/duration,status(privacyStatus,embeddable),statistics/viewCount,localizations)')
        for item in result['items']:
            if item.get('id') not in batch:
                continue
            record = normalize_video(item, channel_id, config, existing=item['id'] in manual_ids)
            if record:
                videos[record['id']] = record
            elif item['id'] not in manual_ids:
                rejected.append(item['id'])
    channel_stats = channel.get('statistics', {})
    hidden = channel_stats.get('hiddenSubscriberCount') is True
    return {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': timestamp(now),
            'source': 'YouTube Data API v3',
            'channel': {'id': channel_id, 'handle': config['channelHandle'],
                        'title': channel.get('snippet', {}).get('title', ''),
                        'subscriberCount': None if hidden else exact_count(channel_stats.get('subscriberCount')),
                        'hiddenSubscriberCount': hidden},
            'videos': videos, 'seenVideoIds': sorted(seen_ids), 'discoveryComplete': True,
            'reviewVideoIds': sorted(set(rejected)), 'requestsUsed': client.calls}


def merge_portfolio_data(manual, snapshot=None, now=None):
    """Overlay exact API facts, preserving manual copy/thumbnail/release settings."""
    merged = deepcopy(manual)
    snapshot = snapshot if fresh_snapshot(snapshot, now) else {}
    available = snapshot.get('videos', {})
    result = []
    existing = set()
    for video in merged.get('videos', []):
        video_id = video['id']
        if video_id in existing:
            continue
        existing.add(video_id)
        # These fields may only come from a currently valid API response.
        for key in ['apiViewCount', 'apiStatisticsUpdatedAt']:
            video.pop(key, None)
        if video_id in available:
            video['apiViewCount'] = exact_count(available[video_id].get('apiViewCount'))
            video['apiStatisticsUpdatedAt'] = snapshot['fetchedAt']
        result.append(video)
    for video_id, record in available.items():
        if video_id in existing or not VIDEO_ID.fullmatch(video_id) or not record.get('category'):
            continue
        video = deepcopy(record)
        video['source'] = 'youtube-data-api'
        video['apiViewCount'] = exact_count(record.get('apiViewCount'))
        video['apiStatisticsUpdatedAt'] = snapshot['fetchedAt']
        result.append(video)
        existing.add(video_id)
    result.sort(key=lambda video: parse_date(video.get('uploadDate')) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    merged['videos'] = result
    channel = merged.setdefault('channel', {})
    channel.pop('apiSubscriberCount', None)
    channel.pop('apiStatisticsUpdatedAt', None)
    channel.pop('apiChannelId', None)
    channel.pop('apiHiddenSubscriberCount', None)
    if snapshot:
        channel['apiSubscriberCount'] = exact_count(snapshot.get('channel', {}).get('subscriberCount'))
        channel['apiStatisticsUpdatedAt'] = snapshot['fetchedAt']
        channel['apiChannelId'] = snapshot.get('channel', {}).get('id')
        channel['apiHiddenSubscriberCount'] = snapshot.get('channel', {}).get('hiddenSubscriberCount') is True
    merged['youtubeSync'] = {'status': 'ready' if snapshot else 'not-configured',
                             'fetchedAt': snapshot.get('fetchedAt'),
                             'source': 'YouTube Data API v3'}
    return merged


def latest_episode(videos):
    episodic = [video for video in videos if re.fullmatch(r's[1-9][0-9]*', video.get('category', ''))]
    return max(episodic, key=lambda video: parse_date(video.get('uploadDate')) or datetime.min.replace(tzinfo=timezone.utc), default=None)


def count_html(count, *, lang='ko', kind='views', updated_at=None):
    """Exact decimal count, accessible label, and timestamp; nothing for missing data."""
    count = exact_count(count)
    if count is None:
        return ''
    label = ('YouTube views' if kind == 'views' else 'YouTube subscribers') if lang == 'en' else ('YouTube 조회수' if kind == 'views' else 'YouTube 구독자')
    updated = parse_date(updated_at)
    date = timestamp(updated) if updated else ''
    return (f'<span class="youtube-api-count" data-youtube-api-count data-updated-at="{escape(date, quote=True)}">'
            f'{label} <strong>{count}</strong></span>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'youtube-sync.json')
    parser.add_argument('--source', type=Path, default=ROOT / 'portfolio-data.json')
    parser.add_argument('--cache', type=Path, default=DEFAULT_CACHE)
    parser.add_argument('--require-key', action='store_true')
    parser.add_argument('--force', action='store_true', help='Manual recovery only; bypass the daily cache guard.')
    args = parser.parse_args(argv)
    try:
        key = os.environ.get('YOUTUBE_API_KEY', '').strip()
        if not key:
            print('YouTube API sync inactive: YOUTUBE_API_KEY is not configured; no API calls or placeholder counts.')
            return 2 if args.require_key else 0
        config = load_config(args.config)
        manual = read_json(args.source, {})
        previous = load_snapshot(args.cache)
        client = YouTubeClient(key, max_requests=config['maxRequestsPerRun'])
        snapshot = synchronize(client, manual, previous, config, force=args.force)
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.cache.with_suffix('.tmp')
        temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(args.cache)
        print(f'YouTube API sync: {len(snapshot["videos"])} videos; {client.calls} requests; fetched {snapshot["fetchedAt"]}.')
        return 0
    except SyncError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
