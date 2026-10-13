#!/usr/bin/env python3
"""Emula PPC title-only selector (sem GPU/console) e bloqueia regressões."""
import struct
import unittest

from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as pc

from title_only_selector import (
    build,install,WRAPPER,CALLSITE,ORIGINAL_CALL_BE,BASE,
    ORIGINAL_INTRO,PRINT,ACTIVATE_DIALOGS,ACTIVATE_COURSES,
    CONTROLLER_PTR,LANG_BASE,
)
from language_activation import PT_TABLE,ES_TABLE,EN_TABLE,DEST as DIALOG_DEST
from course_table_activation import (
    COURSE_DEST,STAR_DEST,COURSE_COUNT,STAR_COUNT,COURSE_META,STAR_META,
)

GPR=[getattr(pc,"UC_PPC_REG_"+str(i)) for i in range(32)]
LR=pc.UC_PPC_REG_LR
PC=pc.UC_PPC_REG_PC
STACK=0x81010000
STOP=0x84010000
CONTROLLER=0x84000200

def write16(uc,addr,val):
    uc.mem_write(addr,struct.pack(">H",val&0xffff))
def read16(uc,addr):
    return struct.unpack(">H",bytes(uc.mem_read(addr,2)))[0]
def write32(uc,addr,val):
    uc.mem_write(addr,struct.pack(">I",val&0xffffffff))
def read32(uc,addr):
    return struct.unpack(">I",bytes(uc.mem_read(addr,4)))[0]

def exercise(state,selected,buttons,held=0,force_dummy_original=0):
    uc=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    for b,s in ((0x82000000,0x1000000),(LANG_BASE,0x20000),
                (0x81000000,0x20000),(0x84000000,0x20000)):
        uc.mem_map(b,s)
    uc.mem_write(WRAPPER,build())
    write32(uc,LANG_BASE+0x14,state)
    write32(uc,LANG_BASE+0x18,selected)
    uc.mem_write(LANG_BASE+0xC0,b"COURSE3\0")
    uc.mem_write(LANG_BASE+0x80,b"\xA5\xB6\xC7\xD8\xE9\xFA\xAB\xCD")
    write32(uc,CONTROLLER_PTR,CONTROLLER)
    write16(uc,CONTROLLER+0x10,held)
    write16(uc,CONTROLLER+0x12,buttons)
    write32(uc,0x82E52F88,0x7E11001B) # alpha and fade are separate bytes

    for idx,t in enumerate((PT_TABLE,ES_TABLE,EN_TABLE)):
        for i in range(170):
            write32(uc,t+4*i,(0xAB000000|(idx<<20)|i))
    for section, dest, meta, count, offsets in (
        ("course",COURSE_DEST,COURSE_META,COURSE_COUNT,(0x1C000,0x1C100,0x1C200)),
        ("star",STAR_DEST,STAR_META,STAR_COUNT,(0x1C300,0x1C500,0x1C700))
    ):
        for idx,off in enumerate(offsets):
            write32(uc,meta+4*idx,off)
            for i in range(count):
                write32(uc,LANG_BASE+off+4*i,0xBC000000|(idx<<20)|(int(section=="star")<<18)|i)
        uc.mem_write(dest,b"\x55"*(count*4))
        uc.mem_write(dest-4,b"\x12\x34\x56\x78")
        uc.mem_write(dest+count*4,b"\x89\xAB\xCD\xEF")

    calls=[]
    shown=[]
    native_return=force_dummy_original
    uc.reg_write(GPR[1],STACK+0xF000)
    uc.reg_write(LR,STOP)
    uc.reg_write(GPR[30],0x11223344)
    uc.reg_write(GPR[31],0x55667788)

    def hook(u,addr,size,user):
        if addr==STOP:
            u.emu_stop();return
        word=read32(u,addr)
        opcode=word>>26
        rt=(word>>21)&31
        ra=(word>>16)&31
        ds=word&0xFFFC
        ds=ds-0x10000 if ds&0x8000 else ds
        # Unicorn in PPC32 mode cannot execute the native64 std/ld frame.
        if opcode in (58,62) and word&3==0:
            ptr=(u.reg_read(GPR[ra])+ds)&0xffffffff
            if opcode==62: u.mem_write(ptr,struct.pack(">Q",u.reg_read(GPR[rt])))
            else: u.reg_write(GPR[rt],int.from_bytes(u.mem_read(ptr,8),"big")&0xffffffff)
            u.reg_write(PC,addr+4);return
        if addr==ORIGINAL_INTRO:
            down=read16(u,CONTROLLER+0x10)
            pressed=read16(u,CONTROLLER+0x12)
            calls.append(("intro",down,pressed))
            u.reg_write(GPR[3],100 if pressed&0x1000 else native_return)
            u.reg_write(PC,u.reg_read(LR));return
        if addr==PRINT:
            shown.append((u.reg_read(GPR[3]),u.reg_read(GPR[4]),u.reg_read(GPR[5])))
            u.reg_write(PC,u.reg_read(LR));return

    uc.hook_add(UC_HOOK_CODE,hook)
    uc.emu_start(WRAPPER,STOP+4,count=10000)

    # Native v0.4 pointer activation actual CPU code is separately covered by
    # test_language_activation + test_course_table_activation_ppc. This test
    # stops at the first activation and does not claim full game emulation.
    return uc,calls,shown

