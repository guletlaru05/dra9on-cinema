"""Split the existing watermarked atlas; never regenerate or retouch artwork."""
from pathlib import Path
from hashlib import sha256
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT/'site-assets/assets/notes/min-stickers-12-center-soft-wm.webp'
    target = ROOT/'site-assets/assets/stickers'
    target.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(source).convert('RGB')
    width, height = sheet.width // 3, sheet.height // 4
    assert width == height and sheet.size == (width * 3, height * 4)
    records = []
    for index in range(12):
        x, y = (index % 3) * width, (index // 3) * height
        tile = sheet.crop((x, y, x + width, y + height))
        files = []
        for size in (240, 360, 'full'):
            image = tile if size == 'full' else tile.resize((size, size), Image.Resampling.LANCZOS)
            name = f'min-{index + 1:02}-{size}.webp'
            image.save(target/name, 'WEBP', lossless=size == 'full', quality=92, method=6)
            files.append({'file': name, 'width': image.width, 'height': image.height, 'bytes': (target/name).stat().st_size})
        records.append({'index': index, 'crop': [x, y, x + width, y + height], 'files': files})
    inventory = {'source': source.relative_to(ROOT).as_posix(), 'sourceSha256': sha256(source.read_bytes()).hexdigest(), 'count': len(records), 'watermark': 'Existing pixels preserved; no watermark added or removed.', 'tiles': records}
    (target/'manifest.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'count': len(records), 'thumbnail240Bytes': sum(item['files'][0]['bytes'] for item in records), 'thumbnail360Bytes': sum(item['files'][1]['bytes'] for item in records)}))


if __name__ == '__main__':
    main()
