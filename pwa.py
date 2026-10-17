"""Add installable, network-only public navigation without caching private data."""
from pathlib import Path
from hashlib import sha256
from html import escape
import json, os, re
from datetime import datetime, timezone
from PIL import Image

LANGS=('ko','en','ja','es')
OFFLINE={
 'ko':('연결이 끊겼습니다','인터넷 연결을 확인한 뒤 다시 시도해 주세요. 영상은 인터넷에 연결되어 있어야 재생할 수 있습니다.','다시 연결'),
 'en':('You are offline','Check your internet connection and try again. Videos require an internet connection.','Reconnect'),
 'ja':('インターネットに接続されていません','接続を確認して、もう一度お試しください。動画の再生にはインターネット接続が必要です。','再接続'),
 'es':('Sin conexión','Comprueba tu conexión e inténtalo de nuevo. Los vídeos necesitan conexión a internet.','Volver a conectar')}

def build_pwa(out,origin,works,base_path=''):
 folder=out/'pwa';folder.mkdir(exist_ok=True)
 # Resize the existing brand asset, never synthesize a replacement logo.
 logo=Image.open(out/'assets/press/dra9on-logo-dark-background.png').convert('RGBA')
 alpha=logo.getchannel('A').getbbox()
 if alpha:logo=logo.crop(alpha)
 for size,name in [(192,'icon-192.png'),(512,'icon-512.png'),(512,'icon-maskable-512.png'),(180,'apple-touch-icon.png')]:
  canvas=Image.new('RGBA',(size,size),'#101011');mark=logo.copy();mark.thumbnail((int(size*.74),int(size*.58)),Image.Resampling.LANCZOS)
  canvas.alpha_composite(mark,((size-mark.width)//2,(size-mark.height)//2));canvas.convert('RGB').save(folder/name,optimize=True)
 for lang in LANGS:
  prefix='' if lang=='ko' else '/'+lang
  manifest={'id':base_path+'/', 'name':'DRA9ON CINEMA','short_name':'DRA9ON','lang':lang,'start_url':base_path+prefix+'/', 'scope':base_path+'/', 'display':'standalone','background_color':'#101011','theme_color':'#101011','icons':[{'src':base_path+'/pwa/icon-192.png','sizes':'192x192','type':'image/png','purpose':'any'},{'src':base_path+'/pwa/icon-512.png','sizes':'512x512','type':'image/png','purpose':'any'},{'src':base_path+'/pwa/icon-maskable-512.png','sizes':'512x512','type':'image/png','purpose':'maskable'}]}
  (folder/f'manifest-{lang}.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf-8')
  title,body,button=OFFLINE[lang]
  offline=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#101011"><title>{title} | DRA9ON CINEMA</title><style>body{{margin:0;background:#101011;color:#f4f4f2;font:16px/1.8 system-ui,sans-serif;min-height:100svh;display:grid;place-items:center}}main{{max-width:520px;padding:32px}}strong{{color:#e62143;letter-spacing:2px}}h1{{font-size:clamp(25px,5vw,38px)}}p{{color:#aaaab6}}a{{display:inline-block;background:#f4f4f2;color:#101011;padding:10px 20px;border-radius:4px;text-decoration:none}}</style></head><body><main><strong>DRA9ON CINEMA</strong><h1>{title}</h1><p>{body}</p><a href="{base_path+prefix+'/'}">{button}</a></main></body></html>'''
  (folder/f'offline-{lang}.html').write_text(offline,encoding='utf-8')
 # Keep the push feed limited to released episodic works, in the existing four languages.
 catalogs={}
 for lang in LANGS:
  file=out/('catalog.js' if lang=='ko' else lang+'/catalog.js')
  catalogs[lang]={v['id']:v for v in json.loads(file.read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))}
 now=datetime.now(timezone.utc);episodes=[]
 for work in works:
  if not re.fullmatch(r's[1-9][0-9]*',work['category']):continue
  if work.get('releaseAt') and datetime.fromisoformat(work['releaseAt'].replace('Z','+00:00'))>now:continue
  if work.get('uploadDate') and datetime.fromisoformat(work['uploadDate'].replace('Z','+00:00'))>now:continue
  episodes.append({'id':work['id'],'season':work['season'],'episode':work['episode'],'publishedAt':work.get('releaseAt') or work['uploadDate'], 'image':work['image'],'locales':{lang:{'title':catalogs[lang][work['id']]['name'],'url':catalogs[lang][work['id']]['path']} for lang in LANGS}})
 (folder/'episodes.json').write_text(json.dumps({'revision':os.getenv('GITHUB_SHA','local'),'generatedAt':now.isoformat(),'episodes':episodes},ensure_ascii=False),encoding='utf-8')
 template=(out/'service-worker-template.js').read_text(encoding='utf-8')
 version=sha256((template+''.join((folder/f'offline-{lang}.html').read_text(encoding='utf-8') for lang in LANGS)).encode()).hexdigest()[:16]
 (out/'sw.js').write_text(template.replace('__BASE_JSON__',json.dumps(base_path)).replace('__VERSION__',version),encoding='utf-8')
 (out/'service-worker-template.js').unlink()
 asset_version=sha256((out/'pwa.js').read_bytes()+(out/'pwa.css').read_bytes()).hexdigest()[:12]
 for file in out.rglob('*.html'):
  if file.parent==folder:continue
  path=file.relative_to(out).as_posix();lang=path.split('/')[0];lang=lang if lang in LANGS else 'ko'
  source=file.read_text(encoding='utf-8')
  source=source.replace('</head>',f'<link rel="manifest" href="{base_path}/pwa/manifest-{lang}.webmanifest"><meta name="theme-color" content="#101011"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black"><meta name="apple-mobile-web-app-title" content="DRA9ON"><link rel="apple-touch-icon" sizes="180x180" href="{base_path}/pwa/apple-touch-icon.png"><link rel="stylesheet" href="{base_path}/pwa.css?v={asset_version}"><script src="{base_path}/pwa.js?v={asset_version}" data-pwa-base="{escape(base_path,quote=True)}" defer></script></head>',1)
  file.write_text(source,encoding='utf-8')
