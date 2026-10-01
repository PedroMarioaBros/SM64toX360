#!/usr/bin/env python3
"""Build the .lang section for the SM64 Xbox 360 multilingual edition.

This script does not contain or download game bytes. It expects:
  --base-pe      decrypted/decompressed v0.4 PE extracted from the user's XEX
  --dialogs-dir  generated PT-BR/ES/EN dialog pools + indexes
  --output-pe    destination PE

The new section is stored in physical PE bytes not referenced by any existing
section and mapped at a new RVA. It keeps gameplay code/data untouched.

Layout inside .lang (big-endian metadata for PowerPC runtime):
  0x00  "SM64LANG"
  0x08  version
  0x0C  language count
  0x10  dialog count
  0x14  flags
  0x18  PT-BR pointer-table offset
  0x1C  ES pointer-table offset
  0x20  EN pointer-table offset
  0x24  PT-BR pool offset
  0x28  ES pool offset
  0x2C  EN pool offset
  0x30  used bytes
  0x80  SHA-256 fingerprints for PT-BR / ES / EN pools
"""

from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import struct

IMAGE_BASE = 0x82000000
LANG_RVA = 0x1040000
LANG_RAW = LANG_RVA
LANG_SIZE = 0x20000
LANGUAGES = ("pt_br", "es", "en")
DIALOG_COUNT = 170

def align(value: int, n: int) -> int:
    return (value + n - 1) & ~(n - 1)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-pe", required=True, type=Path)
    ap.add_argument("--dialogs-dir", required=True, type=Path)
    ap.add_argument("--output-pe", required=True, type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    original = args.base_pe.read_bytes()
    data = bytearray(original)
    required_size = LANG_RVA + LANG_SIZE
    if len(data) > required_size:
        raise RuntimeError("base PE is larger than planned multilingual image")
    if len(data) < required_size:
        data.extend(b"\0" * (required_size - len(data)))

    payload = bytearray(LANG_SIZE)
    payload[0:8] = b"SM64LANG"
    struct.pack_into(">IIII", payload, 0x08, 1, len(LANGUAGES), DIALOG_COUNT, 0)

    ptr_table_off: dict[str, int] = {}
    pool_off: dict[str, int] = {}
    cursor = 0x100

    for lang in LANGUAGES:
        cursor = align(cursor, 16)
        ptr_table_off[lang] = cursor
        cursor += DIALOG_COUNT * 4

    cursor = align(cursor, 8)
    pool_meta = {}
    for lang in LANGUAGES:
        pool = (args.dialogs_dir / lang / "dialogs.bin").read_bytes()
        pool_off[lang] = cursor
        payload[cursor:cursor + len(pool)] = pool
        pool_meta[lang] = {
            "offset": hex(cursor),
            "bytes": len(pool),
            "sha256": hashlib.sha256(pool).hexdigest(),
        }
        cursor = align(cursor + len(pool), 8)

    if cursor > LANG_SIZE:
        raise RuntimeError(f".lang overflow: used={cursor} capacity={LANG_SIZE}")

    for lang in LANGUAGES:
        index = json.loads(
            (args.dialogs_dir / lang / "dialog_index.json").read_text(encoding="utf-8")
        )
        if [row["id"] for row in index] != list(range(DIALOG_COUNT)):
            raise RuntimeError(f"{lang}: dialog index must be exactly 0..169")
        for row in index:
            va = IMAGE_BASE + LANG_RVA + pool_off[lang] + row["pool_offset"]
            struct.pack_into(">I", payload, ptr_table_off[lang] + row["id"] * 4, va)

    struct.pack_into(
        ">IIIIIII", payload, 0x18,
        ptr_table_off["pt_br"], ptr_table_off["es"], ptr_table_off["en"],
        pool_off["pt_br"], pool_off["es"], pool_off["en"], cursor,
    )

    for n, lang in enumerate(LANGUAGES):
        pool = (args.dialogs_dir / lang / "dialogs.bin").read_bytes()
        payload[0x80 + n * 32:0x80 + (n + 1) * 32] = hashlib.sha256(pool).digest()

    # .lang lives beyond the canonical v0.4 image, outside its existing
    # runtime data/BSS. The newly appended range must be zero before use.
    if any(data[LANG_RAW:LANG_RAW + LANG_SIZE]):
        raise RuntimeError("new .lang range is not empty")

    pe = struct.unpack_from("<I", data, 0x3C)[0]
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    section_table = pe + 24 + opt_size
    new_header = section_table + section_count * 40
    if section_count != 8 or new_header + 40 > 0x400:
        raise RuntimeError("unexpected PE section layout")

    data[LANG_RAW:LANG_RAW + LANG_SIZE] = payload
    data[new_header:new_header + 8] = b".lang\0\0\0"
    struct.pack_into(
        "<IIIIIIHHI", data, new_header + 8,
        LANG_SIZE, LANG_RVA, LANG_SIZE, LANG_RAW,
        0, 0, 0, 0, 0x40000040,
    )
    struct.pack_into("<H", data, pe + 6, section_count + 1)

    section_align = struct.unpack_from("<I", data, pe + 24 + 32)[0]
    size_of_image = align(LANG_RVA + LANG_SIZE, section_align)
    struct.pack_into("<I", data, pe + 24 + 56, size_of_image)

    args.output_pe.write_bytes(data)

    report = {
        "base_sha256": hashlib.sha256(original).hexdigest(),
        "output_sha256": hashlib.sha256(data).hexdigest(),
        "pe_bytes": len(data),
        "section_rva": hex(LANG_RVA),
        "section_raw": hex(LANG_RAW),
        "section_size": LANG_SIZE,
        "used_bytes": cursor,
        "free_bytes": LANG_SIZE - cursor,
        "size_of_image": hex(size_of_image),
        "pointer_tables": {k: hex(v) for k, v in ptr_table_off.items()},
        "pools": pool_meta,
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
