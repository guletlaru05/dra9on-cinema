"""Ensure every translated listing has the same complete browsing metadata."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from tutorial_catalog import COPY, CATEGORIES, LESSONS

class Listing(HTMLParser):
 def __init__(self, source):
  super().__init__(); self.cards=[]; self.topics=[]; self.sorts=[]; self.feed(source)
 def handle_starttag(self, tag, attrs):
  attrs=dict(attrs)
  if tag=='a' and attrs.get('class')=='tutorial-preview': self.cards.append(attrs)
  if 'data-topic' in attrs:self.topics.append(attrs['data-topic'])
  if 'data-tutorial-sort' in attrs:self.sorts.append(attrs['data-tutorial-sort'])

class Catalog(unittest.TestCase):
 def test_all_languages_have_working_filter_contract_without_removing_articles(self):
  for lang,words in COPY.items():
   source=(Path('dist')/('' if lang=='ko' else lang)/'tutorials/index.html').read_text(encoding='utf-8')
   doc=Listing(source)
   self.assertEqual(len(doc.cards),len(LESSONS))
   self.assertEqual(doc.topics,list(CATEGORIES));self.assertEqual(doc.sorts,['latest','popular'])
   self.assertNotIn('class="tutorial-topics"',source)
   self.assertIn('<h1>'+words[0]+'</h1>',source)
   self.assertEqual(source.count('data-tutorial-list'),1)
   for card in doc.cards:
    slug=card['href'].rstrip('/').split('/')[-1]
    self.assertEqual(card['data-topics'].split(),LESSONS[slug][0])
    self.assertNotIn('hidden',card)
   self.assertIn('data-tutorial-browser hidden',source) # progressive enhancement

if __name__=='__main__':unittest.main()
