"""The game's English label encoding, and replacing labels inside its 'st2e' text files.

st2e layout (offsets in bytes):
  0   'st2e'
  4   u32 string count N, u32 4, u32 32 (offset of the ID list)
  20  u32 offset T of the text section
  32  N x u32 string IDs
  T   u32 1 (groups), u32 12 (group offset), u32 text length L (from T)
  T+12  u32 N, then N+1 x u32 string offsets relative to T+12; the last one marks the end of the strings
  Strings are NUL-terminated; the file is zero-padded to a multiple of 4.
"""
from hashlib import sha256
import struct

_GLYPHS = {' ': 0x04}
_GLYPHS.update({chr(ord('A') + i): 0x20 + i for i in range(26)})
_GLYPHS.update({chr(ord('a') + i): 0x3A + i for i in range(26)})
_GLYPHS.update({str(d): 0x85 + d for d in range(1, 10)})


def encode(text):
    """Encode a label in the game's glyph codes, NUL-terminated. Letters, spaces and 1-9 only."""
    if not text:
        raise ValueError('empty label')
    bad = sorted({c for c in text if c not in _GLYPHS})
    if bad:
        raise ValueError(f'{text!r}: unsupported characters {bad}')
    return bytes(_GLYPHS[c] for c in text) + b'\0'


def _layout(raw):
    if raw[:4] != b'st2e':
        raise ValueError('not an st2e text file')
    count, stride, ids_at = struct.unpack_from('<III', raw, 4)
    text_at, = struct.unpack_from('<I', raw, 20)
    groups, group_rel, text_len = struct.unpack_from('<III', raw, text_at)
    base = text_at + group_rel
    if stride != 4 or groups != 1 or struct.unpack_from('<I', raw, base)[0] != count:
        raise ValueError('unexpected st2e layout')
    ids = struct.unpack_from(f'<{count}I', raw, ids_at)
    offsets = list(struct.unpack_from(f'<{count + 1}I', raw, base + 4))
    if base + offsets[-1] != text_at + text_len:
        raise ValueError('unexpected st2e bounds')
    return ids, offsets, base, text_at


def replace_labels(raw, changes, source_sha256=None):
    """Return raw with each {string_id: (old_text, new_text)} replaced; old text must match exactly."""
    if source_sha256 and sha256(raw).hexdigest() != source_sha256:
        raise ValueError('text file differs from the supported game version')
    ids, offsets, base, text_at = _layout(raw)
    edits = {}
    for string_id, (old, new) in changes.items():
        start = offsets[ids.index(string_id)]
        before, after = encode(old), encode(new)
        if raw[base + start:base + start + len(before)] != before:
            raise ValueError(f'string {string_id} is not {old!r}')
        if offsets[:-1].count(start) > 1:
            raise ValueError(f'string {string_id} is shared with another ID')
        edits[start] = (len(before), after)

    strings = raw[base:base + offsets[-1]]  # group header, offset table, then the strings
    cuts = sorted(edits)
    out = bytearray(strings[:offsets[0]])
    cursor = offsets[0]
    for start in cuts:
        out += strings[cursor:start]
        old_len, after = edits[start]
        out += after
        cursor = start + old_len
    out += strings[cursor:]
    new_offsets = [offset + sum(len(edits[s][1]) - edits[s][0] for s in cuts if s < offset) for offset in offsets]
    struct.pack_into(f'<{len(new_offsets)}I', out, 4, *new_offsets)

    result = bytearray(raw[:base]) + out
    struct.pack_into('<I', result, text_at + 8, len(result) - text_at)
    result += b'\0' * (-len(result) % 4)
    return bytes(result)
