#!/usr/bin/env python3
"""Rotina PowerPC isolada para ativar 26 fases + 90 estrelas da .lang COURSE3.

Recebe r3=0 PT-BR, 1 ES, 2 EN. Não instala hook, não modifica XEX:
apenas produz os bytes PPC da rotina que um seletor seguro poderá chamar.

Usa metadados de curso preparados em install_trilingual_course_tables.py:
  0x830400D8 + 4*idioma -> offset da tabela de 26 ponteiros
  0x830400E4 + 4*idioma -> offset da tabela de 90 ponteiros
  cada offset relativo a 0x83040000, armazena VA BE de nome N64.
  Destinos reais: 0x829E8C70, 0x829E9620.
Registros voláteis: r4..r10, CTR, CR0. r3 preservado caso entrada válida.
Não usa armazenamento permanente; exige ser chamada uma só vez após a
escolha de idioma na tela legítima de título.
"""
import hashlib
import json
import struct

ROUTINE_VA=0x823BCC00
LANG_BASE=0x83040000
COURSE_META=LANG_BASE+0xD8
STAR_META=LANG_BASE+0xE4
COURSE_DEST=0x829E8C70
STAR_DEST=0x829E9620
COURSE_COUNT=26
STAR_COUNT=90

class Assembler:
    def __init__(self):
        self.words=[]
        self.labels={}
        self.fix=[]
    def pc(self):
        return ROUTINE_VA+len(self.words)*4
    def emit(self,word):
        self.words.append(word&0xffffffff)
    def label(self,label):
        if label in self.labels: raise ValueError("duplicate label")
        self.labels[label]=self.pc()
    def li(self,rt,val):
        if not -32768<=val<32768:raise ValueError("li imm range")
        self.emit(0x38000000|(rt<<21)|(val&0xffff))
    def lis(self,rt,imm):
        self.emit(0x3c000000|(rt<<21)|(imm&0xffff))
    def addi(self,rt,ra,imm):
        if not -32768<=imm<32768:raise ValueError("addi imm range")
        self.emit(0x38000000|(rt<<21)|(ra<<16)|(imm&0xffff))
    def ori(self,ra,rs,imm):
        self.emit(0x60000000|(rs<<21)|(ra<<16)|(imm&0xffff))
    def cmpwi(self,ra,val):
        self.emit(0x2c000000|(ra<<16)|(val&0xffff))
    def lwz(self,rt,disp,ra):
        self.emit(0x80000000|(rt<<21)|(ra<<16)|(disp&0xffff))
    def stw(self,rs,disp,ra):
        self.emit(0x90000000|(rs<<21)|(ra<<16)|(disp&0xffff))
    def lwzx(self,rt,ra,rb):
        self.emit(0x7c00002e|(rt<<21)|(ra<<16)|(rb<<11))
    def add(self,rt,ra,rb):
        self.emit(0x7c000214|(rt<<21)|(ra<<16)|(rb<<11))
    def slwi(self,ra,rs,bits):
        self.emit(0x54000000|(rs<<21)|(ra<<16)|(bits<<11) | ((31-bits)<<1))
    def mtctr(self,rs):
        self.emit(0x7c0903a6|(rs<<21))
    def blr(self):
        self.emit(0x4e800020)
    def branch(self,label,kind):
        self.fix.append((len(self.words),label,kind))
        self.emit(0)
    def resolve(self):
        for idx,label,kind in self.fix:
            pc=ROUTINE_VA+idx*4
            delta=self.labels[label]-pc
            if delta%4: raise ValueError("unaligned branch")
            if kind=="beq":
                if not -32768<=delta<32768:raise ValueError("conditional too far")
                self.words[idx]=0x41820000 |(delta&0xfffc)
            elif kind=="bdnz":
                if not -32768<=delta<32768:raise ValueError("counter too far")
                self.words[idx]=0x42000000|(delta&0xfffc)
            elif kind=="b":
                if not -(1<<25)<=delta<(1<<25):raise ValueError("branch too far")
                self.words[idx]=0x48000000|(delta&0x03fffffc)
            else:raise ValueError("unknown branch kind")
        return b"".join(struct.pack(">I",x) for x in self.words)

def emit_copy(a,meta,dest,count,tag):
    a.lis(9,LANG_BASE>>16)
    a.addi(9,9,meta-LANG_BASE)
    a.lwzx(4,9,8)
    a.lis(10,LANG_BASE>>16)
    a.add(4,4,10)
    a.lis(5,dest>>16)
    a.ori(5,5,dest&0xffff)
    a.li(6,count)
    a.mtctr(6)
    a.label(f"{tag}_loop")
    a.lwz(7,0,4)
    a.stw(7,0,5)
    a.addi(4,4,4)
    a.addi(5,5,4)
    a.branch(f"{tag}_loop","bdnz")

def build():
    a=Assembler()
    # Invalid selector -> PT-BR default. r3 = 0,1,2 accepted.
    for val in (0,1,2):
        a.cmpwi(3,val)
        a.branch("valid","beq")
    a.li(3,0)
    a.label("valid")
    a.slwi(8,3,2)
    emit_copy(a,COURSE_META,COURSE_DEST,COURSE_COUNT,"course")
    emit_copy(a,STAR_META,STAR_DEST,STAR_COUNT,"star")
    a.blr()
    return a.resolve()

def report():
    code=build()
    return {
        "status":"STANDALONE_PPC_ROUTINE_NOT_INSTALLED",
        "routine_va":hex(ROUTINE_VA),
        "bytes":len(code),
        "sha256":hashlib.sha256(code).hexdigest(),
        "langs":{"pt_br":0,"es":1,"en":2},
        "pointer_dests":{"course":hex(COURSE_DEST),"star":hex(STAR_DEST)},
        "pointer_counts":{"course":COURSE_COUNT,"star":STAR_COUNT},
        "hook_installed":False,
        "console_tested":False,
        "note":"Only callable from future safe title/intro selector, never global level_script hook"
    }

if __name__=="__main__":
    print(json.dumps(report(),indent=2))
