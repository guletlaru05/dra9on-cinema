from pathlib import Path
import importlib.util,tempfile,unittest
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('preview_login',ROOT/'scripts/preview_login.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
class PreviewLoginTests(unittest.TestCase):
 def fixture(self,out):
  (out/'library').mkdir()
  for name in ('library.js','index.html'):(out/'library'/name).write_bytes((ROOT/'site-assets/library'/name).read_bytes())
  index=out/'library/index.html';index.write_text(index.read_text(encoding='utf-8').replace('<head>','<head><meta http-equiv="Content-Security-Policy" content="frame-src https://www.google.com/recaptcha/">'),encoding='utf-8')
  (out/'engagement-config.js').write_bytes((ROOT/'site-assets/engagement-config.js').read_bytes())
 def test_production_is_byte_identical(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp);self.fixture(out);before={p.relative_to(out):p.read_bytes() for p in out.rglob('*') if p.is_file()}
   preview.configure(out,'production')
   self.assertEqual(before,{p.relative_to(out):p.read_bytes() for p in out.rglob('*') if p.is_file()})
 def test_preview_uses_same_origin_and_keeps_owner_load(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp);self.fixture(out);preview.configure(out,'preview')
   self.assertEqual((out/'engagement-config.js').read_bytes(),(ROOT/'site-assets/engagement-config.js').read_bytes())
   code=(out/'library/library.js').read_text(encoding='utf-8');self.assertIn('previewLogin.restore()',code)
   self.assertIn('authDomain:"dra9on-cinema.pages.dev"',code)
   source=(ROOT/'site-assets/library/library.js').read_text(encoding='utf-8')
   # The complete owner/Firestore loader is preserved, including verified-Google check.
   self.assertEqual(code[code.index(' async function load(user)'):code.index(' $("retry-load")')],source[source.index(' async function load(user)'):source.index(' $("retry-load")')])
   self.assertTrue((out/'_worker.js').is_file());self.assertIn('login-bootstrap.js',(out/'library/index.html').read_text(encoding='utf-8'))
   import json
   public=json.loads((out/'__/firebase/init.json').read_text());self.assertEqual(set(public),{'apiKey','projectId','appId','authDomain'})
if __name__=='__main__':unittest.main()
