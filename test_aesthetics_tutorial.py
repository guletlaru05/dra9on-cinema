"""Image provenance, unabridged prompt, and bilingual publication contracts."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import json,re,unittest
from PIL import Image
from aesthetics_tutorial import PATH

class Content(HTMLParser):
 def __init__(self,source):
  super().__init__();self.inside=False;self.prompts=[];self.current='';self.feed(source)
 def handle_starttag(self,tag,attrs):
  if tag=='code':self.inside=True;self.current=''
 def handle_data(self,text):
  if self.inside:self.current+=text
 def handle_endtag(self,tag):
  if tag=='code':self.inside=False;self.prompts.append(self.current)

class AestheticsLesson(unittest.TestCase):
 def test_prompts_match_records_and_downloads_in_both_languages(self):
  root=Path('dist');assets=root/'assets/tutorials/aesthetics'
  records=json.loads((assets/'generation-manifest.json').read_text(encoding='utf-8'))
  self.assertEqual(len(records),3)
  self.assertEqual([r['model'] for r in records],['midjourney-v8.2','gpt_image_2_5','gpt_image_2_5'])
  for prefix in ('','en/'):
   source=(root/prefix/PATH.strip('/')/'index.html').read_text(encoding='utf-8')
   self.assertEqual(Content(source).prompts,[r['prompt'] for r in records])
   self.assertEqual(source.count('class="aesthetic-prompt-card"'),3)
   self.assertNotIn('<iframe',source)
   for r in records:self.assertEqual((assets/(r['id']+'-prompt.txt')).read_text(encoding='utf-8').rstrip('\n'),r['prompt'])
 def test_images_have_native_proportions_and_no_letterbox_bands(self):
  root=Path('dist/assets/tutorials/aesthetics')
  for record in json.loads((root/'generation-manifest.json').read_text(encoding='utf-8')):
   with Image.open(root/record['file']).convert('RGB') as im:
    self.assertEqual(im.size,(record['width'],record['height']))
    self.assertLess(record['bytes'],150_000)
    for y in (0,im.height-1):
     pixels=im.load();row=[pixels[x,y] for x in range(im.width)]
     self.assertLess(sum(max(pixel)<10 for pixel in row)/len(row),.98)
 def test_preview_links_and_sitemap_include_the_new_article(self):
  for prefix in ('','en/'):
   for route in ('','tutorials/'):
    source=(Path('dist')/prefix/route/'index.html').read_text(encoding='utf-8')
    cards=re.findall(r'class="tutorial-preview" href="([^"]+)"',source)
    self.assertTrue(cards)
    self.assertEqual(cards[0],'/'+prefix+PATH.lstrip('/'))
   sitemap=Path('dist/sitemap.xml').read_text(encoding='utf-8')
   self.assertIn('https://dra9oncinema.com/'+prefix+PATH.lstrip('/'),sitemap)

if __name__=='__main__':unittest.main()
