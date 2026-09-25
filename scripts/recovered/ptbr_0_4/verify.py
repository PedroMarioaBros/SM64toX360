"""Static integrity checks for the exact supplied Xbox 360 executable.
This is not an Xbox 360 emulator and does not prove successful console startup.
"""
from pathlib import Path
import hashlib,json,re,struct,subprocess,sys
from PIL import Image,ImageDraw
import analyze as a
ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'ptbr-work'
original=(ROOT/'inspect/base.bin').read_bytes()
b=(ROOT/'inspect/translated-base.bin').read_bytes()
xex=(ROOT/'sm64-ptbr-teste.xex').read_bytes()
report=json.loads((WORK/'patch-report.json').read_text())
fonts=json.loads((WORK/'font-map.json').read_text())
for ch,slot in fonts.items():a.cm[ch]=bytes([slot])
a.keys[:]=sorted(a.cm,key=len,reverse=True)
enc=a.encode
BASE=0x82000000
u32=lambda data,at:struct.unpack_from('>I',data,at)[0]
fontlut=struct.unpack_from('>256I',b,0x9df3b0)
menulut=struct.unpack_from('>256I',b,0x842de0)
widths=b[0x3c89b8:0x3c8ab8]
special={0xd0:widths[0x9e]*2,0xd1:sum(widths[a.cm[c][0]] for c in 'the'),0xd2:sum(widths[a.cm[c][0]] for c in 'you'),0xe0:14}
def width(text):return sum(special.get(v,widths[v]) for v in enc(text)[:-1])
def ptrvalid(addr,size):return 0x3c0000<=addr-BASE<=len(b)-size
# Independent parser/decryptor round-trip of the final XEX, not the intermediate.
r=subprocess.run([str(ROOT/'inspect/xextool/build/XexTool'),'-b',str(ROOT/'inspect/reopened-base.bin'),str(ROOT/'sm64-ptbr-teste.xex')],capture_output=True,text=True)
assert r.returncode==0,(r.stdout,r.stderr)
assert (ROOT/'inspect/reopened-base.bin').read_bytes()==b,'XEX readback differs'
assert len(b)==len(original)
# v0.4 changes control labels, retaining every original instruction exactly as
# in the user-tested v0.3 (including the existing text-address branches).
v03_code_sha256='5b828a2e35489d2ea0df44f27b93b4ff37fb7b247bde9a05e10c71f4c3317014'
assert hashlib.sha256(b[0x90000:0x3bc468]).hexdigest()==v03_code_sha256
assert b[0x165998:0x165c90]==original[0x165998:0x165c90]
assert hashlib.sha256((ROOT/'inspect/sm64.xex').read_bytes()).hexdigest()=='6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8', 'Wrong baseline XEX'
def xex_options(data):
 return {u32(data,24+i*8):u32(data,28+i*8) for i in range(u32(data,20))}
source_xex=(ROOT/'inspect/sm64.xex').read_bytes()
assert xex_options(xex)[0x10100]==xex_options(source_xex)[0x10100]==0x8239e3b8, 'Changed corrected-build entry point'
# Verify the entire backwards SHA-1 page chain and header digest directly.
assert xex[:4]==b'XEX2'
security=u32(xex,16);headers=u32(xex,8);count=u32(xex,security+0x180)
remaining=len(b);digest=bytes(20)
for i in range(count-1,-1,-1):
 at=security+0x184+i*24;descriptor=xex[at:at+24]
 assert descriptor[4:24]==digest,('section digest',i)
 size=(u32(xex,at)>>4)*0x10000;remaining-=size
 assert remaining>=0
 digest=hashlib.sha1(b[remaining:remaining+size]+descriptor).digest()
assert remaining==0
assert digest==xex[security+0x114:security+0x128],'image root hash'
assert hashlib.sha1(xex[security+0x17c:headers]+xex[:security+8]).digest()==xex[security+0x164:security+0x178],'header hash'
# All original dialogue records retain box metadata and resolve to PT-BR text.
dialogs=json.loads((WORK/'dialogs-layout.json').read_text())
assert len(dialogs)==170 and [r['id'] for r in dialogs]==list(range(170))
for row in dialogs:
 assert not re.search(r'\[(?:A|B|C|Z|R|L)\]',row['text']),('Legacy controller icon',row['id'])
