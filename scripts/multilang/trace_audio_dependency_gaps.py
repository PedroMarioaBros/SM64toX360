#!/usr/bin/env python3
"""Auditoria de dependências de bytes ausentes no BPS (sem inferir conteúdo).

Cada byte do alvo é marcado com seu deslocamento na ROM fonte caso provenha de
SourceRead/SourceCopy/TargetCopy sobre origem; TargetRead fica sem dependência.
Nenhum byte desconhecido é substituído. Entradas do port XEX são condicionais
à equivalência com a ROM de origem, cujo CRC integral não foi confirmado.
"""
import argparse
import hashlib
import json
import struct
from array import array
from collections import Counter
from pathlib import Path

from audit_bps_xex_overlap import patch_data, read_varint, read_xex_pe
from reconstruct_ptbr_audio_from_xex import (
    read_patch, SRC_CTL, SRC_TBL, DST_CTL, DST_TBL,
    CTL_BYTES, TBL_BYTES, PE_CTL, PE_TBL,
)

TBL_TOTAL = 0x21D300


def source_offset_map(patch):
    """Returns the absolute ROM source byte offset for each target byte.

    Sentinel -1 means a literal TargetRead. For source-originated bytes, a
    nonnegative integer is retained across TargetCopy, including overlap.
    """
    if patch[:4] != b'BPS1' or len(patch) < 16:
        raise ValueError('cabeçalho BPS inválido')
    source_size, pos = read_varint(patch, 4)
    target_size, pos = read_varint(patch, pos)
    metadata_size, pos = read_varint(patch, pos)
    pos += metadata_size
    if pos > len(patch) - 12:
        raise ValueError('metadados BPS fora do arquivo')
    origin = array('i', [-1]) * target_size
    current = from_source = from_target = 0
    while pos < len(patch) - 12:
        instruction, pos = read_varint(patch, pos)
        mode, size = instruction & 3, (instruction >> 2) + 1
        if current + size > target_size:
            raise ValueError('ação BPS ultrapassa alvo')
        if mode == 0:
            if current + size > source_size:
                raise ValueError('SourceRead fora da ROM')
            origin[current:current+size] = array('i', range(current, current+size))
        elif mode == 1:
            if pos + size > len(patch) - 12:
                raise ValueError('TargetRead truncado')
            pos += size
        elif mode == 2:
            delta, pos = read_varint(patch, pos)
            from_source += -(delta >> 1) if delta & 1 else delta >> 1
            if from_source < 0 or from_source + size > source_size:
                raise ValueError('SourceCopy fora da ROM')
            origin[current:current+size] = array('i', range(from_source, from_source+size))
            from_source += size
        else:
            delta, pos = read_varint(patch, pos)
            from_target += -(delta >> 1) if delta & 1 else delta >> 1
            if from_target < 0 or from_target >= current:
                raise ValueError('TargetCopy fora do prefixo')
            if from_target + size <= current:
                origin[current:current+size] = origin[from_target:from_target+size]
            else:
                for i in range(size):
                    origin[current+i] = origin[from_target+i]
            from_target += size
        current += size
    if current != target_size or pos != len(patch)-12:
        raise ValueError('BPS não consumido integralmente')
    return origin


def contiguous_runs(known, begin, end):
    i = begin
    while i < end:
        if known[i]:
            i += 1
            continue
        start = i
        while i < end and not known[i]:
            i += 1
        yield start, i


def origin_segments(origin, begin, end):
    """Groups increasing one-byte source references, without hiding jumps."""
    items = []
    i = begin
    while i < end:
        s = origin[i]
        j = i+1
        while j < end and origin[j] == origin[j-1]+1:
            j += 1
        items.append({'target_offset': hex(i), 'bytes': j-i,
                      'source_start': None if s < 0 else hex(s),
                      'source_end_exclusive': None if s < 0 else hex(origin[j-1]+1)})
        i = j
    return items


