import struct
import unittest

from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as cp

import test12_live_ui as ui

LANG=ui.LANG_BASE
PAD_GLOBAL=ui.CONTROLLER_GLOBAL
PAD=0x84000200
STOP=0x84001000
DIALOG=ui.ACTIVATE_DIALOGS
COURSE=ui.ACTIVATE_COURSES
PRINT=ui.PRINT_CENTER
PRINT_TITLE=ui.PRINT_CENTER
ORIGINAL=ui.ORIGINAL_PRINT
REG=[getattr(cp,f"UC_PPC_REG_{i}") for i in range(32)]

def w32(u,a,v):u.mem_write(a,struct.pack(">I",v&0xffffffff))
def r32(u,a):return struct.unpack(">I",bytes(u.mem_read(a,4)))[0]
def w16(u,a,v):u.mem_write(a,struct.pack(">H",v&0xffff))
def r16(u,a):return struct.unpack(">H",bytes(u.mem_read(a,2)))[0]
def cstr(u,a):
    out=bytearray()
    for i in range(128):
        b=bytes(u.mem_read(a+i,1))[0]
        if b==0:break
        out.append(b)
    return out.decode("ascii")

def decode_selector(u,a):
    reverse={i+0x0A:chr(65+i) for i in range(26)}
    reverse.update({i+0x24:chr(97+i) for i in range(26)})
    reverse.update({0x9E:' ',0x65:'ê',0x64:'é',0x42:'ñ',0x41:'Ê',0x40:'É',0x43:'Ñ',
                     0x60:'á',0x66:'í',0x67:'ó',0x6A:'ú',0x6D:'Á',0x71:'Ã',0x70:'Â',
                     0x7A:'Ç',0x72:'É',0x73:'Ê',0x74:'Í',0x75:'Ó',0x76:'Ô',0x77:'Õ',0x78:'Ú',0x79:'Ü'})
    out=[]
    for i in range(128):
        b=bytes(u.mem_read(a+i,1))[0]
        if b==0xFF:break
        out.append(reverse.get(b,'?'))
    return ''.join(out)

