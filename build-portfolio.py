"""Build the static portfolio and its searchable watch pages."""
import json,re,pathlib,html,argparse
root=pathlib.Path(__file__).resolve().parent
from urllib.parse import urlsplit
import shutil
p = argparse.ArgumentParser()
p.add_argument('--origin', required=True, help='Host origin, e.g. https://username.github.io')
p.add_argument('--base-path', default='', help='Project path, e.g. /dra9on-cinema; empty for a custom domain')
p.add_argument('--output', default='dist', help='Build output directory')
args = p.parse_args()
host = urlsplit(args.origin)
if host.scheme not in {'http', 'https'} or not host.netloc or host.path not in {'', '/'} or host.query or host.fragment or host.username or host.password:
    p.error('--origin must be an HTTP(S) origin without a path, query, or credentials')
base_path = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
if not re.fullmatch(r'(?:/[A-Za-z0-9_-][A-Za-z0-9._-]*)*', base_path):
    p.error('--base-path must contain ordinary URL path segments')
origin = args.origin.rstrip('/') + base_path
out = root / args.output
out.mkdir(parents=True, exist_ok=True)
shutil.copytree(root / 'site-assets', out, dirs_exist_ok=True)
data=json.loads((root/'portfolio-data.json').read_text(encoding='utf-8'))
esc=lambda s:html.escape(str(s),quote=True)
icons={'play':'<path d="m8 4 13 8-13 8z" fill="currentColor" stroke="none"/>','arrow':'<path d="M5 12h14m-6-6 6 6-6 6"/>','plus':'<path d="M12 5v14M5 12h14"/>','search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>','left':'<path d="m15 5-7 7 7 7"/>','right':'<path d="m9 5 7 7-7 7"/>','close':'<path d="m6 6 12 12M6 18 18 6"/>','external':'<path d="M14 4h6v6M20 4 10 14M10 4H4v16h16v-6"/>'}
def icon(n):return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons[n]+'</svg>'
custom={'4f6Zguf7c2M':'FALL 707 시즌 1 — 몰아보기','dGnjxL64HHY':'목포진의 밤 — 시즌 2 EP.1–2','pBti3GK2nkc':'조선귀살특무대','j95SyBMQiNI':'검은 마탑의 청소부','VCd4T8sLFjg':'타깃 : 부재중','OLSjUGODAeE':'그녀가 다시 눈을 뜨다','L53hio-gtv0':'죽지도 않는 미친X과 n번째 저승사자 2','Byh-aCKSDgo':'악령퇴마 관리과 퇴마사','UxrkaAvtsNI':'아이언 레버넌트','iVwqj1gUPDY':'죽지도 않는 미친X과 n번째 저승사자'}
works=[]
for v in data['videos']:
 title=v['title'];fall='FALL 707' in title;season=2 if 'S2' in title else 1 if fall else 0
 m=re.search(r'EP\.?\s*(\d+)',title);ep=int(m.group(1)) if m else 0
 cat='full' if 'Full Movie' in title else 'trailer' if 'TRAILER' in title else f's{season}' if fall else 'original'
 name=custom.get(v['id'],title.split('|')[-1].strip());label={'full':'FULL MOVIE','trailer':'TRAILER','s1':f'S1 · EP.{ep:02}','s2':f'S2 · EP.{ep:02}','original':'ORIGINAL FILM'}[cat]
 slug=f'fall-707-s{season}-ep{ep}' if cat in ['s1','s2'] else 'fall-707-season-1-full' if v['id']=='4f6Zguf7c2M' else 'fall-707-season-2-ep1-2' if v['id']=='dGnjxL64HHY' else 'film-'+v['id']
 paragraphs=[x.strip() for x in v.get('description','').split('\n\n') if x.strip()]
 korean=[x for x in paragraphs if re.search('[가-힣]',x) and not re.search(r'https?://|CHAPTERS|Business|▶|#',x)]
 summary=korean[0] if korean else f'DRA9ON CINEMA의 {name}. 공식 채널에서 공개한 오리지널 영상 작품을 감상하세요.'
 summary=summary.split('\nA Korean')[0].split('\nDRA9ON CINEMA')[0].strip()
 if len(summary)>420:summary=summary[:417].rsplit(' ',1)[0]+'…'
 works.append({**{k:v.get(k) for k in ['id','title','duration','uploadDate','seconds']},'name':name,'category':cat,'season':season,'episode':ep,'label':label,'path':f'/watch/{slug}/','image':f'/assets/portfolio/{v["id"]}.jpg','summary':summary})
