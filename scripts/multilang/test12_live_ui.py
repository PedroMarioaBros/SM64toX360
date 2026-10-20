#!/usr/bin/env python3
"""Build a fail-closed TEST12 patch from the exact mapped TEST11 PE."""
from __future__ import annotations
import hashlib, struct
from test9_selector_native import PPC, BASE, PE_LEN, WRAPPER, CAVE, LANG_BASE, LANG_RVA, LANG_CAPACITY, CURSOR_OFF, INDEX_OFF, STATE_OFF, ACTIVATE_DIALOGS, ACTIVATE_COURSES, CONTROLLER_GLOBAL, ORIGINAL_PRINT, PRINT_CENTER, CALLSITE

SOURCE_SHA='a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd'
WRAPPER_SHA='7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1'
MENU_HELPER=0x823BCB00
MENU_HELPER_CAP=0x100
PREVIEW_SLOTS=(0x58,0x5C,0x60,0x64,0x68)

# Use the native glyph-map renderer for selector labels so accents are supported.
# The cursor and Start prompt retain the safe ASCII color-font renderer.
PREVIEW={
  # Visible order is top-to-bottom: English, Spanish, Portuguese.
  0:['Idiomas','Inglês','Espanhol','Português','Pressione A para confirmar','APERTE','START'],
  1:['Idiomas','Inglés','Español','Portugués','Pulsa A para confirmar','PULSA','START'],
  2:['Languages','English','Spanish','Portuguese','Press A to confirm','PRESS','START'],
}
# Offset, capacity in bytes including 0xFF terminator, PT-BR, Spanish, English.
MENU_ITEMS=[
 (0x3CD050,12,'VOLTAR','VOLVER','BACK'),
 (0x3CD05C,12,'VER PONTOS','VER PUNTOS','VIEW POINTS'),
 (0x3CD068,12,'DUPLICAR','DUPLICAR','COPY'),
 (0x3CD074,7,'APAGAR','BORRAR','ERASE'),
 (0x3CD080,8,'ESTÉREO','ESTÉREO','STEREO'),
 (0x3CD088,5,'MONO','MONO','MONO'),
 (0x3CD090,6,'FONES','FONOS','AUDIO'),
 (0x3CD0C4,12,'ABRIR JOGO','ABRIR JUEGO','OPEN FILE'),
 (0x3CD0D0,8,'PTS.','PTS.','PTS.'),
 (0x3CD0D8,8,'COPIAR','COPIAR','COPY'),
 (0x3CD0E0,8,'APAGAR','BORRAR','ERASE'),
 (0x3CD0E8,9,'VER JOGO','VER','VIEW'),
 (0x3CD0F4,17,'SEM DADOS SALVOS','SIN DATOS','NO SAVE DATA'),
 (0x3CD10C,12,'DUPLICAR','DUPLICAR','COPY'),
 (0x3CD118,20,'COPIAR PARA ONDE?','COPIAR A DONDE?','COPY TO WHERE?'),
 (0x3CD12C,24,'SEM DADOS SALVOS','SIN DATOS','NO SAVE DATA'),
 (0x3CD144,20,'CÓPIA CONCLUÍDA','COPIA COMPLETA','COPY COMPLETE'),
 (0x3CD158,20,'HÁ DADOS SALVOS','HAY DATOS GUARDADOS','SAVE DATA EXISTS'),
 (0x3CD16C,9,'SEM VAGA','SIN ESP.','NO SPACE'),
 (0x3CD175,7,'ARQ.','FICH','FILE'),
 (0x3CD17C,4,'NÃO','NO','NO'),
]
ACC={'Á':0x6D,'Ã':0x71,'Â':0x70,'Ç':0x7A,'É':0x72,'Ê':0x73,'Í':0x74,
     'Ó':0x75,'Ô':0x76,'Õ':0x77,'Ú':0x78,'Ü':0x79,'Ñ':0x43,
     '.':0x3F,'?':0xF4,'!':0xF2,'-':0x9F}

def enc_menu(s:str)->bytes:
    out=[]
    for ch in s.upper():
        if ch==' ':out.append(0x9E)
        elif 'A'<=ch<='Z':out.append(ord(ch)-ord('A')+0x0A)
        elif ch in ACC:out.append(ACC[ch])
        else:raise ValueError(f'unsupported menu glyph {ch!r} in {s!r}')
    return bytes(out+[0xFF])

