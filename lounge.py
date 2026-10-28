"""Review-gated fan lounge; uses the existing Firestore board without moving data."""
import os,json,re,shutil
from datetime import datetime,timezone
from urllib.parse import urlsplit
from pathlib import Path
from html import escape as e
from hashlib import sha256
from lounge_content import UI,PEOPLE,EVENTS,LANGS,row
BASE='/fall-707/characters/'
HERE=Path(__file__).parent
PRIVATE=HERE.parents[1]/'output/2026-10-18/fan-lounge'
def enabled():return os.getenv('D9_LOUNGE_PREVIEW')=='1' or json.loads((HERE/'lounge_config.json').read_text())['approved_for_publication']
def new_routes():return ['/lounge/',BASE,*[BASE+p['slug']+'/' for p in PEOPLE]] if enabled() else []
def routes():return [*new_routes(),'/questions/'] if enabled() else []
def extra_bilingual():return len(new_routes())

def released_appearances(works,now=None):
 now=now or datetime.now(timezone.utc);episodes=set()
 for work in works:
  if not re.fullmatch(r's[1-9][0-9]*',work.get('category','')):continue
  season,episode=work.get('season'),work.get('episode')
  if not isinstance(season,int) or not isinstance(episode,int) or season<1 or episode<1:continue
  released=True
  for key in ('releaseAt','uploadDate'):
   if not work.get(key):continue
   try:
    date=datetime.fromisoformat(str(work[key]).replace('Z','+00:00'))
    if date.tzinfo is None:date=date.replace(tzinfo=timezone.utc)
    if date>now:released=False
   except ValueError:released=False
  if released:episodes.add((season,episode))
 return sorted(episodes)