byid={v['id']:v for v in works};s1=sorted([v for v in works if v['category']=='s1'],key=lambda v:v['episode']);s2=sorted([v for v in works if v['category']=='s2'],key=lambda v:v['episode'])
(out/'catalog.js').write_text('window.PORTFOLIO = '+json.dumps(works,ensure_ascii=False).replace('</','<\\/')+';\n',encoding='utf-8')
brand='<a href="/" class="wordmark" aria-label="DRA9ON CINEMA 홈"><span>DRA9ON</span><span class="brand-sub">CINEMA</span></a>'
def header(home=False):
 nav='<button class="nav-link active" data-view="all" aria-current="page">홈</button><button class="nav-link" data-view="fall">FALL 707</button><button class="nav-link" data-view="original">작품집</button><a class="nav-link" href="#about">ABOUT</a>' if home else '<a class="nav-link" href="/">홈</a><a class="nav-link" href="/#episodes">FALL 707</a><a class="nav-link" href="/#originals">작품집</a><a class="nav-link" href="/#about">ABOUT</a>'
 search=f'<div class="search-wrap" id="search-wrap"><button class="icon-button" id="search-toggle" aria-label="작품 검색" aria-expanded="false">{icon("search")}</button><input type="search" id="search" placeholder="작품, 에피소드 검색" aria-label="작품 또는 에피소드 검색" autocomplete="off" hidden></div>' if home else ''
 return f'<a class="skip-link" href="#main">콘텐츠로 바로 가기</a><header class="header">{brand}<nav class="nav" aria-label="주 메뉴">{nav}</nav><div class="header-actions">{search}<a class="channel-button" href="https://www.youtube.com/@dra9oncinema" target="_blank" rel="noopener noreferrer">YouTube {icon("external")}</a></div></header>'
def footer():return f'<footer>{brand}<p>AI로 세계관을 실사화하는 크리에이터.<br><span>© 2026 DRA9ON CINEMA. All rights reserved.</span><br><span>작품·이미지·텍스트의 무단 복제, 재업로드 및 상업적 이용을 금합니다. 이용 문의는 이메일로 연락해 주세요.</span></p><div class="footer-links"><a href="https://www.youtube.com/@dra9oncinema" target="_blank" rel="noopener noreferrer">YouTube {icon("external")}</a><a href="mailto:guletlaru05@gmail.com">협업 문의 {icon("arrow")}</a></div></footer>'
def card(v):return f'<article class="card"><a class="card-open" href="{v["path"]}" data-detail="{v["id"]}" aria-label="{esc(v["label"]+" "+v["name"])} 상세 보기"><div class="card-image"><img src="{v["image"]}" alt="{esc(v["name"])} 공식 썸네일" width="720" height="405" loading="lazy"><span class="duration">{esc(v["duration"] or "")}</span><span class="card-hover-play"><span>{icon("play")}</span></span></div><p class="card-label">{v["label"]}</p><h3 class="card-name">{esc(v["name"])}</h3></a><button class="card-save" data-save="{v["id"]}" aria-label="{esc(v["name"])} 찜하기" aria-pressed="false">{icon("plus")}</button></article>'
def shelf(id,title,subtitle,items):return f'<section class="shelf" id="{id}" aria-labelledby="{id}-title"><div class="shelf-heading"><div><p class="section-eyebrow">{subtitle}</p><h2 class="shelf-title" id="{id}-title">{title}</h2></div><div class="shelf-controls"><button data-scroll="{id}-track" data-direction="-1" aria-label="{title} 이전 보기">{icon("left")}</button><button data-scroll="{id}-track" data-direction="1" aria-label="{title} 다음 보기">{icon("right")}</button></div></div><div class="shelf-track" id="{id}-track">'+''.join(card(v) for v in items)+'</div></section>'
def head(title,desc,path='/',schema=None):
 schema_text=json.dumps(schema,ensure_ascii=False).replace('</','<\\/') if schema else ''
 return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101011"><meta name="referrer" content="strict-origin-when-cross-origin"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index,follow,max-image-preview:large,max-video-preview:-1"><link rel="canonical" href="{origin}{path}"><meta property="og:type" content="{'website' if path=='/' else 'video.episode'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{origin}{path}"><meta property="og:site_name" content="DRA9ON CINEMA"><meta property="og:locale" content="ko_KR"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23101011'/%3E%3Cpath d='M8 7h7c13 0 13 18 0 18H8zm5 4v10h2c7 0 7-10 0-10z' fill='%23ed233a'/%3E%3C/svg%3E"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;0,800;1,700;1,800&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/portfolio.css"><script src="/catalog.js" defer></script><script src="/portfolio.js" defer></script><script type="application/ld+json">{schema_text}</script></head>'''
