"""TEST10 diagnostic: use exact routine, no controller writes or selector activation."""
import hashlib
import struct
import unittest
from unittest.mock import patch as mocked
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as reg
import test10_controller_read_probe as target

G=[getattr(reg,f'UC_PPC_REG_{i}') for i in range(32)]
PAD=0x82E47BB8
STOP=0x84010000

def half(u,at):return struct.unpack('>H',bytes(u.mem_read(at,2)))[0]
def sethalf(u,at,n):u.mem_write(at,struct.pack('>H',n))

def emulate(button, pad_available=True):
    u=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    for start,size in ((0x82000000,0x1000000),
                       (0x83040000,0x20000),(0x81010000,0x10000),
                       (0x84010000,0x10000)):
        u.mem_map(start,size)
    offsets=[0x18000,0x18040,0x18080,0x180c0,0x18100]
    labels=['TESTE10','PORTUGUES','ESPANOL','ENGLISH','X']
    pointers={}
    for word,at in zip(labels,offsets):
        va=0x83040000+at
        u.mem_write(va,word.encode('ascii')+b'\0')
        pointers[word]=va
    code=target.build(pointers)
    u.mem_write(target.WRAPPER,code)
    u.mem_write(target.PAD_PTR,struct.pack('>I',PAD if pad_available else 0))
    sethalf(u,PAD+0x10,button)
    sethalf(u,PAD+0x12,0x1234)  # Must remain intact
    u.reg_write(G[1],0x81018000)
    u.reg_write(G[30],0x80808080)
    u.reg_write(reg.UC_PPC_REG_LR,STOP)
    labels=[];calls=[]
    def cb(emu,pc,size,unused):
        if pc==STOP:
            emu.emu_stop();return
        if pc==target.PRINT_CENTER:
            addr=emu.reg_read(G[5])
            text=bytes(emu.mem_read(addr,30)).split(b'\0')[0].decode('ascii')
            labels.append((text,emu.reg_read(G[3]),emu.reg_read(G[4])))
            emu.reg_write(reg.UC_PPC_REG_PC,emu.reg_read(reg.UC_PPC_REG_LR))
        if pc==target.ORIGINAL_PRINT:
            calls.append('native')
            emu.reg_write(reg.UC_PPC_REG_PC,emu.reg_read(reg.UC_PPC_REG_LR))
    u.hook_add(UC_HOOK_CODE,cb)
    u.emu_start(target.WRAPPER,STOP+4,count=10000)
    return u,labels,calls

class Test10ReadOnlyControlTests(unittest.TestCase):
    def test_wrapper_structure(self):
        addr={'TESTE10':0x8305ca1c,'PORTUGUES':0x8305ca00,'ESPANOL':0x8305ca0c,'ENGLISH':0x8305ca14,'X':0x8305ca24}
        code=target.build(addr)
        self.assertEqual(hashlib.sha256(code).hexdigest(),'4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f')
        self.assertEqual(len(code),204)
        self.assertNotIn(bytes.fromhex('b10b0012'),code)  # Never st(h) to buttonPressed
        self.assertNotIn(bytes.fromhex('b10b0010'),code)  # Never st(h) to buttonDown

    def test_first_frame_has_title_and_options_only(self):
        u,labels,native=emulate(0)
        self.assertEqual(native,['native'])
        self.assertEqual([x[0] for x in labels],['TESTE10','PORTUGUES','ESPANOL','ENGLISH'])
        self.assertEqual(half(u,PAD+0x12),0x1234)
        self.assertEqual(half(u,PAD+0x10),0)
        self.assertEqual(u.reg_read(G[1]),0x81018000)
        self.assertEqual(u.reg_read(G[30]),0x80808080)

    def test_each_held_button_draws_marker_without_writing_input(self):
        for btn,y in ((0x800,145),(0x400,115),(0x8000,85)):
            u,labels,native=emulate(btn)
            self.assertEqual(labels[-1],('X',14,y))
            self.assertEqual(half(u,PAD+0x10),btn)
            self.assertEqual(half(u,PAD+0x12),0x1234)
            self.assertEqual(native,['native'])

    def test_start_keeps_native_behavior_untouched(self):
        u,labels,native=emulate(0x1000)
        self.assertEqual(len(labels),4)
        self.assertEqual(half(u,PAD+0x10),0x1000)
        self.assertEqual(half(u,PAD+0x12),0x1234)

    def test_null_controller_pointer_does_not_crash(self):
        u,labels,native=emulate(0x800,False)
        self.assertEqual(len(labels),4)
        self.assertEqual(native,['native'])

if __name__=='__main__':unittest.main()