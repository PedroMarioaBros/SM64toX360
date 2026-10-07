#!/usr/bin/env python3
"""Execute new PPC hooks, real input mapper, and native set_mario_action.
Unicorn32 models PPC64 loads/stores and int-to-float instructions explicitly.
This is CPU validation, not Xbox or graphics validation.
"""
import sys,struct,json
from pathlib import Path
from unicorn import *
from unicorn import ppc_const as p
from direct_jumps import *
BASE=0x82000000;STOP=0x84000000;STACK=0x81010000;MARIO=0x84001000;CTRL=0x84002000
R=lambda n:p.UC_PPC_REG_0+n
F=lambda n:p.UC_PPC_REG_FPR0+n
b=install(Path('SM64toX360/_localization_build/layout-lang.pe').read_bytes())
def put(u,a,v,n=4):u.mem_write(a,v.to_bytes(n,'big'))
def get(u,a,n=4):return int.from_bytes(u.mem_read(a,n),'big')
def machine():
 u=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);u.mem_map(BASE,0x2000000);u.mem_write(BASE,b);u.mem_map(0x81000000,0x20000);u.mem_map(STOP,0x10000);u.reg_write(R(1),STACK);u.reg_write(p.UC_PPC_REG_MSR,0x2000)
 def cpu(u,a,size,data):
  w=get(u,a);op=w>>26;rt=(w>>21)&31;ra=(w>>16)&31;d=w&0xfffc;d=d-65536 if d&32768 else d
  if op in (58,62) and w&3==0:
   at=(u.reg_read(R(ra))+d)&0xffffffff
   if op==62:put(u,at,u.reg_read(R(rt)),8)
   else:u.reg_write(R(rt),get(u,at,8)&0xffffffff)
   u.reg_write(p.UC_PPC_REG_PC,a+4)
  elif op==31 and (w>>1)&1023==986:
   u.reg_write(R(ra),u.reg_read(R(rt)));u.reg_write(p.UC_PPC_REG_PC,a+4)
  elif op==63 and (w>>1)&1023==846:
   fs=(w>>11)&31;v=u.reg_read(F(fs));v=v-(1<<64) if v&(1<<63) else v
   u.reg_write(F(rt),int.from_bytes(struct.pack('>d',float(v)),'big'));u.reg_write(p.UC_PPC_REG_PC,a+4)
 u.hook_add(UC_HOOK_CODE,cpu);return u
def mapper_case(buttons,rx=0,ry=0,previous=0):
 u=machine();pad=CTRL
 u.reg_write(R(3),pad);put(u,BASE+0xf6ca24,1);put(u,0x82f9e364,previous,2)
 def external(u,a,size,data):
  if a==0x8239e010:
   u.mem_write(u.reg_read(R(4)),struct.pack('>IHBBhhhh',1,buttons,0,0,0,0,rx,ry));u.reg_write(R(3),0);u.reg_write(p.UC_PPC_REG_PC,u.reg_read(p.UC_PPC_REG_LR))
 u.hook_add(UC_HOOK_CODE,external);u.emu_start(0x821659ac,0x82165c78,count=10000)
 assert u.reg_read(p.UC_PPC_REG_PC)==0x82165c78
 assert get(u,BASE+0xf6ca24)==1,'Y changed shadows'
 # Real filter used between mapper and Controller buttonPressed computation.
 put(u,0x82e47bd0,pad);put(u,0x82e47c2c,0);u.reg_write(p.UC_PPC_REG_LR,STOP)
 u.emu_start(0x820ccbf8,STOP,count=1000)
 assert u.reg_read(p.UC_PPC_REG_PC)==STOP
 return get(u,pad,2),get(u,0x83040080),get(u,0x83040084)
def game_case(action,pressed=0,down=0,input_bits=0,held=0):
 u=machine();put(u,MARIO+0xc,action);put(u,MARIO+0x9c,CTRL);put(u,MARIO+2,input_bits,2);put(u,MARIO+0x7c,held)
 put(u,MARIO+0x68,0x84003000);put(u,0x83040084,pressed);put(u,0x83040080,down)
 u.reg_write(R(11),MARIO);u.reg_write(p.UC_PPC_REG_LR,STOP)
 # Execute native set_mario_action + airborne setup, not a stub.
 u.emu_start(GAME_CAVE,STOP,count=20000)
 assert u.reg_read(p.UC_PPC_REG_PC)==STOP
 assert u.reg_read(R(1))==STACK and u.reg_read(R(11))==MARIO
 assert u.reg_read(R(10))==get(u,MARIO+0xc)
 return get(u,MARIO+0xc),get(u,MARIO+2,2),struct.unpack('>f',u.mem_read(MARIO+0x4c,4))[0]
checks=[]
for physical,expected in [(0,0),(0x1000,0x8000),(0x4000,0x4000),(0x2000,0),(0x8000,0),(0xa000,0),(1,0x800),(0x9000,0x8000)]:
 assert mapper_case(physical)[0]==expected,(hex(physical),mapper_case(physical));checks.append('mapper '+hex(physical))
for ground in (0x0c400201,0x04000440,0x0c000231,0x04000470):
 for bit,expected in [(0x2000,DOUBLE),(0x8000,TRIPLE),(0xa000,TRIPLE)]:
  out=game_case(ground,bit,bit);assert out[0]==expected,(hex(ground),out);assert out[2]>0;checks.append({'ground':hex(ground),'button':hex(bit),'action':hex(out[0]),'vertical_velocity':out[2]})
 assert game_case(ground)[0]==ground,'A/default changed'
for blocked in (0x03000880,0x03000881,0x01000882,0x380022c0,0x0c000227,0x00001904):
 assert game_case(blocked,0x2000,0x2000)[0]==blocked;checks.append('blocked '+hex(blocked))
for flags in (4,0x10,0x40,0x200,0x400):assert game_case(0x0c400201,0x2000,0x2000,flags)[0]==0x0c400201
assert game_case(0x0c400201,0x2000,0x2000,held=1)[0]==0x0c400201
assert game_case(DOUBLE,down=0x2000)[1]&0x80
assert not game_case(DOUBLE,down=0)[1]&0x80
# All right-stick directions/diagonals preserve camera bits and produce no shortcuts.
for rx in (-32768,0,32767):
 for ry in (-32768,0,32767):
  camera=(2 if rx < -16000 else 1 if rx > 16000 else 0)|(8 if ry > 16000 else 4 if ry < -16000 else 0)
  out=mapper_case(0,rx,ry);assert out==(camera,0,0),(rx,ry,out)
  for button in (0x2000,0x8000):
   out=mapper_case(button,rx,ry);assert out==(camera,button,button)
   held=mapper_case(button,rx,ry,button);assert held==(camera,button,0)
  checks.append({'camera_rx':rx,'camera_ry':ry,'camera_bits':camera,'no_shortcut':True})
for camera in (1,2,4,8,15):
 assert game_case(0x0c400201,pressed=camera,down=camera)[0]==0x0c400201
report={'status':'PASS','hardware_verified':False,'checks':checks,'scope':'actual mapper and native action setup; graphics not exercised'}
print(json.dumps(report,indent=2))
