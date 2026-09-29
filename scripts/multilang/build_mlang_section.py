#!/usr/bin/env python3
"""Constrói a seção .mlang sobre a imagem mapeada PT-BR v0.4.

Entradas:
  v0.4 mapped PE/basefile;
  diretório com pools pt_br/es/en já validados;
  bundle espanhol contendo os quatro glifos extras.

Saída:
  PE/basefile ampliado com seção RW .mlang.

A seção armazena três tabelas DialogEntry e três pools de diálogo. Nenhuma
rotina de jogo é desviada neste estágio; o seletor/hook é uma etapa separada.
"""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json, struct

BASE=0x82000000
FONT_LUT=0x9DF3B0
MENU_LUT=0x842DE0
WIDTH_POS=0x3C89B8
OLD_POOL_END=0x9E7CD0
OLD_FREE=720
OLD_POOL_START=OLD_POOL_END-OLD_FREE
DIALOG_TABLE=0x9E7CD8
SECTION_RVA=0x1040000
SECTION_SIZE=0x40000
SECTION_END=SECTION_RVA+SECTION_SIZE
SLOTS={'ñ':0x42,'Ñ':0x43,'¡':0x44,'¿':0x45}
BASE_CHAR={'ñ':'n','Ñ':'N','¡':'!','¿':'?'}
ASCII_IDX={chr(ord('A')+i):0x0A+i for i in range(26)}
ASCII_IDX.update({chr(ord('a')+i):0x24+i for i in range(26)})
ASCII_IDX.update({'!':0xF2,'?':0xF4})

def ia4(path):
    im=Image.open(path).convert('LA')
    if im.size != (16,8): raise RuntimeError(f"{path}: {im.size}")
    vals=[]
    for I,A in im.getdata():
        vals.append((round(I*7/255)<<1)|(1 if A>=128 else 0))
    return bytes((vals[i]<<4)|vals[i+1] for i in range(0,128,2))

def ia8(path):
    im=Image.open(path).convert('LA')
    if im.size != (8,8): raise RuntimeError(f"{path}: {im.size}")
    return bytes((round(I*15/255)<<4)|round(A*15/255) for I,A in im.getdata())

