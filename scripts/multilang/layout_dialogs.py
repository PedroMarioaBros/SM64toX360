#!/usr/bin/env python3
"""Reflow EN/ES for v0.4 widths, retaining its per-dialog page geometry.

Usage: layout_dialogs.py glyphs.pe
Does not write the mapped image or alter PT-BR. Uses the same 125-unit limit
as the recovered v0.4 builder. Choice rows end on the last row of a page.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

from build_dialog_pools import ROOT, encoder, load_charmap

LIMIT = 125
CHOICES = {5, 9, 10, 11, 12, 13, 14, 55, 79, 164}
POINTER_BASE = 0x9E7CD8
WIDTH_BASE = 0x3C89B8


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: layout_dialogs.py glyphs.pe")
    image = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(image).hexdigest() != "5b4ec5d2f79ecc1cbe23b5d01b7657e4b7ac619937584ea09e2ec26443e2cdf1":
        raise RuntimeError("expected canonical v0.4 image with verified Spanish glyphs")
    widths = image[WIDTH_BASE:WIDTH_BASE + 256]
    if len(widths) != 256:
        raise RuntimeError("width table outside image")
    cm = load_charmap()
    encode = encoder(cm)
    special = {0xD0: widths[0x9E] * 2,
               0xD1: sum(widths[cm[c][0]] for c in "the"),
               0xD2: sum(widths[cm[c][0]] for c in "you"), 0xE0: 14}

    def width(text):
        return sum(special.get(byte, widths[byte]) for byte in encode(text)[:-1])

    def reflow(line):
        if width(line) <= LIMIT:
            return [line]
        result = []
        current = ""
        words = []
        for word in line.split():
            if width(word) > LIMIT:
                # Some Spanish source strings join phrases with ellipses.
                # Break at that punctuation without removing any characters.
                words.extend(part for part in re.split(r"(?<=\.\.\.)", word) if part)
            else:
                words.append(word)
        for word in words:
            if width(word) > LIMIT:
                raise RuntimeError(f"single word exceeds width limit: {word!r}")
            trial = (current + " " + word).strip()
            if current and width(trial) > LIMIT:
                result.append(current)
                current = word
            else:
                current = trial
        result.append(current)
        return result

    report = {"schema": 1, "date": "2026-10-05", "limit": LIMIT,
              "mapped_image_sha256": hashlib.sha256(image).hexdigest(),
              "geometry": "linesPerBox at pointer_member-8; no metadata writes",
              "languages": {}, "scope": "static layout checks; hardware pending"}
    for lang in ("en", "es"):
        folder = ROOT / "_localization_build" / lang
        rows = json.loads((folder / "dialogs_xbox360.json").read_text())
        changes = []
        overflow_before = 0
        widest = 0
        for row in rows:
            original = row["text"]
            old_lines = original.split("\n")
            widest = max(widest, max(map(width, old_lines)))
            overflow_before += any(width(line) > LIMIT for line in old_lines)
            lines = []
            for number, line in enumerate(old_lines):
                if row["id"] in CHOICES and number == len(old_lines) - 1:
                    # Slash byte D0 is a two-space renderer command, not an
                    # ink glyph. Reduce spacing only; keep both choice labels.
                    while width(line) > LIMIT:
                        runs = [match for match in re.finditer(r"/{2,}", line)]
                        if not runs:
                            raise RuntimeError(f"choice labels require editorial shortening: {lang}/{row['id']}")
                        longest = max(runs, key=lambda match: len(match[0]))
                        line = line[:longest.start()] + line[longest.start() + 1:]
                    lines.append(line)
                else:
                    lines.extend(reflow(line))
            page_lines = image[POINTER_BASE + row["id"] * 16 - 8]
            if not 1 <= page_lines <= 20:
                raise RuntimeError("invalid canonical linesPerBox")
            padding = 0
            if row["id"] in CHOICES:
                if not lines[-1].startswith("/"):
                    raise RuntimeError(f"{lang} choice row missing: {row['id']}")
                while len(lines) % page_lines:
                    lines.insert(-1, "")
                    padding += 1
            result = "\n".join(lines)
            before_check, after_check = original, result
            if row["id"] in CHOICES:
                before_check = before_check.replace("/", " ")
                after_check = after_check.replace("/", " ")
            if re.sub(r"\s+", "", before_check) != re.sub(r"\s+", "", after_check):
                raise RuntimeError("non-whitespace text changed")
            if any(width(line) > LIMIT for line in lines):
                raise RuntimeError("oversized output")
            if result != original:
                changes.append({"id": row["id"], "old_lines": len(old_lines),
                                "new_lines": len(lines), "page_lines": page_lines,
                                "choice_padding": padding,
                                "old_encoded_sha256": hashlib.sha256(encode(original)).hexdigest(),
                                "new_encoded_sha256": hashlib.sha256(encode(result)).hexdigest()})
            row["text"] = result
            row["lines"] = page_lines
        (folder / "dialogs_layout.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
        report["languages"][lang] = {"dialogs": len(rows), "oversized_dialogs_before": overflow_before,
                                     "max_width_before": widest, "oversized_lines_after": 0,
                                     "label_or_punctuation_changes": 0, "choice_rows_validated": len(CHOICES),
                                     "spacing_note": "D0 slash renderer spacers may be reduced on oversized choice rows; labels retained",
                                     "changes": changes}
    report["status"] = "PASS"
    (ROOT / "_localization_build/layout_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "languages": {lang: {key: value for key, value in data.items() if key != "changes"}
                                                             for lang, data in report["languages"].items()}}))


if __name__ == "__main__":
    main()
