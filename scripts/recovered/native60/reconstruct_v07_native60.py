#!/usr/bin/env python3
"""Reconstruct the exact v0.7 NATIVE60 CORE mapped image from PT-BR v0.4.

This script patches only the verified Xbox 360 frame limiter constant:
1,666,666 -> 833,333 time-base ticks.

It does NOT package a XEX by itself. Feed the resulting mapped image to the
recovered 0.4 pack.py/XexTool pipeline.
"""
from pathlib import Path
import hashlib
import sys

BASE_SHA = "6381bf1333bf1985474af00c139f33f9cdbad71a371c3231db0d861b72cfac2c"
EXPECTED_MAPPED_SHA = "4630aacb5011ec4726e8c852a05d09bf4acc1a9749913811d8267f00d6313312"
EXPECTED_XEX_SHA = "51d898f1d027aff2ee28f16ea43ce89672c73c0bf2212c7b3bda015ba3389382"

PATCHES = {
    0x1652A8: ("3d6b0019", "3d6b000d"),  # addis r11,r11,25 -> 13
    0x1652B0: ("3d6a0019", "3d6a000d"),  # addis r11,r10,25 -> 13
    0x1652B4: ("396b6e6a", "396bb735"),  # +0x6E6A -> -0x48CB
}

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: reconstruct_v07_native60.py v0.4.mapped.bin v0.7.mapped.bin")
    src, dst = map(Path, sys.argv[1:])
    data = bytearray(src.read_bytes())
    got = hashlib.sha256(data).hexdigest()
    if got != BASE_SHA:
        raise SystemExit(f"Base incorreta: {got}")

    changed = 0
    for off, (old_hex, new_hex) in PATCHES.items():
        old, new = bytes.fromhex(old_hex), bytes.fromhex(new_hex)
        if data[off:off+4] != old:
            raise SystemExit(f"Bytes inesperados em {off:#x}: {data[off:off+4].hex()}")
        changed += sum(a != b for a, b in zip(old, new))
        data[off:off+4] = new

    assert changed == 4
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_MAPPED_SHA, digest
    dst.write_bytes(data)
    print("PASS v0.7 mapped:", digest)
    print("XEX esperado após pack.py:", EXPECTED_XEX_SHA)

if __name__ == "__main__":
    main()
