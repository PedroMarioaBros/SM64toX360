import struct
import unittest

from reconstruct_ptbr_audio_from_xex import (
    DST_CTL, DST_TBL, collect, decode_vadpcm, NAMES,
)

class VoiceReconstructionTests(unittest.TestCase):
    def fixture(self):
        target = bytearray(DST_TBL + 0x4000)
        target[DST_CTL:DST_CTL+4] = b"\0\x01\0\x26"
        target[DST_TBL:DST_TBL+4] = b"\0\x02\0\x26"
        cbank08 = DST_CTL + 0x140
        cbank0a = DST_CTL + 0x540
        tbank08 = DST_TBL + 0x140
        for bank, c_off, t_off, n in ((8,0x140,0x140,27),
                                      (10,0x540,0x940,24)):
            struct.pack_into(">II",target,DST_CTL+4+bank*8,c_off,0x400)
            struct.pack_into(">II",target,DST_TBL+4+bank*8,t_off,0x800)
            struct.pack_into(">I",target,DST_CTL+c_off,n)
        base = cbank08 + 16
        struct.pack_into(">I",target,base+4+4*4,0x80)  # physical slot 04
        struct.pack_into(">BBBBI",target,base+0x80,0,0,127,208,0x200)
        struct.pack_into(">If",target,base+0x80+16,0xC0,1.5)
        struct.pack_into(">IIIII",target,base+0xC0,0,0,0x150,0x100,9)
        struct.pack_into(">II",target,base+0x100,2,2)
        struct.pack_into(">IIiI",target,base+0x150,0,17,0,0)
        target[tbank08:tbank08+9] = b"\0" + b"\x11"*8
        mask=bytearray(b"\x01"*len(target))
        return target,mask,base,tbank08

    def test_decoder_zero_coefficients(self):
        book=struct.pack(">II",2,2)+bytes(64)
        samples=decode_vadpcm(b"\0"+b"\x11"*8,book)
        self.assertEqual(samples, [1]*16)

    def test_true_source_tracking(self):
        target,mask,base,at=self.fixture()
        rows=collect(target,mask)
        eligible=[r for r in rows if r.get("ready")]
        self.assertEqual(len(eligible),1)
        self.assertEqual((eligible[0]["bank"],eligible[0]["slot"]),("08","04"))
        self.assertEqual(eligible[0]["pcm_samples"],16)

    def test_missing_sample_byte_blocks_export(self):
        target,mask,base,at=self.fixture()
        mask[at+3]=0
        self.assertFalse(any(r.get("ready") for r in collect(target,mask)))

    def test_missing_book_coefficient_blocks_export(self):
        target,mask,base,at=self.fixture()
        mask[base+0x100+9]=0
        self.assertFalse(any(r.get("ready") for r in collect(target,mask)))

    def test_physical_slot_03_is_null(self):
        target,mask,base,at=self.fixture()
        rows=collect(target,mask)
        null=[r for r in rows if r["bank"]=="0A" and r["slot"]=="03"]
        self.assertEqual(len(null),1)
        self.assertTrue(null[0]["empty"])
        self.assertIsNone(null[0]["name"])

    def test_instrument_event_labels(self):
        self.assertEqual(len(NAMES[8]),27)
        self.assertEqual(len(NAMES[10]),24)
        self.assertEqual(NAMES[8][4],"yahoo")
        self.assertEqual(NAMES[10][9],"punch_yah")

if __name__=="__main__":
    unittest.main()
