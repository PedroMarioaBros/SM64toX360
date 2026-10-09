#!/usr/bin/env python3
"""Audita correspondências byte-exatas entre áudio de patch BPS e XEX Xbox 360.

Apenas analisa: não reconstrói ROM, não publica amostras de áudio, não modifica XEX.
A ausência de hits NÃO demonstra ausência das vozes/áudio em outra codificação.
Dependências SourceRead/SourceCopy permanecem desconhecidas sem a ROM fonte.
"""
import argparse
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

CTL_START = 0x57F8D0
TBL_START = 0x597710
TBL_SCAN_END = 0x794970  # fronteira exploratória, NÃO delimitação comprovada


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_varint(buf, pos):
    value, scale = 0, 1
    while True:
        if pos >= len(buf):
            raise ValueError('BPS varint truncado')
        byte = buf[pos]
        pos += 1
        value += (byte & 127) * scale
        if byte & 128:
            return value, pos
        scale <<= 7
        value += scale


def patch_data(path):
    data = path.read_bytes()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith('.bps')]
            if len(names) != 1:
                raise ValueError('ZIP deve conter exatamente um BPS')
            return z.read(names[0]), sha256(data), names[0]
    return data, sha256(data), path.name


def bps_known_map(patch):
    if patch[:4] != b'BPS1' or len(patch) < 16:
        raise ValueError('BPS inválido')
    if zlib.crc32(patch[:-4]) != struct.unpack_from('<I', patch, len(patch)-4)[0]:
        raise ValueError('CRC32 do BPS inválido')
    source_size, pos = read_varint(patch, 4)
    target_size, pos = read_varint(patch, pos)
    meta_size, pos = read_varint(patch, pos)
    pos += meta_size
    if pos > len(patch)-12:
        raise ValueError('metadados BPS truncados')
    known = bytearray(target_size)
    value = bytearray(target_size)
    cursor = source_cursor = target_cursor = 0
    while pos < len(patch)-12:
        instruction, pos = read_varint(patch, pos)
        mode, count = instruction & 3, (instruction >> 2) + 1
        if cursor + count > target_size:
            raise ValueError('ação BPS excede destino')
        if mode == 0:
            if cursor + count > source_size:
                raise ValueError('SourceRead excede fonte')
        elif mode == 1:
            if pos + count > len(patch)-12:
                raise ValueError('TargetRead truncado')
            value[cursor:cursor+count] = patch[pos:pos+count]
            known[cursor:cursor+count] = b'\x01' * count
            pos += count
        else:
            delta, pos = read_varint(patch, pos)
            delta = -(delta >> 1) if delta & 1 else delta >> 1
            if mode == 2:
                source_cursor += delta
                if source_cursor < 0 or source_cursor + count > source_size:
                    raise ValueError('SourceCopy fora da fonte')
                source_cursor += count
            else:
                target_cursor += delta
                if target_cursor < 0 or target_cursor >= cursor:
                    raise ValueError('TargetCopy fora do destino anterior')
                if target_cursor + count <= cursor:
                    value[cursor:cursor+count] = value[target_cursor:target_cursor+count]
                    known[cursor:cursor+count] = known[target_cursor:target_cursor+count]
                else:
                    for j in range(count):
                        value[cursor+j] = value[target_cursor+j]
                        known[cursor+j] = known[target_cursor+j]
                target_cursor += count
        cursor += count
    if cursor != target_size or pos != len(patch)-12:
        raise ValueError('BPS não consumido integralmente')
    return source_size, target_size, value, known


