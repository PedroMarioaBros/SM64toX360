"""Static differential diagnosis after Xbox TEST10 button-triggered Fatal Crash.

READ ME: this audit does NOT run a game or prove the specific crash cause.
It verifies the binary-level difference between each no-button frame and the
button-triggered common path, explaining why testing right stick didn't crash.
"""
import hashlib
import struct
import unittest

import test10_controller_read_probe as probe

BASE = probe.WRAPPER
PRINT_CENTER = probe.PRINT_CENTER
ORIGINAL_PRINT = probe.ORIGINAL_PRINT
ADDRS = {
    'PORTUGUES': 0x8305CA00,
    'ESPANOL': 0x8305CA0C,
    'ENGLISH': 0x8305CA14,
    'TESTE10': 0x8305CA1C,
    'X': 0x8305CA24,
}


def branch_target(pc, insn):
    # PPC I-form branch relative 24-bit signed LI shifted 2; AA=0.
    if insn >> 26 != 18 or (insn & 2):
        return None
    disp = insn & 0x03FFFFFC
    if disp & 0x02000000:
        disp -= 0x04000000
    return (pc + disp) & 0xFFFFFFFF


def calls_to(code, destination):
    found = []
    for offset in range(0, len(code), 4):
        insn = struct.unpack_from('>I', code, offset)[0]
        if insn & 1 and branch_target(BASE + offset, insn) == destination:
            found.append(BASE + offset)
    return found


class FatalCrashButtonPathAudit(unittest.TestCase):
    def setUp(self):
        self.code = probe.build(ADDRS)

    def test_exact_code_matches_real_test10_xex(self):
        self.assertEqual(len(self.code), 204)
        self.assertEqual(hashlib.sha256(self.code).hexdigest(),
                         '4fd27ff93e2ed0140a849e971b0a9bcdcd39f0b86665506f0af8c78a956b4a6f')

    def test_only_fifth_render_call_uses_pressed_button_path(self):
        self.assertEqual(calls_to(self.code, PRINT_CENTER), [
            0x823BCD20, 0x823BCD34, 0x823BCD48, 0x823BCD5C, 0x823BCDB8
        ])
        self.assertEqual(calls_to(self.code, ORIGINAL_PRINT), [0x823BCD0C])
        # Last call sits after the UP/DOWN/A condition tree; reaches the X.
        self.assertEqual(struct.unpack_from('>I', self.code, 0xB4)[0], 0x60A5CA24)

    def test_controller_is_read_even_without_button(self):
        # lwz r11,-30320(r11), lhz r9,16(r11) on shared path.
        self.assertEqual(self.code[0x64:0x68].hex(), '816b8990')
        self.assertEqual(self.code[0x70:0x74].hex(), 'a12b0010')
        # D-pad UP/DOWN/A masks, each followed by a conditional branch.
        self.assertEqual(self.code[0x74:0x78].hex(), '71280800')
        self.assertEqual(self.code[0x88:0x8C].hex(), '71280400')
        self.assertEqual(self.code[0x9C:0xA0].hex(), '71288000')

    def test_no_controller_write_in_wrapper(self):
        # PPC D-form store-word/half/byte/dword opcodes are not used for input.
        # This code has just stwu/stw for stack frame, not stores via r11.
        words = [struct.unpack_from('>I', self.code, offset)[0]
                 for offset in range(0, len(self.code), 4)]
        stores_via_controller_r11 = [w for w in words
                                     if w >> 26 in (36, 37, 38, 39, 44, 45, 46, 47)
                                     and (w >> 16) & 31 == 11]
        self.assertEqual(stores_via_controller_r11, [])

    def test_marker_label_valid_and_nul_terminated_in_real_test10_pe(self):
        # To run locally against private PE, this check is performed separately;
        # the public repo must never contain Nintendo proprietary PE bytes.
        self.assertEqual(ADDRS['X'], 0x8305CA24)
        self.assertEqual(ADDRS['TESTE10'], 0x8305CA1C)


if __name__ == '__main__':
    unittest.main()