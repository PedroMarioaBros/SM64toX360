#!/usr/bin/env python3
"""TEST10: Xbox title-input READ-ONLY diagnostic based on TEST8 visual PASS.

TEST9 crashed as title appeared, so isolate just the global controller READ.
No change to buttonPressed, no language state, no dialog activation, no Start gate.
Display X beside PT/ES/EN *while* corresponding button is held:
D-pad UP -> X beside PORTUGUES; D-pad DOWN -> X beside ESPANOL;
Xbox A -> X beside ENGLISH. All labels remain static; this is NOT a selector.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from test9_selector_native import PPC, u32, bl, sha

BASE = 0x82000000
TEST8_SHA = 'fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438'
LEN = 17170432
WRAPPER = 0x823BCD00
CALLSITE = 0x821472D4
ORIGINAL_PRINT = 0x82098D18
PRINT_CENTER = 0x8212B498
PAD_PTR = 0x823C8990
LANG_RVA = 0x01040000
CURSOR_OFF = 0x38
LANG_SIZE = 0x20000
CODE_SPACE = 0x300

# Same 3 options/coordinates which successfully rendered in the TEST8.
LABELS = [('PORTUGUES',85,145), ('ESPANOL',85,115), ('ENGLISH',85,85)]
UP = 0x0800
DOWN = 0x0400
A = 0x8000

def render(p,x,y,va):
    p.li(3,x)
    p.li(4,y)
    p.lis(5,(va>>16)&0xffff)
    p.ori(5,5,va&0xffff)
    p.call(PRINT_CENTER)

def build(addrs):
    p=PPC(base=WRAPPER)
    p.w(0x7c0802a6)    # mflr r0
    p.w(0x9421ff80)    # stwu r1, -0x80(r1)
    p.stw(0,0x78,1)   # save LR (matches TEST8 native visual)
    p.call(ORIGINAL_PRINT)
    render(p,85,180,addrs['TESTE10'])
    for name,x,y in LABELS:
        render(p,x,y,addrs[name])

    # This is the ONLY new behaviour compared with TEST8: read controller.
    # PPC D-form signed displacement: (0x823C8990+0x8000)>>16 = 0x823D,
    # lwz signed 0x8990 offsets down to original native global pointer.
    p.lis(11,(PAD_PTR+0x8000)>>16)
    p.lwz(11,PAD_PTR&0xffff,11)
    p.cmpwi(11,0)
    p.branch('done','beq')
    p.lhz(9,0x10,11)   # buttonDown, READ ONLY - no buttonPressed write.
    p.andi(8,9,UP)
    p.cmpwi(8,0)
    p.branch('down','beq')
    p.li(4,145)
    p.branch('marker','b')
    p.label('down')
    p.andi(8,9,DOWN)
    p.cmpwi(8,0)
    p.branch('a','beq')
    p.li(4,115)
    p.branch('marker','b')
    p.label('a')
    p.andi(8,9,A)
    p.cmpwi(8,0)
    p.branch('done','beq')
    p.li(4,85)
    p.label('marker')
    p.li(3,14)
    p.lis(5,addrs['X']>>16)
    p.ori(5,5,addrs['X']&0xffff)
    p.call(PRINT_CENTER)
    p.label('done')
    p.lwz(0,0x78,1)
    p.w(0x38210080)  # addi r1,r1,0x80
    p.w(0x7c0803a6)  # mtlr r0
    p.w(0x4e800020)  # blr
    raw=p.resolve()
    if len(raw)>CODE_SPACE:raise ValueError('routine exceeds previously empty cave')
    return raw

def patch(pe:bytes, strict=True):
    if len(pe)!=LEN or (strict and sha(pe)!=TEST8_SHA):
        raise ValueError('Expected exactly hardware-tested TEST8 mapped PE')
    def require(off,raw):
        if pe[off:off+len(raw)] != raw:
            raise ValueError(f'Unexpected bytes at 0x{off:X}')
    require(0x147448,bytes.fromhex('4bfffe31'))  # no global title hook
    require(CALLSITE-BASE,u32(bl(CALLSITE,WRAPPER)))
    require(0xcd128,bytes.fromhex('4bfc8321'))
    require(LANG_RVA,b'SM64LANG')
    require(0x10400C0,b'COURSE3\0')
    require(0x1040080,bytes(8)) # B/Y scratch unaffected
    require(0x778,b'TESTE8')
    require(0x1c98,b'TESTE8 START')
    old=pe[WRAPPER-BASE:WRAPPER-BASE+112]
    if sha(old)!='53fcb898120d7b30526770bf1e58b622f87aa582b519ef8d9d001251c2991d5c':
        raise ValueError('Missing actual TEST8 native renderer')
    if any(pe[WRAPPER-BASE+112:WRAPPER-BASE+CODE_SPACE]):
        raise ValueError('code cave occupied')
    used=struct.unpack_from('>I',pe,LANG_RVA+CURSOR_OFF)[0]
    if not 0x18000<used<LANG_SIZE:raise ValueError('lang cursor unexpected')
    if any(pe[LANG_RVA+used:LANG_RVA+LANG_SIZE]):
        raise ValueError('nonzero bytes after lang cursor')

    # Use exactly the 3 strings rendered in hardware TEST8.
    addrs={}
    for name,_,_ in LABELS:
        at=pe.find(name.encode('ascii')+b'\0',LANG_RVA+0x18000,LANG_RVA+used)
        if at<0:raise ValueError('TEST8 title label not found: '+name)
        addrs[name]=BASE+at
    image=bytearray(pe)
    at=(used+3)&~3
    for label in ['TESTE10','X']:
        value=label.encode('ascii')+b'\0'
        if at+len(value)>LANG_SIZE:raise ValueError('no space in lang section')
        image[LANG_RVA+at:LANG_RVA+at+len(value)]=value
        addrs[label]=BASE+LANG_RVA+at
        at=(at+len(value)+3)&~3
    struct.pack_into('>I',image,LANG_RVA+CURSOR_OFF,at)
    code=build(addrs)
    image[WRAPPER-BASE:WRAPPER-BASE+CODE_SPACE]=code+bytes(CODE_SPACE-len(code))
    # Preserve the original TEST8 native title resources.
    final=bytes(image)
    permitted=[(WRAPPER-BASE,WRAPPER-BASE+CODE_SPACE),
               (LANG_RVA+CURSOR_OFF,LANG_RVA+CURSOR_OFF+4),
               (LANG_RVA+used,LANG_RVA+at)]
    changes=[i for i,(x,y) in enumerate(zip(pe,final)) if x!=y]
    if any(not any(l<=i<h for l,h in permitted) for i in changes):
        raise ValueError('Unexpected changes to game binary')
    if final[0x1040000:0x1040038]!=pe[0x1040000:0x1040038]:
        raise ValueError('Language state modified')
    if final[0x1040080:0x1040088]!=pe[0x1040080:0x1040088]:
        raise ValueError('B/Y scratch modified')
    if final[0x1040100:0x10406f0]!=pe[0x1040100:0x10406f0]:
        raise ValueError('Dialog pointers modified')
    if final[0xCD128:0xCD12C]!=pe[0xCD128:0xCD12C]:
        raise ValueError('Level script hook modified')
    report={
        'status':'TEST10_READ_ONLY_CONTROLLER_DIAGNOSTIC_NOT_SELECTOR',
        'test8_pe_sha256':sha(pe),'test10_pe_sha256':sha(final),
        'wrapper_va':hex(WRAPPER),'wrapper_bytes':len(code),
        'wrapper_sha256':sha(code), 'changed_byte_count':len(changes),
        'pressed_input_read':'buttonDown at controller+0x10',
        'controller_pointer_global':hex(PAD_PTR),
        'gameplay_byte_mutations':0,'controller_global_writes':0,
        'language_activation':False,'start_blocked':False,
        'title_marker':'TESTE10, with X displayed on held D-pad up/down or A',
        'xbox_result':'PENDING','dubbing_out_of_scope':True
    }
    return final,report

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('test8_mapped_pe',type=Path)
    pa.add_argument('output_mapped_pe',type=Path)
    pa.add_argument('--report',type=Path)
    opts=pa.parse_args()
    output,report=patch(opts.test8_mapped_pe.read_bytes())
    opts.output_mapped_pe.write_bytes(output)
    if opts.report:opts.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()