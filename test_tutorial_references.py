import tempfile,unittest,json
from pathlib import Path
from tutorial_references import build_reference_index
class PublicReferenceTests(unittest.TestCase):
 def test_only_public_html_and_exact_pre_text(self):
  temporary=Path(__file__).parent/'.cache'/'tests';temporary.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=temporary) as folder:
   root=Path(folder);article=root/'tutorials/example/index.html';article.parent.mkdir(parents=True)
   article.write_text('<main><h1>공개 튜토리얼</h1><pre>  first\n&lt;camera&gt; &amp; light\n\nlast  </pre></main>',encoding='utf-8')
   private=root/'library/private.json';private.parent.mkdir();private.write_text('{"SECRET":"never public"}')
   self.assertEqual(build_reference_index(root,'https://dra9oncinema.com'),1)
   value=json.loads((root/'tutorial-reference-index.json').read_text(encoding='utf-8'))
   self.assertEqual(value['documents'][0]['prompts'][0],'  first\n<camera> & light\n\nlast  ')
   self.assertNotIn('SECRET',str(value));self.assertEqual(value['documents'][0]['source_type'],'내 튜토리얼')
if __name__=='__main__':unittest.main()
