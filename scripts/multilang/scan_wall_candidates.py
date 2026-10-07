#!/usr/bin/env python3
"""Static candidate scan for Mario wall/crawling routines in an Xbox 360 PE.

This deliberately reports candidates only; it does not patch or claim an ABI match.
"""
import json, struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN

if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} image.pe")
b = Path(sys.argv[1]).read_bytes()
pe = struct.unpack_from('<I', b, 60)[0]
base = struct.unpack_from('<I', b, pe + 52)[0]
sec_count = struct.unpack_from('<H', b, pe + 6)[0]
opt_size = struct.unpack_from('<H', b, pe + 20)[0]
sec_table = pe + 24 + opt_size
text_rva = text_raw = text_size = None
for i in range(sec_count):
    o = sec_table + i * 40
    name = b[o:o+8].rstrip(b'\0')
    vs, va, raw_size, raw = struct.unpack_from('<IIII', b, o + 8)
    if name == b'.text':
        text_rva, text_raw, text_size = va, raw, raw_size
        break
if text_rva is None:
    raise SystemExit('missing .text')
text = b[text_raw:text_raw + text_size]
text_va = base + text_rva
pdata_raw = None
for i in range(sec_count):
    o = sec_table + i * 40
    if b[o:o+6] == b'.pdata':
        pdata_raw = struct.unpack_from('<I', b, o + 20)[0]
        pdata_size = struct.unpack_from('<I', b, o + 16)[0]
        break
if pdata_raw is None:
    raise SystemExit('missing .pdata')
md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
rows = []
for off in range(0, pdata_size, 16):
    start, _, end, _ = struct.unpack_from('>IIII', b, pdata_raw + off)
    if not (text_va <= start < text_va + len(text)) or end <= start:
        continue
    code = text[start - text_va:end - text_va]
    ins = list(md.disasm(code, start))
    text_ins = '\n'.join(f'{x.mnemonic} {x.op_str}' for x in ins)
    counts = {hex(n): text_ins.count(f'{n:#x}') for n in (0x20, 0x24, 0x60, 0x64, 0x68, 0x9c)}
    wall = sum(text_ins.count(f'{n:#x}') for n in (0x60, 0x64, 0x68))
    io = text_ins.count('0x9c')
    if wall >= 2 or (wall and io):
        rows.append({'start': hex(start), 'end': hex(end), 'instruction_count': len(ins),
                     'mariostate_offset_mentions': counts,
                     'note': 'candidate only; verify source fingerprint and ABI'})
print(json.dumps({'status':'PASS','image_base':hex(base),'text_va':hex(text_va),
                  'candidate_count':len(rows),'candidates':rows}, indent=2))

