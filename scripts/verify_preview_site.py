"""Read public preview pages/assets from CI; never mutate board or private data."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
import json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'dist'
HOST='https://dra9on-cinema.pages.dev'

def check(file):
 rel=file.relative_to(SITE).as_posix()
 path='/'+rel.removesuffix('index.html') if rel.endswith('index.html') else '/'+rel
 method='GET' if file.suffix=='.html' else 'HEAD'
 result={'path':path,'method':method}
 try:
  with urlopen(Request(HOST+path,method=method,headers={'User-Agent':'DRA9ON-deploy-check/1.0'}),timeout=30) as response:
   result.update(status=response.status,url=response.geturl())
   if file.suffix=='.html':
    text=response.read(2_000_000).decode('utf-8')
    if 'noindex,nofollow,noarchive' not in text:raise ValueError('Preview is indexable')
    if 'Content-Security-Policy' not in text:raise ValueError('Existing CSP missing')
 except HTTPError as error:
  result.update(status=error.code)
  if path!='/404.html':result['error']='HTTP '+str(error.code)
 except Exception as error:result['error']=str(error)
 return result

def main():
 files=[p for p in SITE.rglob('*') if p.is_file()]
 if not files:raise ValueError('Build first')
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,files))
 errors=[r for r in rows if r.get('error')]
 report={'checked':len(rows),'html':sum(p.suffix=='.html' for p in files),'errors':errors,'files':rows,'privateDataRead':False,'postsWritten':False,'notificationsSent':False}
 destination=ROOT/'.cache/preview-live-verification.json';destination.parent.mkdir(exist_ok=True)
 destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'checked':len(rows),'html':report['html'],'errorCount':len(errors),'firstErrors':errors[:10]},ensure_ascii=False))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
