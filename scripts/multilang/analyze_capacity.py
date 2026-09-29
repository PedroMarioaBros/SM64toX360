#!/usr/bin/env python3
"""
Analisa capacidade REAL da imagem mapeada do SM64 Xbox 360 para a edição multilíngue.

Não escreve no arquivo. O relatório identifica:
- seções PE e limites;
- runs de zero potencialmente utilizáveis;
- região de code cave já usada pela v0.4;
- descritores de Basic Compression do XEX;
- tamanho estimado dos pools de diálogo já gerados.

Uso:
  python3 scripts/multilang/analyze_capacity.py \
      /caminho/v04.mapped.bin /caminho/v04.xex
"""

from __future__ import annotations
from pathlib import Path
import hashlib
import json
import struct
import sys

IMAGE_BASE = 0x82000000
KNOWN = {
    "main_font_lut": 0x9DF3B0,
    "menu_font_lut": 0x842DE0,
    "hud_font_lut": 0x9DF2C8,
    "dialog_table": 0x9E7CD8,
    "dialog_original_end": 0x9E7CD0,
    "v04_code_cave_start": 0x3BC600,
    "v04_code_cave_limit": 0x3C0000,
}

def pe_sections(data: bytes):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe+4] != b"PE\0\0":
        raise RuntimeError("mapped image does not contain PE signature")
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt = struct.unpack_from("<H", data, pe + 20)[0]
    table = pe + 24 + opt
    rows = []
    for i in range(count):
        at = table + i * 40
        name = data[at:at+8].split(b"\0",1)[0].decode("ascii","replace")
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, at+8)
        rows.append({
            "name": name,
            "virtual_size": vsize,
            "virtual_address": va,
            "mapped_start": va,
            "mapped_end": va + vsize,
            "raw_size": raw_size,
            "raw_pointer": raw_ptr,
        })
    return rows

def zero_runs(data: bytes, minimum=256):
    runs = []
    i = 0
    n = len(data)
    while i < n:
        if data[i] != 0:
            i += 1
            continue
        start = i
        i += 1
        while i < n and data[i] == 0:
            i += 1
        if i - start >= minimum:
            runs.append({
                "offset": start,
                "va": IMAGE_BASE + start,
                "bytes": i - start,
                "end_offset": i,
            })
    return runs

def compression_pairs(xex: bytes):
    # The recovered pack.py proved these three Basic Compression pairs for this
    # exact XEX family. We report rather than mutate them here.
    rows = []
    for off in range(0x19FC, 0x1A14, 8):
        if off + 8 > len(xex):
            break
        size, zero = struct.unpack_from(">II", xex, off)
        rows.append({"header_offset": off, "data_bytes": size, "zero_bytes": zero})
    return rows

def generated_pool_sizes(root: Path):
    out = {}
    build = root / "_localization_build"
    for lang in ("pt_br","es","en"):
        p = build / lang / "dialogs.bin"
        out[lang] = p.stat().st_size if p.exists() else None
    return out

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: analyze_capacity.py v04.mapped.bin v04.xex")
    mapped_path, xex_path = map(Path, sys.argv[1:])
    mapped = mapped_path.read_bytes()
    xex = xex_path.read_bytes()

    runs = zero_runs(mapped)
    # High-value candidates only: >= 4 KiB.
    candidates = [r for r in runs if r["bytes"] >= 4096]
    candidates.sort(key=lambda r: r["bytes"], reverse=True)

    report = {
        "mapped": {
            "path": str(mapped_path),
            "bytes": len(mapped),
            "sha256": hashlib.sha256(mapped).hexdigest(),
            "sections": pe_sections(mapped),
        },
        "xex": {
            "path": str(xex_path),
            "bytes": len(xex),
            "sha256": hashlib.sha256(xex).hexdigest(),
            "basic_compression_pairs": compression_pairs(xex),
        },
        "known_offsets": KNOWN,
        "generated_dialog_pool_bytes": generated_pool_sizes(Path.cwd()),
        "zero_runs_ge_256": len(runs),
        "largest_zero_runs": candidates[:64],
        "warning": (
            "Zero bytes are only CANDIDATES. A region is not allocatable until "
            "section semantics, runtime references and Basic Compression are checked."
        ),
    }

    out = Path("_localization_build/capacity_report.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
