from pathlib import Path
import sys,struct,json,math

from pregame_gate import GATE_VA
from unicorn import *
from unicorn import ppc_const as p
b=Path(sys.argv[1]).read_bytes();u=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN);u.mem_map(0x82000000,0x2000000);u.mem_write(0x82000000,b);u.mem_map(0x81000000,0x20000);u.mem_map(0x84000000,0x40000);u.reg_write(p.UC_PPC_REG_1,0x81010000);u.reg_write(p.UC_PPC_REG_3,0x82005848);u.reg_write(p.UC_PPC_REG_LR,0x84000000);u.reg_write(p.UC_PPC_REG_MSR,0x2000)
for a,v in [(0x82e47b80,0x84010000),(0x82e47b18,0x84030000),(0x82e47b14,0x84000040),(0x84000040,0x84020000),(0x84000044,0x10000),(0x84000048,0),(0x82e47b10,0x84010000),(0x82e47b3c,0x84000080)]:u.mem_write(a,struct.pack('>I',v))
state,selection,timer,buttons=map(int,sys.argv[2:6]);
u.mem_write(0x83040014,struct.pack('>III',state,selection,timer));u.mem_write(0x823c8990,struct.pack('>I',0x84000300));u.mem_write(0x84000312,struct.pack('>H',buttons));u.mem_write(0x8304001c,struct.pack('>I',timer));trace=[];count=[0];calls=[]
def h(u,a,s,d):
 count[0]+=1;trace.append(a)
 if a in (0x820ce780,0x82099498,0x820ce7b0,0x820fb8a0):calls.append(hex(a))
 if a==0x82095448:
  calls.append('original');u.reg_write(p.UC_PPC_REG_3,0x8200584c);u.reg_write(p.UC_PPC_REG_PC,u.reg_read(p.UC_PPC_REG_LR));return
 if len(trace)>20:trace.pop(0)
 if a in (0x823a7cb8,0x823a7c78):
  v=struct.unpack('>d',struct.pack('>Q',u.reg_read(p.UC_PPC_REG_FPR1)))[0]
  u.reg_write(p.UC_PPC_REG_FPR1,int.from_bytes(struct.pack('>d',float(math.floor(v) if a==0x823a7cb8 else math.ceil(v))),'big'));u.reg_write(p.UC_PPC_REG_PC,u.reg_read(p.UC_PPC_REG_LR));return
 w=int.from_bytes(u.mem_read(a,4),'big');op=w>>26;rt=(w>>21)&31;ra=(w>>16)&31;ds=w&0xfffc;ds=ds-0x10000 if ds&0x8000 else ds
 if op==31 and (w>>1)&1023==986:
  u.reg_write(p.UC_PPC_REG_0+ra,u.reg_read(p.UC_PPC_REG_0+rt));u.reg_write(p.UC_PPC_REG_PC,a+4);return
 if op==63 and (w>>1)&1023==846:
  fs=(w>>11)&31;v=u.reg_read(p.UC_PPC_REG_FPR0+fs);v=v-(1<<64) if v&(1<<63) else v
  u.reg_write(p.UC_PPC_REG_FPR0+rt,int.from_bytes(struct.pack('>d',float(v)),'big'));u.reg_write(p.UC_PPC_REG_PC,a+4);return
 if op in (58,62) and w&3==0:
  addr=(u.reg_read(p.UC_PPC_REG_0+ra)+ds)&0xffffffff
  if op==62:u.mem_write(addr,struct.pack('>Q',u.reg_read(p.UC_PPC_REG_0+rt)))
  else:u.reg_write(p.UC_PPC_REG_0+rt,int.from_bytes(u.mem_read(addr,8),'big')&0xffffffff)
  u.reg_write(p.UC_PPC_REG_PC,a+4)
u.hook_add(UC_HOOK_CODE,h)
u.emu_start(GATE_VA,0x84000000,count=100000)
assert u.reg_read(p.UC_PPC_REG_PC)==0x84000000
assert u.reg_read(p.UC_PPC_REG_1)==0x81010000
out_timer=int.from_bytes(u.mem_read(0x8304001c,4),'big')
out_state=int.from_bytes(u.mem_read(0x83040014,4),'big');out_selection=int.from_bytes(u.mem_read(0x83040018,4),'big')
assert ('original' in calls)==(state==2)
assert u.reg_read(p.UC_PPC_REG_3)==(0x8200584c if state==2 else 0x82005848)
if state==0:assert out_state==(1 if timer==44 or buttons&0x8000 else 0)
if state==1 and buttons==0x8000:
 assert out_state==2
 table=(0x83040100,0x830403b0,0x83040660)[selection]
 for i in range(170):assert u.mem_read(0x829e7cd8+i*16,4)==u.mem_read(table+i*4,4)
if state==1 and buttons==0x800:assert out_selection==(selection-1)%3
if state==1 and buttons==0x400:assert out_selection==(selection+1)%3
print(json.dumps({'status':'PASS','state_in':state,'state_out':out_state,'selection_in':selection,'selection_out':out_selection,'buttons':buttons,'timer_in':timer,'timer_out':out_timer,'instructions':count[0],'calls':calls,'scope':'actual rendering CPU code with synthetic pool/task, PPC64 instructions and floor/ceil modeled, original interpreter stubbed; no GPU/Xbox validation'}))
