#!/usr/bin/env python3
"""Bounded hardware diagnostic: 300 frames of language navigation preserving menu alpha, then original script.
Exercises actual init/render/end/alloc with ortho and known text visual probe; no language activation.
Keeps direct jump TEST3 patch; does not claim selector functionality.
"""
from pregame_gate import Asm,GATE_VA,INIT_RCP,RENDER_GAME,END_MASTER_DISPLAY_LIST,ALLOC_DISPLAY_LIST,ORIG_LEVEL_SCRIPT_EXECUTE,CREATE_DL_ORTHO,PRINT_GENERIC_STRING_FADE
import struct
def build():
 a=Asm(GATE_VA)
 a.mflr();a.emit(0x9421ff60);a.stw(0,0x98,1)
 a.emit(0xfbc10080);a.emit(0xfbe10088) # std r30/r31 (preserve full native registers)
 a.mr(31,3);a.lis(30,0x8304);a.lwz(10,0x1c,30);a.cmpwi(10,300);a.branch('original','beq')
 a.addi(10,10,1);a.stw(10,0x1c,30)
 a.call(INIT_RCP);a.call(RENDER_GAME)
 a.call(CREATE_DL_ORTHO)
 a.lis(11,0x82e5)
 a.emit(0x894b2f88);a.stw(10,0x70,1) # lbz r10,base alpha; save frame-local
 a.emit(0x894b2f8b);a.stw(10,0x74,1) # lbz r10,fade alpha
 a.li(10,255);a.stb(10,0x2f88,11);a.li(10,0);a.stb(10,0x2f8b,11)
 for x,y,off in [(76,195,0x58),(118,145,0x5c),(118,115,0x60),(118,85,0x64),(104,30,0x68)]:
  a.li(3,x);a.li(4,y);a.lwz(5,0x40,30);a.call(PRINT_GENERIC_STRING_FADE)
 a.lwz(10,0x18,30);a.li(3,96);a.cmpwi(10,0);a.branch('pt','beq');a.cmpwi(10,1);a.branch('es','beq');a.li(4,85);a.branch('marker')
 a.label('pt');a.li(4,145);a.branch('marker');a.label('es');a.li(4,115)
 a.label('marker');a.lwz(5,0x40,30);a.call(PRINT_GENERIC_STRING_FADE)
 # Normalized controller pointer; no language activation in this diagnostic.
 a.lis(11,0x823d);a.lwz(10,-0x7670,11);a.cmpwi(10,0);a.branch('restore','beq');a.lhz(9,0x12,10)
 a.andi(8,9,0x0800);a.cmpwi(8,0);a.branch('down','beq');a.lwz(10,0x18,30);a.cmpwi(10,0);a.branch('up_dec','bne');a.li(10,2);a.branch('store')
 a.label('up_dec');a.addi(10,10,-1);a.branch('store')
 a.label('down');a.andi(8,9,0x0400);a.cmpwi(8,0);a.branch('confirm','beq');a.lwz(10,0x18,30);a.cmpwi(10,2);a.branch('down_inc','bne');a.li(10,0);a.branch('store')
 a.label('down_inc');a.addi(10,10,1)
 a.label('store');a.stw(10,0x18,30);a.branch('restore')
 a.label('confirm');a.andi(8,9,0x8000);a.cmpwi(8,0);a.branch('restore','beq');a.li(10,300);a.stw(10,0x1c,30)
 a.label('restore')
 # Alpha is embedded in emitted display commands; restore globals each frame.
 a.lis(11,0x82e5);a.lwz(10,0x70,1);a.stb(10,0x2f88,11);a.lwz(10,0x74,1);a.stb(10,0x2f8b,11)
 a.call(END_MASTER_DISPLAY_LIST);a.li(3,0);a.call(ALLOC_DISPLAY_LIST)
 a.mr(3,31);a.branch('exit')
 a.label('original');a.mr(3,31);a.call(ORIG_LEVEL_SCRIPT_EXECUTE)
 a.label('exit');a.emit(0xebc10080);a.emit(0xebe10088);a.lwz(0,0x98,1);a.emit(0x382100a0);a.mtlr();a.blr()
 return a.resolve()
def install(image):
 b=bytearray(image);o=GATE_VA-0x82000000;code=build();assert not any(b[o:o+len(code)])
 assert b[0xcd128:0xcd12c].hex()=='4bfc8321'
 assert b[0x104001c:0x1040020]==bytes(4)
 b[o:o+len(code)]=code;b[0xcd128:0xcd12c]=struct.pack('>I',0x482ef7d9)
 return bytes(b)