def install_glyphs(data, es):
    widths=bytearray(data[WIDTH_POS:WIDTH_POS+256])
    main=list(struct.unpack_from('>256I',data,FONT_LUT))
    menu=list(struct.unpack_from('>256I',data,MENU_LUT))
    for ch,slot in SLOTS.items():
        if main[slot] or menu[slot] or widths[slot]:
            raise RuntimeError(f"slot {slot:#x} ocupado para {ch}")
    cursor=OLD_POOL_START
    allocations=[]
    def put(raw,kind,ch):
        nonlocal cursor
        at=cursor
        if at+len(raw)>OLD_POOL_END: raise RuntimeError("pool antigo esgotado")
        data[at:at+len(raw)]=raw
        cursor=(at+len(raw)+7)&~7
        allocations.append(dict(kind=kind,char=ch,offset=at,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        return at
    mf={'ñ':'custom_font_graphics_n_accent.ia4.png','Ñ':'custom_font_graphics_up_N_accent.ia4.png','¡':'custom_font_graphics_exclamation_spanish.ia4.png','¿':'custom_font_graphics_question_spanish.ia4.png'}
    for ch,slot in SLOTS.items():
        at=put(ia4(es/'textures/segment2'/mf[ch]),'main',ch)
        struct.pack_into('>I',data,FONT_LUT+slot*4,BASE+at)
        widths[slot]=widths[ASCII_IDX[BASE_CHAR[ch]]]
    mm={'Ñ':'custom_main_menu_seg7_us_N_accent.ia8.png','¡':'custom_main_menu_seg7_us_exclamation_spanish.ia8.png','¿':'custom_main_menu_seg7_us_question_spanish.ia8.png'}
    for ch in ('Ñ','¡','¿'):
        slot=SLOTS[ch]
        at=put(ia8(es/'levels/menu'/mm[ch]),'menu',ch)
        struct.pack_into('>I',data,MENU_LUT+slot*4,BASE+at)
    data[WIDTH_POS:WIDTH_POS+256]=widths
    return dict(used=cursor-OLD_POOL_START,remaining=OLD_POOL_END-cursor,slots={k:hex(v) for k,v in SLOTS.items()},widths={k:widths[v] for k,v in SLOTS.items()},allocations=allocations)

def add_section(data):
    pe=struct.unpack_from('<I',data,0x3c)[0]
    num=struct.unpack_from('<H',data,pe+6)[0]
    opt=struct.unpack_from('<H',data,pe+20)[0]
    sect=pe+24+opt
    headers=struct.unpack_from('<I',data,pe+24+60)[0]
    align=struct.unpack_from('<I',data,pe+24+32)[0]
    if num != 8 or align != 0x10000 or sect+(num+1)*40 > headers:
        raise RuntimeError("layout PE inesperado")
    if len(data)<SECTION_END: data.extend(b'\0'*(SECTION_END-len(data)))
    at=sect+num*40
    data[at:at+8]=b'.mlang\0\0'
    struct.pack_into('<IIIIIIHHI',data,at+8,SECTION_SIZE,SECTION_RVA,SECTION_SIZE,SECTION_RVA,0,0,0,0,0xC0000040)
    struct.pack_into('<H',data,pe+6,num+1)
    struct.pack_into('<I',data,pe+24+56,SECTION_END)
    return dict(header_offset=at,rva=hex(SECTION_RVA),size=SECTION_SIZE,end=hex(SECTION_END),characteristics='0xC0000040')

def make_record(ptr,unused,lines,left,width):
    # Layout real observado na compilação Xbox 360:
    # ptr, unused, lines, pad, left, width, pad2.
    return struct.pack('>IIBbhhH',ptr,unused,lines,0,left,width,0)

def write_mlang(data,pools_root):
    rows={l:json.loads((pools_root/l/'dialogs.json').read_text()) for l in ('pt_br','es','en')}
    pools={l:(pools_root/l/'dialogs.bin').read_bytes() for l in ('pt_br','es','en')}
    indexes={l:json.loads((pools_root/l/'dialog_index.json').read_text()) for l in ('pt_br','es','en')}
    cursor=0x100
    desc={}
    for lang in ('pt_br','es','en'):
        cursor=(cursor+15)&~15
        table_off=cursor;cursor+=170*16
        cursor=(cursor+15)&~15
        pool_off=cursor
        data[SECTION_RVA+pool_off:SECTION_RVA+pool_off+len(pools[lang])]=pools[lang]
        cursor+=len(pools[lang])
        desc[lang]=dict(table_off=table_off,pool_off=pool_off,pool_size=len(pools[lang]))
        for i,(row,ix) in enumerate(zip(rows[lang],indexes[lang])):
            ptr=BASE+SECTION_RVA+pool_off+ix['pool_offset']
            if lang in ('pt_br','en'):
                rec=bytearray(data[DIALOG_TABLE+i*16:DIALOG_TABLE+(i+1)*16])
                struct.pack_into('>I',rec,0,ptr)
                rec=bytes(rec)
            else:
                rec=make_record(ptr,1,row['lines'],row['left'],row['width'])
            start=SECTION_RVA+table_off+i*16
            data[start:start+16]=rec
    header=bytearray(0x100)
    header[0:8]=b'MLNG360\0'
    struct.pack_into('>IIII',header,8,1,3,0,0)
    codes={'pt_br':b'ptBR','es':b'esES','en':b'enUS'}
    for n,lang in enumerate(('pt_br','es','en')):
        off=0x20+n*0x20
        d=desc[lang]
        header[off:off+4]=codes[lang]
        struct.pack_into('>IIIIIII',header,off+4,
            BASE+SECTION_RVA+d['table_off'],
            BASE+SECTION_RVA+d['pool_off'],
            d['pool_size'],0,0,0,0)
    data[SECTION_RVA:SECTION_RVA+0x100]=header
    if cursor>SECTION_SIZE: raise RuntimeError("seção .mlang esgotada")
    return dict(magic='MLNG360',version=1,used_bytes=cursor,free_bytes=SECTION_SIZE-cursor,section_va=hex(BASE+SECTION_RVA),languages=desc)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mapped_v04',type=Path)
    ap.add_argument('pools_root',type=Path)
    ap.add_argument('spanish_bundle',type=Path)
    ap.add_argument('output',type=Path)
    ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    original=a.mapped_v04.read_bytes()
    if hashlib.sha256(original).hexdigest()!='6381bf1333bf1985474af00c139f33f9cdbad71a371c3231db0d861b72cfac2c':
        raise SystemExit('base mapped não é v0.4 canônica')
    data=bytearray(original)
    report=dict(source_sha256=hashlib.sha256(original).hexdigest(),source_bytes=len(original))
    report['glyphs']=install_glyphs(data,a.spanish_bundle)
    report['section']=add_section(data)
    report['mlang']=write_mlang(data,a.pools_root)
    report['output_sha256']=hashlib.sha256(data).hexdigest()
    report['output_bytes']=len(data)
    a.output.write_bytes(data)
    if a.report: a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
