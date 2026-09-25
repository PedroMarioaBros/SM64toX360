from analyze import *
import unicodedata,hashlib
from PIL import Image,ImageDraw
original=b
assert hashlib.sha256(b).hexdigest()=='75f653c7383b8cbbd218449bbd7ea45c787b7bf62db3d9e312356517834a91c7', 'Use the mapped image from sm64corrigido.xex'
out=bytearray(b)
widths=bytearray((ROOT/'ptbr-work/widths.bin').read_bytes());width_pos=b.find(widths)
font_pos=0x9df3b0
lut=list(struct.unpack_from('>256I',b,font_pos))
# Add single-byte Portuguese accented letters to previously unused font slots.
accents='áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ'
slots=list(range(0x60,0x6f))+list(range(0x70,0x80))
for char,slot in zip(accents,slots):
 assert lut[slot]==0 and widths[slot]==0
 cm[char]=bytes([slot]);widths[slot]=widths[cm[unicodedata.normalize('NFD',char)[0]][0]]
keys[:]=sorted(cm,key=len,reverse=True)
def text_width(s):
 special={0xd0:widths[0x9e]*2,0xd1:sum(widths[cm[c][0]] for c in 'the'),0xd2:sum(widths[cm[c][0]] for c in 'you'),0xe0:14}
 return sum(special.get(v,widths[v]) for v in encode(s)[:-1])
def wrap(s,limit=125):
 lines=[]
 for para in s.split('\n'):
  if para.startswith('//') or not para:lines.append(para);continue
  line=''
  for word in para.split():
   if line and text_width(line+' '+word)>limit:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  lines.append(line)
 return '\n'.join(lines)
translations={int(l.split('|',1)[0]):l.split('|',1)[1].replace('\\n','\n') for l in (ROOT/'ptbr-work/dialogs-pt.txt').read_text().splitlines() if l.strip()}
assert set(translations)==set(range(170))
start=dialogs[0]['offset'];end=0x9e7cd0;cursor=start
records=[]
for d in dialogs:
 text=wrap(translations[d['id']])
 # Keep the answer row in the last row of a dialogue page.
 if '//' in text:
  ls=text.split('\n');assert ls[-1].startswith('//')
  while len(ls)%d['lines']!=0:ls.insert(-1,'')
  text='\n'.join(ls)
 enc=encode(text)
 assert cursor+len(enc)<end
 out[cursor:cursor+len(enc)]=enc
 ptr=0x9e7cd8+d['id']*16
 assert struct.unpack_from('>I',b,ptr)[0]==0x82000000+d['offset']
 struct.pack_into('>I',out,ptr,0x82000000+cursor)
 records.append(dict(id=d['id'],offset=cursor,length=len(enc),text=text,lines=d['lines']))
 cursor=(cursor+len(enc)+7)&~7
text_end=cursor
# The remaining original dialogue storage belongs to our translated string pool.
# No code or BSS space is borrowed.
preview=Image.new('RGB',(26*32,80),(35,40,48));draw=ImageDraw.Draw(preview)
for i,(ch,slot) in enumerate(zip(accents,slots)):
 base,mark=unicodedata.normalize('NFD',ch)
 ptr=lut[cm[base][0]]-0x82000000
 raw=b[ptr:ptr+64]
 vals=[]
 for v in raw:vals.extend([v>>4,v&15])
 packed=Image.new('L',(16,8));packed.putdata(vals)
 canonical=packed.transpose(Image.Transpose.TRANSVERSE)
 pix=list(canonical.getdata())
 im=Image.new('L',(8,16));im.putdata([255 if v&1 else 0 for v in pix])
 # Find the top ink row. Preserve base glyph and put accents in spare top rows.
 bbox=im.getbbox();top=bbox[1]
 if mark=='\u0327':
  y=min(bbox[3],13);coords=[(3,y),(3,y+1),(2,y+2)]
 elif mark=='\u0301':coords=[(4,max(0,top-3)),(3,max(1,top-2))]
 elif mark=='\u0300':coords=[(2,max(0,top-3)),(3,max(1,top-2))]
 elif mark=='\u0302':coords=[(3,max(0,top-3)),(2,max(1,top-2)),(4,max(1,top-2))]
 elif mark=='\u0303':coords=[(2,max(0,top-3)),(3,max(0,top-3)),(4,max(1,top-2)),(5,max(1,top-2))]
 elif mark=='\u0308':coords=[(2,max(1,top-2)),(4,max(1,top-2))]
 else:raise ValueError(mark)
 for x,y in coords:pix[y*8+x]=15
 canonical.putdata(pix)
 vals=list(canonical.transpose(Image.Transpose.TRANSVERSE).getdata())
 raw2=bytes((vals[j]<<4)|vals[j+1] for j in range(0,128,2))
 assert cursor+64<=end
 out[cursor:cursor+64]=raw2
 struct.pack_into('>I',out,font_pos+slot*4,0x82000000+cursor)
 im.putdata([int((v>>1)/7*255) if v&1 else 0 for v in pix]);preview.paste(im.convert('RGB').resize((32,64),Image.Resampling.NEAREST),(i*32,0))
 draw.text((i*32,66),ch,fill='white')
 cursor+=64
