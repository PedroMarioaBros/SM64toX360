"""Valida atualização delta de ES/EN no .lang sem tocar em PT-BR."""
import struct
import unittest
from unittest.mock import patch

from patch_existing_lang_dialogs import (
    update_dialogs,check_pt_br,
    LANG_RVA,LANG_SIZE,BASE,TABLE_OFFSETS,
    PT_POOL_START,PT_POOL_END
)

def encode(s):
    return s.encode("utf-8")+b"\xff"

def fixture():
    img=bytearray(LANG_RVA+LANG_SIZE)
    img[LANG_RVA:LANG_RVA+8]=b"SM64LANG"
    struct.pack_into(">III",img,LANG_RVA+8,2,3,170)
    struct.pack_into(">I",img,LANG_RVA+0x38,0x12000)
    old_at=0x1500
    img[LANG_RVA+old_at:LANG_RVA+old_at+4]=b"OLD\xff"
    for lang,offset in TABLE_OFFSETS.items():
        for i in range(170):
            struct.pack_into(">I",img,LANG_RVA+offset+i*4,
                             BASE+LANG_RVA+old_at)
    # Store a sentinel of the already-staged COURSE3 header.
    img[LANG_RVA+0xC0:LANG_RVA+0xC8]=b"COURSE3\0"
    rows={k:[{"id":i,"text":"OLD"} for i in range(170)] for k in ("es","en")}
    return bytes(img),rows

def guard(img):
    return (
        bytes(img[LANG_RVA+TABLE_OFFSETS["pt_br"]:LANG_RVA+TABLE_OFFSETS["pt_br"]+680]),
        bytes(img[LANG_RVA+PT_POOL_START:LANG_RVA+PT_POOL_END]),
    )

class LangDeltaTests(unittest.TestCase):
    def patched(self,img,rows):
        with patch("patch_existing_lang_dialogs.check_pt_br",return_value=guard(img)):
            return update_dialogs(img,rows,encode)

    def test_changes_only_es_en_and_append(self):
        img,rows=fixture()
        rows["es"][15]["text"]="PULSA A Y X"
        rows["en"][33]["text"]="LEFT STICK"
        result,report=self.patched(img,rows)
        self.assertEqual(result[:LANG_RVA],img[:LANG_RVA])
        self.assertEqual(result[LANG_RVA+0xC0:LANG_RVA+0xC8],b"COURSE3\0")
        self.assertEqual(report["lang_changed_dialog_ids"],{"es":[15],"en":[33]})
        self.assertEqual(report["unchanged_dialog_count"],{"es":169,"en":169})
        self.assertTrue(report["pt_br_bytes_unchanged"])
        self.assertEqual(guard(result),guard(img))
        for lang,idx,want in (("es",15,b"PULSA A Y X\xff"),("en",33,b"LEFT STICK\xff")):
            ptr=struct.unpack_from(">I",result,LANG_RVA+TABLE_OFFSETS[lang]+idx*4)[0]
            self.assertEqual(result[ptr-BASE:ptr-BASE+len(want)],want)

    def test_no_change_keeps_original_byte_identical(self):
        img,rows=fixture()
        result,report=self.patched(img,rows)
        self.assertEqual(result,img)
        self.assertEqual(report["lang_changed_dialog_ids"],{"es":[],"en":[]})

    def test_rejects_missing_source_dialog(self):
        img,rows=fixture()
        rows["es"].pop(45)
        with self.assertRaisesRegex(ValueError,"170 ordered"):
            self.patched(img,rows)

    def test_rejects_full_section_without_overflow(self):
        img,rows=fixture()
        changed=bytearray(img)
        # Existing cursor almost exhausts capacity; upper range still zero.
        struct.pack_into(">I",changed,LANG_RVA+0x38,LANG_SIZE-4)
        rows["es"][15]["text"]="VERY LONG TEXT"
        with self.assertRaisesRegex(ValueError,"capacity exhausted"):
            self.patched(bytes(changed),rows)

    def test_rejects_unexpected_ptr_outside_lang(self):
        img,rows=fixture()
        b=bytearray(img)
        struct.pack_into(">I",b,LANG_RVA+TABLE_OFFSETS["es"],BASE+0x1500)
        with self.assertRaisesRegex(ValueError,"not within"):
            self.patched(bytes(b),rows)

    def test_real_ptbr_guard_rejects_synthetic_source(self):
        img,_=fixture()
        with self.assertRaisesRegex(ValueError,"PT-BR bytes"):
            check_pt_br(img)


if __name__=="__main__":
    unittest.main()
