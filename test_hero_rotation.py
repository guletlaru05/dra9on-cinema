from pathlib import Path
import json,re,unittest
from PIL import Image
ROOT=Path(__file__).resolve().parent
class WorkHeroTests(unittest.TestCase):
 def test_approved_five_work_order_and_four_localized_homes(self):
  config=json.loads((ROOT/'hero_rotation_config.json').read_text(encoding='utf-8'))
  self.assertTrue(config['approved']);self.assertEqual(config['approvedOrder'],['01-min-current','02-s2','03-s1','04-immortal','05-actors'])
  for lang in ('','en','ja','es'):
   text=(ROOT/'dist'/lang/'index.html').read_text(encoding='utf-8')
   self.assertIn('data-work-hero',text);self.assertNotIn('data-hero-next',text)
   payload=json.loads(re.search(r'<script type="application/json" data-work-hero-config>(.*?)</script>',text,re.S)[1])
   self.assertEqual([s['id'] for s in payload['slides']],config['approvedOrder'])
   self.assertEqual(text.count('role="tab"'),5);self.assertIn('role="tabpanel"',text)
   self.assertIn('/actors/min-seoa/?casting=1#casting-inquiry',text)
   for s in payload['slides']:
    self.assertTrue(s['title'] and s['description'] and s['tab']);self.assertEqual(s['duration'],8)
    self.assertTrue((ROOT/'dist'/s['url'].lstrip('/')/'index.html').is_file())
    self.assertEqual(set(s['focus']),{'desktop','mobile'})
   self.assertNotRegex(text,r'<video[^>]*\ssrc=')
 def test_versioned_web_media_and_posters_have_bounded_size(self):
  config=json.loads((ROOT/'hero_rotation_config.json').read_text(encoding='utf-8'))
  for clip in config['clips']:
   for kind,name in clip['files'].items():
    self.assertRegex(name,r'\.[a-f0-9]{12}\.(?:mp4|webm|jpg|webp)$')
    file=ROOT/'site-assets/assets/hero'/name;self.assertLess(file.stat().st_size,1_000_000 if kind in ('mobile','poster','mobilePoster') else 5_000_000)
    if kind=='poster':
     with Image.open(file) as im:self.assertEqual(im.size,tuple(clip.get('dimensions',{'desktop':[960,540]})['desktop']))
