"""Keep upper/lower parts in story order on every localized watch page."""
from html.parser import HTMLParser
from pathlib import Path
import unittest


class EpisodeLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.next = []
        self.siblings = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = attrs.get('class', '').split()
        if tag == 'a' and 'next-episode' in classes:
            self.next.append(attrs['href'])
        if tag == 'a' and 'episode-item' in classes:
            self.siblings.append(attrs['href'])


class PartEpisodeLinksTests(unittest.TestCase):
    def test_upper_part_leads_to_lower_part_in_all_languages(self):
        for language in ('', 'en', 'ja', 'es'):
            prefix = '/' + language if language else ''
            paths = [prefix + '/watch/fall-707-s3-ep4-part' + str(n) + '/' for n in (1, 2)]
            for part, path in enumerate(paths):
                with self.subTest(language=language, part=part + 1):
                    parser = EpisodeLinks()
                    parser.feed((Path('dist') / path.strip('/') / 'index.html').read_text(encoding='utf-8'))
                    self.assertLess(parser.siblings.index(paths[0]), parser.siblings.index(paths[1]))
                    if part == 0:
                        self.assertEqual(parser.next, [paths[1]])
                    else:
                        self.assertNotIn(paths[0], parser.next)
