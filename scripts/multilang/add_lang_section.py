#!/usr/bin/env python3
"""Create/replace the mapped .lang section used by the SM64 multilingual build.

The recovered Xbox 360 basefile is a mapped PE image: runtime addresses use
IMAGE_BASE + mapped offset. The original image ends at 0x00FB0000 while the
PE header reserves SizeOfImage through 0x0103C400. We place multilingual data
at mapped offset/RVA 0x01000000, avoiding the original .data/BSS region.

Usage:
  python3 add_lang_section.py input.pe payload.bin output.pe
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

LANG_RVA = 0x01000000
LANG_CAPACITY = 0x0003C000
EXPECTED_SOURCE_SIZE = 0x00FB0000

def align(value, boundary):
    return (value + boundary - 1) & ~(boundary - 1)

def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: add_lang_section.py input.pe payload.bin output.pe")

    src_path, payload_path, out_path = map(Path, sys.argv[1:])
    src = src_path.read_bytes()
    payload = payload_path.read_bytes()
    if len(payload) > LANG_CAPACITY:
        raise SystemExit(f"payload too large: {len(payload)} > {LANG_CAPACITY}")
    if len(src) != EXPECTED_SOURCE_SIZE:
        raise SystemExit(f"unexpected v0.4 PE size: {len(src):#x}")

    data = bytearray(src)
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe+4] != b"PE\0\0":
        raise SystemExit("invalid PE signature")

    coff = pe + 4
    nsec = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    section_table = opt + opt_size
    size_headers = struct.unpack_from("<I", data, opt + 60)[0]
    size_image = struct.unpack_from("<I", data, opt + 56)[0]

    if LANG_RVA + LANG_CAPACITY > size_image:
        raise SystemExit(
            f".lang exceeds existing SizeOfImage: {LANG_RVA+LANG_CAPACITY:#x} > {size_image:#x}"
        )

    # Reuse .lang if already present; otherwise append its section header.
    lang_header = None
    for i in range(nsec):
        off = section_table + i * 40
        name = data[off:off+8].split(b"\0", 1)[0]
        if name == b".lang":
            lang_header = off
            break

    if lang_header is None:
        lang_header = section_table + nsec * 40
        if lang_header + 40 > size_headers:
            raise SystemExit("no room for an additional PE section header")
        struct.pack_into("<H", data, coff + 2, nsec + 1)

        old_init = struct.unpack_from("<I", data, opt + 8)[0]
        struct.pack_into("<I", data, opt + 8, old_init + LANG_CAPACITY)

    needed = LANG_RVA + LANG_CAPACITY
    if len(data) < needed:
        data.extend(b"\x00" * (needed - len(data)))

    # Clear whole section so rebuilds are deterministic.
    data[LANG_RVA:LANG_RVA+LANG_CAPACITY] = b"\x00" * LANG_CAPACITY
    data[LANG_RVA:LANG_RVA+len(payload)] = payload

    header = (
        b".lang\0\0\0"
        + struct.pack(
            "<IIIIIIHHI",
            LANG_CAPACITY,  # VirtualSize
            LANG_RVA,       # VirtualAddress / mapped offset
            LANG_CAPACITY,  # SizeOfRawData (mapped image convention)
            LANG_RVA,       # PointerToRawData
            0, 0, 0, 0,
            0xC0000040,     # initialized read/write data
        )
    )
    data[lang_header:lang_header+40] = header

    out_path.write_bytes(data)
    report = {
        "input_sha256": hashlib.sha256(src).hexdigest(),
        "output_sha256": hashlib.sha256(data).hexdigest(),
        "input_bytes": len(src),
        "output_bytes": len(data),
        "lang_rva": hex(LANG_RVA),
        "lang_capacity": LANG_CAPACITY,
        "payload_bytes": len(payload),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "free_bytes": LANG_CAPACITY - len(payload),
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
