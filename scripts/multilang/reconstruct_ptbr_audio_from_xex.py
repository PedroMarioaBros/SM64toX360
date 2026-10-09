#!/usr/bin/env python3
"""Recuperação forense PARCIAL de vozes SM64 PT-BR usando CTL/TBL do port Xbox.

O XEX fornece somente os bytes de duas regiões de áudio da ROM fonte.
A igualdade entre essas regiões XEX e a ROM original exigida pelo BPS NÃO foi
comprovada pelo CRC integral; prévias devem ser consideradas experimentais.
Preserva a proveniência por byte e NUNCA completa zeros como dados conhecidos.
Não modifica XEX nem gera ROM distribuível.
"""
import argparse
import hashlib
import json
import struct
import wave
from pathlib import Path

from audit_bps_xex_overlap import patch_data, read_varint, read_xex_pe

SRC_CTL, SRC_TBL = 0x57B720, 0x593560
DST_CTL, DST_TBL = 0x57F8D0, 0x597710
PE_CTL, PE_TBL = 0xA27B90, 0xA3F9D0
CTL_BYTES, TBL_BYTES = 0x17E00, 0x21D2F0
BANKS = (8, 10)
EXPECTED_PE_SHA = "bb1a7ecd3c7deb0e10c316a92bf467ca0ea1104dae86bc602af9c6802aab6b56"
EXPECTED_PATCH_SHA = "1a6a0d6acb3f9626d52ed8f6a71866007df059e494461984591887c509bef4a2"
NAMES = {
    8: ["jump_hoo", "jump_wah", "yah", "haha", "yahoo", "uh", "hrmm",
        "wah2", "whoa", "eeuh", "attacked", "ooof", "here_we_go", "yawning",
        "snoring1", "snoring2", "doh", "game_over", "hello",
        "press_start_to_play", "twirl_bounce", "snoring3", "so_longa_bowser",
        "ima_tired", "waha", "yippee", "lets_a_go"],
    10: ["waaaooow", "hoohoo", "panting", None, "dying", "on_fire",
         "uh2", "coughing", "its_a_me_mario", "punch_yah", "punch_hoo",
         "mama_mia", "okey_dokey", "drowning", "thank_you_playing_my_game",
         "peach_dear_mario", "peach_mario", "peach_power_of_the_stars",
         "peach_thanks_to_you", "peach_thank_you_mario",
         "peach_something_special", "peach_bake_a_cake",
         "peach_for_mario", "peach_mario2"]
}

def u32(data, off):
    return struct.unpack_from(">I", data, off)[0]

def read_patch(patch, pe):
    if hashlib.sha256(patch).hexdigest() != EXPECTED_PATCH_SHA:
        raise ValueError("BPS não corresponde ao patch auditado")
    if hashlib.sha256(pe).hexdigest() != EXPECTED_PE_SHA:
        raise ValueError("PE não corresponde ao XEX auditado")
    if pe[PE_CTL:PE_CTL+4] != b"\0\x01\0\x26" or pe[PE_TBL:PE_TBL+4] != b"\0\x02\0\x26":
        raise ValueError("índices CTL/TBL Xbox 360 inválidos")
    s, pos = read_varint(patch, 4)
    size, pos = read_varint(patch, pos)
    metadata, pos = read_varint(patch, pos)
    pos += metadata
    if (s, size) != (8388608, 9090352):
        raise ValueError("dimensões BPS inesperadas")
    source, sknown = bytearray(s), bytearray(s)
    for address, file_off, length in ((SRC_CTL, PE_CTL, CTL_BYTES),
                                       (SRC_TBL, PE_TBL, TBL_BYTES)):
        source[address:address+length] = pe[file_off:file_off+length]
        sknown[address:address+length] = b"\x01"*length
    target, known = bytearray(size), bytearray(size)
    at = so = to = 0
    while pos < len(patch)-12:
        operation, pos = read_varint(patch, pos)
        mode, length = operation & 3, (operation >> 2)+1
        if at+length > size:
            raise ValueError("BPS excede tamanho de destino")
        if mode == 0:
            target[at:at+length] = source[at:at+length]
            known[at:at+length] = sknown[at:at+length]
        elif mode == 1:
            target[at:at+length] = patch[pos:pos+length]
            known[at:at+length] = b"\x01"*length
            pos += length
        else:
            d,pos = read_varint(patch,pos)
            delta = -(d >> 1) if d & 1 else d >> 1
            if mode == 2:
                so += delta
                target[at:at+length] = source[so:so+length]
                known[at:at+length] = sknown[so:so+length]
                so += length
            else:
                to += delta
                if not (0 <= to < at):
                    raise ValueError("TargetCopy fora do prefixo")
                if to+length <= at:
                    target[at:at+length] = target[to:to+length]
                    known[at:at+length] = known[to:to+length]
                else:
                    for j in range(length):
                        target[at+j] = target[to+j]
                        known[at+j] = known[to+j]
                to += length
        at += length
    if at != size or pos != len(patch)-12:
        raise ValueError("fim BPS inconsistente")
    return target, known

