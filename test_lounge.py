import json,os,re,unittest
from pathlib import Path
from unittest.mock import patch
import lounge
class LoungeTests(unittest.TestCase):
 def test_pending_review_cannot_publish(self):
  with patch.dict(os.environ,{},clear=True),patch.object(lounge.json,'loads',return_value={'approved_for_publication':False}):
   self.assertFalse(lounge.enabled());self.assertEqual(lounge.new_routes(),[])
 def test_all_languages_preserve_board_forms_and_redirect(self):
  root=Path('dist-lounge-preview')
  if not root.exists():self.skipTest('Build the private lounge preview first')
  for lang in ('ko','en','ja','es'):
   pre='' if lang=='ko' else lang+'/'
   doc=(root/pre/'lounge/index.html').read_text(encoding='utf-8')
   self.assertEqual(doc.count('id="board-form"'),1)
   for id in ('characters','events','board','ask','board-owner-panel','board-notify-on','board-filter','board-topic'):self.assertIn('id="'+id+'"',doc)
   self.assertEqual(doc.count('value="character"'),2)
   for attr in ('maxlength="24"','maxlength="120"','maxlength="3000"'):self.assertIn(attr,doc)
   self.assertNotIn('type="password"',doc)
   old=(root/pre/'questions/index.html').read_text(encoding='utf-8');self.assertIn('/lounge/#board',old);self.assertIn('lounge-redirect.js',old);self.assertNotIn('community.js',old)
   for p in lounge.PEOPLE:
    char=(root/pre/('fall-707/characters/'+p['slug']+'/index.html')).read_text(encoding='utf-8')
    self.assertIn('topic=character&amp;character='+p['slug']+'#ask',char)
    self.assertIn('hreflang="es"',char)
    self.assertIn('noindex,nofollow,noarchive',char)
 def test_approved_images_use_owner_season_two_sources(self):
  manifest=json.loads(Path('character_evidence.json').read_text(encoding='utf-8'))
  for person in manifest.values():
   for frame in person['frames']:
    self.assertEqual(frame['season'],2)
    self.assertTrue((Path('site-assets/assets/characters')/frame['file']).is_file())
    self.assertNotIn('candidate',frame)
    self.assertEqual(frame['channel_id'],'UCEZSQzQw7lIy2DBbojztyqg')
    self.assertIn('youtube.com/watch?v=',frame['source_url'])
  self.assertEqual(len(manifest['hyeolmaek']['frames']),0,'Never use Yuna as a substitute for her master')
 def test_no_database_migration_or_visitor_push_subscription(self):
  source=Path('site-assets/community.js').read_text(encoding='utf-8')
  self.assertIn("collection(db,'communityPosts')",source)
  self.assertIn("collection(db,'communityArchive')",source)
  worker=Path('workers/episode-push/src/board.mjs').read_text(encoding='utf-8')
  self.assertNotIn('FROM push_subscriptions',worker)
  self.assertIn("p.firebase?.sign_in_provider==='google.com'",worker)
  rules=Path('firestore.rules').read_text(encoding='utf-8')
  for invariant in ["duration.value(10,'m')","allow update: if libraryOwner()","d.body.size() <= 3000","d.answer.size() <= 5000"]:self.assertIn(invariant,rules)
if __name__=='__main__':unittest.main()
