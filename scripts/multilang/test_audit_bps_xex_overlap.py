import unittest
import zlib
import struct
from audit_bps_xex_overlap import bps_known_map, known_runs, coverage, probe

def var(n):
    result=bytearray()
    while True:
        x=n & 127
        n >>= 7
        if n==0:
            result.append(x | 128)
            return result
        result.append(x)
        n-=1

def fixture():
    # SourceRead 4, TargetRead XYZ, TargetCopy XYZ, SourceCopy 6
    p=bytearray(b'BPS1')
    p+=var(16)+var(16)+var(0)
    p+=var((4-1)*4+0)
    p+=var((3-1)*4+1)+b'XYZ'
    p+=var((3-1)*4+3)+var(8)
    p+=var((6-1)*4+2)+var(8)
    p+=struct.pack('<II',0,0)
    p+=struct.pack('<I',zlib.crc32(p))
    return bytes(p)

class ProvenanceTest(unittest.TestCase):
    def test_copy_provenance(self):
        src,size,values,known=bps_known_map(fixture())
        self.assertEqual((src,size),(16,16))
        self.assertEqual(sum(known),6)
        self.assertEqual(bytes(values[4:10]),b'XYZXYZ')
        self.assertEqual(coverage(known,0,16)['source_dependent_bytes'],10)
        self.assertEqual(list(known_runs(known,0,16,3)),[(4,10)])
    def test_crc_guard(self):
        invalid=fixture()[:-1]+b'\0'
        with self.assertRaises(ValueError):bps_known_map(invalid)
    def test_probe_true_positive(self):
        _,_,v,k=bps_known_map(fixture())
        self.assertEqual(probe(b'123XYZXYZabc',v,k,0,16,3,3)['exact_matches'],2)
    def test_probe_false_positive_guard(self):
        _,_,v,k=bps_known_map(fixture())
        self.assertEqual(probe(b'abcQRSTUVW',v,k,0,16,3,3)['exact_matches'],0)

if __name__=='__main__':unittest.main()
