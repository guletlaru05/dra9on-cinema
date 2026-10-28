"""Owner-approved work reel; no remote media or generated footage at build time."""
from hashlib import sha256
from html import escape
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parent
LANGS=('ko','en','ja','es')

def tr(*items):return dict(zip(LANGS,items))

COPY=[
 {'title':tr('FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT'),
  'tab':tr('낙하 707 · 최신 회차','FALL 707 · Latest','FALL 707・最新話','FALL 707 · Lo más reciente'),
  'label':tr('시즌 3 · EP.04 · PART 1','SEASON 3 · EP.04 · PART 1','シーズン3・EP.04 · PART 1','TEMPORADA 3 · EP.04 · PART 1'),
  'description':tr('다섯 개의 기둥, 그리고 마지막 한 발. 시즌 3 4화 상편 공개.','Five pillars. One last round. Season 3, Episode 4, Part 1 is out now.','五つの柱、そして最後の一発。シーズン3第4話・前編を公開。','Cinco pilares. Una última bala. Ya disponible: temporada 3, episodio 4, parte 1.'),
  'path':'/watch/fall-707-s3-ep4-part1/'},
 {'title':tr('FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT'),
  'tab':tr('시즌 3 · 3화','Season 3 · Episode 3','シーズン3・第3話','Temporada 3 · Episodio 3'),
  'label':tr('시즌 3 · EP.03','SEASON 3 · EP.03','シーズン3・EP.03','TEMPORADA 3 · EP.03'),
  'description':tr('대저택을 포위한 칼끝. 같은 밤, 서울이 깨어난다.','The mansion is surrounded. On that same night, Seoul awakens.','屋敷を囲む刃。同じ夜、ソウルが目覚める。','La mansión está rodeada. Esa misma noche, Seúl despierta.'),
  'path':'/watch/fall-707-s3-ep3/'},
 {'title':tr('FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT','FALL 707: REBOOT'),
  'tab':tr('시즌 3 · 2화','Season 3 · Episode 2','シーズン3・第2話','Temporada 3 · Episodio 2'),
  'label':tr('시즌 3 · EP.02 · 물러서지 마라',"SEASON 3 · EP.02 · DON'T BACK DOWN",'シーズン3・EP.02・退くな','TEMPORADA 3 · EP.02 · NO RETROCEDAS'),
  'description':tr('물러서지 않는 민서아 대위. 사격과 근접 교전으로 이어지는 액션.','Captain Min Seo-a refuses to back down. Gunfire gives way to close-quarters combat.','退かないミン・ソア大尉。銃撃から近接戦闘へ続くアクション。','La capitana Min Seo-a no retrocede. Los disparos dan paso al combate cuerpo a cuerpo.'),
  'path':'/watch/fall-707-s3-ep2/'},
 {'title':tr('FALL 707 · 시즌 2','FALL 707 · Season 2','FALL 707・シーズン2','FALL 707 · Temporada 2'),
  'tab':tr('시즌 2 · 몰아보기','Season 2 · Full story','シーズン2・一気見','Temporada 2 · Completa'),
  'label':tr('시즌 2 · 전체 이야기','SEASON 2 · FULL STORY','シーズン2・全編','TEMPORADA 2 · HISTORIA COMPLETA'),
  'description':tr('조선의 밤, 현대의 전술. 시즌 2의 전투를 한 편으로.','Joseon nights. Modern tactics. Experience the complete second season.','朝鮮の夜、現代の戦術。シーズン2の戦いを一編で。','Noches de Joseon y tácticas modernas. Vive la segunda temporada completa.'),
  'path':'/watch/fall-707-season-2-full/'},
 {'title':tr('FALL 707 · 시즌 1','FALL 707 · Season 1','FALL 707・シーズン1','FALL 707 · Temporada 1'),
  'tab':tr('시즌 1 · 이야기의 시작','Season 1 · The beginning','シーズン1・物語の始まり','Temporada 1 · El comienzo'),
  'label':tr('시즌 1 · 전체 이야기','SEASON 1 · FULL STORY','シーズン1・全編','TEMPORADA 1 · HISTORIA COMPLETA'),
  'description':tr('낯선 시대에 떨어진 한 사람. 모든 이야기의 시작.','One soldier in an unfamiliar era. See where it all began.','見知らぬ時代に降り立った一人の兵士。すべての始まり。','Una soldado en una época desconocida. Descubre cómo comenzó todo.'),
  'path':'/watch/fall-707-season-1-full/'},
 {'title':tr('죽지도 않는 미친X과\nn번째 저승사자','The Immortal Crazy X\nand the n-th Grim Reaper','死なないヤツと\nn番目の死神','Crazy X inmortal\ny el enésimo segador'),
  'tab':tr('미친X과 저승사자','The Immortal & the Reaper','不死のヤツと死神','Crazy X y el segador'),
  'label':tr('DRA9ON 오리지널 · 판타지','DRA9ON ORIGINAL · FANTASY','DRA9ON ORIGINAL・ファンタジー','DRA9ON ORIGINAL · FANTASÍA'),
  'description':tr('끝나지 않는 삶과, 오늘도 찾아온 저승사자.','A life that will not end. A reaper who keeps coming back.','終わらない命と、今日も訪れる死神。','Una vida que no termina. Un segador que siempre vuelve.'),
  'path':'/watch/film-iVwqj1gUPDY/'},
 {'title':tr('AI 배우 에이전시','AI Actor Agency','AI俳優エージェンシー','Agencia de actores de IA'),
  'tab':tr('AI 배우 · 새로운 얼굴','AI actors · Meet the cast','AI俳優・キャスト紹介','Actores IA · El reparto'),
  'label':tr('오리지널 AI 캐릭터','ORIGINAL AI CHARACTERS','オリジナルAIキャラクター','PERSONAJES ORIGINALES DE IA'),
  'description':tr('민서아 · 연화 · 유나 · 하슬. 드라마 밖에서 만나는 네 배우.','Min Seoa, Yeonhwa, Yuna and Haseul. Meet the cast beyond the drama.','ミン・ソア、ヨンファ、ユナ、ハスル。ドラマの外の四人に出会う。','Min Seoa, Yeonhwa, Yuna y Haseul. Conoce al reparto fuera del drama.'),
  'path':'/actors/'}]