def decode_vadpcm(sample, book):
    """Codec de quadros 9->16, coeficientes inteiros Q11, 2 preditores."""
    if len(book)!=72 or struct.unpack_from(">II",book,0)!=(2,2):
        raise ValueError("livro VADPCM inesperado")
    coeffs=struct.unpack_from(">32h",book,8)
    predictors=[]
    for p in range(2):
        table=[[0]*10 for _ in range(8)]
        for j in range(2):
            for i in range(8):
                table[i][j]=coeffs[p*16+j*8+i]
        for i in range(1,8):
            table[i][2]=table[i-1][1]
        table[0][2]=2048
        for k in range(1,8):
            for j in range(8):
                table[j][k+2]=0 if j<k else table[j-k][2]
        predictors.append(table)
    history=[0,0]
    samples=[]
    for frameoff in range(0,len(sample),9):
        frame=sample[frameoff:frameoff+9]
        if len(frame)!=9 or (frame[0]>>4)>12 or (frame[0]&15)>1:
            raise ValueError("quadro VADPCM inválido")
        shift, pred=frame[0]>>4,frame[0]&15
        residual=[]
        for byte in frame[1:]:
            for nib in (byte>>4,byte&15):
                residual.append((nib if nib<8 else nib-16)<<shift)
        for half in range(2):
            values=history+residual[half*8:half*8+8]
            group=[sum(a*b for a,b in zip(predictors[pred][i],values))//2048
                   for i in range(8)]
            samples.extend(group)
            history=group[-2:]
    return samples

def collect(target, known, export_dir=None):
    def is_known(a,n):
        return a >= 0 and a+n <= len(known) and all(known[a:a+n])
    rows=[]
    if target[DST_CTL:DST_CTL+4] != b"\0\x01\0\x26" or target[DST_TBL:DST_TBL+4] != b"\0\x02\0\x26":
        raise ValueError("destino CTL/TBL parcial não validado")
    for bank in BANKS:
        co,cl=struct.unpack_from(">II",target,DST_CTL+4+bank*8)
        to,tl=struct.unpack_from(">II",target,DST_TBL+4+bank*8)
        base=DST_CTL+co+16
        tbl=DST_TBL+to
        n=u32(target,DST_CTL+co)
        if n!=len(NAMES[bank]): raise ValueError("instrumentos inesperados")
        for slot in range(n):
            ptrat=base+4+slot*4
            if not is_known(ptrat,4):
                continue
            inst=u32(target,ptrat)
            if inst==0:
                rows.append(dict(bank=f"{bank:02X}",slot=f"{slot:02X}",
                                 name=NAMES[bank][slot],empty=True,ready=False))
                continue
            ins=base+inst
            desc=u32(target,ins+16)
            info=base+desc
            # Sem os 32 bytes do instrumento + 20 do descritor, nada é exportado.
            if not is_known(ins,32) or not is_known(info,20):
                rows.append(dict(bank=f"{bank:02X}",slot=f"{slot:02X}",
                                 name=NAMES[bank][slot],ready=False,reason="instrument_or_descriptor"))
                continue
            zero,offset,loop,book,size=struct.unpack_from(">IIIII",target,info)
            bookat,loopat,sampleat=base+book,base+loop,tbl+offset
            ready=(zero==0 and size>0 and size%9 in (0,1) and offset+size<=tl
                   and is_known(bookat,72) and is_known(loopat,16)
                   and is_known(sampleat,size))
            if not ready:
                rows.append(dict(bank=f"{bank:02X}",slot=f"{slot:02X}",
                                 name=NAMES[bank][slot],ready=False,reason="audio_or_metadata_incomplete"))
                continue
            ls,le,lc,pad=struct.unpack_from(">IIiI",target,loopat)
            if lc!=0 or pad!=0 or not 0<le<=((size//9)*16)+1:
                ready=False
            if target[bookat:bookat+8] != b"\0\0\0\x02\0\0\0\x02":
                ready=False
            if not ready:
                rows.append(dict(bank=f"{bank:02X}",slot=f"{slot:02X}",
                                 name=NAMES[bank][slot],ready=False,reason="unsupported_loop_or_book"))
                continue
            compressed=target[sampleat:sampleat+size-(size%9)]
            pcm=decode_vadpcm(compressed,target[bookat:bookat+72])[:le]
            tuning=struct.unpack_from(">f",target,ins+20)[0]
            samplerate=round(32000*tuning)
            entry=dict(bank=f"{bank:02X}",slot=f"{slot:02X}",
                       name=NAMES[bank][slot],ready=True, sample_bytes=size,
                       pcm_samples=len(pcm),sample_rate=samplerate,
                       compressed_sha256=hashlib.sha256(compressed).hexdigest())
            if export_dir is not None:
                export_dir.mkdir(parents=True,exist_ok=True)
                path=export_dir/f"SM64_PTBR_EXPERIMENTAL_{bank:02X}_{slot:02X}_{entry['name']}.wav"
                clipped=[max(-32767,min(32767,n)) for n in pcm]
                with wave.open(str(path),"wb") as out:
                    out.setnchannels(1);out.setsampwidth(2);out.setframerate(samplerate)
                    out.writeframes(struct.pack("<%dh"%len(clipped),*clipped))
                entry["wav_name"]=path.name
                entry["wav_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(entry)
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("patch_zip",type=Path)
    p.add_argument("xex_zip",type=Path)
    p.add_argument("--export-dir",type=Path)
    p.add_argument("--report",type=Path)
    args=p.parse_args()
    patch,_,_=patch_data(args.patch_zip)
    _,pe=read_xex_pe(args.xex_zip)
    target,known=read_patch(patch,pe)
    rows=collect(target,known,args.export_dir)
    report={
        "status":"CONDITIONAL_PREVIEWS_NOT_VERIFIED_SOURCE_ROM",
        "source_crc_not_confirmed":True,
        "target_bytes_known_with_xex":sum(known),
        "ctl_known":sum(known[DST_CTL:DST_TBL]),
        "ctl_total":DST_TBL-DST_CTL,
        "events_ready":[x for x in rows if x["ready"]],
        "events_unready":sum(not x["ready"] for x in rows),
        "restrictions":["XEX não prova igualdade com ROM N64 exigida pelo patch",
                        "WAVs são prévias experimentais e devem ser escutados",
                        "Não publicar conteúdos de áudio ou XEX no GitHub público"]}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
