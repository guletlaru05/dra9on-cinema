"""Four-language lighting lesson; all image records must exist before building."""
from html import escape
from hashlib import sha256
import json,re
from lighting_content import COPY

PATH='/tutorials/lighting-contrast/'
ART='/assets/tutorials/lighting-contrast/gpt-rembrandt.webp'
DATE='2026-10-18'
ASSETS='/assets/tutorials/lighting-contrast/'
TITLE_KO=COPY['ko']['title'];TITLE_EN=COPY['en']['title']

def teaser(t):
 return '<a class="tutorial-preview" href="'+PATH+'"><img src="'+ART+'" width="1344" height="752" loading="lazy" alt="'+t('GPT Image 2.5 · 창가 인물의 렘브란트 조명과 명암 비교','GPT Image 2.5 · Rembrandt window light and contrast on a fictional adult')+'"><div><p class="section-eyebrow">LIGHT / CONTRAST / MIDJOURNEY × HIGGSFIELD</p><h3>'+t(TITLE_KO,TITLE_EN)+'</h3><p class="tutorial-card-date"><time datetime="'+DATE+'">2026.10.18</time> · '+t('조명 4종 · 모델 비교 · 전체 프롬프트','Four lighting setups · Model comparison · Full prompts')+'</p><span>'+t('강좌 열기','Open lesson')+' →</span></div></a>'

def build(out,origin,head,header,footer,t):
 # Register all KO -> EN pairs before the regular English pass.
 def register(a,b):
  if isinstance(a,str):t(a,b)
  elif isinstance(a,list):
   for x,y in zip(a,b):register(x,y)
  elif isinstance(a,dict):
   for k in a:register(a[k],b[k])
 register(COPY['ko'],COPY['en'])
 render(out,origin,head,header(),footer(),'ko')

