import unittest

from test7_intro_path_probe import patch,MARKERS,REGULAR_CALL,GAMEOVER_CALL,LANG_SECTION,GLOBAL_LEVEL_CALL,TITLE_DISPATCH

class IntroRegularPathProbeTests(unittest.TestCase):
    def base(self):
        pe=bytearray(17170432)
        pe[REGULAR_CALL:REGULAR_CALL+4]=bytes.fromhex("4bf51a45")
        pe[GAMEOVER_CALL:GAMEOVER_CALL+4]=bytes.fromhex("4bf519b1")
        pe[TITLE_DISPATCH:TITLE_DISPATCH+4]=bytes.fromhex("482754b9")
        pe[GLOBAL_LEVEL_CALL:GLOBAL_LEVEL_CALL+4]=bytes.fromhex("4bfc8321")
        pe[LANG_SECTION[0]:LANG_SECTION[0]+8]=b"SM64LANG"
        for at,old,new in MARKERS:
            pe[at:at+len(old)]=old
        return bytes(pe)

    def test_probes_only_intro_regular_and_title_marker(self):
        original=self.base()
        patched,report=patch(original,strict_sha=False)
        self.assertEqual(report["changed_byte_count"],6)
        self.assertEqual(patched[REGULAR_CALL:REGULAR_CALL+4],bytes.fromhex("60000000"))
        self.assertEqual(patched[GAMEOVER_CALL:GAMEOVER_CALL+4],original[GAMEOVER_CALL:GAMEOVER_CALL+4])
        self.assertEqual(patched[TITLE_DISPATCH:TITLE_DISPATCH+4],original[TITLE_DISPATCH:TITLE_DISPATCH+4])
        self.assertEqual(patched[GLOBAL_LEVEL_CALL:GLOBAL_LEVEL_CALL+4],original[GLOBAL_LEVEL_CALL:GLOBAL_LEVEL_CALL+4])
        self.assertEqual(patched[LANG_SECTION[0]:LANG_SECTION[1]],original[LANG_SECTION[0]:LANG_SECTION[1]])
        self.assertEqual(patched[0x778:0x77e],b"TESTE7")
        self.assertEqual(patched[0x1c98:0x1ca4],b"TESTE7 START")

    def test_digest_guard_rejects_other_build(self):
        with self.assertRaisesRegex(ValueError,"exactly original"):
            patch(self.base())

    def test_edited_regular_call_is_rejected(self):
        image=bytearray(self.base())
        image[REGULAR_CALL:REGULAR_CALL+4]=bytes.fromhex("60000000")
        with self.assertRaisesRegex(ValueError,"print call differs"):
            patch(bytes(image),strict_sha=False)

    def test_wrong_marker_is_rejected(self):
        image=bytearray(self.base())
        image[0x778]=0
        with self.assertRaisesRegex(ValueError,"unexpected title marker"):
            patch(bytes(image),strict_sha=False)

    def test_global_level_script_hook_mutation_is_rejected(self):
        image=bytearray(self.base())
        image[GLOBAL_LEVEL_CALL:GLOBAL_LEVEL_CALL+4]=bytes.fromhex("482ef7d9")
        with self.assertRaisesRegex(ValueError,"global level script"):
            patch(bytes(image),strict_sha=False)

if __name__=="__main__":
    unittest.main()
