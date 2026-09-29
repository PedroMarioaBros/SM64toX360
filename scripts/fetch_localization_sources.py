#!/usr/bin/env python3
"""
Baixa somente repositórios-fonte públicos para uma pasta de trabalho local.

Este script NÃO copia ROM, XEX, baserom, vozes originais da Nintendo
ou outros assets proprietários para o repositório SM64toX360.

Uso:
    python3 scripts/fetch_localization_sources.py
"""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_localization_sources"

SOURCES = {
    "ptbr_bmatsantos": "https://github.com/bMatSantos/sm64-ptbr.git",
    "es_reonu": "https://github.com/Reonu/ultrasm64-spanish.git",
}

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    WORK.mkdir(exist_ok=True)

    for name, url in SOURCES.items():
        dest = WORK / name
        if dest.exists():
            print(f"[update] {name}")
            run(["git", "-C", str(dest), "pull", "--ff-only"])
        else:
            print(f"[clone] {name}")
            run(["git", "clone", "--depth", "1", url, str(dest)])

    print(f"Fontes disponíveis em: {WORK}")

if __name__ == "__main__":
    main()