def enc_selector_title(s:str)->bytes:
    special={'ê':0x65,'é':0x64,'ñ':0x42,'Ê':0x41,'É':0x40,'Ñ':0x43,
             'á':0x60,'í':0x66,'ó':0x67,'ú':0x6A,'Á':0x6D,'Í':0x66,
             'Ó':0x75,'Ú':0x78}
    out=[]
    for ch in s:
        if 'A'<=ch<='Z':out.append(ord(ch)-ord('A')+0x0A)
        elif 'a'<=ch<='z':out.append(ord(ch)-ord('a')+0x24)
        elif ch==' ':out.append(0x9E)
        elif ch in special:out.append(special[ch])
        else:raise ValueError(f'unsupported title glyph {ch!r} in {s!r}')
    return bytes(out+[0xFF])

def append_blob(out,cursor,blob):
    cursor=(cursor+3)&~3
    if cursor+len(blob)>LANG_CAPACITY:raise ValueError('.lang overflow')
    off=LANG_RVA+cursor
    out[off:off+len(blob)]=blob
    return BASE+off,cursor+len(blob)

def build_wrapper():
    p=PPC()
    p.w(0x7c0802a6);p.w(0x9421ff80);p.stw(0,0x78,1)
    p.lis(11,LANG_BASE>>16);p.lwz(10,STATE_OFF,11);p.cmpwi(10,0);p.branch('pass_original','bne')
    p.lis(11,(CONTROLLER_GLOBAL+0x8000)>>16);p.lwz(11,CONTROLLER_GLOBAL&0xffff,11);p.cmpwi(11,0);p.branch('draw','beq')
    p.lhz(9,0x12,11);p.andi(8,9,~0x1000&0xffff);p.sth(8,0x12,11)
    p.andi(8,9,0x0800);p.cmpwi(8,0);p.branch('down','beq')
    p.lis(11,LANG_BASE>>16);p.lwz(10,INDEX_OFF,11);p.cmpwi(10,2);p.branch('up_increment','bne');p.li(10,0);p.branch('write_index')
    p.label('up_increment');p.addi(10,10,1);p.branch('write_index')
    p.label('down');p.andi(8,9,0x0400);p.cmpwi(8,0);p.branch('check_A','beq')
    p.lis(11,LANG_BASE>>16);p.lwz(10,INDEX_OFF,11);p.cmpwi(10,0);p.branch('down_decrement','bne');p.li(10,2);p.branch('write_index')
    p.label('down_decrement');p.addi(10,10,-1)
    p.label('write_index');p.stw(10,INDEX_OFF,11);p.branch('draw')
    p.label('check_A');p.andi(8,9,0x8000);p.cmpwi(8,0);p.branch('draw','beq')
    p.lis(11,LANG_BASE>>16);p.lwz(3,INDEX_OFF,11);p.call(ACTIVATE_DIALOGS)
    p.lis(11,LANG_BASE>>16);p.lwz(3,INDEX_OFF,11);p.call(ACTIVATE_COURSES)
    p.lis(11,LANG_BASE>>16);p.lwz(3,INDEX_OFF,11);p.call(MENU_HELPER)
    p.lis(11,LANG_BASE>>16);p.li(10,1);p.stw(10,STATE_OFF,11);p.branch('pass_original')
    p.label('draw')
    # Resolve the row from header pointers; .lang+0x80..0x87 stays untouched.
    p.lis(12,LANG_BASE>>16);p.lwz(10,INDEX_OFF,12);p.cmpwi(10,0);p.branch('preview_pt','beq');p.cmpwi(10,1);p.branch('preview_es','beq')
    p.lwz(11,0x78,12);p.branch('preview_load')
    p.label('preview_pt');p.lwz(11,0x70,12);p.branch('preview_load')
    p.label('preview_es');p.lwz(11,0x74,12)
    p.label('preview_load')
    for i,slot in enumerate(PREVIEW_SLOTS):
        p.lwz(10,i*4,11);p.stw(10,slot,12)
    for x,y,slot in ((76,195,0x58),(118,145,0x5C),(118,115,0x60),(118,85,0x64),(104,30,0x68)):
        p.lis(12,LANG_BASE>>16);p.li(3,x);p.li(4,y);p.lwz(5,slot,12);p.call(0x82143110)
    p.lis(11,LANG_BASE>>16);p.lwz(10,INDEX_OFF,11);p.cmpwi(10,0);p.branch('marker_pt','beq');p.cmpwi(10,1);p.branch('marker_es','beq');p.li(4,145);p.branch('marker')
    p.label('marker_pt');p.li(4,85);p.branch('marker');p.label('marker_es');p.li(4,115)
    p.label('marker');p.li(3,14);p.lis(5,0x8305);p.ori(5,5,0xCA30);p.call(PRINT_CENTER);p.branch('epilogue')
    p.label('pass_original')
    # Preserve native no-controller behavior; ES/EN use localized prompt strings.
    p.lis(12,LANG_BASE>>16);p.lwz(10,INDEX_OFF,12);p.cmpwi(10,0);p.branch('original_prompt','beq')
    p.lis(11,(CONTROLLER_GLOBAL+0x8000)>>16);p.lwz(11,CONTROLLER_GLOBAL&0xffff,11);p.cmpwi(11,0);p.branch('original_prompt','beq')
    p.lis(12,LANG_BASE>>16);p.lwz(10,INDEX_OFF,12);p.cmpwi(10,1);p.branch('prompt_es','beq');p.lwz(11,0x78,12);p.branch('prompt_load')
    p.label('prompt_es');p.lwz(11,0x74,12)
    p.label('prompt_load');p.stw(11,0x60,1)
    p.li(3,60);p.li(4,38);p.lwz(5,20,11);p.call(PRINT_CENTER)
    p.lwz(11,0x60,1);p.li(3,60);p.li(4,20);p.lwz(5,24,11);p.call(PRINT_CENTER);p.branch('epilogue')
    p.label('original_prompt');p.call(ORIGINAL_PRINT)
    p.label('epilogue');p.lwz(0,0x78,1);p.w(0x38210080);p.w(0x7c0803a6);p.w(0x4e800020)
    code=p.resolve()
    if len(code)>CAVE:raise ValueError(f'wrapper {len(code)} > {CAVE}')
    return code

