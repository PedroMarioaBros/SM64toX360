#!/usr/bin/env python3
"""Seletor PT/ES/EN isolado na chamada de intro_regular() da tela de título.

NÃO intercepta level_script_execute (crash), nem a entrada intro_regular
(antigo TEST1 inválido). Substitui SOMENTE a BL em 0x82147448, que é executada
pela ramificação LVL_INTRO_REGULAR em lvl_intro_update, confirmada por disassembly PPC do TEST3.

Contrato de hardware (TEST3, ainda precisa de teste):
- state (.lang + 0x14) = 0: chama intro_regular original, mas temporariamente
  suprime START e mantém buttonDown ativo para impedir demo automático.
  Desenha o seletor depois, dentro do callback da intro já inicializada;
  UP/DOWN mudam escolha, A a confirma. Retorna 0 (mantém tela do título).
- após A, instala 170 ponteiros de diálogos + 26 cursos + 90 estrelas
  e marca state=1. No próximo frame, a BL volta a executar intro_regular
  normalmente; START continua para file select e level_script é intocado.
- Em nenhum momento altera a memória do mapeador B/Y (+0x80/+0x84) nem
  aloca objetos durante gameplay. r30 e r31 e LR nativos preservados.

Esta rotina sozinha não é XEX; boot, render e save são pendências de hardware.
"""
from __future__ import annotations
import hashlib, json, struct
from pregame_gate import Asm

BASE=0x82000000
CALLSITE=0x82147448
ORIGINAL_CALL_BE=bytes.fromhex("4bfffe31")  # bl intro_regular, 0x82147278
ORIGINAL_INTRO=0x82147278
WRAPPER=0x823BC900
WRAPPER_CAPACITY=0x300
ACTIVATE_DIALOGS=0x823BC800
ACTIVATE_COURSES=0x823BCC00
PRINT=0x82143110
LANG_BASE=0x83040000
CONTROLLER_PTR=0x823C8990
MENU_ALPHA=0x82E52F88
MENU_FADE=0x82E52F8B
CAVE_LANG=0x823BC800
CAVE_COURSES=0x823BCC00

def lbz(a,rt,disp,ra):
    a.emit(0x88000000|(rt<<21)|(ra<<16)|(disp&0xffff))
def sth(a,rs,disp,ra):
    a.emit(0xb0000000|(rs<<21)|(ra<<16)|(disp&0xffff))
def ori(a,ra,rs,imm):
    a.emit(0x60000000|(rs<<21)|(ra<<16)|(imm&0xffff))

def build():
    a=Asm(WRAPPER)
    a.mflr()
    a.emit(0x9421FF60)     # stwu r1,-0xA0(r1)
    a.stw(0,0x98,1)
    a.emit(0xFBC10080)     # std r30,0x80(r1)
    a.emit(0xFBE10088)     # std r31,0x88(r1)
    a.lis(30,0x8304)
    a.lwz(10,0x14,30)
    a.cmpwi(10,0)
    a.branch("passthrough","bne")

    # Store native controller fields for brief suppression of title START.
    a.li(10,0);sth(a,10,0x70,1);sth(a,10,0x72,1)
    a.lis(11,0x823D)
    a.lwz(11,-0x7670,11)
    a.cmpwi(11,0)
    a.branch("run_original","beq")
    a.lhz(9,0x10,11)        # buttonDown
    sth(a,9,0x70,1)
    a.lhz(9,0x12,11)        # buttonPressed
    sth(a,9,0x72,1)
    a.lhz(9,0x10,11)
    ori(a,8,9,1)           # harmless activity to disable attract/demo timer
    sth(a,8,0x10,11)
    a.lhz(9,0x12,11)
    a.andi(8,9,0xEFFF)     # mask START=0x1000 during language selection
    sth(a,8,0x12,11)

    a.label("run_original")
    a.call(ORIGINAL_INTRO) # native greeting/intro display still works
    a.mr(31,3)

    # Restore controller inputs before any other operation.
    a.lis(11,0x823D)
    a.lwz(11,-0x7670,11)
    a.cmpwi(11,0)
    a.branch("draw","beq")
    a.lhz(9,0x70,1)
    sth(a,9,0x10,11)
    a.lhz(9,0x72,1)
    sth(a,9,0x12,11)

    a.label("draw")
    a.lis(11,0x82E5)
    lbz(a,10,0x2F88,11)
    a.stb(10,0x74,1)
    lbz(a,10,0x2F8B,11)
    a.stb(10,0x75,1)
    a.li(10,255);a.stb(10,0x2F88,11)
    a.li(10,0);a.stb(10,0x2F8B,11)
    for x,y,ptr in (
        (76,195,0x58),  # IDIOMA / LANGUAGE
        (118,145,0x5C), # Português
        (118,115,0x60), # Español
        (118,85,0x64),  # English
        (104,30,0x68),  # A - OK
    ):
        a.li(3,x);a.li(4,y);a.lwz(5,ptr,30);a.call(PRINT)
    a.lwz(10,0x18,30)
    a.li(3,96)
    a.cmpwi(10,0);a.branch("pt","beq")
    a.cmpwi(10,1);a.branch("es","beq")
    a.li(4,85);a.branch("marker","b")
    a.label("pt");a.li(4,145);a.branch("marker","b")
    a.label("es");a.li(4,115)
    a.label("marker");a.lwz(5,0x6c,30);a.call(PRINT)
    a.lis(11,0x82E5)
    lbz(a,10,0x74,1);a.stb(10,0x2f88,11)
    lbz(a,10,0x75,1);a.stb(10,0x2f8b,11)

    # Navigate using *original* buttonPressed stored before START mask.
    a.lhz(9,0x72,1)
    a.andi(8,9,0x800)     # D-pad UP
    a.cmpwi(8,0);a.branch("down","beq")
    a.lwz(10,0x18,30)
    a.cmpwi(10,0);a.branch("dec","bne")
    a.li(10,2);a.branch("store","b")
    a.label("dec");a.addi(10,10,-1);a.branch("store","b")
    a.label("down")
    a.andi(8,9,0x400)     # D-pad DOWN
    a.cmpwi(8,0);a.branch("confirm","beq")
    a.lwz(10,0x18,30)
    a.cmpwi(10,2);a.branch("inc","bne")
    a.li(10,0);a.branch("store","b")
    a.label("inc");a.addi(10,10,1)
    a.label("store");a.stw(10,0x18,30);a.branch("remain","b")
    a.label("confirm")
    a.andi(8,9,0x8000)    # Xbox A
    a.cmpwi(8,0);a.branch("remain","beq")
    a.lwz(3,0x18,30);a.call(ACTIVATE_DIALOGS)
    a.lwz(3,0x18,30);a.call(ACTIVATE_COURSES)
    a.li(10,1);a.stw(10,0x14,30)
    a.label("remain")
    a.li(3,0)             # continue title loop, never load file-select yet
    a.branch("exit","b")

    a.label("passthrough")
    a.call(ORIGINAL_INTRO) # title after selection: native Start works
    a.label("exit")
    a.emit(0xEBC10080)     # ld r30,0x80(r1)
    a.emit(0xEBE10088)     # ld r31,0x88(r1)
    a.lwz(0,0x98,1)
    a.emit(0x382100A0)
    a.mtlr();a.blr()
    code=a.resolve()
    if len(code)>WRAPPER_CAPACITY:
        raise ValueError(f"intro selector code {len(code)} exceeds cave {WRAPPER_CAPACITY}")
    return code