def render(out,origin,head,nav,foot,lang,base_path=''):
 c=COPY[lang];prefix='' if lang=='ko' else '/'+lang;route=prefix+PATH
 records=json.loads((out/(ASSETS.strip('/')+'/generation-manifest.json')).read_text(encoding='utf-8'))
 if len(records)!=10:raise ValueError('Lighting lesson requires ten verified image records.')
 by_id={r['id']:r for r in records}
 def figure(record,title,hero=False):
  src=ASSETS+record['file'];alt=record['model']+' · '+title
  return '<figure class="lighting-figure"><a href="'+src+'" target="_blank" rel="noopener"><img src="'+src+'" width="'+str(record['width'])+'" height="'+str(record['height'])+'" alt="'+escape(alt,quote=True)+'" '+('fetchpriority="high"' if hero else 'loading="lazy"')+' decoding="async"></a><figcaption>'+escape(alt)+'</figcaption></figure>'
 def prompt_card(r):
  rows=[(c['tool'],r['tool']),(c['model'],r['model']),(c['ratio'],r['ratio']),(c['image'],f'{r["width"]} × {r["height"]} · {round(r["bytes"]/1024)} KB')]
  meta='<dl class="aesthetic-record">'+''.join('<div><dt>'+escape(k)+'</dt><dd>'+escape(v)+'</dd></div>'for k,v in rows)+'</dl>'
  parameters={k:v for k,v in r['parameters'].items() if k!='prompt'}
  card='<details class="lighting-prompt"><summary>'+escape(c['full'])+' · '+escape(r['model'])+'</summary>'+meta+'<pre tabindex="0"><code>'+escape(r['prompt'])+'</code></pre><p>'+escape(c['settings'])+'</p><dl class="aesthetic-settings">'+''.join('<div><dt>'+escape(k)+'</dt><dd>'+escape(str(v))+'</dd></div>'for k,v in parameters.items())+'</dl><a class="text-button" href="'+ASSETS+r['id']+'-prompt.txt" download>'+escape(c['download'])+' ↓</a>'
  if r.get('requested_model') and r['requested_model']!=r['model']:
   note={'ko':'요청 모델은 Nano Banana Pro였으나 서비스 결과 모델은 Nano Banana 2였습니다. Pro의 결과로 간주하지 않습니다.','en':'Nano Banana Pro was requested, but the service returned Nano Banana 2. This is not presented as a Pro result.','ja':'Nano Banana Proを指定しましたが、サービスの結果モデルはNano Banana 2でした。Proの結果としては扱いません。','es':'Se solicitó Nano Banana Pro, pero el servicio devolvió Nano Banana 2. No se presenta como un resultado de Pro.'}[lang]
   card+='<p class="tutorial-notice">'+escape(note)+'</p>'
  (out/(ASSETS.strip('/')+'/'+r['id']+'-prompt.txt')).write_text(r['prompt'],encoding='utf-8')
  return card+'</details>'
 def section(index):
  title,paragraphs=c['sections'][index]
  return '<section class="aesthetic-section"><h2>'+escape(title)+'</h2>'+''.join('<p>'+escape(p)+'</p>'for p in paragraphs)+'</section>'
 body='<body class="watch-page">'+nav+'<main id="main" class="tutorial-main aesthetic-main lighting-main"><a class="note-back" href="'+prefix+'/tutorials/">← '+escape(c['back'])+'</a><header class="aesthetic-heading"><p class="section-eyebrow">DRA9ON CINEMA / LIGHT & CONTRAST</p><h1>'+escape(c['title'])+'</h1><p class="tutorial-intro">'+escape(c['subtitle'])+'</p><p class="tutorial-date"><time datetime="'+DATE+'">2026.10.18</time></p></header>'
 body+=figure(by_id['gpt-rembrandt'],c['lights'][1][0],True)+'<p class="tutorial-notice">'+escape(c['notice'])+'</p>'+section(0)+section(1)+section(2)
 body+='<p class="tutorial-notice">'+escape(c['caution'])+'</p>'
 observation={'ko':'결과 관찰: GPT 렘브란트의 뺨 삼각형은 약하고, Seedream의 삼각형은 더 선명합니다. 미드저니는 네 조명 요청의 차이가 작고 실루엣에서도 얼굴이 남았습니다. 프롬프트가 목표를 적었다고 결과가 그 목표를 모두 달성한 것은 아닙니다.','en':'Observed results: the cheek triangle is faint in GPT Rembrandt and clearer in Seedream. Midjourney changes little across these four requests and leaves facial detail in its silhouette. A requested effect is not proof that the output achieved it.','ja':'結果の観察：GPTのレンブラントでは頬の三角形が弱く、Seedreamではより明瞭です。Midjourneyは4つの指定の差が小さく、シルエットにも顔の情報が残りました。指定した効果と実際の達成度を分けて見てください。','es':'Resultados observados: el triángulo de la mejilla es débil en GPT y más claro en Seedream. Midjourney varía poco entre las cuatro peticiones y mantiene detalle facial en la silueta. Pedir un efecto no demuestra que el resultado lo haya logrado.'}[lang]
 body+='<p class="tutorial-notice">'+escape(observation)+'</p>'
 for i,key in enumerate(['gpt-high-key','gpt-rembrandt','gpt-split','gpt-silhouette']):
  name,description=c['lights'][i]
  body+='<section class="aesthetic-section" id="light-'+str(i+1)+'"><h2>'+str(i+1)+'. '+escape(name)+'</h2><p>'+escape(description)+'</p>'+figure(by_id[key],name)+prompt_card(by_id[key])+'</section>'
 body+=section(3)+'<section class="aesthetic-section"><h2>'+escape(c['comparison'])+'</h2><div class="lighting-model-grid">'
 for key in ['gpt-rembrandt','seedream-rembrandt','nano-rembrandt']:
  r=by_id[key];body+='<article>'+figure(r,c['lights'][1][0])+prompt_card(r)+'</article>'
 body+='</div></section><section class="aesthetic-section"><h2>'+escape(c['mj'])+'</h2><p>'+escape(c['mj_note'])+'</p><figure class="lighting-figure"><a href="'+ASSETS+'midjourney-lighting-grid.webp" target="_blank" rel="noopener"><img src="'+ASSETS+'midjourney-lighting-grid.webp" width="1600" height="980" loading="lazy" alt="'+escape('Midjourney v8.2 · '+c['mj'],quote=True)+'"></a></figure><div class="lighting-mj-grid">'
 for i,key in enumerate(['mj-high-key','mj-rembrandt','mj-split','mj-silhouette']):
  r=by_id[key];body+='<article><h3>'+str(i+1)+'. '+escape(c['lights'][i][0])+'</h3>'+'<a class="text-button" href="'+ASSETS+r['file']+'" target="_blank" rel="noopener">'+escape(r['model'])+' · '+str(i+1)+' ↗</a>'+prompt_card(r)+'</article>'
 body+='</div></section>'+section(4)+'<a class="text-button" href="'+prefix+'/tutorials/">'+escape(c['more'])+' →</a></main>'+foot+'</body></html>'
 schema={'@context':'https://schema.org','@type':'Article','headline':c['title'],'description':c['subtitle'],'datePublished':DATE,'dateModified':DATE,'inLanguage':lang,'author':{'@type':'Organization','name':'DRA9ON CINEMA'},'image':origin+ASSETS+'lighting-share.jpg','url':origin+route}
 page=head(c['title']+' | DRA9ON CINEMA',c['subtitle'],route,schema)
 page=page.replace('<html lang="ko">','<html lang="'+lang+'">').replace('property="og:type" content="video.episode"','property="og:type" content="article"')
 page=re.sub(r'(property="og:locale" content=")[^"]*',lambda m:m[1]+{'ko':'ko_KR','en':'en_US','ja':'ja_JP','es':'es_ES'}[lang],page)
 for attr in ['property="og:image"','name="twitter:image"']:page=re.sub('('+re.escape(attr)+' content=")[^"]*',lambda m:m[1]+origin+ASSETS+'lighting-share.jpg',page)
 for attr,value in [('og:image:width','1200'),('og:image:height','630'),('og:image:alt',by_id['gpt-rembrandt']['model']+' · '+c['lights'][1][0])]:page=re.sub('(property="'+attr+'" content=")[^"]*',lambda m:m[1]+escape(value,quote=True),page)
 page=re.sub('(name="twitter:image:alt" content=")[^"]*',lambda m:m[1]+escape(by_id['gpt-rembrandt']['model']+' · '+c['lights'][1][0],quote=True),page)
 resources='<link rel="stylesheet" href="/aesthetics-tutorial.css"><link rel="stylesheet" href="/lighting-tutorial.css?v='+sha256((out/'lighting-tutorial.css').read_bytes()).hexdigest()[:12]+'"><meta property="article:published_time" content="'+DATE+'">'
 if lang in ('ja','es'):resources+='<script src="/'+lang+'/locale.js" defer></script>'
 page=page.replace('</head>',resources+'</head>')
 target=out/route.strip('/');target.mkdir(parents=True,exist_ok=True);document=page+body
 if base_path:
  document=re.sub(r'((?:href|src)=")(/[^"]*)',lambda m:m[1]+(m[2] if m[2].startswith(base_path+'/') else base_path+m[2]),document)
 (target/'index.html').write_text(document,encoding='utf-8')