def cpu(selected=2,button=0,state=0):
    u=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    for base,size in ((0x82000000,0x1000000),(LANG,0x20000),(0x84000000,0x20000)):
        u.mem_map(base,size)
    u.mem_write(ui.WRAPPER,ui.build_wrapper())
    u.mem_write(ui.MENU_HELPER,ui.build_menu_helper())
    u.mem_write(LANG+0x80,b"BY-STATE")
    w32(u,LANG+0x14,state);w32(u,LANG+0x18,selected)
    labels={}
    for lang_id,texts in ui.PREVIEW.items():
        row=LANG+0x1000+lang_id*0x100
        ptrs=[]
        for i,text in enumerate(texts):
            ptr=LANG+0x2000+lang_id*0x200+i*0x40
            raw=ui.enc_selector_title(text) if i<5 else text.encode("ascii")+b"\0"
            u.mem_write(ptr,raw)
            ptrs.append(ptr)
        for i,ptr in enumerate(ptrs):w32(u,row+i*4,ptr)
        w32(u,LANG+0x70+lang_id*4,row)
        labels[lang_id]=texts
    for lang_id,col in ((0,2),(1,3),(2,4)):
        row=LANG+0x5000+lang_id*0x1000
        for i,(off,cap,pt,es,en) in enumerate(ui.MENU_ITEMS):
            src=LANG+0x9000+lang_id*0x1000+i*0x40
            raw=ui.enc_menu((pt,es,en)[lang_id])
            u.mem_write(src,raw)
            w32(u,row+i*12,0x82000000+off)
            w32(u,row+i*12+4,src)
            w32(u,row+i*12+8,cap)
            # Initialize each target with the PT-BR bytes so a translation is observable.
            u.mem_write(0x82000000+off,ui.enc_menu(pt))
        w32(u,LANG+0xA0+lang_id*4,row)
    for lang_id,label in ((0,"NOVO"),(1,"NUEVO"),(2,"NEW")):
        ptr=LANG+0x15000+lang_id*0x100
        u.mem_write(ptr,ui.enc_menu(label))
        w32(u,LANG+ui.NOVO_STATUS_PTRS_OFF+lang_id*4,ptr)
    w32(u,PAD_GLOBAL,PAD)
    w16(u,PAD+0x12,button)
    u.reg_write(REG[1],0x84018000)
    u.reg_write(REG[30],0x12345678);u.reg_write(REG[31],0x87654321)
    u.reg_write(cp.UC_PPC_REG_LR,STOP)
    printed=[];original=[]
    def hook(emu,addr,size,_):
        if addr==STOP:emu.emu_stop()
        elif addr in (DIALOG,COURSE,PRINT,PRINT_TITLE,ui.PREVIEW_DRAW_CALL,ORIGINAL):
            if addr in (PRINT,PRINT_TITLE,ui.PREVIEW_DRAW_CALL):
                x,y,p=(emu.reg_read(REG[k]) for k in (3,4,5))
                raw=bytes(emu.mem_read(p,128))
                ff=raw.find(bytes([255]));nul=raw.find(bytes([0]))
                text=decode_selector(emu,p) if ff>=0 and (nul<0 or ff<nul) else cstr(emu,p)
                printed.append((text,x,y))
            elif addr==ORIGINAL:original.append(True)
            emu.reg_write(cp.UC_PPC_REG_PC,emu.reg_read(cp.UC_PPC_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(ui.WRAPPER,STOP+4,count=20000)
    return u,printed,original

class Test12LiveUIRuntime(unittest.TestCase):
    def test_live_preview_uses_current_language_before_A(self):
        for lang_id,expected in ui.PREVIEW.items():
            u,printed,original=cpu(lang_id,0,0)
            self.assertEqual([x[0] for x in printed[:5]],expected[:5])
            self.assertEqual(r32(u,LANG+0x18),lang_id)
            self.assertFalse(original)
            self.assertEqual(bytes(u.mem_read(LANG+0x80,8)),b"BY-STATE")

    def test_down_moves_through_English_Spanish_Portuguese(self):
        for selected,expected in ((2,1),(1,0),(0,2)):
            u,printed,original=cpu(selected,0x0400,0)
            self.assertEqual(r32(u,LANG+0x18),expected)
            self.assertEqual([x[0] for x in printed[:5]],ui.PREVIEW[expected][:5])

    def test_up_moves_through_Portuguese_Spanish_English(self):
        for selected,expected in ((0,1),(1,2),(2,0)):
            u,printed,original=cpu(selected,0x0800,0)
            self.assertEqual(r32(u,LANG+0x18),expected)
            self.assertEqual([x[0] for x in printed[:5]],ui.PREVIEW[expected][:5])

    def test_A_localizes_save_menu_and_start_prompt(self):
        for lang_id in (1,2):
            u,printed,original=cpu(lang_id,0x8000|0x1000,0)
            self.assertEqual(r32(u,LANG+0x14),1)
            self.assertEqual(len(original),0)
            self.assertIn((ui.PREVIEW[lang_id][5],60,38),printed)
            self.assertIn(("START",60,20),printed)
            for off,cap,pt,es,en in ui.MENU_ITEMS:
                self.assertEqual(bytes(u.mem_read(0x82000000+off,len(ui.enc_menu((pt,es,en)[lang_id])))),
                                 ui.enc_menu((pt,es,en)[lang_id]))
            self.assertEqual(bytes(u.mem_read(LANG+0x80,8)),b"BY-STATE")
            self.assertEqual(u.reg_read(REG[30]),0x12345678)
            self.assertEqual(u.reg_read(REG[31]),0x87654321)

    def test_empty_save_slot_status_pointer_tracks_each_language(self):
        for lang_id,label in ((0,"NOVO"),(1,"NUEVO"),(2,"NEW")):
            u,printed,original=cpu(lang_id,0,0)
            ptr=LANG+0x15000+lang_id*0x100
            u.mem_write(ui.NOVO_HELPER,ui.build_novo_pointer_helper())
            u.reg_write(REG[0],0xCAFEBABE)
            u.reg_write(REG[10],0x10203040)
            u.reg_write(REG[11],0x87654321)
            u.reg_write(cp.UC_PPC_REG_LR,STOP)
            u.emu_start(ui.NOVO_HELPER,STOP+4,count=2000)
            self.assertEqual(u.reg_read(REG[6]),ptr)
            self.assertEqual(bytes(u.mem_read(ptr,len(ui.enc_menu(label)))),ui.enc_menu(label))
            self.assertEqual(u.reg_read(REG[0]),0xCAFEBABE)
            self.assertEqual(u.reg_read(REG[10]),0x10203040)
            self.assertEqual(u.reg_read(REG[11]),0x87654321)

    def test_A_in_Portuguese_preserves_native_prompt_and_localizes_menu(self):
        u,printed,original=cpu(0,0x8000|0x1000,0)
        self.assertEqual(r32(u,LANG+0x14),1)
        self.assertEqual(len(original),1)
        self.assertEqual(printed,[])
        for off,cap,pt,es,en in ui.MENU_ITEMS:
            self.assertEqual(bytes(u.mem_read(0x82000000+off,len(ui.enc_menu(pt)))),ui.enc_menu(pt))

if __name__=="__main__":
    unittest.main()
