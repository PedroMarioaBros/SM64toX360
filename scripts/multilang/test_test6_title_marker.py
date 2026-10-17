import unittest
from test6_title_marker import mark,MARKERS

class MarkerProbeTests(unittest.TestCase):
    def fixture(self):
        pe=bytearray(0x1060000)
        pe[0x1040000:0x1040008]=b"SM64LANG"
        pe[0x147448:0x14744C]=bytes.fromhex("482754b9")
        pe[0xCD128:0xCD12C]=bytes.fromhex("4bfc8321")
        for p,(old,_) in MARKERS.items():
            pe[p:p+len(old)]=old
        return bytes(pe)

    def test_only_title_strings_change(self):
        a=self.fixture()
        b,r=mark(a,require_known_sha=False)
        self.assertEqual(len(a),len(b))
        self.assertEqual(r["changed_bytes"],12)
        self.assertEqual(b[0x778:0x77e],b"TESTE6")
        self.assertEqual(b[0x1c98:0x1ca4],b"TESTE6 START")
        self.assertEqual(a[0x1040000:0x1060000],b[0x1040000:0x1060000])
        self.assertEqual(a[0x147448:0x14744c],b[0x147448:0x14744c])
        self.assertEqual(a[0xcd128:0xcd12c],b[0xcd128:0xcd12c])

    def test_wrong_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"exact mapped TEST5"):
            mark(self.fixture())

    def test_unknown_title_string_is_rejected(self):
        b=bytearray(self.fixture())
        b[0x778]=0
        with self.assertRaisesRegex(ValueError,"unexpected title"):
            mark(bytes(b),require_known_sha=False)

if __name__=="__main__":
    unittest.main()
