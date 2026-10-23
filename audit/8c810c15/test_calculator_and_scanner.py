#!/usr/bin/env python3
"""
test_calculator_and_scanner.py — S8C8-T3 automated unit tests for:
  1. Gold melt calculator math & input edge cases (0, negative, NaN, Infinity,
     standard karats, NIST units g/dwt/ozt, optional asking price, live DOM JS).
  2. Hallucination, HTML official-link, CSP/workflow security, and WCAG contrast
     scanner positive/negative regression checks.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import security_and_hallucination_scanner as scanner  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAMS_PER_TROY_OZ = Decimal("31.1034768")
GRAMS_PER_DWT = Decimal("1.55517384")


def compute_melt_reference(
    weight: float,
    unit: str,
    karat: int,
    spot_usd_per_ozt: float,
    ask_usd: float | None = None,
) -> dict | None:
    """Reference NIST OWM / FTC 16 CFR Part 23 pure-gold & melt calculation."""
    import math

    if not (math.isfinite(weight) and math.isfinite(karat) and math.isfinite(spot_usd_per_ozt)):
        return None
    if weight <= 0 or karat <= 0 or karat > 24 or spot_usd_per_ozt <= 0:
        return None
    w = Decimal(str(weight))
    if unit == "g":
        grams = w
    elif unit == "dwt":
        grams = w * GRAMS_PER_DWT
    elif unit == "ozt":
        grams = w * GRAMS_PER_TROY_OZ
    else:
        return None
    fine_g = grams * Decimal(karat) / Decimal(24)
    usd_per_g = Decimal(str(spot_usd_per_ozt)) / GRAMS_PER_TROY_OZ
    melt_usd = fine_g * usd_per_g
    out: dict = {
        "grams": float(round(grams, 4)),
        "fine_g": float(round(fine_g, 3)),
        "melt_usd": float(round(melt_usd, 2)),
        "multiple": None,
    }
    if ask_usd is not None:
        if not math.isfinite(ask_usd) or ask_usd <= 0:
            out["ask_invalid"] = True
        else:
            out["multiple"] = float(round(Decimal(str(ask_usd)) / melt_usd, 2))
    return out


class TestGoldMeltCalculatorMath(unittest.TestCase):
    def test_standard_karats_exact_nist_precision(self) -> None:
        # VRAI 18K ring: 2.86g @ $4,028.53/ozt -> 2.145g fine -> $277.82
        vrai = compute_melt_reference(2.86, "g", 18, 4028.53)
        self.assertIsNotNone(vrai)
        assert vrai is not None
        self.assertAlmostEqual(vrai["fine_g"], 2.145, places=3)
        self.assertAlmostEqual(vrai["melt_usd"], 277.82, places=2)

        # Automic Gold Coffin Ring 14K: 6.1g @ $4,028.53/ozt -> 3.558g fine -> $460.88, ask $1,910 -> 4.14x
        ag = compute_melt_reference(6.1, "g", 14, 4028.53, ask_usd=1910.0)
        assert ag is not None
        self.assertAlmostEqual(ag["fine_g"], 3.558, places=3)
        self.assertAlmostEqual(ag["melt_usd"], 460.88, places=2)
        self.assertAlmostEqual(ag["multiple"], 4.14, places=2)

        # 3.00g 14K default -> 1.750g fine -> $226.66 at $4,028.53/ozt (exact: 226.6606097...)
        d14 = compute_melt_reference(3.0, "g", 14, 4028.53)
        assert d14 is not None
        self.assertAlmostEqual(d14["fine_g"], 1.750, places=3)
        self.assertAlmostEqual(d14["melt_usd"], 226.66, places=2)

    def test_nist_unit_conversions_dwt_and_ozt(self) -> None:
        # 20 dwt == 1 troy oz == 31.1034768 g in 24K -> melt must equal spot $4,028.53 exact to $0.00
        by_dwt = compute_melt_reference(20.0, "dwt", 24, 4028.53)
        by_ozt = compute_melt_reference(1.0, "ozt", 24, 4028.53)
        by_g = compute_melt_reference(31.1034768, "g", 24, 4028.53)
        assert by_dwt and by_ozt and by_g
        self.assertAlmostEqual(by_dwt["melt_usd"], 4028.53, places=2)
        self.assertAlmostEqual(by_ozt["melt_usd"], 4028.53, places=2)
        self.assertAlmostEqual(by_g["melt_usd"], 4028.53, places=2)

    def test_invalid_zero_negative_nan_infinity_inputs_rejected(self) -> None:
        self.assertIsNone(compute_melt_reference(0.0, "g", 14, 4028.53))
        self.assertIsNone(compute_melt_reference(-3.0, "g", 14, 4028.53))
        self.assertIsNone(compute_melt_reference(float("nan"), "g", 14, 4028.53))
        self.assertIsNone(compute_melt_reference(float("inf"), "g", 14, 4028.53))
        self.assertIsNone(compute_melt_reference(3.0, "g", 0, 4028.53))
        self.assertIsNone(compute_melt_reference(3.0, "g", 25, 4028.53))
        self.assertIsNone(compute_melt_reference(3.0, "g", 14, -100.0))

    def test_live_prices_html_dom_calculator_handles_edge_cases(self) -> None:
        prices_path = REPO_ROOT / "prices.html"
        html = prices_path.read_text(encoding="utf-8")
        m_ext = re.search(r'<script[^>]*\bsrc="([^"]+)"[^>]*></script>', html)
        if m_ext:
            calc_path = (prices_path.parent / m_ext.group(1)).resolve()
            self.assertTrue(calc_path.exists(), f"Missing calculator script {calc_path}")
            driver = """
