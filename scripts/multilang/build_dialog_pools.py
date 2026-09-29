#!/usr/bin/env python3
"""
Constrói pools binários de diálogos para Português / Español / English.

Este estágio NÃO altera o XEX. Ele produz dados determinísticos que depois são
injetados pelo patcher Xbox 360 quando a imagem mapeada da v0.4 estiver presente.

Entradas esperadas:
  _localization_build/pt_br/dialogs.json
  _localization_build/es/dialogs_xbox360.json
  _localization_build/en/dialogs_xbox360.json
  _localization_sources/sm64_upstream/charmap.txt
  localization/manifests/glyphs.json

Saída por idioma:
  _localization_build/<lang>/dialogs.bin
  _localization_build/<lang>/dialog_index.json
"""

from __future__ import annotations
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "_localization_build"
UPSTREAM = ROOT / "_localization_sources/sm64_upstream"
GLYPHS = json.loads(
    (ROOT / "localization/manifests/glyphs.json").read_text(encoding="utf-8")
)

def load_charmap():
    cm = {}
    charmap_path = UPSTREAM / "charmap.txt"
    source = subprocess.check_output(
        ["cpp", "-P", "-DVERSION_US", str(charmap_path)],
        text=True, encoding="utf-8"
    )
    for line in source.splitlines():
        m = re.match(r"('(?:\\.|[^'])*')\s*=\s*(.*)", line)
        if not m:
            continue
        try:
            key = ast.literal_eval(m.group(1))
        except Exception:
            continue
        rhs = m.group(2).strip()
        # We intentionally accept only literal byte mappings. VERSION/CN helper
        # macros are irrelevant to our US Xbox 360 build.
        if not re.fullmatch(r"0x[0-9A-Fa-f]{2}(?:\s*,\s*0x[0-9A-Fa-f]{2})*", rhs):
            continue
        cm[key] = bytes(int(v, 16) for v in re.findall(r"0x([0-9A-Fa-f]{2})", rhs))

    # Stock control/dynamic tokens used by source text.
    cm["\n"] = b"\xFE"
    cm["\\n"] = b"\xFE"

    for ch, slot in GLYPHS["ptbr_v04_fixed"].items():
        cm[ch] = bytes([int(slot, 16)])
    for ch, spec in GLYPHS["spanish_extra_candidates"].items():
        cm[ch] = bytes([int(spec["candidate_slot"], 16)])

    return cm

def encoder(cm):
    keys = sorted(cm, key=len, reverse=True)

    def encode(text: str) -> bytes:
        out = bytearray()
        rest = text
        while rest:
            for key in keys:
                if rest.startswith(key):
                    out += cm[key]
                    rest = rest[len(key):]
                    break
            else:
                cp = ord(rest[0])
                raise ValueError(
                    f"Unsupported glyph/token {rest[0]!r} U+{cp:04X} "
                    f"near {rest[:30]!r}"
                )
        out.append(0xFF)
        return bytes(out)

    return encode

def main():
    cm = load_charmap()
    encode = encoder(cm)
    summary = {}

    inputs = {
        "pt_br": BUILD / "pt_br/dialogs.json",
        "es": BUILD / "es/dialogs_xbox360.json",
        "en": BUILD / "en/dialogs_xbox360.json",
    }

    for lang, source in inputs.items():
        rows = json.loads(source.read_text(encoding="utf-8"))
        if [r["id"] for r in rows] != list(range(170)):
            raise RuntimeError(f"{lang}: dialog IDs must be exactly 0..169")

        pool = bytearray()
        index = []
        for row in rows:
            while len(pool) & 7:
                pool.append(0)
            offset = len(pool)
            raw = encode(row["text"])
            pool += raw
            index.append({
                "id": row["id"],
                "lines": row["lines"],
                "pool_offset": offset,
                "length": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })

        target = BUILD / lang
        (target / "dialogs.bin").write_bytes(pool)
        (target / "dialog_index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary[lang] = {
            "dialogs": len(index),
            "pool_bytes": len(pool),
            "sha256": hashlib.sha256(pool).hexdigest(),
        }

    (BUILD / "dialog_pools_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
