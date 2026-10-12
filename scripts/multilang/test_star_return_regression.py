import unittest
from audit_star_return_regression import (
    compare_pe, CALL_OFFSET, CODE_BEGIN, CODE_END, ORIGINAL_BL, CREDITS_BL
)


def fixtures():
    expected = bytearray(CODE_END + 16)
    altered = bytearray(CODE_END + 16)
    expected[CALL_OFFSET:CALL_OFFSET+4] = ORIGINAL_BL
    altered[CALL_OFFSET:CALL_OFFSET+4] = CREDITS_BL
    altered[CODE_BEGIN:CODE_BEGIN+4] = bytes.fromhex("7c0802a6")
    return expected, altered


class StarReturnABAuditTests(unittest.TestCase):
    def test_only_hook_and_reserved_gate_are_allowed(self):
        expected, altered = fixtures()
        report = compare_pe(expected, altered)
        self.assertTrue(report["no_other_pe_differences"])
        self.assertEqual(report["modified_bytes"], 8)
        self.assertEqual(report["experimental_code"]["reserved_bytes"], 264)
        self.assertEqual(report["control_pe_sha256"], report["restored_pe_sha256"])
        self.assertEqual(report["hardware_result"], "PENDING")

    def test_unexpected_gameplay_change_blocks_validation(self):
        expected, altered = fixtures()
        altered[0x100] = 1
        with self.assertRaisesRegex(ValueError, "fora do hook"):
            compare_pe(expected, altered)

    def test_missing_original_call_blocks_validation(self):
        expected, altered = fixtures()
        expected[CALL_OFFSET:CALL_OFFSET+4] = bytes(4)
        with self.assertRaisesRegex(ValueError, "chamada original"):
            compare_pe(expected, altered)

    def test_unknown_nonzero_original_code_cave_blocks_validation(self):
        expected, altered = fixtures()
        expected[CODE_END-1] = 1
        with self.assertRaisesRegex(ValueError, "não está vazia"):
            compare_pe(expected, altered)


if __name__ == "__main__":
    unittest.main()
