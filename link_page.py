"""Build the social-profile landing page from the same film catalog."""
from html import escape


def build_links(out, origin, works, head, icon):
    latest = max((v for v in works if v['category'] in ('s1', 's2')),
                 key=lambda v: (v['season'], v['episode']))
    full = next(v for v in works if v['id'] == '4f6Zguf7c2M')
    schema = {'@context': 'https://schema.org', '@type': 'WebPage',
              'name': 'DRA9ON CINEMA | Official Links', 'url': origin + '/links/'}
    body = f'''<body class="links-page"><main class="links-main" id="main">
<header class="links-header"><a class="links-wordmark" href="/" aria-label="DRA9ON CINEMA 홈">DRA9ON<span>CINEMA</span></a><div class="header-actions"></div></header>
<p class="links-eyebrow">INDEPENDENT AI FILMMAKER</p>
<h1>상상을, 장면으로.</h1><p class="links-intro">FALL 707과 오리지널 영화들을 만나보세요.</p>
<nav class="bio-links" aria-label="공식 링크">
<a class="bio-feature" href="{latest['path']}"><img src="{latest['image']}" width="720" height="405" alt="{escape(latest['name'])}"><div class="bio-feature-shade"></div><div class="bio-feature-copy"><span class="bio-label">LATEST EPISODE · S{latest['season']} EP.{latest['episode']:02}</span><strong>최신화 보기</strong><span>{escape(latest['name'])}</span></div><span class="bio-arrow">{icon('play')}</span></a>
<a class="bio-row" href="{full['path']}"><span class="bio-index">01</span><span><strong>시즌 1 풀버전</strong><small>FALL 707 · FULL MOVIE · {full['duration']}</small></span>{icon('arrow')}</a>
<a class="bio-row" href="/"><span class="bio-index">02</span><span><strong>전체 작품 둘러보기</strong><small>OFFICIAL WEBSITE</small></span>{icon('arrow')}</a>
<a class="bio-row" href="https://www.youtube.com/@dra9oncinema" target="_blank" rel="noopener noreferrer"><span class="bio-index">03</span><span><strong>YouTube</strong><small>@dra9oncinema</small></span>{icon('external')}</a>
<a class="bio-row" href="mailto:guletlaru05@gmail.com"><span class="bio-index">04</span><span><strong>협업 문의</strong><small>LET’S CREATE SOMETHING.</small></span>{icon('arrow')}</a>
</nav><p class="links-signoff">© 2026 DRA9ON CINEMA. All rights reserved.</p></main></body></html>'''
    directory = out / 'links'
    directory.mkdir(exist_ok=True)
    (directory / 'index.html').write_text(head('DRA9ON CINEMA | 공식 링크',
        'FALL 707 최신화, 시즌 1 풀버전, 공식 유튜브와 협업 문의를 한곳에서.',
        '/links/', schema) + body, encoding='utf-8')
