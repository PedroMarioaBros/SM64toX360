import hashlib
import struct
import unittest

import test9_selector_native as old
from test12_live_ui import (
    BASE, CAVE, LANG_RVA, LANG_CAPACITY, MENU_HELPER, MENU_HELPER_CAP,
    SOURCE_SHA, WRAPPER_SHA, MENU_ITEMS, PREVIEW, enc_menu, enc_preview, build_wrapper,
    build_menu_helper, build_novo_pointer_helper, NOVO_HELPER, NOVO_CALLSITE,
    NOVO_STATUS_PTRS_OFF, PREVIEW_DRAW_CALL, REGULAR_INTRO_CALLSITE, REGULAR_INTRO_ORIGINAL,
    GAMEOVER_CALLSITE, GAMEOVER_ORIGINAL, patch_test11,
)

ADDRS={
    "IDIOMAS":0x8305CA1C,
    "PORTUGUES":0x8305CA00,
    "ESPANOL":0x8305CA0C,
    "ENGLISH":0x8305CA14,
    "A CONFIRMAR":0x8305CA24,
    "X":0x8305CA30,
}

class Test12LiveUI(unittest.TestCase):
    def test_generated_code_fits_verified_caves(self):
        wrapper=build_wrapper()
        helper=build_menu_helper()
        novo_helper=build_novo_pointer_helper()
        self.assertEqual(len(wrapper),596)
        self.assertEqual(wrapper.count(bytes.fromhex("386000a0")),5)  # all five lines centered at x=160
        self.assertIn(bytes.fromhex("3d6082e539400000b14b2fe8"),wrapper)  # suppress idle demo timer
        self.assertEqual(PREVIEW_DRAW_CALL,0x8212B498)
        self.assertLessEqual(len(wrapper),CAVE)
        self.assertEqual(len(helper),108)
        self.assertEqual(hashlib.sha256(helper).hexdigest(),
                         "1d86b3c85607d3b5a8ca011e66a667699b5155c4bb2f9aae3b2bba9375172d7f")
        self.assertLessEqual(len(helper),MENU_HELPER_CAP)
        self.assertEqual(len(novo_helper),96)
        self.assertEqual(NOVO_HELPER,0x823BCB70)
        self.assertLessEqual(len(helper),NOVO_HELPER-MENU_HELPER)
        self.assertLessEqual(len(novo_helper),MENU_HELPER_CAP-(NOVO_HELPER-MENU_HELPER))

    def test_preview_labels_use_color_font_ascii_and_nul_terminator(self):
        for texts in PREVIEW.values():
            for label in texts[:5]:
                raw=enc_preview(label)
                self.assertTrue(raw.endswith(b'\0'))
                self.assertNotIn(0xFF,raw)
                self.assertEqual(raw[:-1].decode('ascii'),label)
                self.assertEqual(label, label.upper(), "selector must avoid lowercase glyphs that render gray")

    def test_all_menu_translations_fit_original_string_buffers(self):
        for off,capacity,pt,es,en in MENU_ITEMS:
            for text in (pt,es,en):
                self.assertLessEqual(len(enc_menu(text)),capacity,
                                     f"{text!r} overflows original buffer {off:#x}")

    def test_exact_TEST11_hash_is_required_by_default(self):
        with self.assertRaisesRegex(ValueError,"exact TEST11 mapped PE"):
            patch_test11(bytes(100),strict=True)

    def test_fixture_patch_is_scoped_and_keeps_BY_scratch(self):
        pe=bytearray(17_170_432)
        pe[:2]=b"MZ"
        pe[0x1040000:0x1040008]=b"SM64LANG"
        pe[0x10400C0:0x10400C8]=b"COURSE3\0"
        pe[0x1472D4:0x1472D8]=bytes.fromhex("48275a2d")
        pe[REGULAR_INTRO_CALLSITE-BASE:REGULAR_INTRO_CALLSITE-BASE+4]=REGULAR_INTRO_ORIGINAL
        pe[GAMEOVER_CALLSITE-BASE:GAMEOVER_CALLSITE-BASE+4]=GAMEOVER_ORIGINAL
        pe[0xCD128:0xCD12C]=bytes.fromhex("4bfc8321")
        pe[0x3BC600:0x3BC608]=bytes.fromhex("3cc0829e60c67170")
        pe[0x3BC608:0x3BC60C]=bytes.fromhex("4bd86d44")
        struct.pack_into(">I",pe,0x1040038,0x1CA32)
        pe[0x1040000+0x1CA30:0x1040000+0x1CA32]=b"O\0"
        pe[0x823BCD00-BASE:0x823BCD00-BASE+384]=old.build(ADDRS)
        original=bytes(pe)
        candidate,report=patch_test11(original,strict=False)
        self.assertEqual(report["wrapper_bytes"],596)
        self.assertEqual(report["helper_bytes"],108)
        self.assertEqual(report["menu_records"],len(MENU_ITEMS))
        self.assertEqual(report["novo_pointer_helper_bytes"],96)
        self.assertEqual(candidate[NOVO_HELPER-BASE:NOVO_HELPER-BASE+96],build_novo_pointer_helper())
        self.assertTrue(report["novo_callsite_patched"])
        self.assertTrue(report["b_y_scratch_unchanged"])
        self.assertTrue(report["global_hook_unchanged"])
        self.assertEqual(candidate[0x1040080:0x1040088],original[0x1040080:0x1040088])
        self.assertEqual(candidate[0xCD128:0xCD12C],original[0xCD128:0xCD12C])
        regular=old.PPC(base=REGULAR_INTRO_CALLSITE);regular.call(0x823BCD00)
        self.assertEqual(candidate[REGULAR_INTRO_CALLSITE-BASE:REGULAR_INTRO_CALLSITE-BASE+4],regular.resolve())
        gameover=old.PPC(base=GAMEOVER_CALLSITE);gameover.call(0x823BCD00)
        self.assertEqual(candidate[GAMEOVER_CALLSITE-BASE:GAMEOVER_CALLSITE-BASE+4],gameover.resolve())
        self.assertEqual(struct.unpack_from(">I",candidate,0x1040018)[0],2)
        labels=("NOVO","NUEVO","NEW")
        ptrs=struct.unpack_from(">III",candidate,LANG_RVA+NOVO_STATUS_PTRS_OFF)
        for ptr,label in zip(ptrs,labels):
            raw=enc_menu(label)
            self.assertEqual(candidate[ptr-BASE:ptr-BASE+len(raw)],raw)
        call=old.PPC(base=NOVO_CALLSITE)
        call.call(NOVO_HELPER);call.w(0x60000000)
        self.assertEqual(candidate[NOVO_CALLSITE-BASE:NOVO_CALLSITE-BASE+8],call.resolve())

if __name__=="__main__":
    unittest.main()
