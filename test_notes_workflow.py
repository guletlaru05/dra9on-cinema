"""Contracts for the reviewed multilingual articles and their real film frames."""
from pathlib import Path
import json
import re
import unittest
import os
from html.parser import HTMLParser
from PIL import Image
DIST = Path(os.environ.get('D9_NOTES_TEST_OUTPUT', 'dist'))


class Images(HTMLParser):
    def __init__(self):
        super().__init__(); self.images = []
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))


class ReviewedNotes(unittest.TestCase):
    def test_all_eight_pages_are_public_localized_and_linked(self):
        for lang in ('ko', 'en', 'ja', 'es'):
            prefix = '' if lang == 'ko' else '/' + lang
            for slug in ('workflow', 'fall-707-beginnings'):
                doc = (DIST / prefix.strip('/') / 'notes' / slug / 'index.html').read_text(encoding='utf-8')
                self.assertIn(f'<html lang="{lang}">', doc)
                self.assertNotIn('noindex', doc)
                self.assertNotIn('review-status', doc)
                self.assertNotIn('workflow-review', doc)
                self.assertIn('data-tutorial-image-viewer', doc)
                self.assertIn('data-image-close', doc)
                if lang in ('ja', 'es'):
                    self.assertFalse(re.search('[가-힣]', doc.replace('aria-label="한국어"', '')))
                for code in ('ko', 'en', 'ja', 'es'):
                    alternate = 'https://dra9oncinema.com' + ('' if code == 'ko' else '/' + code) + '/notes/' + slug + '/'
                    self.assertIn(f'hreflang="{code}" href="{alternate}"', doc)
                if slug == 'workflow':
                    self.assertEqual(doc.count('class="workflow-step"'), 8)
                else:
                    self.assertEqual(doc.count('class="comic-panel"'), 6)
                    self.assertIn('id="early-critique"', doc)
                if lang == 'ko':
                    self.assertIn('조선시대 고증', doc)
                    self.assertIn('한때 낙하 707 제작을 포기했습니다', doc)

    def test_stills_keep_verified_source_and_native_dimensions(self):
        folder = DIST / 'assets/notes/production-workflow'
        records = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(records), 14)
        for record in records:
            with Image.open(folder / record['file']) as image:
                self.assertEqual(image.size, (record['width'], record['height']))
            if record['kind'] == 'actual-video-frame':
                self.assertRegex(record['source'], r'^https://www.youtube.com/watch\?v=')
                self.assertIsInstance(record['time_seconds'], (int, float))
        sitemap = (DIST / 'sitemap.xml').read_text(encoding='utf-8')
        for code in ('', '/en', '/ja', '/es'):
            for route in ('/notes/workflow/', '/notes/fall-707-beginnings/'):
                self.assertIn('https://dra9oncinema.com' + code + route, sitemap)


if __name__ == '__main__':
    unittest.main()
