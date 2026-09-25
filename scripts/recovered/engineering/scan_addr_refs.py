from pathlib import Path
import struct,sys
B=Path('sm64corrigido.mapped.bin').read_bytes(); START,END=0x90000,0x3bc600

def u32(o): return struct.unpack_from('>I',B,o)[0]
def scan(addr):
 out=[]
 hi_add=((addr+0x8000)>>16)&0xffff
 hi_ori=(addr>>16)&0xffff
 lo=addr&0xffff
 for o in range(START,END-4,4):
  w=u32(o);op=w>>26;rd=(w>>21)&31;ra=(w>>16)&31
  if op!=15 or ra!=0:continue
  imm=w&0xffff
  for d in range(1,9):
   p=o+4*d;x=u32(p);xop=x>>26
   if xop==14:
    rt=(x>>21)&31; xa=(x>>16)&31; simm=x&0xffff; simm=simm-0x10000 if simm&0x8000 else simm
    val=((imm<<16)+simm)&0xffffffff
    if xa==rd and val==addr: out.append((o,p,'addi',rd,rt))
   elif xop==24:
    rs=(x>>21)&31; xa=(x>>16)&31
    val=((imm<<16)|(x&0xffff))&0xffffffff
    if rs==rd and xa==rd and val==addr: out.append((o,p,'ori',rd,rd))
 return out
for s in sys.argv[1:]:
 a=int(s,0);print(hex(a),[(hex(o),hex(p),k,r,t) for o,p,k,r,t in scan(a)])
