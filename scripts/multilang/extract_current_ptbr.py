#!/usr/bin/env python3
"""
Extrai os 170 diálogos PT-BR diretamente da imagem mapeada da v0.4.

Fonte canônica do PT-BR:
  o próprio SM64 PT-BR Xbox 360 produzido por PeterKleizoon - PMCN Studios.

Não usa o texto PT-BR de nenhum projeto externo.

Uso:
  python3 scripts/multilang/extract_current_ptbr.py \
      /caminho/translated-v04.bin \
      _localization_sources/sm64_upstream/charmap.txt

Saída:
  _localization_build/pt_br/dialogs.json
"""

from __future__ import annotations
from pathlib import Path
import ast
import json
import re
import struct
import sys

BASE = 0x82000000
DIALOG_TABLE = 0x9E7CD8
DIALOG_COUNT = 170

# Exatamente a alocação usada pelo construtor recuperado da v0.4.
ACCENTS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
SLOTS = list(range(0x60, 0x6F)) + list(range(0x70, 0x80))

def load_reverse_charmap(path: Path):
    reverse = {}
    source = subprocess.check_output(
        ["cpp", "-P", "-DVERSION_US", str(path)],
        text=True, encoding="utf-8"
    )
    for line in source.splitlines():
        m = re.match(r"('(?:\\.|[^'])*')\s*=\s*(.*)", line)
        if not m:
            continue
        try:
            char = ast.literal_eval(m.group(1))
            raw = bytes(int(x, 16) for x in m.group(2).split(","))
        except Exception:
            continue
        if len(raw) == 1:
            reverse[raw[0]] = char

    for ch, slot in zip(ACCENTS, SLOTS):
        reverse[slot] = ch

    reverse[0xFE] = "\n"
    # Tokens compressed by SM64's text format.
    reverse[0xD0] = "  "
    reverse[0xD1] = "the"
    reverse[0xD2] = "you"
    return reverse

def decode_dialog(data: bytes, start: int, reverse):
    out = []
    p = start
    while p < len(data):
        v = data[p]
        p += 1
        if v == 0xFF:
            return "".join(out), p
        if v == 0xE0:
            # Percent / dynamic number token in the stock charmap.
            out.append("[%]")
            continue
        if v not in reverse:
            out.append(f"<0x{v:02X}>")
        else:
            out.append(reverse[v])
    raise RuntimeError(f"unterminated dialog at 0x{start:X}")

def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "Uso: extract_current_ptbr.py translated-v04.bin charmap.txt"
        )
    image = Path(sys.argv[1]).read_bytes()
    reverse = load_reverse_charmap(Path(sys.argv[2]))

    rows = []
    unknown = []
    for dialog_id in range(DIALOG_COUNT):
        rec = DIALOG_TABLE + dialog_id * 16
        if rec + 16 > len(image):
            raise RuntimeError("dialog table outside mapped image")
        lines = image[rec + 2]
        ptr = struct.unpack_from(">I", image, rec + 8)[0]
        off = ptr - BASE
        if not (0 <= off < len(image)):
            raise RuntimeError(
                f"dialog {dialog_id}: invalid ptr 0x{ptr:08X}"
            )
        text, end = decode_dialog(image, off, reverse)
        if "<0x" in text:
            unknown.append(dialog_id)
        rows.append({
            "id": dialog_id,
            "lines": lines,
            "offset": off,
            "length": end - off,
            "text": text,
        })

    target = Path("_localization_build/pt_br")
    target.mkdir(parents=True, exist_ok=True)
    (target / "dialogs.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = {
        "dialogs": len(rows),
        "unknown_code_dialogs": unknown,
        "source": str(Path(sys.argv[1])),
        "canonical": "PeterKleizoon - PMCN Studios v0.4 mapped image",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if unknown:
        raise SystemExit("Há códigos de texto ainda não decodificados.")

if __name__ == "__main__":
    main()
