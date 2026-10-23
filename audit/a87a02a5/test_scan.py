#!/usr/bin/env python3
"""Negative controls for the S-A87A02A5 provenance scanner.

A scanner that always reports PASS proves nothing. Every test here injects one
specific defect into a throwaway copy of the committed registers and asserts the
scanner catches it, plus one positive control asserting the unmodified tree is
clean. Nothing in the real repository is modified: each case builds its own
fixture under a temporary directory.

Run:  python3 audit/a87a02a5/test_scan.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SCANNER = os.path.join(HERE, "hallucination_provenance_scan.py")

COPY_DIRS = ("data", "evidence", "research")
COPY_GLOBS = (
    "index.html", "solid-gold.html", "solitaire.html", "halo-pave.html",
    "three-stone-vintage.html", "18k.html", "budget.html", "retailers.html",
    "prices.html", "flags.html", "methods.html",
)


def build_fixture() -> str:
    """Copy only what the scanner reads into a fresh temp tree."""
    tmp = tempfile.mkdtemp(prefix="a87a02a5-scan-")
    for d in COPY_DIRS:
        src = os.path.join(REPO, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(tmp, d))
    import glob as _glob
    for pattern in COPY_GLOBS:
        for src in _glob.glob(os.path.join(REPO, pattern)):
            shutil.copy2(src, os.path.join(tmp, os.path.basename(src)))
    os.makedirs(os.path.join(tmp, "explore", "data"), exist_ok=True)
    cat = os.path.join(REPO, "explore", "data", "catalog.json")
    if os.path.exists(cat):
        shutil.copy2(cat, os.path.join(tmp, "explore", "data", "catalog.json"))
    return tmp


def run_scan(root: str):
    proc = subprocess.run(
        [sys.executable, SCANNER, root], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def find_melt_row(root: str):
    """Return (row_html, melt_amount, fine_gram_text) for one real melt row.

    Values are read from the committed page at run time rather than hardcoded,
    so these controls keep working when the gold reference or the register
    legitimately changes. Hardcoded constants here broke once already, on
    2026-10-23, when peers refreshed the quote from 4,028.53 to 4,024.45.
    """
    text = read_text(os.path.join(root, "prices.html"))
    for row in re.findall(r"<tr[^>]*>.*?</tr>", text, re.S):
        plain = re.sub(r"<[^>]+>", " ", row)
        if not re.search(r"\b\d{2}K\b", plain):
            continue
        grams = re.findall(r"\d+\.\d+\s*g", plain)
        amounts = re.findall(r"\$[\d,]+\.\d{2}", plain)
        if grams and amounts:
            return row, amounts[0], grams[-1]
    raise AssertionError("no melt row found in prices.html; fixture is unusable")


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def mutate_json(root: str, rel: str, fn):
    path = os.path.join(root, rel)
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    fn(data)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)


def first_item(data):
    return data["items"][0]


class ScannerNegativeControls(unittest.TestCase):
    def setUp(self):
        self.root = build_fixture()
        self.addCleanup(shutil.rmtree, self.root, True)

    def assert_catches(self, code: str, mutate, rel: str | None = None, raw=None):
        if rel is not None:
            mutate_json(self.root, rel, mutate)
        else:
            raw(self.root)
        rc, out = run_scan(self.root)
        self.assertEqual(rc, 1, f"scanner should exit 1 for {code}; output:\n{out[-2500:]}")
        self.assertIn(f"FAIL {code}", out, f"expected a {code} failure; output:\n{out[-2500:]}")

    # ---- positive control -------------------------------------------------
    def test_00_unmodified_tree_is_clean(self):
        rc, out = run_scan(self.root)
        self.assertEqual(rc, 0, f"unmodified registers must scan clean:\n{out[-3000:]}")
        self.assertIn("RESULT: PASS", out)

    # ---- C01 official source link ----------------------------------------
    def test_01_missing_source_url(self):
        def m(d): first_item(d)["source_url"] = None
        self.assert_catches("C01", m, "data/listings/solitaire.json")

    def test_02_offsite_source_url(self):
        def m(d): first_item(d)["source_url"] = "https://example.com/ring"
        self.assert_catches("C01", m, "data/listings/solitaire.json")

    def test_03_http_downgrade(self):
        def m(d):
            it = first_item(d)
            it["source_url"] = it["source_url"].replace("https://", "http://")
        self.assert_catches("C01", m, "data/listings/solitaire.json")

    # ---- C02 evidence file ------------------------------------------------
    def test_04_evidence_file_missing(self):
        def m(d): first_item(d)["evidence_file"] = "evidence/listings/does-not-exist.md"
        self.assert_catches("C02", m, "data/listings/solitaire.json")

    def test_05_evidence_file_url_mismatch(self):
        def raw(root):
            path = os.path.join(root, "evidence/listings/bn-203348.md")
            text = read_text(path)
            write_text(path, text.replace("item-203348", "item-999999"))
        self.assert_catches("C02", None, raw=raw)

    # ---- C04 invented price ----------------------------------------------
    def test_06_price_with_no_quote_at_all(self):
        def m(d):
            it = first_item(d)
            it["price"] = 4321.99
            it["currency"] = "USD"
            it["field_evidence"].pop("price", None)
        self.assert_catches("C04", m, "data/solid-gold-verified.json")

    def test_07_price_digits_not_in_quote(self):
        def m(d):
            it = next(x for x in d["items"] if x["id"] == "AG-SAPPHIRE-RING")
            it["price"] = 527.0  # quote says $526
        self.assert_catches("C04", m, "data/solid-gold-verified.json")

    def test_08_invented_weight(self):
        def m(d):
            it = next(x for x in d["items"] if x["id"] == "AG-SAPPHIRE-RING")
            it["weight_g"] = 3.3  # page states a 1.2 g gross item weight, no 3.3 g anywhere
        self.assert_catches("C05", m, "data/solid-gold-verified.json")

    # ---- C07/C08 currency discipline -------------------------------------
    def test_09_price_without_currency(self):
        def m(d):
            it = next(x for x in d["items"] if x["id"] == "AG-SAPPHIRE-RING")
            it["currency"] = None
        self.assert_catches("C07", m, "data/solid-gold-verified.json")

    def test_10_unsupported_iso_currency(self):
        def m(d):
            it = next(x for x in d["items"] if x["id"] == "BE-121H6")
            it["currency"] = "USD"  # quotes show EUR only; USD would be invented
            it["field_evidence"]["currency"] = ["\u20ac990.00"]
        self.assert_catches("C08", m, "data/listings/solitaire.json")

    # ---- C09/C10 flags and dates -----------------------------------------
    def test_11_unknown_flag_reference(self):
        def m(d): first_item(d)["flags"].append("F-999")
        self.assert_catches("C09", m, "data/listings/solitaire.json")

    def test_12_future_retrieval_date(self):
        def m(d): first_item(d)["retrieved_at"] = "2027-06-01"
        self.assert_catches("C10", m, "data/listings/solitaire.json")

    def test_13_malformed_retrieval_date(self):
        def m(d): first_item(d)["retrieved_at"] = "last tuesday"
        self.assert_catches("C10", m, "data/listings/solitaire.json")

    # ---- C16 arithmetic ---------------------------------------------------
    def test_14_wrong_gram_constant(self):
        def m(d): d["grams_per_troy_ounce"] = 31.1
        self.assert_catches("C16", m, "data/gold-price.json")

    def test_15_gold_quote_not_in_evidence(self):
        def m(d):
            d["usd_per_troy_oz"] = 4999.99
            d["evidence_quotes"] = ["4,028.53"]
            d.setdefault("field_evidence", {})["usd_per_troy_oz"] = ["4,028.53"]
        self.assert_catches("C16", m, "data/gold-price.json")

    def test_16_corrupted_melt_value_on_page(self):
        def raw(root):
            path = os.path.join(root, "prices.html")
            _row, melt, _fine = find_melt_row(root)
            text = read_text(path)
            self.assertIn(melt, text)
            write_text(path, text.replace(melt, "$999,999.99", 1))
        self.assert_catches("C16", None, raw=raw)

    def test_17_corrupted_fine_gold_on_page(self):
        def raw(root):
            path = os.path.join(root, "prices.html")
            _row, _melt, fine = find_melt_row(root)
            text = read_text(path)
            self.assertIn(fine, text)
            write_text(path, text.replace(fine, "9.999 g", 1))
        self.assert_catches("C16", None, raw=raw)

    # ---- C18 page/data reference parity ----------------------------------
    def test_18_page_shows_different_gold_reference(self):
        def raw(root):
            path = os.path.join(root, "index.html")
            with open(os.path.join(root, "data/gold-price.json"), encoding="utf-8") as fh:
                stored = json.load(fh)["usd_per_troy_oz"]
            want = f"{stored:,.2f}"          # derived from data, never typed
            text = read_text(path)
            self.assertIn(want, text, f"index.html should display the stored reference {want}")
            replacement = "4,099.99" if want != "4,099.99" else "4,000.01"
            write_text(path, text.replace(want, replacement, 1))
        self.assert_catches("C18", None, raw=raw)

    # ---- C11/C12/C17 rendered rows ---------------------------------------
    def test_19_row_loses_its_official_link(self):
        def raw(root):
            path = os.path.join(root, "solid-gold.html")
            text = read_text(path)
            write_text(path, text.replace(
                'href="https://www.automicgold.com/products/sapphire-ring"', 'href="local-note.html"'))
        self.assert_catches("C11", None, raw=raw)

    def test_20_typed_price_into_a_null_price_row(self):
        def raw(root):
            path = os.path.join(root, "solitaire.html")
            text = read_text(path)
            # BN-203348 has price null: injecting a dollar figure must be caught
            write_text(path, text.replace(
                '<td class="num"><span class="blank"',
                '<td class="num"><strong>$1,234.56</strong><span class="blank"', 1))
        raw(self.root)          # apply the mutation before scanning
        mutated = read_text(os.path.join(self.root, "solitaire.html"))
        self.assertIn("$1,234.56", mutated, "test fixture failed to inject the typed price")
        rc, out = run_scan(self.root)
        self.assertEqual(rc, 1, f"typed price must be caught:\n{out[-2000:]}")
        self.assertTrue("FAIL C12" in out or "FAIL C17" in out,
                        f"expected C12/C17 failure; output:\n{out[-2000:]}")

    def test_21_unbacked_row_with_no_register_entry(self):
        def raw(root):
            path = os.path.join(root, "solid-gold.html")
            text = read_text(path)
            fake = ('<tr class="item-row" id="item-fake" data-item-id="FAKE-001" '
                    'data-source-url="https://www.automicgold.com/products/fake">'
                    '<td>Fake Ring</td><td><a href="https://www.automicgold.com/products/fake">x</a></td></tr>')
            write_text(path, text.replace("</tbody>", fake + "</tbody>", 1))
        self.assert_catches("C11", None, raw=raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
