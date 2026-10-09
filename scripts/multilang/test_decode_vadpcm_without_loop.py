"""Testa exportação VADPCM em quadro inteiro quando apenas loop está ausente."""
import unittest

from decode_vadpcm_without_loop import frame_complete_no_loop
from test_reconstruct_ptbr_audio_from_xex import VoiceReconstructionTests


class FrameWithoutLoopTests(unittest.TestCase):
    def fixture(self):
        target,mask,base,at=VoiceReconstructionTests().fixture()
        return target,mask,base,at

    def test_incomplete_loop_allows_full_frame_stream(self):
        target,mask,base,at=self.fixture()
        mask[base+0x150+12]=0
        found=frame_complete_no_loop(target,mask)
        self.assertEqual(len(found),1)
        self.assertEqual((found[0]['bank'],found[0]['physical_slot']),('08','04'))
        self.assertEqual(found[0]['pcm_samples'],16)
        self.assertFalse(found[0]['duration_is_exact_gameplay'])

    def test_complete_loop_skips_diagnostic(self):
        target,mask,base,at=self.fixture()
        self.assertEqual(frame_complete_no_loop(target,mask),[])

    def test_missing_frame_byte_blocks_diagnostic(self):
        target,mask,base,at=self.fixture()
        mask[base+0x150+12]=0
        mask[at+1]=0
        self.assertEqual(frame_complete_no_loop(target,mask),[])

    def test_missing_coefficient_blocks_diagnostic(self):
        target,mask,base,at=self.fixture()
        mask[base+0x150+12]=0
        mask[base+0x100+10]=0
        self.assertEqual(frame_complete_no_loop(target,mask),[])

    def test_missing_descriptor_blocks_diagnostic(self):
        target,mask,base,at=self.fixture()
        mask[base+0x150+12]=0
        mask[base+0xC0+16]=0
        self.assertEqual(frame_complete_no_loop(target,mask),[])

if __name__=='__main__':
    unittest.main()
