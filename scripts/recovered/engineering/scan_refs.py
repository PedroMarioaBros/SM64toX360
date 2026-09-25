from pathlib import Path
import struct
B=Path('sm64corrigido.mapped.bin').read_bytes(); BASE=0x82000000
START,END=0x90000,0x3bc600

def u32(o): return struct.unpack_from('>I',B,o)[0]

def refs(addr):
 hi=(addr>>16)&0xffff; lo=addr&0xffff; out=[]
 for o in range(START,END-20,4):
  w=u32(o); op=w>>26; rt=(w>>21)&31; ra=(w>>16)&31
  if op!=15 or ra!=0 or (w&0xffff)!=hi: continue
  for d in range(1,7):
   p=o+4*d; x=u32(p); xop=x>>26
   if xop==14: # addi rD,rA,imm
    xd=(x>>21)&31; xa=(x>>16)&31; imm=x&0xffff
    simm=imm-0x10000 if imm&0x8000 else imm
    val=((hi<<16)+simm)&0xffffffff
    if xa==rt and val==addr: out.append((o,p,'addi',rt,xd))
   elif xop==24: # ori rA,rS,uimm
    xs=(x>>21)&31; xa=(x>>16)&31; imm=x&0xffff
    val=(hi<<16)|imm
    if xs==rt and xa==rt and val==addr: out.append((o,p,'ori',rt,rt))
 return out
for off,label in [(0x5848,'sm64config'),(0x5a90,'bad_mtx'),(0x5b88,'frame log'),(0x5e6c,'dump path'),(0x5f14,'frame dump header'),(0x6051,'frame dump footer')]:
 a=BASE+off
 print(label,hex(a),refs(a))
