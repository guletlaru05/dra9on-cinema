"""Read public preview pages/assets from CI; never mutate board or private data."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import json
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'dist'
HOST='https://dra9on-cinema.pages.dev'
STAGE='preview'

class SocialMeta(HTMLParser):
 def __init__(self,text):
  super().__init__();self.values={};self.feed(text)
 def handle_starttag(self,tag,pairs):
  attrs=dict(pairs)
  if tag=='meta':self.values[attrs.get('property',attrs.get('name'))]=attrs.get('content','')

def check_once(file):
 rel=file.relative_to(SITE).as_posix()
 path='/'+rel.removesuffix('index.html') if rel.endswith('index.html') else '/'+rel
 method='GET' if file.suffix=='.html' else 'HEAD'
 result={'path':path,'method':method}
 try:
  with urlopen(Request(HOST+path,method=method,headers={'User-Agent':'DRA9ON-deploy-check/1.0'}),timeout=30) as response:
   result.update(status=response.status,url=response.geturl(),cacheControl=response.headers.get('Cache-Control'))
   if path.startswith(('/assets/build/','/assets/optimized/','/assets/fonts/','/assets/og/pages/','/assets/hero/')) and 'max-age=31536000' not in (response.headers.get('Cache-Control') or ''):raise ValueError('Missing long-lived versioned asset cache header')
   if file.suffix=='.html':
    text=response.read(2_000_000).decode('utf-8')
    if STAGE=='preview' and 'noindex,nofollow,noarchive' not in text:raise ValueError('Preview is indexable')
    if 'Content-Security-Policy' not in text:raise ValueError('Existing CSP missing')
    if response.headers.get('X-Content-Type-Options')!='nosniff':raise ValueError('Missing nosniff header')
    if not response.headers.get('Strict-Transport-Security'):raise ValueError('Missing HSTS header')
    if response.headers.get('X-Frame-Options') not in ('DENY','SAMEORIGIN'):raise ValueError('Missing clickjacking protection')
    expected=SocialMeta(file.read_text(encoding='utf-8')).values
    if '/assets/og/pages/' in expected.get('og:image',''):
     actual=SocialMeta(text).values
     for key in ('og:image','twitter:image','og:title','og:description','twitter:card'):
      if actual.get(key)!=expected.get(key):raise ValueError('Live social metadata differs from this build: '+key)
     result['ogImage']=actual['og:image']
 except HTTPError as error:
  result.update(status=error.code)
  if path!='/404.html':result['error']='HTTP '+str(error.code)
 except Exception as error:result['error']=str(error)
 return result

def check(file):
 # A single reset must not fail an otherwise healthy CDN deployment.
 for attempt in range(3):
  result=check_once(file)
  transient=result.get('error') and result.get('status') in (None,429,502,503,504)
  if not transient or attempt==2:return result
  sleep(attempt+1)

def main():
 global HOST,STAGE
 record=json.loads((SITE/'deployment.json').read_text());STAGE=record['stage'];HOST=record['origin']
 if (STAGE,HOST) not in [('preview','https://dra9on-cinema.pages.dev'),('production','https://dra9oncinema.com')]:raise ValueError('Unapproved verification origin')
 # Advanced-mode Worker and routing configuration are deployment inputs, not public files.
 files=[p for p in SITE.rglob('*') if p.is_file() and p.name not in ('_worker.js','_routes.json','_headers')]
 if not files:raise ValueError('Build first')
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,files))
 errors=[r for r in rows if r.get('error')]
 report={'checked':len(rows),'html':sum(p.suffix=='.html' for p in files),'errors':errors,'files':rows,'privateDataRead':False,'postsWritten':False,'notificationsSent':False}
 destination=ROOT/'.cache/preview-live-verification.json';destination.parent.mkdir(exist_ok=True)
 destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'checked':len(rows),'html':report['html'],'errorCount':len(errors),'firstErrors':errors[:10]},ensure_ascii=False))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
