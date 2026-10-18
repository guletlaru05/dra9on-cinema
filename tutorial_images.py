"""An accessible, same-page image viewer for every public tutorial article."""
from hashlib import sha256
import re

COPY={
 'ko':('튜토리얼 이미지 크게 보기','닫기 ×','원본 이미지 열기','이미지를 불러오지 못했습니다. 원본 링크를 확인해 주세요.'),
 'en':('Enlarged tutorial image','Close ×','Open original image','The image could not be loaded. Try the original link.'),
 'ja':('チュートリアル画像を拡大','閉じる ×','元の画像を開く','画像を読み込めませんでした。元の画像のリンクをご確認ください。'),
 'es':('Ampliar imagen del tutorial','Cerrar ×','Abrir imagen original','No se pudo cargar la imagen. Prueba el enlace al original.'),
}
def inject_images(out,base_path=''):
 assets={}
 for extension in ('css','js'):
  content=(out/('tutorial-images.'+extension)).read_bytes()
  name='tutorial-images.'+sha256(content).hexdigest()[:12]+'.'+extension
  (out/'assets/build'/name).write_bytes(content)
  assets[extension]=base_path+'/assets/build/'+name
 for page in out.rglob('index.html'):
  path='/'+page.relative_to(out).as_posix().removesuffix('index.html')
  canonical=re.sub(r'^/(en|ja|es)(?=/)','',path)
  from importlib.util import find_spec
  note_routes=lambda:set()
  if find_spec('notes_update') is not None:
   from notes_update import routes as note_routes
  is_note=canonical in (note_routes()-{'/notes/'})
  from lounge import new_routes
  is_character=canonical in new_routes()
  if not is_note and not is_character and (not canonical.startswith('/tutorials/') or canonical=='/tutorials/'):continue
  lang=path.split('/')[1] if path.startswith(('/en/','/ja/','/es/')) else 'ko'
  title,close,original,error=COPY[lang]
  if is_note:title={'ko':'제작 비하인드 이미지 크게 보기','en':'Enlarged production image','ja':'制作後記の画像を拡大','es':'Ampliar imagen de producción'}[lang]
  if is_character:title={'ko':'장면 이미지 크게 보기','en':'Enlarged scene image','ja':'場面画像を拡大','es':'Ampliar imagen de la escena'}[lang]
  dialog=f'<dialog class="tutorial-image-viewer" data-tutorial-image-viewer aria-labelledby="tutorial-image-title"><header><h2 id="tutorial-image-title">{title}</h2><button type="button" data-image-close autofocus>{close}</button></header><figure><div data-enlarged-mount></div><figcaption data-enlarged-caption></figcaption></figure><p data-image-error hidden role="status">{error}</p><a data-image-original target="_blank" rel="noopener">{original} ↗</a></dialog>'
  doc=page.read_text(encoding='utf-8')
  doc=doc.replace('</body>',dialog+'</body>',1)
  doc=doc.replace('</head>','<link rel="stylesheet" href="'+assets['css']+'"><script src="'+assets['js']+'" defer></script></head>',1)
  page.write_text(doc,encoding='utf-8')
