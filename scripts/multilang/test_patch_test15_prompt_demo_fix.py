import struct
import unittest

from patch_test15_prompt_demo_fix import (
    BASE, PE_LEN, CALLSITE, CALLSITE_RVA, ORIGINAL_CALL,
    MAIN_WRAPPER_NULL_BRANCH, MAIN_WRAPPER_NULL_BRANCH_RVA,
    ORIGINAL_NULL_BRANCH, NOP, PROMPT_WRAPPER, PROMPT_WRAPPER_RVA,
    PROMPT_CAVE_START, PROMPT_CAVE_END, PRINT_CENTER, PRINT_INTRO_TEXT,
    branch_dest, build_prompt_wrapper, patch, sha,
)


def get_word(data, offset):
    return struct.unpack_from(">I", data, offset)[0]


def code_word(stub, word_offset):
    return get_word(stub, word_offset * 4)


def cond_dest(pc, instruction):
    if (instruction & 0xFFFF0000) != 0x41820000:
        raise ValueError("not a beq instruction")
    displacement = instruction & 0xFFFC
    if displacement & 0x8000:
        displacement -= 0x10000
    return pc + displacement


def synthetic_test14_pe():
    data = bytearray(PE_LEN)
    struct.pack_into(">I", data, CALLSITE_RVA, ORIGINAL_CALL)
    struct.pack_into(">I", data, MAIN_WRAPPER_NULL_BRANCH_RVA, ORIGINAL_NULL_BRANCH)
    # Cave and preservation ranges start as zero-filled for this synthetic fixture.
    return data


class Test15PromptPatch(unittest.TestCase):
    def test_wrapper_size_and_targets(self):
        stub = build_prompt_wrapper()
        self.assertEqual(len(stub), 124)
        self.assertEqual(sha(stub), "2b3c39d949055c0a21584ad3d248cd5c55b3fb72dae459cd62d53bbc8e0eb913")
        self.assertEqual(cond_dest(PROMPT_WRAPPER + 6*4, code_word(stub, 6)), PROMPT_WRAPPER + 26*4)
        self.assertEqual(cond_dest(PROMPT_WRAPPER + 9*4, code_word(stub, 9)), PROMPT_WRAPPER + 26*4)
        self.assertEqual(branch_dest(PROMPT_WRAPPER + 20*4, code_word(stub, 20)), PRINT_CENTER)
        self.assertEqual(branch_dest(PROMPT_WRAPPER + 24*4, code_word(stub, 24)), PRINT_CENTER)
        self.assertEqual(branch_dest(PROMPT_WRAPPER + 25*4, code_word(stub, 25)), PROMPT_WRAPPER + 27*4)
        self.assertEqual(branch_dest(PROMPT_WRAPPER + 26*4, code_word(stub, 26)), PRINT_INTRO_TEXT)

    def test_candidate_patch_and_preservation(self):
        source = synthetic_test14_pe()
        final, report = patch(bytes(source), strict=False)
        self.assertEqual(len(final), PE_LEN)
        self.assertEqual(branch_dest(CALLSITE, get_word(final, CALLSITE_RVA)), PROMPT_WRAPPER)
        self.assertEqual(get_word(final, MAIN_WRAPPER_NULL_BRANCH_RVA), NOP)
        self.assertEqual(final[PROMPT_CAVE_START:PROMPT_CAVE_START+124], build_prompt_wrapper())
        self.assertEqual(final[0x1040100:0x10406F0], source[0x1040100:0x10406F0])
        self.assertEqual(final[0x1040080:0x1040088], source[0x1040080:0x1040088])
        self.assertEqual(final[0xCD128:0xCD12C], source[0xCD128:0xCD12C])
        self.assertTrue(report["selector_centering_unchanged"])
        self.assertEqual(report["hardware_test"], "PENDING")

    def test_strict_mode_rejects_noncanonical_source(self):
        with self.assertRaisesRegex(ValueError, "exact mapped TEST14"):
            patch(bytes(synthetic_test14_pe()))

    def test_reject_wrong_callsite(self):
        source = synthetic_test14_pe()
        struct.pack_into(">I", source, CALLSITE_RVA, NOP)
        with self.assertRaisesRegex(ValueError, "remaining print_intro_text call"):
            patch(bytes(source), strict=False)

    def test_reject_occupied_cave(self):
        source = synthetic_test14_pe()
        source[PROMPT_CAVE_START] = 1
        with self.assertRaisesRegex(ValueError, "cave is not completely zero-filled"):
            patch(bytes(source), strict=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