def install(mapped:bytes):
    code=build()
    if mapped[CALLSITE-BASE:CALLSITE-BASE+4]!=ORIGINAL_CALL_BE:
        raise ValueError("TEST3 original title-only call has changed")
    if any(mapped[WRAPPER-BASE:WRAPPER-BASE+WRAPPER_CAPACITY]):
        raise ValueError("selector cave is not empty")
    if mapped[0xCD128:0xCD12C]!=bytes.fromhex("4bfc8321"):
        raise ValueError("original global level_script call was modified")
    if mapped[0x1040000:0x1040008]!=b"SM64LANG":
        raise ValueError("missing fixed language section")
    if mapped[0x10400C0:0x10400C8]!=b"COURSE3\0":
        raise ValueError("safe relocated COURSE3 metadata missing")
    if any(mapped[0x1040080:0x1040088]):
        raise ValueError("do not overwrite B/Y controller state fields")

    # All three patches are in fully free, disjoint code caves of TEST3.
    from language_activation import build as dialogs,ROUTINE_VA as dlg_addr
    from course_table_activation import build as courses,ROUTINE_VA as course_addr
    image=bytearray(mapped)
    for va,chunk,capacity in [
        (dlg_addr,dialogs(),0x100),
        (WRAPPER,code,WRAPPER_CAPACITY),
        (course_addr,courses(),0x100),
    ]:
        off=va-BASE
        if any(image[off:off+capacity]):
            raise ValueError(f"code cave occupied 0x{va:X}")
        image[off:off+len(chunk)]=chunk

    delta=WRAPPER-CALLSITE
    if delta%4 or not -(1<<25)<=delta<(1<<25):
        raise ValueError("title branch out of range")
    struct.pack_into(">I",image,CALLSITE-BASE,0x48000001|(delta&0x03fffffc))
    return bytes(image), {
        "status":"CANDIDATE_TITLE_ONLY_LANGUAGE_SELECTOR_NOT_HARDWARE_TESTED",
        "original_title_callsite":hex(CALLSITE),
        "original_target":hex(ORIGINAL_INTRO),
        "selector_wrapper":hex(WRAPPER),
        "wrapper_bytes":len(code),
        "wrapper_sha256":hashlib.sha256(code).hexdigest(),
        "activation_dialogs":hex(dlg_addr),
        "activation_courses":hex(course_addr),
        "original_level_script_hook_unchanged":True,
        "code_regions_modified":[
            [hex(CALLSITE-BASE),4],
            [hex(dlg_addr-BASE),len(dialogs())],
            [hex(WRAPPER-BASE),len(code)],
            [hex(course_addr-BASE),len(courses())]
        ],
        "pt_br_original_dialogs_preserved":True,
        "no_dubbing_work":True,
        "runtime_xbox_verified":False,
    }

if __name__=="__main__":
    print(json.dumps({"selector_code_bytes":len(build()),
                      "wrapper_sha256":hashlib.sha256(build()).hexdigest(),
                      "title_callsite":hex(CALLSITE),
                      "title_original":hex(ORIGINAL_INTRO),
                      "mode":"title-only no-global-hooks"},indent=2))
