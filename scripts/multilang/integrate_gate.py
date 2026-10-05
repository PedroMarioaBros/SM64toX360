#!/usr/bin/env python3
"""Install the tested gate in .lang PE and validate against prior integration.

Usage: integrate_gate.py lang.pe previous-validated.pe output.pe dialogs-dir report.json
Previous reference must be the known 05/10 static integration. This command
permits subsequent changes ONLY inside .lang, retaining all prior patches.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

import language_activation
import pregame_gate

REFERENCE_SHA = "315498a8ca65cbff54d83b9654b9c6fe7fe2efa4f66ae7aee2dfeecddab04769"
LANG_START = 0x1040000
LANG_END = 0x1060000


def main():
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    src, reference_path, dst, dialogs, report_path = map(Path, sys.argv[1:])
    data = bytearray(src.read_bytes())
    reference = reference_path.read_bytes()
    if hashlib.sha256(reference).hexdigest() != REFERENCE_SHA:
        raise RuntimeError("unrecognized reference integration")
    if len(data) != LANG_END or len(reference) != len(data):
        raise RuntimeError("unexpected PE image size")
    if data[LANG_START:LANG_START + 8] != b"SM64LANG":
        raise RuntimeError(".lang header missing")
    for address, code in [(language_activation.ROUTINE_VA, language_activation.build()),
                          (pregame_gate.GATE_VA, pregame_gate.build())]:
        offset = address - 0x82000000
        if any(data[offset:offset + len(code)]):
            raise RuntimeError("code cave not empty")
        data[offset:offset + len(code)] = code
    hook = 0xCD128
    old = struct.unpack_from(">I", data, hook)[0]
    if old != 0x4BFC8321:
        raise RuntimeError("original hook instruction differs")
    new = 0x48000001 | ((pregame_gate.GATE_VA - 0x820CD128) & 0x03FFFFFC)
    struct.pack_into(">I", data, hook, new)
    unexpected = sum(a != b for a, b in zip(data[:LANG_START], reference[:LANG_START]))
    if unexpected:
        raise RuntimeError(f"unexpected changes outside .lang: {unexpected}")
    validated = 0
    pools = {}
    for number, lang in enumerate(("pt_br", "es", "en")):
        table_offset = struct.unpack_from(">I", data, LANG_START + 0x20 + number * 4)[0]
        pool_offset = struct.unpack_from(">I", data, LANG_START + 0x2C + number * 4)[0]
        blob = (dialogs / lang / "dialogs.bin").read_bytes()
        if data[LANG_START + pool_offset:LANG_START + pool_offset + len(blob)] != blob:
            raise RuntimeError("pool differs from supplied input")
        index = json.loads((dialogs / lang / "dialog_index.json").read_text())
        if [row['id'] for row in index] != list(range(170)):
            raise RuntimeError("invalid dialog IDs")
        for row in index:
            pointer = struct.unpack_from(">I", data, LANG_START + table_offset + row["id"] * 4)[0]
            offset = pointer - 0x82000000
            expected = LANG_START + pool_offset + row["pool_offset"]
            if offset != expected or offset + row["length"] > LANG_START + pool_offset + len(blob):
                raise RuntimeError("invalid pool pointer")
            raw = data[offset:offset + row["length"]]
            if raw[-1] != 0xFF or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise RuntimeError("invalid encoded dialog")
            validated += 1
        pools[lang] = {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
    dst.write_bytes(data)
    report = {"date": "2026-10-05", "status": "STATIC_INTEGRATION_PASS",
              "hardware_verified": False, "reference_pe_sha256": REFERENCE_SHA,
              "output_pe_sha256": hashlib.sha256(data).hexdigest(), "pools": pools,
              "pointers_validated": validated, "unexpected_changes_outside_lang": unexpected,
              "hook_old": hex(old), "hook_new": hex(new),
              "gate_sha256": hashlib.sha256(pregame_gate.build()).hexdigest(),
              "note": "Layout successor; same gate, activation, glyphs and PT-BR as validated reference."}
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