out[width_pos:width_pos+256]=widths
print('Dialogues:',len(records),'text bytes:',text_end-start,'font bytes:',cursor-text_end,'pool remaining:',end-cursor)
preview.save(ROOT/'ptbr-work/font-preview.png')
(ROOT/'ptbr-work/dialogs-layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(ROOT/'inspect/translated-base.bin').write_bytes(out)
(ROOT/'ptbr-work/font-map.json').write_text(json.dumps({ch:slot for ch,slot in zip(accents,slots)},ensure_ascii=False))
# More text is placed after custom glyphs in the recovered original dialogue pool.
static_refs={int(k):v for k,v in json.loads((ROOT/'ptbr-work/static-refs.json').read_text()).items()}
code_cursor=0x3bc600
assert out[code_cursor:0x3c0000]==bytes(0x3c0000-code_cursor)
patches=[]
def allocate(data):
 global cursor
 at=cursor;assert at+len(data)<=end
 out[at:at+len(data)]=data;cursor=(at+len(data)+7)&~7
 return at
def redirect(at,target):
 global code_cursor
 w=struct.unpack_from('>I',b,at)[0];op=w>>26
 assert op in (14,24),hex(at)
 reg=(w>>21)&31 if op==14 else (w>>16)&31
 address=0x82000000+target
 code=struct.pack('>III',0x3c000000|(reg<<21)|(address>>16),0x60000000|(reg<<21)|(reg<<16)|(address&65535),0x48000000|((at+4-(code_cursor+8))&0x03fffffc))
 assert code_cursor+12<0x3c0000
 out[code_cursor:code_cursor+12]=code
 struct.pack_into('>I',out,at,0x48000000|((code_cursor-at)&0x03fffffc))
 patches.append(dict(at=at,cave=code_cursor,target=target,reg=reg,old=w))
 code_cursor+=12
# All course strings are referenced through native address tables.
course_rows=json.loads((ROOT/'ptbr-work/courses-map.json').read_text())
for row in course_rows:
 enc=encode(row['pt']);new=allocate(enc)
 for old in row['offsets']:
  needle=struct.pack('>I',0x82000000+old)
  refs=[m.start() for m in re.finditer(re.escape(needle),b) if m.start()%4==0 and (m.start()<0x90000 or m.start()>=0x3c0000)]
  assert refs,(row['en'],hex(old))
  for p in refs:struct.pack_into('>I',out,p,0x82000000+new)
# Static UI strings are matched only in the two verified UI/ending ranges.
ui=json.loads((ROOT/'ptbr-work/ui-pt.json').read_text());ui['SCORE']='PTS.';ui['SURE?']='CERTO';ui['NO EMPTY FILE']='SEM VAGA'
covered=[];static_done=[];unresolved=[]
for s,t in sorted(ui.items(),key=lambda it:len(it[0]),reverse=True):
 variants=[encode(s),b''.join(cm[c] for c in s)+b'\xff' if all(c in cm for c in s) else b'']
 poss=sorted(set(m.start() for en in variants if en for m in re.finditer(re.escape(en),b) if 0x3cd054<=m.start()<0x3cd184 or 0x3c8ad0<=m.start()<0x3c8bb7))
 for p in poss:
  if any(a<=p<z for a,z in covered):continue
  oldlen=b.index(b'\xff',p)-p+1;enc=encode(t)
  # Add exactly identified zero alignment bytes when necessary, never cross another object.
  avail=oldlen
  while (p+avail)%4 and b[p+avail]==0:avail+=1
  if len(enc)<=avail:
   out[p:p+len(enc)]=enc
   static_done.append(dict(en=s,pt=t,offset=p))
  elif static_refs.get(p):
   target=allocate(enc)
   refs=static_refs[p]
   protected=[]
   if p==0x3cd0b8:
    # r29 at 0x1432c4 is a common base for starIcon (+4) and xIcon (+8)
    # in the existing-save path. It must NOT be moved with textNew. Only
    # r6 at 0x143348 is the direct textNew argument in the empty-save path.
    assert s=='NEW' and refs==[0x1432c4,0x143348]
    assert struct.unpack_from('>I',b,0x1432c4)[0]==0x3babd0b8
    assert struct.unpack_from('>I',b,0x1432cc)[0]==0x38dd0004
    assert struct.unpack_from('>I',b,0x1432ec)[0]==0x38dd0008
    protected=[0x1432c4]
    refs=[0x143348]
   for at in refs:redirect(at,target)
   static_done.append(dict(en=s,pt=t,offset=p,redirect=True,refs=refs,protected_base_refs=protected))
  else:unresolved.append(dict(en=s,offset=p,reason='length'))
  covered.append((p,p+oldlen))
# Stack arrays are immutable. Redirect the pointer-producing addi only.
# Original register values, CR, LR, stack initializers and game logic remain intact.
stacks=json.loads((ROOT/'ptbr-work/stack-map.json').read_text());stack_done=[]
for s,rows in stacks.items():
 for row in rows:
  if not row['refs']:continue
  if ui[s]==s:continue
  target=allocate(encode(ui[s]))
  for at in row['refs']:redirect(at,target)
  stack_done.append(dict(en=s,pt=ui[s],refs=row['refs']))
# Declare the newly used part of the existing executable page in PE VirtualSize.
pe=struct.unpack_from('<I',b,60)[0];sect=pe+24+struct.unpack_from('<H',b,pe+20)[0]
assert b[sect+2*40:sect+2*40+5]==b'.text'
struct.pack_into('<I',out,sect+2*40+8,code_cursor-0x90000)
# ASCII renderer (title prompt and role labels in credits); retain all staff names.
ascii_map={'NO CONTROLLER':'SEM CONTROLE','PRESS':'APERTE','SELECT STAGE':'VER FASE','PRESS START BUTTON':'APERTE START','GAME DIRECTOR':'DIRETOR','ASSISTANT DIRECTORS':'DIRETORES ADJUNTOS','SYSTEM PROGRAMMERS':'SISTEMA','PROGRAMMERS':'PROGRAMACAO','CAMERA PROGRAMMER':'PROGRAMA DA CAMERA','MARIO FACE PROGRAMMER':'ROSTO DO MARIO','COURSE DIRECTORS':'DIRECAO DE FASES','COURSE DESIGNERS':'DESIGN DE FASES','SOUND COMPOSER':'COMPOSICAO','SOUND EFFECTS':'EFEITOS DE SOM','SOUND PROGRAMMER':'PROGRAMA DE SOM','3-D ANIMATORS':'ANIMACAO 3-D','ADDITIONAL GRAPHICS':'GRAFICOS ADICIONAIS','TECHNICAL SUPPORT':'SUPORTE TECNICO','PROJECT STAFF':'EQUIPE','PROGRESS MANAGEMENT':'GESTAO DO PROJETO','SCREEN TEXT WRITER':'TEXTOS DO JOGO','TRANSLATION':'TRADUCAO','MARIO VOICE':'VOZ MARIO','PEACH VOICE':'VOZ PEACH','SPECIAL THANKS TO':'AGRADECIMENTOS','EAD STAFF':'EQUIPE EAD','ALL NINTENDO PERSONNEL':'EQUIPE NINTENDO','MARIO CLUB STAFF':'EQUIPE MARIO CLUB','PRODUCER':'PRODUTOR','EXECUTIVE PRODUCER':'PRODUTOR EXECUTIVO'}
ascii_done=[]
for s,t in ascii_map.items():
 for m in re.finditer(re.escape(s.encode()+b'\0'),b[:0x1cac]):
  p=m.start();en=s.encode()+b'\0';new=t.encode()+b'\0'
  avail=len(en)
  while p+avail<len(b) and b[p+avail]==0 and p+avail<((p+len(en)+3)&~3):avail+=1
  if len(new)<=avail:out[p:p+len(new)]=new;ascii_done.append(s)
  else:unresolved.append(dict(en=s,offset=p,reason='ASCII length'))
assert cursor<=end
print('Courses:',len(course_rows),'static UI:',len(static_done),'stack UI:',len(stack_done),'ASCII:',len(ascii_done),'trampolines:',len(patches),'pool free:',end-cursor)
print('Unresolved',unresolved)
(ROOT/'inspect/translated-base.bin').write_bytes(out)
(ROOT/'ptbr-work/patch-report.json').write_text(json.dumps(dict(static_ui=static_done,stack_ui=stack_done,ascii=ascii_done,unresolved=unresolved,code_patches=patches,pool_free=end-cursor),ensure_ascii=False,indent=2))
# Add missing J and V to the original color HUD font using the existing menu
# letter silhouettes; the US font table deliberately left these entries null.
menu_lut_pos=0x842de0;menu_lut=list(struct.unpack_from('>256I',b,menu_lut_pos))
hud_lut_pos=0x9df2c8
for ch in 'JV':
 idx=cm[ch][0];assert struct.unpack_from('>I',b,hud_lut_pos+idx*4)[0]==0
 ptr=menu_lut[idx]-0x82000000
 small=Image.new('L',(8,8));small.putdata([v&15 for v in b[ptr:ptr+64]])
 large=small.resize((14,14),Image.Resampling.NEAREST)
 tile=Image.new('L',(16,16));tile.paste(large,(1,1));rgba=[]
 for y in range(16):
  for x in range(16):
   a=tile.getpixel((x,y));v=0
   if a:
    # Familiar saturated red/gold lettering with a modest vertical gradient.
    red=31;green=max(4,27-y);blue=2
    v=(red<<11)|(green<<6)|(blue<<1)|1
   rgba.append(v)
 raw=struct.pack('>256H',*rgba);ptr_new=allocate(raw)
 struct.pack_into('>I',out,hud_lut_pos+idx*4,0x82000000+ptr_new)
# Native 8x8 menu font receives uppercase accents used by course titles.
for ch in accents:
 if not ch.isupper():continue
 idx=cm[ch][0];assert menu_lut[idx]==0
 base,mark=unicodedata.normalize('NFD',ch);p=menu_lut[cm[base][0]]-0x82000000
 tile=Image.new('L',(8,8));tile.putdata(b[p:p+64])
 ink=Image.new('L',(8,8));ink.putdata([v&15 for v in b[p:p+64]])
 box=ink.getbbox()
 # Reserve the top two rows for the accent; keep a 5-pixel capital below.
 face=tile.crop(box).resize((box[2]-box[0],5),Image.Resampling.NEAREST)
 final=Image.new('L',(8,8));final.paste(face,(box[0],3))
 if mark=='\u0301':coords=[(4,0),(3,1)]
 elif mark=='\u0300':coords=[(2,0),(3,1)]
 elif mark=='\u0302':coords=[(3,0),(2,1),(4,1)]
 elif mark=='\u0303':coords=[(2,0),(3,0),(4,1),(5,1)]
 elif mark=='\u0308':coords=[(2,1),(4,1)]
 elif mark=='\u0327':
  final=Image.new('L',(8,8));final.paste(face,(box[0],1));coords=[(3,6),(2,7)]
 else:raise ValueError(mark)
 for x,y in coords:final.putpixel((x,y),255)
 ptr_new=allocate(bytes(final.getdata()));struct.pack_into('>I',out,menu_lut_pos+idx*4,0x82000000+ptr_new)
(ROOT/'inspect/translated-base.bin').write_bytes(out)
report=json.loads((ROOT/'ptbr-work/patch-report.json').read_text());report.update(pool_free=end-cursor,added_hud_letters='JV',added_menu_accents=[c for c in accents if c.isupper()]);(ROOT/'ptbr-work/patch-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Final free pool',end-cursor)
# The erased-file message changes its A/B/C/D letter at runtime. Translate the
# suffix in the original local array, preserving that mutable character.
at=0x1445dc;w=struct.unpack_from('>I',b,at)[0];assert w==0x38a10090
reg=5;sp=0x90;suffix=encode(' APAGADO');assert len(suffix)<=13
cave_start=code_cursor
# The suffix begins at an unaligned byte address. Byte stores avoid PowerPC
# alignment exceptions and leave the dynamically selected file letter intact.
for j,value in enumerate(suffix):
 words=[0x38000000|(reg<<21)|value,0x98000000|(reg<<21)|(1<<16)|(sp+7+j)]
 out[code_cursor:code_cursor+8]=struct.pack('>II',*words);code_cursor+=8
out[code_cursor:code_cursor+8]=struct.pack('>II',w,0x48000000|((at+4-(code_cursor+4))&0x03fffffc));code_cursor+=8
struct.pack_into('>I',out,at,0x48000000|((cave_start-at)&0x03fffffc))
struct.pack_into('<I',out,sect+2*40+8,code_cursor-0x90000)
report['dynamic_erased_message']=dict(at=at,cave=cave_start,end=code_cursor,stack=sp,text='MARIO ? APAGADO',old=w)
(ROOT/'ptbr-work/patch-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(ROOT/'inspect/translated-base.bin').write_bytes(out)
