from pathlib import Path
from html.parser import HTMLParser
import json,unittest,tempfile,shutil,warnings
from urllib.parse import urlsplit
from PIL import Image

ROOT=Path(__file__).resolve().parent
class Meta(HTMLParser):
 def __init__(self,text):super().__init__();self.values={};self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.values[a.get('property',a.get('name'))]=a.get('content','')
class SocialCardsTests(unittest.TestCase):
 def test_new_page_without_artwork_warns_and_gets_safe_branded_card(self):
  from social_cards import build_social_cards
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory);(out/'new-public-page').mkdir();(out/'assets/press').mkdir(parents=True)
   shutil.copyfile(ROOT/'site-assets/assets/press/dra9on-logo-dark-background.png',out/'assets/press/dra9on-logo-dark-background.png')
   (out/'new-public-page/index.html').write_text('<!doctype html><html><head><meta name="description" content="New public page description"></head><body><main><h1>New public page</h1></main></body></html>',encoding='utf-8')
   with warnings.catch_warnings(record=True) as raised:
    warnings.simplefilter('always');rows=build_social_cards(out,'https://dra9oncinema.com')
   self.assertEqual(len(raised),1);self.assertIn('OG representative image missing',str(raised[0].message))
   self.assertEqual(rows[0]['sources'],['assets/press/dra9on-logo-dark-background.png'])
   self.assertTrue(rows[0]['warning']);self.assertTrue(rows[0]['url'].startswith('https://'))
   self.assertEqual(Meta((out/'new-public-page/index.html').read_text(encoding='utf-8')).values['og:image'],rows[0]['url'])
 def test_every_indexable_page_has_own_sized_local_share_image(self):
  out=ROOT/'dist';manifest=json.loads((out/'assets/og/pages/manifest.json').read_text(encoding='utf-8'))
  from xml.etree import ElementTree as ET
  sitemap={node.text for node in ET.fromstring((out/'sitemap.xml').read_text(encoding='utf-8')).iter() if node.tag.endswith('}loc')}
  self.assertEqual({row['url'].split('/assets/og/')[0]+('' if row['language']=='ko' else '/'+row['language'])+row['route'] for row in manifest},sitemap)
  for record in manifest:
   with self.subTest(route=record['route'],language=record['language']):
    file=out/record['image'].lstrip('/');self.assertLess(file.stat().st_size,1_000_000)
    with Image.open(file) as image:self.assertEqual(image.size,(1200,630))
    route=('' if record['language']=='ko' else record['language']+'/')+record['route'].strip('/')
    doc=(out/route/'index.html').read_text(encoding='utf-8') if route else (out/'index.html').read_text(encoding='utf-8')
    meta=Meta(doc).values
    self.assertEqual(meta['og:image'],record['url']);self.assertEqual(meta['og:image'],meta['twitter:image'])
    self.assertEqual(meta['twitter:card'],'summary_large_image');self.assertIn('?v=',meta['og:image'])
    self.assertTrue(meta['og:title']);self.assertTrue(meta['og:description']);self.assertEqual(meta['og:image:width'],'1200');self.assertIn('id="d9-scroll-progress"',doc)
 def test_sources_are_existing_approved_assets_and_no_new_story_stills(self):
  manifest=json.loads((ROOT/'dist/assets/og/pages/manifest.json').read_text(encoding='utf-8'))
  for row in manifest:
   self.assertFalse(row['warning'])
   self.assertTrue(all(Path(source).suffix in ('.jpg','.png','.webp','.jpeg') for source in row['sources']))
  for lang in ('ko','en','ja','es'):
   group=next(r for r in manifest if r['kind']=='actors' and r['language']==lang)
   self.assertEqual([Path(s).stem for s in group['sources']],['min-seoa','yeonhwa','yuna','haseul'])
