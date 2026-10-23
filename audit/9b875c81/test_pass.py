#!/usr/bin/env python3
"""
test_pass.py — Session S-9B875C81 automated unit & negative-mutation test suite for:
  1. Live 2026-10-23 NIST precious-metals calculator math (`g`, `dwt`, `ozt`, set gemstone
     carat subtraction `1 ct = 0.200 g`, retail/melt multiple, gold value share, boundary/NaN/Inf).
  2. Live workspace zero-finding pass across `audit/9b875c81/`, root, `site/`, and `dashboard/`.
  3. Negative mutation tests proving scanner catches hallucinated melt numbers, ambiguous gross
     weights stuffed into `weight_g`, broken internal links/anchors, unlinked `<tr>` rows,
     unpinned GitHub Actions, and WCAG 2.1 AA contrast violations.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hallucination_security_pass as hsp  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestS9B875C81CalculatorAndScanner(unittest.TestCase):
    def test_nist_conversions_and_2026_10_23_spot_4024_45(self) -> None:
        # 1 troy oz = 20 dwt = 31.1034768 g in 24K -> exact $4,024.45
        for val, unit in ((1.0, "ozt"), (20.0, "dwt"), (31.1034768, "g")):
            res = hsp.compute_melt_nist(val, 24, 4024.45, unit=unit)
            self.assertIsNotNone(res)
            assert res is not None
            self.assertAlmostEqual(res["melt_usd"], 4024.45, places=2)

        # AG-24K: 11.0g 24K stone-free @ $4,024.45 -> $1,423.28 melt, $3,520 ask -> 2.47x (40.43%)
        ag24 = hsp.compute_melt_nist(11.0, 24, 4024.45, ask_usd=3520.0)
        assert ag24 is not None
        self.assertAlmostEqual(ag24["fine_g"], 11.0, places=3)
        self.assertAlmostEqual(ag24["melt_usd"], 1423.28, places=2)
        self.assertAlmostEqual(ag24["multiple"], 2.47, places=2)
        self.assertAlmostEqual(ag24["gold_share_pct"], 40.43, places=2)

        # SAR-144773: 13.40g 14K stone-free @ $4,024.45 -> 7.817g fine -> $1,011.39 melt, $1,362 ask -> 74.26%
        sar_band = hsp.compute_melt_nist(13.40, 14, 4024.45, ask_usd=1362.0)
        assert sar_band is not None
        self.assertAlmostEqual(sar_band["fine_g"], 7.817, places=3)
        self.assertAlmostEqual(sar_band["melt_usd"], 1011.39, places=2)
        self.assertAlmostEqual(sar_band["gold_share_pct"], 74.26, places=2)

        # Gemstone carat mass subtraction check: FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K
        fdj = hsp.compute_melt_nist(1.25, 14, 4024.45, stone_carats_deduct=1.37, ask_usd=1299.99)
        assert fdj is not None
        self.assertAlmostEqual(fdj["stone_g"], 0.274, places=4)
        self.assertAlmostEqual(fdj["net_metal_g"], 0.976, places=4)
        self.assertAlmostEqual(fdj["fine_g"], 0.569, places=3)
        self.assertAlmostEqual(fdj["melt_usd"], 73.67, places=2)

    def test_rejects_invalid_or_stone_exceeding_gross_inputs(self) -> None:
        self.assertIsNone(hsp.compute_melt_nist(0, 14, 4024.45))
        self.assertIsNone(hsp.compute_melt_nist(-2.5, 14, 4024.45))
        self.assertIsNone(hsp.compute_melt_nist(float("nan"), 14, 4024.45))
        self.assertIsNone(hsp.compute_melt_nist(float("inf"), 14, 4024.45))
        self.assertIsNone(hsp.compute_melt_nist(3.0, 25, 4024.45))
        # 10 carats = 2.0g > 1.25g gross -> impossible net metal mass -> rejected closed!
        self.assertIsNone(hsp.compute_melt_nist(1.25, 14, 4024.45, stone_carats_deduct=10.0))

    def test_workspace_passes_with_zero_findings(self) -> None:
        report = hsp.scan_workspace(REPO_ROOT)
        self.assertEqual(report["findings"], [], f"Unexpected findings: {report['findings']}")
        self.assertGreater(report["controls_passed"], 50)

    def test_negative_mutations_are_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "audit" / "9b875c81" / "evidence").mkdir(parents=True)
            (root / "dashboard" / "assets").mkdir(parents=True)
            (root / ".github" / "workflows").mkdir(parents=True)

            (root / "audit" / "9b875c81" / "verified-sources-2026-10-23.json").write_text(
                json.dumps({"gold_spot_reference": {"usd_per_troy_oz": 4024.45}}),
                encoding="utf-8",
            )
            (root / "audit" / "9b875c81" / "evidence" / "bad.md").write_text(
                "# Evidence — BAD-1\n- Ring Name\n- SKU1\n- Solid 14K Gold\n",
                encoding="utf-8",
            )
            # Stuff ambiguous gross weight directly into weight_g AND hallucinate melt_usd
            (root / "audit" / "9b875c81" / "new-listings-2026-10-23.json").write_text(
                json.dumps(
                    {
                        "spot_usd_per_troy_oz": 4024.45,
                        "new_verified_listings": [
                            {
                                "id": "BAD-1",
                                "name": "Ring Name",
                                "sku": "SKU1",
                                "karat": 14,
                                "weight_g": 1.25,
                                "ambiguous_weight_g": 1.25,
                                "price": 999.0,
                                "solid_gold_explicit": True,
                                "nominal_fine_gold_g": 0.729,
                                "nominal_melt_usd": 999.99,
                                "evidence_file": "audit/9b875c81/evidence/bad.md",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            # Broken internal link + missing CSP + unlinked table row + low contrast + unpinned workflow
            (root / "dashboard" / "index.html").write_text(
                "<!doctype html><html><head></head><body>"
                "<p>No hallucinations policy — <a href='missing.html'>broken</a></p>"
                "<table><tr><td>Row without official link</td></tr></table>"
                "</body></html>",
                encoding="utf-8",
            )
            (root / "dashboard" / "assets" / "style.css").write_text(
                ":root { --bg: #ffffff; --card: #ffffff; --gold: #c9a227; }\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows" / "bad.yml").write_text(
                "steps:\n  - uses: actions/checkout@v4\n",
                encoding="utf-8",
            )

            res = hsp.scan_workspace(root)
            codes = {f["code"] for f in res["findings"]}
            self.assertIn("AMBIGUOUS-WEIGHT-ASSIGNED-AS-METAL", codes)
            self.assertIn("MELT-USD-DRIFT", codes)
            self.assertIn("MISSING-CSP", codes)
            self.assertIn("BROKEN-INTERNAL-LINK", codes)
            self.assertIn("ROW-MISSING-OFFICIAL-SOURCE", codes)
            self.assertIn("WCAG-AA-CONTRAST-FAIL", codes)
            self.assertIn("WORKFLOW-NOT-SHA-PINNED", codes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
