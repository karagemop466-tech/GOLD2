#!/usr/bin/env python3
"""Independent, read-only cross-file audit of the dated 2026-10-23 price pass.

This deliberately does not import project verifiers. It checks that every assigned
price has a source/quote/currency chain and that the pass log, data and WGC date
semantics agree. It does not establish source truth, physical purity, or security.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PRICED_ROWS = 17
EXPECTED_UNPRICED_ROWS = 27
EXPECTED_CORRECTIONS = {"mene-rose", "mene-knot"}
ALLOWED_HOSTS = {
    "auvere.com", "consumer.ftc.gov", "mejuri.com", "mene.com",
    "www.automicgold.com", "www.bbb.org", "www.bluenile.com",
    "www.brilliantearth.com", "www.catbirdnyc.com",
    "www.factorydirectjewelry.com", "www.gia.edu", "www.gold.org",
    "www.jmbullion.com", "www.lbma.org.uk", "www.nist.gov",
    "www.quince.com", "www.sarraf.com", "www.stoneandstrand.com",
    "www.trustpilot.com", "www.vrai.com", "www.zales.com",
}


def load(root: Path, relative: str):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def has_number(text: str, number: int | float) -> bool:
    """Require a complete numeric token; 726 must not match 1,726."""
    normalized = re.sub(r"\s+", " ", text.replace(",", ""))
    token = re.escape(str(number))
    zeroes = r"(?:\.0+)?" if float(number).is_integer() else ""
    return re.search(rf"(?<![\d.]){token}{zeroes}(?![\d.])", normalized) is not None


def validate_data(catalog, evidence, verification, gold) -> list[str]:
    errors: list[str] = []
    products = catalog.get("products", [])
    sources = evidence.get("sources", [])
    by_product = {row.get("id"): row for row in products}
    by_source = {row.get("id"): row for row in sources}
    if len(by_product) != len(products):
        errors.append("duplicate product id")
    if len(by_source) != len(sources):
        errors.append("duplicate source id")

    priced = {row["id"]: row for row in products if row.get("price") is not None}
    if len(priced) != EXPECTED_PRICED_ROWS:
        errors.append(f"expected {EXPECTED_PRICED_ROWS} assigned rows, found {len(priced)}")
    if len(products) - len(priced) != EXPECTED_UNPRICED_ROWS:
        errors.append(f"expected {EXPECTED_UNPRICED_ROWS} blank prices, found {len(products)-len(priced)}")

    # Independently resolve each assigned price to its official source passage(s).
    for pid, product in priced.items():
        price = product["price"]
        if not isinstance(price.get("amount"), (int, float)) or price["amount"] <= 0:
            errors.append(f"{pid}: invalid assigned amount")
        if price.get("currency") not in {"USD", "EUR"}:
            errors.append(f"{pid}: unsupported/missing currency")
        quoted_amount = False
        currency_proved = False
        for ref in price.get("evidence", []):
            source = by_source.get(ref.get("source"))
            quote = source.get("quotes", {}).get(ref.get("quote")) if source else None
            if not isinstance(quote, str):
                errors.append(f"{pid}: unresolved price evidence {ref}")
                continue
            quoted_amount |= has_number(quote, price["amount"])
            currency_proved |= bool(re.search(r"\bUSD\b|US\$", quote)) if price["currency"] == "USD" else bool(re.search(r"\bEUR\b|€", quote))
        if not quoted_amount:
            errors.append(f"{pid}: no cited official quote contains the assigned amount")
        if not currency_proved:
            errors.append(f"{pid}: no cited official quote establishes {price['currency']}")
        if price.get("observedAt") != "2026-10-23":
            errors.append(f"{pid}: date-level price observation not recorded")

    # The independent verification log must have exactly one URL-linked snapshot per assigned row.
    snapshots = {entry["id"]: entry for entry in verification.get("entries", []) if entry.get("id", "").startswith("A182-PRICE-")}
    expected_ids = {f"A182-PRICE-{pid.upper()}" for pid in priced}
    if set(snapshots) != expected_ids:
        errors.append("dated price snapshot log does not cover exactly the assigned-price rows")
    statuses = {pid: snapshots.get(f"A182-PRICE-{pid.upper()}", {}).get("status") for pid in priced}
    corrections = {pid for pid, status in statuses.items() if status == "verified_correction"}
    if corrections != EXPECTED_CORRECTIONS:
        errors.append(f"expected only Menē price corrections, found {sorted(corrections)}")
    for pid, product in priced.items():
        entry = snapshots.get(f"A182-PRICE-{pid.upper()}")
        if not entry:
            continue
        src = by_source.get(product.get("source"))
        if entry.get("url") != (src or {}).get("url"):
            errors.append(f"{pid}: log URL does not match the product's official source")
        text = " ".join(entry.get("observed", [])) + " " + entry.get("note", "")
        if not has_number(text, product["price"]["amount"]):
            errors.append(f"{pid}: dated log does not reproduce the stored amount")
        if entry.get("checked_at") != "2026-10-23":
            errors.append(f"{pid}: missing date-only check date")

    # Only source URLs on the fixed publisher allowlist are accepted in this audit.
    for source in sources:
        parts = urlsplit(source.get("url", ""))
        if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.username or parts.password:
            errors.append(f"{source.get('id')}: URL is not an allowed official HTTPS publisher")

    # Dynamic WGC header: keep the market date and chart date separate; never fabricate a time.
    if gold.get("usd_per_troy_oz") != 3995.47 or gold.get("currency") != "USD":
        errors.append("WGC recorded amount/currency mismatch")
    if gold.get("quote_date") is not None or gold.get("chart_as_of_date") != "2026-10-22":
        errors.append("WGC quote date must stay null and chart date separate")
    if re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d*x", gold.get("quote_scope", ""), re.I):
        errors.append("WGC scope contains a fabricated/partial request timestamp")
    wgc = by_source.get("wgc-panel-review", {})
    if wgc.get("quotes", {}).get("quote") != "3,995.47":
        errors.append("WGC source quote does not match the dated spot input")
    wgc_log = next((e for e in verification.get("entries", []) if e.get("id") == "A182-MARKET-WGC-2026-10-23"), None)
    if not wgc_log or wgc_log.get("url") != wgc.get("url") or wgc_log.get("checked_at") != "2026-10-23":
        errors.append("WGC source-linked verification entry is missing")
    if 3996.31 not in [obs.get("value") for obs in gold.get("superseded_observations", [])]:
        errors.append("superseded WGC observation $3,996.31 was not retained as dated history")

    if by_product.get("mene-rose", {}).get("price", {}).get("amount") != 1325:
        errors.append("Menē Rose latest amount does not match the re-observed page")
    if by_product.get("mene-knot", {}).get("price", {}).get("amount") != 1442:
        errors.append("Menē Knot latest amount does not match the re-observed page")
    for pid, previous in (("mene-rose", "$1,336"), ("mene-knot", "$1,454")):
        source = by_source.get(pid, {})
        if previous not in source.get("quotes", {}).get("previous-price", ""):
            errors.append(f"{pid}: superseded same-day price history was not preserved")

    return errors


def main() -> int:
    data = (
        load(ROOT, "data/catalog.json"),
        load(ROOT, "research/evidence.json"),
        load(ROOT, "data/verification-log.json"),
        load(ROOT, "data/gold-price.json"),
    )
    errors = validate_data(*data)
    if errors:
        print("FAIL independent A182 provenance/hallucination audit")
        for error in errors:
            print(" -", error)
        return 1
    print("PASS independent A182 provenance/hallucination audit")
    print("44 products; 17 assigned prices source/currency-linked; 27 prices remain blank.")
    print("Menē history preserved; WGC quote date remains null; 18 official-source verification entries resolve.")
    print("Read-only structural corroboration only—not proof of seller claims or physical gold purity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
