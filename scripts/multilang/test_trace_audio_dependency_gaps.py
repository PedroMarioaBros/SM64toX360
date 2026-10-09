"""Testes de origem BPS com dados artificiais, sem ROM/XEX."""
import struct
import unittest
import zlib

from trace_audio_dependency_gaps import (
    source_offset_map, origin_segments, audit_gaps, contiguous_runs,
)


def varint(n):
    result=bytearray()
    while True:
        byte=n&127
        n>>=7
        if n==0:
            result.append(byte|128)
            return bytes(result)
        result.append(byte)
        n-=1


def instruction(mode, size):
    return varint(((size-1)<<2)|mode)


def toy_patch():
    data=bytearray(b'BPS1')
    data+=varint(12)+varint(10)+varint(0)
    data+=instruction(0,4)  # SourceRead -> 0,1,2,3
    data+=instruction(1,2)+b'xx'  # TargetRead -> -1,-1
    data+=instruction(2,2)+varint(8) # SourceCopy +4 -> 4,5
    data+=instruction(3,2)+varint(0) # TargetCopy offset 0 -> 0,1
    data+=struct.pack('<III',0,0,0)
    struct.pack_into('<I',data,len(data)-4,zlib.crc32(data[:-4]))
    return bytes(data)


class TraceAudioDependencyGapsTests(unittest.TestCase):
    def test_all_bps_copy_modes_preserve_source_origin(self):
        trace=source_offset_map(toy_patch())
        self.assertEqual(list(trace),[0,1,2,3,-1,-1,4,5,0,1])

    def test_unknown_runs_source_segments(self):
        known=bytearray([1,1,0,0,1,0,0,1,1,1])
        self.assertEqual(list(contiguous_runs(known,0,len(known))),[(2,4),(5,7)])
        trace=source_offset_map(toy_patch())
        self.assertEqual(origin_segments(trace,2,4),[{
            'target_offset':'0x2','bytes':2,
            'source_start':'0x2','source_end_exclusive':'0x4'
        }])
        report=audit_gaps(known,trace,0,10,(0,4),(4,6))
        self.assertEqual(report['unknown_runs'],2)
        self.assertEqual(report['unknown_bytes'],4)
        self.assertEqual(report['unknown_source_classification'].get('inside_source_ctl'),2)
        self.assertEqual(report['unknown_source_classification'].get('inside_source_tbl'),1)
        self.assertEqual(report['unknown_source_classification'].get('unexpected_no_source_ref'),1)

    def test_targetcopy_overlap(self):
        patch=bytearray(b'BPS1')
        patch+=varint(8)+varint(8)+varint(0)
        patch+=instruction(0,2)
        patch+=instruction(3,6)+varint(0)
        patch+=struct.pack('<III',0,0,0)
        struct.pack_into('<I',patch,len(patch)-4,zlib.crc32(patch[:-4]))
        self.assertEqual(list(source_offset_map(bytes(patch))),[0,1,0,1,0,1,0,1])

    def test_reject_copy_invalid(self):
        patch=bytearray(b'BPS1')
        patch+=varint(3)+varint(2)+varint(0)
        patch+=instruction(3,2)+varint(0)
        patch+=struct.pack('<III',0,0,0)
        struct.pack_into('<I',patch,len(patch)-4,zlib.crc32(patch[:-4]))
        with self.assertRaises(ValueError):
            source_offset_map(bytes(patch))

if __name__=='__main__':
    unittest.main()
