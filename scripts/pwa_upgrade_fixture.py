"""Disposable localhost-only UI for testing the real SW upgrade lifecycle.

No real accounts, notification subscriptions or production browser data are used.
Open /control, install the old worker, then apply the new one through its buttons.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, subprocess, base64, sys

ROOT=Path(__file__).resolve().parents[1]
STATE={'version':1,'offline':False,'navigations':0}
OLD=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'show','c1d2a77:site-assets/service-worker-template.js'],cwd=ROOT).decode()
NEW=(ROOT/'site-assets/service-worker-template.js').read_text(encoding='utf-8')
PAGE='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>PWA 구버전 전환 검증</title>
<style>body{background:#101011;color:#eee;font:16px/1.7 system-ui;max-width:1000px;margin:30px auto;padding:20px}button,a{padding:10px;margin:6px;color:inherit;background:#303038}pre{white-space:pre-wrap;background:#202025;padding:20px}h1{color:#ed233a}</style>
<h1>PWA 구버전 → 새 버전 복구 검증</h1><p>로컬 테스트 전용 · 로그인/구독은 합성 보존 표식입니다.</p>
<button id="install">1. 구버전 설치와 오래된 캐시 준비</button><button id="upgrade">2. 새 버전 적용</button>
<button id="check">보존 상태 확인</button><button id="offline">네트워크 장애 재현</button><button id="online">네트워크 복원</button>
<a href="/">홈 열기</a><pre id="status">확인 중…</pre>
<script>
const loads=Number(sessionStorage.getItem('fixture-loads')||0)+1;sessionStorage.setItem('fixture-loads',loads);
const status=document.querySelector('#status');
const db=()=>new Promise((resolve,reject)=>{const r=indexedDB.open('synthetic-auth-preservation',1);r.onupgradeneeded=()=>r.result.createObjectStore('auth');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
async function auth(write=false){const d=await db();return new Promise((resolve,reject)=>{const t=d.transaction('auth',write?'readwrite':'readonly'),s=t.objectStore('auth'),r=write?s.put('synthetic-signed-in','owner'):s.get('owner');r.onsuccess=()=>resolve(write?'synthetic-signed-in':r.result);r.onerror=()=>reject(r.error);t.oncomplete=()=>d.close();});}
async function snapshot(){const data={pageLoads:loads,controller:!!navigator.serviceWorker.controller,cacheNames:await caches.keys(),localStorage:localStorage.getItem('fixture-resume'),authIndexedDB:await auth(),cookie:document.cookie.includes('fixture-session=preserved'),browser:navigator.userAgent};status.textContent=JSON.stringify(data,null,2);}
document.querySelector('#install').onclick=async()=>{try{await fetch('/release/1',{method:'POST'});localStorage.setItem('fixture-resume','resume-preserved');document.cookie='fixture-session=preserved; SameSite=Lax; path=/';await auth(true);await navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'});await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));const c=await caches.open('dra9on-pwa-contaminated');for(const path of ['/', 'https://dra9on-cinema.pages.dev/old.js','https://guletlaru05.github.io/dra9on-cinema/old.js'])await c.put(path,new Response('obsolete fixture data'));await caches.open('unrelated-keep');await snapshot();}catch(e){status.textContent=String(e);}};
document.querySelector('#upgrade').onclick=async()=>{try{await fetch('/release/2',{method:'POST'});const r=await navigator.serviceWorker.getRegistration();await r.update();await snapshot();}catch(e){status.textContent=String(e);}};
document.querySelector('#check').onclick=snapshot;
document.querySelector('#offline').onclick=async()=>{await fetch('/offline/1',{method:'POST'});status.textContent='장애 모드: 홈 열기를 누르세요.';};
document.querySelector('#online').onclick=async()=>{await fetch('/offline/0',{method:'POST'});await snapshot();};
snapshot();
</script></html>'''

class Handler(BaseHTTPRequestHandler):
 def send(self,data,kind='text/html; charset=utf-8'):
  if isinstance(data,str):data=data.encode()
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.path.startswith('/release/'):STATE['version']=int(self.path[-1])
  if self.path.startswith('/offline/'):STATE['offline']=self.path[-1]=='1'
  self.send(json.dumps(STATE),'application/json')
 def do_GET(self):
  if self.path.startswith('/control'):return self.send(PAGE)
  if self.path=='/sw.js':return self.send((OLD if STATE['version']==1 else NEW).replace('__BASE_JSON__','""').replace('__VERSION__','fixture-v'+str(STATE['version'])),'application/javascript')
  if self.path.startswith('/pwa/offline-'):return self.send('<h1>오프라인 복구 화면</h1><p>개인 자료와 오래된 HTML을 노출하지 않습니다.</p><a href="/control">검증 화면 돌아가기</a>')
  if self.path.startswith('/pwa/icon-'):return self.send(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jk1cAAAAASUVORK5CYII='),'image/png')
  if self.path=='/':
   if STATE['offline']:self.close_connection=True;return
   STATE['navigations']+=1;return self.send('<h1>최신 네트워크 HTML · 버전 '+str(STATE['version'])+'</h1><a href="/control">검증 화면 돌아가기</a>')
  self.send_error(404)

if __name__=='__main__':
 port=int(sys.argv[1]) if len(sys.argv)>1 else 8820
 print(f'PWA fixture: http://127.0.0.1:{port}/control',flush=True)
 ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
