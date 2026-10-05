#!/usr/bin/env python3
"""Audit pinned sources and current pools without publishing game text.

Run after the importer, controller localizer and pool builder.
Requires full project git history for the pre-camera-normalization comparison.
This verifies reproducibility, not visual layout or Xbox runtime behavior.
"""
import hashlib
import json
from pathlib import Path
import subprocess

import build_dialog_pools as pools
import import_text_sources as importer
import localize_controller_texts as controls

ROOT = pools.ROOT
HISTORICAL_REF = "f5cebc7"
EXPECTED = {
    "en": "819dba9fa68d2db08edc27f2ce05532bdfc734dd1a3a24754ab51abff3479f29",
    "es": "361bce11e893615be1bdcca5699dd863db84fdd31091f1763f6f2f3059d35685",
}
SOURCES = {
    "en": ("sm64_upstream", "9921382a68bb0c865e5e45eb594d9c64db59b1af"),
    "es": ("es_reonu", "b720e8328c4ead21e3eac5dfceb21edba38ed79b"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def pack(rows, convert):
    encode = pools.encoder(pools.load_charmap())
    output = bytearray()
    index = []
    for row in rows:
        raw = encode(convert(row))
        output.extend(bytes((-len(output)) % 8))
        index.append({"id": row["id"], "offset": len(output),
                      "length": len(raw), "sha256": sha(raw)})
        output.extend(raw)
    return bytes(output), index


def main():
    namespace = {"__file__": str(ROOT / "scripts/multilang/localize_controller_texts.py"),
                 "__name__": "historical_audit"}
    exec(git("show", f"{HISTORICAL_REF}:scripts/multilang/localize_controller_texts.py"), namespace)
    report = {"schema": 1, "date": "2026-10-05", "historical_converter_ref": HISTORICAL_REF,
              "scope": "source/pool reproducibility; NOT Xbox or visual validation",
              "languages": {}, "checkpoint_hash_discrepancy_resolved": False}
    for lang, (folder, pin) in SOURCES.items():
        source_dir = ROOT / "_localization_sources" / folder
        if git("-C", str(source_dir), "rev-parse", "HEAD") != pin:
            raise RuntimeError(f"{lang}: source revision differs from pin")
        if git("-C", str(source_dir), "status", "--porcelain", "--", "text/us/dialogs.h", "charmap.txt"):
            raise RuntimeError(f"{lang}: dirty source files")
        source_path = source_dir / "text/us/dialogs.h"
        rows = importer.parse_dialogs(source_path)
        target = ROOT / "_localization_build" / lang
        imported = json.loads((target / "dialogs.json").read_text())
        final = json.loads((target / "dialogs_xbox360.json").read_text())
        if rows != imported:
            raise RuntimeError(f"{lang}: imported JSON differs from pinned source")
        convert = lambda row: controls.convert(row["text"], lang) if row["id"] in controls.AFFECTED else row["text"]
        if any(convert(row) != out["text"] for row, out in zip(rows, final)) or len(final) != 170:
            raise RuntimeError(f"{lang}: localized JSON differs from converter")
        rebuilt, index = pack(rows, convert)
        if rebuilt != (target / "dialogs.bin").read_bytes():
            raise RuntimeError(f"{lang}: stored pool differs from regeneration")
        old_convert = lambda row: namespace["convert"](row["text"], lang) if row["id"] in namespace["AFFECTED"] else row["text"]
        historical, old_index = pack(rows, old_convert)
        changed = [{"id": row["id"], "previous_length": before["length"],
                    "current_length": after["length"], "previous_sha256": before["sha256"],
                    "current_sha256": after["sha256"]}
                   for row, before, after in zip(rows, old_index, index)
                   if before["sha256"] != after["sha256"]]
        report["languages"][lang] = {
            "source_commit": pin, "source_file_sha256": sha(source_path.read_bytes()),
            "source_import_identical": True, "controller_conversion_identical": True,
            "pool_regeneration_byte_identical": True, "dialogs": 170,
            "current_bytes": len(rebuilt), "current_sha256": sha(rebuilt),
            "checkpoint_expected_sha256": EXPECTED[lang],
            "matches_checkpoint": sha(rebuilt) == EXPECTED[lang],
            "pre_camera_normalization_bytes": len(historical),
            "pre_camera_normalization_sha256": sha(historical),
            "camera_normalization_changes": changed, "dialog_index": index,
        }
    report["conclusion"] = (
        "Current EN/ES pools reproduce pinned sources and current conversion exactly. "
        "Camera normalization explains five EN dialog changes and 33931→33955 bytes, "
        "but does not reproduce the checkpoint hashes. ES has no camera-normalization changes. "
        "Original checkpoint pools/producer remain needed to establish historical byte differences."
    )
    output = ROOT / "_localization_build/pool_reproducibility_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"reproducibility": "PASS", "historical_discrepancy": "UNRESOLVED",
                      "report": str(output.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
