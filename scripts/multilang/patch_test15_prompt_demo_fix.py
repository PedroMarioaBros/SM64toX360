#!/usr/bin/env python3
"""Build TEST15's targeted localized-intro-prompt candidate from exact TEST14 PE.

This patcher only edits two verified existing instructions plus a zero-filled
executable cave. It intentionally leaves the selector input handler untouched.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

BASE = 0x82000000
PE_LEN = 17_170_432
TEST14_SHA = "6266c97deec43d4f43fe3c89bce2ebfb019ab220409702a35fccbd17b0878742"
CALLSITE = 0x820DBEF8
CALLSITE_RVA = CALLSITE - BASE
ORIGINAL_CALL = 0x4BFBCE21
MAIN_WRAPPER = 0x823BCD00
MAIN_WRAPPER_NULL_BRANCH = 0x823BCEF4
MAIN_WRAPPER_NULL_BRANCH_RVA = MAIN_WRAPPER_NULL_BRANCH - BASE
ORIGINAL_NULL_BRANCH = 0x4182004C
NOP = 0x60000000
PROMPT_WRAPPER = 0x823BCF60
PROMPT_WRAPPER_RVA = PROMPT_WRAPPER - BASE
PROMPT_CAVE_START = 0x823BCF54 - BASE
PROMPT_CAVE_END = 0x823BD000 - BASE
PRINT_INTRO_TEXT = 0x82098D18
PRINT_CENTER = 0x8212B498


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign_extend(v: int, bits: int) -> int:
    return (v ^ (1 << (bits - 1))) - (1 << (bits - 1))


def branch_word(pc: int, target: int, *, link: bool = False) -> int:
    disp = target - pc
    if disp & 3:
        raise ValueError("PowerPC branch target must be 4-byte aligned")
    if not -(1 << 25) <= disp < (1 << 25):
        raise ValueError("PowerPC relative branch displacement out of range")
    return 0x48000000 | (disp & 0x03FFFFFC) | int(link)


def branch_dest(pc: int, word: int) -> int:
    if (word & 0xFC000002) != 0x48000000:
        raise ValueError(f"not a relative PPC branch: 0x{word:08x}")
    return (pc + sign_extend(word & 0x03FFFFFC, 26)) & 0xFFFFFFFF


def cond_beq(pc: int, target: int) -> int:
    disp = target - pc
    if disp & 3 or not -0x8000 <= disp <= 0x7FFC:
        raise ValueError("conditional branch displacement out of range")
    return 0x41820000 | (disp & 0xFFFC)


def build_prompt_wrapper(va: int = PROMPT_WRAPPER) -> bytes:
    # Fixed PPC routine; word offsets are resolved to exact target addresses.
    words = [
        0x7C0802A6, 0x9421FFE0, 0x9001001C, 0x3D608304,
        0x814B0014, 0x2C0A0000, 0x41820000, 0x814B0018,
        0x2C0A0000, 0x41820000, 0x554A103A, 0x396B0070,
        0x7D6B502E, 0x80AB0014, 0x90A10010, 0x80AB0018,
        0x90A10014, 0x3860003C, 0x38800026, 0x80A10010,
        0x48000001, 0x3860003C, 0x38800014, 0x80A10014,
        0x48000001, 0x48000000, 0x48000001, 0x8001001C,
        0x38210020, 0x7C0803A6, 0x4E800020,
    ]
    # State zero and Portuguese both delegate to the native renderer.
    words[6] = cond_beq(va + 6*4, va + 26*4)
    words[9] = cond_beq(va + 9*4, va + 26*4)
    words[20] = branch_word(va + 20*4, PRINT_CENTER, link=True)
    words[24] = branch_word(va + 24*4, PRINT_CENTER, link=True)
    words[25] = branch_word(va + 25*4, va + 27*4)
    words[26] = branch_word(va + 26*4, PRINT_INTRO_TEXT, link=True)
    return b"".join(struct.pack(">I", w) for w in words)


def patch(pe: bytes, *, strict: bool = True) -> tuple[bytes, dict]:
    if len(pe) != PE_LEN:
        raise ValueError(f"expected {PE_LEN} bytes, got {len(pe)}")
    if strict and sha(pe) != TEST14_SHA:
        raise ValueError("source hash is not the exact mapped TEST14 PE")
    if struct.unpack_from(">I", pe, CALLSITE_RVA)[0] != ORIGINAL_CALL:
        raise ValueError("unexpected remaining print_intro_text call at DBEF8")
    if struct.unpack_from(">I", pe, MAIN_WRAPPER_NULL_BRANCH_RVA)[0] != ORIGINAL_NULL_BRANCH:
        raise ValueError("unexpected controller-null fallback branch in TEST14 wrapper")
    if any(pe[PROMPT_CAVE_START:PROMPT_CAVE_END]):
        raise ValueError("planned prompt wrapper cave is not completely zero-filled")

    wrapper = build_prompt_wrapper()
    if PROMPT_WRAPPER_RVA + len(wrapper) > PROMPT_CAVE_END:
        raise ValueError("prompt-only wrapper exceeds executable zero-fill cave")

    out = bytearray(pe)
    struct.pack_into(">I", out, CALLSITE_RVA, branch_word(CALLSITE, PROMPT_WRAPPER, link=True))
    struct.pack_into(">I", out, MAIN_WRAPPER_NULL_BRANCH_RVA, NOP)
    out[PROMPT_WRAPPER_RVA:PROMPT_WRAPPER_RVA+len(wrapper)] = wrapper
    final = bytes(out)

    allowed = [
        (CALLSITE_RVA, CALLSITE_RVA+4),
        (MAIN_WRAPPER_NULL_BRANCH_RVA, MAIN_WRAPPER_NULL_BRANCH_RVA+4),
        (PROMPT_WRAPPER_RVA, PROMPT_WRAPPER_RVA+len(wrapper)),
    ]
    changed = [i for i, (a, b) in enumerate(zip(pe, final)) if a != b]
    if any(not any(a <= i < b for a, b in allowed) for i in changed):
        raise ValueError("unexpected out-of-scope binary changes")
    if final[0x1040100:0x10406F0] != pe[0x1040100:0x10406F0]:
        raise ValueError("canonical dialog pointers/translation changed")
    if final[0x1040080:0x1040088] != pe[0x1040080:0x1040088]:
        raise ValueError("B/Y scratch space changed")
    if final[0xCD128:0xCD12C] != pe[0xCD128:0xCD12C]:
        raise ValueError("global level script hook changed")

    new_call = struct.unpack_from(">I", final, CALLSITE_RVA)[0]
    if branch_dest(CALLSITE, new_call) != PROMPT_WRAPPER:
        raise ValueError("new callsite does not reach the prompt-only wrapper")
    report = {
        "status": "TEST15_PROMPT_DEMO_FIX_CANDIDATE_NOT_HARDWARE_VALIDATED",
        "source_pe_sha256": sha(pe),
        "candidate_pe_sha256": sha(final),
        "candidate_pe_length": len(final),
        "changed_byte_count": len(changed),
        "changed_ranges": [
            {"start_rva": hex(a), "end_rva_exclusive": hex(b), "length": b-a}
            for a, b in allowed
        ],
        "hook": {"callsite_va": hex(CALLSITE), "old_word": f"{ORIGINAL_CALL:08x}", "new_word": f"{new_call:08x}", "target_va": hex(PROMPT_WRAPPER)},
        "localized_prompt_guard": {"address_va": hex(MAIN_WRAPPER_NULL_BRANCH), "old_word": f"{ORIGINAL_NULL_BRANCH:08x}", "new_word": f"{NOP:08x}", "purpose": "Do not fall back to PT-BR solely because the controller pointer is null after language selection."},
        "prompt_wrapper": {"address_va": hex(PROMPT_WRAPPER), "length": len(wrapper), "sha256": sha(wrapper), "state_zero_behavior": "calls original native print only; selector input handler is untouched", "pt_br_behavior": "calls original native print", "es_en_behavior": "draws localized two-line prompt from existing language table without controller dereference"},
        "selector_centering_unchanged": True,
        "ptbr_translation_and_dialog_pointers_unchanged": True,
        "b_y_scratch_unchanged": True,
        "fps_baseline": 30,
        "native60_or_dubbing_added": False,
        "hardware_test": "PENDING",
    }
    return final, report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source_pe", type=Path)
    ap.add_argument("output_pe", type=Path)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()
    final, report = patch(a.source_pe.read_bytes())
    a.output_pe.write_bytes(final)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if a.report:
        a.report.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
