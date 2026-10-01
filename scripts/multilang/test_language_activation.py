#!/usr/bin/env python3
from __future__ import annotations
import struct
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as pc
from language_activation import build, ROUTINE_VA, PT_TABLE, ES_TABLE, EN_TABLE, DEST, COUNT

GPR=[getattr(pc,f"UC_PPC_REG_{i}") for i in range(32)]

def run(lang:int, source:int):
    uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    # map code, canonical dialog data, and .lang
    uc.mem_map(0x823B0000,0x10000)
    uc.mem_map(0x829E0000,0x10000)
    uc.mem_map(0x83040000,0x20000)
    raw=build(); uc.mem_write(ROUTINE_VA,raw)

    expected=[(0xA0000000 | (lang<<20) | i) & 0xffffffff for i in range(COUNT)]
    for table,tag in ((PT_TABLE,0),(ES_TABLE,1),(EN_TABLE,2)):
        vals=[(0xA0000000 | (tag<<20) | i) & 0xffffffff for i in range(COUNT)]
        uc.mem_write(table,b''.join(struct.pack('>I',v) for v in vals))

    # Fill each 16-byte canonical record with sentinel bytes.
    sentinel=bytearray()
    for _ in range(COUNT):
        sentinel += b"\xDE\xAD\xBE\xEF" + b"\x55"*12
    uc.mem_write(DEST,bytes(sentinel))

    stop=ROUTINE_VA+len(raw)+4
    uc.reg_write(GPR[3],lang)
    uc.reg_write(pc.UC_PPC_REG_LR,stop)
    uc.hook_add(UC_HOOK_CODE,lambda u,a,s,_: u.emu_stop() if a==stop else None)
    uc.emu_start(ROUTINE_VA,stop+4,count=5000)

    chosen={0:PT_TABLE,1:ES_TABLE}.get(lang,EN_TABLE)
    want=[struct.unpack('>I',uc.mem_read(chosen+i*4,4))[0] for i in range(COUNT)]
    for i,v in enumerate(want):
        rec=bytes(uc.mem_read(DEST+i*16,16))
        assert struct.unpack('>I',rec[:4])[0]==v,(lang,i)
        assert rec[4:]==b"\x55"*12,(lang,i,rec.hex())
    return want[0],want[-1]

def main():
    results={}
    for lang in (0,1,2):
        results[lang]=run(lang,{0:PT_TABLE,1:ES_TABLE,2:EN_TABLE}[lang])
    # Undefined values intentionally fall back to EN.
    results[99]=run(99,EN_TABLE)
    print({"status":"PASS","cases":results,"writes_per_case":COUNT})

if __name__=="__main__":
    main()
