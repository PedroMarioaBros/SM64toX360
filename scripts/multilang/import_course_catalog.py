#!/usr/bin/env python3
"""Importa títulos de fases/missões EN/ES por IDs sem alterar o PT-BR.

15 COURSE_ACTS x 6, 10 SECRET_STAR, 1 CASTLE_SECRET_STARS e 7 EXTRA_TEXT.
Inputs: _localization_build/{en,es}/courses_source.txt já importados de
pinned upstream. Não contém ROM ou ativos proprietários e não gera XEX.
"""
from __future__ import annotations
import argparse
import ast
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"_localization_build"
HEAD=re.compile(r"^(COURSE_ACTS|SECRET_STAR|CASTLE_SECRET_STARS|EXTRA_TEXT)\(",re.M)
QUOTED=re.compile(r'_\("((?:\\.|[^"\\])*)"\)')
COURSE_ID=re.compile(r"\(\s*(COURSE_[A-Z0-9_]+)\s*,")
EXTRA_ID=re.compile(r"\(\s*(\d+)\s*,")
COURSE_COUNT=15
ACTS_PER_COURSE=6
SECRET_COUNT=10
EXTRA_COUNT=7
SPANISH_COURSE_ERRATA={
  # Verified typo in pinned Spanish source for Whomp's Fortress act 4.
  ("COURSE_WF",4):("MONEDAS ROJAS EN LA ISLA FLOANTE",
                    "MONEDAS ROJAS EN LA ISLA FLOTANTE")
}


def parse_course_source(source):
    matches=list(HEAD.finditer(source))
    courses={}
    secrets={}
    extras={}
    castle=None
    for index,m in enumerate(matches):
        segment=source[m.start():matches[index+1].start() if index+1<len(matches) else len(source)]
        labels=[ast.literal_eval('"'+x.group(1)+'"') for x in QUOTED.finditer(segment)]
        kind=m.group(1)
        if kind=="COURSE_ACTS":
            id_match=COURSE_ID.search(segment)
            if not id_match or len(labels)!=7:
                raise ValueError(f"malformed course index {index} / {segment[:80]!r}")
            key=id_match.group(1)
            if key in courses:
                raise ValueError("duplicate course ID")
            courses[key]={"name":labels[0], "acts":labels[1:]}
        elif kind=="SECRET_STAR":
            id_match=COURSE_ID.search(segment)
            if not id_match or len(labels)!=1:
                raise ValueError("malformed secret stage")
            key=id_match.group(1)
            if key in secrets:
                raise ValueError("duplicate secret stage")
            secrets[key]=labels[0]
        elif kind=="CASTLE_SECRET_STARS":
            if castle is not None or len(labels)!=1:
                raise ValueError("duplicate/invalid castle secret label")
            castle=labels[0]
        else:
            id_match=EXTRA_ID.search(segment)
            if not id_match or len(labels)!=1:
                raise ValueError("malformed extra label")
            key=int(id_match.group(1))
            if key in extras:
                raise ValueError("duplicate extra ID")
            extras[key]=labels[0]
    if len(courses)!=COURSE_COUNT or len(secrets)!=SECRET_COUNT or len(extras)!=EXTRA_COUNT or castle is None:
        raise ValueError(f"bad catalog dimensions: courses={len(courses)}, secrets={len(secrets)}, extras={len(extras)}")
    if set(extras)!=set(range(EXTRA_COUNT)):
        raise ValueError("EXTRA_TEXT IDs must be 0..6")
    return {"courses":courses,"secrets":secrets,"castle_secret_stars":castle,
            "extra_text":extras}


def apply_spanish_course_errata(catalog):
    changed=[]
    for (key,act),(before,after) in SPANISH_COURSE_ERRATA.items():
        text=catalog["courses"][key]["acts"][act-1]
        if text.count(before)!=1:
            raise ValueError(f"course ES {key}/act{act}: unexpected source text")
        catalog["courses"][key]["acts"][act-1]=text.replace(before,after,1)
        changed.append({"course":key,"act":act,"kind":"orthography_only"})
    return changed


def audit_course_alignment(en,es):
    for tag in ("courses","secrets","extra_text"):
        if list(en[tag])!=list(es[tag]):
            raise ValueError(f"{tag}: English/Spanish IDs or order diverge")
    if any(len(row["acts"])!=6 for lang in (en,es) for row in lang["courses"].values()):
        raise ValueError("inconsistent act counts")
    extra_ids=list(en["extra_text"])
    if extra_ids!=list(range(7)):
        raise ValueError("extra labels are not aligned")
    return {
        "status":"PASS_STAGE_ID_ALIGNMENT",
        "main_courses":15, "named_missions":90,
        "secret_stage_slots":10,
        "castle_secret_heading":1,
        "auxiliary_strings":7,
        "en_es_ids_identical":True,
        "pt_br_not_modified":True,
        "semantic_equivalence_human_certified":False,
        "game_runtime_integration_completed":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()
    en=parse_course_source((BUILD/"en/courses_source.txt").read_text(encoding="utf-8"))
    es=parse_course_source((BUILD/"es/courses_source.txt").read_text(encoding="utf-8"))
    changes=apply_spanish_course_errata(es)
    result=audit_course_alignment(en,es)
    result["spanish_errata"]=changes
    for lang,catalog in (("en",en),("es",es)):
        (BUILD/lang/"course_catalog.json").write_text(
            json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
