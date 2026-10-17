"""Index only already-public tutorial HTML; never opens a private corpus."""
from html.parser import HTMLParser
from pathlib import Path
import json,re

class PublicArticle(HTMLParser):
 def __init__(self,text):
  super().__init__();self.main=False;self.h1=False;self.pre=False;self.hidden=0;self.text=[];self.title='';self.prompts=[];self.prompt='';self.feed(text)
 def handle_starttag(self,tag,attrs):
  if tag=='main':self.main=True
  if tag in ('script','style'):self.hidden+=1
  if self.main and tag=='h1':self.h1=True
  if self.main and tag=='pre':self.pre=True;self.prompt=''
 def handle_data(self,text):
  if not self.main or self.hidden:return
  if self.h1:self.title+=text
  if self.pre:self.prompt+=text
  self.text.append(text)
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
  if tag=='h1':self.h1=False
  if tag=='pre' and self.pre:self.prompts.append(self.prompt);self.pre=False
  if tag=='main':self.main=False

def build_reference_index(out,origin):
 documents=[]
 for language,prefix in [('ko',''),('en','/en')]:
  for path in sorted((out/(prefix.strip('/')+'/tutorials').lstrip('/')).glob('*/index.html')):
   parser=PublicArticle(path.read_text(encoding='utf-8'))
   if not parser.title:continue
   body='\n'.join(parser.text)
   documents.append({'id':'tutorial:'+path.parent.name+':'+language,'title':parser.title,'language':language,'url':origin+prefix+'/tutorials/'+path.parent.name+'/','source_type':'내 튜토리얼','body':body,'prompts':parser.prompts,'tags':[tag for tag,pattern in [('카메라',r'구도|카메라|camera|framing'),('조명',r'조명|명암|lighting'),('캐릭터 일관성',r'캐릭터|일관성|character|identity'),('액션',r'액션|추격|전투|action|chase'),('분위기',r'분위기|미감|색감|cinematic|texture')] if re.search(pattern,body,re.I)]})
 (out/'tutorial-reference-index.json').write_text(json.dumps({'version':1,'scope':'public tutorials only','documents':documents},ensure_ascii=False),encoding='utf-8')
 return len(documents)
