#!/usr/bin/env python3
"""Refresh the dated WGC observation to the value re-read by S-1B04074F.

Live evidence (https://www.gold.org/goldhub/data/gold-prices, fetched 2026-10-23):
    USD /oz - 3,995.47
    Data as of 22 October, 2026      <- chart date, NOT a header timestamp (F-026)
    Market Data: Provided by ICE Data Services.

Only the moving-header value changes. Every earlier value is retained in
superseded_observations / the dated history table. No price, product or
verification claim is invented; derived figures are recomputed from the
stored spot and NIST 31.1034768 g/ozt.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OLD = 3996.31
NEW = 3995.47
RETRIEVED = "2026-10-23"
READ_AT = "2026-10-23T23:4xZ"
TROY = 31.1034768


def sub(path: str, pairs: list[tuple[str, str]]) -> None:
    p = ROOT / path
    text = p.read_text()
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f"pattern not found in {path}: {old[:70]!r}")
        text = text.replace(old, new)
    p.write_text(text)


# 1. Root machine-readable quote -------------------------------------------------
p = ROOT / "data/gold-price.json"
d = json.loads(p.read_text())
assert d["usd_per_troy_oz"] == OLD, d["usd_per_troy_oz"]
d["usd_per_troy_oz"] = NEW
d["retrieved_at"] = RETRIEVED
d["evidence_quotes"] = ["3,995.47", "Data as of 22 October, 2026"]
d["field_evidence"]["usd_per_troy_oz"] = ["USD\n\n/oz\n\n-\n\n3,995.47"]
d["quote_scope"] = (
    f"Moving-header observation retrieved {READ_AT}; exact quote-as-of timestamp is unconfirmed "
    "(F-026). The chart's stated date (22 October 2026) is stored separately and is not assigned "
    "to the header."
)
d["superseded_observations"].append(
    {
        "value": OLD,
        "currency": "USD",
        "quote_date": None,
        "retrieved_at": "2026-10-23",
        "chart_as_of_date": "2026-10-22",
        "status": "superseded_moving_header",
        "reason": (
            "Header value observed earlier the same day (2026-10-23). The moving header is not a "
            "fixed benchmark; only the latest 2026-10-23 observation (3,995.47) is used in calculations."
        ),
    }
)
p.write_text(json.dumps(d, indent=2) + "\n")

# 2. Companion dashboard reference ----------------------------------------------
p = ROOT / "dashboard/data/gold-reference.json"
d = json.loads(p.read_text())
assert d["spot_usd_per_troy_oz"] == OLD
d["spot_usd_per_troy_oz"] = NEW
d["usd_per_fine_gram"] = round(NEW / TROY, 5)
d["spot_quotes"] = ["USD /oz - 3,995.47", "Data as of 22 October, 2026"]
p.write_text(json.dumps(d, indent=2) + "\n")

# 3. Root verification log entry -------------------------------------------------
p = ROOT / "data/verification-log.json"
d = json.loads(p.read_text())
for e in d["entries"]:
    if e["id"] == "GOLD-QUOTE":
        e["observed"][0] = "3,995.47"
        e["note"] = (
            "Late-evening re-read on 2026-10-23 replaced the earlier same-day header observation "
            "(3,996.31). The header is moving; quote_date stays null because it carries no timestamp "
            "(F-026). Earlier values are retained only as superseded history."
        )
p.write_text(json.dumps(d, indent=2) + "\n")

# 4. Dashboard generator: quote constant and every literal that renders it --------
sub(
    "dashboard/scripts/build.py",
    [
        ('SPOT_USD = Decimal("3996.31")', 'SPOT_USD = Decimal("3995.47")'),
        ('"spot_usd_per_troy_oz": 3996.31', '"spot_usd_per_troy_oz": 3995.47'),
        (
            '"spot_quotes": ["USD /oz - 3,996.31", "Data as of 22 October, 2026"]',
            '"spot_quotes": ["USD /oz - 3,995.47", "Data as of 22 October, 2026"]',
        ),
    ],
)
p = ROOT / "dashboard/scripts/build.py"
text = p.read_text()
text = text.replace("$3,996.31", "$3,995.47").replace("3,996.31", "3,995.47")
text = text.replace("3996.31", "3995.47").replace("$128.48", "$128.46")
p.write_text(text)

# 5. Calculator tests: expectation values recomputed at the new quote -------------
sub(
    "dashboard/scripts/calc-test.js",
    [
        (
            "// 2. Live 2026-10-23 spot ($3,996.31/oz) across units & asking-price multiples",
            "// 2. Live 2026-10-23 spot ($3,995.47/oz) across units & asking-price multiples",
        ),
        ('check("1 ozt == 20 dwt == $3,996.31 exact"',
         'check("1 ozt == 20 dwt == $3,995.47 exact"'),
        ("Math.abs(sarBand.melt - 1004.319336) < 1e-3 && Math.abs(sarBand.goldSharePct - 73.7386) < 1e-2",
         "Math.abs(sarBand.melt - 1004.108234) < 1e-3 && Math.abs(sarBand.goldSharePct - 73.7231) < 1e-2"),
        ('check("SAR-144773 13.40g 14K melt $1,004.32 & 73.74% gold share"',
         'check("SAR-144773 13.40g 14K melt $1,004.11 & 73.72% gold share"'),
        ("Math.abs(gemDeduct.melt - 73.1477) < 1e-2", "Math.abs(gemDeduct.melt - 73.1350) < 1e-2"),
        ('check("FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K ($73.15)"',
         'check("FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K ($73.14)"'),
    ],
)
p = ROOT / "dashboard/scripts/calc-test.js"
p.write_text(p.read_text().replace("3996.31", "3995.47"))

print("gold refresh applied:", OLD, "->", NEW)
print("usd_per_fine_gram:", round(NEW / TROY, 5))
