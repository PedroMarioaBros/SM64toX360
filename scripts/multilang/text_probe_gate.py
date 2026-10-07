#!/usr/bin/env python3
"""Bounded hardware diagnostic: 90 frames with one text, then original script.
Exercises actual init/render/end/alloc with ortho and one existing encoded text; no language activation.
Keeps direct jump TEST3 patch; does not claim selector functionality.
"""
from pregame_gate import Asm,GATE_VA,INIT_RCP,RENDER_GAME,END_MASTER_DISPLAY_LIST,ALLOC_DISPLAY_LIST,ORIG_LEVEL_SCRIPT_EXECUTE,CREATE_DL_ORTHO,PRINT_GENERIC_STRING_FADE
import struct
def build():
 a=Asm(GATE_VA)
 a.mflr();a.emit(0x9421ff60);a.stw(0,0x98,1)
 a.emit(0xfbc10080);a.emit(0xfbe10088) # std r30/r31 (preserve full native registers)
 a.mr(31,3);a.lis(30,0x8304);a.lwz(10,0x1c,30);a.cmpwi(10,90);a.branch('original','beq')
 a.addi(10,10,1);a.stw(10,0x1c,30)
 a.call(INIT_RCP);a.call(RENDER_GAME)
 a.call(CREATE_DL_ORTHO)
 a.lis(11,0x82e5);a.li(10,255);a.stb(10,0x2f88,11);a.li(10,0);a.stb(10,0x2f8b,11)
 a.li(3,92);a.li(4,150);a.lwz(5,0x40,30);a.call(PRINT_GENERIC_STRING_FADE)
 a.call(END_MASTER_DISPLAY_LIST);a.li(3,0);a.call(ALLOC_DISPLAY_LIST)
 a.mr(3,31);a.branch('exit')
 a.label('original');a.lis(11,0x82e5);a.li(10,0);a.stb(10,0x2f88,11);a.stb(10,0x2f8b,11);a.mr(3,31);a.call(ORIG_LEVEL_SCRIPT_EXECUTE)
 a.label('exit');a.emit(0xebc10080);a.emit(0xebe10088);a.lwz(0,0x98,1);a.emit(0x382100a0);a.mtlr();a.blr()
 return a.resolve()
def install(image):
 b=bytearray(image);o=GATE_VA-0x82000000;code=build();assert not any(b[o:o+len(code)])
 assert b[0xcd128:0xcd12c].hex()=='4bfc8321'
 assert b[0x104001c:0x1040020]==bytes(4)
 b[o:o+len(code)]=code;b[0xcd128:0xcd12c]=struct.pack('>I',0x482ef7d9)
 return bytes(b)
