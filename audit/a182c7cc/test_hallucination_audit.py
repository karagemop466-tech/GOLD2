"""Mutation controls for the independent A182 audit (no repository writes)."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from hallucination_audit import load, validate_data  # noqa: E402


class IndependentAuditMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = (
            load(ROOT, "data/catalog.json"),
            load(ROOT, "research/evidence.json"),
            load(ROOT, "data/verification-log.json"),
            load(ROOT, "data/gold-price.json"),
        )

    def mutated(self):
        return tuple(copy.deepcopy(item) for item in self.baseline)

    def test_checked_in_snapshot_passes(self):
        self.assertEqual(validate_data(*self.mutated()), [])

    def test_invented_mene_price_without_matching_quote_fails(self):
        catalog, evidence, verification, gold = self.mutated()
        row = next(p for p in catalog["products"] if p["id"] == "mene-rose")
        row["price"]["amount"] = 1336
        errors = validate_data(catalog, evidence, verification, gold)
        self.assertTrue(any("mene-rose: no cited official quote contains" in e for e in errors))

    def test_filling_a_blank_price_without_a_snapshot_fails(self):
        catalog, evidence, verification, gold = self.mutated()
        row = next(p for p in catalog["products"] if p["price"] is None)
        row["price"] = {"amount": 1035, "currency": "USD", "observedAt": "2026-10-23", "evidence": []}
        errors = validate_data(catalog, evidence, verification, gold)
        self.assertTrue(any("expected 17 assigned rows, found 18" in e for e in errors))
        self.assertTrue(any("does not cover exactly" in e for e in errors))

    def test_assigning_chart_date_to_wgc_header_fails(self):
        catalog, evidence, verification, gold = self.mutated()
        gold["quote_date"] = "2026-10-22"
        errors = validate_data(catalog, evidence, verification, gold)
        self.assertTrue(any("WGC quote date must stay null" in e for e in errors))

    def test_partial_request_time_placeholder_fails(self):
        catalog, evidence, verification, gold = self.mutated()
        gold["quote_scope"] = "retrieved 2026-10-23T23:4xZ"
        errors = validate_data(catalog, evidence, verification, gold)
        self.assertTrue(any("fabricated/partial request timestamp" in e for e in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
