"""Press resources from existing production footage, with no generated stills."""
from html import escape
from hashlib import sha256
import json
from site_config import ABOUT_PARAGRAPHS, CONTACT_EMAIL
from collaboration import CASES
from youtube_sync import exact_count

ROUTES=['/press/']
TRANSLATIONS={}
WORLD_ENABLED=False
def t(ko,en):
 TRANSLATIONS[ko]=en
 return escape(ko)

SEASONS=[
 {'season':1,'logline':('현대의 전술, 조선의 어둠. 낯선 시대에 떨어진 군인이 살아남기 위해 싸운다.','Modern tactics. Joseon-era darkness. A soldier stranded in another time fights to survive.'),
  'synopsis':('707 특임대 장교 민서아는 조선의 궁궐 후원으로 추락한다. 왕자 이서와의 만남 이후, 익숙한 무기로 설명할 수 없는 위협과 마주한다. 검은 방울이 울리는 밤, 그녀는 낯선 시대의 사람들과 함께 살아남을 길을 찾아야 한다.','Captain Min Seo-a of the 707 Special Mission Unit falls into the grounds of a Joseon palace. An encounter with Prince Iseo draws her into a threat that familiar weapons cannot explain. When a black bell rings in the night, survival depends on the people she meets in this unfamiliar era.')},
 {'season':2,'logline':('구해야 할 사람들이 적이 되어 돌아왔다. 그래도 그들을 두고 돌아갈 수 없다.','The people she came to save have become her enemies. She still cannot leave them behind.'),
  'synopsis':('조선에 머문 지 석 달, 목포진의 겨울에 자리 잡은 민서아와 연화의 평온은 오래가지 않는다. 성 안으로 침투한 이들과 기이한 종소리가 다시 밤을 흔든다. 민서아는 사라진 동료와 연화를 지키기 위해, 자신이 아는 전투의 경계를 넘어선다.','Three months into her life in Joseon, Min Seo-a finds a fragile peace in winter-bound Mokpojin alongside Yeonhwa. Infiltrators and an unnatural bell soon shatter that calm. To protect Yeonhwa and find her missing comrades, Min must fight beyond the limits of everything she knows.')},
]

def metrics(data):
 ch=data.get('channel',{});count=exact_count(ch.get('apiSubscriberCount'))
 return {'youtube':count,'updatedAt':ch.get('apiStatisticsUpdatedAt') or '',
         'instagram':'92000','facebook':'73000','socialSource':'owner-provided'}

