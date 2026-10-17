"""Deterministic tests for official API synchronization; no live requests or keys."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import youtube_sync as yt

NOW = datetime(2026, 10, 17, 1, 0, tzinfo=timezone.utc)
CHANNEL = 'UC' + 'a' * 22
MANUAL_ID = '0I75_YXhMSM'
NEW_ID = 'newvideo003'
OTHER_ID = 'different01'


def config():
    return {'channelHandle': '@dra9oncinema', 'channelId': '', 'maxRequestsPerRun': 25,
            'maxPlaylistPages': 20, 'refreshHours': 24, 'minimumEpisodeSeconds': 180,
            'includeVideos': {}, 'excludeVideoIds': []}


def item(video_id, title='FALL 707: REBOOT S3 EP.2 | New Story | 새 이야기', count='12345'):
    return {'id': video_id, 'snippet': {'channelId': CHANNEL, 'title': title,
            'description': '한국어 원고를 그대로 유지합니다.', 'publishedAt': '2026-10-17T00:01:00Z',
            'thumbnails': {'high': {'url': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'}},
            'liveBroadcastContent': 'none'}, 'status': {'privacyStatus': 'public', 'embeddable': True},
            'contentDetails': {'duration': 'PT12M3S'}, 'statistics': {'viewCount': count}}


def channel_result(subscribers='13800', hidden=False):
    return {'items': [{'id': CHANNEL, 'snippet': {'title': 'DRA9ON CINEMA'},
            'contentDetails': {'relatedPlaylists': {'uploads': 'UU' + 'a' * 22}},
            'statistics': {'subscriberCount': subscribers, 'hiddenSubscriberCount': hidden}}]}


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
        self.requests = []

    def list(self, resource, **params):
        self.calls += 1
        self.requests.append((resource, params))
        if not self.replies:
            raise AssertionError('Unexpected extra API call')
        return self.replies.pop(0)


class YouTubeSyncTests(unittest.TestCase):
    def test_raw_counts_zero_large_values_and_reject_coercion(self):
        for value in ['0', '13800', '10000000000000000001']:
            self.assertEqual(yt.exact_count(value), value)
        for value in [0, 13800, 1.5, None, '1.38만', '13,800', '001', '-1', '<script>']:
            self.assertIsNone(yt.exact_count(value))

    def test_duration_and_exact_display(self):
        self.assertEqual(yt.duration_seconds('PT1H2M3S'), 3723)
        self.assertEqual(yt.duration_seconds('P1DT2H'), 93600)
        self.assertIsNone(yt.duration_seconds('12:34'))
        self.assertEqual(yt.duration_label(723), '12:03')
        self.assertIn('<strong>12345</strong>', yt.count_html('12345'))
        self.assertNotIn(',', yt.count_html('12345'))
        self.assertEqual(yt.count_html(None), '')

    def test_classify_korean_english_full_and_promos(self):
        options = config()
        for title in ['FALL 707: REBOOT S3 EP.2 | title', '낙하 707 시즌 3 2화', 'FALL 707 Season 3 Episode 2']:
            self.assertEqual(yt.classify_video(title, 723, options, NEW_ID), {'category': 's3', 'season': 3, 'episode': 2})
        self.assertEqual(yt.classify_video('낙하 707 시즌 4 몰아보기', 3000, options, NEW_ID), {'category': 'full', 'season': 4, 'episode': 0})
        for title, seconds in [('FALL 707 S3 EP.2 #shorts', 60), ('FALL 707 S3 EP.2 TRAILER', 600),
                               ('FALL 707 S3 EP.2 하이라이트', 600), ('FALL 707 S3 EP.2', 60),
                               ('FALL 707 S3', 600), ('unrelated title', 600)]:
            self.assertIsNone(yt.classify_video(title, seconds, options, NEW_ID))
        options['includeVideos'][NEW_ID] = {'season': 3, 'episode': 2}
        self.assertEqual(yt.classify_video('title without markers', 60, options, NEW_ID)['category'], 's3')

    def test_initial_import_uses_three_calls_and_channel_ownership(self):
        manual = {'channel': {}, 'videos': [{'id': MANUAL_ID, 'title': 'Editorial title'}]}
        bad = item(OTHER_ID)
        bad['snippet']['channelId'] = 'UC' + 'b' * 22
        playlist = {'items': [{'contentDetails': {'videoId': NEW_ID}, 'snippet': {'title': item(NEW_ID)['snippet']['title']}}]}
        client = FakeClient([channel_result(), playlist, {'items': [item(MANUAL_ID), item(NEW_ID), bad]}])
        snapshot = yt.synchronize(client, manual, {}, config(), now=NOW)
        self.assertEqual(client.calls, 3)
        self.assertEqual(client.requests[0][1]['forHandle'], '@dra9oncinema')
        self.assertEqual(snapshot['channel']['subscriberCount'], '13800')
        self.assertEqual(snapshot['videos'][NEW_ID]['apiViewCount'], '12345')
        self.assertNotIn(OTHER_ID, snapshot['videos'])
        self.assertEqual(snapshot['videos'][NEW_ID]['nameEn'], 'New Story')

    def test_merge_deduplicates_preserves_manual_copy_and_separate_stats(self):
        manual = {'channel': {'name': 'Editorial channel'}, 'videos': [
            {'id': MANUAL_ID, 'title': 'Manual Korean', 'thumbnail': '/custom.jpg', 'description': 'Manual story',
             'category': 's3', 'season': 3, 'sitePlayCount': 88, 'uploadDate': '2026-10-15T00:00:00Z'},
            {'id': MANUAL_ID, 'title': 'Duplicate'}]}
        original = deepcopy(manual)
        snapshot = {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': yt.timestamp(NOW),
                    'channel': {'id': CHANNEL, 'subscriberCount': '13800'},
                    'videos': {MANUAL_ID: yt.normalize_video(item(MANUAL_ID, count='0'), CHANNEL, config(), existing=True),
                               NEW_ID: yt.normalize_video(item(NEW_ID), CHANNEL, config())}}
        merged = yt.merge_portfolio_data(manual, snapshot, now=NOW)
        self.assertEqual(manual, original)
        self.assertEqual(len(merged['videos']), 2)
        old = next(video for video in merged['videos'] if video['id'] == MANUAL_ID)
        self.assertEqual((old['title'], old['thumbnail'], old['description']), ('Manual Korean', '/custom.jpg', 'Manual story'))
        self.assertEqual(old['apiViewCount'], '0')
        self.assertEqual(old['sitePlayCount'], 88)
        self.assertEqual(merged['channel']['apiSubscriberCount'], '13800')
        self.assertEqual(yt.latest_episode(merged['videos'])['id'], NEW_ID)

    def test_missing_stats_hidden_subscriber_and_nonpublic_not_invented(self):
        candidate = item(NEW_ID)
        candidate['statistics'] = {}
        self.assertIsNone(yt.normalize_video(candidate, CHANNEL, config())['apiViewCount'])
        for key, value in [('privacyStatus', 'private'), ('embeddable', False)]:
            candidate = item(NEW_ID)
            candidate['status'][key] = value
            self.assertIsNone(yt.normalize_video(candidate, CHANNEL, config()))
        client = FakeClient([channel_result(hidden=True), {'items': []}])
        result = yt.synchronize(client, {'videos': []}, {}, config(), now=NOW)
        self.assertIsNone(result['channel']['subscriberCount'])
        self.assertEqual(client.calls, 2)

    def test_daily_guard_and_next_calendar_day_refresh(self):
        previous = {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': '2026-10-17T00:59:59Z', 'videos': {}}
        client = FakeClient([])
        self.assertIs(yt.synchronize(client, {}, previous, config(), now=NOW), previous)
        self.assertEqual(client.calls, 0)
        previous['fetchedAt'] = '2026-10-16T23:59:59Z'
        client = FakeClient([channel_result(), {'items': []}])
        self.assertEqual(yt.synchronize(client, {}, previous, config(), now=NOW)['fetchedAt'], yt.timestamp(NOW))
        self.assertEqual(client.calls, 2)

    def test_incremental_discovery_stops_at_fully_known_page(self):
        previous = {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': '2026-10-16T01:00:00Z',
                    'channel': {'id': CHANNEL}, 'seenVideoIds': [NEW_ID], 'videos': {}, 'discoveryComplete': True}
        client = FakeClient([channel_result(), {'nextPageToken': 'older-page', 'items': [{'contentDetails': {'videoId': NEW_ID}}]}])
        result = yt.synchronize(client, {}, previous, config(), now=NOW)
        self.assertEqual(client.calls, 2)
        self.assertEqual(client.requests[0][1]['id'], CHANNEL)
        self.assertIn(NEW_ID, result['seenVideoIds'])

    def test_previously_seen_premiere_is_rechecked_after_publication(self):
        previous = {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': '2026-10-16T01:00:00Z',
                    'channel': {'id': CHANNEL}, 'seenVideoIds': [NEW_ID], 'videos': {}, 'discoveryComplete': True}
        client = FakeClient([channel_result(), {'nextPageToken': 'older-page', 'items': [
            {'contentDetails': {'videoId': NEW_ID}, 'snippet': {'title': item(NEW_ID)['snippet']['title']}}]},
            {'items': [item(NEW_ID)]}])
        result = yt.synchronize(client, {}, previous, config(), now=NOW)
        self.assertIn(NEW_ID, result['videos'])
        self.assertEqual(client.calls, 3)

    def test_videos_are_requested_in_batches_of_fifty(self):
        ids = [f'{number:011}' for number in range(51)]
        client = FakeClient([channel_result(), {'items': []}, {'items': []}, {'items': []}])
        yt.synchronize(client, {'videos': [{'id': video_id} for video_id in ids]}, {}, config(), now=NOW)
        self.assertEqual(client.calls, 4)
        self.assertEqual(len(client.requests[2][1]['id'].split(',')), 50)
        self.assertEqual(len(client.requests[3][1]['id'].split(',')), 1)

    def test_incomplete_discovery_aborts_instead_of_saving_false_watermark(self):
        options = config()
        options['maxPlaylistPages'] = 1
        client = FakeClient([channel_result(), {'nextPageToken': 'more', 'items': []}])
        with self.assertRaisesRegex(yt.SyncError, 'maxPlaylistPages'):
            yt.synchronize(client, {}, {}, options, now=NOW)

    def test_stale_cache_not_used_and_counts_not_recovered_from_manual(self):
        old = {'schemaVersion': 1, 'status': 'ready', 'fetchedAt': yt.timestamp(NOW - timedelta(days=30)),
               'channel': {'subscriberCount': '10000'}, 'videos': {NEW_ID: item(NEW_ID)}}
        merged = yt.merge_portfolio_data({'channel': {'apiSubscriberCount': '999'},
                    'videos': [{'id': MANUAL_ID, 'apiViewCount': '999', 'title': 'manual'}]}, old, now=NOW)
        self.assertNotIn('apiSubscriberCount', merged['channel'])
        self.assertNotIn('apiViewCount', merged['videos'][0])
        self.assertEqual(len(merged['videos']), 1)

    def test_transport_key_only_header_limit_and_safe_error(self):
        seen = []
        def opener(request, timeout):
            seen.append(request)
            return io.BytesIO(json.dumps({'items': []}).encode())
        client = yt.YouTubeClient('unit-test-secret', max_requests=1, opener=opener)
        client.list('channels', part='statistics', forHandle='@dra9oncinema')
        self.assertNotIn('unit-test-secret', seen[0].full_url)
        self.assertNotIn('key', parse_qs(urlsplit(seen[0].full_url).query))
        self.assertEqual(seen[0].get_header('X-goog-api-key'), 'unit-test-secret')
        with self.assertRaisesRegex(yt.SyncError, 'request cap'):
            client.list('channels', part='statistics')
        def bad_opener(request, timeout):
            raise HTTPError(request.full_url, 403, 'unit-test-secret upstream message', {}, None)
        with self.assertRaises(yt.SyncError) as raised:
            yt.YouTubeClient('unit-test-secret', opener=bad_opener).list('channels', part='statistics')
        self.assertNotIn('unit-test-secret', str(raised.exception))
        self.assertIn('HTTP 403', str(raised.exception))

    def test_invalid_secret_never_enters_serialized_snapshot(self):
        client = FakeClient([channel_result(), {'items': []}])
        snapshot = yt.synchronize(client, {'videos': []}, {}, config(), now=NOW)
        serialized = json.dumps(snapshot)
        for forbidden in ['apiKey', 'YOUTUBE_API_KEY', 'Authorization', 'X-Goog-Api-Key']:
            self.assertNotIn(forbidden, serialized)


if __name__ == '__main__':
    unittest.main()