WORDS={
 'topic':row('주제','Topic','テーマ','Tema'),'character':row('캐릭터','Character','登場人物','Personaje'),
 'story':row('이야기','Story','物語','Historia'),'making':row('제작','Filmmaking','制作','Creación'),'other':row('기타','Other','その他','Otros'),
 'posts':row('최근 질문과 답변','Recent questions and answers','最近の質問と回答','Preguntas y respuestas recientes'),
 'all':row('전체','All','すべて','Todo'),'refresh':row('새로고침','Refresh','更新','Actualizar'),
 'loading':row('게시판을 불러오는 중…','Loading the board…','掲示板を読み込み中…','Cargando el tablón…'),
 'more':row('이전 글 더 보기','More previous posts','以前の投稿をもっと見る','Ver publicaciones anteriores'),
 'write':row('닉네임으로 글 남기기','Post with a nickname','ニックネームで投稿','Publicar con un apodo'),
 'nickname':row('닉네임','Nickname','ニックネーム','Apodo'),'title':row('제목','Title','件名','Título'),'body':row('내용','Post','内容','Contenido'),
 'write_button':row('글쓰기','Write a post','投稿する','Escribir'),
 'back_list':row('목록으로','Back to list','一覧へ戻る','Volver al listado'),
 'posted':row('작성일','Posted','投稿日','Fecha'),
 'answer_state':row('답변 상태','Reply status','回答状況','Respuesta'),
 'notice':row('누구나 읽는 공개 게시판입니다. 개인정보는 쓰지 마세요. 로그인이나 회원가입 없이 참여할 수 있습니다.','This is a public board. Do not include personal information. No registration or sign-in is needed.','誰でも読める公開掲示板です。個人情報を書かないでください。登録やログインは不要です。','Es un tablón público. No incluyas datos personales. No necesitas registrarte ni iniciar sesión.'),
 'consent':row('글·닉네임의 공개 게시와 글쓰기용 브라우저 식별정보 처리에 동의합니다.','I agree to public posting of my text and nickname, and processing of a browser identity for posting.','本文とニックネームの公開、および投稿用ブラウザ識別情報の処理に同意します。','Acepto publicar el texto y el apodo y el tratamiento de un identificador del navegador para publicar.'),
 'publish':row('공개 게시하기','Publish post','公開する','Publicar'),
 'limit':row('글쓰기는 같은 브라우저에서 10분에 한 번. 닉네임 2~24자, 제목 2~120자, 내용 10~3,000자. 답변은 운영자만 작성합니다.','One post per 10 minutes per browser. Nickname: 2–24 characters; title: 2–120; post: 10–3,000. Only the creator can reply.','同じブラウザからの投稿は10分に1回。名前2〜24文字、件名2〜120文字、本文10〜3,000文字。回答は運営者のみです。','Una publicación cada 10 minutos por navegador. Apodo: 2–24 caracteres; título: 2–120; texto: 10–3.000. Solo el creador puede responder.'),
 'owner':row('제작자 관리','Creator management','制作者の管理','Gestión del creador'),
 'login':row('제작자 Google 로그인','Creator Google sign-in','制作者のGoogleログイン','Acceso de Google para el creador'),
 'redirect':row('현재 창에서 로그인','Sign in in this tab','この画面でログイン','Entrar en esta pestaña'),
 'logout':row('로그아웃','Sign out','ログアウト','Salir'),
 'archive':row('숨긴 글 보관함','Hidden posts archive','非表示投稿の保管庫','Archivo de publicaciones ocultas'),
 'archive_load':row('보관함 불러오기','Load archive','保管庫を読む','Cargar archivo'),
 'archive_more':row('보관한 글 더 보기','More archived posts','保管した投稿をもっと見る','Ver más publicaciones archivadas'),
 'privacy':row('개인정보처리방침','Privacy policy','プライバシーポリシー','Política de privacidad'),
}
def pre(lang):return '' if lang=='ko' else '/'+lang
def build(out,origin,works,head,base_path=''):
 if not enabled():return
 settings=json.loads((HERE/'lounge_config.json').read_text());preview=os.getenv('D9_LOUNGE_PREVIEW')=='1'
 if not preview and not all(settings.values()):raise ValueError('Character copy, stills and quotes require actual owner approval.')
 evidence_file=PRIVATE/'character-evidence.json' if preview else HERE/'character_evidence.json'
 evidence=json.loads(evidence_file.read_text(encoding='utf-8'))
 source=PRIVATE/'assets' if preview else HERE/'site-assets/assets/characters'
 dest=out/'assets/characters'
 if source.exists():shutil.copytree(source,dest,dirs_exist_ok=True)
 css='/lounge.css?v='+sha256((out/'lounge.css').read_bytes()).hexdigest()[:12]
 def t(key,lang):return UI[key][lang]
 def img(item,lang,loading='lazy'):
  path='/assets/characters/'+item['file']
  return '<a class="lounge-image" href="'+path+'"><img src="'+path+'" width="'+str(item['width'])+'" height="'+str(item['height'])+'" alt="'+e(item.get('alt',{}).get(lang,item.get('character','FALL 707')))+'" loading="'+loading+'"></a>'
 def portrait(p,lang):
  record=evidence.get(p['slug'],{});frames=record.get('frames',[])
  if frames:return img(frames[0],lang)
  return '<div class="lounge-portrait-pending">'+e(p['name'][lang])+'</div>'
 def tiles(lang):return '<div class="lounge-cast">'+''.join('<a class="lounge-character" href="'+pre(lang)+BASE+p['slug']+'/"><div>'+portrait(p,lang).replace('<a class="lounge-image" href=', '<span class="lounge-image" data-source=').replace('</a>','</span>')+'</div><p class="section-eyebrow">'+t('lead' if p['slug']=='min-seoa' else 'support',lang)+'</p><h3>'+p['name'][lang]+'</h3><p>'+p['line'][lang]+'</p></a>' for p in PEOPLE)+'</div>'
 def page(lang,path,title,description,body):
  home=(out/('' if lang=='ko' else lang)/'index.html').read_text(encoding='utf-8');nav=re.search(r'<header class="header"[\s\S]*?</header>',home).group();foot=re.search(r'<footer[\s\S]*?</footer>',home).group()
  schema={'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'inLanguage':lang,'url':origin+pre(lang)+path}
  heading=head(title+' | DRA9ON CINEMA',description,pre(lang)+path,schema).replace('<html lang="ko">','<html lang="'+lang+'">').replace('property="og:type" content="video.episode"','property="og:type" content="website"')
  heading=heading.replace('property="og:locale" content="ko_KR"','property="og:locale" content="'+{'ko':'ko_KR','en':'en_US','ja':'ja_JP','es':'es_ES'}[lang]+'"')
  if preview:heading=heading.replace('content="index,follow,max-image-preview:large,max-video-preview:-1"','content="noindex,nofollow,noarchive"')
  heading=heading.replace('</head>','<link rel="stylesheet" href="/editorial.css"><link rel="stylesheet" href="'+css+'"><script src="/lounge.js" defer></script></head>')
  if lang!='ko':heading=heading.replace('src="/catalog.js"','src="/'+lang+'/catalog.js"')
  if lang in ('ja','es'):heading=heading.replace('<script src="/portfolio.js"','<script src="/'+lang+'/locale.js" defer></script><script src="/portfolio.js"')
  banner='<aside class="lounge-draft">'+t('draft',lang)+'</aside>' if preview else ''
  folder=out/pre(lang).strip('/')/path.strip('/');folder.mkdir(parents=True,exist_ok=True)
  if preview:body=body.replace('id="board-submit"','id="board-submit" disabled')
  (folder/'index.html').write_text(heading+'<body class="watch-page"'+(' data-lounge-preview="true"' if preview else '')+'>'+nav+banner+body+foot+'</body></html>',encoding='utf-8')
 for lang in LANGS:
  tr=lambda k:e(t(k,lang));w=lambda k:e(WORDS[k][lang]);prefix=pre(lang)
  topics=''.join('<option value="'+key+'">'+w(key)+'</option>' for key in ('story','making','character','other'))
  columns=''.join('<th scope="col">'+w(key)+'</th>' for key in ('title','topic','nickname','posted','answer_state'))
  board='<section id="board" class="lounge-section question-answers"><p class="section-eyebrow">03 / YOUR VOICE</p><h2 id="posts-heading">'+w('posts')+'</h2><div id="board-list-view"><div class="board-toolbar"><div class="tutorial-actions"><label for="board-filter">'+w('topic')+'</label><select id="board-filter"><option value="all">'+w('all')+'</option>'+topics+'</select><button id="board-refresh" class="button button-glass" type="button">'+w('refresh')+'</button></div><a class="button button-white" href="#ask">'+w('write_button')+'</a></div><table class="board-table"><caption class="visually-hidden">'+w('posts')+'</caption><thead><tr>'+columns+'</tr></thead><tbody id="board-posts"></tbody></table><button id="board-more" class="button button-glass" type="button" hidden>'+w('more')+'</button></div><section id="board-detail" class="board-detail" hidden><a class="button button-glass" href="#board">'+w('back_list')+'</a><div id="board-detail-content"></div></section><p id="board-status" role="status" aria-live="polite">'+w('loading')+'</p></section>'
  privacy_prefix=prefix if lang in ('ko','en') else '/en'
  board+='<section id="ask" class="qna-panel"><a class="button button-glass" href="#board">'+w('back_list')+'</a><h2 tabindex="-1">'+w('write')+'</h2><p>'+w('notice')+'</p><form id="board-form"><label for="board-nickname">'+w('nickname')+'</label><input id="board-nickname" required minlength="2" maxlength="24" autocomplete="off"><label for="board-topic">'+w('topic')+'</label><select id="board-topic">'+topics+'</select><label for="board-title">'+w('title')+'</label><input id="board-title" required minlength="2" maxlength="120"><label for="board-body">'+w('body')+'</label><textarea id="board-body" required minlength="10" maxlength="3000" rows="7"></textarea><div class="qna-trap" aria-hidden="true"><label for="board-website">Website</label><input id="board-website" tabindex="-1" autocomplete="off"></div><label class="qna-check"><input type="checkbox" id="board-consent" required>'+w('consent')+' <a href="'+privacy_prefix+'/privacy/">'+w('privacy')+'</a></label><button id="board-submit" class="button button-white" type="submit">'+w('publish')+'</button></form><p id="board-write-status" role="status" aria-live="polite"></p><p>'+w('limit')+'</p></section>'
  board+='<section class="qna-panel"><h2>'+w('owner')+'</h2><div class="tutorial-actions"><button id="board-owner-login" class="button button-glass" type="button">'+w('login')+'</button><button id="board-owner-redirect" class="button button-glass" type="button">'+w('redirect')+'</button><button id="board-owner-logout" class="button button-glass" type="button" hidden>'+w('logout')+'</button></div><p id="board-owner-status" role="status"></p><div id="board-owner-panel" hidden><div class="lounge-owner-alerts"><p>'+tr('notify_help')+'</p><button type="button" id="board-notify-on" class="button button-white">'+tr('notify')+'</button><button type="button" id="board-notify-off" class="button button-glass">'+tr('notify_off')+'</button><p id="board-notify-status" role="status"></p></div><h3>'+w('archive')+'</h3><button id="board-archive-refresh" class="button button-glass" type="button">'+w('archive_load')+'</button><div id="board-archive"></div><button id="board-archive-more" class="button button-glass" type="button" hidden>'+w('archive_more')+'</button></div></section>'
  events='<section id="events" class="lounge-section"><p class="section-eyebrow">02 / EVENTS</p><h2>'+tr('events')+'</h2><p>'+tr('event_links')+'</p><div class="lounge-events">'
  for event in EVENTS:
   events+='<article id="event-'+event['id']+'" class="lounge-event"><p class="section-eyebrow">'+event['partner']+'</p><h3>'+e(event['title'][lang])+'</h3><p><time>'+event['period']+'</time> · KST</p>'
   poster=event.get('poster')
   if poster:
    if not poster['path'].startswith('/assets/events/') or not (out/poster['path'].lstrip('/')).is_file():raise ValueError('Event poster requires an actual local asset')
    events+='<a class="lounge-image" href="'+e(poster['path'],quote=True)+'"><img src="'+e(poster['path'],quote=True)+'" width="'+str(poster['width'])+'" height="'+str(poster['height'])+'" loading="lazy" alt="'+e(event['title'][lang],quote=True)+'"></a>'
   else:events+='<p class="lounge-pending">'+tr('assets_pending')+'</p>'
   events+='<dl><dt>'+tr('theme')+'</dt><dd>'+e(event['title'][lang])+'</dd><dt>'+tr('prizes')+'</dt><dd>'+e(event['prizes'][lang] if event.get('prizes') else t('pending',lang))+'</dd></dl><h4>'+tr('winners')+'</h4>'
   released=not event.get('announce_at') or datetime.now(timezone.utc)>=datetime.fromisoformat(event['announce_at'])
   if event.get('winners') and released:
    events+='<ul>'
    for winner in event['winners']:
     url=urlsplit(winner['url'])
     if url.scheme!='https' or url.hostname not in ('www.threads.com','threads.com','www.threads.net','threads.net','www.instagram.com','instagram.com') or url.username or url.password:raise ValueError('Winners must link to original Threads/Instagram posts')
     events+='<li><a href="'+e(winner['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">'+e(winner['label'][lang])+' · '+e(winner['author'])+' ↗</a></li>'
    events+='</ul>'
   else:events+='<p>'+tr('announcement' if event.get('announce_at') else 'winners_pending')+'</p>'
   events+='</article>'
  events+='</div></section>'
  hero='<header class="editorial-hero"><p class="section-eyebrow">DRA9ON CINEMA / FAN LOUNGE</p><h1>'+tr('lounge')+'</h1><p>'+tr('intro')+'</p><nav class="lounge-jump" aria-label="'+tr('lounge')+'"><a href="#characters">01 '+tr('characters')+'</a><a href="#events">02 '+tr('events')+'</a><a href="#board">03 '+tr('board')+'</a></nav></header>'
  body='<main id="main" class="editorial-main lounge-main">'+hero+'<section id="characters" class="lounge-section"><p class="section-eyebrow">01 / THE PEOPLE</p><h2>'+tr('characters')+'</h2><p>'+tr('character_intro')+'</p>'+tiles(lang)+'<a class="text-button" href="'+prefix+BASE+'">'+tr('all')+' →</a></section>'+events+board+'</main><script src="/engagement-config.js"></script><script type="module" src="/community.js"></script>'
  page(lang,'/lounge/',t('lounge',lang),t('intro',lang),body)
  page(lang,BASE,'FALL 707 · '+t('characters',lang),t('character_intro',lang),'<main id="main" class="editorial-main"><a class="editorial-back" href="'+prefix+'/lounge/#characters">← '+tr('back')+'</a><header class="editorial-hero"><p class="section-eyebrow">FALL 707 / CHARACTERS</p><h1>'+tr('characters')+'</h1><p>'+tr('spoilers')+'</p></header>'+tiles(lang)+'</main>')
  for p in PEOPLE:
   record=evidence.get(p['slug'],{});frames=record.get('frames',[]);label=p['name'][lang]
   body='<main id="main" class="editorial-main character-main"><a class="editorial-back" href="'+prefix+BASE+'">← '+tr('characters')+'</a><header class="character-hero"><div>'+portrait(p,lang)+'</div><div><p class="section-eyebrow">FALL 707 / '+tr('lead' if p['slug']=='min-seoa' else 'support')+'</p><h1>'+label+'</h1><p class="character-logline">'+e(p['line'][lang])+'</p><p>'+e(p['description'][lang])+'</p><p class="editorial-note">'+tr('spoilers')+'</p></div></header><section class="lounge-section"><h2>'+tr('scenes')+'</h2><div class="character-scenes">'
   for f in frames[1:]:body+='<figure>'+img(f,lang)+'<figcaption>'+tr('actual')+' · S'+str(f['season'])+' EP.'+str(f['episode'])+' · <a href="'+e(f['source_url'],quote=True)+'&t='+str(int(f['seconds']))+'s" target="_blank" rel="noopener noreferrer">'+tr('source')+' ↗</a></figcaption></figure>'
   body+='</div></section><section class="lounge-section"><h2>'+tr('relations')+'</h2><ul class="character-relations">'
   for rel in record.get('relations',[]):body+='<li><a href="'+prefix+BASE+rel['person']+'/">'+next(x['name'][lang] for x in PEOPLE if x['slug']==rel['person'])+'</a><span>'+e(rel['label'][lang])+'</span></li>'
   first=e(record.get('first',{}).get(lang,t('first_pending',lang)))
   if record.get('first_episode'):
    fs,fe=record['first_episode'];first='<a href="'+prefix+'/watch/fall-707-s'+str(fs)+'-ep'+str(fe)+'/">'+first+' →</a>'
   all_episodes=p.get('appearance_scope')=='all_released'
   body+='</ul></section><section class="lounge-section"><h2>'+tr('all_episodes' if all_episodes else 'episodes')+'</h2>'
   if all_episodes:body+='<p>'+tr('every_episode')+'</p>'
   body+='<p>'+tr('first')+' · '+first+'</p><div class="character-episodes">'
   appearances=released_appearances(works) if all_episodes else sorted(set(p['appearances'])|{(f['season'],f['episode']) for f in frames})
   for season,episode in appearances:
    matched=sorted([w for w in works if w.get('season')==season and w.get('episode')==episode and w.get('category')==f's{season}'],key=lambda w:w.get('part') or 0)
    for appearance in matched:
     episode_label='S'+str(season)+' EP.'+str(episode).zfill(2)+((' · Part '+str(appearance['part'])) if appearance.get('part') else '')
     body+='<a class="button button-glass" href="'+prefix+appearance['path']+'">'+episode_label+'</a>'
   body+='</div></section><section class="lounge-section"><h2>'+tr('quotes')+'</h2>'
   quotes=record.get('quotes',[])
   for q in quotes:body+='<figure class="character-quote"><blockquote>'+e(q['text'][lang])+'</blockquote><figcaption><a href="'+e(q['source_url'],quote=True)+'&t='+str(int(q['seconds']))+'s" target="_blank" rel="noopener noreferrer">S'+str(q['season'])+' EP.'+str(q['episode'])+' · '+tr('source')+' ↗</a></figcaption></figure>'
   if not quotes:body+='<p class="lounge-pending">'+tr('quote_pending')+'</p>'
   body+='</section><div class="character-actions"><a class="button button-white" href="'+prefix+'/lounge/?topic=character&amp;character='+p['slug']+'#ask">'+tr('ask')+' →</a></div>'
   if p['slug']=='min-seoa':body+='<p class="character-prequel">'+tr('prequel')+'</p>'
   body+='</main>';page(lang,BASE+p['slug']+'/',label+' · FALL 707',p['line'][lang],body)
  # GitHub Pages has no server redirect rules: replace-location + immediate meta refresh.
  target=prefix+'/lounge/#board';folder=out/prefix.strip('/')/'questions';folder.mkdir(parents=True,exist_ok=True)
  redirect_head=head(t('lounge',lang)+' | DRA9ON CINEMA',t('intro',lang),prefix+'/lounge/',{'@context':'https://schema.org','@type':'WebPage','name':t('lounge',lang),'url':origin+prefix+'/lounge/'}).replace('<html lang="ko">','<html lang="'+lang+'">').replace('content="index,follow,max-image-preview:large,max-video-preview:-1"','content="noindex,follow"').replace('</head>','<meta http-equiv="refresh" content="0;url='+target+'"><script src="/lounge-redirect.js" defer></script></head>')
  redirect_head=redirect_head.replace('property="og:locale" content="ko_KR"','property="og:locale" content="'+{'ko':'ko_KR','en':'en_US','ja':'ja_JP','es':'es_ES'}[lang]+'"')
  home_doc=(out/('' if lang=='ko' else lang)/'index.html').read_text(encoding='utf-8')
  (folder/'index.html').write_text(redirect_head+'<body>'+re.search(r'<header class="header"[\s\S]*?</header>',home_doc).group()+'<a href="'+target+'">'+tr('lounge')+' →</a>'+re.search(r'<footer[\s\S]*?</footer>',home_doc).group()+'</body></html>',encoding='utf-8')
 # Change the existing menu entry in place, including old localized fallback links.
 for file in out.rglob('*.html'):
  path=file.relative_to(out).as_posix();lang=path.split('/')[0] if path.startswith(('en/','ja/','es/')) else 'ko';doc=file.read_text(encoding='utf-8')
  if lang!='ko':
   doc=doc.replace('DRA9ON CINEMA 〈낙하 707: 리부트〉 FALL 707 키비주얼',{'en':'DRA9ON CINEMA FALL 707 key visual','ja':'DRA9ON CINEMA FALL 707 キービジュアル','es':'Imagen principal de FALL 707, DRA9ON CINEMA'}[lang])
  doc=re.sub(r'(<a\b[^>]*href=")[^"<>]*?/questions/(?:#[^"]*)?("[^>]*>)[\s\S]*?</a>',lambda m:m[1]+pre(lang)+'/lounge/'+m[2]+t('lounge',lang)+'</a>',doc)
  if '/fall-707/world/' in '/'+path:
   for p in PEOPLE:
    target=pre(lang)+BASE+p['slug']+'/'
    def linked(match):
     article=match[0];article=re.sub(r'(<img\b[^>]*>)',lambda m:'<a href="'+target+'">'+m[0]+'</a>',article,count=1)
     return article.replace('</article>','<a class="text-button" href="'+target+'">'+t('profile',lang)+' →</a></article>',1)
    doc=re.sub(r'<article id="person-'+re.escape(p['old'])+r'">[\s\S]*?</article>',linked,doc,count=1)
   if 'id="person-hyeolmaek"' not in doc:
    person=next(p for p in PEOPLE if p['slug']=='hyeolmaek')
    card='<article id="person-hyeolmaek"><h3>'+e(person['name'][lang])+'</h3><p>'+e(person['line'][lang])+'</p><a class="text-button" href="'+pre(lang)+BASE+'hyeolmaek/">'+t('profile',lang)+' →</a></article>'
    boundary='</div></section><section class="editorial-section" aria-labelledby="world-relations">'
    if boundary not in doc:raise ValueError('World supporting-character insertion point missing')
    doc=doc.replace(boundary,card+boundary,1)
  file.write_text(doc,encoding='utf-8')
 # Append the owner-alert privacy disclosure only with this review-gated feature.
 privacy_copy=row(
  ('팬 라운지와 운영자 전용 알림','공개 게시판의 닉네임·제목·본문·주제와 운영자 답변은 기존 Firebase 저장소를 사용합니다. 글쓰기용 익명 브라우저 인증과 10분 간격 제한은 유지하며 방문자 회원가입은 만들지 않습니다.','운영자 알림을 켠 기기는 Google로 인증된 운영자 계정인지 서버에서 확인합니다. 알림 주소·암호화 키·운영자 Firebase 식별자·선택 언어를 별도 비공개 Cloudflare D1 영역에 저장하며 방문자용 새 회차 구독과 섞지 않습니다. 공개 글의 닉네임·제목·주제·시각·답변 여부를 알림 집계용으로 복제합니다. 인증 토큰과 App Check 증명은 원문 확인에만 사용하며 저장하거나 로그에 기록하지 않습니다.','새 글 알림은 10분 동안 묶으며 매일 한국 시간 밤 10시에 요약 발송을 시도합니다. 연결이나 브라우저·푸시 제공자 상태에 따라 수신은 지연될 수 있습니다. 원문 저장 후 알림 전달이 실패하면 브라우저의 공개 글 ID 대기열에서 재시도하며 운영자 접속 시 기존 글을 대조합니다. 발송 상태 기록은 7일 보관하고 열람·클릭은 추적하지 않습니다. 운영자 알림을 끄면 해당 기기의 운영자 구독을 삭제합니다.'),
  ('Fan Lounge and owner-only alerts','Public nicknames, titles, posts, topics and creator replies continue to use the existing Firebase store. Anonymous browser authentication and the ten-minute posting limit are retained. No visitor registration is introduced.','The server verifies the Google-authenticated owner before registering a device for board alerts. Push endpoints, encryption keys, the owner’s Firebase identifier and selected language are stored in a separate private Cloudflare D1 area, apart from visitor episode subscriptions. Public post nicknames, titles, topics, timestamps and answered flags are mirrored for notifications. Authentication tokens and App Check proofs are used only to verify the source, never stored or logged.','New-post alerts are grouped for ten minutes, and a daily summary is attempted at 22:00 KST. Network, browser or push-provider conditions may delay receipt. Failed event submissions are retried from a browser queue of public post IDs and reconciled when the owner signs in. Delivery records are retained for seven days without tracking opens or clicks. Turning off owner alerts removes that device’s owner subscription.'),
  (),()
 )
 for lang in ('ko','en'):
  file=out/('' if lang=='ko' else lang)/'privacy/index.html';doc=file.read_text(encoding='utf-8');heading,*paragraphs=privacy_copy[lang]
  added='<section class="lounge-privacy"><h2>'+e(heading)+'</h2>'+''.join('<p>'+e(text)+'</p>' for text in paragraphs)+'</section>'
  file.write_text(doc.replace('</main>',added+'</main>',1),encoding='utf-8')

