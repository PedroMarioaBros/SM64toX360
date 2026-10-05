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
  0x14  selector state (0=credits, 1=language, 2=done)
  0x18  selected language (0=PT-BR, 1=ES, 2=EN)
  0x1C  credits timer
  0x20  PT-BR pointer-table offset
  0x24  ES pointer-table offset
  0x28  EN pointer-table offset
  0x2C  PT-BR pool offset
  0x30  ES pool offset
  0x34  EN pool offset
  0x38  used bytes
  0x40..0x6C selector/credits text pointers
  0x100 PT-BR pointer table (fixed for runtime ABI)
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
    # Version 2 introduces pregame selector state without moving the validated
    # pointer tables at 0x100/0x3B0/0x660.
    struct.pack_into(">III", payload, 0x08, 2, len(LANGUAGES), DIALOG_COUNT)
    struct.pack_into(">III", payload, 0x14, 0, 0, 0)

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
        ">IIIIIII", payload, 0x20,
        ptr_table_off["pt_br"], ptr_table_off["es"], ptr_table_off["en"],
        pool_off["pt_br"], pool_off["es"], pool_off["en"], cursor,
    )

    # Pregame strings use only the stock US charmap plus glyph slots already
    # installed and validated by this project (ê=0x65, ñ=0x42).
    special = {" ": 0x9E, "-": 0x9F, "/": 0xD0, ":": 0xE6, ">": 0x53,
               "ê": 0x65, "ñ": 0x42}
    def enc_selector(text: str) -> bytes:
        out = bytearray()
        for ch in text:
            if "0" <= ch <= "9":
                out.append(ord(ch) - ord("0"))
            elif "A" <= ch <= "Z":
                out.append(ord(ch) - ord("A") + 0x0A)
            elif "a" <= ch <= "z":
                out.append(ord(ch) - ord("a") + 0x24)
            elif ch in special:
                out.append(special[ch])
            else:
                raise RuntimeError(f"unsupported selector char: {ch!r}")
        out.append(0xFF)
        return bytes(out)

    selector_texts = [
        "SUPER MARIO 64",
        "NINTENDO 1996",
        "XBOX 360 PORT: CONFUSIONRS",
        "LOCALIZACAO PT-BR",
        "EDICAO MULTILINGUE",
        "PeterKleizoon - PMCN Studios",
        "IDIOMA / LANGUAGE",
        "Português",
        "Español",
        "English",
        "A - OK",
        ">",
    ]
    selector_ptrs = []
    for text in selector_texts:
        cursor = align(cursor, 4)
        raw = enc_selector(text)
        if cursor + len(raw) > LANG_SIZE:
            raise RuntimeError(".lang overflow while adding selector strings")
        payload[cursor:cursor + len(raw)] = raw
        selector_ptrs.append(IMAGE_BASE + LANG_RVA + cursor)
        cursor += len(raw)

    for i, va in enumerate(selector_ptrs):
        struct.pack_into(">I", payload, 0x40 + i * 4, va)
    struct.pack_into(">I", payload, 0x38, cursor)

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
        "selector": {
            "state_offset": "0x14",
            "selection_offset": "0x18",
            "timer_offset": "0x1c",
            "text_pointer_base": "0x40",
            "text_count": 12,
        },
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
