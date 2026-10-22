from collections import Counter
from pathlib import Path
import json,re,unittest,xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from seo import Metadata
from actors_content import ACTORS,UI

ROOT=Path(__file__).resolve().parent/'dist'

class SEOTests(unittest.TestCase):
 def test_indexed_pages_have_unique_titles_and_descriptions(self):
  titles=[];descriptions=[]
  for page in ROOT.rglob('*.html'):
   meta=Metadata(page.read_text(encoding='utf-8'))
   if meta.noindex:continue
   self.assertTrue(meta.title,page);self.assertTrue(meta.description,page)
   titles.append(meta.title);descriptions.append(meta.description)
  self.assertEqual([v for v,n in Counter(titles).items() if n>1],[])
  self.assertEqual([v for v,n in Counter(descriptions).items() if n>1],[])
 def test_actor_entities_are_explicitly_fictional_creative_works(self):
  for lang in ('ko','en','ja','es'):
   for actor in ACTORS:
    page=ROOT/('' if lang=='ko' else lang)/'actors'/actor['slug']/'index.html'
    schemas=re.findall(r'<script type="application/ld\+json">(.*?)</script>',page.read_text(encoding='utf-8'),re.S)
    entity=json.loads(schemas[0])['mainEntity']
    self.assertEqual(entity['@type'],'CreativeWork')
    self.assertIn(UI['disclosure'][lang],entity['description'])
    self.assertNotIn('"Person"',json.dumps(entity))
    self.assertNotIn('할머니',json.dumps(entity,ensure_ascii=False));self.assertNotIn('영의정',json.dumps(entity,ensure_ascii=False))
 def test_sitemap_covers_public_sections_and_robots_protects_library(self):
  sitemap=ET.parse(ROOT/'sitemap.xml')
  routes={urlsplit(node.text).path for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
  for lang in ('','/en','/ja','/es'):
   for route in ('/actors/','/actors/min-seoa/','/notes/','/lounge/','/watch/fall-707-s3-ep2/'):
    if (ROOT/(lang+route).strip('/')/'index.html').is_file():self.assertIn(lang+route,routes)
  for page in ROOT.rglob('*.html'):
   if Metadata(page.read_text(encoding='utf-8')).noindex:continue
   relative=page.relative_to(ROOT).as_posix()
   route='/'+relative.removesuffix('index.html') if relative.endswith('index.html') else '/'+relative
   self.assertIn(route,routes,page)
  self.assertNotIn('/library/',routes)
  self.assertIn('Disallow: /library/',(ROOT/'robots.txt').read_text())

if __name__=='__main__':unittest.main()
