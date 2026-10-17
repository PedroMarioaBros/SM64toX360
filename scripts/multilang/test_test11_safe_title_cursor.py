import hashlib
import unittest
from test11_safe_title_cursor import patch,CURSOR_LABEL_OFF,EXPECTED_SIZE,OUTPUT_PE_SHA256

class TitleCursorRegression(unittest.TestCase):
    def fixture(self):
        pe=bytearray(EXPECTED_SIZE)
        pe[:2]=b"MZ"
        pe[0x1040000:0x1040008]=b"SM64LANG"
        pe[CURSOR_LABEL_OFF:CURSOR_LABEL_OFF+2]=b"X\x00"
        pe[0x1472d4:0x1472d8]=bytes.fromhex("48275a2d")
        pe[0xcd128:0xcd12c]=bytes.fromhex("4bfc8321")
        return bytes(pe)

    def test_one_byte_only_and_no_runtime_changes(self):
        a=self.fixture()
        b,r=patch(a,strict_source=False)
        self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
        self.assertEqual(b[CURSOR_LABEL_OFF:CURSOR_LABEL_OFF+2],b"O\x00")
        self.assertEqual(r["changed_effective_bytes"],1)
        self.assertEqual(a[:CURSOR_LABEL_OFF],b[:CURSOR_LABEL_OFF])
        self.assertEqual(a[CURSOR_LABEL_OFF+1:],b[CURSOR_LABEL_OFF+1:])

    def test_wrong_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"exact TEST9"):
            patch(self.fixture())

    def test_unexpected_marker_is_rejected(self):
        pe=bytearray(self.fixture())
        pe[CURSOR_LABEL_OFF]=ord("Z")
        with self.assertRaisesRegex(ValueError,"original X NUL"):
            patch(bytes(pe),strict_source=False)

    def test_unrecognized_intro_is_rejected(self):
        pe=bytearray(self.fixture())
        pe[0x1472d4:0x1472d8]=bytes.fromhex("60000000")
        with self.assertRaisesRegex(ValueError,"intro call differs"):
            patch(bytes(pe),strict_source=False)

    def test_expected_digest_pinned(self):
        self.assertEqual(OUTPUT_PE_SHA256,
            "a52da425c9cf294e9005fc4cce95b0c02b015f9ea2b0f88ea17df268c52b9ecd")

if __name__=="__main__":
    unittest.main()
