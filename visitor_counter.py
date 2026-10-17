"""Add cookie-free landing-event totals without browser identities."""
from hashlib import sha256
from html import escape


def inject_visitor_counter(out, base_path=''):
    """Share one versioned widget across public pages; exclude the study library."""
    assets = {}
    asset_dir = out / 'assets' / 'build'
    asset_dir.mkdir(parents=True, exist_ok=True)
    for extension in ('css',):
        content = (out / f'visitors.{extension}').read_bytes()
        filename = f'visitors.{sha256(content).hexdigest()[:12]}.{extension}'
        (asset_dir / filename).write_bytes(content)
        assets[extension] = f'{base_path}/assets/build/{filename}'

    for page in out.rglob('*.html'):
        relative = page.relative_to(out)
        if 'library' in relative.parts:
            continue
        language=relative.parts[0] if relative.parts[0] in ('en','ja','es') else 'ko'
        english = language!='ko'
        labels = {
            'label': 'Site visit statistics' if english else '사이트 방문 통계',
            'today': 'Today’s visits' if english else '오늘 방문',
            'total': 'Total visits' if english else '누적 방문',
            'note': ('Cookie-free landing events · Korea time'
                     if english else '쿠키 없는 외부 유입 횟수 · 한국 시간'),
            'detail': ('External or direct landing events since counting began. '
                       'No identifiers are used; these are not unique people or YouTube views.' if english else
                       '집계 시작 이후 외부 링크·직접 방문으로 들어온 횟수입니다. '
                       '식별자를 사용하지 않아 고유 방문자·실제 사람 수나 YouTube 조회수와 다릅니다.'),
            'status': 'Loading visit totals…' if english else '방문 집계를 불러오는 중…',
            'privacy': 'How visits are counted' if english else '집계 기준',
        }
        privacy_url = base_path + ('/en' if english else '') + '/privacy/'
        if language in ('ja','es'):
            from international_content import text
            labels={key:text(value,language) for key,value in labels.items()}
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
        resources = f'<link rel="stylesheet" href="{assets["css"]}">'
        document = document.replace('</header>', '</header>' + markup, 1)
        document = document.replace('</head>', resources + '</head>', 1)
        page.write_text(document, encoding='utf-8')
