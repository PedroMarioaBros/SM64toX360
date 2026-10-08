import zipfile,pathlib,json,sys
z=pathlib.Path(sys.argv[1]);f=zipfile.ZipFile(z);p=f.read(next(n for n in f.namelist() if n.endswith('.bps')))
def rd(i):
 v=0;s=1
 while 1:
  x=p[i];i+=1;v+=(x&127)*s
  if x&128:return v,i
  s*=128;v+=s
s,i=rd(4);t,i=rd(i);m,i=rd(i);i+=m;pos=so=to=0
matches=[]
while i<len(p)-12:
 a,i=rd(i);mode=a&3;n=(a>>2)+1;src=None
 if mode==0:src=pos
 elif mode==1:i+=n
 else:
  d,i=rd(i);delta=-(d>>1) if d&1 else d>>1
  if mode==2:so+=delta;src=so;so+=n
  else:to+=delta+n
 if src is not None:
  for loc in [0x57b720,0x593560]:
   if src<=loc<src+n:matches.append({'source':hex(loc),'target':hex(pos+loc-src),'copy_length':n})
 pos+=n

print(json.dumps({"audio_anchor_mappings":matches,"limits":"Source-copy provenance locates original audio anchors; it does not reconstruct missing source bytes or prove every modified bank layout."},indent=2))
