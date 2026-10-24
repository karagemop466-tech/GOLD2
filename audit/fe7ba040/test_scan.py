#!/usr/bin/env python3
"""Mutation controls for audit/fe7ba040/hallucination_provenance_scan.py.

A scanner that passes on the real tree proves nothing unless it also *fails* when a
defect is injected. Each control copies the minimum file set the scanner reads into a
temporary tree, applies one defect, and asserts the expected check family reports a
failure. The unmutated copy must PASS.

Run:
    python3 audit/fe7ba040/test_scan.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import hallucination_provenance_scan as scan  # noqa: E402

ROOT_HTML = [
    "index.html", "solid-gold.html", "solitaire.html", "halo-pave.html",
    "three-stone-vintage.html", "18k.html", "budget.html", "retailers.html",
    "analysis.html", "verification.html", "prices.html", "flags.html", "methods.html",
]


def build_tree(dest: Path) -> None:
    shutil.copytree(REPO / "data", dest / "data")
    (dest / "evidence").mkdir()
    shutil.copy(REPO / "evidence" / "gold-price.md", dest / "evidence" / "gold-price.md")
    (dest / "research").mkdir()
    shutil.copy(REPO / "research" / "evidence.json", dest / "research" / "evidence.json")
    for page in ROOT_HTML:
        shutil.copy(REPO / page, dest / page)


def families_of(failures: list[str]) -> set[str]:
    return {f.split("]", 1)[0].lstrip("[") for f in failures}


# ------------------------------------------------------------------ mutators
def mutate_stale_gold(root: Path) -> None:
    """Expose a superseded gold value on a rendered page."""
    p = root / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace("3,995.47", "4,028.53"), encoding="utf-8")


def mutate_missing_root_url(root: Path) -> None:
    """Point a catalog product's source record at a URL that is not a root URL."""
    p = root / "research" / "evidence.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for s in d["sources"]:
        if s.get("id") == "ag-coffin-ring":
            s["url"] = "https://www.example.invalid/products/coffin-ring"
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def mutate_bad_catalog_host(root: Path) -> None:
    """Point a catalog product at a non-official host."""
    p = root / "research" / "evidence.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for s in d["sources"]:
        if s.get("id") == "ag-24k":
            s["url"] = "https://www.example.invalid/24k-band"
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def mutate_flag_count(root: Path) -> None:
    """Change a flag title's stated count away from its affected_items length."""
    p = root / "data" / "flags.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for f in d["flags"]:
        if f.get("id") == "F-001":
            f["title"] = f["title"].replace("17 of 30", "16 of 30")
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def mutate_price_no_currency(root: Path) -> None:
    """Give a priced catalog product no stated currency."""
    p = root / "data" / "catalog.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for prod in d["products"]:
        if prod.get("id") == "ag-natural" and (prod.get("price") or {}).get("amount") is not None:
            prod["price"]["currency"] = None
            break
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def mutate_silent_zero(root: Path) -> None:
    """Replace a null fine-gold field with a silent zero."""
    p = root / "data" / "catalog.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for prod in d["products"]:
        facts = prod.get("facts", {})
        if facts.get("netMetalWeightG") is None and facts.get("karat"):
            facts["netMetalWeightG"] = 0
            break
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def mutate_drop_policy(root: Path) -> None:
    """Remove the No-Hallucinations banner from one page."""
    p = root / "methods.html"
    text = p.read_text(encoding="utf-8").lower().replace("no hallucinations", "no policy text")
    p.write_text(text, encoding="utf-8")


def mutate_gold_evidence(root: Path) -> None:
    """Drop the current value from the gold evidence markdown."""
    p = root / "evidence" / "gold-price.md"
    p.write_text(p.read_text(encoding="utf-8").replace("3,995.47", ""), encoding="utf-8")


def mutate_row_link(root: Path) -> None:
    """Remove one item's official URL from its category page."""
    p = root / "solid-gold.html"
    p.write_text(
        p.read_text(encoding="utf-8").replace(
            "https://www.automicgold.com/products/coffin-ring", ""),
        encoding="utf-8")


CONTROLS = [
    ("stale gold value rendered", mutate_stale_gold, "gold-currency"),
    ("root URL missing from catalog", mutate_missing_root_url, "url-coverage"),
    ("catalog product on bad host", mutate_bad_catalog_host, "url-coverage"),
    ("flag title count mismatch", mutate_flag_count, "flag-counts"),
    ("priced amount without currency", mutate_price_no_currency, "null-semantics"),
    ("null fine-gold replaced by zero", mutate_silent_zero, "null-semantics"),
    ("policy banner removed", mutate_drop_policy, "policy"),
    ("gold evidence value dropped", mutate_gold_evidence, "gold-evidence"),
    ("category row link removed", mutate_row_link, "row-links"),
]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "tree"
        build_tree(root)

        # Baseline: unmutated copy must pass.
        fams, errs = scan.scan(root)
        ok = not errs
        print(("  PASS " if ok else "  FAIL ") + "baseline unmutated tree passes")
        if not ok:
            failures += 1
            for e in errs:
                print("        " + e)

        for name, mutate, expected in CONTROLS:
            mutate(root)
            fams, errs = scan.scan(root)
            caught = expected in families_of(errs)
            print(("  PASS " if caught else "  FAIL ") + f"control catches: {name}")
            if not caught:
                failures += 1
                print(f"        expected family '{expected}'; failures={errs}")
            # restore the pristine tree for the next control
            shutil.rmtree(root)
            build_tree(root)

    print(f"\nmutation controls: {'PASS' if failures == 0 else 'FAIL'} "
          f"({len(CONTROLS) + 1 - failures}/{len(CONTROLS) + 1})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
