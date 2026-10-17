"""Add the public, consent-based visit totals after language generation."""
from hashlib import sha256
from html import escape


def inject_visitor_counter(out, base_path=''):
    """Share one versioned widget across public pages; exclude the study library."""
    assets = {}
    asset_dir = out / 'assets' / 'build'
    asset_dir.mkdir(parents=True, exist_ok=True)
    for extension in ('js', 'css'):
        content = (out / f'visitors.{extension}').read_bytes()
        filename = f'visitors.{sha256(content).hexdigest()[:12]}.{extension}'
        (asset_dir / filename).write_bytes(content)
        assets[extension] = f'{base_path}/assets/build/{filename}'

    for page in out.rglob('*.html'):
        relative = page.relative_to(out)
        if 'library' in relative.parts:
            continue
        english = relative.parts[0] == 'en'
        labels = {
            'label': 'Site visit statistics' if english else '사이트 방문 통계',
            'today': 'Today' if english else '오늘 방문자',
            'total': 'Total visits' if english else '누적 방문자',
            'note': ('Consented visits · Once per browser each day · Korea time'
                     if english else '통계 동의 방문 · 브라우저당 하루 1회 · 한국 시간'),
            'detail': ('Total is the sum of daily browser visits since counting began, '
                       'not unique people, GA4 users or YouTube views.' if english else
                       '누적은 집계 시작일부터 일별 브라우저 방문을 더한 값으로, '
                       '실제 사람 수·GA4 사용자 수·YouTube 조회수와 다릅니다.'),
            'status': 'Loading visit totals…' if english else '방문 집계를 불러오는 중…',
            'privacy': 'How visits are counted' if english else '집계 기준',
        }
        privacy_url = base_path + ('/en' if english else '') + '/privacy/'
        markup = (
            f'<section class="site-visitors" data-site-visitors aria-label="{labels["label"]}">'
            '<span class="site-visitors-eyebrow" aria-hidden="true">VISITORS</span>'
            f'<dl class="site-visitors-counts" title="{escape(labels["detail"], quote=True)}">'
            f'<div><dt>{labels["today"]}</dt><dd data-visits-today>—</dd></div>'
            f'<div><dt>{labels["total"]}</dt><dd data-visits-total>—</dd></div></dl>'
            '<details class="site-visitors-info">'
            f'<summary aria-label="{labels["privacy"]}" title="{labels["privacy"]}">'
            '<span aria-hidden="true">i</span></summary>'
            '<div class="site-visitors-meta">'
            f'<p class="site-visitors-note">{labels["note"]}</p>'
            f'<p>{labels["detail"]}</p>'
            f'<p data-visits-status role="status" aria-live="polite">{labels["status"]}</p>'
            '<p data-visits-since></p>'
            f'<a href="{privacy_url}">{labels["privacy"]} ↗</a>'
            '</div></details></section>'
        )
        document = page.read_text(encoding='utf-8')
        assert 'data-site-visitors' not in document, f'Duplicate visitor widget: {relative}'
        # Keep totals in the first screen. The shared header is overlaid on the
        # home hero; other public pages and the compact links page use flow.
        assert '</header>' in document, f'Missing public header: {relative}'
        resources = (f'<link rel="stylesheet" href="{assets["css"]}">'
                     f'<script src="{assets["js"]}" defer></script>')
        document = document.replace('</header>', '</header>' + markup, 1)
        document = document.replace('</head>', resources + '</head>', 1)
        page.write_text(document, encoding='utf-8')
