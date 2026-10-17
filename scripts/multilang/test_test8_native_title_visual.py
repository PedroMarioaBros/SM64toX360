"""TEST8 regression: native title glyphs are ASCII, no changes to dialogue pointers."""
import unittest
from unittest.mock import patch as mock_patch
import hashlib,struct

import test8_native_title_visual as p

def synthetic():
    data=bytearray(p.LEN)
    data[p.PRINT_CALLSITE-p.BASE:p.PRINT_CALLSITE-p.BASE+4]=p.TEST7_NOP
    data[p.TITLE_DISPATCH-p.BASE:p.TITLE_DISPATCH-p.BASE+4]=p.TEST5_TITLE_BL
    data[0xCD128:0xCD12C]=bytes.fromhex("4bfc8321")
    data[p.LANG_BASE_RVA:p.LANG_BASE_RVA+8]=b"SM64LANG"
    data[0x778:0x77e]=b"TESTE7"
    data[0x1c98:0x1ca4]=b"TESTE7 START"
    struct.pack_into(">I",data,p.CURSOR_OFFSET,117231)
    data[0x1040080:0x1040088]=b"BY-STATE"
    data[0x1040100:0x1040108]=b"PT-BR---"
    return bytes(data)

class Test8NativeTitleVisual(unittest.TestCase):
    def patched(self,data):
        with mock_patch.object(p,"SOURCE_SHA",hashlib.sha256(data).hexdigest()):
            return p.patch(data)

    def test_native_overlay_exact_layout(self):
        original=synthetic()
        output,report=self.patched(original)
        self.assertEqual(report["status"],"TEST8_NATIVE_TITLE_VISUAL_ONLY_NOT_FUNCTIONAL_SELECTOR")
        self.assertEqual(report["code_bytes"],112)
        self.assertEqual(report["code_sha256"],"53fcb898120d7b30526770bf1e58b622f87aa582b519ef8d9d001251c2991d5c")
        self.assertEqual(output[0x147448:0x14744c],p.ORIGINAL_TITLE_BL)
        w=struct.unpack_from(">I",output,p.PRINT_CALLSITE-p.BASE)[0]
        rel=w&0x3fffffc
        if rel&0x2000000:rel-=0x4000000
        self.assertEqual(p.PRINT_CALLSITE+rel,p.WRAPPER)
        self.assertEqual(output[0x1040080:0x1040088],original[0x1040080:0x1040088])
        self.assertEqual(output[0x1040100:0x1040108],original[0x1040100:0x1040108])
        self.assertEqual(output[0xCD128:0xCD12C],original[0xCD128:0xCD12C])
        self.assertEqual(output[0x778:0x77e],b"TESTE8")
        self.assertEqual(output[0x1c98:0x1c9e],b"TESTE8")
        self.assertEqual(report["new_cursor"],117276)

    def test_ascii_nul_terminated_title_strings(self):
        output,report=self.patched(synthetic())
        for name,_,_ in p.LABELS:
            self.assertIn(name.encode("ascii")+b"\x00",
                          output[p.LANG_BASE_RVA+117231:p.LANG_BASE_RVA+117276])
        self.assertEqual(output[p.LANG_BASE_RVA+117276:p.LANG_BASE_RVA+117300],bytes(24))

    def test_input_sha_guard(self):
        with self.assertRaisesRegex(ValueError,"exact TEST7"):
            p.patch(synthetic())

    def test_cave_occupied_fails_closed(self):
        src=bytearray(synthetic());src[p.WRAPPER-p.BASE]=0x99
        with self.assertRaisesRegex(ValueError,"unrecognized bytes"):
            self.patched(bytes(src))

    def test_wrong_intro_branch_fails_closed(self):
        src=bytearray(synthetic())
        src[p.PRINT_CALLSITE-p.BASE:p.PRINT_CALLSITE-p.BASE+4]=bytes.fromhex("4bf51a45")
        with self.assertRaisesRegex(ValueError,"unrecognized bytes"):
            self.patched(bytes(src))

if __name__=="__main__":
    unittest.main()
