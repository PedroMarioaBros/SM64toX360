from pathlib import Path
import struct,sys
b=Path('sm64corrigido.mapped.bin').read_bytes(); START,END=0x90000,0x3bc600; BASE=0x82000000

def u32(o):return struct.unpack_from('>I',b,o)[0]
def target(pc,w):
 d=w&0x03fffffc
 if d&0x02000000:d-=0x04000000
 if w&2:return d & 0xffffffff
 return (pc+d)&0xffffffff
wanted=[int(x,0) for x in sys.argv[1:]]
for wa in wanted:
 refs=[]
 for off in range(START,END,4):
  w=u32(off)
  if w>>26==18:
   pc=BASE+off
   t=target(pc,w)
   if t==wa:refs.append((pc,w&1))
 print(hex(wa),[(hex(pc),'bl' if lk else 'b') for pc,lk in refs])
