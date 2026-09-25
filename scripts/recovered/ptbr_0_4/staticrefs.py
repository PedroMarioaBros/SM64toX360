from analyze import *
refs={};regs={}
for pos in range(0x90000,0x3bc468,4):
 w=struct.unpack_from('>I',b,pos)[0];op=w>>26;rt=(w>>21)&31;ra=(w>>16)&31;imm=w&65535;si=imm if imm<32768 else imm-65536
 if op in (14,15):
  if ra==0:v=si<<(16 if op==15 else 0)
  elif ra in regs:v=regs[ra]+(si<<(16 if op==15 else 0))
  else:regs.pop(rt,None);continue
  regs[rt]=v&0xffffffff
  if op==14 and 0x82000000<=regs[rt]<0x82fb0000:refs.setdefault(regs[rt]-0x82000000,[]).append(pos)
 elif op==24:
  if rt in regs:
   regs[ra]=regs[rt]|imm
   if 0x82000000<=regs[ra]<0x82fb0000:refs.setdefault(regs[ra]-0x82000000,[]).append(pos)
  else:regs.pop(ra,None)
 elif op==31 and ((w>>1)&1023)==444:
  rb=(w>>11)&31
  if rt==rb and rt in regs:regs[ra]=regs[rt]
  else:regs.pop(ra,None)
 elif op in (14,15,32,33,34,35,40,41,42,43,46):regs.pop(rt,None)
 elif op in (16,18,19):regs={}
 elif op not in (10,11,24,36,37,38,39,44,45,47,48,49,50,51,52,53,54,55,63,59):regs.pop(rt,None);regs.pop(ra,None)
(ROOT/'ptbr-work/static-refs.json').write_text(json.dumps(refs))
for p in [0x3cd0b8,0x3cd0d0,0x3cd080,0x3cd180,0x3c8b2c,0x3c8ba0]:print(hex(p),[hex(x) for x in refs.get(p,[])])