dialogs=f'''<dialog id="detail-dialog" aria-labelledby="detail-title"><div class="detail-art"><img id="detail-image" alt=""><div class="detail-shade"></div><button class="icon-button close-button" id="detail-close" aria-label="상세 정보 닫기">{icon('close')}</button></div><div class="detail-body"><p class="section-eyebrow" id="detail-label"></p><h2 id="detail-title"></h2><div class="detail-actions"><button class="button button-white" id="detail-play">{icon('play')}지금 재생</button><button class="save-button" id="detail-save" aria-pressed="false"></button><a class="icon-button" id="detail-page" aria-label="작품 전용 페이지 열기">{icon('external')}</a></div><p class="detail-description" id="detail-description"></p><div class="detail-footer"><span id="detail-meta"></span><button class="text-button" id="detail-share">링크 복사 {icon('external')}</button></div></div></dialog><dialog id="player-dialog" aria-labelledby="player-title"><div class="player-header"><div><p class="section-eyebrow">DRA9ON CINEMA · NOW PLAYING</p><h2 id="player-title"></h2></div><button class="icon-button" id="player-close" aria-label="영상 닫기">{icon('close')}</button></div><div id="player-mount"></div><div class="player-footer"><a id="player-youtube" target="_blank" rel="noopener noreferrer">YouTube에서 보기 {icon('external')}</a><a id="player-next">다음 작품 {icon('arrow')}</a></div></dialog><div class="toast" id="toast" role="status" aria-live="polite"></div>'''
schema={'@context':'https://schema.org','@type':'ProfilePage','name':'DRA9ON CINEMA — 낙하 707 · FALL 707 영상 포트폴리오','url':origin+'/','mainEntity':{'@type':'Organization','name':'DRA9ON CINEMA','description':'AI로 세계관을 실사화하는 크리에이터. 낙하707: 리부트(FALL 707: REBOOT)와 오리지널 AI 영화 제작.','url':origin+'/','sameAs':['https://www.youtube.com/@dra9oncinema']}}
latest=s2[-1];first=s1[0]
main=f'''<body data-page="home">{header(True)}<main id="main"><section class="hero" aria-labelledby="hero-title" id="hero"><img class="hero-image" src="/assets/portfolio/hero.jpg" width="1280" height="720" alt="FALL 707 REBOOT 시즌 2 — 민 대위" fetchpriority="high"><div class="hero-shade"></div><div class="hero-content"><p class="eyebrow"><span class="original-mark">D9</span> DRA9ON CINEMA ORIGINAL</p><p class="hero-kicker">밀리터리 × 판타지 × 오컬트</p><h1 id="hero-title"><span class="hero-korean">FALL</span><span class="hero-number">707</span></h1><p class="hero-english">FALL 707 : REBOOT</p><p class="hero-tagline">낯선 시대에 떨어졌다.<br>살아남는 방식은, 변하지 않았다.</p><p class="hero-description">현대의 특수부대원이 조선에 떨어진다.<br>두 시대가 충돌하는 오리지널 시리즈, 〈낙하 707: 리부트〉.</p><div class="hero-buttons"><button class="button button-white" data-play="{first['id']}">{icon('play')}1화부터 보기</button><a class="button button-glass" href="#episodes">에피소드 보기</a></div><div class="hero-meta"><span>2026</span><span>시즌 1–2</span><span>AI ORIGINAL SERIES</span></div></div><a class="new-episode" href="{latest['path']}"><span class="live-label">최신 에피소드</span><strong>S{latest['season']} EP.{latest['episode']:02}</strong><span>{esc(latest['name'])}</span>{icon('arrow')}</a><div class="hero-bottom"><span>INDEPENDENT VISION. CINEMATIC STORIES.</span><span>01 — SELECTED SERIES</span></div></section><div class="catalog" id="catalog"><div class="filters" aria-label="작품 분류"><button class="filter active" data-category="all" aria-pressed="true">전체 작품</button><button class="filter" data-category="s1" aria-pressed="false">시즌 1</button><button class="filter" data-category="s2" aria-pressed="false">시즌 2</button><button class="filter" data-category="full" aria-pressed="false">몰아보기</button><button class="filter" data-category="original" aria-pressed="false">오리지널</button><button class="filter saved-filter" data-category="saved" aria-pressed="false">찜한 작품</button><span class="filter-caption">{len(works):02} FILMS & EPISODES</span></div><div id="home-rows">'''
main+=shelf('episodes','FALL 707 · 시즌 2','THE STORY CONTINUES',s2)+shelf('season-one','모든 이야기의 시작, 시즌 1','FALL 707 : REBOOT',s1)
main+=f'<section class="feature-strip"><div><p class="section-eyebrow">ONE NIGHT. ONE COMPLETE STORY.</p><h2>한 편의 영화처럼.</h2><p>에피소드 사이의 기다림 없이, FALL 707을 연속으로.</p><a class="button button-white" href="{byid["4f6Zguf7c2M"]["path"]}">{icon("play")}시즌 1 몰아보기</a></div><a href="{byid["4f6Zguf7c2M"]["path"]}" class="feature-art"><img src="/assets/portfolio/4f6Zguf7c2M.jpg" alt="FALL 707 시즌 1 풀무비" width="720" height="405" loading="lazy"></a></section>'
main+=shelf('originals','세계관은 계속 넓어진다','MORE FROM DRA9ON CINEMA',[v for v in works if v['category']=='original'])+shelf('more-cuts','한 번 더, 깊이 빠져들다','FULL MOVIES & TRAILER',[v for v in works if v['category'] in ['full','trailer']])
main+='</div><section id="browse-results" hidden aria-labelledby="browse-title"><h1 id="browse-title"></h1><p id="result-count" aria-live="polite"></p><div class="results-grid" id="results-grid"></div><div class="empty-state" id="empty-state" hidden><h2>아직 작품이 없어요.</h2><p>다른 검색어를 입력하거나 보고 싶은 작품의 + 버튼을 눌러주세요.</p><button class="button button-white" id="reset-browse">전체 작품 보기</button></div></section></div>'
main+=f'<section class="about-section" id="about"><div class="about-copy"><p class="section-eyebrow">BEHIND THE FRAME</p><h2>상상을, 장면으로.<br><span>이야기를, 세계관으로.</span></h2><p>DRA9ON CINEMA는 AI로 세계관을 실사화하는 크리에이터입니다. 밀리터리 판타지 오컬트 스릴러 〈낙하707: 리부트〉(FALL 707: REBOOT)를 비롯해, 장르 영화의 새로운 가능성을 실험합니다.</p><div class="about-tags"><span>AI FILMMAKING</span><span>WORLD BUILDING</span><span>VISUAL STORYTELLING</span></div><div class="about-links"><a class="button button-white" href="mailto:guletlaru05@gmail.com">프로젝트 함께하기 {icon("arrow")}</a><a class="text-button" href="https://www.youtube.com/@dra9oncinema" target="_blank" rel="noopener noreferrer">채널에서 더 보기 {icon("external")}</a></div></div></section></main>{footer()}{dialogs}</body></html>'
(out/'index.html').write_text(head('DRA9ON CINEMA | 낙하 707 리부트 · FALL 707','드래곤시네마의 AI 밀리터리 판타지 〈낙하 707: 리부트〉(낙하707, FALL 707: REBOOT). 시즌 1·2의 에피소드와 몰아보기, 오리지널 AI 영화를 한곳에서 감상하세요.',schema=schema)+main,encoding='utf-8')
paths=['/']
for v in works:
 seq=s1 if v['category']=='s1' else s2 if v['category']=='s2' else [w for w in works if w['category']==v['category']]
 pos=seq.index(v);nextv=seq[pos+1] if pos+1<len(seq) else s2[0] if v['category']=='s1' else None
 page_title=f'{"낙하 707 리부트 · FALL 707 " if v["season"] else ""}{v["label"]} {v["name"]} | DRA9ON CINEMA'
 schema={'@context':'https://schema.org','@type':'VideoObject','name':v['title'],'description':v['summary'],'thumbnailUrl':[origin+v['image']],'embedUrl':f'https://www.youtube-nocookie.com/embed/{v["id"]}','url':origin+v['path'],'creator':{'@type':'Organization','name':'DRA9ON CINEMA','sameAs':'https://www.youtube.com/@dra9oncinema'}}
 if v.get('uploadDate'):schema['uploadDate']=v['uploadDate']
 if v.get('seconds'):schema['duration']=f'PT{v["seconds"]}S'
 body=f'<body class="watch-page" data-page="watch" data-id="{v["id"]}">{header()}<main id="main" class="watch-main"><nav class="breadcrumb" aria-label="경로"><a href="/">DRA9ON CINEMA</a><span>/</span><a href="/{"#episodes" if v["season"] else "#originals"}">{"FALL 707 REBOOT" if v["season"] else "오리지널 작품"}</a><span>/</span><span>{v["label"]}</span></nav><div class="watch-layout"><div class="watch-primary"><div class="watch-screen"><iframe src="https://www.youtube-nocookie.com/embed/{v["id"]}?rel=0&amp;playsinline=1" title="{esc(v["title"])}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><div class="watch-heading"><div><p class="section-eyebrow">{v["label"]} · {v["duration"] or ""}</p><h1>{esc(v["name"])}</h1></div><button class="save-button" data-save="{v["id"]}" aria-label="{esc(v["name"])} 찜하기" aria-pressed="false">{icon("plus")}찜하기</button></div><p class="watch-description">{esc(v["summary"])}</p><div class="watch-meta"><span>DRA9ON CINEMA</span><span>{esc((v.get("uploadDate") or "")[:10])}</span><span>{v["duration"] or ""}</span></div><div class="watch-actions"><a class="text-button" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener noreferrer">YouTube에서 보기 {icon("external")}</a><button class="text-button" data-share="{v["id"]}">이 작품 공유하기 {icon("external")}</button></div><p class="playback-hint">플레이어에서 재생이 제한되면 ‘YouTube에서 보기’를 눌러주세요.</p>'
 if nextv:body+=f'<a class="next-episode" href="{nextv["path"]}"><img src="{nextv["image"]}" alt="" width="160" height="90"><div><p class="section-eyebrow">다음 이야기 · {nextv["label"]}</p><h2>{esc(nextv["name"])}</h2></div>{icon("arrow")}</a>'
 body+='</div><aside class="watch-episodes" aria-label="관련 작품"><h2>'+('에피소드' if v['season'] else '다른 작품')+'</h2>'
 for sibling in seq:
  current=' aria-current="page"' if sibling==v else ''
  body+=f'<a href="{sibling["path"]}" class="episode-item{" active" if sibling==v else ""}"{current}><img src="{sibling["image"]}" alt="" width="160" height="90" loading="lazy"><div><span>{sibling["label"]} · {sibling["duration"] or ""}</span><strong>{esc(sibling["name"])}</strong></div></a>'
 body+=f'</aside></div></main>{footer()}<div class="toast" id="toast" role="status" aria-live="polite"></div></body></html>'
 folder=out/v['path'].strip('/');folder.mkdir(parents=True,exist_ok=True);(folder/'index.html').write_text(head(page_title,('낙하707: 리부트. ' if v['season'] else '')+v['summary'][:170],v['path'],schema)+body,encoding='utf-8');paths.append(v['path'])
