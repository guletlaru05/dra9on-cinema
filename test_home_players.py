"""Home-only exclusions and playable cards must survive translation/builds."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest
from urllib.parse import urlsplit, parse_qs

from home_layout import is_home_episode, home_episode_card


class HomeCards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.frames = []
        self.card_images = []
        self.ids = []

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'data-home-episode' in attrs:
            self.ids.append(attrs['data-home-episode'])
        if tag == 'iframe' and 'data-home-player' in attrs:
            self.frames.append((attrs, [kind for kind, _ in self.stack]))
        if tag == 'img' and any('card-inline' in a.get('class', '').split() for _, a in self.stack):
            self.card_images.append(attrs)
        if tag not in {'img', 'br', 'hr', 'input', 'link', 'meta', 'source', 'wbr'}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


class HomePlayersTests(unittest.TestCase):
    def test_title_keywords_and_individual_episode_identity(self):
        base = {'category': 's3', 'episode': 2, 'title': 'FALL 707 S3 EP.2'}
        self.assertTrue(is_home_episode(base))
        self.assertTrue(is_home_episode({**base, 'title': '707 Captain Lost in Explosion'}))
        for title in ('시즌 3 몰아보기', 'S3 full movie', 'S3 FULL', '시즌 3 풀버전', 'S3 OST collection'):
            self.assertFalse(is_home_episode({**base, 'title': title}), title)
        for category, episode in (('full', 0), ('original', 0), ('trailer', 0), ('ost', 0), ('s3', 0)):
            self.assertFalse(is_home_episode({**base, 'category': category, 'episode': episode}))
        self.assertEqual(base['title'], 'FALL 707 S3 EP.2')

    def test_iframe_is_outside_link_with_lazy_non_autoplay_source(self):
        work = dict(id='S1v3yFoAK5w', title='Don\'t Back Down', name='물러서지 마라',
                    label='S3 · EP.02', path='/watch/fall-707-s3-ep2/', duration='16:05')
        parser = HomeCards()
        parser.feed(home_episode_card(work))
        frame, parents = parser.frames[0]
        self.assertNotIn('a', parents)
        self.assertEqual(parser.card_images, [])
        self.assertEqual(frame['loading'], 'lazy')
        url = urlsplit(frame['data-home-src'])
        self.assertEqual(url.hostname, 'www.youtube-nocookie.com')
        self.assertEqual(parse_qs(url.query)['autoplay'], ['0'])
        self.assertNotIn('autoplay', frame['allow'])
        self.assertIn('16:05', home_episode_card(work))

    def test_four_home_pages_match_episode_filter_but_full_catalog_is_preserved(self):
        out = Path('dist')
        if not (out / 'index.html').exists():
            self.skipTest('Build site first')
        catalog = json.loads((out / 'catalog.js').read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
        included = {work['id'] for work in catalog if is_home_episode(work)}
        excluded = {work['id'] for work in catalog if not is_home_episode(work)}
        self.assertTrue(included)
        self.assertTrue(excluded)
        for language in ('', 'en', 'ja', 'es'):
            source = (out / language / 'index.html').read_text(encoding='utf-8')
            parser = HomeCards()
            parser.feed(source)
            self.assertEqual(set(parser.ids), included, language)
            self.assertEqual(len(parser.ids), len(parser.frames), language)
            self.assertEqual(parser.card_images, [], language)
            self.assertNotIn('id="binge-watch"', source)
            self.assertNotIn('id="soundtracks"', source)
            self.assertNotIn('data-category="full"', source)
        guide = (out / 'fall-707/index.html').read_text(encoding='utf-8')
        for work in catalog:
            self.assertTrue((out / work['path'].strip('/') / 'index.html').exists(), work['path'])
            if work['category'] == 'full':
                self.assertIn(work['path'], guide)


if __name__ == '__main__':
    unittest.main()
