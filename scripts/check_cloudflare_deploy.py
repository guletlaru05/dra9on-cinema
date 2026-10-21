"""Read-only deployment revision gate; never dispatch a notification."""
from pathlib import Path
import argparse,json,re,time
from urllib.request import Request,urlopen
HOST='https://dra9on-cinema.pages.dev'

def read(path):
 with urlopen(Request(HOST+path,headers={'Cache-Control':'no-cache','User-Agent':'DRA9ON-deploy-check/1.0'}),timeout=20) as response:
  if response.geturl().split('?',1)[0]!=HOST+path.split('?',1)[0]:raise ValueError('Unexpected redirect')
  return json.loads(response.read(1_000_000).decode('utf-8'))

def check(revision,attempts=1):
 if not re.fullmatch('[a-f0-9]{40}',revision):raise ValueError('Invalid expected revision')
 for attempt in range(attempts):
  try:
   deployment=read('/deployment.json?revision='+revision)
   feed=read('/pwa/episodes.json?revision='+revision)
   if deployment.get('revision')==revision and feed.get('revision')==revision:
    origins={'preview':HOST,'production':'https://dra9oncinema.com'}
    if deployment.get('origin')!=origins.get(deployment.get('stage')):raise ValueError('Not an approved deployment origin')
    if not isinstance(feed.get('episodes'),list) or not feed['episodes']:raise ValueError('Missing episode feed')
    if any(set(e.get('locales',{}))!={'ko','en','ja','es'} for e in feed['episodes']):raise ValueError('Missing language in episode feed')
    return {'revision':revision,'pages':deployment.get('htmlPages'),'episodes':len(feed['episodes']),'notificationDispatch':False}
  except (OSError,ValueError):
   if attempt+1==attempts:raise
  if attempt+1<attempts:time.sleep(15)
 raise RuntimeError('Cloudflare revision is not visible yet')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('revision');p.add_argument('--attempts',type=int,default=1);a=p.parse_args()
 if not 1<=a.attempts<=20:raise ValueError('Attempts must be bounded')
 print(json.dumps(check(a.revision,a.attempts)))
