import struct,re,json
from capstone import *
b=open('/workspace/scratch/3c8b50e99b92/SM64toX360/_localization_build/direct-jumps3.pe','rb').read(); pe=struct.unpack_from('<I',b,60)[0]; base=struct.unpack_from('<I',b,pe+52)[0]; n=struct.unpack_from('<H',b,pe+6)[0]; os=struct.unpack_from('<H',b,pe+20)[0]; st=pe+24+os
for i in range(n):
 o=st+40*i; name=b[o:o+8].rstrip(b'\0')
 if name==b'.text': tr,raw,rs=struct.unpack_from('<III',b,o+12); break
for i in range(n):
 o=st+40*i; name=b[o:o+8].rstrip(b'\0')
 if name==b'.pdata': praw,psz=struct.unpack_from('<II',b,o+20); break
text=b[raw:raw+rs]; tva=base+tr
md=Cs(CS_ARCH_PPC,CS_MODE_32|CS_MODE_BIG_ENDIAN)
rows=[]
for off in range(0,psz,16):
 start,_,end,_=struct.unpack_from('>IIII',b,praw+off)
 if not (tva<=start<tva+len(text)) or end<=start: continue
 ins=list(md.disasm(text[start-tva:end-tva],start)); ss='\n'.join(f'{x.mnemonic} {x.op_str}' for x in ins)
 # require direct m->wall and action fields from same r3, plus a branch/call
 wall=('0x60(r3)' in ss or '0x60(r30)' in ss or '0x60(r31)' in ss)
 action=('0x18(r3)' in ss or '0x1c(r3)' in ss or '0x18(r30)' in ss or '0x1c(r30)' in ss or '0x18(r31)' in ss or '0x1c(r31)' in ss)
 pos=('0x3c(r3)' in ss or '0x3c(r30)' in ss or '0x3c(r31)' in ss)
 calls=sum(1 for x in ins if x.mnemonic in ('bl','bctrl'))
 if wall and action and pos and calls>=2:
  rows.append({'start':hex(start),'end':hex(end),'ins':len(ins),'calls':calls})
print(json.dumps({'status':'PASS','candidate_count':len(rows),'candidates':rows},indent=2))

