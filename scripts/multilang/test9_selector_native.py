#!/usr/bin/env python3
"""TEST9 trial: title-only, real font, D-pad selection and A activation.

Source must be the exact hardware-verified TEST8 PE. No global hooks or
changes to B/Y state, PT-BR dialogue pool, gameplay, save or audio.

Hardware outcome pending until console test. Not a stable release.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

BASE=0x82000000
TEST8_PE_SHA='fab6a7c31d1fa2cb4aea3ad5e0f3171bde5248a13f48bbcab56d2bc05fc4c438'
PE_LEN=17170432
CALLSITE=0x821472D4
ORIGINAL_PRINT=0x82098D18
PRINT_CENTER=0x8212B498
WRAPPER=0x823BCD00
CAVE=0x300
ACTIVATE_DIALOGS=0x823BC800
ACTIVATE_COURSES=0x823BCC00
CONTROLLER_GLOBAL=0x823C8990
LANG_BASE=0x83040000
LANG_RVA=0x1040000
LANG_CAPACITY=0x20000
STATE_OFF=0x14
INDEX_OFF=0x18
CURSOR_OFF=0x38
TITLE_CALL_ORIGINAL=bytes.fromhex('4bfffe31')
TITLE_PREVIOUS_BL=bytes.fromhex('48275a2d')
LABELS=[('IDIOMAS',72,203),('PORTUGUES',70,164),('ESPANOL',70,134),('ENGLISH',70,104),('A CONFIRMAR',65,43)]
MARKER=('X',14,None)
BTN_UP=0x0800
BTN_DOWN=0x0400
BTN_START=0x1000
BTN_A=0x8000

sha=lambda b:hashlib.sha256(b).hexdigest()

def u32(x):return struct.pack('>I',x&0xffffffff)

def bl(src,target):
    delta=target-src
    if delta%4 or not -(1<<25)<=delta<(1<<25):raise ValueError(f'BL out of range: {src:08x} -> {target:08x}')
    return 0x48000001 | (delta & 0x03fffffc)

class PPC:
    def __init__(self,base=WRAPPER):self.base=base;self.code=[];self.labels={};self.fix=[]
    @property
    def pc(self):return self.base+4*len(self.code)
    def w(self,x):self.code.append(x & 0xffffffff)
    def label(self,s):
        if s in self.labels:raise ValueError('label repeated')
        self.labels[s]=self.pc
    def lis(self,rt,imm):self.w(0x3c000000|(rt<<21)|(imm&0xffff))
    def ori(self,ra,rs,imm):self.w(0x60000000|(rs<<21)|(ra<<16)|(imm&0xffff))
    def addi(self,rt,ra,imm):self.w(0x38000000|(rt<<21)|(ra<<16)|(imm&0xffff))
    def li(self,rt,imm):self.addi(rt,0,imm)
    def lwz(self,rt,d,ra):self.w(0x80000000|(rt<<21)|(ra<<16)|(d&0xffff))
    def stw(self,rs,d,ra):self.w(0x90000000|(rs<<21)|(ra<<16)|(d&0xffff))
    def lhz(self,rt,d,ra):self.w(0xa0000000|(rt<<21)|(ra<<16)|(d&0xffff))
    def sth(self,rs,d,ra):self.w(0xb0000000|(rs<<21)|(ra<<16)|(d&0xffff))
    def cmpwi(self,ra,imm):self.w(0x2c000000|(ra<<16)|(imm&0xffff))
    def andi(self,ra,rs,imm):self.w(0x70000000|(rs<<21)|(ra<<16)|(imm&0xffff))
    def call(self,target):self.w(bl(self.pc,target))
    def branch(self,label,kind='b'):
        if kind not in ('b','beq','bne'):raise ValueError('branch kind')
        self.fix.append((len(self.code),label,kind));self.w(0)
    def resolve(self):
        for idx,label,kind in self.fix:
            at=self.base+4*idx
            disp=self.labels[label]-at
            if disp%4:raise ValueError('unaligned branch')
            if kind=='b':
                if not -(1<<25)<=disp<(1<<25):raise ValueError('far b')
                word=0x48000000|(disp&0x03fffffc)
            else:
                if not -0x8000<=disp<0x8000:raise ValueError('far bc')
                word=(0x41820000 if kind=='beq' else 0x40820000)|(disp&0xfffc)
            self.code[idx]=word
        return b''.join(u32(w) for w in self.code)

def native_render(p: PPC,x:int,y:int,addr:int):
    p.li(3,x);p.li(4,y)
    p.lis(5,(addr>>16)&0xffff);p.ori(5,5,addr&0xffff)
    p.call(PRINT_CENTER)

def build(addrs):
    p=PPC()
    p.w(0x7c0802a6)          # mflr r0
    p.w(0x9421ff80)          # stwu r1,-0x80(r1)
    p.stw(0,0x78,1)          # save LR
    p.lis(11,LANG_BASE>>16)
    p.lwz(10,STATE_OFF,11)
    p.cmpwi(10,0)
    p.branch('pass_original','bne')

    # This callback is proven to run on real Xbox (TEST7 A, TEST8 visual).
    # Native intro_regular checks buttonPressed right AFTER this callback.
    p.lis(11,(CONTROLLER_GLOBAL+0x8000)>>16)
    p.lwz(11,CONTROLLER_GLOBAL&0xffff,11)
    p.cmpwi(11,0)
    p.branch('draw','beq')
    p.lhz(9,0x12,11)            # native Controller.buttonPressed
    p.andi(8,9,~BTN_START & 0xffff)
    p.sth(8,0x12,11)            # keep START masked through caller's check

    # Priority: UP / DOWN / A. One action per frame.
    p.andi(8,9,BTN_UP)
    p.cmpwi(8,0)
    p.branch('down','beq')
    p.lis(11,LANG_BASE>>16)
    p.lwz(10,INDEX_OFF,11)
    p.cmpwi(10,0)
    p.branch('decrement','bne')
    p.li(10,2)
    p.branch('write_index','b')
    p.label('decrement');p.addi(10,10,-1)
    p.branch('write_index','b')
    p.label('down')
    p.andi(8,9,BTN_DOWN)
    p.cmpwi(8,0)
    p.branch('check_A','beq')
    p.lis(11,LANG_BASE>>16)
    p.lwz(10,INDEX_OFF,11)
    p.cmpwi(10,2)
    p.branch('increment','bne')
    p.li(10,0)
    p.branch('write_index','b')
    p.label('increment');p.addi(10,10,1)
    p.label('write_index');p.stw(10,INDEX_OFF,11)
    p.branch('draw','b')
    p.label('check_A')
    p.andi(8,9,BTN_A)
    p.cmpwi(8,0)
    p.branch('draw','beq')
    p.lis(11,LANG_BASE>>16)
    p.lwz(3,INDEX_OFF,11)
    p.call(ACTIVATE_DIALOGS)   # 170 canonical dialog pointer slots
    p.lis(11,LANG_BASE>>16)
    p.lwz(3,INDEX_OFF,11)
    p.call(ACTIVATE_COURSES)   # 26 courses + 90 stars
    p.lis(11,LANG_BASE>>16)
    p.li(10,1)
    p.stw(10,STATE_OFF,11)
    p.branch('pass_original','b')

    p.label('draw')
    for label,x,y in LABELS:
        native_render(p,x,y,addrs[label])
    # Highlight using color font's valid ASCII 'X'.
    p.lis(11,LANG_BASE>>16)
    p.lwz(10,INDEX_OFF,11)
    p.cmpwi(10,0)
    p.branch('marker_pt','beq')
    p.cmpwi(10,1)
    p.branch('marker_es','beq')
    p.li(4,104)
    p.branch('marker','b')
    p.label('marker_pt');p.li(4,164)
    p.branch('marker','b')
    p.label('marker_es');p.li(4,134)
    p.label('marker')
    p.li(3,MARKER[1])
    p.lis(5,(addrs['X']>>16)&0xffff);p.ori(5,5,addrs['X']&0xffff)
    p.call(PRINT_CENTER)
    p.branch('epilogue','b')

    p.label('pass_original')
    p.call(ORIGINAL_PRINT)
    p.label('epilogue')
    p.lwz(0,0x78,1)
    p.w(0x38210080)
    p.w(0x7c0803a6)
    p.w(0x4e800020)
    raw=p.resolve()
    if len(raw)>CAVE:raise ValueError(f'code length {len(raw)} exceeds {CAVE}')
    return raw

def patch(pe:bytes,strict=True):
    if len(pe)!=PE_LEN or (strict and sha(pe)!=TEST8_PE_SHA):raise ValueError('requires exact TEST8 mapped PE')
    def chk(off,expected):
        if pe[off:off+len(expected)]!=expected:raise ValueError(f'unexpected bytes at {off:#x}')
    chk(0x1040000,b'SM64LANG')
    chk(0x10400C0,b'COURSE3\0')
    chk(0x147448,TITLE_CALL_ORIGINAL)
    chk(0xCD128,bytes.fromhex('4bfc8321'))
    chk(0x1040014,bytes(8)) # state and index must be zero at initial boot
    chk(0x1040080,bytes(8)) # live B/Y scratch space
    chk(0x778,b'TESTE8');chk(0x1c98,b'TESTE8 START')
    prev_code_len=112
    old_code=pe[WRAPPER-BASE:WRAPPER-BASE+prev_code_len]
    if sha(old_code)!='53fcb898120d7b30526770bf1e58b622f87aa582b519ef8d9d001251c2991d5c':
        raise ValueError('unexpected TEST8 overlay function')
    if any(pe[WRAPPER-BASE+prev_code_len:WRAPPER-BASE+CAVE]):raise ValueError('nonzero TEST8 free cave tail')
    cur=struct.unpack_from('>I',pe,LANG_RVA+CURSOR_OFF)[0]
    if not 0x18000<cur<LANG_CAPACITY:raise ValueError('bad .lang cursor')
    if any(pe[LANG_RVA+cur:LANG_RVA+LANG_CAPACITY]):raise ValueError('unallocated .lang payload not zero')
    out=bytearray(pe)
    addrs={}
    new_cursor=cur
    for label,_,_ in LABELS:
        # Reuse the original TEST8 strings for languages. Always append
        # the new title and help text rather than destructively edit pools.
        if label in ('PORTUGUES','ESPANOL','ENGLISH'):
            found=pe.find(label.encode('ascii')+b'\0',LANG_RVA+0x18000,LANG_RVA+cur)
            if found<0:raise ValueError(f'existing TEST8 label missing: {label}')
            addrs[label]=BASE+found
            continue
        new_cursor=(new_cursor+3)&~3
        blob=label.encode('ascii')+b'\0'
        at=LANG_RVA+new_cursor
        if new_cursor+len(blob)>LANG_CAPACITY:raise ValueError('.lang payload overflow')
        out[at:at+len(blob)]=blob
        addrs[label]=BASE+at
        new_cursor+=len(blob)
    new_cursor=(new_cursor+3)&~3
    out[LANG_RVA+new_cursor:LANG_RVA+new_cursor+2]=b'X\0'
    addrs['X']=BASE+LANG_RVA+new_cursor
    new_cursor+=2
    struct.pack_into('>I',out,LANG_RVA+CURSOR_OFF,new_cursor)
    code=build(addrs)
    out[WRAPPER-BASE:WRAPPER-BASE+CAVE]=code+b'\0'*(CAVE-len(code))
    # Keep the exact hardware-verified title printing call from TEST8.
    if pe[CALLSITE-BASE:CALLSITE-BASE+4]!=u32(bl(CALLSITE,WRAPPER)):
        raise ValueError('TEST8 title print call modified')
    # Replace diagnostic message with normal post-confirmation start prompt.
    out[0x778:0x77e]=b'APERTE'
    out[0x1c98:0x1c9e]=b'APERTE'
    img=bytes(out)
    mutable=[(WRAPPER-BASE,WRAPPER-BASE+CAVE),(LANG_RVA+CURSOR_OFF,LANG_RVA+CURSOR_OFF+4),
             (LANG_RVA+cur,LANG_RVA+new_cursor),(0x778,0x77e),(0x1c98,0x1c9e)]
    changed=[i for i,(a,b) in enumerate(zip(pe,img)) if a!=b]
    if any(not any(a<=i<b for a,b in mutable) for i in changed):
        raise ValueError('unrelated game code or PT-BR changed')
    if img[0x1040100:0x10406f0]!=pe[0x1040100:0x10406f0]:
        raise ValueError('canonical PT/ES/EN pointers changed')
    if img[0x1040080:0x1040088]!=pe[0x1040080:0x1040088]:
        raise ValueError('B/Y runtime scratch mutated')
    if img[0xCD128:0xCD12C]!=pe[0xCD128:0xCD12C]:
        raise ValueError('global level script hook mutated')
    return img, {'status':'TEST9_INTERACTIVE_CANDIDATE_NOT_HARDWARE_VALIDATED',
                 'source_pe_sha256':sha(pe),'candidate_pe_sha256':sha(img),
                 'new_runtime_code_bytes':len(code),'new_runtime_code_sha256':sha(code),
                 'code_cave_va':hex(WRAPPER),'controller_global_va':hex(CONTROLLER_GLOBAL),
                 'input':'DPAD_UP_0x0800_DOWN_0x0400_A_0x8000_START_MASK_0x1000',
                 'labels':[s for s,_,_ in LABELS], 'changed_actual_bytes':len(changed),
                 'lang_old_used':cur,'lang_new_used':new_cursor,
                 'lang_free':LANG_CAPACITY-new_cursor,
                 'ptbr_dialog_pointers_unchanged':True,'gameplay_hook_original':True,
                 'dubbing_out_of_scope':True,'hardware_test':'PENDING'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source_test8_pe',type=Path)
    ap.add_argument('output_test9_pe',type=Path)
    ap.add_argument('--report',type=Path)
    opts=ap.parse_args()
    pe,report=patch(opts.source_test8_pe.read_bytes())
    opts.output_test9_pe.write_bytes(pe)
    if opts.report:opts.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))