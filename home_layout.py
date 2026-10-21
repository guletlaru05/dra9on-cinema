"""Remove repeated external video anchors from home, keeping viewing shelves."""
import re
from html import escape


HOME_EXCLUDED_TITLE = re.compile(r'몰아보기|풀버전|(?<![A-Za-z])(?:FULL|OST)(?![A-Za-z])', re.I)


def is_home_episode(work):
    """Filter only home presentation; never remove records from the catalog."""
    return (bool(re.fullmatch(r's[1-9][0-9]*', work.get('category', '')))
            and int(work.get('episode') or 0) > 0
            and not HOME_EXCLUDED_TITLE.search(str(work.get('title') or '')))


def home_episode_card(work):
    """Keep controls outside the player so the iframe receives every click."""
    video_id = escape(work['id'], quote=True)
    title = escape(work['title'], quote=True)
    name = escape(work['name'], quote=True)
    label = escape(work['label'], quote=True)
    path = escape(work['path'], quote=True)
    duration = escape(work.get('duration') or '', quote=True)
    return (
        f'<article class="card card-inline" data-home-episode="{video_id}">'
        '<div class="card-image home-player">'
        f'<iframe data-home-player data-home-src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&amp;playsinline=1&amp;autoplay=0" '
        f'title="{title}" width="720" height="405" loading="lazy" '
        'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
        f'<a class="card-open" href="{path}" data-detail="{video_id}" '
        f'aria-label="{label} {name} 상세 보기"><p class="card-label">{label}'
        f'<span class="duration card-inline-duration">{duration}</span></p>'
        f'<h3 class="card-name">{name}</h3></a>'
        f'<button class="card-save" data-save="{video_id}" aria-label="{name} 찜하기" aria-pressed="false">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button></article>'
    )

def contain_hero_media(document):
    """Keep the poster, silent preview and shade in one independently sized frame."""
    if 'class="hero-media"' in document:
        return document
    document,count=re.subn(r'(<img\b[^>]*class="hero-image"[^>]*>)(\s*<div class="hero-shade"></div>)',r'<div class="hero-media">\1\2</div>',document,count=1)
    if count!=1:
        raise ValueError('Home must have one poster and shade to group into its media frame')
    return document

def simplify_home_links(document):
    allowed=[(m.start(),m.end()) for m in re.finditer(r'<(?:header|footer)\b[^>]*>[\s\S]*?</(?:header|footer)>',document)]
    hero=re.search(r'<p class="hero-subscribe">[\s\S]*?</p>',document)
    if hero:allowed.append((hero.start(),hero.end()))
    def replace(match):
        if any(start<=match.start()<end for start,end in allowed):return match.group(0)
        # Preserve the channel name in the numeric collaboration stat, without a link.
        text=re.sub('<[^>]+>','',match.group(1)).strip()
        return '<span>YouTube</span>' if text=='YouTube' else ''
    return re.sub(r'<a\b[^>]*href="https://(?:www\.)?(?:youtube\.com|youtu\.be)/[^"]*"[^>]*>([\s\S]*?)</a>',replace,document)
