#!/usr/bin/env python3
"""TEST8 VISUAL ONLY. Replace hardware-confirmed intro_regular print call with
a tiny wrapper that calls original print_intro_text and native print_text_centered.

No D-pad/A handler or language switching in this probe. TEST3 PT-BR baseline,
gameplay, saves, level script and audio unaffected. Requires exact TEST7 PE.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

BASE=0x82000000
SOURCE_SHA="cee2a0cbb4bbb7b47e867e387b13f81e71e72a2f60134851abedc9bfbd4986aa"
LEN=17170432
ORIGINAL_PRINT=0x82098D18
PRINT_CENTER=0x8212B498
WRAPPER=0x823BCD00
WRAPPER_SPACE=0x200
PRINT_CALLSITE=0x821472D4
TITLE_DISPATCH=0x82147448
LANG_BASE_RVA=0x1040000
LANG_CAPACITY=0x20000
CURSOR_OFFSET=LANG_BASE_RVA+0x38
LABELS=[("IDIOMAS TESTE8",85,180),("PORTUGUES",85,145),("ESPANOL",85,115),("ENGLISH",85,85)]
TEST7_NOP=bytes.fromhex("60000000")
TEST5_TITLE_BL=bytes.fromhex("482754b9")
ORIGINAL_TITLE_BL=bytes.fromhex("4bfffe31")

def sha(data):return hashlib.sha256(data).hexdigest()
def word(x):return struct.pack(">I",x&0xffffffff)
def li(reg,n):
    if not -32768<=n<=32767:raise ValueError("li out of range")
    return 0x38000000|(reg<<21)|(n&0xffff)
def lis(reg,n):return 0x3c000000|(reg<<21)|(n&0xffff)
def ori(dest,source,n):return 0x60000000|(source<<21)|(dest<<16)|(n&0xffff)
def bl(src,dst):
    delta=dst-src
    if delta%4 or not -(1<<25)<=delta<(1<<25):raise ValueError("PPC BL out of range")
    return 0x48000001|(delta&0x03fffffc)

def wrapper_code(addrs):
    ins=[]
    def emit(v):ins.append(v)
    def call(target):emit(bl(WRAPPER+4*len(ins),target))
    emit(0x7c0802a6) # mflr r0
    emit(0x9421ff80) # stwu r1,-128(r1)
    emit(0x90010078) # stw r0,120(r1)
    call(ORIGINAL_PRINT)
    for name,x,y in LABELS:
        va=addrs[name]
        emit(li(3,x));emit(li(4,y))
        emit(lis(5,va>>16));emit(ori(5,5,va&0xffff))
        call(PRINT_CENTER)
    emit(0x80010078) # lwz r0,120(r1)
    emit(0x38210080) # addi r1,r1,128
    emit(0x7c0803a6) # mtlr r0
    emit(0x4e800020) # blr
    data=b"".join(word(v) for v in ins)
    if len(data)>WRAPPER_SPACE:raise ValueError("title wrapper exceeds reserved cave")
    return data

def patch(pe:bytes,require_sha=True):
    if len(pe)!=LEN or (require_sha and sha(pe)!=SOURCE_SHA):
        raise ValueError("need exact TEST7 mapped PE")
    def check(at,expected):
        if pe[at:at+len(expected)]!=expected:
            raise ValueError(f"unrecognized bytes at PE offset {at:#x}")
    check(PRINT_CALLSITE-BASE,TEST7_NOP)
    check(TITLE_DISPATCH-BASE,TEST5_TITLE_BL)
    check(0xCD128,bytes.fromhex("4bfc8321"))
    check(LANG_BASE_RVA,b"SM64LANG")
    check(WRAPPER-BASE,bytes(WRAPPER_SPACE))
    check(0x778,b"TESTE7")
    check(0x1C98,b"TESTE7 START")
    cur=struct.unpack_from(">I",pe,CURSOR_OFFSET)[0]
    if not 0x18000<=cur<LANG_CAPACITY:raise ValueError("unexpected .lang cursor")
    if any(pe[LANG_BASE_RVA+cur:LANG_BASE_RVA+LANG_CAPACITY]):
        raise ValueError(".lang free region contains unknown bytes")
    out=bytearray(pe)
    addrs={}
    old_cur=cur
    for name,_,_ in LABELS:
        cur=(cur+3)&~3
        data=name.encode("ascii")+b"\0"
        if cur+len(data)>LANG_CAPACITY:raise ValueError("exhausted section")
        at=LANG_BASE_RVA+cur
        out[at:at+len(data)]=data
        addrs[name]=BASE+at
        cur+=len(data)
    struct.pack_into(">I",out,CURSOR_OFFSET,cur)
    code=wrapper_code(addrs)
    out[WRAPPER-BASE:WRAPPER-BASE+len(code)]=code
    out[PRINT_CALLSITE-BASE:PRINT_CALLSITE-BASE+4]=word(bl(PRINT_CALLSITE,WRAPPER))
    out[TITLE_DISPATCH-BASE:TITLE_DISPATCH-BASE+4]=ORIGINAL_TITLE_BL
    out[0x778:0x77e]=b"TESTE8"
    out[0x1c98:0x1c9e]=b"TESTE8"
    result=bytes(out)
    allowed=[
        (WRAPPER-BASE,WRAPPER-BASE+len(code)),
        (PRINT_CALLSITE-BASE,PRINT_CALLSITE-BASE+4),
        (TITLE_DISPATCH-BASE,TITLE_DISPATCH-BASE+4),
        (0x778,0x77e),(0x1c98,0x1c9e),
        (CURSOR_OFFSET,CURSOR_OFFSET+4),
        (LANG_BASE_RVA+old_cur,LANG_BASE_RVA+cur+4)
    ]
    changed=[i for i,(a,b) in enumerate(zip(pe,result)) if a!=b]
    if any(not any(lo<=i<hi for lo,hi in allowed) for i in changed):
        raise ValueError("unrelated byte differences")
    if result[0xCD128:0xCD12c]!=pe[0xCD128:0xCD12c]:
        raise ValueError("global level script hook changed")
    if result[0x1040100:0x10406f0]!=pe[0x1040100:0x10406f0]:
        raise ValueError("PT/ES/EN pointers changed")
    if result[0x1040080:0x1040088]!=pe[0x1040080:0x1040088]:
        raise ValueError("B/Y state changed")
    return result,{
        "status":"TEST8_NATIVE_TITLE_VISUAL_ONLY_NOT_FUNCTIONAL_SELECTOR",
        "source_sha256":sha(pe),"output_pe_sha256":sha(result),
        "changed_bytes":len(changed),
        "title_dispatch_restored_to_original":True,
        "intro_regular_print_call_wrapped":True,
        "native_title_font":True,
        "dialog_and_course_pointers_unchanged":True,
        "script_global_hook_unchanged":True,
        "language_labels_approximate_no_accents":True,
        "labels":[name for name,_,_ in LABELS],
        "code_va":hex(WRAPPER),"code_bytes":len(code),
        "code_sha256":sha(code),"old_cursor":old_cur,"new_cursor":cur,
        "xbox_hardware_result":"PENDING",
        "dubbing":"OUT_OF_SCOPE"
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("test7_mapped_pe",type=Path)
    a.add_argument("output_pe",type=Path)
    a.add_argument("--report",type=Path)
    args=a.parse_args()
    output,report=patch(args.test7_mapped_pe.read_bytes())
    args.output_pe.write_bytes(output)
    if args.report:args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":main()