max_width=0
for row in dialogs:
 i=row['id'];p=0x9e7cd0+i*16;data=enc(row['text'])
 assert b[p:p+8]==original[p:p+8] and b[p+12:p+16]==original[p+12:p+16],i
 ptr=u32(b,p+8)-BASE
 assert ptr==row['offset'] and b[ptr:ptr+len(data)]==data,i
 for line in row['text'].split('\n'):
  w=width(line);max_width=max(max_width,w)
  assert w<=125,(i,w,line)
 if '//' in row['text']:assert len(row['text'].split('\n'))%row['lines']==0,i
 for v in data[:-1]:
  if v not in (0x9e,0xd0,0xd1,0xd2,0xe0,0xfe):assert ptrvalid(fontlut[v],64),(i,hex(v))
for ch,slot in fonts.items():
 assert ptrvalid(fontlut[slot],64) and widths[slot]>0,ch
 assert original[0x9df3b0+slot*4:0x9df3b0+slot*4+4]==bytes(4),ch
 if ch.isupper():assert ptrvalid(menulut[slot],64),ch
for ch in 'JV':assert ptrvalid(u32(b,0x9df2c8+a.cm[ch][0]*4),512),ch
# textNew shares a compiler-generated base with the star and multiply icons.
# Preserve that base for existing saves; redirect only the empty-slot text.
assert b[0x1432c4:0x1432c8]==original[0x1432c4:0x1432c8]==bytes.fromhex('3babd0b8')
assert b[0x3cd0bc:0x3cd0be]==bytes.fromhex('35ff')
assert b[0x3cd0c0:0x3cd0c2]==bytes.fromhex('32ff')
assert b[0x778:0x77f]==b'APERTE\0' and b[0x780:0x786]==b'START\0'
assert b[0x1c98:0x1ca5]==b'APERTE START\0'
# Every native pointer to a course/mission label resolves to its translated text.
courses=json.loads((WORK/'courses-map.json').read_text());course_refs=0
for row in courses:
 data=enc(row['pt'])
 for old in row['offsets']:
  refs=[m.start() for m in re.finditer(re.escape(struct.pack('>I',BASE+old)),original) if m.start()%4==0 and (m.start()<0x90000 or m.start()>=0x3c0000)]
  assert refs,row
  for ref in refs:
   ptr=u32(b,ref)-BASE
   assert b[ptr:ptr+len(data)]==data,(row['pt'],ref)
   course_refs+=1
 for v in data[:-1]:
  if v!=0x9e:assert ptrvalid(menulut[v],64),(row['pt'],hex(v))
# Verify the generated PowerPC address hooks with a small instruction decoder.
def branch_target(pc,word):
 assert word>>26==18 and word&3==0,hex(word)
 d=word&0x03fffffc
 if d&0x02000000:d-=0x04000000
 return pc+d
sites=set()
for p in report['code_patches']:
 at=p['at'];cave=p['cave'];reg=p['reg'];sites.add(at)
 assert u32(original,at)==p['old']
 assert branch_target(at,u32(b,at))==cave
 w1,w2,w3=struct.unpack_from('>III',b,cave)
 assert w1>>26==15 and (w1>>16)&31==0 and (w1>>21)&31==reg
 assert w2>>26==24 and (w2>>21)&31==reg and (w2>>16)&31==reg
 address=((w1&65535)<<16)|(w2&65535)
 assert address==BASE+p['target'] and ptrvalid(address,1)
 assert branch_target(cave+8,w3)==at+4
camera=next(row for row in report['stack_ui'] if row['en']=='SET CAMERA ANGLE WITH R')
assert camera['pt']=='AJUSTE A CÂMERA COM RB'
for at in camera['refs']:
 target=next(row['target'] for row in report['code_patches'] if row['at']==at)
 assert b[target:target+len(enc(camera['pt']))]==enc(camera['pt'])
