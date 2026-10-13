#!/usr/bin/env python3
"""Emula a rotina de nomes de fases EN/ES/PT em PowerPC sem console Xbox."""
import struct
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as p
from course_table_activation import (
    build,report,ROUTINE_VA,LANG_BASE,
    COURSE_DEST,STAR_DEST,COURSE_COUNT,STAR_COUNT
)

GPR=[getattr(p,f"UC_PPC_REG_{i}") for i in range(32)]
TABLES={
    "course":[0x2000,0x2100,0x2200],
    "star":[0x2300,0x2500,0x2700],
}

def run(lang:int):
    uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    uc.mem_map(0x823B0000,0x10000)
    uc.mem_map(0x829E0000,0x10000)
    uc.mem_map(LANG_BASE,0x20000)
    code=build()
    uc.mem_write(ROUTINE_VA,code)
    for class_id,(section,count,dest,meta) in enumerate((
        ("course",COURSE_COUNT,COURSE_DEST,0xD8),
        ("star",STAR_COUNT,STAR_DEST,0xE4)
    )):
        for idx,off in enumerate(TABLES[section]):
            val=[0x90000000|(idx<<20)|(class_id<<18)|j for j in range(count)]
            uc.mem_write(LANG_BASE+off,b"".join(struct.pack(">I",z) for z in val))
            uc.mem_write(LANG_BASE+meta+4*idx,struct.pack(">I",off))
        uc.mem_write(dest-4,b"\xDE\xAD\xBE\xEF")
        uc.mem_write(dest,b"\xAA"*(count*4))
        uc.mem_write(dest+count*4,b"\xFE\xED\xFA\xCE")

    stop=ROUTINE_VA+len(code)+4
    uc.reg_write(GPR[3],lang)
    uc.reg_write(p.UC_PPC_REG_LR,stop)
    uc.hook_add(UC_HOOK_CODE,lambda u,a,s,d: u.emu_stop() if a==stop else None)
    uc.emu_start(ROUTINE_VA,stop+4,count=5000)
    selected=lang if lang in (0,1,2) else 0
    for class_id,(section,count,dest,_) in enumerate((
        ("course",COURSE_COUNT,COURSE_DEST,0xD8),
        ("star",STAR_COUNT,STAR_DEST,0xE4)
    )):
        seen=list(struct.unpack(">"+str(count)+"I",uc.mem_read(dest,count*4)))
        desired=[0x90000000|(selected<<20)|(class_id<<18)|j for j in range(count)]
        assert seen==desired,(lang,section,seen[:4],desired[:4])
        assert bytes(uc.mem_read(dest-4,4))==b"\xDE\xAD\xBE\xEF"
        assert bytes(uc.mem_read(dest+count*4,4))==b"\xFE\xED\xFA\xCE"
    assert uc.reg_read(GPR[3])==selected,(lang,"wrong selection")
    return {"language":lang,"resolved":selected,
            "names_written":COURSE_COUNT,"stars_written":STAR_COUNT}

if __name__=="__main__":
    results=[run(x) for x in (0,1,2,99,-1)]
    print({"status":"PPC_EMULATION_PASS_NO_XBOX_GAMEPLAY","cases":results,
           "routine":report(),"console_tested":False})
