#!/usr/bin/env python3
"""Deterministically reconstruct v0.10 NATIVE60 RC2 mapped image from its verified base.

The instruction patches and injected PPC cave bytes are the exact bytes recovered
from the original historical build. No game XEX is embedded here. After this
script, the recovered 0.4 pack.py + XexTool pipeline reproduces the historical
XEX bit-for-bit when supplied the correct corrected-base XEX container.
"""
from pathlib import Path
import hashlib
import struct
import sys

BASE_SHA = "9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12"
EXPECTED_MAPPED_SHA = "b87b33f3664aaefe3d7163d998f0535a666f13437b9f4d91f556bad49512426b"
EXPECTED_XEX_SHA = "f9e0102099949ba1a276ffd09a1ccf004aa25c58ddc58dd25e67965b1cbd82b7"
IMAGE_BASE = 0x82000000
CAVE_VA = 0x823BCAB0
CAVE = bytes.fromhex("3d208200c189067cc00b00b8ec0003324bd46f843d208200c189067cc1ab00b8edad03324bd470743d208200c149067cedad02b2ed6c68284bd469fc3d208200c169067ced806afa4bd46a28c0eb00e43d208200c0c9067cece701b24bd46ab83d208200c0a9067cefbd0172ecc7e8284bd46bfc3d208200c169067ced806afa4bd46c28ec00002cedbe07b24bd46b48fc00002cfd4b00324bd46db83d2082e5a12998187129000141820008394a00014bce08403d2082e5a12998187129000141820008394a00014bce08683d2082e5a12998187129000141820008394a00014bce0b84556af87e554a06fe4bcdc1983d0082e481087c1c710800017d695b7841820008392b00014bd88fc43d0082e481087c1c710800017d2b4b78418200083969001a4bd890b83d2082e5a1299818712900017d48537841820008390a00014bd485243d2082e5a12998187129000141820008394a00014bd56610")
OLD_TEXT_VIRTUAL_SIZE = 0x32CAB0
NEW_TEXT_VIRTUAL_SIZE = 0x32CC0C

