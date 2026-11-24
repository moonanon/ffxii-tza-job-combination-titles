import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hybrid_job_titles import build  # noqa: E402


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data' / 'job-titles.json').read_text(encoding='utf-8'))

    def test_all_pairs_unique_and_vanilla(self):
        pairs = {frozenset(h['jobs']) for h in self.data['hybrids']}
        self.assertEqual(len(pairs), 66)
        self.assertTrue(all(len(p) == 2 and p <= set(build.NATIVE_JOBS) for p in pairs))
        self.assertEqual(len({h['title'] for h in self.data['hybrids']}), 66)

    def test_titles_encodable(self):
        for h in self.data['hybrids']:
            self.assertLessEqual(len(build.encode_label(h['title'])), 24, h['title'])

    def test_stub_jumps_land_on_fallback(self):
        stub, imm = build.stub_template()
        self.assertEqual(stub[-3:], b'\x41\xff\xe3')
        self.assertEqual(set(imm), {'table', 'cont1', 'cont2', 'lookup'})

    def test_lua_generated(self):
        lua = build.build_lua(self.data)
        self.assertIn('-- Paladin', lua)
        self.assertIn('{232,66,52,218,255}', lua)  # CALL 0x2F9860 from 0x556419


if __name__ == '__main__':
    unittest.main()


class LabelsTest(unittest.TestCase):
    def make(self, labels):
        from hybrid_job_titles.labels import encode
        import struct
        ids = list(labels)
        strings = b''.join(encode(t) for t in labels.values())
        n = len(ids)
        text_at = 32 + 4 * n
        table = 4 + 4 * (n + 1)
        offsets, pos = [], table
        for t in labels.values():
            offsets.append(pos); pos += len(encode(t))
        offsets.append(pos)
        group = struct.pack('<I', n) + struct.pack(f'<{n + 1}I', *offsets) + strings
        raw = (b'st2e' + struct.pack('<IIII', n, 4, 32, 0) + struct.pack('<I', text_at) + b'\0' * 8
               + struct.pack(f'<{n}I', *ids) + struct.pack('<III', 1, 12, 12 + len(group)) + group)
        return raw + b'\0' * (-len(raw) % 4)

    def test_replace_shifts_later_strings(self):
        from hybrid_job_titles.labels import replace_labels
        raw = self.make({10100: 'White Mage', 10101: 'Uhlan', 10102: 'Machinist'})
        out = replace_labels(raw, {10101: ('Uhlan', 'Lancer')})
        self.assertEqual(out, self.make({10100: 'White Mage', 10101: 'Lancer', 10102: 'Machinist'}))

    def test_wrong_source_text_refused(self):
        from hybrid_job_titles.labels import replace_labels
        raw = self.make({10101: 'Uhlan'})
        with self.assertRaises(ValueError):
            replace_labels(raw, {10101: ('Lancer', 'Uhlan')})
