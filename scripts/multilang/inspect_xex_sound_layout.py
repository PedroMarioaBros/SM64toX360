#!/usr/bin/env python3
"""Inspeciona estruturas VADPCM do PE Xbox 360 e cruza livros parciais do BPS.

Somente analise: nao edita/gera executaveis, audio ou ROM. Enderecos sao
offsets do mapped PE ou da ROM-alvo BPS, nao ponteiros runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path

from audit_bps_xex_overlap import bps_known_map, patch_data, read_xex_pe
from scan_vadpcm_partial import book_shard_candidates, valid_header

BOOK_MAGIC = bytes.fromhex('0000000200000002')
PE_DATA_START = 0x3C0000
VOICE_SAMPLE_ANCHOR = 0xA3FB10
CANONICAL_PE_SHA = 'bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56'


def find_books(pe, start=PE_DATA_START):
    """Janelas com metadados (order=2, predictors=2) e 64 bytes nao vazios."""
    matches = []
    cursor = start
    while True:
        pos = pe.find(BOOK_MAGIC, cursor)
        if pos < 0:
            break
        cursor = pos + 1
        if pos % 8 or pos + 72 > len(pe):
            continue
        coeffs = pe[pos + 8: pos + 72]
        nonzero_pairs = sum(coeffs[i] != 0 or coeffs[i+1] != 0
                            for i in range(0, 64, 2))
        if nonzero_pairs >= 30:
            matches.append((pos, coeffs))
    return matches


def masked_book_matches(partial_data, provenance, fragments, pe_books):
    """Compara apenas bytes conhecidos; bytes fonte-dependentes nao sao zeros."""
    matches = []
    for fragment in fragments:
        offset = int(fragment['offset'], 16)
        mask = provenance[offset:offset + 64]
        payload = partial_data[offset:offset + 64]
        for at, coeffs in pe_books:
            if all(payload[i] == coeffs[i] for i in range(64) if mask[i]):
                matches.append({'patch_coeff_offset':hex(offset), 'xex_book_offset':hex(at)})
    return matches


def frame_window(pe, start, count=64):
    if not 0 <= start <= len(pe) - count * 9:
        raise ValueError('janela de frames invalida')
    sample = pe[start:start + count * 9]
    headers = sample[::9]
    return {
        'offset': hex(start), 'frame_count': count,
        'matching_headers': sum(valid_header(x) for x in headers),
        'nonzero_bytes': sum(x != 0 for x in sample),
        'unique_byte_values': len(set(sample)),
    }


def inspect(patch, xex):
    _, pe = read_xex_pe(xex)
    _, _, partial_data, provenance = bps_known_map(patch)
    pe_sha = hashlib.sha256(pe).hexdigest()
    books = find_books(pe)
    fragments = book_shard_candidates(partial_data, provenance)
    overlap = masked_book_matches(partial_data, provenance, fragments, books)
    observed = frame_window(pe, VOICE_SAMPLE_ANCHOR) if pe_sha == CANONICAL_PE_SHA else None
    return {
        'status':'COMPATIBLE_VADPCM_STRUCTURES_NO_VOICE_DECODED',
        'xex_zip_sha256':hashlib.sha256(xex.read_bytes()).hexdigest(),
        'xex_pe_sha256':pe_sha,
        'patch_sha256':hashlib.sha256(patch).hexdigest(),
        'xex_codebook_candidates':len(books),
        'xex_first_codebook_offsets':[hex(at) for at, _ in books[:12]],
        'patch_partial_coefficient_windows':len(fragments),
        'patch_complete_coefficient_windows':sum(f['fully_recoverable'] for f in fragments),
        'masked_coefficient_matches':len(overlap),
        'masked_matches_first':overlap[:15],
        'xex_first_vadpcm_frame_window':observed,
        'notes':[
            'Os 452 candidatos deste XEX possuem cabecalho order=2/predictors=2 e 64 bytes de coeficientes nao triviais.',
            'O bloco de 64 quadros a partir de 0xA3FB10 contem headers VADPCM coerentes e dados variaveis.',
            'Janelas por assinatura nao substituem resolucao de ponteiros, bancos e samples individuais.',
            'Zero match de coeficientes alterados nao prova ausencia da voz no XEX, apenas ausencia de match byte-a-byte sob este criterio.',
            'A voz de dublagem PT-BR ainda nao foi identificada ou decodificada.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bps_or_zip',type=Path)
    parser.add_argument('xex_or_zip',type=Path)
    parser.add_argument('--report',type=Path)
    args = parser.parse_args()
    patch, _, _ = patch_data(args.bps_or_zip)
    report = inspect(patch, args.xex_or_zip)
    serial = json.dumps(report,indent=2,ensure_ascii=False) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(serial,encoding='utf-8')
    print(serial)


if __name__=='__main__':
    main()
