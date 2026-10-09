#!/usr/bin/env python3
"""Identifica fragmentos de VADPCM em BPS parcial, sem inventar bytes ausentes.

Heuristica: o N64 VADPCM tipico usa quadros de 9 bytes (16 amostras PCM)
e cabecalho com shift <= 12 e indice de preditor 0..1.
O resultado NAO identifica vozes, limites completos de samples, nem decodifica audio.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from audit_bps_xex_overlap import bps_known_map, patch_data, known_runs

CTL_START = 0x57F8D0
TBL_START = 0x597710
DATA_START = 0x60C040
SCAN_END = 0x794970  # fronteira exploratoria, nao TBL final


def valid_header(byte):
    return (byte >> 4) <= 12 and (byte & 15) <= 1


def frame_score(data, start, stop, phase):
    if not (0 <= phase < 9) or start + phase >= stop:
        raise ValueError('fase fora do trecho')
    count = (stop - start - phase) // 9
    if count <= 0:
        return {'phase': phase, 'frames': 0, 'valid': 0, 'fraction': 0.0}
    first = start + phase
    valid = sum(valid_header(b) for b in data[first:first + count * 9:9])
    return {'phase': phase, 'frames': count, 'valid': valid,
            'fraction': round(valid / count, 8)}


def scan_fragments(data, known, start=DATA_START, stop=SCAN_END, min_run=512):
    if len(data) != len(known) or not 0 <= start < stop <= len(data):
        raise ValueError('regiao ou mapa de proveniencia invalido')
    results = []
    for a, b in known_runs(known, start, stop, min_run):
        phases = [frame_score(data, a, b, phase) for phase in range(9)]
        best = max(phases, key=lambda x: (x['fraction'], x['frames'], -x['phase']))
        results.append({
            'start': hex(a), 'end_exclusive': hex(b), 'known_bytes': b - a,
            'best_phase': best['phase'], 'full_frames': best['frames'],
            'valid_headers': best['valid'], 'header_fraction': best['fraction'],
            'perfect': best['valid'] == best['frames'],
        })
    return results


def book_shard_candidates(data, known, start=CTL_START, stop=TBL_START):
    """Trechos alinhados de 64 bytes com 62+ bytes conhecidos e 30+ coeficientes
    nao nulos. Nao presume que a janela e um codebook real ou integro.
    """
    out = []
    for offset in range(start, stop - 63, 8):
        mask = known[offset:offset + 64]
        num = sum(mask)
        if num < 62:
            continue
        packed = data[offset:offset + 64]
        nonzero = sum(
            bool(packed[i] or packed[i + 1]) and bool(mask[i] or mask[i+1])
            for i in range(0, 64, 2)
        )
        if nonzero < 30:
            continue
        out.append({
            'offset': hex(offset), 'known_bytes': num,
            'unknown_byte_positions': [i for i, flag in enumerate(mask) if not flag],
            'fully_recoverable': num == 64,
        })
    return out


def make_report(patch):
    source_size, target_size, data, known = bps_known_map(patch)
    if target_size < SCAN_END:
        raise ValueError('alvo BPS menor que a regiao examinada')
    fragments = scan_fragments(data, known)
    books = book_shard_candidates(data, known)
    total = sum(f['full_frames'] for f in fragments if f['perfect'])
    return {
        'status': 'VADPCM_PATTERN_CONFIRMED_NO_VOICE_DECODED',
        'patch_sha256': hashlib.sha256(patch).hexdigest(),
        'source_size': source_size, 'target_size': target_size,
        'scanned_region': {'start': hex(DATA_START), 'end_exclusive': hex(SCAN_END)},
        'format_check': '9-byte frames; high nibble <=12, predictor low nibble <=1',
        'statistics': {
            'known_runs_min_512': len(fragments),
            'perfect_phase_runs': sum(f['perfect'] for f in fragments),
            'phase_runs_at_least_95pct': sum(f['header_fraction'] >= 0.95 for f in fragments),
            'fully_known_frames_in_perfect_runs': total,
            'candidate_coefficient_windows': len(books),
            'complete_candidate_coefficient_windows': sum(b['fully_recoverable'] for b in books),
        },
        'first_audio_fragment': next((f for f in fragments if f['start'] == hex(DATA_START)), None),
        'fragments': fragments,
        'coefficient_window_candidates': books,
        'limitations': [
            'Um trecho BPS conhecido nao e necessariamente um sample inteiro.',
            'Mudancas de fase podem indicar mudancas de sample/padding; nao presumir limites.',
            'Uma janela de coeficientes e heuristica, nao um codebook identificado por ponteiro.',
            'Nenhuma janela de coeficientes completa encontrada com este filtro.',
            'A simples ocorrencia de quadros VADPCM nao associa o audio a Mario/Peach.',
            'Nao reconstruir bytes de source, nao produzir WAV/AIFF sem CTL/livro verificavel.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bps_or_zip', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    patch, _, _ = patch_data(args.bps_or_zip)
    report = make_report(patch)
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding='utf-8')
    print(json.dumps({'statistics': report['statistics'],
                      'first_audio_fragment': report['first_audio_fragment']},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
