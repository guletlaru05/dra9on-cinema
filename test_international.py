"""Published language scope, identity, metadata and raw-count contracts."""
from pathlib import Path
import re,json,unittest

class InternationalPages(unittest.TestCase):
 def test_japanese_and_spanish_have_no_accidental_korean_copy(self):
  for lang in ('ja','es'):
   files=list((Path('dist')/lang).rglob('*.html'))
   self.assertTrue(files)
   self.assertFalse((Path('dist')/lang/'tutorials').exists())
   for file in files:
    source=file.read_text(encoding='utf-8').replace('aria-label="한국어"','')
    residual=re.findall(r'[^<>]*[가-힣][^<>]*',source)
    self.assertFalse(residual,(str(file),residual[:4]))
 def test_catalog_has_localized_fall_routes_and_english_only_original_routes(self):
  for lang in ('ja','es'):
   source=(Path('dist')/lang/'catalog.js').read_text(encoding='utf-8')
   records=json.loads(source.split(' = ',1)[1].rstrip(';\n'))
   for record in records:
    self.assertTrue(record['path'].startswith('/'+lang+'/watch/' if record['season'] else '/en/watch/'))
    self.assertFalse(re.search('[가-힣]',record['name']))
 def test_crop_dimensions_are_real_and_not_padded(self):
  from PIL import Image
  root=Path('dist/assets/press')
  for record in json.loads((root/'stills.json').read_text(encoding='utf-8')):
   with Image.open(root/(record['id']+'.jpg')) as image:self.assertEqual(image.size,(record['width'],record['height']))
   self.assertLess(record['height'],record['originalFrameHeight'])
   self.assertEqual(record['width'],record['originalFrameWidth'])
 def test_world_has_only_two_seasons_and_real_portraits(self):
  from PIL import Image
  for lang in ('','en/','ja/','es/'):
   file=Path('dist')/lang/'fall-707/world/index.html'
   source=file.read_text(encoding='utf-8')
   self.assertNotIn('S3',source)
   self.assertNotIn('시즌 3',source)
   self.assertIn('world-relationship-map',source)
   self.assertIn('fall-707-season-1-full/',source)
   self.assertIn('fall-707-season-2-full/',source)
   for name in ('captain-min','prince-iseo','yeonhwa'):
    self.assertIn(name+'.webp',source)
    with Image.open(Path('dist/assets/press')/(name+'.webp')) as image:self.assertEqual(image.size,(540,720))
 def test_world_episode_and_character_coverage(self):
  from world_details import CAST,EDGES
  from PIL import Image
  metadata=json.loads(Path('dist/assets/world/manifest.json').read_text(encoding='utf-8'))
  for lang in ('','en/','ja/','es/'):
   source=(Path('dist')/lang/'fall-707/world/index.html').read_text(encoding='utf-8')
   self.assertEqual(set(re.findall(r'data-world-episode="(s\de\d)"',source)),{f's{s}e{e}' for s in (1,2) for e in range(1,7)})
   self.assertEqual(len(re.findall(r'<article id="person-',source)),11)
   lead=re.search(r'class="world-people world-lead">(.*?)</div>',source).group(1)
   self.assertEqual(re.findall(r'id="person-([^"]+)"',lead),['captain-min'])
   supporting=re.search(r'class="world-people world-supporting">(.*?)</section>',source).group(1)
   self.assertEqual(len(re.findall(r'<article id="person-',supporting)),10)
   for person,_,_ in CAST:self.assertIn('id="person-'+person+'"',source)
   for first,second,_ in EDGES:
    for person in (first,second):self.assertIn('id="person-'+person+'"',source)
   home=(Path('dist')/lang/'index.html').read_text(encoding='utf-8')
   self.assertIn('world-home-entry',home)
   self.assertRegex(home,r'class="nav-link" href="/'+lang+'fall-707/world/"')
  ko=Path('dist/fall-707/world/index.html').read_text(encoding='utf-8')
  self.assertIn('한 중사 · 707 돌격대원',ko)
  self.assertIn('김 중사 · 707 의무·통신 대원',ko)
  self.assertNotIn(('elder-shaman','bell-shaman'),[(a,b) for a,b,_ in EDGES])
  for name,record in metadata.items():
   with Image.open(Path('dist/assets/world')/(name+'.webp')) as image:self.assertEqual(image.size,(record['width'],record['height']))

if __name__=='__main__':unittest.main()
