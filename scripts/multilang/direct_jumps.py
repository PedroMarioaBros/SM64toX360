#!/usr/bin/env python3
"""Generate direct grounded double/triple jump shortcuts, leaving Xbox A unchanged.
Physical Xbox B/Y down/pressed live in .lang+0x80/+0x84; camera bits remain original.
"""
from pregame_gate import Asm
import struct
MAPPER_CAVE=0x823BD600
GAME_CAVE=0x823BD000
MAPPER_HOOK=0x82165A50
GAME_HOOK=0x820DF4B0
SET_ACTION=0x820DE350
DOUBLE=0x03000881
TRIPLE=0x01000882
GROUND_IDS=(1,0x40,0x42,0x43,0x44,0x45,0x30,0x31,0x3a,0x70,0x72,0x78)
def ori(a,rt,rs,imm):a.emit(0x60000000|(rs<<21)|(rt<<16)|imm)
def sth(a,rs,d,ra):a.emit(0xb0000000|(rs<<21)|(ra<<16)|(d&65535))
def jump(a,target):a.emit(0x48000000|((target-a.pc())&0x03fffffc))
def mapper():
 a=Asm(MAPPER_CAVE)
 # Physical shortcuts are stored outside the original camera/controller bits.
 # r8 is previous XInput state; r6 is current. Preserve r10/r7 for the original tail.
 a.lis(11,0x8304)
 a.andi(9,6,0xa000);a.stw(9,0x80,11)
 a.emit(0x7c000078|(6<<21)|(9<<16)|(8<<11)) # andc r9,r6,r8
 a.andi(9,9,0xa000);a.stw(9,0x84,11)
 jump(a,0x82165A7C)
 return a.resolve()
def gameplay():
 a=Asm(GAME_CAVE)
 a.mflr();a.emit(0x9421ff80);a.stw(0,0x78,1);a.stw(11,0x70,1)
 a.lwz(8,0x9c,11);a.cmpwi(8,0);a.branch('exit','beq')
 # Hold B sustains the native double-jump height, without faking A in menus.
 a.lis(9,0x8304);a.lwz(9,0x80,9);a.andi(9,9,0x2000);a.cmpwi(9,0);a.branch('press','beq')
 a.lwz(10,0xc,11);a.lis(9,0x300);ori(a,9,9,0x881)
 a.emit(0x7c000000|(10<<16)|(9<<11));a.branch('press','bne') # cmpw r10,r9
 a.lhz(9,2,11);ori(a,9,9,0x80);sth(a,9,2,11)
 a.label('press');a.lis(9,0x8304);a.lwz(9,0x84,9);a.andi(9,9,0xa000);a.cmpwi(9,0);a.branch('exit','beq')
 a.lhz(10,2,11);a.andi(10,10,0x654);a.cmpwi(10,0);a.branch('exit','bne') # off floor/first person/squished/water/stomp
 a.lwz(10,0x7c,11);a.cmpwi(10,0);a.branch('exit','bne') # holding object
 a.lwz(10,0xc,11);a.andi(10,10,0x1ff)
 for ident in GROUND_IDS:a.cmpwi(10,ident);a.branch('launch','beq')
 a.branch('exit')
 a.label('launch');a.andi(10,9,0x8000);a.cmpwi(10,0);a.branch('double','beq')
 a.lis(4,0x100);ori(a,4,4,0x882);a.branch('call')
 a.label('double');a.lhz(10,2,11);ori(a,10,10,0x80);sth(a,10,2,11)
 a.lis(4,0x300);ori(a,4,4,0x881)
 a.label('call');a.mr(3,11);a.li(5,0);a.call(SET_ACTION)
 a.label('exit');a.lwz(11,0x70,1);a.lwz(10,0xc,11) # replay replaced lwz
 a.lwz(0,0x78,1);a.emit(0x38210080);a.mtlr();a.blr()
 return a.resolve()
def install(image):
 b=bytearray(image)
 for address,raw in [(MAPPER_CAVE,mapper()),(GAME_CAVE,gameplay())]:
  off=address-0x82000000
  assert not any(b[off:off+len(raw)]),'cave not empty'
  b[off:off+len(raw)]=raw
 for address,expected,target,link in [(MAPPER_HOOK,'54cb0420',MAPPER_CAVE,0),(GAME_HOOK,'814b000c',GAME_CAVE,1)]:
  off=address-0x82000000
  assert b[off:off+4].hex()==expected,(hex(address),b[off:off+4].hex())
  b[off:off+4]=struct.pack('>I',0x48000000|((target-address)&0x3fffffc)|link)
 return bytes(b)
