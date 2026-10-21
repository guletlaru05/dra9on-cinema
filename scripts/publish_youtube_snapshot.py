"""Publish only validated public YouTube metadata, never the cache directory."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import youtube_sync as yt
TOP={'schemaVersion','status','fetchedAt','source','channel','videos','seenVideoIds','discoveryComplete','reviewVideoIds','requestsUsed'}
CHANNEL={'id','handle','title','subscriberCount','hiddenSubscriberCount'}
VIDEO={'id','title','description','uploadDate','thumbnail','seconds','duration','isEmbeddable','apiViewCount','season','episode','category','nameEn','summaryEn'}

def public_snapshot(data,channel_id):
 if not isinstance(data,dict) or not yt.fresh_snapshot(data):raise ValueError('A fresh successful official snapshot is required')
 if data.get('source')!='YouTube Data API v3' or data.get('channel',{}).get('id')!=channel_id:raise ValueError('Snapshot belongs to another source or channel')
 if set(data)-TOP or set(data['channel'])-CHANNEL:raise ValueError('Unknown fields cannot be published')
 if not isinstance(data.get('videos'),dict) or len(data['videos'])>1000:raise ValueError('Invalid public video collection')
 for key,row in data['videos'].items():
  if set(row)-VIDEO or not yt.VIDEO_ID.fullmatch(key) or row.get('id')!=key or row.get('isEmbeddable') is not True:raise ValueError('Invalid or unexpected public video fields')
  if row.get('apiViewCount') is not None and yt.exact_count(row['apiViewCount']) is None:raise ValueError('Invalid count')
 for field in ('seenVideoIds','reviewVideoIds'):
  if not isinstance(data.get(field),list) or len(data[field])>10000 or any(not yt.VIDEO_ID.fullmatch(v) for v in data[field]):raise ValueError('Invalid discovery ids')
 return data

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--output',type=Path,default=ROOT/'build-assets/youtube-public.json');a=p.parse_args()
 config=yt.load_config()
 data=public_snapshot(json.loads(a.source.read_text(encoding='utf-8')),config['channelId'])
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 print('Validated public YouTube snapshot:',len(data['videos']),'videos')
if __name__=='__main__':main()
