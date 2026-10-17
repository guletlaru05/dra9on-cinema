import unittest,json,re
from pathlib import Path
from PIL import Image
class PWA(unittest.TestCase):
 def test_four_languages_install_and_launch_without_changing_catalogs(self):
  root=Path('dist')
  for lang in ('ko','en','ja','es'):
   manifest=json.loads((root/'pwa'/f'manifest-{lang}.webmanifest').read_text(encoding='utf-8'))
   self.assertEqual(manifest['name'],'DRA9ON CINEMA');self.assertEqual(manifest['short_name'],'DRA9ON');self.assertEqual(manifest['display'],'standalone');self.assertEqual(manifest['id'],'/')
   prefix='' if lang=='ko' else lang+'/'
   source=(root/prefix/'index.html').read_text(encoding='utf-8')
   self.assertIn('manifest-'+lang+'.webmanifest',source);self.assertIn('apple-touch-icon',source)
   self.assertIn('연결이 끊겼습니다' if lang=='ko' else {'en':'You are offline','ja':'接続されていません','es':'Sin conexión'}[lang],(root/'pwa'/f'offline-{lang}.html').read_text(encoding='utf-8'))
  for name,size in [('icon-192.png',192),('icon-512.png',512),('icon-maskable-512.png',512),('apple-touch-icon.png',180)]:
   with Image.open(root/'pwa'/name) as icon:self.assertEqual(icon.size,(size,size));self.assertEqual(icon.getpixel((0,0)),(16,16,17))
 def test_feed_is_released_episodic_only_with_real_localized_paths(self):
  feed=json.loads(Path('dist/pwa/episodes.json').read_text(encoding='utf-8'))
  self.assertEqual(len({e['id'] for e in feed['episodes']}),len(feed['episodes']))
  for item in feed['episodes']:
   self.assertEqual(set(item['locales']),{'ko','en','ja','es'})
   for value in item['locales'].values():self.assertTrue((Path('dist')/value['url'].lstrip('/')/'index.html').is_file());self.assertTrue(value['title'])
 def test_no_private_assets_or_html_are_precached(self):
  sw=Path('dist/sw.js').read_text(encoding='utf-8');self.assertNotIn('__BASE_JSON__',sw);self.assertNotIn('__VERSION__',sw);self.assertIn("cache:'no-store'",sw)
  self.assertIn('d9-continue-v1',Path('dist/continue-watching.js').read_text(encoding='utf-8'))
