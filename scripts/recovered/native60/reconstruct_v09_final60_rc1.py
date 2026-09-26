#!/usr/bin/env python3
"""Deterministically reconstruct v0.9 NATIVE60 FINAL60 RC1 mapped image from its verified base.

The instruction patches and injected PPC cave bytes are the exact bytes recovered
from the original historical build. No game XEX is embedded here. After this
script, the recovered 0.4 pack.py + XexTool pipeline reproduces the historical
XEX bit-for-bit when supplied the correct corrected-base XEX container.
"""
from pathlib import Path
import hashlib
import struct
import sys

BASE_SHA = "b8eb88dfbb8fb11d418e17dec2693667586d4c0a3083708e43506bc838add6a2"
EXPECTED_MAPPED_SHA = "9d7e6ddac954900702c123b1a2441e6ad57b508e2c8b88266fbf04d8e6a57b12"
EXPECTED_XEX_SHA = "7009c42c7962090d045d9e547037f1ff7c88f4992633903718afc41d00bfd856"
IMAGE_BASE = 0x82000000
CAVE_VA = 0x823BC7B8
CAVE = bytes.fromhex("3d608200c00b067cec630032ec840032ff0110004bcd9c203d4082e6a14a9818714a00014082000c39670001916301544bcd4d7c7c0a484041820010712b0001408200084bcd6ec44bcd6fc03ce08200c007067cc1080000c0eb00a0ecc8383ad0cb00a0c0aa0000c08b00a8ec65203ad06b00a84e8000203ce08200c187067cc00a0000c1ab00a4ed806b3ad18b00a44e8000203d4082e5812a84783d008200c008067ceda1102aedad0032c18900b0ed6c682ac1480720fc0b500040800008fd605090d16900b0c18900a4ed8b603ad18900a47d2b4b784bd422e0817f84783d408200c14a067cc00b00acc1ab00a0efe06abac18b00b4c16b00a8efcc5aba4bd421443ce08200c007067cc1ab00acc1880000ed8d603ad1880000c16b00b4c14a0000ed4b503ad14a00003cc082e580c68478c12600e4c10600b0ed09403ad10600b0c0e90000ece8383ad0e900004e8000203d0082e481087c1c71080001408200103d4a0001394affff4bcd72284e8000203d0082e481087c1c71080001408200103d4a0001394affff4bcd72684e8000203d608200c00b067cec2100323d6082004bd41fa03d4082e6a14a9818714a000140820008396b00014bd2201c3d4082e6a14a9818714a000140820008396b00014bd2202c3d4082e6a14a9818714a000140820008396bffff4bd2243c3d4082e6a14a9818714a000140820008396bffff4bd224383d4082e6a14a9818714a000140820008396bffff4bd1d1b43d4082e6a14a9818714a00014082000c390bffff480000087d685b784bd21d083d2082e6a129981871290001408200103d6a0001396bffff4bd227fc4bd227fc3d4082e6a14a9818714a00014082000c7d8802a64bd225404e8000203d408200c18a067cedad0332ec00682a4bd307603d408200c16a067cedad02f2ed8d002a4bd307703d408200c18a067cedad0332ec0068284bd307843d408200c1aa067cec0003727fcb07344bd305283d408200c16a067ced2902f2ed0c027a4bd3dba83cc08200c106067cec0002327d6a4c2eed4b683a4bd3dc90")
OLD_TEXT_VIRTUAL_SIZE = 0x32C7B8
NEW_TEXT_VIRTUAL_SIZE = 0x32CAB0

PATCHES = {
    0x0963E8: ("ff011000", "483263d0", "approach_f32: half +/- float approach increments globally"),
    0x091558: ("54eb003e", "4832b278", "Object oTimer: increment at legacy 30Hz while behavior executes 60Hz"),
    0x0936B8: ("7f0a4840", "48329134", "Animation frame advance: legacy timing at 60Hz renderer"),
    0x0FEC20: ("c1080000", "482bdbe4", "Generic object X/Z integration: dt=0.5"),
    0x0FEC70: ("c00a0000", "482bdbc0", "Generic object Y integration: dt=0.5"),
    0x0FEB28: ("3d4082e5", "482bdd24", "Generic object gravity+Y integration: dt=0.5"),
    0x0FE9E0: ("817f8478", "482bdeb4", "Object collision intended X/Z: half displacement per 60Hz tick"),
    0x0FF480: ("c00b00ac", "482bd43c", "Generic velocity+gravity object integrator: dt=0.5"),
    0x093B44: ("3d4a0001", "48328dc8", "Level script sleep: legacy 30Hz frame duration"),
    0x093BA4: ("3d4a0001", "48328d88", "Level script sleep2: legacy 30Hz frame duration"),
    0x0FE8F8: ("3d608200", "482be054", "Generic object drag strength per 60Hz tick: 0.5x"),
    0x0DE98C: ("396b0001", "482ddfd4", "Mario framesSinceA: legacy real-time cadence"),
    0x0DE9B4: ("396b0001", "482ddfc4", "Mario framesSinceB: legacy real-time cadence"),
    0x0DEDDC: ("396b00ff", "482ddbb4", "Mario wall-kick timer: legacy real-time cadence"),
    0x0DEDF0: ("396b00ff", "482ddbb8", "Mario double-jump timer: legacy real-time cadence"),
    0x0D9B84: ("396bffff", "482e2e3c", "Mario invincibility timer: legacy real-time cadence"),
    0x0DE6F8: ("390b00ff", "482de2e0", "Mario squish timer: legacy real-time cadence"),
    0x0DF204: ("3d6a0001", "482dd7f4", "Mario cap timer: legacy real-time cadence"),
    0x0DEF68: ("7d8802a6", "482ddab0", "Mario health/drain/heal update: 30Hz cadence"),
    0x0ED1A0: ("ec00682a", "482cf894", "RC1 walking-labelled +1.1 acceleration helper"),
    0x0ED1C4: ("ed8d002a", "482cf884", "RC1 walking-labelled curved acceleration helper"),
    0x0ED1EC: ("ec006828", "482cf870", "RC1 walking-labelled -1.0 deceleration helper"),
    0x0ECFA4: ("7fcb0734", "482cfacc", "Slope acceleration: half per 60Hz tick"),
    0x0FA638: ("ed0c027a", "482c244c", "Moving-sand push: half per 60Hz tick"),
    0x0FA734: ("7d6a4c2e", "482c2364", "Horizontal wind push: half per 60Hz tick"),
    0x0ED208: ("38c00800", "38c00400", "RC1 yaw positive step 0x800 -> 0x400"),
    0x0ED210: ("38a00800", "38a00400", "RC1 yaw negative step 0x800 -> 0x400"),
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
        raise SystemExit("Uso: reconstruct_v09_final60_rc1.py base.mapped.bin saida.mapped.bin")
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
