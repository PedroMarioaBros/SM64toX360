import struct
import unittest

from scan_intro_text_callers import BASE, IMAGE_LEN, PRINT_INTRO_TEXT, scan


def bl(src, target):
    disp = target - src
    if disp % 4 or not -(1 << 25) <= disp < (1 << 25):
        raise ValueError("branch out of range")
    return 0x48000001 | (disp & 0x03FFFFFC)


class IntroTextCallScannerTests(unittest.TestCase):
    def test_finds_relative_branch_and_link_to_print_intro_text(self):
        image = bytearray(IMAGE_LEN)
        caller = 0x821472D4
        struct.pack_into(">I", image, caller - BASE, bl(caller, PRINT_INTRO_TEXT))
        result = scan(bytes(image))
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["candidates"][0]["caller_va"], hex(caller))
        self.assertEqual(result["candidates"][0]["target_va"], hex(PRINT_INTRO_TEXT))
        self.assertFalse(result["binary_modified"])

    def test_ignores_branch_to_another_target(self):
        image = bytearray(IMAGE_LEN)
        caller = 0x82147368
        struct.pack_into(">I", image, caller - BASE, bl(caller, 0x82012340))
        result = scan(bytes(image))
        self.assertEqual(result["candidate_count"], 0)

    def test_rejects_xex_or_wrong_size_input(self):
        with self.assertRaisesRegex(ValueError, "expected mapped PE length"):
            scan(b"XEX2")

    def test_reports_candidates_as_unverified(self):
        image = bytearray(IMAGE_LEN)
        caller = 0x821472D4
        struct.pack_into(">I", image, caller - BASE, bl(caller, PRINT_INTRO_TEXT))
        result = scan(bytes(image))
        self.assertEqual(result["candidates"][0]["validation"],
                         "CANDIDATE_ONLY_REQUIRES_DISASSEMBLY")
        self.assertIn("Aligned data may resemble", result["warning"])


if __name__ == "__main__":
    unittest.main()
