from pathlib import Path
import re,ast,subprocess,json,struct
ROOT=Path(__file__).resolve().parent.parent
src=ROOT/'referencia/sm64'
if not src.exists():src=ROOT/'inspect/sm64-source'
b=(ROOT/'inspect/base.bin').read_bytes()
cm={}
for line in (src/'charmap.txt').read_text().splitlines():
 m=re.match(r"('(?:\\.|[^'])*')\s*=\s*(.*)",line)
 if m:
  try:cm[ast.literal_eval(m[1])]=bytes(int(x,16) for x in m[2].split(','))
  except:pass
cm['\n']=b'\xfe';cm['\\n']=b'\xfe'
keys=sorted(cm,key=len,reverse=True)
def encode(s):
 o=b''
 while s:
  for k in keys:
   if s.startswith(k):o+=cm[k];s=s[len(k):];break
  else:raise ValueError(s[:20])
 return o+b'\xff'
def cpp(path):return subprocess.check_output(['cpp','-P','-DVERSION_US','-D_(x)=x',str(path)],text=True)
s=cpp(src/'text/us/dialogs.h');dialogs=[]
for m in re.finditer(r'DEFINE_DIALOG\(DIALOG_(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*((?:"(?:\\.|[^"\\])*"\s*)+)\)',s):
 st=''.join(ast.literal_eval(t) for t in re.findall(r'"(?:\\.|[^"\\])*"',m[6]));e=encode(st);pos=b.find(e)
 dialogs.append(dict(id=int(m[1]),lines=int(m[3]),text=st,offset=pos,size=len(e)))
if __name__=='__main__':
 print('dialogs',len(dialogs),'found',sum(d['offset']>=0 for d in dialogs));print('not found',[(d['id'],d['text'][:50]) for d in dialogs if d['offset']<0])
 (ROOT/'ptbr-work/dialogs-en.json').write_text(json.dumps(dialogs,ensure_ascii=False,indent=2))
 (ROOT/'ptbr-work/dialogs-en.txt').write_text('\n\n'.join(f"{d['id']:03} [{d['size']} bytes/{d['lines']} lines] " +d['text'].replace('\n',' ') for d in dialogs))
 # locate native pointer table to fonts by strides
 for i in range(0,len(b)-1024,4):
  x=struct.unpack_from('>I',b,i)[0]
  if not 0x823c0000<x<0x82fa0000:continue
  vals=struct.unpack_from('>64I',b,i)
  if len(set(vals))==64 and all(v==x+j*64 for j,v in enumerate(vals)) and b[i+256:i+320]==bytes(64):print('FONT LUT',hex(i),hex(x),'stride64')
