from pathlib import Path
import importlib.util,json,tempfile,unittest

def load(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).parent/'scripts'/f'{name}.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
cf=load('build_cloudflare');pub=load('publish_youtube_snapshot')

class CloudflareBuildTests(unittest.TestCase):
 def test_fixed_origin_and_revision(self):
  base={'SITE_ORIGIN':'https://dra9on-cinema.pages.dev','CF_PAGES_COMMIT_SHA':'a'*40}
  self.assertEqual(cf.configuration(base),('preview',base['SITE_ORIGIN'],'a'*40))
  for origin in ('http://dra9on-cinema.pages.dev','https://evil.pages.dev','https://dra9on-cinema.pages.dev/path','https://user@dra9on-cinema.pages.dev'):
   with self.assertRaises(ValueError):cf.configuration({**base,'SITE_ORIGIN':origin})
  with self.assertRaises(ValueError):cf.configuration({**base,'D9_DEPLOYMENT_STAGE':'production'})
 def test_preview_noindex_feed_revision_and_public_manifest(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp);(out/'pwa').mkdir();(out/'index.html').write_text('<head><meta name="robots" content="index,follow"></head>',encoding='utf-8')
   (out/'pwa/episodes.json').write_text(json.dumps({'revision':'a'*40}),encoding='utf-8')
   cf.finalize(out,'preview','https://dra9on-cinema.pages.dev','a'*40)
   self.assertIn('noindex,nofollow,noarchive',(out/'index.html').read_text())
   self.assertEqual((out/'robots.txt').read_text(),'User-agent: *\nDisallow: /\n')
   self.assertEqual(json.loads((out/'deployment.json').read_text())['revision'],'a'*40)
   with self.assertRaises(ValueError):cf.finalize(out,'preview','https://dra9on-cinema.pages.dev','b'*40)
 def test_reject_unknown_or_other_channel_snapshot(self):
  import youtube_sync as yt
  d={'schemaVersion':1,'status':'ready','fetchedAt':yt.timestamp(yt.utc_now()),'source':'YouTube Data API v3','channel':{'id':'UC'+'a'*22},'videos':{},'seenVideoIds':[],'reviewVideoIds':[]}
  self.assertEqual(pub.public_snapshot(d,d['channel']['id']),d)
  with self.assertRaises(ValueError):pub.public_snapshot({**d,'apiKey':'should-never-publish'},d['channel']['id'])
  with self.assertRaises(ValueError):pub.public_snapshot(d,'UC'+'b'*22)
if __name__=='__main__':unittest.main()
