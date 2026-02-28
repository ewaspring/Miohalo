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

# Fallback transliteration hints for letters that are uncommon in Unicode sign names.
FALLBACK_TOKEN_HINTS: dict[str, tuple[str, ...]] = {
    "C": ("KA", "KU", "GA"),
    "F": ("PA", "PI", "PU"),
    "J": ("IA", "I", "YA"),
    "Q": ("QA", "KA", "K"),
    "V": ("WA", "U", "UB"),
    "W": ("WA", "WE", "WI", "WU", "U"),
    "Y": ("YA", "IA", "I"),
}


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


def _extract_tokens(name: str) -> list[str]:
    body = name.removeprefix("CUNEIFORM SIGN ")
    return [t for t in re.split(r"[^A-Z0-9]+", body) if t]


def _rank_candidates(signs: list[dict], letter: str) -> list[tuple[int, int, str, dict]]:
    hints = FALLBACK_TOKEN_HINTS.get(letter, ())
    ranked: list[tuple[int, int, str, dict]] = []

    for sign in signs:
        name = sign["name"]
        if not name.startswith("CUNEIFORM SIGN "):
            continue

        tokens = _extract_tokens(name)

        stage = None
        if any(tok == letter for tok in tokens):
            stage = 0
        elif any(tok.startswith(letter) and tok.isalpha() for tok in tokens):
            stage = 1
        elif any(letter in tok and tok.isalpha() for tok in tokens):
            stage = 2
        elif hints and any(tok.startswith(hint) for hint in hints for tok in tokens):
            stage = 3

        if stage is None:
            continue

        ranked.append((stage, len(name), name, sign))

    return sorted(ranked)


def select_for_letters(signs: list[dict]) -> dict[str, dict]:
    selections: dict[str, dict] = {}
    used_codepoints: set[str] = set()

    ranked_by_letter = {letter: _rank_candidates(signs, letter) for letter in LATIN_26}
    letter_order = sorted(LATIN_26, key=lambda letter: len(ranked_by_letter[letter]))

    for letter in letter_order:
        ranked = ranked_by_letter[letter]
        chosen = next((item for item in ranked if item[3]["codepoint"] not in used_codepoints), None)
        if chosen is None and ranked:
            chosen = ranked[0]

        if chosen is None:
            # Last-resort deterministic fallback: pick the shortest sign name not used yet.
            pool = [
                s
                for s in signs
                if s["name"].startswith("CUNEIFORM SIGN ") and s["codepoint"] not in used_codepoints
            ]
            if not pool:
                pool = [s for s in signs if s["name"].startswith("CUNEIFORM SIGN ")]
            forced = sorted(pool, key=lambda s: (len(s["name"]), s["name"]))[0]
            selections[letter] = {
                "letter": letter,
                "status": "selected",
                "char": forced["char"],
                "codepoint": forced["codepoint"],
                "name": forced["name"],
                "reason": "Fallback fill to complete 26/26 coverage.",
            }
            used_codepoints.add(forced["codepoint"])
            continue

        stage, _, _, sign = chosen
        stage_reason = {
            0: "Exact token match.",
            1: "Token-prefix match.",
            2: "Token-contains-letter match.",
            3: "Phonetic fallback token hint match.",
        }[stage]

        selections[letter] = {
            "letter": letter,
            "status": "selected",
            "char": sign["char"],
            "codepoint": sign["codepoint"],
            "name": sign["name"],
            "reason": f"Auto-picked by staged heuristic. {stage_reason}",
        }
        used_codepoints.add(sign["codepoint"])

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
