"""TEST9 PowerPC REAL routine bytes: CPU-only simulation, no game files.

Code bytes are the SHA-256-verified 384-byte wrapper from the private TEST9
candidate PE. This test runs the SAME instructions that would run on Xbox.
It mocks native title printer and verifies controller/read/copies.
None of these tests are a claim of actual Xbox hardware validation.
"""
import hashlib
import struct
import unittest
from unicorn import Uc, UC_ARCH_PPC, UC_MODE_32, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn import ppc_const as cp
from language_activation import build as dialog_code
from course_table_activation import build as course_code

WRAPPER=0x823BCD00
PRINT=0x8212B498
ORIG=0x82098D18
DIALOG_ACT=0x823BC800
COURSE_ACT=0x823BCC00
PAD_GLOBAL=0x823C8990
PAD=0x84000200
LANG=0x83040000
STOP=0x84001000
DEST_DIALOG=0x829E7CD8
DEST_COURSE=0x829E8C70
DEST_STAR=0x829E9620
RAW=bytes.fromhex(
"7c0802a69421ff80900100783d608304814b00142c0a0000408201543d60823d816b89902c0b0000418200a0a12b00127128efffb10b0012712808002c080000418200243d608304814b00182c0a00004082000c3940000248000034394affff4800002c712804002c080000418200283d608304814b00182c0a00024082000c3940000048000008394a0001914b001848000038712880002c0800004182002c3d608304806b00184bfffa593d608304806b00184bfffe4d3d60830439400001914b0014480000a838600048388000cb3ca0830560a5ca1c4bd6e6c138600046388000a43ca0830560a5ca004bd6e6ad38600046388000863ca0830560a5ca0c4bd6e69938600046388000683ca0830560a5ca144bd6e685386000413880002b3ca0830560a5ca244bd6e6713d608304814b00182c0a0000418200142c0a0001418200143880006848000010388000a448000008388000863860000e3ca0830560a5ca304bd6e635480000084bcdbead80010078382100807c0803a64e800020"
)
assert len(RAW)==384
assert hashlib.sha256(RAW).hexdigest()=="7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1"
G=[getattr(cp,f"UC_PPC_REG_{i}") for i in range(32)]
def u32(v):return struct.pack(">I",v&0xffffffff)
def wr32(u,a,v):u.mem_write(a,u32(v))
def rd32(u,a):return struct.unpack(">I",bytes(u.mem_read(a,4)))[0]
def wr16(u,a,v):u.mem_write(a,struct.pack(">H",v&65535))
def rd16(u,a):return struct.unpack(">H",bytes(u.mem_read(a,2)))[0]
def cpu(state=0,idx=0,button=0):
    u=Uc(UC_ARCH_PPC,UC_MODE_32|UC_MODE_BIG_ENDIAN)
    for base,size in ((0x82000000,0x1000000),(LANG,0x20000),
                      (0x81010000,0x10000),(0x84000000,0x20000)):
        u.mem_map(base,size)
    for addr,data in ((WRAPPER,RAW),(DIALOG_ACT,dialog_code()),(COURSE_ACT,course_code())):
        u.mem_write(addr,data)
    labels={"IDIOMAS":0x8305CA1C,"PORTUGUES":0x8305CA00,
            "ESPANOL":0x8305CA0C,"ENGLISH":0x8305CA14,
            "A CONFIRMAR":0x8305CA24,"X":0x8305CA30}
    for word,addr in labels.items():
        u.mem_write(addr,word.encode("ascii")+b"\0")
    wr32(u,LANG+0x14,state);wr32(u,LANG+0x18,idx)
    u.mem_write(LANG+0x80,b"BY-STATE")
    wr32(u,PAD_GLOBAL,PAD)
    wr16(u,PAD+0x12,button)
    for lang,table in enumerate((0x83040100,0x830403B0,0x83040660)):
        for i in range(170):
            wr32(u,table+i*4,0xAF000000|(lang<<20)|i)
    for sec,meta,dest,n,offsets in (
        (0,0x830400D8,DEST_COURSE,26,(0x1C000,0x1C100,0x1C200)),
        (1,0x830400E4,DEST_STAR,90,(0x1C300,0x1C500,0x1C700))
    ):
        for lang,off in enumerate(offsets):
            wr32(u,meta+4*lang,off)
            for i in range(n):
                wr32(u,LANG+off+4*i,0xB1000000|(lang<<20)|(sec<<18)|i)
        u.mem_write(dest,b"\x55"*(4*n))
        u.mem_write(dest-4,b"\xDA\x7A\xDA\x7A")
        u.mem_write(dest+4*n,b"\xFE\xDC\xBA\x98")
    u.reg_write(G[1],0x81018000)
    u.reg_write(G[30],0x12345678)
    u.reg_write(G[31],0x87654321)
    u.reg_write(cp.UC_PPC_REG_LR,STOP)
    printed=[];original=[]
    def hook(emu,addr,size,_):
        if addr==STOP:
            emu.emu_stop()
        elif addr==PRINT:
            x,y,p=(emu.reg_read(G[k]) for k in (3,4,5))
            printed.append((bytes(emu.mem_read(p,25)).split(b"\0")[0].decode("ascii"),x,y))
            emu.reg_write(cp.UC_PPC_REG_PC,emu.reg_read(cp.UC_PPC_REG_LR))
        elif addr==ORIG:
            original.append(True)
            emu.reg_write(cp.UC_PPC_REG_PC,emu.reg_read(cp.UC_PPC_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(WRAPPER,STOP+4,count=10000)
    return u,printed,original

class Test9CpuRegressions(unittest.TestCase):
    def test_title_native_labels_and_registers(self):
        u,labels,orig=cpu()
        self.assertEqual(orig,[])
        self.assertEqual([s[0] for s in labels],
                         ["IDIOMAS","PORTUGUES","ESPANOL","ENGLISH","A CONFIRMAR","X"])
        self.assertEqual(labels[-1],("X",14,164))
        self.assertEqual(u.reg_read(G[1]),0x81018000)
        self.assertEqual(u.reg_read(G[30]),0x12345678)
        self.assertEqual(u.reg_read(G[31]),0x87654321)

    def test_start_does_not_enter_before_selection(self):
        u,labels,orig=cpu(0,0,0x1000)
        self.assertEqual(orig,[])
        self.assertEqual(rd16(u,PAD+0x12)&0x1000,0)
        self.assertEqual(rd32(u,LANG+0x14),0)

    def test_navigation_wraps_and_marks_row(self):
        for before,button,after,y in ((0,0x0800,2,104),(0,0x0400,1,134),
                                      (2,0x0400,0,164),(1,0x0800,0,164)):
            u,labels,orig=cpu(0,before,button|0x1000)
            self.assertEqual(rd32(u,LANG+0x18),after)
            self.assertEqual(labels[-1],("X",14,y))
            self.assertFalse(rd16(u,PAD+0x12)&0x1000)
            self.assertEqual(bytes(u.mem_read(LANG+0x80,8)),b"BY-STATE")

    def test_A_switches_all_286_pointers_per_language(self):
        for selected in (0,1,2):
            u,labels,orig=cpu(0,selected,0x8000|0x1000)
            self.assertEqual(rd32(u,LANG+0x14),1)
            self.assertEqual(rd32(u,LANG+0x18),selected)
            self.assertEqual(len(orig),1)
            self.assertEqual(labels,[])
            for i in range(170):
                self.assertEqual(rd32(u,DEST_DIALOG+i*16),0xAF000000|(selected<<20)|i)
            for sec,dest,n in ((0,DEST_COURSE,26),(1,DEST_STAR,90)):
                for i in range(n):
                    self.assertEqual(rd32(u,dest+4*i),
                                     0xB1000000|(selected<<20)|(sec<<18)|i)
                self.assertEqual(bytes(u.mem_read(dest-4,4)),b"\xDA\x7A\xDA\x7A")
                self.assertEqual(bytes(u.mem_read(dest+4*n,4)),b"\xFE\xDC\xBA\x98")
            self.assertEqual(bytes(u.mem_read(LANG+0x80,8)),b"BY-STATE")
            self.assertFalse(rd16(u,PAD+0x12)&0x1000)
            self.assertEqual(u.reg_read(G[30]),0x12345678)
            self.assertEqual(u.reg_read(G[31]),0x87654321)

    def test_after_confirmation_start_is_native(self):
        u,labels,orig=cpu(1,2,0x1000)
        self.assertEqual(labels,[])
        self.assertEqual(len(orig),1)
        self.assertEqual(rd16(u,PAD+0x12)&0x1000,0x1000)

if __name__=="__main__":
    unittest.main()
