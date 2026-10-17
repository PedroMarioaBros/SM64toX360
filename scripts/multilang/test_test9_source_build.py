"""Reproducibility and fail-closed guards for complete TEST9 source builder."""
import hashlib
import unittest
from test9_selector_native import build,patch,WRAPPER,CAVE,LANG_RVA,LANG_BASE

ADDRS={
 "IDIOMAS":0x8305CA1C,"PORTUGUES":0x8305CA00,
 "ESPANOL":0x8305CA0C,"ENGLISH":0x8305CA14,
 "A CONFIRMAR":0x8305CA24,"X":0x8305CA30,
}

class Test9BuildGuards(unittest.TestCase):
    def test_generated_wrapper_matches_exact_hardware_candidate(self):
        data=build(ADDRS)
        self.assertEqual(len(data),384)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "7198267b6f0e7699f5226637cd5db7e5f9470d5b5f3b9aac69e8d6e2ac0db6b1")
        self.assertLess(len(data),CAVE)
        self.assertEqual(data[:12].hex(),"7c0802a69421ff8090010078")

    def test_rejects_wrong_source_pe(self):
        with self.assertRaisesRegex(ValueError,"exact TEST8"):
            patch(bytes(100),strict=True)

    def test_published_source_retains_no_global_hook(self):
        import inspect
        import test9_selector_native as source
        data=inspect.getsource(source.patch)
        self.assertIn("global level script hook mutated",data)
        self.assertIn("canonical PT/ES/EN pointers changed",data)
        self.assertIn("B/Y runtime scratch mutated",data)
        self.assertNotIn("game_hook_install",data)

if __name__=="__main__":
    unittest.main()
