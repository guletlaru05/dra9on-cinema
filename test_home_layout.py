"""The photo/shade frame must not grow with translated copy or late fonts."""
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image
import unittest
from home_layout import contain_hero_media

class HeroMarkup(HTMLParser):
    def __init__(self):
        super().__init__();self.stack=[];self.photo=[];self.shade=[];self.copy=[]
    def handle_starttag(self,tag,attributes):
        attributes=dict(attributes);classes=attributes.get('class','').split()
        # A responsive <picture> may sit between the image and its media plane.
        parent=[name for _,classes in self.stack for name in classes]
        if 'hero-image' in classes:self.photo.append((parent,attributes))
        if 'hero-shade' in classes:self.shade.append(parent)
        if 'hero-content' in classes:self.copy.append(any('hero-media' in c for _,c in self.stack))
        if tag not in ('img','input','link','meta','br','hr','source','area','wbr','embed'):
            self.stack.append((tag,classes))
    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,-1,-1):
            if self.stack[index][0]==tag:
                del self.stack[index:];break

class HeroLayoutTests(unittest.TestCase):
    def test_grouping_is_idempotent_and_preserves_copy(self):
        document='<section id="hero"><img class="hero-image" width="1280" height="720"><div class="hero-shade"></div><div class="hero-content">Long translated copy</div></section>'
        grouped=contain_hero_media(document)
        self.assertEqual(contain_hero_media(grouped),grouped)
        parser=HeroMarkup();parser.feed(grouped)
        self.assertIn('hero-media',parser.photo[0][0]);self.assertIn('hero-media',parser.shade[0]);self.assertEqual(parser.copy,[False])
        self.assertIn('Long translated copy',grouped)

    def test_four_generated_home_pages_keep_photo_and_shade_apart_from_copy(self):
        if not Path('dist/index.html').exists():self.skipTest('Build site first')
        for language in ('','en','ja','es'):
            parser=HeroMarkup();parser.feed((Path('dist')/language/'index.html').read_text(encoding='utf-8'))
            self.assertEqual(len(parser.photo),1,language);self.assertEqual(len(parser.shade),1,language)
            self.assertIn('hero-media',parser.photo[0][0],language);self.assertIn('hero-media',parser.shade[0],language)
            self.assertEqual(parser.copy,[False],language)
            attributes=parser.photo[0][1]
            media=Path('dist/assets')/attributes['src'].split('/assets/',1)[1]
            with Image.open(media) as image:
                self.assertEqual((int(attributes['width']),int(attributes['height'])),image.size,language)

    def test_four_home_pages_put_navigation_before_video_below_header(self):
        if not Path('dist/index.html').exists():self.skipTest('Build site first')
        for language in ('','en','ja','es'):
            document=(Path('dist')/language/'index.html').read_text(encoding='utf-8')
            self.assertEqual(document.count('class="home-explore"'),1,language)
            self.assertLess(document.index('</header>'),document.index('class="home-explore"'),language)
            self.assertLess(document.index('class="home-explore"'),document.index('id="hero"'),language)

if __name__=='__main__':unittest.main()
