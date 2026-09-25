from pathlib import Path
import struct,subprocess,hashlib,json
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
ROOT=Path(__file__).resolve().parent.parent
orig=(ROOT/'inspect/sm64.xex').read_bytes();base=(ROOT/'inspect/translated-base.bin').read_bytes()
s=struct.unpack_from('>I',orig,16)[0];header=struct.unpack_from('>I',orig,8)[0]
def crypt(key,data,encrypt=False):
 c=Cipher(algorithms.AES(key),modes.CBC(bytes(16)))
 return (c.encryptor() if encrypt else c.decryptor()).update(data)
key=crypt(bytes(16),orig[s+0x150:s+0x160])
packed=bytearray();pos=0
for off in range(0x19fc,0x1a14,8):
 size,zero=struct.unpack_from('>II',orig,off)
 packed+=base[pos:pos+size];pos+=size
 assert base[pos:pos+zero]==bytes(zero),'changed zero-compressed memory'
 pos+=zero
assert pos==len(base)
assert len(packed)==len(orig)-header
(ROOT/'inspect/intermediate.xex').write_bytes(orig[:header]+crypt(key,bytes(packed),True))
tool=ROOT/'inspect/xextool/build/XexTool'
# Repack using the independent XEX implementation, which rebuilds chained page
# hashes and signs devkit homebrew headers using its standard development key.
for args in [['-e','u','-o',str(ROOT/'inspect/ptbr-unencrypted.xex'),str(ROOT/'inspect/intermediate.xex')],['-e','e','-o',str(ROOT/'sm64-ptbr-teste.xex'),str(ROOT/'inspect/ptbr-unencrypted.xex')]]:
 r=subprocess.run([str(tool),*args],capture_output=True,text=True);print(r.stdout);print(r.stderr);assert r.returncode==0