# Execute the dynamic suffix hook on a synthetic frame. Only r5 and suffix bytes
# may change; the file-slot letter must survive until the original code sets it.
p=report['dynamic_erased_message'];at=p['at'];sites.add(at)
assert u32(original,at)==p['old'] and branch_target(at,u32(b,at))==p['cave']
regs=[0x20000000+i*0x1234 for i in range(32)];regs[1]=0x100000
before_regs=regs.copy();frame=bytearray([0xa5]*512);original_frame=bytes(frame)
for pc in range(p['cave'],p['end']-4,4):
 w=u32(b,pc);op=w>>26;rt=(w>>21)&31;ra=(w>>16)&31;imm=w&65535
 if imm&0x8000:imm-=65536
 if op==14:regs[rt]=((regs[ra] if ra else 0)+imm)&0xffffffff
 elif op==38:
  dst=regs[ra]+imm-regs[1]
  assert p['stack']+7<=dst<p['stack']+7+len(enc(' APAGADO'))
  frame[dst]=regs[rt]&255
 else:raise AssertionError(('unexpected suffix instruction',hex(w)))
assert regs[5]==regs[1]+p['stack']
assert all(regs[i]==before_regs[i] for i in range(32) if i!=5)
suffix=enc(' APAGADO');start=p['stack']+7
assert frame[start:start+len(suffix)]==suffix
assert frame[:start]==original_frame[:start] and frame[start+len(suffix):]==original_frame[start+len(suffix):]
assert branch_target(p['end']-4,u32(b,p['end']-4))==at+4
# No change to the original instruction range outside the documented hooks.
for i in range(0x90000,0x3bc468,4):
 if b[i:i+4]!=original[i:i+4]:assert i in sites,hex(i)
pe=struct.unpack_from('<I',b,60)[0];section=pe+24+struct.unpack_from('<H',b,pe+20)[0]+2*40
assert struct.unpack_from('<I',b,section+8)[0]+0x90000==p['end']
assert p['end']<0x3c0000
# Retain a useful local preview rendered from the actual patched font data.
# It is a layout simulation, explicitly not a console screenshot.
def glyph(code,menu=False):
 lut=menulut if menu else fontlut;p=lut[code]-BASE
 if menu:
  raw=b[p:p+64];tile=Image.new('L',(8,8));tile.putdata([(v&15)*17 for v in raw]);return tile
 raw=b[p:p+64];vals=[]
 for v in raw:vals.extend((v>>4,v&15))
 tile=Image.new('L',(16,8));tile.putdata([int((v>>1)/7*255) if v&1 else 0 for v in vals]);return tile.transpose(Image.Transpose.TRANSVERSE)
def draw_encoded(canvas,text,x,y,menu=False):
 start=x
 for v in enc(text)[:-1]:
  if v==0xfe:x=start;y+=16;continue
  if v in (0xd0,0xe0,0x9e):x+=special.get(v,4 if menu else widths[v]);continue
  if v in (0xd1,0xd2):
   token='the' if v==0xd1 else 'you'
   for c in token:
    g=glyph(a.cm[c][0],menu);canvas.paste((245,246,249),(x,y),g);x+=widths[a.cm[c][0]]
   continue
  g=glyph(v,menu);canvas.paste((245,246,249),(x,y),g);x+=8 if menu else widths[v]
