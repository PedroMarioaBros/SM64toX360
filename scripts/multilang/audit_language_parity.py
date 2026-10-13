#!/usr/bin/env python3
"""Audit reproducible EN→ES control coverage for SM64 Xbox multilingual text.

Does not assert automatic full semantic translation equivalence. The game
source is external, held in _localization_sources at pinned commits; only
counts, findings, and IDs may be published. No proprietary game content
included in reports.

Usage:
  python3 scripts/multilang/audit_language_parity.py --output docs/...
Requires import_text_sources.py + localize_controller_texts.py en|es first.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "_localization_build"
SOURCE_LOCK = ROOT / "localization/manifests/source_lock.json"
CANONICAL_DIALOGS = 170

N64_LABELS = {
    "A": r"\[A\]",
    "X": r"\[B\]",
    "LT/LB": r"\[Z\]",
    "RB/RT": r"\[R\]",
    "CAMERA_STICK": r"\[C\]",
    "MOVE_STICK": r"\bControl Stick\b",
}
ES_LABELS = {
    "A": r"\bA\b",
    "X": r"\bX\b",
    "LT/LB": r"\bLT/LB\b",
    "RB/RT": r"\bRB/RT\b",
    "CAMERA_STICK": r"\bstick derecho\b",
    "MOVE_STICK": r"\bstick izquierdo\b",
}
EN_LABELS = {
    "A": r"\bA\b",
    "X": r"\bX\b",
    "LT/LB": r"\bLT/LB\b",
    "RB/RT": r"\bRB/RT\b",
    "CAMERA_STICK": r"\bright stick\b",
    "MOVE_STICK": r"\bleft stick\b",
}
LEGACY = re.compile(r"\[(?:A|B|Z|R|C(?:\^|\||[<>]|[▲▼▶◀])?)\]")
NEUTRAL_INPUT_RE = re.compile(
    r"\b(?:Control Stick|control stick|stick de control|stick analógico)\b"
)

def _ids(rows, lang):
    ids = [x["id"] for x in rows]
    if ids != list(range(CANONICAL_DIALOGS)):
        raise ValueError(f"{lang}: IDs must be exactly 000..169 in order")
    if any(not isinstance(x["text"], str) or not x["text"].strip() for x in rows):
        raise ValueError(f"{lang}: dialog text empty or invalid")


def _classes(text, patterns):
    return {name for name, pattern in patterns.items() if re.search(pattern, text)}


def audit(en_source, en_xbox, es_source, es_xbox, pt_pool_sha=None):
    for label, rows in (
        ("en original", en_source), ("en Xbox", en_xbox),
        ("es original", es_source), ("es Xbox", es_xbox),
    ):
        _ids(rows, label)

    missing = []
    surviving_tokens = []
    neutral_tokens = []
    control_delta = []
    for did in range(CANONICAL_DIALOGS):
        original = en_source[did]["text"]
        eng = en_xbox[did]["text"]
        esp = es_xbox[did]["text"]
        expected = _classes(original, N64_LABELS)
        # Always allow *semantic* N64 left-stick references only where English
        # explicitly mentions them. Right-stick patterns also include [C]^ etc.
        actual_en, actual_es = _classes(eng, EN_LABELS), _classes(esp, ES_LABELS)
        # 'A' as a standalone Spanish preposition is an approximate detection;
        # this checks presence, not exact tutorial semantics.
        absent_en = expected - actual_en
        absent_es = expected - actual_es
        if absent_en or absent_es:
            missing.append({
                "id":did, "expected":sorted(expected),
                "missing_en":sorted(absent_en), "missing_es":sorted(absent_es)
            })
        extra_es = actual_es - expected
        if extra_es:
            control_delta.append({"id":did,"additional_es_labels":sorted(extra_es)})
        for lang, text in (("en",eng),("es",esp)):
            if LEGACY.search(text):
                surviving_tokens.append({"id":did,"language":lang})
            if NEUTRAL_INPUT_RE.search(text):
                neutral_tokens.append({"id":did,"language":lang})

    source_refs=json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))["sources"]
    report = {
        "schema":1,
        "status":"PASS_INPUT_CLASS_COVERAGE" if not (missing or surviving_tokens or neutral_tokens)
                 else "FAIL_INPUT_CLASS_COVERAGE",
        "sources":{
            "en":source_refs["sm64_upstream"]["repository"]+"@"+source_refs["sm64_upstream"]["commit"],
            "es":source_refs["es_reonu"]["repository"]+"@"+source_refs["es_reonu"]["commit"]
        },
        "dialogs_per_language":{lang:CANONICAL_DIALOGS for lang in ("pt_br","es","en")},
        "pt_br_source":"canonic 30 FPS v0.4 fixed, not modified by EN/ES scripts",
        "pt_br_dialog_pool_sha256_from_prior_binary_audit":pt_pool_sha,
        "pt_br_binary_rechecked_in_this_audit":False,
        "missing_input_classes":missing,
        "remaining_legacy_n64_tokens":surviving_tokens,
        "ambiguous_n64_analog_references":neutral_tokens,
        "additional_es_control_labels":control_delta,
        "note":"A PASS confirms IDs and coverage of Xbox controller categories, NOT "
               "human-certified equivalence of all dialogues/courses/menus.",
        "human_translation_parity_certified":False,
        "in_game_xbox_test_completed":False,
    }
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()

    def read(lang,file):
        return json.loads((BUILD/lang/file).read_text(encoding="utf-8"))

    sizes=json.loads((ROOT/"docs/MULTILANG_TEXT_SIZE_REPORT.json").read_text())
    pt_pool=sizes["dialogs"]["pt_br"]["sha256"]
    result=audit(read("en","dialogs.json"),read("en","dialogs_xbox360.json"),
                 read("es","dialogs.json"),read("es","dialogs_xbox360.json"),
                 pt_pool_sha=pt_pool)
    data=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
    print(data)
    if result["status"]!="PASS_INPUT_CLASS_COVERAGE":
        raise SystemExit("Localization has missing/legacy Xbox input instruction categories")


if __name__=="__main__":
    main()
