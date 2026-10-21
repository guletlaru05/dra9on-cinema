"""Apply temporary-host login repair only to the Cloudflare preview output.

Production source files and GitHub Pages output are left byte-for-byte intact.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('Login source changed; review preview integration before deploying')
 return text.replace(old,new,1)
def configure(out,stage):
 if stage!='preview':return
 library=out/'library/library.js';code=library.read_text(encoding='utf-8')
 code=replace_once(code,'const config=window.D9_ENGAGEMENT_CONFIG,app=','const config={...window.D9_ENGAGEMENT_CONFIG,authDomain:"dra9on-cinema.pages.dev"},app=')
 code='import {installPreviewLogin} from "./preview-login.mjs?v=20261021-login1";\n'+code
 start=code.index(' getRedirectResult(auth).catch(');end=code.index(' async function loadOwnerVisits',start)
 code=code[:start]+''' let loginStorage;try{loginStorage=sessionStorage;}catch{}
 const previewLogin=installPreviewLogin({auth,GoogleAuthProvider,signInWithPopup,signInWithRedirect,getRedirectResult,deadline,storage:loginStorage});
 await previewLogin.restore();
'''+code[end:]
 start=code.index(' $("login").addEventListener(');end=code.index(' $("logout").addEventListener(',start)
 code=code[:start]+code[end:]
 code=replace_once(code,' ready=true;',' ready=true;window.D9PreviewLibrary?.ready();')
 code=replace_once(code,'boot().catch(error=>message("자료실을 시작하지 못했습니다. "+(error.code||error.message)));','boot().catch(error=>{const text="로그인 보안 연결을 시작하지 못했습니다. 네트워크·콘텐츠 차단을 확인하세요. (library/initialization-failed)";message(text);window.D9PreviewLibrary?.error(text);});')
 library.write_text(code,encoding='utf-8')
 index=out/'library/index.html';html=index.read_text(encoding='utf-8')
 html=replace_once(html,'</head>','<script src="./login-bootstrap.js?v=20261021-login1" defer></script></head>')
 html=html.replace('library.js?v=20261018-auto-desk','library.js?v=20261021-login1')
 # Add only the precise same-origin helper path to this page's existing CSP.
 html=replace_once(html,'frame-src https://www.google.com/recaptcha/','frame-src https://dra9on-cinema.pages.dev/__/auth/ https://www.google.com/recaptcha/')
 index.write_text(html,encoding='utf-8')
 for name in ('login-bootstrap.js','preview-login.mjs'):(out/'library'/name).write_bytes((ROOT/'cloudflare'/name).read_bytes())
 (out/'_worker.js').write_bytes((ROOT/'cloudflare/auth-proxy.mjs').read_bytes())
 (out/'_routes.json').write_text(json.dumps({'version':1,'include':['/__/auth/*','/__/firebase/init.json'],'exclude':[]}),encoding='utf-8')
 # Auth is enabled without a Firebase Hosting release, so its init.json is 404.
 # Publish only the existing public web IDs; never include App Check tokens/owner data.
 source=(out/'engagement-config.js').read_text(encoding='utf-8')
 public={key:re.search(r'\b'+key+r':\s*"([^"]+)"',source).group(1) for key in ('apiKey','projectId','appId')}
 if public['projectId']!='dra9on-cinema-stats':raise ValueError('Unexpected Firebase project')
 public['authDomain']='dra9on-cinema.pages.dev'
 init=out/'__/firebase/init.json';init.parent.mkdir(parents=True,exist_ok=True);init.write_text(json.dumps(public),encoding='utf-8')
