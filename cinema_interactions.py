"""Content-addressed, dependency-free motion for the existing public layouts."""
from hashlib import sha256


def inject_cinema_interactions(out, base_path=''):
    assets = []
    for name in ('cinema-motion.css', 'cinema-motion.js'):
        content = (out / name).read_bytes()
        stem, suffix = name.rsplit('.', 1)
        target = f'{stem}.{sha256(content).hexdigest()[:12]}.{suffix}'
        (out / 'assets' / 'build' / target).write_bytes(content)
        url = f'{base_path}/assets/build/{target}'
        assets.append(f'<link rel="stylesheet" href="{url}">' if suffix == 'css'
                      else f'<script src="{url}" defer></script>')
    for page in out.rglob('*.html'):
        document = page.read_text(encoding='utf-8')
        document = document.replace('</head>', ''.join(assets) + '</head>', 1)
        page.write_text(document, encoding='utf-8')
