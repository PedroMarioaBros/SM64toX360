import unittest

from inspect_xex_sound_layout import (
    BOOK_MAGIC, find_books, frame_window, masked_book_matches,
)


class XexSoundLayoutTests(unittest.TestCase):
    def test_complete_coefficients(self):
        payload = bytes(range(1,65))
        pe = bytes(16) + BOOK_MAGIC + payload + bytes(128)
        matches = find_books(pe, start=0)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], (16, payload))

    def test_alignment_filters_candidates(self):
        payload = bytes(range(1,65))
        pe = bytes(17) + BOOK_MAGIC + payload + bytes(128)
        self.assertEqual(find_books(pe, start=0), [])

    def test_masked_match_does_not_fill_missing_byte(self):
        coeff = bytes(range(1,65))
        data = bytearray(coeff)
        mask = bytearray([1]*64)
        mask[63] = 0
        found = masked_book_matches(data, mask,
                                    [{'offset': '0x0'}], [(0x100, coeff)])
        self.assertEqual(found, [{
            'patch_coeff_offset':'0x0', 'xex_book_offset':'0x100'
        }])
        modified = bytearray(coeff)
        modified[21] ^= 0x80
        self.assertEqual(masked_book_matches(modified, mask,
                                            [{'offset':'0x0'}],
                                            [(0x100, coeff)]), [])

    def test_frame_window(self):
        payload = (bytes([0x31]) + bytes(range(1, 9))) * 64
        result = frame_window(payload, 0)
        self.assertEqual(result['matching_headers'], 64)
        self.assertEqual(result['nonzero_bytes'], 576)
        self.assertEqual(result['frame_count'], 64)


if __name__ == '__main__':
    unittest.main()
