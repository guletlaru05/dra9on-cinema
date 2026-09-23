"""Read JPEG dimensions with the standard library (no deployment dependency)."""
from struct import unpack

def jpeg_size(path):
    with open(path, 'rb') as image:
        if image.read(2) != b'\xff\xd8':
            raise ValueError(f'Not a JPEG: {path}')
        while True:
            byte = image.read(1)
            if not byte:
                raise ValueError(f'JPEG dimensions missing: {path}')
            if byte != b'\xff':
                continue
            marker = image.read(1)
            while marker == b'\xff':
                marker = image.read(1)
            if marker in (b'\xd8', b'\xd9'):
                continue
            length = unpack('>H', image.read(2))[0]
            if marker and marker[0] in (0xC0, 0xC1, 0xC2):
                _, height, width = unpack('>BHH', image.read(5))
                return width, height
            image.seek(length - 2, 1)
