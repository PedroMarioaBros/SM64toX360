#!/usr/bin/env python3
"""
Importa textos EN/ES das fontes de referência sem vendorizá-los no repositório.

Pré-requisito:
    python3 scripts/fetch_localization_sources.py

Saída:
    _localization_build/en/dialogs.json
    _localization_build/es/dialogs.json
    _localization_build/en/courses_source.txt
    _localization_build/es/courses_source.txt

O PT-BR NÃO é substituído por fontes externas: a tradução canônica é a já
presente no binário 0.4 de PeterKleizoon - PMCN Studios.
"""

from __future__ import annotations
from pathlib import Path
import ast
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "_localization_sources"
OUT = ROOT / "_localization_build"

DIALOG_RE = re.compile(
    r'DEFINE_DIALOG\(DIALOG_(\d+),\s*([^,]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*_\(((?:"(?:\\.|[^"\\])*"\s*)+)\)\)',
    re.S,
)

def preprocess_us(path: Path):
    proc = subprocess.run(
        ["cpp", "-P", "-DVERSION_US", str(path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return proc.stdout

def parse_dialogs(path: Path):
    # A fonte usa macros condicionais (PLASTERED, SCRAM, GIVE_UP etc.).
    # Pré-processar como VERSION_US garante os mesmos 170 diálogos da build US.
    source = preprocess_us(path)
    rows = []
    for m in DIALOG_RE.finditer(source):
        pieces = re.findall(r'"(?:\\.|[^"\\])*"', m.group(6))
        text = "".join(ast.literal_eval(p) for p in pieces)
        rows.append({
            "id": int(m.group(1)),
            "lines": int(m.group(3)),
            "left": int(m.group(4)),
            "width": int(m.group(5)),
            "text": text,
        })
    ids = [r["id"] for r in rows]
    if ids != list(range(170)):
        missing = sorted(set(range(170)) - set(ids))
        raise RuntimeError(f"{path}: expected dialogs 0..169; missing={missing}")
    return rows

def main():
    es = SOURCES / "es_reonu"
    # bMatSantos fork is also a clean US-source reference, but we deliberately
    # do not use its PT text as our canonical PT-BR localization.
    if not es.exists():
        raise SystemExit("Run scripts/fetch_localization_sources.py first.")

    # English baseline comes from the parent lineage present in the Spanish repo.
    # For reproducibility, fetch the upstream source clone separately if needed.
    upstream = SOURCES / "sm64_upstream"
    if not upstream.exists():
        raise SystemExit(
            "Missing _localization_sources/sm64_upstream. "
            "Update fetch_localization_sources.py / run it again."
        )

    sources = {
        "en": upstream / "text/us/dialogs.h",
        "es": es / "text/us/dialogs.h",
    }

    OUT.mkdir(exist_ok=True)
    summary = {}
    for lang, path in sources.items():
        rows = parse_dialogs(path)
        target = OUT / lang
        target.mkdir(parents=True, exist_ok=True)
        (target / "dialogs.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        courses = path.parents[0] / "courses.h"
        (target / "courses_source.txt").write_text(
            courses.read_text(encoding="utf-8"), encoding="utf-8"
        )
        summary[lang] = {"dialogs": len(rows), "source": str(path.relative_to(ROOT))}

    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
