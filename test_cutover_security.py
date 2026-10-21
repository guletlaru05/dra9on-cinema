from pathlib import Path
from html.parser import HTMLParser
import json,unittest
OUT=Path(__file__).resolve().parent/'dist'
class Meta(HTMLParser):
 def __init__(self,text):super().__init__();self.policy='';self.feed(text)
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy':self.policy=attrs['content']
class CutoverSecurityTests(unittest.TestCase):
 def test_private_metrics_not_dependent_on_analytics(self):
  library=Meta((OUT/'library/index.html').read_text(encoding='utf-8')).policy
  connect=next(s for s in library.split(';') if s.strip().startswith('connect-src '))
  self.assertIn('https://dra9on-tutorial-metrics.tutorial-metrics.workers.dev',connect)
  self.assertIn('https://firestore.googleapis.com',connect)
 def test_static_security_headers_and_preserved_csp(self):
  headers=(OUT/'_headers').read_text();self.assertIn('Strict-Transport-Security: max-age=31536000',headers)
  for name in ('X-Frame-Options: DENY','X-Content-Type-Options: nosniff','Referrer-Policy: strict-origin-when-cross-origin','Permissions-Policy: camera=()'):self.assertIn(name,headers)
  for file in ('index.html','library/index.html','watch/fall-707-s3-ep2/index.html'):
   policy=Meta((OUT/file).read_text(encoding='utf-8')).policy
   self.assertIn("default-src 'self'",policy);self.assertIn('https://www.youtube-nocookie.com',policy)
 def test_helper_origin_tracks_actual_deployment(self):
  origin=json.loads((OUT/'deployment.json').read_text())['origin'];host=origin.split('://')[1]
  self.assertIn('authDomain:"'+host+'"',(OUT/'library/library.js').read_text(encoding='utf-8'))
  self.assertIn('frame-src '+origin+'/__/auth/',Meta((OUT/'library/index.html').read_text(encoding='utf-8')).policy)
  routes=json.loads((OUT/'_routes.json').read_text());self.assertEqual(routes['include'],['/__/auth/*','/__/firebase/init.json'])
if __name__=='__main__':unittest.main()
