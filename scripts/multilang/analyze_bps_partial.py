import zipfile, pathlib, hashlib, json, struct, zlib, sys
z=pathlib.Path(sys.argv[1])
p=zipfile.ZipFile(z).read(next(n for n in zipfile.ZipFile(z).namelist() if n.endswith('.bps')))
def read(i):
 v=0;s=1
 while True:
  x=p[i];i+=1;v+=(x&127)*s
  if x&128:return v,i
  s*=128;v+=s
src,i=read(4);size,i=read(i);meta,i=read(i);i+=meta
out=bytearray(size);known=bytearray(size);pos=0;so=to=0;counts=[0]*4
while i<len(p)-12:
 a,i=read(i);mode=a&3;n=(a>>2)+1;counts[mode]+=1
 if mode==1:
  out[pos:pos+n]=p[i:i+n];known[pos:pos+n]=b'\1'*n;i+=n
 elif mode in (2,3):
  d,i=read(i);delta=-(d>>1) if d&1 else d>>1
  if mode==2:so+=delta;so+=n
  else:
   to+=delta
   for j in range(n):
    assert 0<=to<pos+j
    out[pos+j]=out[to];known[pos+j]=known[to];to+=1
 pos+=n
assert pos==size
ranges=[];start=None
for j,k in enumerate(known+b'\0'):
 if k and start is None:start=j
 elif not k and start is not None:
  if j-start>=4096:ranges.append({'start':hex(start),'end':hex(j),'bytes':j-start})
  start=None
r={'zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(p).hexdigest(),'patch_crc_valid':zlib.crc32(p[:-4])==struct.unpack('<I',p[-4:])[0],'source_size':src,'target_size':size,'source_crc32':hex(struct.unpack('<I',p[-12:-8])[0]),'target_crc32':hex(struct.unpack('<I',p[-8:-4])[0]),'actions':counts,'known_bytes_without_source':sum(known),'unknown_bytes':size-sum(known),'known_runs_over_4k':ranges,'limits':'Sparse bytes are not a playable ROM; no voice bank identified or decoded.'}
pathlib.Path('/tmp/bps_report.json').write_text(json.dumps(r,indent=2));pathlib.Path('/tmp/bps_sparse.bin').write_bytes(out);pathlib.Path('/tmp/bps_known.bin').write_bytes(known)
print(json.dumps(r,indent=2))

