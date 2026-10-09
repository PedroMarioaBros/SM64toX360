#!/usr/bin/env python3
"""Exporta APENAS prévias diagnósticas com quadros VADPCM e codebook completos
mas cabeçalho de loop incompleto. Reproduz todos os quadros sem corte por loop.

Não inventa bytes nem comprimento de loop: a duração exportada é somente a
duração total dos quadros de 9 bytes disponíveis, e não necessariamente a
duração exata do evento no jogo. Audio XEX->ROM é fonte condicional porque a
ROM original (CRC32 BPS) não está disponível para conferência integral.
"""
import argparse
import hashlib
import json
import math
import struct
import wave
from pathlib import Path

from audit_bps_xex_overlap import patch_data, read_xex_pe
from reconstruct_ptbr_audio_from_xex import (
    read_patch, decode_vadpcm, BANKS, NAMES, DST_CTL, DST_TBL
)


def u32(b, at):
    return struct.unpack_from('>I', b, at)[0]


def known_bytes(mask, at, length):
    return at >= 0 and length >= 0 and at+length <= len(mask) and all(mask[at:at+length])


def frame_complete_no_loop(target, known, export_dir=None):
    """Restringe exportação a amostras cujo loop HEADER tem lacunas verificadas."""
    if len(target) != len(known):
        raise ValueError('dados e proveniência de tamanhos diferentes')
    if target[DST_CTL:DST_CTL+4] != b'\0\x01\0\x26':
        raise ValueError('cabeçalho CTL não validado')
    if target[DST_TBL:DST_TBL+4] != b'\0\x02\0\x26':
        raise ValueError('cabeçalho TBL não validado')
    result=[]
    for bank in BANKS:
        co, cl=struct.unpack_from('>II',target,DST_CTL+4+bank*8)
        to, tl=struct.unpack_from('>II',target,DST_TBL+4+bank*8)
        ctl_start=DST_CTL+co
        ctl_end=ctl_start+cl
        tbl_start=DST_TBL+to
        tbl_end=tbl_start+tl
        base=ctl_start+16
        if tbl_end > len(target) or ctl_end > DST_TBL:
            raise ValueError('banco além dos limites conhecidos')
        if not known_bytes(known,ctl_start,16):
            raise ValueError('header de banco não conhecido')
        n=u32(target,ctl_start)
        if n!=len(NAMES[bank]):
            raise ValueError('contador de instrumentos inesperado')
        for slot in range(n):
            iptr=base+4+slot*4
            if not known_bytes(known,iptr,4):
                continue
            ioff=u32(target,iptr)
            if ioff==0:
                continue
            inst=base+ioff
            if inst+32>ctl_end or not known_bytes(known,inst,32):
                continue
            desc_off,tuning=struct.unpack_from('>If',target,inst+16)
            desc=base+desc_off
            if desc_off==0 or desc+20>ctl_end or not known_bytes(known,desc,20):
                continue
            zero,offset,loop_offset,book_offset,length=struct.unpack_from('>IIIII',target,desc)
            loop=base+loop_offset
            book=base+book_offset
            sample=tbl_start+offset
            if zero!=0 or not (0<length and length%9 in (0,1)):
                continue
            if loop_offset==0 or loop+16>ctl_end:
                continue
            if book_offset==0 or book+72>ctl_end:
                continue
            if sample+length>tbl_end:
                continue
            if known_bytes(known,loop,16):
                continue  # já elegível para trilha estrita; não é diagnóstico sem loop
            if not known_bytes(known,book,72) or not known_bytes(known,sample,length):
                continue
            if not math.isfinite(tuning):
                continue
            sample_rate=round(32000*tuning)
            if not 1<=sample_rate<=192000:
                continue
            audio=target[sample:sample+length-(length%9)]
            if any((x>>4)>12 or (x&15)>1 for x in audio[::9]):
                continue
            coeff=target[book:book+72]
            pcm=decode_vadpcm(audio,coeff)
            entry={
                'bank':f'{bank:02X}',
                'physical_slot':f'{slot:02X}',
                'event_name_candidate':NAMES[bank][slot],
                'source_rom_crc32_verified':False,
                'loop_header_complete':False,
                'sample_and_codebook_fully_known':True,
                'compressed_bytes':len(audio),
                'frames':len(audio)//9,
                'pcm_samples':len(pcm),
                'sample_rate_hz':sample_rate,
                'frame_duration_seconds':len(pcm)/sample_rate,
                'compressed_sha256':hashlib.sha256(audio).hexdigest(),
                'duration_is_exact_gameplay':False,
            }
            if export_dir is not None:
                export_dir.mkdir(parents=True,exist_ok=True)
                name=f"SM64_DIAG_FRAMES_NO_LOOP_{bank:02X}_{slot:02X}_{NAMES[bank][slot]}.wav"
                file=export_dir/name
                clipped=[max(-32767,min(32767,x)) for x in pcm]
                with wave.open(str(file),'wb') as w:
                    w.setnchannels(1)
                    w.setsampwidth(2)
                    w.setframerate(sample_rate)
                    w.writeframes(struct.pack('<%dh'%len(clipped),*clipped))
                entry['wav_name']=name
                entry['wav_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            result.append(entry)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('patch_zip',type=Path)
    ap.add_argument('xex_zip',type=Path)
    ap.add_argument('--export-dir',type=Path)
    ap.add_argument('--report',type=Path)
    options=ap.parse_args()
    patch,_,_=patch_data(options.patch_zip)
    _,pe=read_xex_pe(options.xex_zip)
    target,known=read_patch(patch,pe)
    entries=frame_complete_no_loop(target,known,options.export_dir)
    report={
        'status':'FRAME_COMPLETE_NO_LOOP_DIAGNOSTIC_ONLY',
        'input_bps_sha256':hashlib.sha256(patch).hexdigest(),
        'input_pe_sha256':hashlib.sha256(pe).hexdigest(),
        'source_rom_crc32_verified':False,
        'events':entries,
        'notes':[
          'O fim exato de loop/playback não foi recuperado para estas amostras.',
          'Áudios exportados somente se 100% dos quadros e do codebook forem conhecidos.',
          'A identificação de idioma/fala exige validação por escuta.',
          'Não exporta ROM nem XEX, não publica áudio em GitHub.',
        ],
    }
    if options.report:
        options.report.parent.mkdir(parents=True,exist_ok=True)
        options.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
