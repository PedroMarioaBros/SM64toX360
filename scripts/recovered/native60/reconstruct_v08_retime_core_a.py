#!/usr/bin/env python3
"""Reconstruct the exact v0.8 NATIVE60 RETIME CORE A mapped image.

Input must be the exact reconstructed v0.7 mapped image. The patch list below
was independently recovered from the v0.4 disassembly and validated because the
resulting XEX matches the historical v0.8 SHA-256 bit-for-bit.
"""
from pathlib import Path
import hashlib
import sys

BASE_SHA = "4630aacb5011ec4726e8c852a05d09bf4acc1a9749913811d8267f00d6313312"
EXPECTED_MAPPED_SHA = "b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2"
EXPECTED_XEX_SHA = "ff5c185bc6a78c38b80b14c6923bc6d94f2ff733c6e1c8f0a3855dc6c11583f6"
MAPPER_SHA = "b51af5c7f53d6cf7a058a3353f9de40dfbe514890a0822427c151026904d3e03"

PATCHES = {
    0x0FA9D8: ("2f1b0004", "2f1b0002", "ground substeps 4 -> 2"),
    0x0FB2C0: ("2f1b0004", "2f1b0002", "air substeps 4 -> 2"),
    0x0FAED8: ("c18a0834", "c18a0848", "twirl gravity 4.0 -> 2.0"),
    0x0FAFB0: ("c00b0674", "c00b067c", "cannon gravity 1.0 -> 0.5"),
    0x0FB11C: ("c00b1728", "c00b0eac", "lava/star gravity 3.2 -> 1.6"),
    0x0FB06C: ("c00b0eac", "c00b0a50", "metal-water gravity 1.6 -> 0.8"),
    0x0FB0B8: ("c00a0848", "c00a0674", "wing gravity 2.0 -> 1.0"),
    0x0FB0DC: ("c18b0834", "c18b0848", "wing recovery 4.0 -> 2.0"),
    0x0FB108: ("c00b0834", "c00b0848", "normal gravity 4.0 -> 2.0"),
    0x0FB130: ("c00b0848", "c00b0674", "long-jump/slide gravity 2.0 -> 1.0"),
    0x0FB200: ("c18b0c10", "c18b1be0", "vertical wind 1/8 -> 1/16"),
    0x15CF70: ("3be00002", "3be00001", "audio blocks/frame 2 -> 1"),
    0x15CF90: ("57a41838", "57a4103a", "audio buffer bytes x8 -> x4"),
}

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: reconstruct_v08_retime_core_a.py v0.7.mapped.bin v0.8.mapped.bin")
    src, dst = map(Path, sys.argv[1:])
    data = bytearray(src.read_bytes())
    got = hashlib.sha256(data).hexdigest()
    if got != BASE_SHA:
        raise SystemExit(f"Base incorreta: {got}")

    for off, (old_hex, new_hex, label) in PATCHES.items():
        old, new = bytes.fromhex(old_hex), bytes.fromhex(new_hex)
        if data[off:off+4] != old:
            raise SystemExit(f"{label}: bytes inesperados em {off:#x}: {data[off:off+4].hex()}")
        data[off:off+4] = new

    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_MAPPED_SHA, digest
    mapper = hashlib.sha256(data[0x165998:0x165C90]).hexdigest()
    assert mapper == MAPPER_SHA, mapper
    dst.write_bytes(data)
    print("PASS v0.8 mapped:", digest)
    print("PASS mapper preservado:", mapper)
    print("XEX esperado após pack.py:", EXPECTED_XEX_SHA)

if __name__ == "__main__":
    main()