def build_menu_helper():
    p=PPC(base=MENU_HELPER)
    p.lis(12,LANG_BASE>>16);p.lwz(10,INDEX_OFF,12);p.cmpwi(10,0);p.branch('menu_pt','beq');p.cmpwi(10,1);p.branch('menu_es','beq')
    p.lwz(11,0xA8,12);p.branch('menu_loop')
    p.label('menu_pt');p.lwz(11,0xA0,12);p.branch('menu_loop')
    p.label('menu_es');p.lwz(11,0xA4,12)
    p.label('menu_loop');p.li(10,len(MENU_ITEMS))
    p.label('entry');p.lwz(7,0,11);p.lwz(8,4,11)
    p.label('copy_byte');p.w(0x88C80000) # lbz r6,0(r8)
    p.cmpwi(6,0xFF);p.branch('copy_done','beq')
    p.w(0x98C70000) # stb r6,0(r7)
    p.addi(7,7,1);p.addi(8,8,1);p.branch('copy_byte')
    p.label('copy_done');p.w(0x98C70000);p.addi(11,11,12);p.addi(10,10,-1);p.cmpwi(10,0);p.branch('entry','bne');p.w(0x4E800020)
    code=p.resolve()
    if len(code)>MENU_HELPER_CAP:raise ValueError(f'menu helper {len(code)} > {MENU_HELPER_CAP}')
    return code