(out/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n',encoding='utf-8')
(out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(origin+p)}</loc></url>' for p in paths)+'</urlset>',encoding='utf-8')
(out/'404.html').write_text(head('페이지를 찾을 수 없습니다 | DRA9ON CINEMA','홈에서 다른 작품을 만나보세요.')+f'<body class="watch-page">{header()}<main class="not-found"><p class="section-eyebrow">404 · SCENE NOT FOUND</p><h1>이 장면은 찾을 수 없어요.</h1><a href="/" class="button button-white">작품 둘러보기</a></main>{footer()}</body></html>',encoding='utf-8')
print(json.dumps({'works':len(works),'pages':len(paths),'seasons':{'1':len(s1),'2':len(s2)},'origin':origin}))

from localization import localize_site
from link_page import build_links
build_links(out, origin, works, head, icon)
localize_site(out, works, origin, base_path)
# Public ownership proof for the owner's Google and Naver webmaster properties.
verification_tag = (
 '<meta name="google-site-verification" content="PYrvbyrAOQQDNSZzhI9SdsjlhtRdl0l_tHM6tUelxnU">'
 '<meta name="naver-site-verification" content="f8539e272fb651d0f1d9c63533879922377ddd47">'
)
for homepage in ('index.html', 'en/index.html'):
 page = out / homepage
 document = page.read_text(encoding='utf-8')
 page.write_text(document.replace('</head>', verification_tag + '</head>', 1), encoding='utf-8')
print('Built Korean and English routes with versioned assets.')

(out / '.nojekyll').touch()
