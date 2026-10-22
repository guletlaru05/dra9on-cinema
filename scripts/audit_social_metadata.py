"""Read rendered public HTML; never execute pages or access private account data."""
from concurrent.futures import ThreadPoolExecutor
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
import argparse,csv,json,re,time

class Metadata(HTMLParser):
 def __init__(self,text):super().__init__();self.meta={};self.canonical='';self.feed(text)
 def handle_starttag(self,tag,pairs):
  a=dict(pairs)
  if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content','')
  if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href','')

def audit(origin,output,routes=None):
 if routes is None:
  import xml.etree.ElementTree as ET
  with urlopen(Request(origin+'/sitemap.xml',headers={'User-Agent':'DRA9ON-deploy-check/1.0'}),timeout=30) as r:sitemap=ET.fromstring(r.read())
  routes=[urlsplit(node.text).path for node in sitemap.iter() if node.tag.endswith('}loc')]
 routes=sorted(set(routes))
 def read(path):
  error=None
  for attempt in range(3):
   try:
    with urlopen(Request(origin+path,headers={'User-Agent':'DRA9ON-OG-audit/1.0','Cache-Control':'no-cache'}),timeout=30) as r:
     page=Metadata(r.read(3_000_000).decode('utf-8'));m=page.meta
     image=m.get('og:image','');default=bool(re.search(r'/assets/og/(?:og-(?:ko|en)\.jpg(?:\?|$)|pages/home-(?:ko|en|ja|es)-)',image))
     return {'page':origin+path,'language':path.split('/')[1] if path.startswith(('/en/','/ja/','/es/')) else 'ko','og:title':m.get('og:title',''),'og:description':m.get('og:description',''),'og:image':image,'twitter:image':m.get('twitter:image',''),'defaultPoster':default,'status':r.status}
   except Exception as ex:error=str(ex);time.sleep(.5*(attempt+1))
  return {'page':origin+path,'error':error}
 with ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(read,routes))
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 (output/'metadata.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 keys=['page','language','og:title','og:description','og:image','twitter:image','defaultPoster','status','error']
 with (output/'metadata.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
 table='<table><thead><tr>'+''.join('<th>'+escape(k)+'</th>' for k in keys)+'</tr></thead><tbody>'
 for row in rows:table+='<tr>'+''.join('<td>'+escape(str(row.get(k,'')))+'</td>' for k in keys)+'</tr>'
 doc='<!doctype html><meta charset="utf-8"><title>OG 메타데이터 점검</title><style>body{font:14px/1.6 system-ui;background:#111;color:#eee}table{border-collapse:collapse}td,th{border:1px solid #444;padding:10px;vertical-align:top;min-width:120px;max-width:480px;overflow-wrap:anywhere}th{position:sticky;top:0;background:#222}</style><h1>공개 페이지 OG 점검</h1>'+table+'</tbody></table>'
 (output/'metadata.html').write_text(doc,encoding='utf-8')
 summary={'pages':len(rows),'defaultPoster':sum(bool(row.get('defaultPoster')) for row in rows),'errors':sum('error' in row for row in rows),'languages':{lang:sum(row.get('language')==lang for row in rows) for lang in ('ko','en','ja','es')}}
 (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');return summary

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--origin',default='https://dra9oncinema.com');p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(audit(a.origin,a.output)))
