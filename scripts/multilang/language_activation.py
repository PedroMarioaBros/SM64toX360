#!/usr/bin/env python3
"""Build the PowerPC routine that activates one multilingual dialog table.

ABI:
  r3 = language index (0=PT-BR, 1=ES, any other value=EN)
Effects:
  copies 170 32-bit text pointers into the canonical v0.4 dialog records.
  Only r3-r7, CTR and CR0 are clobbered (volatile PPC ABI state).

Canonical addresses:
  PT table 0x83040100
  ES table 0x830403B0
  EN table 0x83040660
  destination records 0x829E7CD8, stride 16
"""

from __future__ import annotations
import hashlib
import json
import struct

ROUTINE_VA = 0x823BC800
PT_TABLE = 0x83040100
ES_TABLE = 0x830403B0
EN_TABLE = 0x83040660
DEST = 0x829E7CD8
COUNT = 170

def build() -> bytes:
    code=[]; labels={}; fix=[]
    def emit(w): code.append(w)
    def label(n): labels[n]=ROUTINE_VA+4*len(code)
    def lis(rt,imm): emit(0x3c000000|(rt<<21)|(imm&0xffff))
    def addi(rt,ra,imm): emit(0x38000000|(rt<<21)|(ra<<16)|(imm&0xffff))
    def cmpwi(ra,imm): emit(0x2c000000|(ra<<16)|(imm&0xffff))
    def beq(n): fix.append((len(code),n,'beq')); emit(0)
    def b(n): fix.append((len(code),n,'b')); emit(0)
    def mtctr(rs): emit(0x7c0903a6|(rs<<21))
    def lwz(rt,d,ra): emit(0x80000000|(rt<<21)|(ra<<16)|(d&0xffff))
    def stw(rs,d,ra): emit(0x90000000|(rs<<21)|(ra<<16)|(d&0xffff))
    def bdnz(n): fix.append((len(code),n,'bdnz')); emit(0)

    cmpwi(3,0); beq('pt')
    cmpwi(3,1); beq('es')
    lis(4,EN_TABLE>>16); addi(4,4,EN_TABLE&0xffff); b('got')
    label('es'); lis(4,ES_TABLE>>16); addi(4,4,ES_TABLE&0xffff); b('got')
    label('pt'); lis(4,PT_TABLE>>16); addi(4,4,PT_TABLE&0xffff)
    label('got')
    lis(5,DEST>>16); addi(5,5,DEST&0xffff)
    addi(6,0,COUNT); mtctr(6)
    label('loop')
    lwz(7,0,4); stw(7,0,5)
    addi(4,4,4); addi(5,5,16)
    bdnz('loop')
    emit(0x4e800020) # blr

    for idx,name,kind in fix:
        pc=ROUTINE_VA+idx*4
        disp=labels[name]-pc
        if kind=='beq': code[idx]=0x41820000|(disp&0xfffc)
        elif kind=='b': code[idx]=0x48000000|(disp&0x03fffffc)
        else: code[idx]=0x42000000|(disp&0xfffc)

    return b''.join(struct.pack('>I',w) for w in code)

def report() -> dict:
    raw=build()
    return {
        "routine_va":hex(ROUTINE_VA),
        "bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "pt_table":hex(PT_TABLE),
        "es_table":hex(ES_TABLE),
        "en_table":hex(EN_TABLE),
        "destination":hex(DEST),
        "dialog_count":COUNT,
    }

if __name__ == "__main__":
    print(json.dumps(report(),indent=2))
