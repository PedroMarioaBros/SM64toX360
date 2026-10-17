#!/usr/bin/env python3
"""TEST7: diagnostic title branch probe, not a language selector.

Base: original TEST6 mapped PE. Prove whether intro_regular's native call
to print_intro_text renders the visible "PRESS/APERTE START". The Game Over
call is left untouched. This diagnostic only: no runtime string switching,
no B/Y mapping modification and no audio work.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

BASE_PE_SHA="98ec2515a57af928a91369b0cac24a4448aa619d95da63314162afb200a20e4f"
EXPECTED_OUT_SHA="cee2a0cbb4bbb7b47e867e387b13f81e71e72a2f60134851abedc9bfbd4986aa"
MARKERS=((0x778,b"TESTE6",b"TESTE7"),
         (0x1C98,b"TESTE6 START",b"TESTE7 START"))
REGULAR_CALL=0x1472D4
GAMEOVER_CALL=0x147368
TITLE_DISPATCH=0x147448
GLOBAL_LEVEL_CALL=0xCD128
LANG_SECTION=(0x1040000,0x1060000)
ORIGINAL_REGULAR_BL=bytes.fromhex("4bf51a45")
ORIGINAL_GAMEOVER_BL=bytes.fromhex("4bf519b1")
PPC_NOP=bytes.fromhex("60000000")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def patch(mapped_pe:bytes, strict_sha=True):
    if strict_sha and sha(mapped_pe)!=BASE_PE_SHA:
        raise ValueError("TEST7 must use exactly original mapped TEST6 PE")
    if len(mapped_pe)!=17170432:
        raise ValueError("Unexpected mapped TEST6 image length")
    if mapped_pe[REGULAR_CALL:REGULAR_CALL+4]!=ORIGINAL_REGULAR_BL:
        raise ValueError("intro_regular print call differs: do not patch")
    if mapped_pe[GAMEOVER_CALL:GAMEOVER_CALL+4]!=ORIGINAL_GAMEOVER_BL:
        raise ValueError("intro_game_over changed: do not patch")
    if mapped_pe[TITLE_DISPATCH:TITLE_DISPATCH+4]!=bytes.fromhex("482754b9"):
        raise ValueError("missing TEST5/6 selector call for controlled comparison")
    if mapped_pe[GLOBAL_LEVEL_CALL:GLOBAL_LEVEL_CALL+4]!=bytes.fromhex("4bfc8321"):
        raise ValueError("global level script hook unexpectedly modified")
    if mapped_pe[LANG_SECTION[0]:LANG_SECTION[0]+8]!=b"SM64LANG":
        raise ValueError("multilingual data unexpectedly missing")
    allowed=set(range(REGULAR_CALL,REGULAR_CALL+4))
    image=bytearray(mapped_pe)
    for off,old,new in MARKERS:
        if len(old)!=len(new) or image[off:off+len(old)]!=old:
            raise ValueError(f"unexpected title marker at PE offset 0x{off:X}")
        allowed.update(range(off,off+len(old)))
        image[off:off+len(old)]=new
    image[REGULAR_CALL:REGULAR_CALL+4]=PPC_NOP
    changed=[i for i,(x,y) in enumerate(zip(mapped_pe,image)) if x!=y]
    if any(i not in allowed for i in changed):
        raise ValueError("unrelated binary region changed")
    if image[LANG_SECTION[0]:LANG_SECTION[1]]!=mapped_pe[LANG_SECTION[0]:LANG_SECTION[1]]:
        raise ValueError("PT/ES/EN data changed")
    if image[GAMEOVER_CALL:GAMEOVER_CALL+4]!=ORIGINAL_GAMEOVER_BL:
        raise ValueError("Game Over branch changed")
    result=bytes(image)
    report={
        "status":"TEST7_DIAGNOSTIC_NOT_NEW_FUNCTIONAL_SELECTOR",
        "source_pe_sha256":sha(mapped_pe),
        "output_pe_sha256":sha(result),
        "changed_byte_count":len(changed),
        "changed_positions_hex":[hex(x) for x in changed],
        "regular_intro_print_skipped":True,
        "game_over_intro_print_untouched":True,
        "all_language_data_identical":True,
        "selector_code_and_saves_unchanged":True,
        "dubbing_out_of_scope":True,
        "hardware_result":"PENDING"
    }
    return result,report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test6_mapped_pe",type=Path)
    parser.add_argument("output_pe",type=Path)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    result,report=patch(args.test6_mapped_pe.read_bytes())
    if sha(result)!=EXPECTED_OUT_SHA: raise ValueError("unexpected output PE digest")
    args.output_pe.write_bytes(result)
    if args.report:
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