def patch_test11(pe:bytes,strict=True):
    if len(pe)!=PE_LEN or (strict and hashlib.sha256(pe).hexdigest()!=SOURCE_SHA):raise ValueError('requires exact TEST11 mapped PE')
    def chk(off,expected):
        if pe[off:off+len(expected)]!=expected:raise ValueError(f'unexpected bytes at {off:#x}: {pe[off:off+len(expected)].hex()}')
    chk(0x1040000,b'SM64LANG');chk(0x1472D4,bytes.fromhex('48275a2d'));chk(0xCD128,bytes.fromhex('4bfc8321'))
    chk(0x1040014,bytes(8));chk(0x1040080,bytes(8))
    if hashlib.sha256(pe[WRAPPER-BASE:WRAPPER-BASE+384]).hexdigest()!=WRAPPER_SHA:raise ValueError('TEST11 wrapper fingerprint mismatch')
    if any(pe[WRAPPER-BASE+384:WRAPPER-BASE+CAVE]):raise ValueError('wrapper cave tail is not free')
    if any(pe[MENU_HELPER-BASE:MENU_HELPER-BASE+MENU_HELPER_CAP]):raise ValueError('menu helper cave is not free')
    cur=struct.unpack_from('>I',pe,LANG_RVA+CURSOR_OFF)[0]
    if cur!=0x1CA32:raise ValueError(f'unexpected TEST11 cursor {cur:#x}')
    if any(pe[LANG_RVA+cur:LANG_RVA+LANG_CAPACITY]):raise ValueError('TEST11 .lang tail is not zero')
    out=bytearray(pe);cursor=cur;rows={}
    for lang_id,texts in PREVIEW.items():
        ptrs=[]
        for i,text in enumerate(texts):
            # First five are native glyph-map strings (0xFF terminator);
            # final two are ASCII for the title color-font Start prompt (NUL).
            raw=enc_selector_title(text) if i<5 else text.encode('ascii')+b'\0'
            va,cursor=append_blob(out,cursor,raw);ptrs.append(va)
        cursor=(cursor+3)&~3
        if cursor+len(ptrs)*4>LANG_CAPACITY:raise ValueError('.lang overflow in preview table')
        table_off=LANG_RVA+cursor
        for i,va in enumerate(ptrs):struct.pack_into('>I',out,table_off+i*4,va)
        row_va=BASE+table_off;cursor+=len(ptrs)*4
        struct.pack_into('>I',out,LANG_RVA+0x70+lang_id*4,row_va);rows[lang_id]=ptrs
    menu_rows={}
    for lang_id in (0,1,2):
        records=[]
        for off,cap,pt,es,en in MENU_ITEMS:
            raw=enc_menu((pt,es,en)[lang_id])
            if len(raw)>cap:raise ValueError(f'{(pt,es,en)[lang_id]!r} exceeds buffer at {off:#x}: {len(raw)}>{cap}')
            src,cursor=append_blob(out,cursor,raw);records.append((BASE+off,src,cap))
        cursor=(cursor+3)&~3
        if cursor+len(records)*12>LANG_CAPACITY:raise ValueError('.lang overflow in menu table')
        row_off=LANG_RVA+cursor
        for i,(dst,src,cap) in enumerate(records):struct.pack_into('>III',out,row_off+i*12,dst,src,cap)
        row_va=BASE+row_off;cursor+=len(records)*12
        struct.pack_into('>I',out,LANG_RVA+0xA0+lang_id*4,row_va);menu_rows[lang_id]=row_va
    struct.pack_into('>III',out,LANG_RVA+0x14,0,2,0)
    for i,va in enumerate(rows[2][:5]):struct.pack_into('>I',out,LANG_RVA+0x58+i*4,va)
    struct.pack_into('>I',out,LANG_RVA+CURSOR_OFF,cursor)
    code=build_wrapper();helper=build_menu_helper()
    out[WRAPPER-BASE:WRAPPER-BASE+CAVE]=code+b'\0'*(CAVE-len(code))
    out[MENU_HELPER-BASE:MENU_HELPER-BASE+MENU_HELPER_CAP]=helper+b'\0'*(MENU_HELPER_CAP-len(helper))
    image=bytes(out);changed=[i for i,(a,b) in enumerate(zip(pe,image)) if a!=b]
    allowed=[(LANG_RVA+0x14,LANG_RVA+0x1c),(LANG_RVA+0x38,LANG_RVA+0x3c),(LANG_RVA+0x58,LANG_RVA+0x7c),(LANG_RVA+0xA0,LANG_RVA+0xAC),(LANG_RVA+cur,LANG_RVA+cursor),(WRAPPER-BASE,WRAPPER-BASE+CAVE),(MENU_HELPER-BASE,MENU_HELPER-BASE+MENU_HELPER_CAP)]
    if any(not any(a<=i<b for a,b in allowed) for i in changed):raise ValueError('unrelated PE bytes changed')
    if image[LANG_RVA+0x80:LANG_RVA+0x88]!=pe[LANG_RVA+0x80:LANG_RVA+0x88]:raise ValueError('B/Y scratch changed')
    if image[0xCD128:0xCD12C]!=pe[0xCD128:0xCD12C]:raise ValueError('global level script hook changed')
    return image,{'source_sha256':hashlib.sha256(pe).hexdigest(),'candidate_sha256':hashlib.sha256(image).hexdigest(),'wrapper_bytes':len(code),'helper_bytes':len(helper),'old_cursor':cur,'new_cursor':cursor,'changed_bytes':len(changed),'b_y_scratch_unchanged':True,'global_hook_unchanged':True,'selector_rows':{k:[hex(x) for x in v] for k,v in rows.items()},'menu_records':len(MENU_ITEMS),'selector_renderer':'native glyph-map with accents','hardware_validated':False}
