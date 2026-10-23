#!/usr/bin/env python3
"""
Mutation-control tests for audit/f03ab52d/hallucination_audit.py.

Each test copies the committed data into a temp root, injects ONE defect, and
asserts the scanner reports the expected check as FAIL. A scanner that cannot
catch an injected hallucination is not a scanner. Run with:

    python3 audit/f03ab52d/test_audit.py
"""
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import hallucination_audit as ha  # noqa: E402

IGNORE = shutil.ignore_patterns(".git", "node_modules", "test-results", "*.pyc", "__pycache__")


def make_root(tmp):
    dst = Path(tmp) / "repo"
    shutil.copytree(ROOT, dst, ignore=IGNORE)
    return dst


def write(root, rel, obj):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def read(root, rel):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def failed_ids(rep):
    return {c["id"] for c in rep.checks if c["status"] == "FAIL"}


def expect_fail(name, root, expected):
    rep = ha.run(root)
    ids = failed_ids(rep)
    ok = expected in ids
    print(f"  [{'ok' if ok else 'BAD'}] {name}: expected {expected} FAIL, got {sorted(ids)}")
    if not ok:
        print("       summary:", rep.summary())
    return ok


def main():
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = make_root(tmp)

        # M1 — price amount invented (not in any evidence quote)
        r = make_root(tmp + "_m1")
        cat = read(r, "data/catalog.json")
        p = [x for x in cat["products"] if x["id"] == "ag-coffin-ring"][0]
        p["price"]["amount"] = 9999
        write(r, "data/catalog.json", cat)
        n += expect_fail("M1 invented price", r, "C2")

        # M2 — karat value changed away from the quote
        r = make_root(tmp + "_m2")
        cat = read(r, "data/catalog.json")
        p = [x for x in cat["products"] if x["id"] == "ag-natural"][0]
        p["facts"]["karat"]["value"] = 18
        write(r, "data/catalog.json", cat)
        n += expect_fail("M2 karat mismatch", r, "C2")

        # M3 — solidGold=True but the backing quote no longer says solid gold
        r = make_root(tmp + "_m3")
        ev = read(r, "research/evidence.json")
        for s in ev["sources"]:
            if s["id"] == "ag-natural":
                s["quotes"]["material"] = "950 platinum"
        write(r, "research/evidence.json", ev)
        n += expect_fail("M3 solidGold unbacked", r, "C2")

        # M4 — a product source URL downgraded to http
        r = make_root(tmp + "_m4")
        ev = read(r, "research/evidence.json")
        for s in ev["sources"]:
            if s["id"] == "ag-natural":
                s["url"] = "http://www.automicgold.com/products/natural"
        write(r, "research/evidence.json", ev)
        n += expect_fail("M4 non-https source", r, "C1")

        # M5 — an unrecorded gold figure injected into the evidence md
        r = make_root(tmp + "_m5")
        md = (r / "evidence/gold-price.md").read_text(encoding="utf-8")
        md = md.replace("3,996.31", "3,996.31\n\nAnomalous reading 4,321.00\n")
        (r / "evidence/gold-price.md").write_text(md, encoding="utf-8")
        n += expect_fail("M5 unrecorded gold figure", r, "C5")

        # M6 — gold JSON value changed away from the evidence md
        r = make_root(tmp + "_m6")
        g = read(r, "data/gold-price.json")
        g["usd_per_troy_oz"] = 1234.56
        write(r, "data/gold-price.json", g)
        n += expect_fail("M6 gold JSON mismatch", r, "C5")

        # M7 — hallmark claimed true with no stamp wording in the evidence file
        r = make_root(tmp + "_m7")
        sg = read(r, "data/solid-gold-verified.json")
        for it in sg["items"]:
            if it["id"] == "SS-CLARA":
                it["hallmark_stated"] = True
        write(r, "data/solid-gold-verified.json", sg)
        n += expect_fail("M7 hallmark unbacked", r, "C7")

        # M8 — root price contradicts the combined catalog price
        r = make_root(tmp + "_m8")
        sg = read(r, "data/solid-gold-verified.json")
        for it in sg["items"]:
            if it["id"] == "AG-COFFIN-RING":
                it["price"] = 5000
        write(r, "data/solid-gold-verified.json", sg)
        n += expect_fail("M8 root/catalog price conflict", r, "C4")

        # M9 — a derived assay field populated without an evidence quote
        r = make_root(tmp + "_m9")
        cat = read(r, "data/catalog.json")
        p = [x for x in cat["products"] if x["id"] == "ag-natural"][0]
        p["facts"]["fineGoldWeightG"] = {"value": 0.7, "source": "ag-natural", "quote": "no-such-quote"}
        write(r, "data/catalog.json", cat)
        n += expect_fail("M9 derived value unbacked", r, "C6")

    print(f"\n{n}/9 mutation controls behaved as expected")
    return 0 if n == 9 else 1


if __name__ == "__main__":
    sys.exit(main())