LABELS={
 'view':tr('작품 보기','Explore the work','作品を見る','Ver la obra'),
 'inquiry':tr('섭외·협업 문의','Casting & collaboration','出演・コラボのお問い合わせ','Casting y colaboración'),
 'pause':tr('일시정지','Pause','一時停止','Pausar'),
 'resume':tr('재생','Resume','再生','Reanudar'),
 'tabs':tr('추천 작품 선택','Select a featured work','注目作品を選択','Selecciona una obra'),
}

def inject(out,base_path=''):
 config=json.loads((ROOT/'hero_rotation_config.json').read_text(encoding='utf-8'))
 if not config['approved']:raise ValueError('Hero clip approval is required')
 if len(COPY)!=len(config['clips']) or [c['id'] for c in config['clips']]!=config['approvedOrder']:
  raise ValueError('Hero copy, clips and approved order must match')
 out=Path(out);tags=[]
 for name in ('work-hero.css','work-hero.js'):
  data=(out/name).read_bytes();stem,ext=name.rsplit('.',1)
  if ext=='css':
   # This small, home-only critical style needs no extra render-blocking request.
   # The existing CSP already permits inline styles; no policy is broadened.
   tags.append('<style data-work-hero-style>'+data.decode('utf-8')+'</style>');continue
  hashed=stem+'.'+sha256(data).hexdigest()[:12]+'.'+ext
  (out/'assets/build'/hashed).write_bytes(data);url=base_path+'/assets/build/'+hashed
  tags.append('<link rel="stylesheet" href="'+url+'">' if ext=='css' else '<script src="'+url+'" defer></script>')
 for lang in LANGS:
  prefix=base_path+('' if lang=='ko' else '/'+lang);page=out/(('' if lang=='ko' else lang+'/')+'index.html')
  slides=[]
  for copy,clip in zip(COPY,config['clips']):
   assert clip['approved'] and clip['id'] in config['approvedOrder']
   route=prefix+copy['path']
   # Existing original shorts have KO/EN watch pages; use EN when JA/ES is absent.
   view_label=LABELS['view'][lang]
   if not (out/route[len(base_path):].lstrip('/')/'index.html').is_file():
    route=base_path+'/en'+copy['path'];view_label={'ja':'英語版を見る','es':'Ver en inglés'}.get(lang,view_label)
   files={k:base_path+'/assets/hero/'+v for k,v in clip['files'].items()}
   dimensions=clip.get('dimensions',{'desktop':[960,540],'mobile':[640,360]})
   poster_mobile=clip.get('posterDimensions',dimensions)['mobile']
   slides.append({k:copy[k][lang] for k in ('title','tab','label','description')}|{'id':clip['id'],'url':route,'viewLabel':view_label,'duration':clip['duration'],'focus':clip['focus'],'focusTrack':clip.get('focusTrack',[]),'fit':clip['fit'],'width':dimensions['desktop'][0],'height':dimensions['desktop'][1],'mobileWidth':poster_mobile[0],'mobileHeight':poster_mobile[1],**files})
  first=slides[0];e=lambda value:escape(str(value),quote=True)
  payload=json.dumps({'slides':slides,'pause':LABELS['pause'][lang],'resume':LABELS['resume'][lang]},ensure_ascii=False).replace('<',r'\u003c')
  tabs=''.join('<button type="button" class="d9-work-tab" id="work-tab-'+str(i)+'" role="tab" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0' if i==0 else '-1')+'" aria-controls="work-hero-panel" data-work-index="'+str(i)+'"><span class="d9-work-line" aria-hidden="true"><i></i></span><span class="d9-work-number">'+str(i+1).zfill(2)+'</span><span class="d9-work-name">'+e(s['tab'])+'</span></button>' for i,s in enumerate(slides))
  fallback=''.join('<li><a href="'+e(s['url'])+'">'+e(s['title'])+'</a> — '+e(s['description'])+'</li>' for s in slides)
  hero=f'''<section class="hero d9-work-hero" id="hero" data-work-hero style="--d9-work-count:{len(slides)}" aria-labelledby="hero-title"><div class="hero-media"><picture><source class="hero-mobile-poster" media="(max-width:700px)" srcset="{e(first.get('mobilePoster',first['poster']))}"><img class="hero-image" src="{e(first['poster'])}" alt="{e(first['tab'])}" width="{first['width']}" height="{first['height']}" fetchpriority="high" decoding="async"></picture><div class="hero-shade"></div></div><div class="hero-content" id="work-hero-panel" role="tabpanel" aria-labelledby="work-tab-0"><p class="eyebrow">DRA9ON CINEMA</p><p class="d9-work-label">{e(first['label'])}</p><h1 id="hero-title">{e(first['title'])}</h1><p class="d9-work-description">{e(first['description'])}</p><div class="hero-buttons"><a class="button button-white hero-feature-link" href="{e(first['url'])}">{e(LABELS['view'][lang])} ↗</a><a class="button button-glass hero-casting-link" href="{prefix}/actors/min-seoa/?casting=1#casting-inquiry">{e(LABELS['inquiry'][lang])} ↗</a></div></div><button type="button" class="d9-work-pause" aria-label="{e(LABELS['pause'][lang])}" aria-pressed="false">Ⅱ</button><div class="d9-work-tabs" role="tablist" aria-label="{e(LABELS['tabs'][lang])}">{tabs}</div><script type="application/json" data-work-hero-config>{payload}</script><noscript><ul class="d9-work-noscript">{fallback}</ul></noscript></section>'''
  document=page.read_text(encoding='utf-8');document,n=re.subn(r'<section\b[^>]*id="hero"[^>]*>[\s\S]*?</section>',lambda _:hero,document,count=1)
  if n!=1:raise ValueError('Expected exactly one home hero: '+lang)
  # The parser can start the correct first-screen poster before the hero markup;
  # mutually exclusive media queries avoid fetching the desktop image on phones.
  preload='<link rel="preload" as="image" href="'+e(first.get('mobilePoster',first['poster']))+'" media="(max-width:700px)" fetchpriority="high"><link rel="preload" as="image" href="'+e(first['poster'])+'" media="(min-width:701px)" fetchpriority="high">'
  document=document.replace('</head>',preload+''.join(tags)+'</head>',1);page.write_text(document,encoding='utf-8')

