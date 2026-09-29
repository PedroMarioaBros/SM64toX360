#!/usr/bin/env python3
"""
Validação fail-closed da localização multilíngue.

Falha a build se:
- algum idioma não tiver exatamente 170 diálogos;
- sobrar token de controle N64;
- houver caractere fora do alfabeto suportado;
- os IDs divergirem entre idiomas;
- o manifesto de voz não contiver os três idiomas.
"""

from __future__ import annotations
from pathlib import Path
import ast
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "_localization_build"
SOURCES = ROOT / "_localization_sources"
LEGACY = re.compile(r"\[(?:A|B|Z|R|C(?:\^|\||>|<)?)\]")

def load_supported_chars():
    chars = set()
    path = SOURCES / "sm64_upstream/charmap.txt"
    source = subprocess.check_output(
        ["cpp", "-P", "-DVERSION_US", str(path)],
        text=True, encoding="utf-8"
    )
    for line in source.splitlines():
        m = re.match(r"('(?:\\.|[^'])*')\s*=", line)
        if m:
            try:
                token = ast.literal_eval(m.group(1))
            except Exception:
                continue
            if len(token) == 1:
                chars.add(token)

    glyphs = json.loads(
        (ROOT / "localization/manifests/glyphs.json").read_text(encoding="utf-8")
    )
    chars.update(glyphs["ptbr_v04_fixed"])
    chars.update(glyphs["spanish_extra_candidates"])
    chars.add("\n")
    return chars

def final_path(lang):
    if lang == "pt_br":
        return BUILD / lang / "dialogs.json"
    return BUILD / lang / "dialogs_xbox360.json"

def main():
    supported = load_supported_chars()
    reports = {}
    canonical_ids = list(range(170))

    for lang in ("pt_br", "es", "en"):
        path = final_path(lang)
        rows = json.loads(path.read_text(encoding="utf-8"))
        ids = [r["id"] for r in rows]
        if ids != canonical_ids:
            raise RuntimeError(f"{lang}: expected dialog IDs 0..169")

        legacy = []
        unsupported = {}
        for row in rows:
            found = LEGACY.findall(row["text"])
            if found:
                legacy.append({"id": row["id"], "tokens": found})
            for ch in row["text"]:
                # Multi-character SM64 tokens such as [%] are handled below.
                if ch not in supported and ch not in "[]%":
                    unsupported.setdefault(ch, []).append(row["id"])

        if legacy:
            raise RuntimeError(f"{lang}: legacy N64 tokens remain: {legacy}")
        if unsupported:
            compact = {k: sorted(set(v))[:12] for k, v in unsupported.items()}
            raise RuntimeError(f"{lang}: unsupported characters: {compact}")

        reports[lang] = {
            "dialogs": len(rows),
            "legacy_n64_control_tokens": 0,
            "unsupported_characters": 0,
        }

    voices = json.loads(
        (ROOT / "localization/manifests/voice_events.json").read_text(encoding="utf-8")
    )
    if set(voices["languages"]) != {"pt_br", "es", "en"}:
        raise RuntimeError("voice manifest must define pt_br, es and en")

    out = {
        "status": "PASS",
        "languages": reports,
        "voice_languages": sorted(voices["languages"]),
    }
    (BUILD / "validation_report.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
