"""Check shipped responsive photos, stable layout and local font loading."""
from html.parser import HTMLParser
from pathlib import Path
import math
import unittest
from PIL import Image, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parent

class Media(HTMLParser):
    def __init__(self):super().__init__();self.images=[];self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=='img':self.images.append(dict(attrs))
        if tag=='source':self.sources.append(dict(attrs))

class PerformanceTests(unittest.TestCase):
    def test_actors_have_avif_srcsets_dimensions_and_local_fonts(self):
        for lang in ('','en','ja','es'):
            for route in ('actors','actors/min-seoa'):
                text=(ROOT/'dist'/lang/route/'index.html').read_text(encoding='utf-8')
                media=Media();media.feed(text)
                self.assertTrue(media.sources)
                self.assertTrue(all(image.get('width') and image.get('height') for image in media.images))
                self.assertTrue(all('srcset' in image for image in media.images[:-1]))
                self.assertIn('/assets/fonts/fonts-',text)
                self.assertNotIn('href="https://fonts.googleapis.com',text)
                self.assertTrue(all(source.get('type')=='image/avif' for source in media.sources))
    def test_compression_keeps_photo_dimensions_watermark_and_copyright(self):
        text=(ROOT/'dist/actors/min-seoa/index.html').read_text(encoding='utf-8')
        media=Media();media.feed(text)
        path=next(item.split()[0] for item in media.sources[0]['srcset'].split(',') if item.strip().endswith('800w'))
        before=Image.open(ROOT/'site-assets/assets/actors/min-seoa.webp').convert('RGB')
        with Image.open(ROOT/'dist'/path.lstrip('/')) as output:
            self.assertEqual(output.size,before.size)
            self.assertIn('DRA9ON CINEMA',output.getexif().get(33432,''))
            self.assertIn('© DRA9ON CINEMA. All rights reserved.'.encode(),output.info.get('xmp',b''))
            # The central watermark band must survive without crops or heavy damage.
            band=(0,round(before.height*.37),before.width,round(before.height*.48))
            difference=ImageChops.difference(before.crop(band),output.convert('RGB').crop(band))
            rms=math.sqrt(sum(value**2 for value in ImageStat.Stat(difference).rms)/3)
            self.assertGreater(20*math.log10(255/max(rms,.001)),30)
    def test_long_cache_does_not_cache_private_library_or_dynamic_feed(self):
        headers=(ROOT/'cloudflare/headers.txt').read_text()
        self.assertIn('/library/*\n  Cache-Control: no-store',headers)
        self.assertIn('/pwa/*\n  Cache-Control: no-cache',headers)
        self.assertIn('/assets/optimized/*\n  Cache-Control: public, max-age=31536000, immutable',headers)

if __name__=='__main__':unittest.main()
