import unittest

from scan_vadpcm_partial import (
    book_shard_candidates,
    frame_score,
    scan_fragments,
    valid_header,
)


class VadpcmHeuristicsTests(unittest.TestCase):
    def test_header_decoding(self):
        self.assertTrue(valid_header(0x40))
        self.assertTrue(valid_header(0x31))
        self.assertFalse(valid_header(0x42))
        self.assertFalse(valid_header(0xD0))

    def test_perfect_frames(self):
        block = bytes([0x31]) + bytes([0xFF] * 8)
        data = block * 100
        score = frame_score(data, 0, len(data), 0)
        self.assertEqual(score['frames'], 100)
        self.assertEqual(score['valid'], 100)
        self.assertEqual(score['fraction'], 1.0)

    def test_known_run_phase(self):
        noise = bytes([0xFF]) * 4
        block = bytes([0x31]) + bytes([0xFF] * 8)
        data = noise + block * 100
        matches = scan_fragments(data, bytearray([1] * len(data)),
                                 start=0, stop=len(data), min_run=512)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['best_phase'], 4)
        self.assertEqual(matches[0]['full_frames'], 100)
        self.assertTrue(matches[0]['perfect'])

    def test_missing_data_breaks_run(self):
        block = bytes([0x21]) + bytes([0xFF] * 8)
        data = block * 80 + bytes([0] * 20) + block * 80
        mask = bytearray([1] * len(data))
        mask[720:740] = bytes(20)
        matches = scan_fragments(data, mask, 0, len(data), 512)
        self.assertEqual(len(matches), 2)
        self.assertEqual([x['full_frames'] for x in matches], [80, 80])
        self.assertTrue(all(x['perfect'] for x in matches))

    def test_incomplete_book_stays_incomplete(self):
        bank = bytearray(256)
        known = bytearray(256)
        for i in range(64):
            bank[8 + i] = (i % 128) + 1
            known[8 + i] = 1
        known[8 + 63] = 0
        found = book_shard_candidates(bank, known, 0, len(bank))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['offset'], hex(8))
        self.assertEqual(found[0]['known_bytes'], 63)
        self.assertEqual(found[0]['unknown_byte_positions'], [63])
        self.assertFalse(found[0]['fully_recoverable'])


if __name__ == '__main__':
    unittest.main()
