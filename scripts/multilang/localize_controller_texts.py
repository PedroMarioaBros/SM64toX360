#!/usr/bin/env python3
"""
Adapta referências de controles N64 para o mapeamento real do Xbox 360.

A adaptação automática é conservadora: troca tokens de botão por rótulos
semanticamente equivalentes. A saída é então validada para garantir que nenhum
token legado [B]/[Z]/[R]/[C] permaneça.

Uso:
  python3 scripts/multilang/localize_controller_texts.py en
  python3 scripts/multilang/localize_controller_texts.py es
"""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "_localization_build"
MAP = json.loads(
    (ROOT / "localization/manifests/controller_mapping.json").read_text(
        encoding="utf-8"
    )
)

AFFECTED = set(MAP["affected_dialog_ids"])

# Ordenar C-direções antes do C genérico.
TOKENS = ["[C]^", "[C]|", "[C]>", "[C]<", "[C]", "[Z]", "[R]", "[B]", "[A]"]

BUTTON_LABEL = {
    "en": {
        "[A]": "A",
        "[B]": "X",
        "[Z]": "LT/LB",
        "[R]": "RB/RT",
        "[C]": "right stick",
        "[C]^": "right stick up",
        "[C]|": "right stick down",
        "[C]>": "right stick right",
        "[C]<": "right stick left",
    },
    "es": {
        "[A]": "A",
        "[B]": "X",
        "[Z]": "LT/LB",
        "[R]": "RB/RT",
        "[C]": "stick derecho",
        "[C]^": "stick derecho arriba",
        "[C]|": "stick derecho abajo",
        "[C]>": "stick derecho derecha",
        "[C]<": "stick derecho izquierda",
    },
}

# Frases conhecidas onde uma substituição literal ficaria artificial.
PHRASES = {
    "en": {
        "Control Stick": "left stick",
        "control stick": "left stick",
        "the [C] Buttons": "the right stick",
        "[C] Buttons": "right-stick controls",
        "the [C] buttons": "the right-stick controls",
        "[C] buttons": "right-stick controls",
    },
    "es": {
        "Palanca de Control": "stick izquierdo",
        "palanca de control": "stick izquierdo",
        "Control Stick": "stick izquierdo",
        "los botones [C]": "los controles del stick derecho",
        "cuatro botones de\ncámara, también llamados\nbotones [C]":
            "controles de cámara del\nstick derecho",
        "Usa los botones [C]": "Usa el stick derecho",
    },
}

LEGACY_RE = re.compile(r"\[(?:A|B|Z|R|C(?:\^|\||>|<)?)\]")

ALT_CAMERA_TOKENS = {
    "[C]▲": "[C]^",
    "[C]▼": "[C]|",
    "[C]▶": "[C]>",
    "[C]◀": "[C]<",
}

def convert(text, lang):
    for old, new in ALT_CAMERA_TOKENS.items():
        text = text.replace(old, new)
    for old, new in PHRASES.get(lang, {}).items():
        text = text.replace(old, new)
    for token in TOKENS:
        text = text.replace(token, BUTTON_LABEL[lang][token])
    return text

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("en", "es"):
        raise SystemExit("Uso: localize_controller_texts.py en|es")
    lang = sys.argv[1]
    path = BUILD / lang / "dialogs.json"
    rows = json.loads(path.read_text(encoding="utf-8"))

    changed = []
    for row in rows:
        if row["id"] not in AFFECTED:
            continue
        old = row["text"]
        new = convert(old, lang)
        row["text"] = new
        if old != new:
            changed.append(row["id"])

    leftovers = [
        {"id": row["id"], "tokens": LEGACY_RE.findall(row["text"])}
        for row in rows
        if LEGACY_RE.search(row["text"])
    ]
    if leftovers:
        raise RuntimeError(f"Legacy N64 control tokens remain: {leftovers}")

    out = BUILD / lang / "dialogs_xbox360.json"
    out.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = {
        "language": lang,
        "dialogs_total": len(rows),
        "controller_dialogs_expected": len(AFFECTED),
        "dialogs_changed": changed,
        "legacy_tokens_remaining": 0,
    }
    (BUILD / lang / "controller_localization_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
