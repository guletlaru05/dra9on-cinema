"""Functional, browser-only episode memory; no server history or identity."""
from hashlib import sha256
def inject_continue_watching(out,base_path=''):
 assets=[]
 for name in ('continue-watching.js','continue-watching.css'):
  content=(out/name).read_bytes();stem,ext=name.rsplit('.',1)
  filename=stem+'.'+sha256(content).hexdigest()[:12]+'.'+ext
  (out/'assets/build'/filename).write_bytes(content)
  assets.append(base_path+'/assets/build/'+filename)
 for page in out.rglob('*.html'):
  relative=page.relative_to(out).as_posix()
  if relative.startswith(('en/','ja/','es/')):relative=relative.split('/',1)[1]
  if relative!='index.html' and not relative.startswith('watch/'):continue
  text=page.read_text(encoding='utf-8').replace('</head>',f'<script src="{assets[0]}" defer></script><link rel="stylesheet" href="{assets[1]}"></head>',1)
  page.write_text(text,encoding='utf-8')
