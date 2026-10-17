#!/usr/bin/env python3
"""Minimal fail-closed repair for TEST9's verified crashing title glyph "X".

The Xbox TEST9 crashed at title, and Xenia Canary dac2794 reproduced:
PC 0x8215F1A4, invalid read 0x0000000100000000. In a private XEX,
changing ONLY the label byte at guest VA 0x8305CA30 from ASCII X to O
rendered the cursor, enabled D-pad/A/Start, and removed the emulator crash.

This operates on the decrypted *mapped PE*, not encrypted XEX, and refuses
any build other than the precise TEST9 PE. DO NOT place game PE/XEX in GitHub.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_PE_SHA256="a405ba6e97c933298a1e24361423b7230f75957a4ee0c0ecfced21d957b2e641"
OUTPUT_PE_SHA256="a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd"
EXPECTED_SIZE=17170432
VA_BASE=0x82000000
CURSOR_LABEL_VA=0x8305CA30
CURSOR_LABEL_OFF=CURSOR_LABEL_VA-VA_BASE
OLD=b"X\x00"
NEW=b"O\x00"

def sha(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def patch(mapped_pe: bytes, *, strict_source=True):
    if len(mapped_pe)!=EXPECTED_SIZE:
        raise ValueError("invalid TEST9 mapped PE size")
    if strict_source and sha(mapped_pe)!=SOURCE_PE_SHA256:
        raise ValueError("source must be the exact TEST9 mapped PE")
    if mapped_pe[:2]!=b"MZ":
        raise ValueError("expected PE header")
    if mapped_pe[0x1040000:0x1040008]!=b"SM64LANG":
        raise ValueError("trilingual section signature mismatch")
    if mapped_pe[CURSOR_LABEL_OFF:CURSOR_LABEL_OFF+2]!=OLD:
        raise ValueError("unsafe cursor label: original X NUL not present")
    if mapped_pe[0x1472d4:0x1472d8]!=bytes.fromhex("48275a2d"):
        raise ValueError("native intro call differs")
    if mapped_pe[0xcd128:0xcd12c]!=bytes.fromhex("4bfc8321"):
        raise ValueError("gameplay hook differs")
    image=bytearray(mapped_pe)
    image[CURSOR_LABEL_OFF]=ord("O")
    changed=[i for i,(a,b) in enumerate(zip(mapped_pe,image)) if a!=b]
    if changed!=[CURSOR_LABEL_OFF]:
        raise ValueError("patch modified unexpected bytes")
    out=bytes(image)
    if strict_source and sha(out)!=OUTPUT_PE_SHA256:
        raise ValueError("new PE SHA differs from hardware diagnosis candidate")
    return out,{
        "status":"TEST11_XENIA_VALIDATED_CURSOR_GLYPH_REPLACEMENT_HARDWARE_PENDING",
        "source_pe_sha256":sha(mapped_pe),
        "output_pe_sha256":sha(out),
        "changed_effective_bytes":1,
        "changed_pe_offset":hex(CURSOR_LABEL_OFF),
        "guest_va":hex(CURSOR_LABEL_VA),
        "before":"X",
        "after":"O",
        "all_controller_logic_unchanged":True,
        "all_dialogs_courses_stars_unchanged":True,
        "save_gameplay_code_unchanged":True,
        "dubbing_out_of_scope":True,
        "emulator_status":"XENIA_CANARY_LINUX_VULKAN_LLVMPIPE_PASS",
        "xbox_hardware_status":"PENDING"
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("test9_decrypted_pe",type=Path)
    a.add_argument("patched_pe",type=Path)
    a.add_argument("--audit-json",type=Path)
    opt=a.parse_args()
    out,report=patch(opt.test9_decrypted_pe.read_bytes())
    opt.patched_pe.write_bytes(out)
    if opt.audit_json:
        opt.audit_json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
