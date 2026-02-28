#!/usr/bin/env python3
"""Build a local cuneiform library and select A-Z candidate signs.

Usage:
  python cuneiform-alphabet-table/scripts/select_cuneiform.py --build-library
  python cuneiform-alphabet-table/scripts/select_cuneiform.py --select
  python cuneiform-alphabet-table/scripts/select_cuneiform.py --build-library --select
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Unicode blocks that contain cuneiform signs.
CUNEIFORM_BLOCKS = (
    (0x12000, 0x123FF, "Cuneiform"),
    (0x12400, 0x1247F, "Cuneiform Numbers and Punctuation"),
    (0x12480, 0x1254F, "Early Dynastic Cuneiform"),
)

LATIN_26 = [chr(v) for v in range(ord("A"), ord("Z") + 1)]


@dataclass
class Sign:
    char: str
    codepoint: str
    name: str
    block: str


def iter_cuneiform_signs() -> Iterable[Sign]:
    for start, end, block_name in CUNEIFORM_BLOCKS:
        for cp in range(start, end + 1):
            ch = chr(cp)
            name = unicodedata.name(ch, "")
            if not name:
                continue
            yield Sign(
                char=ch,
                codepoint=f"U+{cp:05X}",
                name=name,
                block=block_name,
            )


def build_library(raw_json: Path, raw_csv: Path) -> list[dict]:
    signs = [s.__dict__ for s in iter_cuneiform_signs()]

    raw_json.parent.mkdir(parents=True, exist_ok=True)
    with raw_json.open("w", encoding="utf-8") as f:
        json.dump(signs, f, ensure_ascii=False, indent=2)

    with raw_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["char", "codepoint", "name", "block"])
        writer.writeheader()
        writer.writerows(signs)

    return signs


def _score(name: str, token: str) -> tuple[int, int, str]:
    # Prefer exact "SIGN X" names, shorter names, then lexical order.
    exact = 0 if name.endswith(f"SIGN {token}") else 1
    return (exact, len(name), name)


def select_for_letters(signs: list[dict]) -> dict[str, dict]:
    selections: dict[str, dict] = {}

    for letter in LATIN_26:
        token = re.compile(rf"\b{re.escape(letter)}\b")
        candidates = [
            s
            for s in signs
            if s["name"].startswith("CUNEIFORM SIGN ") and token.search(s["name"])
        ]

        if not candidates:
            selections[letter] = {
                "letter": letter,
                "status": "missing",
                "char": "",
                "codepoint": "",
                "name": "",
                "reason": "No direct token hit in Unicode cuneiform names.",
            }
            continue

        chosen = sorted(candidates, key=lambda s: _score(s["name"], letter))[0]
        selections[letter] = {
            "letter": letter,
            "status": "selected",
            "char": chosen["char"],
            "codepoint": chosen["codepoint"],
            "name": chosen["name"],
            "reason": "Auto-picked by exact token/short-name heuristic.",
        }

    return selections


def write_selection_outputs(selection: dict[str, dict], out_json: Path, out_csv: Path, out_md: Path) -> None:
    rows = [selection[l] for l in LATIN_26]

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["letter", "status", "char", "codepoint", "name", "reason"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Cuneiform A-Z Candidate Selection (auto)\n\n")
        f.write("| Letter | Status | Sign | Codepoint | Unicode Name | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in rows:
            sign = r["char"] if r["char"] else "-"
            name = r["name"] if r["name"] else "-"
            f.write(
                f"| {r['letter']} | {r['status']} | {sign} | {r['codepoint'] or '-'} | {name} | {r['reason']} |\n"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cuneiform library and select A-Z candidates.")
    parser.add_argument("--build-library", action="store_true", help="Extract Unicode cuneiform signs to data/raw.")
    parser.add_argument("--select", action="store_true", help="Generate A-Z candidate selections to data/processed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.build_library and not args.select:
        raise SystemExit("Please pass --build-library and/or --select")

    root = Path(__file__).resolve().parents[1]
    raw_json = root / "data" / "raw" / "cuneiform_unicode_library.json"
    raw_csv = root / "data" / "raw" / "cuneiform_unicode_library.csv"

    signs: list[dict]
    if args.build_library:
        signs = build_library(raw_json=raw_json, raw_csv=raw_csv)
        print(f"[ok] library built: {len(signs)} signs")
    else:
        if not raw_json.exists():
            raise SystemExit("Library missing. Run with --build-library first.")
        signs = json.loads(raw_json.read_text(encoding="utf-8"))

    if args.select:
        selection = select_for_letters(signs)
        out_json = root / "data" / "processed" / "az_cuneiform_selection.json"
        out_csv = root / "data" / "processed" / "az_cuneiform_selection.csv"
        out_md = root / "data" / "processed" / "az_cuneiform_selection.md"
        write_selection_outputs(selection, out_json, out_csv, out_md)
        selected = sum(1 for v in selection.values() if v["status"] == "selected")
        print(f"[ok] A-Z selection generated: {selected}/26 letters matched")


if __name__ == "__main__":
    main()
