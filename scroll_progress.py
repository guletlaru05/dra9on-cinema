"""Shared decorative progress, included after public and PWA pages are built."""
from hashlib import sha256
import re

def inject(out,base_path=''):
 tags=[]
 for name in ('scroll-progress.css','scroll-progress.js'):
  data=(out/name).read_bytes();stem,suffix=name.rsplit('.',1)
  target=stem+'.'+sha256(data).hexdigest()[:12]+'.'+suffix
  (out/'assets/build'/target).write_bytes(data)
  url=base_path+'/assets/build/'+target
  tags.append('<link rel="stylesheet" href="'+url+'">' if suffix=='css' else '<script src="'+url+'" defer></script>')
 for page in out.rglob('*.html'):
  doc=page.read_text(encoding='utf-8')
  if 'id="d9-scroll-progress"' in doc:continue
  doc=doc.replace('</head>',''.join(tags)+'</head>',1)
  doc=re.sub(r'(<body\b[^>]*>)',r'\1<div id="d9-scroll-progress" aria-hidden="true" hidden><span></span></div>',doc,count=1)
  page.write_text(doc,encoding='utf-8')
