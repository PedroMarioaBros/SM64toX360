from analyze import *
# Recover byte array initializers emitted as li/lis/ori + stack stores.
# Keep source instruction metadata for each known byte.
regs={};mem={};found={};function_start=0x90000;ui=json.loads((ROOT/'ptbr-work/ui-pt.json').read_text())
patterns={s:encode(s) for s in ui}
# __ strings use single characters, including separate closing/opening parentheses.
patterns.update({s:b''.join(cm[c] for c in s)+b'\xff' for s in ui if s.startswith('(NORMAL)')})
def search():
 if not mem:return
 for text,pat in patterns.items():
  for addr in mem:
   if mem[addr][0]!=pat[0]:continue
   if all(addr+j in mem and mem[addr+j][0]==v for j,v in enumerate(pat)):
    seq=[mem[addr+j][1] for j in range(len(pat))]
    refs=[]
    for at in range(function_start,pos+4,4):
     ins=struct.unpack_from('>I',b,at)[0]
     if ins>>26==14 and (ins>>16)&31==1 and ins&65535==addr:refs.append(at)
    key=tuple(seq)
    found.setdefault(text,{})[key]=dict(stack=addr,sources=seq,refs=refs,function_start=function_start,function_end=pos+4)
for pos in range(0x90000,0x3bc468,4):
 w=struct.unpack_from('>I',b,pos)[0];op=w>>26;rt=(w>>21)&31;ra=(w>>16)&31;imm=w&65535
 if op==37 and rt==ra==1:search();regs={};mem={};function_start=pos
 if op==14 and ra==0:
  v=imm if imm<32768 else imm-65536
  regs[rt]=[(v>>s&255,(pos,s) if s<16 else None) for s in (24,16,8,0)]
 elif op==15 and ra==0:
  regs[rt]=[(imm>>8,(pos,8)),(imm&255,(pos,0)),(0,None),(0,None)]
 elif op==24:
  if rt in regs:
   rr=regs[rt]
   if rr[2][0]==rr[3][0]==0:regs[ra]=rr[:2]+[(imm>>8,(pos,8)),(imm&255,(pos,0))]
   else:regs.pop(ra,None)
  else:regs.pop(ra,None)
 elif op in (36,38,44) and ra==1:
  size={36:4,38:1,44:2}[op];a=imm if imm<32768 else imm-65536
  if rt in regs:
   for j,v in enumerate(regs[rt][-size:]):mem[a+j]=v
  else:
   for j in range(size):mem.pop(a+j,None)
 elif op==31 and ((w>>1)&1023)==444:
  rb=(w>>11)&31
  if rt==rb and rt in regs:regs[ra]=regs[rt]
  else:regs.pop(ra,None)
 elif op in (14,15,32,33,34,35,40,41,42,43,46):regs.pop(rt,None)
 elif op==19 and ((w>>1)&1023)==16:search();regs={};mem={}
 # Other instructions invalidate target conservatively when not stores/branches/compares.
 elif op not in (14,15,16,18,19,24,36,37,38,39,44,45,47,48,49,50,51,52,53,54,55,10,11,63,59):
  regs.pop(rt,None);regs.pop(ra,None)
search()
rows={k:list(v.values()) for k,v in found.items()}
print({k:len(v) for k,v in rows.items()})
(ROOT/'ptbr-work/stack-map.json').write_text(json.dumps(rows,indent=2))
