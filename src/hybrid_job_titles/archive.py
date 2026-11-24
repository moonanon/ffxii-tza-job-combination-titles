"""Read-only access to single files inside the game's FFXII_TZA.vbf archive.

Layout: a header ('SRYK', header size, file count), one MD5 of each lower-cased path, one 32-byte record per file
(first block index, size, data offset), a NUL-separated name table, then one u16 stored length per 64 KiB block.
A block whose stored length is shorter than its real length is zlib-compressed; a stored length of 0 means 64 KiB.
The last 16 bytes of the file are the MD5 of the header.
"""
from hashlib import md5
from pathlib import Path
import struct
import zlib

BLOCK = 0x10000


class Archive:
    def __init__(self, path):
        self.path = Path(path)
        with self.path.open('rb') as f:
            magic, header_size, count = struct.unpack('<4sIQ', f.read(16))
            if magic != b'SRYK':
                raise ValueError(f'{self.path}: not a VBF archive')
            f.seek(0)
            header = f.read(header_size)
            f.seek(-16, 2)
            if md5(header).digest() != f.read(16):
                raise ValueError(f'{self.path}: header checksum mismatch')
        self._header = header
        hashes_at = 16
        records_at = hashes_at + 16 * count
        names_at = records_at + 32 * count
        names_size, = struct.unpack_from('<I', header, names_at)
        self._blocks_at = names_at + names_size
        self._index = {}
        for i in range(count):
            digest = header[hashes_at + 16 * i:hashes_at + 16 * (i + 1)]
            first_block, _, size, offset, _ = struct.unpack_from('<IIQQQ', header, records_at + 32 * i)
            self._index[digest] = (first_block, size, offset)

    def read(self, name):
        key = md5(name.replace('\\', '/').lower().encode()).digest()
        try:
            first_block, size, offset = self._index[key]
        except KeyError:
            raise KeyError(f'{name} is not in the archive') from None
        data = bytearray()
        with self.path.open('rb') as f:
            f.seek(offset)
            block = first_block
            while len(data) < size:
                want = min(BLOCK, size - len(data))
                stored, = struct.unpack_from('<H', self._header, self._blocks_at + 2 * block)
                stored = stored or BLOCK
                chunk = f.read(stored)
                if stored < want:
                    chunk = zlib.decompress(chunk)
                if len(chunk) != want:
                    raise ValueError(f'{name}: damaged block {block}')
                data += chunk
                block += 1
        return bytes(data)
