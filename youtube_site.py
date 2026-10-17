"""Materialize official thumbnails and render exact build-time API counts."""
from html import escape
from pathlib import Path
import re
from hashlib import sha256
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from youtube_sync import count_html, exact_count
from image_dimensions import jpeg_size


def prepare_images(works,out,root):
    for work in works:
        destination=out/work['image'].lstrip('/')
        if destination.is_file(): continue
        url=work.get('thumbnail') or ''
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.hostname not in {'i.ytimg.com','img.youtube.com'}:
            work['image']='/assets/og/og-ko.jpg'
            continue
        temporary=destination.with_suffix('.download')
        try:
            request=Request(url,headers={'User-Agent':'DRA9ON-site-build/1.0'})
            with urlopen(request,timeout=15) as response:
                content=response.read(2_000_001)
            if len(content)>2_000_000 or not content.startswith(b'\xff\xd8'):
                raise ValueError('Not a bounded JPEG')
            destination.parent.mkdir(parents=True,exist_ok=True)
            temporary.write_bytes(content)
            jpeg_size(temporary)
            temporary.replace(destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            # A genuine site artwork fallback is safer than a broken thumbnail;
            # the API entry and counts remain present, with no invented image.
            work['image']='/assets/og/og-ko.jpg'


def inject_youtube_counts(out,works,data,base_path=''):
    channel=data.get('channel',{})
    stylesheet=out/'youtube-api.css'
    content=stylesheet.read_bytes()
    filename='youtube-api.'+sha256(content).hexdigest()[:12]+'.css'
    (out/'assets/build'/filename).write_bytes(content)
    for page in out.rglob('*.html'):
        rel=page.relative_to(out).as_posix()
        if rel.startswith('library/'): continue
        en=rel.startswith('en/')
        lang='en' if en else 'ko'
        source=page.read_text(encoding='utf-8')
        count=channel.get('apiSubscriberCount')
        if rel in ('index.html','en/index.html'):
            stamp=escape(channel.get('apiStatisticsUpdatedAt') or '',quote=True)
            pattern=r'<div class="collaboration-stat">(?:(?!</div>).)*?<dt>(?P<title>(?:(?!</dt>).)*?youtube\.com(?:(?!</dt>).)*?)</dt>(?:(?!</div>).)*?</div>'
            def channel_stat(match):
                title=match.group('title')
                if exact_count(count) is None:
                    if channel.get('apiHiddenSubscriberCount'):
                        unavailable='Subscriber count hidden by channel' if en else '채널 구독자 수 비공개'
                    elif data.get('youtubeSync',{}).get('status')=='ready':
                        unavailable='API subscriber count unavailable' if en else 'API 구독자 수 제공 안 됨'
                    else:
                        unavailable='API connection pending' if en else 'API 연결 대기 중'
                    return f'<div class="collaboration-stat"><dt>{title}</dt><dd><span>{unavailable}</span></dd></div>'
                unit='subscribers' if en else '구독자'
                note=('YouTube Data API value; YouTube rounds subscriber counts down to 3 significant figures.' if en
                      else 'YouTube Data API 제공값 · YouTube가 유효숫자 3자리로 내림한 값입니다.')
                return (f'<div class="collaboration-stat" data-youtube-api-count data-updated-at="{stamp}">'
                        f'<dt>{title}</dt><dd><strong>{count}</strong><span>{unit}</span></dd>'
                        f'<p class="youtube-api-note">{note}<br><time datetime="{stamp}">{stamp}</time></p></div>')
            source,matched=re.subn(pattern,channel_stat,source,count=1,flags=re.S)
            assert matched==1, 'The YouTube collaboration stat could not be updated uniquely.'
            if exact_count(count) is not None:
                from collaboration import UPDATED_AT
                note=(f'YouTube uses the API retrieval time shown above. Other platform profiles: {UPDATED_AT}. Audiences may overlap.' if en
                      else f'YouTube는 위 API 갱신 시각 기준입니다. 다른 플랫폼은 {UPDATED_AT} 공개 프로필 기준이며 중복 이용자를 포함합니다.')
                source=re.sub(r'<p class="collaboration-count-note">.*?</p>','<p class="collaboration-count-note">'+note+'</p>',source,count=1,flags=re.S)
                # The homepage's featured work already has a compact metadata
                # row; show the raw subscriber value there without another bar.
                source=source.replace('<div class="hero-meta">','<div class="hero-meta">'+count_html(count,lang=lang,kind='subscribers',updated_at=channel.get('apiStatisticsUpdatedAt')),1)
        for work in works:
            raw=work.get('apiViewCount')
            if exact_count(raw) is None: continue
            value=count_html(raw,lang=lang,updated_at=work.get('apiStatisticsUpdatedAt'))
            if f'data-id="{work["id"]}"' in source:
                source=source.replace('<div class="watch-actions">','<p class="youtube-api-watch">'+value+'</p><div class="watch-actions">',1)
            pattern=r'(<a class="card-open"[^>]*data-detail="'+re.escape(work['id'])+ r'".*?</h3>)(</a>)'
            source=re.sub(pattern,lambda m:m[1]+value+m[2],source,flags=re.S)
        source=source.replace('</head>',f'<link rel="stylesheet" href="{base_path}/assets/build/{filename}"></head>',1)
        page.write_text(source,encoding='utf-8')