PATCHES = {
    0x0ED1A0: ("482cf894", "ec00682a", "restore shell +1.1 accel"),
    0x0ED1C4: ("482cf884", "ed8d002a", "restore shell curved accel"),
    0x0ED1EC: ("482cf870", "ec006828", "restore shell -1.0 decel"),
    0x0ED208: ("38c00400", "38c00800", "restore shell yaw +0x800"),
    0x0ED210: ("38a00400", "38a00800", "restore shell yaw -0x800"),
    0x3BCA44: ("4bd30760", "4bd309ec", "walking +1.1 helper resume"),
    0x3BCA58: ("4bd30770", "4bd309fc", "walking curved helper resume"),
    0x3BCA6C: ("4bd30784", "4bd30a10", "walking -1.0 helper resume"),
    0x0ED42C: ("ec00682a", "482cf608", "walking +1.1 acceleration half dt"),
    0x0ED450: ("ed8d002a", "482cf5f8", "walking curved acceleration half dt"),
    0x0ED478: ("ec006828", "482cf5e4", "walking deceleration half dt"),
    0x0ED49C: ("38c00800", "38c00400", "walking yaw positive 0x800 -> 0x400"),
    0x0ED4A4: ("38a00800", "38a00400", "walking yaw negative 0x800 -> 0x400"),
    0x103A40: ("c00b00b8", "482b9070", "object_step collision XZ half dt"),
    0x103B44: ("c1ab00b8", "482b8f80", "object_step final XZ half dt"),
    0x1034E0: ("ed6c6828", "482b95f8", "object_step gravity half dt"),
    0x10351C: ("ed80682a", "482b95d0", "object_step vertical displacement half dt"),
    0x1035C0: ("c0eb00e4", "482b953c", "object_step slope gravity half dt"),
    0x103680: ("edbe07b2", "482b94b4", "object_step friction sqrt timing"),
    0x103718: ("ecc7e828", "482b93f8", "object_step underwater net gravity half dt"),
    0x103754: ("ed80682a", "482b93d0", "object_step underwater vertical displacement half dt"),
    0x1038FC: ("fd4b0032", "482b9244", "object_step underwater damping sqrt timing"),
    0x105110: ("390a0001", "482b7ac8", "Bob-omb chase manual animFrame legacy cadence"),
    0x105154: ("38c00800", "38c00400", "Bob-omb chase yaw 0x800 -> 0x400"),
    0x113214: ("394a0001", "482a99e0", "Bob-omb fuse timer legacy cadence"),
    0x09D39C: ("394a0001", "4831f7b0", "yellow coin oAnimState legacy cadence"),
    0x09D3DC: ("394a0001", "4831f788", "temporary coin oAnimState legacy cadence"),
    0x09D710: ("394a0001", "4831f46c", "coin formation oAnimState legacy cadence"),
    0x098D30: ("556a06fe", "48323e64", "PRESS START blink half-rate phase"),
    0x145B78: ("392b0001", "48277028", "title logo frame counter legacy cadence"),
    0x145C88: ("3969001a", "48276f34", "title TM/copyright alpha legacy cadence"),
    0x146FDC: ("2b0b0320", "2b0b0640", "PRESS START demo timeout 800 -> 1600"),
    0x15AF88: ("c00b0674", "c00b067c", "opening Mario state2 +1.0 -> +0.5"),
    0x15AFD4: ("c00b0674", "c00b067c", "opening Mario state3 +1.0 -> +0.5"),
    0x15B010: ("c00b0674", "c00b067c", "opening Mario state4 +1.0 -> +0.5"),
    0x15B070: ("c1ab0674", "c1ab067c", "opening Mario state5 -1.0 -> -0.5"),
    0x15B088: ("c1ab0674", "c1ab067c", "opening Mario state5 +1.0 -> +0.5"),
    0x15B76C: ("c00b0674", "c00b067c", "game-over Mario +1.0 -> +0.5"),
    0x15B094: ("39600096", "3960012c", "opening stillTimer 150 -> 300"),
    0x15B0B4: ("3960012c", "39600258", "opening stillTimer 300 -> 600"),
}

def set_text_virtual_size(data: bytearray) -> None:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    sections = pe + 24 + optional_size
    for i in range(section_count):
        at = sections + i * 40
        name = bytes(data[at:at+8]).split(b"\0", 1)[0]
        if name == b".text":
            current = struct.unpack_from("<I", data, at + 8)[0]
            if current != OLD_TEXT_VIRTUAL_SIZE:
                raise SystemExit(f"VirtualSize .text inesperado: {current:#x}")
            struct.pack_into("<I", data, at + 8, NEW_TEXT_VIRTUAL_SIZE)
            return
    raise SystemExit("Secao .text nao encontrada")

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: reconstruct_v10_native60_rc2.py base.mapped.bin saida.mapped.bin")
    src, dst = map(Path, sys.argv[1:])
    data = bytearray(src.read_bytes())
    got = hashlib.sha256(data).hexdigest()
    if got != BASE_SHA:
        raise SystemExit(f"Base incorreta: {got}")

    for off, (old_hex, new_hex, note) in PATCHES.items():
        old = bytes.fromhex(old_hex)
        new = bytes.fromhex(new_hex)
        if data[off:off+len(old)] != old:
            raise SystemExit(f"{note}: bytes inesperados em {off:#x}: {data[off:off+len(old)].hex()}")
        data[off:off+len(new)] = new

    cave_off = CAVE_VA - IMAGE_BASE
    if data[cave_off:cave_off+len(CAVE)] != bytes(len(CAVE)):
        raise SystemExit(f"Code cave nao esta vazia em {CAVE_VA:#x}")
    data[cave_off:cave_off+len(CAVE)] = CAVE
    set_text_virtual_size(data)

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_MAPPED_SHA:
        raise SystemExit(f"Hash mapped divergente: {digest}")
    dst.write_bytes(data)
    print("PASS mapped:", digest)
    print("XEX esperado apos pack.py:", EXPECTED_XEX_SHA)

if __name__ == "__main__":
    main()
