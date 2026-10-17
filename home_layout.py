"""Remove repeated external video anchors from home, keeping viewing shelves."""
import re

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
