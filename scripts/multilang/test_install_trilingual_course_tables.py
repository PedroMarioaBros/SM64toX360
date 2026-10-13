"""Regressões de 26 nomes/90 estrelas do .lang, sem ROM/XEX privado."""
import hashlib
import struct
import unittest
from unittest.mock import patch

from install_trilingual_course_tables import (
    IMAGE_BASE, LANG_RVA, LANG_SIZE, COURSE_TABLE, STAR_TABLE,
    COURSE_COUNT, STAR_COUNT, MAIN_COURSES, SECRETS,
    check_original_tables, ordered_catalog, install,
)


def catalogs():
    def one(language):
        return {
            "courses": {
                k:{"name":f"{i+1} {language.upper()} COURSE {i}",
                   "acts":[f"{language.upper()} STAR {i}:{j}" for j in range(6)]}
                for i,k in enumerate(MAIN_COURSES)
            },
            "secrets":{k:("" if k=="COURSE_CAKE_END" else f"{language.upper()} SECRET {i}")
                       for i,k in enumerate(SECRETS)},
            "castle_secret_stars":f"{language.upper()} CASTLE STARS",
            "extra_text":{i:"" for i in range(7)}
        }
    return one("en"),one("es")


def synthetic_pe(cursor=0x2000):
    data=bytearray(LANG_RVA+LANG_SIZE)
    data[LANG_RVA:LANG_RVA+8]=b"SM64LANG"
    data[LANG_RVA+8:LANG_RVA+12]=b"TEST"
    struct.pack_into(">I",data,LANG_RVA+0x38,cursor)
    data[LANG_RVA+0x100:LANG_RVA+0x108]=b"PTBBLOCK"
    pt_courses=b"".join(struct.pack(">I",IMAGE_BASE+0x8000+i*16) for i in range(26))
    pt_stars=b"".join(struct.pack(">I",IMAGE_BASE+0x9000+i*16) for i in range(90))
    data[COURSE_TABLE:COURSE_TABLE+len(pt_courses)]=pt_courses
    data[STAR_TABLE:STAR_TABLE+len(pt_stars)]=pt_stars
    return bytes(data),pt_courses,pt_stars


def encoder(text):
    # Synthetic test encoding, never used as a real SM64 string encoder.
    return text.encode("utf-8")+b"\xff"


class ThreeLanguageCourseTableTests(unittest.TestCase):
    def test_26_course_names_and_90_star_titles(self):
        image,ptc,pts=synthetic_pe()
        en,es=catalogs()
        with patch("install_trilingual_course_tables.check_original_tables",return_value=(ptc,pts)):
            changed,report=install(image,en,es,encoder)
        self.assertEqual(report["status"],"COURSE3_STAGED_NO_RUNTIME_HOOK")
        self.assertEqual(changed[:LANG_RVA],image[:LANG_RVA])
        self.assertEqual(changed[LANG_RVA+0x100:LANG_RVA+0x108],b"PTBBLOCK")
        self.assertEqual(changed[LANG_RVA+0x80:LANG_RVA+0x88],b"COURSE3\0")
        self.assertTrue(report["existing_dialogs_and_layout_preserved"])
        self.assertEqual(report["records"]["es_course"]["count"],26)
        self.assertEqual(report["records"]["en_star"]["count"],90)
        for i in range(3):
            pco=struct.unpack_from(">I",changed,LANG_RVA+0x98+4*i)[0]
            pso=struct.unpack_from(">I",changed,LANG_RVA+0xA4+4*i)[0]
            self.assertEqual(len(changed[LANG_RVA+pco:LANG_RVA+pco+26*4]),104)
            self.assertEqual(len(changed[LANG_RVA+pso:LANG_RVA+pso+90*4]),360)
            cake=struct.unpack_from(">I",changed,LANG_RVA+pco+24*4)[0]
            original_cake=struct.unpack_from(">I",ptc,24*4)[0]
            self.assertEqual(cake,original_cake)
            if i==0:
                self.assertEqual(changed[LANG_RVA+pco:LANG_RVA+pco+104],ptc)
                self.assertEqual(changed[LANG_RVA+pso:LANG_RVA+pso+360],pts)
            else:
                self.assertNotEqual(changed[LANG_RVA+pco:LANG_RVA+pco+104],ptc)
        self.assertGreater(report["new_used_bytes"],report["old_used_bytes"])
        self.assertTrue(report["runtime_switch_not_installed"])

    def test_original_ptbr_pointer_guards_fail_closed(self):
        image,_,_=synthetic_pe()
        with self.assertRaisesRegex(ValueError,"differs from hardware-approved TEST3"):
            check_original_tables(image)

    def test_cannot_overwrite_existing_header_metadata(self):
        image,ptc,pts=synthetic_pe()
        arr=bytearray(image)
        arr[LANG_RVA+0x80]=1
        en,es=catalogs()
        with patch("install_trilingual_course_tables.check_original_tables",return_value=(ptc,pts)):
            with self.assertRaisesRegex(ValueError,"already occupied"):
                install(bytes(arr),en,es,encoder)

    def test_no_capacity_is_rejected(self):
        image,ptc,pts=synthetic_pe(LANG_SIZE-0x10)
        en,es=catalogs()
        with patch("install_trilingual_course_tables.check_original_tables",return_value=(ptc,pts)):
            with self.assertRaisesRegex(ValueError,"capacity|overflow"):
                install(image,en,es,encoder)

    def test_wrong_course_order_is_rejected(self):
        en,es=catalogs()
        data=es["courses"].pop("COURSE_BOB")
        es["courses"]["COURSE_BOB"]=data
        with self.assertRaisesRegex(ValueError,"order|diverge"):
            ordered_catalog(en,es)

    def test_missing_secret_slot_is_rejected(self):
        en,es=catalogs()
        es["secrets"].pop("COURSE_CAKE_END")
        with self.assertRaises(ValueError):
            ordered_catalog(en,es)

    def test_base_game_bytes_never_overwritten(self):
        image,ptc,pts=synthetic_pe()
        en,es=catalogs()
        with patch("install_trilingual_course_tables.check_original_tables",return_value=(ptc,pts)):
            changed,_=install(image,en,es,encoder)
        self.assertEqual(hashlib.sha256(image[:LANG_RVA]).hexdigest(),
                         hashlib.sha256(changed[:LANG_RVA]).hexdigest())


if __name__=="__main__":
    unittest.main()
