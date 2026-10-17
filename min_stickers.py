from html import escape
TITLE=('민 대위의 쉬는 시간','Captain Min, off duty')
INTRO=('단발과 위장무늬 군복, 무뚝뚝하지만 조금 귀여운 민 대위. 표정을 눌러 크게 보세요.','Short bob, camouflage and a quietly cute side. Tap an expression to enlarge it.')
LABELS=[('충성!','Salute!'),('보급 시급','Need supplies'),('수상한데…','Suspicious…'),('잠깐만?!','Wait a second?!'),('내가 간다!','On my way!'),('고마워♡','Thank you ♡'),('5분만…','Five more minutes…'),('밥부터 먹자','Let’s eat first'),('나만 믿어','Trust me'),('흥.','Hmph.'),('할 수 있다!','You can do it!'),('오늘은 휴무','Off duty today')]
CLOSE=('닫기','Close')
TRANSLATIONS=dict([TITLE,INTRO,CLOSE,*LABELS])
HOME_TITLE=('민 대위 이모티콘','Captain Min stickers')
ALL=('12종 전체 보기','View all 12 stickers')
TRANSLATIONS.update([HOME_TITLE,ALL])

def home_teaser():
 def card(i):
  ko=escape(LABELS[i][0])
  return f'<a class="sticker-card" href="/stickers/"><span class="min-sprite min-sprite-{i}" aria-hidden="true"></span><span>{ko}</span></a>'
 preview=''.join(card(i) for i in [0,5,8])
 return f'<section class="min-stickers sticker-home sticker-art-ready" id="min-stickers"><p class="section-eyebrow">CAPTAIN MIN · OFF DUTY</p><h2>{HOME_TITLE[0]}</h2><p>{INTRO[0]}</p><div class="sticker-grid sticker-preview">{preview}</div><a class="text-button home-more" href="/stickers/">더 보기 →</a></section>'

def build_sticker_page(out,origin,head,header,footer):
 title=HOME_TITLE[0]
 body='<body class="watch-page">'+header()+'<main class="production-note" id="main"><a class="note-back" href="/">← 홈으로</a>'+render()+'</main>'+footer()+'</body></html>'
 folder=out/'stickers';folder.mkdir(exist_ok=True)
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':origin+'/stickers/'}
 (folder/'index.html').write_text(head(title+' | DRA9ON CINEMA',INTRO[0],'/stickers/',schema)+body,encoding='utf-8')
TRANSLATIONS.update({'더 보기':'View all','← 홈으로':'← Home'})

def render():
 out=f'<section class="min-stickers" id="min-stickers"><p class="section-eyebrow">CAPTAIN MIN · OFF DUTY</p><h2>{TITLE[0]}</h2><p>{INTRO[0]}</p><div class="sticker-grid">'
 for i,(ko,en) in enumerate(LABELS):
  out+=f'<button type="button" class="sticker-card" data-sticker="{i}" aria-haspopup="dialog" aria-label="{escape(ko)}"><span class="min-sprite min-sprite-{i}" aria-hidden="true"></span><span>{escape(ko)}</span></button>'
 return out+f'</div><dialog class="sticker-dialog" aria-labelledby="sticker-caption"><button type="button" class="sticker-close">{CLOSE[0]} ×</button><div class="min-sprite" aria-hidden="true"></div><h3 id="sticker-caption"></h3></dialog></section><script src="/min-stickers.js?v=20261011-perf" defer></script>'

