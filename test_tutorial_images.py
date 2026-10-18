"""Every published lesson gets one translated, dismissible modal."""
from pathlib import Path
import re
import unittest
from tutorial_images import COPY

class TutorialImages(unittest.TestCase):
 def test_all_public_lessons_share_one_localized_viewer(self):
  pages=0
  for page in Path('dist').rglob('index.html'):
   path='/'+page.relative_to('dist').as_posix().removesuffix('index.html')
   canonical=re.sub(r'^/(en|ja|es)(?=/)','',path)
   if not canonical.startswith('/tutorials/'):continue
   source=page.read_text(encoding='utf-8')
   if canonical=='/tutorials/':
    self.assertNotIn('data-tutorial-image-viewer',source);continue
   lang=path.split('/')[1] if path.startswith(('/en/','/ja/','/es/')) else 'ko'
   title,close,original,error=COPY[lang]
   self.assertEqual(source.count('data-tutorial-image-viewer'),1)
   self.assertIn('data-image-close autofocus>'+close,source)
   self.assertIn('aria-labelledby="tutorial-image-title"',source)
   self.assertIn(original,source);self.assertIn(error,source)
   self.assertRegex(source,r'/assets/build/tutorial-images\.[a-f0-9]+\.js')
   pages+=1
  self.assertEqual(pages,22)

if __name__=='__main__':unittest.main()
