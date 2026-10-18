"""Publication contracts: original prompts, actual provenance and four languages."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,unittest
from PIL import Image
from lighting_tutorial import PATH
from lighting_content import COPY

class Article(HTMLParser):
 def __init__(self,source):
  super().__init__();self.prompts=[];self.current=None;self.images=[];self.feed(source)
 def handle_starttag(self,tag,attrs):
  if tag=='code':self.current=''
  if tag=='img':self.images.append(dict(attrs))
 def handle_data(self,text):
  if self.current is not None:self.current+=text
 def handle_endtag(self,tag):
  if tag=='code' and self.current is not None:self.prompts.append(self.current);self.current=None

class LightingLesson(unittest.TestCase):
 def test_complete_prompts_and_actual_model_are_preserved_in_four_languages(self):
  root=Path('dist');assets=root/'assets/tutorials/lighting-contrast'
  records=json.loads((assets/'generation-manifest.json').read_text(encoding='utf-8'))
  self.assertEqual(len(records),10)
  expected=[records[i]['prompt']for i in [0,1,2,3,1,4,5,6,7,8,9]]
  self.assertEqual(records[5]['model'],'Nano Banana 2');self.assertEqual(records[5]['requested_model'],'Nano Banana Pro')
  self.assertEqual({r['parameters']['seed']for r in records[6:]},{20261018})
  for lang in COPY:
   prefix='' if lang=='ko' else lang+'/'
   source=(root/prefix/PATH.strip('/')/'index.html').read_text(encoding='utf-8');article=Article(source)
   self.assertIn('<html lang="'+lang+'">',source);self.assertEqual(article.prompts,expected)
   self.assertIn(COPY[lang]['title'],source)
   for language in COPY:self.assertIn('hreflang="'+language+'"',source)
   for image in article.images:
    if 'lighting-contrast' in image['src']:self.assertTrue(any(model in image['alt'] for model in ['GPT Image 2.5','Seedream 5.0 Pro','Nano Banana 2','Midjourney v8.2']))
   if lang!='ko':self.assertFalse(re.search('[가-힣]',source.replace('aria-label="한국어"','')),'Unexpected Korean in '+lang)
  for record in records:
   self.assertEqual((assets/(record['id']+'-prompt.txt')).read_text(encoding='utf-8'),record['prompt'])
   with Image.open(assets/record['file'])as image:self.assertEqual(image.size,(record['width'],record['height']))
   self.assertLess(record['bytes'],180000)
 def test_all_language_home_lists_sitemap_and_numeric_registry(self):
  root=Path('dist');sitemap=(root/'sitemap.xml').read_text(encoding='utf-8')
  for lang in COPY:
   prefix='' if lang=='ko' else lang+'/'
   for suffix in ['', 'tutorials/']:
    source=(root/prefix/suffix/'index.html').read_text(encoding='utf-8')
    first=re.findall(r'class="tutorial-preview" href="([^"]+)"',source)[0]
    self.assertEqual(first,'/'+prefix+PATH.lstrip('/'))
   self.assertIn('https://dra9oncinema.com/'+prefix+PATH.lstrip('/'),sitemap)

if __name__=='__main__':unittest.main()
