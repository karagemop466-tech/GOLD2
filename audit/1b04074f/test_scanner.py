#!/usr/bin/env python3
"""Mutation controls for audit/1b04074f/hallucination_scanner.py.

A scanner that always passes is worthless. Each control below copies the
repository into a temporary directory, injects exactly one defect of a class
the scanner claims to catch, and asserts that the scanner fails with that
control id. Any surviving mutation is reported as a scanner defect.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
IGNORE = shutil.ignore_patterns(".git", "node_modules", "test-results", "__pycache__", ".cache")


def clone(tmp: pathlib.Path) -> pathlib.Path:
    dst = tmp / "repo"
    shutil.copytree(REPO, dst, ignore=IGNORE)
    return dst


def run(root: pathlib.Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(root / "audit/1b04074f/hallucination_scanner.py"), str(root)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def edit_json(path: pathlib.Path, mutate) -> None:
    d = json.loads(path.read_text())
    mutate(d)
    path.write_text(json.dumps(d, indent=2) + "\n")


def m_c02(root: pathlib.Path) -> None:
    def mut(d):
        d["items"][0]["price"] = 123.45
    edit_json(root / "data/solid-gold-verified.json", mut)


def m_c03(root: pathlib.Path) -> None:
    def mut(d):
        d["items"][0]["flags"] = list(d["items"][0].get("flags", [])) + ["F-999"]
    edit_json(root / "data/solid-gold-verified.json", mut)


def m_c05(root: pathlib.Path) -> None:
    p = root / "index.html"
    p.write_text(p.read_text().replace("</body>", "<p>3,996.31 / troy oz</p></body>", 1))


def m_c09(root: pathlib.Path) -> None:
    def mut(d):
        d["products"][0]["source"] = "nonexistent-source"
    edit_json(root / "data/catalog.json", mut)


def m_c10(root: pathlib.Path) -> None:
    def mut(d):
        for p in d["products"]:
            if p.get("price") and p["price"].get("amount") is not None:
                p["price"]["evidence"] = [{"source": "nope", "quote": "none"}]
                break
    edit_json(root / "data/catalog.json", mut)


def m_c11(root: pathlib.Path) -> None:
    p = root / "methods.html"
    t = p.read_text()
    for bad in ("No hallucinations", "no hallucination", "No invented prices", "no invented prices",
                "Zero-hallucination", "zero-hallucination", "no-hallucinations"):
        t = t.replace(bad, "Policy")
    p.write_text(t)


def m_c06(root: pathlib.Path) -> None:
    def mut(d):
        d["spot_usd_per_troy_oz"] = 4000.00
    edit_json(root / "dashboard/data/gold-reference.json", mut)


def m_c14(root: pathlib.Path) -> None:
    def mut(d):
        d["items"][0]["source_url"] = "https://example.com/not-in-register"
    edit_json(root / "data/solid-gold-verified.json", mut)


MUTATIONS = [
    ("C02", m_c02, "assigned price without evidence"),
    ("C03", m_c03, "listing references an undefined flag"),
    ("C05", m_c05, "superseded gold value rendered"),
    ("C06", m_c06, "dashboard spot disagrees with root register"),
    ("C09", m_c09, "product points at a missing source"),
    ("C10", m_c10, "price evidence key removed"),
    ("C11", m_c11, "no-hallucination policy removed from a page"),
    ("C14", m_c14, "root row URL absent from combined register"),
]


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        base = clone(pathlib.Path(td))
        code, out = run(base)
        print(f"  clean copy: exit {code} (expected 0)")
        if code != 0:
            failures += 1
            print(out)
    for cid, fn, label in MUTATIONS:
        with tempfile.TemporaryDirectory() as td:
            root = clone(pathlib.Path(td))
            fn(root)
            code, out = run(root)
            caught = code != 0 and cid in out
            print(f"  {'PASS' if caught else 'FAIL'} {cid} {label}: exit {code}")
            if not caught:
                failures += 1
                print(out[-1200:])
    total = len(MUTATIONS) + 1
    print(f"mutation controls: {total - failures}/{total} correct")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