class TitleOnlySelectorTests(unittest.TestCase):
    def test_code_cave_within_reserved_range(self):
        self.assertLessEqual(len(build()),0x300)

    def test_title_navigation_retains_native_controller_buttons(self):
        for old,button,expected in ((0,0x0800,2),(0,0x0400,1),(2,0x0400,0)):
            u,calls,shown=exercise(0,old,button)
            self.assertEqual(read32(u,LANG_BASE+0x18),expected)
            self.assertEqual(read32(u,LANG_BASE+0x14),0)
            self.assertEqual(read16(u,CONTROLLER+0x12),button)
            self.assertEqual(read16(u,CONTROLLER+0x10),0)
            self.assertEqual(bytes(u.mem_read(LANG_BASE+0x80,8)),b"\xA5\xB6\xC7\xD8\xE9\xFA\xAB\xCD")
            self.assertEqual(len(shown),6)
            self.assertEqual(calls[0][0],"intro")
            self.assertNotEqual(calls[0][1],0) # demo suppressed
            self.assertEqual(u.reg_read(GPR[3]),0)
            self.assertEqual(u.reg_read(GPR[1]),STACK+0xF000)
            self.assertEqual(u.reg_read(GPR[30]),0x11223344)
            self.assertEqual(u.reg_read(GPR[31]),0x55667788)

    def test_title_start_is_blocked_until_language_confirmed(self):
        u,calls,shown=exercise(0,0,0x1000)
        self.assertEqual(calls[0][2]&0x1000,0)
        self.assertEqual(read16(u,CONTROLLER+0x12),0x1000)
        self.assertEqual(u.reg_read(GPR[3]),0)
        self.assertEqual(len(shown),6)

    def test_title_start_passthrough_after_confirmation(self):
        u,calls,shown=exercise(1,2,0x1000)
        self.assertTrue(calls[0][2]&0x1000)
        self.assertEqual(u.reg_read(GPR[3]),100)
        self.assertEqual(shown,[])
        self.assertEqual(read32(u,LANG_BASE+0x18),2)
        self.assertEqual(bytes(u.mem_read(LANG_BASE+0x80,8)),b"\xA5\xB6\xC7\xD8\xE9\xFA\xAB\xCD")

    def test_bl_target_is_title_only_intros_original(self):
        self.assertEqual(ORIGINAL_CALL_BE.hex(),"4bfff68d")
        before=bytearray(0x1060000)
        before[CALLSITE-BASE:CALLSITE-BASE+4]=ORIGINAL_CALL_BE
        before[0xCD128:0xCD12C]=bytes.fromhex("4bfc8321")
        before[0x1040000:0x1040008]=b"SM64LANG"
        before[0x10400C0:0x10400C8]=b"COURSE3\0"
        after,rep=install(bytes(before))
        self.assertEqual(rep["status"],"CANDIDATE_TITLE_ONLY_LANGUAGE_SELECTOR_NOT_HARDWARE_TESTED")
        self.assertEqual(after[0xCD128:0xCD12C],before[0xCD128:0xCD12C])
        self.assertEqual(after[0x1040080:0x1040088],bytes(8))
        self.assertEqual(after[0x1040000:0x1060000],before[0x1040000:0x1060000])
        for i,(old,new) in enumerate(zip(before,after)):
            if old!=new:
                self.assertTrue(
                  (CALLSITE-BASE<=i<CALLSITE-BASE+4) or
                  (0x3bc800<=i<0x3bc900) or
                  (0x3bc900<=i<0x3bcc00) or
                  (0x3bcc00<=i<0x3bcd00),
                  f"unexpected mutation {i:#x}"
                )

if __name__=="__main__":
    unittest.main()