preview=Image.new('RGB',(640,760),(23,28,39));draw=ImageDraw.Draw(preview)
draw.text((16,10),'PREVIA DE FONTES E TEXTO - SIMULACAO, SEM EXECUCAO NO CONSOLE',fill='white')
for pos,i in enumerate([0,5,10,20,79,163]):
 row=dialogs[i];x=12+(pos%2)*314;y=44+(pos//2)*216
 draw.text((x+6,y),'Dialogo %03d / pagina de amostra'%i,fill=(164,184,214))
 panel=Image.new('RGB',(150,94),(7,10,16))
 lines=row['text'].split('\n');lines=lines[-row['lines']:] if i in (5,79) else lines[:row['lines']]
 draw_encoded(panel,'\n'.join(lines),8,0)
 preview.paste(panel.resize((300,188),Image.Resampling.NEAREST),(x,y+18))
draw_encoded(preview,' 2 FORTALEZA DO ESMAGÃO',18,702,True)
draw_encoded(preview,'TIRO PARA A ILHA NO CÉU',330,702,True)
draw_encoded(preview,'á à â ã é ê í ó ô õ ú ü ç',18,729)
draw_encoded(preview,'Á À Â Ã É Ê Í Ó Ô Õ Ú Ü Ç',330,729)
preview.save(WORK/'previa-textos.png')
# Show every page of the principal Xbox 360 tutorials using the actual font.
control_pages=[]
for i in [33,35,36,46,50,105,167]:
 row=dialogs[i];lines=row['text'].split('\n')
 for start in range(0,len(lines),row['lines']):
  control_pages.append((i,start//row['lines']+1,lines[start:start+row['lines']]))
controls_preview=Image.new('RGB',(948,38+((len(control_pages)+2)//3)*228),(23,28,39))
draw=ImageDraw.Draw(controls_preview)
draw.text((14,10),'CONTROLES XBOX 360 - SIMULACAO COM A FONTE DO JOGO, SEM CAPTURA DO CONSOLE',fill='white')
for pos,(i,page,lines) in enumerate(control_pages):
 x=12+(pos%3)*312;y=38+(pos//3)*228
 draw.text((x+6,y),'Dialogo %03d / pagina %d'%(i,page),fill=(164,184,214))
 panel=Image.new('RGB',(150,100),(7,10,16))
 draw_encoded(panel,'\n'.join(lines),8,0)
 controls_preview.paste(panel.resize((300,200),Image.Resampling.NEAREST),(x,y+18))
controls_preview.save(WORK/'previa-controles.png')
result={
 'status':'PASS - verificacao estatica do arquivo; teste completo no console pendente',
 'version':'0.4 - instrucoes adaptadas ao controle real do port para Xbox 360',
 'corrected_baseline_entry_point_preserved':'0x8239e3b8',
 'original_xex_sha256':hashlib.sha256((ROOT/'inspect/sm64.xex').read_bytes()).hexdigest(),
 'patched_xex_sha256':hashlib.sha256(xex).hexdigest(),
 'patched_xex_bytes':len(xex),'mapped_image_bytes':len(b),
 'xex_roundtrip_exact':True,'xex_page_hash_chain':True,'xex_header_hash':True,
 'dialogues_checked':len(dialogs),'dialogue_max_line_width':max_width,
 'course_and_mission_labels_checked':len(courses),'course_pointers_checked':course_refs,
 'main_font_accents_checked':len(fonts),'menu_font_accents_checked':13,
 'hud_letters_added':'JV','address_hooks_checked':len(report['code_patches']),
 'dynamic_erase_suffix_hook_checked':True,'other_original_instructions_unchanged':True,
 'existing_save_icon_base_preserved':True,'title_prompt':'APERTE START',
 'original_instruction_range_identical_to_v03':True,
 'original_instruction_range_sha256':v03_code_sha256,
 'input_routine_unchanged':True,'legacy_controller_tokens_in_dialogues':0,
 'camera_menu_prompt':camera['pt'],
 'unresolved_selected_patches':report['unresolved'],
 'limitations':['A versao 0.4 ainda nao foi executada em Xbox 360.','Os testes isolados de rotinas PowerPC estao documentados em regressao-menu.json e controles-verificados.json.','Os testes nao validam o visual completo, o salvamento real ou canhoes em execucao no console.','O usuario confirmou carregar progresso e salvar e sair repetidas vezes na versao 0.3.','Vozes e certas artes permanecem no idioma original.']}
(WORK/'verificacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
