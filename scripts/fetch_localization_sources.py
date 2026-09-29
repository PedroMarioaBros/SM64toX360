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
    "sm64_upstream": (
        "https://github.com/n64decomp/sm64.git",
        "9921382a68bb0c865e5e45eb594d9c64db59b1af",
    ),
    "ptbr_bmatsantos": (
        "https://github.com/bMatSantos/sm64-ptbr.git",
        "be7920d79192df4b8130a0f63c76d3db5adf6b6d",
    ),
    "es_reonu": (
        "https://github.com/Reonu/ultrasm64-spanish.git",
        "b720e8328c4ead21e3eac5dfceb21edba38ed79b",
    ),
}

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    WORK.mkdir(exist_ok=True)

    for name, (url, commit) in SOURCES.items():
        dest = WORK / name
        if not dest.exists():
            print(f"[clone] {name}")
            run(["git", "clone", url, str(dest)])
        print(f"[pin] {name} -> {commit}")
        run(["git", "-C", str(dest), "fetch", "origin", commit])
        run(["git", "-C", str(dest), "checkout", "--detach", commit])

    print(f"Fontes fixadas e disponíveis em: {WORK}")

if __name__ == "__main__":
    main()
