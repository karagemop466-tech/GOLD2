#!/usr/bin/env python3
"""Mutation controls for audit/e0d6dd62/hallucination_and_count_scanner.py.

Each control copies the repository data into a temporary tree, injects one
realistic defect, and asserts that the scanner reports a failure for that
defect family. A scanner that passes on the real tree but also passes on a
doctored tree is worthless, so these controls are the actual evidence that the
checks work.

Run: python3 audit/e0d6dd62/test_scanner.py .
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCANNER = Path(__file__).resolve().parent / "hallucination_and_count_scanner.py"
COPY = ("data", "research", "evidence", "README.md")
HTML_GLOBS = ("*.html", "explore", "dashboard", "site")


def build_tree(root: Path, dest: Path) -> Path:
    for name in COPY:
        src = root / name
        if src.is_dir():
            shutil.copytree(src, dest / name, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, dest / name)
    for pattern in HTML_GLOBS:
        for path in root.glob(pattern) if pattern.endswith(".html") else [root / pattern]:
            if path.is_dir():
                shutil.copytree(path, dest / path.name, dirs_exist_ok=True)
            elif path.exists():
                shutil.copy2(path, dest / path.name)
    return dest


def run(tree: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SCANNER), str(tree)], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def mutate(*, data=None, readme=None, page=None, evidence=None):
    def apply(tree: Path) -> None:
        if data:
            rel, fn = data
            path = tree / rel
            obj = json.loads(path.read_text(encoding="utf-8"))
            fn(obj)
            path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if readme:
            path = tree / "README.md"
            path.write_text(path.read_text(encoding="utf-8").replace(*readme), encoding="utf-8")
        if page:
            rel, needle, replacement = page
            path = tree / rel
            path.write_text(path.read_text(encoding="utf-8").replace(needle, replacement), encoding="utf-8")
        if evidence:
            rel, needle, replacement = evidence
            path = tree / rel
            path.write_text(path.read_text(encoding="utf-8").replace(needle, replacement), encoding="utf-8")
    return apply


def invent_price(catalog):
    for product in catalog["products"]:
        if product["id"] == "ag-sapphire":
            product["price"]["amount"] = 4321.0


def drop_currency(catalog):
    for product in catalog["products"]:
        if product["id"] == "ag-sapphire":
            product["price"]["evidence"] = [r for r in product["price"]["evidence"] if r["source"] != "automic-currency"]


def stale_gold(gold):
    gold["superseded_observations"].append({
        "value": 3860.00,
        "currency": "USD",
        "quote_date": None,
        "retrieved_at": "2026-10-23",
        "status": "superseded_intraday",
        "reason": "mutation control",
    })


def flag_count(flags):
    for flag in flags["flags"]:
        if flag["id"] == "F-001":
            flag["affected_items"] = flag["affected_items"][:-5]


CONTROLS = [
    ("invented price with no supporting passage", mutate(data=("data/catalog.json", invent_price)), "[price]"),
    ("USD label without a currency statement", mutate(data=("data/catalog.json", drop_currency)), "[price]"),
    ("superseded gold value left in a rendered page",
     mutate(data=("data/gold-price.json", stale_gold),
            page=("index.html", "Flagged for Review", "Flagged for Review <strong>3,860.00</strong>")), "[stale-price]"),
    ("README count that no longer matches the data", mutate(readme=("44 product records", "45 product records")), "[stale-count]"),
    ("flag title count disagreeing with affected_items", mutate(data=("data/flags.json", flag_count)), "[flag-count]"),
    ("evidence file missing a quoted value", mutate(evidence=("evidence/listings/ag-coffin-ring.md", "Approximately 6.1g (gold) or 9.2g (platinum)", "Weight not published")), "[root-evidence]"),
    ("placeholder text published on a page", mutate(page=("index.html", "</body>", "<p>TODO rewrite</p></body>")), "[placeholder]"),
    ("gold figure in the evidence file that no observation supports",
     mutate(evidence=("evidence/gold-price.md", "## Calculation boundaries", "A reading of 4,111.11 was seen.\n\n## Calculation boundaries")), "[gold-evidence]"),
]


def main(root: Path) -> int:
    base_code, base_out = run(root)
    if base_code != 0:
        print("baseline tree already fails; mutation controls are meaningless until it passes")
        print(base_out[-2000:])
        return 1
    print(f"  baseline: scanner PASS on the unmodified tree ({len(CONTROLS)} controls)")

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        clean = build_tree(root, Path(tmp) / "clean")
        for index, (label, apply, family) in enumerate(CONTROLS):
            tree = Path(tmp) / f"mutation-{index}"
            shutil.copytree(clean, tree)
            apply(tree)
            code, out = run(tree)
            if code == 0 or family not in out:
                failures += 1
                print(f"  FAIL control not detected: {label} (expected {family})")
                print("       " + out.strip().splitlines()[-1])
            else:
                matches = [line.strip() for line in out.splitlines() if line.strip().startswith("FAIL " + family)]
                print(f"  PASS detected: {label}\n       {matches[0] if matches else out.strip().splitlines()[-1]}")

    print(f"\nRESULT: {'PASS' if not failures else 'FAIL'} — {len(CONTROLS) - failures}/{len(CONTROLS)} mutation controls detected")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
