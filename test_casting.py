from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import unittest
import casting
from actors_content import ACTORS

class Forms(HTMLParser):
 def __init__(self,text):super().__init__();self.fields={};self.hrefs=[];self.feed(text)
 def handle_starttag(self,tag,pairs):
  attrs=dict(pairs)
  if tag in ('input','select','textarea'):self.fields[attrs.get('name')]=attrs
  if tag=='a':self.hrefs.append(attrs.get('href'))

class CastingTests(unittest.TestCase):
 def test_all_actors_all_existing_languages_have_same_required_fields(self):
  for actor in ACTORS:
   for lang in ('ko','en','ja','es'):
    top,bottom=casting.render(actor,lang)
    self.assertIn(casting.COPY['cta'][lang],unescape(top))
    self.assertIn(casting.COPY['note'][lang],top)
    parser=Forms(bottom)
    for name in ('company','contact','email','actor','purpose','message','consent'):self.assertIn('required',parser.fields[name])
    self.assertIn('value="'+actor['slug']+'" selected',bottom)
    self.assertIn(('/privacy/' if lang=='ko' else '/en/privacy/'),parser.hrefs)
    self.assertNotIn('TURNSTILE_SECRET',bottom)
 def test_live_output_form_and_security_origins_are_limited_to_actor_profiles(self):
  root=Path(__file__).resolve().parent/'dist'
  for lang in ('','en','ja','es'):
   doc=(root/lang/'actors/min-seoa/index.html').read_text(encoding='utf-8')
   self.assertIn('id="casting-dialog"',doc)
   self.assertIn('data-casting-form',doc)
   self.assertIn('https://challenges.cloudflare.com',doc)
   self.assertIn(casting.configuration()['endpoint'].rsplit('/',1)[0],doc)
   home=(root/lang/'index.html').read_text(encoding='utf-8')
   self.assertNotIn('https://challenges.cloudflare.com',home)
  self.assertNotIn('https://dra9on-casting', (root/'library/index.html').read_text(encoding='utf-8'))
