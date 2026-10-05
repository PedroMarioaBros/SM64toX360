#!/usr/bin/env python3
from __future__ import annotations
import struct
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as pc
from pregame_gate import (
    build, GATE_VA, LANG_BASE, ORIG_LEVEL_SCRIPT_EXECUTE, INIT_RCP, RENDER_GAME,
    CREATE_DL_ORTHO, PRINT_GENERIC_STRING_FADE, END_MASTER_DISPLAY_LIST,
    ALLOC_DISPLAY_LIST, ACTIVATE_LANGUAGE, PLAYER1_CONTROLLER_PTR,
)

R3=pc.UC_PPC_REG_3
LR=pc.UC_PPC_REG_LR
SP=pc.UC_PPC_REG_1
STOP=0x8400F000
STACK=0x81010000
CTRL=0x84001000
LEVEL_PTR=0x82ABCDEF

EXTERNALS={
    INIT_RCP:"init",
    RENDER_GAME:"render",
    CREATE_DL_ORTHO:"ortho",
    PRINT_GENERIC_STRING_FADE:"print",
    END_MASTER_DISPLAY_LIST:"end",
    ALLOC_DISPLAY_LIST:"alloc",
    ACTIVATE_LANGUAGE:"activate",
    ORIG_LEVEL_SCRIPT_EXECUTE:"original",
}

def put32(uc,addr,v): uc.mem_write(addr,struct.pack(">I",v&0xffffffff))
def get32(uc,addr): return struct.unpack(">I",bytes(uc.mem_read(addr,4)))[0]
def put16(uc,addr,v): uc.mem_write(addr,struct.pack(">H",v&0xffff))

def run(state, selection=0, timer=0, buttons=0):
    uc=Uc(UC_ARCH_PPC, UC_MODE_32|UC_MODE_BIG_ENDIAN)
    for base,size in [
        (0x81000000,0x20000),(0x82090000,0x70000),(0x820CE000,0x10000),
        (0x82140000,0x10000),(0x823B0000,0x20000),(0x82E50000,0x10000),(0x83040000,0x20000),
        (0x84000000,0x20000)
    ]:
        try: uc.mem_map(base,size)
        except Exception: pass

    uc.mem_write(GATE_VA,build())
    # External targets only need mapped instruction bytes; hook returns them.
    for addr in EXTERNALS:
        try: uc.mem_write(addr,b"\x4e\x80\x00\x20")
        except Exception: pass

    put32(uc,LANG_BASE+0x14,state)
    put32(uc,LANG_BASE+0x18,selection)
    put32(uc,LANG_BASE+0x1c,timer)
    for i in range(12):
        put32(uc,LANG_BASE+0x40+i*4,LANG_BASE+0x18000+i*0x20)

    put32(uc,PLAYER1_CONTROLLER_PTR,CTRL)
    put16(uc,CTRL+0x12,buttons)

    calls=[]
    activation=[]
    def hook(uc,address,size,user):
        if address==STOP:
            uc.emu_stop(); return
        if address not in EXTERNALS:
            return
        kind=EXTERNALS[address]
        calls.append(kind)
        if kind=="activate":
            activation.append(uc.reg_read(R3))
        if kind=="original":
            uc.reg_write(R3,0xDEADBEEF)
        uc.reg_write(pc.UC_PPC_REG_PC,uc.reg_read(LR))

    uc.hook_add(UC_HOOK_CODE,hook)
    uc.reg_write(SP,STACK+0x1F000)
    uc.reg_write(R3,LEVEL_PTR)
    uc.reg_write(LR,STOP)
    uc.emu_start(GATE_VA,STOP+4,count=5000)
    return {
        "state":get32(uc,LANG_BASE+0x14),
        "selection":get32(uc,LANG_BASE+0x18),
        "timer":get32(uc,LANG_BASE+0x1c),
        "r3":uc.reg_read(R3)&0xffffffff,
        "calls":calls,
        "activation":activation,
    }

def main():
    c=run(0,0,0,0)
    assert c["state"]==0 and c["timer"]==1 and c["r3"]==LEVEL_PTR
    assert c["calls"].count("print")==6 and "original" not in c["calls"]

    c=run(0,0,44,0)
    assert (c["state"],c["selection"],c["timer"])==(1,0,0)

    c=run(0,0,0,0x8000)
    assert c["state"]==1

    c=run(1,0,0,0x0800)
    assert c["selection"]==2
    c=run(1,2,0,0x0400)
    assert c["selection"]==0

    c=run(1,1,0,0x8000)
    assert c["state"]==2 and c["activation"]==[1] and "original" not in c["calls"]
    assert c["r3"]==LEVEL_PTR

    c=run(2,2,0,0)
    assert c["calls"]==["original"] and c["r3"]==0xDEADBEEF

    print({
        "status":"PASS",
        "credits":"timer + A skip",
        "navigation":"UP/DOWN wrap",
        "confirm":"activation receives selected language",
        "release":"state 2 delegates only to original level_script_execute",
    })

if __name__=="__main__":
    main()
