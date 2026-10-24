#!/usr/bin/env python3
"""
Mutation Control Test Suite for audit/86379ca7/hallucination_security_scanner.py
Session S-86379CA7 (2026-10-23 UTC)

Runs 10 synthetic defect-injection tests against temporary workspace copies
to prove the scanner catches every class of hallucination and security defect.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hallucination_security_scanner as scanner

REPO_ROOT = Path(__file__).resolve().parents[2]


def copy_minimal_tree(dst: Path) -> None:
    for p in scanner.ROOT_HTML_PAGES:
        shutil.copy2(REPO_ROOT / p, dst / p)
    for folder in ("data", "evidence", "research", "explore", "dashboard", ".github"):
        shutil.copytree(REPO_ROOT / folder, dst / folder)


class ScannerMutationTests(unittest.TestCase):
    def test_01_clean_tree_passes_with_zero_hard_failures(self):
        failures, warnings, metrics = scanner.run_scan(REPO_ROOT, strict_cross_register=False)
        self.assertEqual(failures, [], f"Expected 0 hard failures on repo root, got {failures}")
        self.assertEqual(metrics["root_items"], 30)
        self.assertGreaterEqual(metrics["catalog_products"], 44)

    def test_02_catches_removed_no_hallucinations_banner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            idx = root / "index.html"
            idx.write_text("<html><body><a href='flags.html'>Flags</a></body></html>", encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("[Check 1]" in f and "index.html" in f for f in failures))

    def test_03_catches_table_row_missing_official_https_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            sol = root / "solitaire.html"
            html = sol.read_text(encoding="utf-8")
            html = html.replace("</tbody>", "<tr><td>Fake Ring</td><td>No Link</td></tr></tbody>", 1)
            sol.write_text(html, encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("[Check 2]" in f and "lacks an external https://" in f for f in failures))

    def test_04_catches_javascript_href_and_missing_noopener(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            idx = root / "index.html"
            html = idx.read_text(encoding="utf-8")
            html += '<a href="javascript:alert(1)">bad</a><a href="https://example.com" target="_blank">bad2</a>'
            idx.write_text(html, encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("Unsafe or non-HTTPS href" in f for f in failures))
            self.assertTrue(any("without rel=noopener" in f for f in failures))

    def test_05_catches_hallucinated_price_not_in_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            sg_file = root / "data" / "solid-gold-verified.json"
            data = json.loads(sg_file.read_text(encoding="utf-8"))
            data["items"][0]["price"] = 9999.99
            sg_file.write_text(json.dumps(data), encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("[Check 3]" in f and "9999.99" in f for f in failures))

    def test_06_catches_zero_or_string_placeholder_and_non_null_fine_gold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            sg_file = root / "data" / "solid-gold-verified.json"
            data = json.loads(sg_file.read_text(encoding="utf-8"))
            data["items"][0]["fine_gold_g"] = 3.558
            data["items"][1]["weight_g"] = 0
            sg_file.write_text(json.dumps(data), encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("fine_gold_g must be null" in f for f in failures))
            self.assertTrue(any("non-positive number" in f for f in failures))

    def test_07_catches_catalog_unbacked_net_metal_weight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            cat_file = root / "data" / "catalog.json"
            data = json.loads(cat_file.read_text(encoding="utf-8"))
            data["products"][0]["facts"]["netMetalWeightG"] = {"value": 2.5}
            cat_file.write_text(json.dumps(data), encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("[Check 4]" in f and "netMetalWeightG" in f for f in failures))

    def test_08_catches_superseded_gold_quote_leak_and_nist_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            gp_file = root / "data" / "gold-price.json"
            gp = json.loads(gp_file.read_text(encoding="utf-8"))
            gp["grams_per_troy_ounce"] = 31.1
            gp_file.write_text(json.dumps(gp), encoding="utf-8")
            idx = root / "index.html"
            idx.write_text(idx.read_text(encoding="utf-8") + "<!-- 4,028.53 -->", encoding="utf-8")
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("Invalid NIST constant" in f for f in failures))
            self.assertTrue(any("Superseded gold quote 4,028.53 leaked" in f for f in failures))

    def test_09_catches_inline_event_handler_and_external_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_minimal_tree(root)
            idx = root / "index.html"
            idx.write_text(
                idx.read_text(encoding="utf-8")
                + '<button onclick="evil()">x</button><script src="https://evil.example/x.js"></script>',
                encoding="utf-8",
            )
            failures, _, _ = scanner.run_scan(root)
            self.assertTrue(any("Inline DOM event handler" in f for f in failures))
            self.assertTrue(any("External runtime <script" in f for f in failures))

    def test_10_strict_cross_register_mode_flags_companion_and_flag_drift(self):
        failures, _, _ = scanner.run_scan(REPO_ROOT, strict_cross_register=True)
        self.assertGreater(len(failures), 0, "Expected strict_cross_register=True to surface cross-register drift")


if __name__ == "__main__":
    unittest.main(verbosity=2)
