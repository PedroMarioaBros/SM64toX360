#!/usr/bin/env python3
"""Read-only candidate scanner for PPC BL calls to print_intro_text.

Input is the exact 17,170,432-byte mapped PE image (not an XEX wrapper).
This deliberately reports candidates only: aligned data can resemble a PPC
instruction, so every result must be validated in disassembly/context before
it is treated as a real callsite. It never modifies the input.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x82000000
IMAGE_LEN = 17_170_432
PRINT_INTRO_TEXT = 0x82098D18


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def scan(mapped_pe: bytes, target: int = PRINT_INTRO_TEXT) -> dict:
    if len(mapped_pe) != IMAGE_LEN:
        raise ValueError(f"expected mapped PE length {IMAGE_LEN}, got {len(mapped_pe)}")
    hits = []
    # PPC relative branch with link: opcode 18, AA=0, LK=1.
    for off in range(0, len(mapped_pe) - 3, 4):
        word = struct.unpack_from(">I", mapped_pe, off)[0]
        if (word & 0xFC000003) != 0x48000001:
            continue
        disp = sign_extend(word & 0x03FFFFFC, 26)
        pc = BASE + off
        dest = (pc + disp) & 0xFFFFFFFF
        if dest != target:
            continue
        prev = struct.unpack_from(">I", mapped_pe, off - 4)[0] if off >= 4 else None
        nxt = struct.unpack_from(">I", mapped_pe, off + 4)[0] if off + 8 <= len(mapped_pe) else None
        hits.append({
            "file_offset": hex(off),
            "caller_va": hex(pc),
            "branch_word": f"{word:08x}",
            "target_va": hex(dest),
            "previous_word": None if prev is None else f"{prev:08x}",
            "next_word": None if nxt is None else f"{nxt:08x}",
            "validation": "CANDIDATE_ONLY_REQUIRES_DISASSEMBLY",
        })
    return {
        "status": "READ_ONLY_PPC_BL_CANDIDATES",
        "image_length": len(mapped_pe),
        "image_sha256": sha(mapped_pe),
        "target_va": hex(target),
        "candidate_count": len(hits),
        "candidates": hits,
        "warning": "Aligned data may resemble PPC instructions; validate each candidate in executable code/disassembly.",
        "binary_modified": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mapped_pe", type=Path, help="exact mapped PE image, not default.xex")
    ap.add_argument("--target", type=lambda s: int(s, 0), default=PRINT_INTRO_TEXT)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    result = scan(args.mapped_pe.read_bytes(), args.target)
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
