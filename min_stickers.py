"""Complete captioned sticker collection with an accessible shared gallery."""
from html import escape
TITLE=('민 대위 이모티콘','Captain Min stickers','ミン大尉のスタンプ','Stickers de la capitana Min')
HOME_TITLE=TITLE
INTRO=('민 대위의 열두 가지 표정. 눌러서 크게 보고, 좌우로 넘겨보세요.','Twelve expressions of Captain Min. Tap to enlarge and browse left or right.','ミン大尉の12の表情。タップして拡大し、左右に送ってご覧ください。','Doce expresiones de la capitana Min. Toca para ampliar y recorre la colección.')
LABELS=[
 ('충성!','Salute!','敬礼！','¡A sus órdenes!'),
 ('보급 시급','Need supplies','補給が必要','Necesito provisiones'),
 ('수상한데…','Suspicious…','怪しい…','Qué sospechoso…'),
 ('잠깐만?!','Wait a second?!','ちょっと待って?!','¡¿Un momento?!'),
 ('내가 간다!','On my way!','私が行く！','¡Allá voy!'),
 ('고마워♡','Thank you ♡','ありがとう♡','Gracias ♡'),
 ('5분만…','Five more minutes…','あと5分…','Cinco minutos más…'),
 ('밥부터 먹자','Let’s eat first','まずはご飯','Primero, a comer'),
 ('나만 믿어','Trust me','任せて','Confía en mí'),
 ('흥.','Hmph.','ふん。','Hum.'),
 ('할 수 있다!','You can do it!','できる！','¡Tú puedes!'),
 ('오늘은 휴무','Off duty today','今日はお休み','Hoy, de descanso')]
MOTIONS=('salute','droop','tilt','startle','dash','shy','sleep','bounce','confident','hmph','cheer','relax')
COUNT=(f'{len(LABELS)}종',f'{len(LABELS)} stickers',f'全{len(LABELS)}種',f'{len(LABELS)} diseños')
CLOSE=('닫기','Close','閉じる','Cerrar')
MORE=('더 보기','Show more','もっと見る','Ver más')
LESS=('접기','Show less','折りたたむ','Ver menos')
PREVIOUS=('이전 이모티콘','Previous sticker','前のスタンプ','Sticker anterior')
NEXT=('다음 이모티콘','Next sticker','次のスタンプ','Sticker siguiente')
GROUP=('이모티콘 크게 보기','Sticker viewer','スタンプ拡大表示','Visor de stickers')
ROWS=[TITLE,INTRO,COUNT,CLOSE,MORE,LESS,PREVIOUS,NEXT,GROUP,*LABELS]
TRANSLATIONS={row[0]:row[1] for row in ROWS}
def translations(lang):
 index={'ko':0,'en':1,'ja':2,'es':3}[lang]
 return {source:row[index] for row in ROWS for source in row[:2]}

def render(home=False, lang="ko"):
 index={"ko":0,"en":1,"ja":2,"es":3}[lang]
 cards=[]
 for i,row in enumerate(LABELS):
  label=escape(row[index],quote=True);file=f'/assets/stickers/min-{i+1:02}'
  cards.append(f'<button type="button" class="sticker-card" data-sticker="{i}" data-motion="{MOTIONS[i]}" data-full="{file}-full.webp" aria-haspopup="dialog" aria-controls="sticker-dialog" aria-label="{label}"><span class="sticker-art"><img src="{file}-240.webp" srcset="{file}-240.webp 240w, {file}-360.webp 360w" sizes="(max-width:600px) 30vw, (max-width:1000px) 23vw, 16vw" width="360" height="360" alt="{label}" loading="lazy" decoding="async" draggable="false"></span><span class="sticker-name">{label}</span></button>')
 return (f'<section class="min-stickers{" sticker-home" if home else ""}" id="min-stickers" aria-labelledby="sticker-title"><p class="section-eyebrow">CAPTAIN MIN · OFF DUTY</p><div class="sticker-heading"><h2 id="sticker-title">{TITLE[index]}</h2><span class="sticker-count">{COUNT[index]}</span></div><p>{INTRO[index]}</p><div class="sticker-grid" id="sticker-grid">'+''.join(cards)+'</div>'
  +f'<button class="sticker-expand" type="button" aria-expanded="false" aria-controls="sticker-grid" hidden><span class="sticker-more">{MORE[index]}</span><span class="sticker-less" hidden>{LESS[index]}</span><span aria-hidden="true"> ＋</span></button>'
  +f'<dialog class="sticker-dialog" id="sticker-dialog" aria-label="{GROUP[index]}" aria-labelledby="sticker-caption"><button type="button" class="sticker-close">{CLOSE[index]} ×</button><div class="sticker-stage"><img class="sticker-large" src="/assets/stickers/min-01-240.webp" width="362" height="362" loading="lazy" alt="" draggable="false"><button type="button" class="sticker-prev" aria-label="{PREVIOUS[index]}">‹</button><button type="button" class="sticker-next" aria-label="{NEXT[index]}">›</button></div><div class="sticker-caption-row" aria-live="polite" aria-atomic="true"><h3 id="sticker-caption"></h3><span class="sticker-position"></span></div></dialog></section><script src="/min-stickers.js?v=20261022-grid" defer></script>')

def home_teaser():return render(home=True)
def build_sticker_page(out,origin,head,header,footer):
 body='<body class="watch-page">'+header()+'<main class="production-note" id="main"><a class="note-back" href="/">← 홈으로</a>'+render()+'</main>'+footer()+'</body></html>'
 folder=out/'stickers';folder.mkdir(exist_ok=True)
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':TITLE[0],'url':origin+'/stickers/'}
 (folder/'index.html').write_text(head(TITLE[0]+' | DRA9ON CINEMA',INTRO[0],'/stickers/',schema)+body,encoding='utf-8')
