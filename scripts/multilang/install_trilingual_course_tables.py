#!/usr/bin/env python3
"""Integra nomes de fases/90 estrelas em .lang, SEM instalar hook no jogo.

Entrada: PE mapeado já contendo .lang e os course_catalog.json EN/ES gerados
pela fonte fixa. Fonte PT-BR: tabelas intocadas no próprio TEST3 Xbox 360.

Layout adicional em .lang (Big Endian, revisão COURSE3):
  0xC0 magic "COURSE3\\0"
  0xC8: u32 course_count (26)
  0xCC: u32 star_count (90)
  0xD0: u32 VA da tabela original de 26 nomes PT
  0xD4: u32 VA da tabela original de 90 estrelas PT
  0xD8..0xE0: offsets relativos .lang das tabelas PT/ES/EN (26 x u32)
  0xE4..0xEC: offsets relativos .lang das tabelas PT/ES/EN (90 x u32)
  0xF0: u32 novo fim do payload
Nenhuma rotina de execução ou de seleção é modificada nesta fase.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from build_dialog_pools import encoder, load_charmap
from import_course_catalog import audit_course_alignment

IMAGE_BASE=0x82000000
LANG_RVA=0x01040000
LANG_SIZE=0x20000
COURSE_TABLE=0x9E8C70
STAR_TABLE=0x9E9620
COURSE_COUNT=26
STAR_COUNT=90
LANG_USED_OFF=0x38
COURSE_META=0xC0
COURSE_META_END=0xF4

# Hardware A/B confirmed TEST3: these raw pointer arrays are immutable PT-BR.
EXPECTED_PT_COURSE_SHA="3b789baca2d6d547c0f8f2985e96da24b4878944c1278d092c614d53934cbc9d"
EXPECTED_PT_STAR_SHA="ed5c7e598cade70bcfda05d3293b230a449650f9b45bf1f52572749640be30b0"

MAIN_COURSES=(
  "COURSE_BOB","COURSE_WF","COURSE_JRB","COURSE_CCM","COURSE_BBH",
  "COURSE_HMC","COURSE_LLL","COURSE_SSL","COURSE_DDD","COURSE_SL",
  "COURSE_WDW","COURSE_TTM","COURSE_THI","COURSE_TTC","COURSE_RR",
)
SECRETS=(
  "COURSE_BITDW","COURSE_BITFS","COURSE_BITS","COURSE_PSS",
  "COURSE_COTMC","COURSE_TOTWC","COURSE_VCUTM","COURSE_WMOTR",
  "COURSE_SA","COURSE_CAKE_END",
)

def check_original_tables(pe:bytes):
    if len(pe) < STAR_TABLE+STAR_COUNT*4:
        raise ValueError("mapped PE smaller than game name tables")
    names=bytes(pe[COURSE_TABLE:COURSE_TABLE+COURSE_COUNT*4])
    acts=bytes(pe[STAR_TABLE:STAR_TABLE+STAR_COUNT*4])
    if hashlib.sha256(names).hexdigest()!=EXPECTED_PT_COURSE_SHA:
        raise ValueError("PT-BR course pointer table differs from hardware-approved TEST3")
    if hashlib.sha256(acts).hexdigest()!=EXPECTED_PT_STAR_SHA:
        raise ValueError("PT-BR star pointer table differs from hardware-approved TEST3")
    for chunk in (names,acts):
        for (pointer,) in struct.iter_unpack(">I",chunk):
            if not IMAGE_BASE<=pointer<IMAGE_BASE+len(pe):
                raise ValueError(f"out of range PT-BR pointer 0x{pointer:08X}")
    return names,acts

def ordered_catalog(en,es):
    audit_course_alignment(en,es)
    if tuple(en["courses"])!=MAIN_COURSES:
        raise ValueError("course order is not native SM64 sequence")
    if tuple(en["secrets"])!=SECRETS:
        raise ValueError("secret stage order is not native SM64 sequence")
    out={}
    for name,catalog in (("en",en),("es",es)):
        labels=[]
        for key in MAIN_COURSES:
            labels.append(catalog["courses"][key]["name"])
        for key in SECRETS:
            labels.append(catalog["secrets"][key])
        labels.append(catalog["castle_secret_stars"])
        if len(labels)!=COURSE_COUNT:
            raise ValueError("course names count mismatch")
        acts=[text for key in MAIN_COURSES for text in catalog["courses"][key]["acts"]]
        if len(acts)!=STAR_COUNT:
            raise ValueError("star titles count mismatch")
        out[name]={"course_names":labels,"star_names":acts}
    return out

def install(mapped_pe:bytes,en,es,encode):
    original_names,original_acts=check_original_tables(mapped_pe)
    catalogs=ordered_catalog(en,es)
    if len(mapped_pe)!=LANG_RVA+LANG_SIZE:
        raise ValueError("expected exact mapped .lang PE image size")
    if mapped_pe[LANG_RVA:LANG_RVA+8]!=b"SM64LANG":
        raise ValueError("expected pre-existing .lang data inside TEST3 mapped PE; no runtime hook written")
    old_cursor=struct.unpack_from(">I",mapped_pe,LANG_RVA+LANG_USED_OFF)[0]
    if not 0x100<=old_cursor<LANG_SIZE:
        raise ValueError("invalid .lang used-byte counter")
    if any(mapped_pe[LANG_RVA+COURSE_META:LANG_RVA+COURSE_META_END]):
        raise ValueError("reserved course metadata already occupied")
    if any(mapped_pe[LANG_RVA+old_cursor:LANG_RVA+LANG_SIZE]):
        raise ValueError("nonzero bytes beyond .lang used cursor")

    result=bytearray(mapped_pe)
    cursor=(old_cursor+15)&~15
    tables={"pt_br":{},"es":{},"en":{}}
    for lang in ("pt_br","es","en"):
        for section,n in (("course",COURSE_COUNT),("star",STAR_COUNT)):
            cursor=(cursor+15)&~15
            tables[lang][section]=cursor
            cursor+=4*n
            if cursor>=LANG_SIZE:
                raise ValueError("not enough .lang capacity for course tables")

    # Preserve original PT-BR pointers EXACTLY rather than duplicating text.
    pt_off=tables["pt_br"]
    result[LANG_RVA+pt_off["course"]:LANG_RVA+pt_off["course"]+len(original_names)]=original_names
    result[LANG_RVA+pt_off["star"]:LANG_RVA+pt_off["star"]+len(original_acts)]=original_acts

    text_records={}
    for lang in ("es","en"):
        for section,texts in (
            ("course",catalogs[lang]["course_names"]),
            ("star",catalogs[lang]["star_names"])
        ):
            offsets=[]
            for label in texts:
                if not isinstance(label,str):
                    raise ValueError(f"{lang} has non-string {section} title")
                if not label.strip():
                    # Original game has no title for COURSE_CAKE_END.
                    if section=="course" and len(offsets)==24:
                        offsets.append(None)
                        continue
                    raise ValueError(f"{lang} unexpected blank text")
                raw=encode(label)
                if not raw or raw[-1]!=0xFF:
                    raise ValueError(f"{lang} bad SM64 encoded title")
                cursor=(cursor+3)&~3
                if cursor+len(raw)>=LANG_SIZE:
                    raise ValueError(".lang overflow encoding stage names")
                at=LANG_RVA+cursor
                result[at:at+len(raw)]=raw
                offsets.append(IMAGE_BASE+at)
                cursor+=len(raw)
            for i,ptr in enumerate(offsets):
                if ptr is None:
                    # Special empty course slot: keep native original reference.
                    ptr=struct.unpack_from(">I",original_names,i*4)[0]
                struct.pack_into(">I",result,
                                 LANG_RVA+tables[lang][section]+i*4,ptr)
            text_records[f"{lang}_{section}"]={
                "count":len(texts),
                "encoded_nonblank":sum(bool(t.strip()) for t in texts),
            }
    if cursor>=LANG_SIZE:
        raise ValueError(".lang exceeded maximum capacity")
    at=LANG_RVA
    result[at+COURSE_META:at+COURSE_META+8]=b"COURSE3\0"
    struct.pack_into(">IIII",result,at+0xC8,COURSE_COUNT,STAR_COUNT,
                     IMAGE_BASE+COURSE_TABLE,IMAGE_BASE+STAR_TABLE)
    for i,lang in enumerate(("pt_br","es","en")):
        struct.pack_into(">I",result,at+0xD8+4*i,tables[lang]["course"])
        struct.pack_into(">I",result,at+0xE4+4*i,tables[lang]["star"])
    struct.pack_into(">I",result,at+0xF0,cursor)
    struct.pack_into(">I",result,at+LANG_USED_OFF,cursor)

    # No baseline game bytes, including PT-BR original tables, may be changed.
    if result[:LANG_RVA]!=mapped_pe[:LANG_RVA]:
        raise ValueError("unexpected modification outside .lang")
    report={
        "status":"COURSE3_STAGED_NO_RUNTIME_HOOK",
        "original_pe_sha256":hashlib.sha256(mapped_pe).hexdigest(),
        "new_pe_sha256":hashlib.sha256(result).hexdigest(),
        "gameplay_bytes_outside_lang_unchanged":True,
        "pt_course_table_sha256":EXPECTED_PT_COURSE_SHA,
        "pt_star_table_sha256":EXPECTED_PT_STAR_SHA,
        "existing_dialogs_and_layout_preserved":result[at:at+COURSE_META]==mapped_pe[at:at+COURSE_META][:LANG_USED_OFF]+struct.pack(">I",cursor)+mapped_pe[at+LANG_USED_OFF+4:at+COURSE_META],
        "course_tables":{lang:{key:hex(value) for key,value in table.items()} for lang,table in tables.items()},
        "records":text_records,
        "old_used_bytes":old_cursor,"new_used_bytes":cursor,
        "free_bytes":LANG_SIZE-cursor,
        "runtime_switch_not_installed":True,
        "hardware_star_return_not_tested_with_course3":True,
        "no_source_text_in_report":True,
    }
    if not report["existing_dialogs_and_layout_preserved"]:
        raise ValueError("unexpected alteration of preexisting .lang header")
    return bytes(result),report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mapped_lang_pe",type=Path)
    ap.add_argument("catalog_directory",type=Path)
    ap.add_argument("output_pe",type=Path)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    catalogs={}
    for lang in ("en","es"):
        catalogs[lang]=json.loads(
          (args.catalog_directory/lang/"course_catalog.json").read_text(encoding="utf-8")
        )
    out,report=install(args.mapped_lang_pe.read_bytes(),
                       catalogs["en"],catalogs["es"],
                       encoder(load_charmap()))
    args.output_pe.write_bytes(out)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
