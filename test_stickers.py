import json
from pathlib import Path
import unittest
from html.parser import HTMLParser
from PIL import Image, ImageChops
from min_stickers import LABELS, MOTIONS

ROOT=Path(__file__).resolve().parent

class Elements(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,tag,attrs):self.items.append((tag,dict(attrs)))

class Stickers(unittest.TestCase):
 def test_twelve_pages_have_all_localized_stickers_and_lazy_thumbnails(self):
  for language,index in [('ko',0),('en',1),('ja',2),('es',3)]:
   prefix='' if language=='ko' else language+'/'
   for route in ['', 'stickers/', 'notes/fall-707-beginnings/']:
    text=(ROOT/'dist'/prefix/route/'index.html').read_text(encoding='utf-8')
    parser=Elements();parser.feed(text)
    cards=[a for t,a in parser.items if 'data-sticker' in a]
    self.assertEqual([c['aria-label'] for c in cards],[x[index] for x in LABELS])
    self.assertEqual([c['data-motion'] for c in cards],list(MOTIONS))
    thumbs=[a for t,a in parser.items if t=='img' and '/assets/stickers/' in a.get('src','') and a.get('class')!='sticker-large']
    self.assertEqual(len(thumbs),12)
    for image in thumbs:
     self.assertEqual(image['loading'],'lazy');self.assertEqual(image['width'],image['height'])
     self.assertIn('240w',image['srcset']);self.assertIn('360w',image['srcset'])
    self.assertNotIn('min-sprite',text)
 def test_full_crops_preserve_every_watermark_pixel(self):
  manifest=json.loads((ROOT/'site-assets/assets/stickers/manifest.json').read_text())
  atlas=Image.open(ROOT/manifest['source']).convert('RGB')
  for tile in manifest['tiles']:
   full=Image.open(ROOT/'site-assets/assets/stickers'/tile['files'][2]['file']).convert('RGB')
   self.assertIsNone(ImageChops.difference(atlas.crop(tile['crop']),full).getbbox())
 def test_four_language_sticker_routes_in_sitemap(self):
  sitemap=(ROOT/'dist/sitemap.xml').read_text(encoding='utf-8')
  for prefix in ['', '/en', '/ja', '/es']:self.assertIn('https://dra9oncinema.com'+prefix+'/stickers/',sitemap)

if __name__=='__main__':unittest.main()
