"""Build the Hybrid Job Titles mod package.

    python -m hybrid_job_titles [--game "<FINAL FANTASY XII THE ZODIAC AGE folder>"] [--out dist]

Always writes the Lua hook (x64/scripts/HybridJobTitles.lua) with the 66 titles from data/job-titles.json.
With --game, also writes the job renames (Uhlan -> Lancer) as a patched menu_command.bin under
mods/deploy/ff12data/, read from your own FFXII_TZA.vbf.
"""
from pathlib import Path
import argparse
import json
import struct

from .labels import encode as encode_label, replace_labels

ROOT = Path(__file__).resolve().parents[2]

# Native job IDs (vanilla names), as in upstream patches/base_jobs.json.
NATIVE_JOBS = ['White Mage', 'Uhlan', 'Machinist', 'Red Battlemage', 'Knight', 'Monk', 'Time Battlemage',
               'Foebreaker', 'Archer', 'Black Mage', 'Bushi', 'Shikari']
LABEL_FILE = 'ps2data/image/ff12/test_battle/us/binaryfile/menu_command.bin'
LABEL_FILE_SHA256 = '7c800280d2ce0ae91ba04f1d7ca8169d0b4c8d7374c12663a0bad4e489d2358d'
LABEL_FIRST_ID = 10100  # string IDs 10100..10111 are the job names, in native order

# Steam 1.0.4.0, preferred image base 0x120000 (upstream native/hybrid_boards/sites.py, site 18 'pair_label').
SITE = 0x556419           # CALL 0x2F9860 inside the shared "Job/Job" formatter; R13D/R15D = the two jobs
CONTINUATION = 0x55641E
LOOKUP = 0x2F9860


def stub_template():
    """x64 detour. Returns (bytes, {name: imm64 offset}). R15D=-1 makes the formatter print RAX alone."""
    imm = {}
    code = bytearray()

    def emit(b):
        code.extend(b)

    def mov_r11(name):
        emit(b'\x49\xbb'); imm[name] = len(code); emit(b'\0' * 8)

    jumps = []

    def jcc(op):
        emit(bytes([op, 0])); jumps.append(len(code) - 1)

    emit(b'\x41\x83\xfd\x0b'); jcc(0x77)          # cmp r13d,11 ; ja orig
    emit(b'\x41\x83\xff\x0b'); jcc(0x77)          # cmp r15d,11 ; ja orig
    emit(b'\x45\x39\xfd'); jcc(0x74)              # cmp r13d,r15d ; je orig
    emit(b'\x44\x89\xe8')                         # mov eax,r13d
    emit(b'\x6b\xc0\x0c')                         # imul eax,eax,12
    emit(b'\x44\x01\xf8')                         # add eax,r15d
    mov_r11('table')                              # mov r11,table
    emit(b'\x49\x8b\x04\xc3')                     # mov rax,[r11+rax*8]
    emit(b'\x48\x85\xc0'); jcc(0x74)              # test rax,rax ; jz orig
    emit(b'\x41\xbf\xff\xff\xff\xff')             # mov r15d,-1
    mov_r11('cont1'); emit(b'\x41\xff\xe3')       # jmp continuation
    orig = len(code)
    mov_r11('lookup'); emit(b'\x41\xff\xd3')      # call original lookup
    mov_r11('cont2'); emit(b'\x41\xff\xe3')       # jmp continuation
    for at in jumps:
        rel = orig - (at + 1)
        assert 0 < rel < 128
        code[at] = rel
    return bytes(code), imm


def lua_bytes(data):
    return '{' + ','.join(str(b) for b in data) + '}'


def build_lua(data):
    titles = {}
    for h in data['hybrids']:
        a, b = (NATIVE_JOBS.index(j) for j in h['jobs'])
        titles[a * 12 + b] = titles[b * 12 + a] = h['title']
    assert len(titles) == 132
    names = sorted(set(titles.values()))
    stub, imm = stub_template()
    original = b'\xe8' + struct.pack('<i', LOOKUP - (SITE + 5))
    template = (ROOT / 'src' / 'lua' / 'HybridJobTitles.lua.in').read_text(encoding='utf-8')
    fill = {
        'SITE': hex(SITE), 'CONTINUATION': hex(CONTINUATION), 'LOOKUP': hex(LOOKUP),
        'ORIGINAL': lua_bytes(original), 'STUB': lua_bytes(stub),
        'IMM': '{' + ','.join(f'{k}={v}' for k, v in sorted(imm.items())) + '}',
        'NAMES': '{\n' + ''.join(f'  {lua_bytes(encode_label(n))}, -- {n}\n' for n in names) + '}',
        'SLOTS': '{' + ','.join(f'[{k}]={names.index(v) + 1}' for k, v in sorted(titles.items())) + '}',
    }
    for k, v in fill.items():
        template = template.replace('@' + k + '@', v)
    assert '@' not in template.replace('@{', '')
    return template


def build_renames(game, data):
    from .archive import Archive
    raw = Archive(Path(game) / 'FFXII_TZA.vbf').read(LABEL_FILE)
    changes = {LABEL_FIRST_ID + NATIVE_JOBS.index(old): (old, new) for old, new in data['renames'].items()}
    return replace_labels(raw, changes, LABEL_FILE_SHA256)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', help='game folder (holds FFXII_TZA.vbf); enables the job renames')
    ap.add_argument('--out', default=str(ROOT / 'dist'))
    args = ap.parse_args(argv)
    data = json.loads((ROOT / 'data' / 'job-titles.json').read_text(encoding='utf-8'))
    out = Path(args.out) / 'HybridJobTitles'
    script = out / 'x64' / 'scripts' / 'HybridJobTitles.lua'
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(build_lua(data), encoding='utf-8')
    print('wrote', script)
    if args.game:
        target = out / 'mods' / 'deploy' / 'ff12data' / LABEL_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(build_renames(args.game, data))
        print('wrote', target)
    else:
        print('no --game: skipped the job renames (Uhlan -> Lancer)')


if __name__ == '__main__':
    main()