def read_xex_pe(path):
    raw = path.read_bytes()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith('.xex')]
            if len(names) != 1:
                raise ValueError('ZIP deve conter exatamente um XEX')
            raw = z.read(names[0])
    if raw[:4] != b'XEX2':
        raise ValueError('Não é XEX2')
    u32 = lambda offset: struct.unpack_from('>I', raw, offset)[0]
    opt_count = u32(0x14)
    file_info = next((u32(0x18+j*8+4) for j in range(opt_count)
                      if u32(0x18+j*8) == 0x3FF), None)
    if file_info is None:
        raise ValueError('Header FileFormatInfo ausente')
    info_size, encryption, compression = struct.unpack_from('>IHH', raw, file_info)
    if info_size != 16 or compression != 1 or encryption != 1:
        raise ValueError('Suporte restrito a XEX Basic + AES-CBC (encrypted)')
    size, zeros = struct.unpack_from('>II', raw, file_info+8)
    basefile = u32(8)
    security = u32(16)
    if size % 16 or basefile + size != len(raw):
        raise ValueError('Bloco Basic inesperado')
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    def aes_decrypt(key, encrypted):
        dec = Cipher(algorithms.AES(key), modes.CBC(bytes(16))).decryptor()
        return dec.update(encrypted) + dec.finalize()
    key = aes_decrypt(bytes(16), raw[security+0x150:security+0x160])
    pe = aes_decrypt(key, raw[basefile:]) + bytes(zeros)
    if pe[:2] != b'MZ' or pe[struct.unpack_from('<I', pe, 0x3C)[0]:][:4] != b'PE\x00\x00':
        raise ValueError('PE de XEX inválido; outra chave/formato?')
    return raw, pe


def known_runs(known, a, b, min_length):
    i = a
    while i < b:
        if known[i] == 0:
            i += 1
            continue
        start = i
        while i < b and known[i]:
            i += 1
        if i-start >= min_length:
            yield start, i


def coverage(known, a, b):
    return {'start':hex(a),'end_exclusive':hex(b),'bytes':b-a,
            'known_bytes':sum(known[a:b]),'source_dependent_bytes':(b-a)-sum(known[a:b])}


def probe(pe, value, known, a, b, length, stride):
    probes = matches = 0
    hits = []
    for start, end in known_runs(known, a, b, length):
        for offset in range(start, end-length+1, stride):
            probes += 1
            at = pe.find(value[offset:offset+length])
            if at >= 0:
                matches += 1
                hits.append({'bps_target':hex(offset), 'pe_offset':hex(at)})
    return {'fragment_bytes':length, 'stride_bytes':stride,
            'probes':probes, 'exact_matches':matches, 'first_hits':hits[:10]}


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('bps_or_zip', type=Path)
    args.add_argument('xex_or_zip', type=Path)
    args.add_argument('--report', type=Path)
    options = args.parse_args()
    patch, zip_sha, patch_name = patch_data(options.bps_or_zip)
    source_size, target_size, values, known = bps_known_map(patch)
    raw, pe = read_xex_pe(options.xex_or_zip)
    if target_size < TBL_SCAN_END:
        raise ValueError('patch menor que intervalos de áudio auditados')
    regions = {'ctl':(CTL_START,TBL_START), 'tbl_prefix':(TBL_START,0x60C040),
               'tbl_candidate_data':(0x60C040,TBL_SCAN_END)}
    report = {
        'status':'FORENSIC_ONLY_NO_AUDIO_EXTRACTED',
        'patch':{'filename':patch_name,'archive_sha256':zip_sha,'bps_sha256':sha256(patch),
                 'source_size':source_size,'target_size':target_size,
                 'source_crc32':f'{struct.unpack_from("<I",patch,len(patch)-12)[0]:08x}',
                 'target_crc32':f'{struct.unpack_from("<I",patch,len(patch)-8)[0]:08x}'},
        'xex':{'sha256':sha256(raw),'bytes':len(raw),'mapped_pe_sha256':sha256(pe),'mapped_pe_bytes':len(pe)},
        'regions':{name:coverage(known,*limits) for name,limits in regions.items()},
        'probes':{str(n):probe(pe,values,known,CTL_START,TBL_SCAN_END,n,2048) for n in (16,32,64)},
        'notes':[ 'Região tbl_candidate_data é exploratória, não fim do TBL validado.',
                 'Não reutilizar bytes do PE como fonte BPS sem equivalência de formato e proveniência comprovada.',
                 'Ausência de matches nos trechos modificados não prova ausência de áudio original do XEX.',
                 'Sem ROM fonte: bytes dependentes permanecem desconhecidos; nenhum banco/voz foi reconstruído.' ]}
    payload = json.dumps(report,ensure_ascii=False,indent=2) + '\n'
    if options.report:
        options.report.parent.mkdir(parents=True,exist_ok=True)
        options.report.write_text(payload,encoding='utf-8')
    print(payload)

if __name__ == '__main__':
    main()