const calc = require(%s);
const els = {
  w: { value: '3.0', listeners: [] },
  unit: { value: 'g', listeners: [] },
  k: { value: '14', listeners: [] },
  spot: { value: '4028.53', listeners: [] },
  ask: { value: '', listeners: [] },
  fine: { textContent: '' },
  melt: { textContent: '' },
  ratio: { textContent: '' },
  over: { textContent: '' },
};
for (const k of Object.keys(els)) {
  els[k].addEventListener = (ev, fn) => els[k].listeners.push(fn);
}
calc.bindCalculator({ getElementById: (id) => els[id] || null });
const run = (w, k, spot, ask, unit='g') => {
  els.w.value = w; els.k.value = k; els.spot.value = spot; els.ask.value = ask; els.unit.value = unit;
  els.w.listeners[0]();
  return { pure: els.fine.textContent, melt: els.melt.textContent, mult: els.ratio.textContent, over: els.over.textContent };
};
console.log(JSON.stringify({
  default14: run('3.0', '14', '4028.53', ''),
  vrai18: run('2.86', '18', '4028.53', ''),
  coffin14: run('6.1', '14', '4028.53', '1910'),
  dwt24: run('20', '24', '4028.53', '', 'dwt'),
  zeroW: run('0', '14', '4028.53', ''),
  negW: run('-5', '14', '4028.53', ''),
  nanW: run('abc', '14', '4028.53', ''),
}));
""" % json.dumps(str(calc_path))
            proc = subprocess.run(["node", "-e", driver], capture_output=True, text=True, check=True)
            res = json.loads(proc.stdout)
            self.assertEqual(res["default14"]["pure"], "1.750 g")
            self.assertEqual(res["default14"]["melt"], "$226.66")
            self.assertEqual(res["vrai18"]["pure"], "2.145 g")
            self.assertEqual(res["vrai18"]["melt"], "$277.82")
            self.assertEqual(res["coffin14"]["melt"], "$460.88")
            self.assertIn("4.14", res["coffin14"]["mult"])
            self.assertEqual(res["dwt24"]["melt"], "$4,028.53")
            for bad_key in ("zeroW", "negW", "nanW"):
                self.assertEqual(res[bad_key]["melt"], "—")
                self.assertEqual(res[bad_key]["pure"], "—")
            return


class TestSecurityAndHallucinationScanner(unittest.TestCase):
    def _make_minimal_fixture(self, root: Path) -> None:
        (root / "data" / "listings").mkdir(parents=True)
        (root / "evidence" / "listings").mkdir(parents=True)
        (root / "assets").mkdir(parents=True)
        (root / "site").mkdir(parents=True)
        (root / ".github" / "workflows").mkdir(parents=True)

        (root / "data" / "gold-price.json").write_text(
            json.dumps(
                {
                    "usd_per_troy_oz": 4028.53,
                    "quote_date": "2026-10-21",
                    "retrieved_at": "2026-10-22",
                    "evidence_quotes": ["USD /oz - 4,028.53", "Data as of 21 October, 2026"],
                }
            ),
            encoding="utf-8",
        )
        (root / "data" / "flags.json").write_text(
            json.dumps({"flags": [{"id": "F-016", "title": "Width unverified", "detail": "Band width omitted."}]}),
            encoding="utf-8",
        )
        (root / "evidence" / "listings" / "sample.md").write_text(
            "## TEST-1\n- `Solid 14k Gold`\n- `14k Yellow Gold`\n- `$1,910`\n",
            encoding="utf-8",
        )
        (root / "data" / "listings" / "sample.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "id": "TEST-1",
                            "sku": None,
                            "metal": "Solid 14k Gold",
                            "karat": 14,
                            "color": "Yellow",
                            "width_mm": None,
                            "weight_g": 6.1,
                            "price": 1910.0,
                            "currency": "USD",
                            "source_url": "https://www.automicgold.com/products/coffin-ring",
                            "evidence_file": "evidence/listings/sample.md",
                            "evidence_quotes": ["Solid 14k Gold", "14k Yellow Gold", "$1,910"],
                            "solid_gold_explicit": True,
                            "flags": ["F-016"],
                            "notes": "Verified solid gold ring.",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        valid_page = (
            '<!doctype html><html><head>'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'self\'">'
            "</head><body>"
            "<section><h2>No-Hallucinations Policy</h2>"
            '<p>Spot $4,028.53 — <a href="flags.html">Flagged for Review</a></p></section>'
            '<table><tbody><tr><td>Ring</td><td><a href="https://www.automicgold.com/products/coffin-ring" '
            'target="_blank" rel="noopener noreferrer">Official source</a></td></tr></tbody></table>'
            "</body></html>"
        )
        for name in ("index.html", "prices.html", "methods.html", "site/index.html"):
            (root / name).write_text(valid_page, encoding="utf-8")
        (root / "assets" / "style.css").write_text(
            ":root { --bg: #faf9f6; --surface: #ffffff; --ink: #16161a; --muted: #555560; --accent: #5b3cc4; }\n"
            ".eyebrow { color: #6b5014; }\n",
            encoding="utf-8",
        )
        (root / "site" / "style.css").write_text(
            ":root { --bg: #fafaf7; --surface: #ffffff; --ink: #171717; --muted: #525252; }\n"
            ".eyebrow { color: #6b5014; }\n",
            encoding="utf-8",
        )
        (root / ".github" / "workflows" / "ci.yml").write_text(
            "steps:\n  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n",
            encoding="utf-8",
        )

    def test_clean_fixture_passes_with_zero_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_minimal_fixture(root)
            res = scanner.audit_repository(root)
            self.assertEqual(res["findings"], [])

    def test_detects_hallucinated_color_unlinked_row_unpinned_action_and_low_contrast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_minimal_fixture(root)
            # 1. Inject hallucinated color not in item section
            doc = json.loads((root / "data" / "listings" / "sample.json").read_text(encoding="utf-8"))
            doc["items"][0]["color"] = "Rose"
            (root / "data" / "listings" / "sample.json").write_text(json.dumps(doc), encoding="utf-8")
            # 2. Inject table row missing https:// link
            (root / "methods.html").write_text(
                '<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'"></head>'
                "<body><p>$4,028.53</p><table><tr><td>Unlinked claim row</td></tr></table></body></html>",
                encoding="utf-8",
            )
            # 3. Inject unpinned tag action
            (root / ".github" / "workflows" / "ci.yml").write_text("steps:\n  - uses: actions/checkout@v4\n", encoding="utf-8")
            # 4. Inject WCAG AA contrast violation (#aa8135 on #f7f7f1 = 3.21:1 < 4.50:1)
            (root / "site" / "style.css").write_text(
                ":root { --gold: #aa8135; --paper: #f7f7f1; }\n.eyebrow { color: var(--gold); }\n",
                encoding="utf-8",
            )

            res = scanner.audit_repository(root)
            codes = {f["code"] for f in res["findings"]}
            self.assertIn("COLOR-NOT-IN-ITEM-SECTION", codes)
            self.assertIn("TABLE-ROW-MISSING-OFFICIAL-HTTPS-LINK", codes)
            self.assertIn("UNPINNED-GITHUB-ACTION", codes)
            self.assertIn("WCAG-CONTRAST-FAIL", codes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
