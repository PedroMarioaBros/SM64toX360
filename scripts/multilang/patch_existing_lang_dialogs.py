#!/usr/bin/env python3
"""Atualiza SOMENTE textos EN/ES divergentes na .lang da TEST3.

Preserva todos os 170 ponteiros PT-BR, pool PT-BR e bytes do jogo fora de
.lang. Nunca reescreve a tradução PT-BR. Usa o texto revisado e formatado
pela pipeline vigente (dialogs_layout.json) e a mesma codificação N64.

Quando o texto codificado já corresponde ao existente, mantém seu ponteiro
intocado; quando difere, anexa a nova string e atualiza apenas o ponteiro
específico ES ou EN. Falha se a reserva de 0x20000 bytes for insuficiente.
Não instala hook, não gera XEX, não ativa seletor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

from build_dialog_pools import encoder, load_charmap

BASE=0x82000000
LANG_RVA=0x01040000
LANG_SIZE=0x20000
DIALOG_COUNT=170
TABLE_OFFSETS={"pt_br":0x100,"es":0x3b0,"en":0x660}
PT_POOL_START=0x908
PT_POOL_END=0x6ec8
PT_PTR_SHA="b612518417970dcf93904dc023aededcba046f9b1d0f823cf1beb799ee6c5a97"
PT_POOL_SHA="614f3e4aa7eca2f657757a4ff8ef790c7deb5bf7426837f0e1ce94be673b69a8"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check_pt_br(pe):
    head=LANG_RVA
    ptrs=pe[head+TABLE_OFFSETS["pt_br"]:head+TABLE_OFFSETS["pt_br"]+DIALOG_COUNT*4]
    pool=pe[head+PT_POOL_START:head+PT_POOL_END]
    if sha(ptrs)!=PT_PTR_SHA or sha(pool)!=PT_POOL_SHA:
        raise ValueError("PT-BR bytes or 170 pointers differ from hardware-approved TEST3")
    return bytes(ptrs),bytes(pool)

def read_encoded_string(pe,ptr):
    if not BASE+LANG_RVA<=ptr<BASE+LANG_RVA+LANG_SIZE:
        raise ValueError("EN/ES current pointer not within .lang")
    off=ptr-BASE
    limit=LANG_RVA+LANG_SIZE
    end=pe.find(b"\xff",off,min(off+0x1000,limit))
    if end<0:
        raise ValueError("unterminated existing encoded dialogue")
    return bytes(pe[off:end+1])

def update_dialogs(mapped_pe:bytes,rows,encode):
    if len(mapped_pe)!=LANG_RVA+LANG_SIZE:
        raise ValueError("expected TEST3 mapped image with .lang section")
    if mapped_pe[LANG_RVA:LANG_RVA+8]!=b"SM64LANG":
        raise ValueError("SM64LANG section missing")
    ver,languages,dialogues=struct.unpack_from(">III",mapped_pe,LANG_RVA+8)
    if ver!=2 or languages!=3 or dialogues!=170:
        raise ValueError("unexpected .lang ABI")
    original_pt,original_pool=check_pt_br(mapped_pe)

    current=struct.unpack_from(">I",mapped_pe,LANG_RVA+0x38)[0]
    if not 0x1000<current<LANG_SIZE:
        raise ValueError("incorrect .lang used counter")
    if any(mapped_pe[LANG_RVA+current:LANG_RVA+LANG_SIZE]):
        raise ValueError("nonzero unallocated payload after used cursor")

    image=bytearray(mapped_pe)
    cursor=current
    changed={}
    retained={}
    for lang in ("es","en"):
        entries=rows[lang]
        if [x.get("id") for x in entries]!=list(range(DIALOG_COUNT)):
            raise ValueError(f"{lang}: expected exactly 170 ordered ID rows")
        changed[lang]=[]
        retained[lang]=0
        for item in entries:
            idx=item["id"]
            table_slot=LANG_RVA+TABLE_OFFSETS[lang]+idx*4
            original_va=struct.unpack_from(">I",mapped_pe,table_slot)[0]
            old=read_encoded_string(mapped_pe,original_va)
            new=encode(item["text"])
            if not new or new[-1]!=0xFF:
                raise ValueError("invalid encoded dialogue")
            if new==old:
                retained[lang]+=1
                continue
            # Original content and other pointers stay where they were.
            cursor=(cursor+3)&~3
            if cursor+len(new)>LANG_SIZE:
                raise ValueError(".lang capacity exhausted by corrected EN/ES dialogs")
            at=LANG_RVA+cursor
            image[at:at+len(new)]=new
            struct.pack_into(">I",image,table_slot,BASE+at)
            cursor+=len(new)
            changed[lang].append(idx)

    struct.pack_into(">I",image,LANG_RVA+0x38,cursor)
    if image[:LANG_RVA]!=mapped_pe[:LANG_RVA]:
        raise ValueError("gameplay binary modified outside .lang")
    if image[LANG_RVA+TABLE_OFFSETS["pt_br"]:LANG_RVA+TABLE_OFFSETS["pt_br"]+680]!=original_pt:
        raise ValueError("PT-BR pointers mutated")
    if image[LANG_RVA+PT_POOL_START:LANG_RVA+PT_POOL_END]!=original_pool:
        raise ValueError("PT-BR text pool mutated")
    for lang in ("es","en"):
        before=mapped_pe[LANG_RVA+TABLE_OFFSETS[lang]:LANG_RVA+TABLE_OFFSETS[lang]+680]
        after=image[LANG_RVA+TABLE_OFFSETS[lang]:LANG_RVA+TABLE_OFFSETS[lang]+680]
        altered_slots=[i for i in range(170)
                       if before[i*4:i*4+4]!=after[i*4:i*4+4]]
        if altered_slots!=changed[lang]:
            raise ValueError("Unexpected change to EN/ES dialog pointer list")
    return bytes(image), {
        "status":"DIALOG_EN_ES_DELTA_STAGED_NOT_ACTIVATED",
        "input_pe_sha256":sha(mapped_pe),
        "output_pe_sha256":sha(image),
        "pt_br_pointer_sha256":PT_PTR_SHA,
        "pt_br_pool_sha256":PT_POOL_SHA,
        "original_gameplay_bytes_unchanged":True,
        "pt_br_bytes_unchanged":True,
        "lang_changed_dialog_ids":changed,
        "unchanged_dialog_count":retained,
        "prior_used_bytes":current,
        "updated_used_bytes":cursor,
        "free_bytes":LANG_SIZE-cursor,
        "runtime_selector_not_installed":True,
        "hardware_test_pending":True,
        "no_dialogue_text_in_report":True,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mapped_lang_pe",type=Path)
    ap.add_argument("dialogs_dir",type=Path)
    ap.add_argument("output_pe",type=Path)
    ap.add_argument("--report",type=Path)
    a=ap.parse_args()
    rows={k:json.loads((a.dialogs_dir/k/"dialogs_layout.json").read_text(encoding="utf-8"))
          for k in ("es","en")}
    result,report=update_dialogs(a.mapped_lang_pe.read_bytes(),rows,
                                 encoder(load_charmap()))
    a.output_pe.write_bytes(result)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
