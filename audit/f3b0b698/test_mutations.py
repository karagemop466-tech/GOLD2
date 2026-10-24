#!/usr/bin/env python3
"""Mutation controls for companion_audit.py; every injected defect must fail."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from companion_audit import scan

SOURCE_ROOT = Path(os.environ.get("GOLD2_AUDIT_ROOT", Path(__file__).resolve().parents[2]))


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gold2-f3-mutation-")
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        for name in ("dashboard", "data", "research"):
            shutil.copytree(SOURCE_ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self):
        self.temp.cleanup()

    def load(self, relative):
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write(self, relative, document):
        (self.root / relative).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def ring(self, ring_id, change):
        document = self.load("dashboard/data/rings.json")
        ring = next(item for item in document["rings"] if item["id"] == ring_id)
        change(ring)
        self.write("dashboard/data/rings.json", document)

    def assert_detected(self, code):
        report = scan(self.root)
        self.assertEqual("FAIL", report["status"], report)
        self.assertIn(code, {issue["code"] for issue in report["issues"]}, report)

    def test_clean_control(self):
        report = scan(self.root)
        self.assertEqual("PASS", report["status"], report)
        self.assertEqual([], report["issues"], report)

    def test_unsupported_null_price_assignment(self):
        self.ring("BN-194158", lambda ring: ring.update(price_usd=1125.0))
        self.assert_detected("price")

    def test_wrong_canonical_amount(self):
        self.ring("AG-CUSHION-SIGNET", lambda ring: ring.update(price_usd=2408.0))
        self.assert_detected("price")

    def test_explicit_usd_evidence_is_mandatory(self):
        self.ring("SAR-147370", lambda ring: ring.update(currency_quotes=["$3,004.00"]))
        self.assert_detected("price")

    def test_null_price_cannot_retain_currency_source(self):
        self.ring("BN-194158", lambda ring: ring.update(currency_source_url=ring["product_url"]))
        self.assert_detected("price")

    def test_identity_mismatch_amount_stays_unassigned(self):
        self.ring("BN-316238", lambda ring: ring.update(unassigned_display="$1,240(Setting Price)"))
        self.assert_detected("price")

    def test_product_host_must_match_seller(self):
        self.ring("SAR-147370", lambda ring: ring.update(product_url="https://www.bluenile.com/not-sarraf"))
        self.assert_detected("identity")

    def test_gross_weight_cannot_become_metal_weight(self):
        self.ring("FDJ-GR0001", lambda ring: ring.update(weight_g=1.25))
        self.assert_detected("weight")

    def test_supported_weight_cannot_be_blank(self):
        self.ring("VRAI-CLASSIC-4P", lambda ring: ring.update(weight_g=None, weight_note="Blank"))
        self.assert_detected("weight")

    def test_invented_bbb_rating(self):
        document = self.load("dashboard/data/retailers.json")
        retailer = next(item for item in document["retailers"] if item["id"] == "automic-gold")
        retailer["bbb_summary"] += " BBB rating B-."
        self.write("dashboard/data/retailers.json", document)
        self.assert_detected("seller")

    def test_blank_seller_field_must_be_flagged(self):
        document = self.load("dashboard/data/retailers.json")
        retailer = next(item for item in document["retailers"] if item["id"] == "mene")
        retailer["unverified_fields"] = [item for item in retailer["unverified_fields"] if item != "return window"]
        self.write("dashboard/data/retailers.json", document)
        self.assert_detected("seller")

    def test_official_rendered_row_link_is_mandatory(self):
        path = self.root / "dashboard/rings.html"
        document = self.load("dashboard/data/rings.json")
        ring = next(item for item in document["rings"] if item["id"] == "SAR-147370")
        text = path.read_text(encoding="utf-8")
        changed = text.replace(f'href="{ring["product_url"]}"', 'href="#removed-official-source"', 1)
        self.assertNotEqual(text, changed)
        path.write_text(changed, encoding="utf-8")
        self.assert_detected("render")

    def test_rendered_fine_gold_arithmetic(self):
        path = self.root / "dashboard/rings.html"
        text = path.read_text(encoding="utf-8")
        changed = text.replace("<strong>2.217 g</strong>", "<strong>9.999 g</strong>", 1)
        self.assertNotEqual(text, changed)
        path.write_text(changed, encoding="utf-8")
        self.assert_detected("render")

    def test_no_hallucination_banner_is_mandatory(self):
        path = self.root / "dashboard/index.html"
        text = path.read_text(encoding="utf-8")
        changed = text.replace("No hallucinations. No invented prices.", "Source review.", 1)
        self.assertNotEqual(text, changed)
        path.write_text(changed, encoding="utf-8")
        self.assert_detected("policy")

    def test_csp_mutation(self):
        path = self.root / "dashboard/rings.html"
        text = path.read_text(encoding="utf-8")
        changed = text.replace("connect-src 'none'", "connect-src 'self'", 1)
        self.assertNotEqual(text, changed)
        path.write_text(changed, encoding="utf-8")
        self.assert_detected("security")

    def test_gold_reference_parity(self):
        document = self.load("dashboard/data/gold-reference.json")
        document["spot_usd_per_troy_oz"] = 1.0
        self.write("dashboard/data/gold-reference.json", document)
        self.assert_detected("gold")

    def test_evidence_quote_cannot_be_removed(self):
        ring_document = self.load("dashboard/data/rings.json")
        ring = next(item for item in ring_document["rings"] if item["id"] == "SAR-147370")
        path = self.root / "dashboard/evidence/rings.md"
        text = path.read_text(encoding="utf-8")
        marker = f"## {ring['id']} —"
        before, section = text.split(marker, 1)
        changed_section = section.replace(ring["quote"], "")
        self.assertNotEqual(section, changed_section)
        path.write_text(before + marker + changed_section, encoding="utf-8")
        self.assert_detected("evidence")

    def test_solid_gold_status_cannot_be_promoted(self):
        self.ring("BN-194158", lambda ring: ring.update(solid_gold_explicit=True))
        self.assert_detected("qualification")


if __name__ == "__main__":
    unittest.main(verbosity=2)