def build_press(out,origin,works,data,head,header,footer):
 meta=metrics(data)
 stills=json.loads((out/'assets/press/stills.json').read_text(encoding='utf-8'))
 desc=t('DRA9ON CINEMA 소개, FALL 707 시즌별 시놉시스, 공식 스틸과 로고, 채널 지표 및 협업 연락처.','DRA9ON CINEMA background, FALL 707 season synopses, production stills, logos, channel figures and collaboration contact.')
 title=t('프레스킷 | DRA9ON CINEMA','Press Kit | DRA9ON CINEMA')
 content='<main id="main" class="editorial-main press-main"><a class="editorial-back" href="/">'+t('← 홈으로','← Home')+'</a><header class="editorial-hero"><p class="section-eyebrow">DRA9ON CINEMA / PRESS KIT</p><h1>'+t('이야기를 소개할 때, 필요한 모든 것.','Everything you need to tell the story.')+'</h1><p>'+desc+'</p><a class="button button-white" href="/assets/press/dra9on-cinema-press-kit.pdf" download>'+t('전체 프레스킷 PDF 다운로드','Download the full press kit PDF')+'</a></header>'
 content+='<section class="editorial-section" aria-labelledby="press-about"><p class="section-eyebrow">01 / THE CREATOR</p><h2 id="press-about">DRA9ON CINEMA</h2>'
 for ko,en in zip(ABOUT_PARAGRAPHS['ko'],ABOUT_PARAGRAPHS['en']):content+='<p>'+t(ko,en)+'</p>'
 content+='</section><section class="editorial-section" aria-labelledby="press-series"><p class="section-eyebrow">02 / ORIGINAL SERIES</p><h2 id="press-series">FALL 707: REBOOT</h2><div class="season-synopses">'
 for season in SEASONS:
  content+='<article><span class="section-eyebrow">SEASON '+str(season['season'])+'</span><h3>'+t(*season['logline'])+'</h3><p>'+t(*season['synopsis'])+'</p></article>'
 content+='</div>'
 if WORLD_ENABLED:content+='<a class="text-button" href="/fall-707/world/">'+t('FALL 707 세계관 살펴보기 →','Explore the world of FALL 707 →')+'</a>'
 content+='</section><section class="editorial-section" aria-labelledby="press-stills"><p class="section-eyebrow">03 / PRODUCTION STILLS</p><h2 id="press-stills">'+t('작품 스틸 8장','Eight production stills')+'</h2><p>'+t('시즌 1·2 실제 영상의 검은 띠를 제거한 스틸입니다. 원본 해상도를 유지하고 각 장면의 실제 비율로 제공합니다.','Frames from the actual Season 1 and 2 films, with encoded black bars removed. Each image keeps its native resolution and actual scene aspect ratio.')+'</p><div class="press-still-grid">'
 for s in stills:
  caption=t(s['caption']['ko'],s['caption']['en']);path='/assets/press/'+s['id']
  pv=sha256((out/(path.lstrip('/')+'.webp')).read_bytes()).hexdigest()[:12]
  jv=sha256((out/(path.lstrip('/')+'.jpg')).read_bytes()).hexdigest()[:12]
  content+=f'<figure><img src="{path}.webp?v={pv}" width="{s["width"]}" height="{s["height"]}" style="aspect-ratio:{s["width"]}/{s["height"]}" alt="FALL 707 · {caption}" loading="lazy"><figcaption><span>{caption}<br>{s["width"]} × {s["height"]}</span><a href="{path}.jpg?v={jv}" download>JPG ↓ <span class="sr-only">{caption}</span></a></figcaption></figure>'
 content+='</div><p class="editorial-note">'+t('작품 소개·보도·협업 검토를 위한 자료입니다. 저작권은 DRA9ON CINEMA에 있으며, 재편집·상업적 이용은 사전 문의해 주세요.','These materials are for editorial coverage and collaboration review. Copyright belongs to DRA9ON CINEMA. Please contact us before re-editing or commercial use.')+'</p></section>'
 content+='<section class="editorial-section" aria-labelledby="press-logos"><p class="section-eyebrow">04 / WORDMARK</p><h2 id="press-logos">'+t('로고 다운로드','Download logos')+'</h2><div class="press-logo-grid">'
 for variant,cls,label in [('dark-background','logo-dark',t('어두운 배경용','For dark backgrounds')),('light-background','logo-light',t('밝은 배경용','For light backgrounds'))]:
  content+=f'<figure class="{cls}"><img src="/assets/press/dra9on-logo-{variant}.png" width="2400" height="1050" alt="DRA9ON CINEMA · {label}"><figcaption>{label} <a href="/assets/press/dra9on-logo-{variant}.png" download>PNG ↓</a></figcaption></figure>'
 content+='</div></section><section class="editorial-section" aria-labelledby="press-figures"><p class="section-eyebrow">05 / CHANNELS</p><h2 id="press-figures">'+t('채널 지표','Channel figures')+'</h2><dl class="press-metrics">'
 for platform,value,label in [('YouTube',meta['youtube'],t('구독자','subscribers')),('Instagram',meta['instagram'],t('팔로워','followers')),('Facebook',meta['facebook'],t('팔로워','followers'))]:
  content+='<div><dt>'+platform+'</dt><dd><strong>'+escape(value if value is not None else t('연결 대기','Connection pending'))+'</strong> '+label+'</dd></div>'
 content+='</dl><p class="editorial-note">'+t('YouTube는 API 제공값 그대로 표시하며 하루 1회 갱신합니다. Instagram·Facebook은 제작자가 제공한 수치로 자동 갱신하지 않습니다. 플랫폼 간 중복 이용자가 포함됩니다.','YouTube figures are shown exactly as returned by the API and refreshed daily. Instagram and Facebook figures were supplied by the creator and are not updated automatically. Audiences may overlap across platforms.')+'</p>'
 if meta['updatedAt']:content+='<p class="editorial-note">'+t('YouTube API 갱신 시각: ','YouTube API retrieved: ')+f'<time datetime="{meta["updatedAt"]}">{meta["updatedAt"]}</time></p>'
 content+='</section><section class="editorial-section" aria-labelledby="press-collaborations"><p class="section-eyebrow">06 / SELECTED WORK</p><h2 id="press-collaborations">'+t('협업·프로그램 참여 사례','Collaborations and creator programs')+'</h2><div class="press-cases">'
 for case in CASES:
  content+=f'<a href="{case["url"]}" target="_blank" rel="noopener noreferrer"><strong>{case["name"]}</strong><span>'+case['type']+'</span></a>'
 content+='</div><p>'+t('Dreamina·Higgsfield·OpenArt CPP 참여. OpenArt는 2026년 8월·9월 선정 이력입니다. 모든 사례가 유료 광고나 공식 제휴를 뜻하지는 않습니다.','Creator program participation: Dreamina, Higgsfield and OpenArt. OpenArt selections: August and September 2026. Participation does not imply that every example is a paid advertisement or an official endorsement.')+'</p></section>'
 content+='<section class="editorial-section press-contact"><p class="section-eyebrow">07 / CONTACT</p><h2>'+t('다음 이야기를 함께.','Let’s make the next story.')+'</h2><a href="mailto:'+CONTACT_EMAIL+'">'+CONTACT_EMAIL+'</a></section></main>'
 page=head(title,desc,'/press/',{'@context':'https://schema.org','@type':'AboutPage','name':title,'description':desc,'url':origin+'/press/'})
 page=page.replace('property="og:type" content="video.episode"','property="og:type" content="website"').replace('</head>','<link rel="stylesheet" href="/editorial.css"></head>')
 folder=out/'press';folder.mkdir(exist_ok=True)
 (folder/'index.html').write_text(page+'<body class="watch-page">'+header()+content+footer()+'</body></html>',encoding='utf-8')
 (out/'assets/press/channel-figures.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 from press_pdf import build_pdf
 build_pdf(out,data,stills)
 pdf_version=sha256((out/'assets/press/dra9on-cinema-press-kit.pdf').read_bytes()).hexdigest()[:12]
 page=folder/'index.html'
 page.write_text(page.read_text(encoding='utf-8').replace('dra9on-cinema-press-kit.pdf"','dra9on-cinema-press-kit.pdf?v='+pdf_version+'"'),encoding='utf-8')