def build_all(out,origin,head,header,footer,base_path=''):
 for lang in COPY:
  if lang=='ko':nav,foot=header(),footer()
  else:
   homepage=(out/lang/'index.html').read_text(encoding='utf-8')
   nav=re.search(r'<header class="header"[\s\S]*?</header>',homepage).group(0)
   foot=re.search(r'<footer[\s\S]*?</footer>',homepage).group(0)
  render(out,origin,head,nav,foot,lang,base_path)
  if lang in ('ja','es'):
   title='作品づくりの裏側を、あなたも。' if lang=='ja' else 'Descubre cómo se crean las escenas.'
   intro='新しい照明の実習から始めましょう。以前の記事は英語版へ進めます。' if lang=='ja' else 'Empieza con la nueva práctica de iluminación. Los artículos anteriores enlazan a su versión en inglés.'
   article=(out/lang/PATH.strip('/')/'index.html').read_text(encoding='utf-8')
   listing_head=article.split('</head>',1)[0]+'</head>'
   listing_head=listing_head.replace(origin+'/'+lang+PATH,origin+'/'+lang+'/tutorials/')
   for key in ['title','description']:
    old=COPY[lang]['title']+' | DRA9ON CINEMA' if key=='title' else COPY[lang]['subtitle']
    new=title+' | DRA9ON CINEMA' if key=='title' else intro
    listing_head=listing_head.replace(escape(old,quote=True),escape(new,quote=True))
   schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'description':intro,'url':origin+'/'+lang+'/tutorials/','inLanguage':lang}
   listing_head=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda _: '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>',listing_head,flags=re.S)
   english=(out/'en/tutorials/index.html').read_text(encoding='utf-8')
   cards=re.findall(r'<a class="tutorial-preview"[\s\S]*?</a>',english)
   first=cards[0].replace('/en'+PATH,'/'+lang+PATH).replace(escape(TITLE_EN),escape(COPY[lang]['title'])).replace('Open lesson',COPY[lang]['read'])
   body='<body class="watch-page">'+nav+'<main id="main" class="tutorial-main"><h1>'+escape(title)+'</h1><p class="tutorial-intro">'+escape(intro)+'</p><div class="tutorial-lesson-list">'+first+''.join(cards[1:])+'</div></main>'+foot+'</body></html>'
   folder=out/lang/'tutorials';folder.mkdir(parents=True,exist_ok=True)
   (folder/'index.html').write_text(listing_head+body,encoding='utf-8')
