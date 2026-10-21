"""Owner-provided rights notice and lossless WebP copyright metadata wrapping.

WebP container reference: https://developers.google.com/speed/webp/docs/riff_container
The encoded image chunks are preserved byte-for-byte; no pixel re-encoding.
"""
import struct
from html import escape
from xml.etree import ElementTree as ET

COPYRIGHT='© DRA9ON CINEMA. All rights reserved.'
TITLE={
 'ko':'AI 배우 및 캐릭터 이용 제한',
 'en':'Restrictions on use of AI actors and characters',
 'ja':'AI俳優およびキャラクターの利用制限',
 'es':'Restricciones de uso de los actores de IA y sus personajes',
}
NOTICE={
 'ko':[
  '본 페이지의 AI 배우 이미지와 캐릭터는 DRA9ON CINEMA의 오리지널 IP입니다.',
  '무단 복제·배포·편집, 상업적 이용, AI 학습 및 이미지·영상 생성 레퍼런스로의 사용을 금지합니다.',
  '출연·라이선스 문의는 섭외 문의를 이용해 주세요.',COPYRIGHT],
 'en':[
  'The AI actors and characters on this page are original IP of DRA9ON CINEMA.',
  'Unauthorized copying, distribution, editing, commercial use, AI training, or use as a reference for image or video generation is prohibited.',
  'For casting or licensing, please use the inquiry form.',COPYRIGHT],
 'ja':[
  '本ページのAI俳優の画像およびキャラクターは、DRA9ON CINEMAのオリジナルIPです。',
  '無断での複製・配布・編集、商用利用、AI学習、および画像・動画生成の参照資料としての使用を禁止します。',
  '出演・ライセンスに関するお問い合わせは、出演のお問い合わせフォームをご利用ください。',COPYRIGHT],
 'es':[
  'Las imágenes de los actores de IA y los personajes de esta página son propiedad intelectual original de DRA9ON CINEMA.',
  'Se prohíben la copia, distribución, edición, uso comercial y entrenamiento de IA sin autorización, así como su uso como referencia para generar imágenes o vídeos.',
  'Para consultas de casting o licencias, utiliza el formulario de contacto.',COPYRIGHT],
}
TERMS_LABEL={'ko':'이용약관','en':'Terms of use','ja':'利用規約','es':'Términos de uso'}
TRANSLATIONS={TITLE['ko']:TITLE['en'],**dict(zip(NOTICE['ko'],NOTICE['en']))}

def terms_href(lang,base_path=''):
 # The existing terms are Korean/English. Japanese and Spanish jump directly
 # to the same-language notice inside the existing English terms page.
 return base_path+('' if lang=='ko' else '/en')+'/terms/#ai-actors'+('-'+lang if lang in ('ja','es') else '')

def notice_html(lang,base_path=''):
 return '<aside class="actor-rights" aria-label="'+escape(TITLE[lang],quote=True)+'">'+''.join('<p>'+escape(line)+'</p>' for line in NOTICE[lang])+'<a href="'+escape(terms_href(lang,base_path),quote=True)+'">'+TERMS_LABEL[lang]+' →</a></aside>'

def terms_section():
 result='<section id="ai-actors"><h2>'+TITLE['ko']+'</h2>'+''.join('<p>'+escape(line)+'</p>' for line in NOTICE['ko'])
 result+='<p><a href="/?inquiry=ai-actor#collaboration-inquiry">섭외 문의</a></p>'
 for lang,label in [('ja','日本語'),('es','Español')]:
  result+='<section id="ai-actors-'+lang+'" lang="'+lang+'"><h3>'+label+' · '+TITLE[lang]+'</h3>'+''.join('<p>'+escape(line)+'</p>' for line in NOTICE[lang])+'</section>'
 return result+'</section>'

def webp_chunks(data):
 if data[:4]!=b'RIFF' or data[8:12]!=b'WEBP' or len(data)!=int.from_bytes(data[4:8],'little')+8:
  raise ValueError('Invalid WebP RIFF container')
 chunks=[];position=12
 while position<len(data):
  if position+8>len(data):raise ValueError('Truncated WebP chunk')
  fourcc=data[position:position+4];size=int.from_bytes(data[position+4:position+8],'little');end=position+8+size
  if end+(size%2)>len(data):raise ValueError('Truncated WebP payload')
  chunks.append((fourcc,data[position+8:end]));position=end+(size%2)
 return chunks

def with_copyright(data):
 chunks=webp_chunks(data)
 ns={'x':'adobe:ns:meta/','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#','dc':'http://purl.org/dc/elements/1.1/','xmpRights':'http://ns.adobe.com/xap/1.0/rights/'}
 for key,value in ns.items():ET.register_namespace(key,value)
 previous=next((payload for key,payload in chunks if key==b'XMP '),None)
 root=ET.fromstring(previous) if previous else ET.Element('{'+ns['x']+'}xmpmeta')
 rdf=root.find('{'+ns['rdf']+'}RDF')
 if rdf is None:rdf=ET.SubElement(root,'{'+ns['rdf']+'}RDF')
 description=rdf.find('{'+ns['rdf']+'}Description')
 if description is None:description=ET.SubElement(rdf,'{'+ns['rdf']+'}Description',{'{'+ns['rdf']+'}about':''})
 for parent in root.iter():
  for child in list(parent):
   if child.tag in ('{'+ns['dc']+'}rights','{'+ns['xmpRights']+'}Marked'):parent.remove(child)
 rights=ET.SubElement(description,'{'+ns['dc']+'}rights');alt=ET.SubElement(rights,'{'+ns['rdf']+'}Alt')
 ET.SubElement(alt,'{'+ns['rdf']+'}li',{'{http://www.w3.org/XML/1998/namespace}lang':'x-default'}).text=COPYRIGHT
 ET.SubElement(description,'{'+ns['xmpRights']+'}Marked').text='True'
 xmp=ET.tostring(root,encoding='utf-8')
 extended=next((p for k,p in chunks if k==b'VP8X'),None)
 if extended:
  if len(extended)!=10:raise ValueError('Invalid VP8X chunk')
  extended=bytes([extended[0]|4])+extended[1:]
 else:
  vp8=next((p for k,p in chunks if k==b'VP8 '),None)
  if vp8 is None or vp8[3:6]!=b'\x9d\x01\x2a':raise ValueError('Expected the static opaque VP8 photos prepared for this site')
  width=int.from_bytes(vp8[6:8],'little')&0x3fff;height=int.from_bytes(vp8[8:10],'little')&0x3fff
  extended=b'\x04\0\0\0'+(width-1).to_bytes(3,'little')+(height-1).to_bytes(3,'little')
 def pack(key,payload):return key+struct.pack('<I',len(payload))+payload+(b'\0' if len(payload)%2 else b'')
 body=b'WEBP'+pack(b'VP8X',extended)+b''.join(pack(k,p) for k,p in chunks if k not in (b'VP8X',b'XMP '))+pack(b'XMP ',xmp)
 return b'RIFF'+struct.pack('<I',len(body))+body
