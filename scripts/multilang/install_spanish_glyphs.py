#!/usr/bin/env python3
"""Instala os quatro glifos exclusivos do espanhol na imagem mapeada PT-BR v0.4.

Não contém bytes do jogo. Recebe:
  1) v0.4 mapped image;
  2) diretório do bundle espanhol (es/);
  3) patch-report.json recuperado da v0.4;
  4) saída mapped.

Os slots PT-BR existentes nunca são movidos.
"""
from pathlib import Path
from PIL import Image
import struct, json, hashlib, sys

BASE=0x82000000
FONT_LUT=0x9DF3B0
MENU_LUT=0x842DE0
WIDTH_POS=0x3C89B8
POOL_END=0x9E7CD0
SLOTS={'ñ':0x42,'Ñ':0x43,'¡':0x44,'¿':0x45}
BASE_CHAR={'ñ':'n','Ñ':'N','¡':'!','¿':'?'}
ASCII_IDX={chr(ord('A')+i):0x0A+i for i in range(26)}
ASCII_IDX.update({chr(ord('a')+i):0x24+i for i in range(26)})
ASCII_IDX.update({'!':0xF2,'?':0xF4})

def ia4(path):
    im=Image.open(path).convert('LA')
    if im.size != (16,8): raise RuntimeError(f"{path}: tamanho {im.size}")
    vals=[]
    for I,A in im.getdata():
        vals.append((round(I*7/255)<<1)|(1 if A>=128 else 0))
    return bytes((vals[i]<<4)|vals[i+1] for i in range(0,128,2))

def ia8(path):
    im=Image.open(path).convert('LA')
    if im.size != (8,8): raise RuntimeError(f"{path}: tamanho {im.size}")
    return bytes((round(I*15/255)<<4)|round(A*15/255) for I,A in im.getdata())

def main():
    if len(sys.argv)!=5:
        raise SystemExit("Uso: install_spanish_glyphs.py v04.mapped.bin bundle_es patch-report.json saida.mapped.bin")
    mapped,bundle,report_path,dst=map(Path,sys.argv[1:])
    data=bytearray(mapped.read_bytes()); before=bytes(data)
    if hashlib.sha256(before).hexdigest()!="6381bf1333bf1985474af00c139f33f9cdbad71a371c3231db0d861b72cfac2c":
        raise SystemExit("Base não é a imagem mapeada v0.4 canônica")

    old_report=json.loads(report_path.read_text(encoding="utf-8"))
    free=int(old_report["pool_free"])
    pool_start=POOL_END-free
    widths=bytearray(data[WIDTH_POS:WIDTH_POS+256])
    main=list(struct.unpack_from('>256I',data,FONT_LUT))
    menu=list(struct.unpack_from('>256I',data,MENU_LUT))
    for ch,slot in SLOTS.items():
        if main[slot] or menu[slot] or widths[slot]:
            raise RuntimeError(f"slot {slot:#x} ocupado para {ch}")

    cursor=pool_start; allocs=[]
    def alloc(raw,kind,ch):
        nonlocal cursor
        at=cursor
        if at+len(raw)>POOL_END: raise RuntimeError("pool esgotado")
        data[at:at+len(raw)]=raw
        cursor=(at+len(raw)+7)&~7
        allocs.append({"kind":kind,"char":ch,"offset":at,"va":BASE+at,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
        return at

    main_dir=bundle/"textures/segment2"
    mf={
      'ñ':'custom_font_graphics_n_accent.ia4.png',
      'Ñ':'custom_font_graphics_up_N_accent.ia4.png',
      '¡':'custom_font_graphics_exclamation_spanish.ia4.png',
      '¿':'custom_font_graphics_question_spanish.ia4.png'}
    for ch,slot in SLOTS.items():
        at=alloc(ia4(main_dir/mf[ch]),"main_font",ch)
        struct.pack_into('>I',data,FONT_LUT+slot*4,BASE+at)
        widths[slot]=widths[ASCII_IDX[BASE_CHAR[ch]]]

    menu_dir=bundle/"levels/menu"
    mm={
      'Ñ':'custom_main_menu_seg7_us_N_accent.ia8.png',
      '¡':'custom_main_menu_seg7_us_exclamation_spanish.ia8.png',
      '¿':'custom_main_menu_seg7_us_question_spanish.ia8.png'}
    for ch in ('Ñ','¡','¿'):
        slot=SLOTS[ch]; at=alloc(ia8(menu_dir/mm[ch]),"menu_font",ch)
        struct.pack_into('>I',data,MENU_LUT+slot*4,BASE+at)

    data[WIDTH_POS:WIDTH_POS+256]=widths
    allowed=[(pool_start,POOL_END),(WIDTH_POS,WIDTH_POS+256)]
    for slot in SLOTS.values():
        allowed += [(FONT_LUT+slot*4,FONT_LUT+slot*4+4),(MENU_LUT+slot*4,MENU_LUT+slot*4+4)]
    unexpected=[i for i,(a,b) in enumerate(zip(before,data)) if a!=b and not any(x<=i<y for x,y in allowed)]
    if unexpected: raise RuntimeError(f"alterações inesperadas: {unexpected[:20]}")

    dst.write_bytes(data)
    result={"source_sha256":hashlib.sha256(before).hexdigest(),"output_sha256":hashlib.sha256(data).hexdigest(),
      "pool_initial_free":free,"pool_used":cursor-pool_start,"pool_remaining":POOL_END-cursor,
      "slots":{k:hex(v) for k,v in SLOTS.items()},"widths":{k:widths[v] for k,v in SLOTS.items()},
      "allocations":allocs,"unexpected_changed_bytes":0}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
