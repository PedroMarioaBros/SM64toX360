from pathlib import Path
import struct, hashlib, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def u32(b,o): return struct.unpack_from('>I', b, o)[0]
def crypt(key,data):
    dec=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).decryptor()
    return dec.update(data)+dec.finalize()

def extract(path,out):
    x=Path(path).read_bytes()
    assert x[:4]==b'XEX2'
    header=u32(x,8); sec=u32(x,16)
    key=crypt(bytes(16),x[sec+0x150:sec+0x160])
    packed=crypt(key,x[header:])
    # This exact executable uses BASIC compression. The project packer records
    # its size/zero descriptors at 0x19fc..0x1a14.
    desc=[]
    for off in range(0x19fc,0x1a14,8):
        size,zero=struct.unpack_from('>II',x,off)
        desc.append((size,zero))
    pos=0; mapped=bytearray()
    for size,zero in desc:
        mapped += packed[pos:pos+size]; pos += size
        mapped += bytes(zero)
    if pos != len(packed):
        raise SystemExit(f'packed bytes left: {len(packed)-pos}')
    Path(out).write_bytes(mapped)
    print(Path(path).name, 'header',hex(header),'security',hex(sec),'descriptors',desc)
    print('mapped',len(mapped),'sha256',hashlib.sha256(mapped).hexdigest())

if __name__=='__main__': extract(sys.argv[1],sys.argv[2])