def audit_gaps(known, origin, begin, end, source_ctl_range, source_tbl_range):
    origin_counts = Counter()
    spans = []
    for begin_run, end_run in contiguous_runs(known, begin, end):
        dependencies = origin_segments(origin, begin_run, end_run)
        for at in range(begin_run, end_run):
            s=origin[at]
            if s < 0:
                origin_counts['unexpected_no_source_ref'] += 1
            elif source_ctl_range[0] <= s < source_ctl_range[1]:
                origin_counts['inside_source_ctl'] += 1
            elif source_tbl_range[0] <= s < source_tbl_range[1]:
                origin_counts['inside_source_tbl'] += 1
            else:
                origin_counts['outside_source_audio'] += 1
        spans.append({
            'target_start':hex(begin_run), 'target_end_exclusive':hex(end_run),
            'bytes':end_run-begin_run, 'source_spans':dependencies,
        })
    return {
        'start':hex(begin), 'end_exclusive':hex(end),
        'total_bytes':end-begin, 'known_bytes':sum(known[begin:end]),
        'unknown_bytes':(end-begin)-sum(known[begin:end]),
        'unknown_runs':len(spans),
        'unknown_source_classification':dict(origin_counts),
        'missing_spans':spans,
    }


def audit(patch, pe):
    target, known = read_patch(patch, pe)
    origin = source_offset_map(patch)
    assert len(origin) == len(target) == len(known)
    ctl_range=(SRC_CTL,SRC_CTL+CTL_BYTES)
    tbl_range=(SRC_TBL,SRC_TBL+TBL_BYTES)
    ctl = audit_gaps(known, origin, DST_CTL, DST_TBL, ctl_range, tbl_range)
    tbl = audit_gaps(known, origin, DST_TBL, DST_TBL+TBL_TOTAL,
                     ctl_range, tbl_range)
    banks={}
    for name in (8,10):
        ctl_off,ctl_size=struct.unpack_from('>II',target,DST_CTL+4+name*8)
        tbl_off,tbl_size=struct.unpack_from('>II',target,DST_TBL+4+name*8)
        banks[f'{name:02X}']={
            'ctl':audit_gaps(known,origin,DST_CTL+ctl_off,
                             DST_CTL+ctl_off+ctl_size,ctl_range,tbl_range),
            'tbl':audit_gaps(known,origin,DST_TBL+tbl_off,
                             DST_TBL+tbl_off+tbl_size,ctl_range,tbl_range),
        }
    return {
        'status':'GAPS_TRACED_NO_MISSING_SOURCE_BYTES_RECONSTRUCTED',
        'input':{
            'bps_sha256':hashlib.sha256(patch).hexdigest(),
            'mapped_pe_sha256':hashlib.sha256(pe).hexdigest(),
            'source_crc32_still_unverified':True,
        },
        'source_audio_ranges':{'ctl':[hex(v) for v in ctl_range],
                               'tbl':[hex(v) for v in tbl_range]},
        'port_asset_padding':{
            'ctl_last_64_bytes_hex':pe[PE_CTL+0x17E00:PE_CTL+0x17E40].hex(),
            'tbl_last_16_bytes_hex':pe[PE_TBL+0x21D2F0:PE_TBL+0x21D300].hex(),
            'note':'Padding recuperado do XEX condicionalmente, não de ROM N64 CRC-validada',
        },
        'target_known_bytes':sum(known), 'target_total_bytes':len(known),
        'target_ctl':ctl, 'target_tbl':tbl, 'voice_banks':banks,
        'limitations':[
          'Deslocamentos fonte fora do intervalo de áudio não estão recuperados.',
          'Não reconstruir conteúdos das 841 lacunas CTL e 316 lacunas TBL restantes.',
          'Offsets são do arquivo BPS alvo ou da ROM fonte, não endereços runtime.',
          'Nenhum WAV novo, nenhum XEX ou ROM final é produzido.',
        ],
    }


def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('patch_zip',type=Path)
    args.add_argument('xex_zip',type=Path)
    args.add_argument('--report',type=Path)
    opt=args.parse_args()
    patch,_,_=patch_data(opt.patch_zip)
    _,pe=read_xex_pe(opt.xex_zip)
    result=audit(patch,pe)
    if opt.report:
        opt.report.parent.mkdir(parents=True,exist_ok=True)
        opt.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({
        'target_known_bytes':result['target_known_bytes'],
        'target_ctl':{k:result['target_ctl'][k] for k in
                      ('unknown_bytes','unknown_runs','unknown_source_classification')},
        'target_tbl':{k:result['target_tbl'][k] for k in
                      ('unknown_bytes','unknown_runs','unknown_source_classification')},
        'voice_banks':{b:{
          t:{k:result['voice_banks'][b][t][k] for k in ('unknown_bytes','unknown_runs')}
          for t in ('ctl','tbl')} for b in result['voice_banks']},
    },ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
