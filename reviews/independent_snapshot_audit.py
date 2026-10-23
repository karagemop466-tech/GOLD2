#!/usr/bin/env python3
"""Independent negative checks for a GOLD2 review snapshot.

Usage: python reviews/independent_snapshot_audit.py /path/to/extracted/snapshot

This reviewer does not edit the snapshot or treat its own evidence archive as proof
that an official page was retrieved. Official-page comparisons are recorded separately.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: independent_snapshot_audit.py SNAPSHOT_ROOT")
    root = Path(sys.argv[1]).resolve()
    findings: list[tuple[str, str, str]] = []
    passes: list[str] = []

    def flag(code: str, item: str, detail: str) -> None:
        findings.append((code, item, detail))

    listing_paths = sorted((root / "data" / "listings").glob("*.json"))
    items = []
    for path in listing_paths:
        payload = json.loads(path.read_text())
        for item in payload["items"]:
            item["_category"] = payload["category_id"]
            items.append(item)

    flags_payload = json.loads((root / "data" / "flags.json").read_text())
    flags = {entry["id"]: entry for entry in flags_payload["flags"]}

    for item in items:
        item_id = item["id"]
        evidence_path = root / item["evidence_file"]
        evidence = evidence_path.read_text()
        item_file_heading = re.search(rf"(?m)^#\s+Evidence\s+—\s+{re.escape(item_id)}\s*$", evidence)
        heading = re.search(rf"(?m)^##\s+{re.escape(item_id)}\b.*$", evidence)
        if item_file_heading:
            # Current schema: one item per evidence file, with field-scoped excerpts.
            section = evidence
        elif not heading:
            flag("EVIDENCE-SECTION", item_id, "No item-specific evidence heading")
            section = ""
        else:
            # Legacy schema: multiple items in one shared category evidence file.
            next_heading = re.search(r"(?m)^##\s+", evidence[heading.end():])
            end = heading.end() + next_heading.start() if next_heading else len(evidence)
            section = evidence[heading.start():end]

        # Field-level checks deliberately use only this item's section, not the
        # shared category file. URL text alone is not accepted as a SKU quote.
        if item.get("metal") and norm(item["metal"]) not in norm(section):
            flag("METAL-NOT-IN-ITEM-EVIDENCE", item_id, item["metal"])
        if item.get("color") and not re.search(rf"\b{re.escape(str(item['color']))}\b", section, re.I):
            flag("COLOR-NOT-IN-ITEM-EVIDENCE", item_id, str(item["color"]))
        scoped_quotes = [quote for quotes in item.get("field_evidence", {}).values() for quote in quotes]
        quote_text = " ".join([*item.get("evidence_quotes", []), *scoped_quotes])
        if item.get("sku") and norm(item["sku"]) not in norm(quote_text):
            flag("SKU-NOT-IN-QUOTES", item_id, "Identifier may be URL-derived; no SKU/style quote")
        notes = norm(item.get("notes", ""))
        affirmative_solid_claim = re.search(
            r"\b(?:is|are|was|were|made of|made from|constructed from|verified as)\s+(?!(?:not|never|no)\b)(?:\w+\s+){0,2}solid[ -]gold\b",
            notes,
        )
        if not item.get("solid_gold_explicit") and affirmative_solid_claim:
            flag("SOLID-NARRATIVE-CONTRADICTION", item_id, item["notes"])
        if item.get("width_mm") is None:
            related = [flags[fid] for fid in item.get("flags", []) if fid in flags]
            if not any("width" in (f["title"] + " " + f["detail"]).lower() for f in related):
                flag("WIDTH-BLANK-WITHOUT-WIDTH-FLAG", item_id, "Blank is titled unverified but has no width-specific flag")

    review_report = root / "reviews" / "2026-10-22-6ca03571.md"
    if review_report.exists():
        report_lines = review_report.read_text().splitlines()
        for item in items:
            matching = [line for line in report_lines if line.startswith(f"| {item['id']} |")]
            if len(matching) != 1:
                flag("REVIEW-ROW-MISSING-OR-DUPLICATE", item["id"], f"found {len(matching)}")
                continue
            line = matching[0]
            if item["source_url"] not in line:
                flag("REVIEW-SOURCE-URL-MISMATCH", item["id"], item["source_url"])
            if item.get("width_mm") is not None:
                width = Decimal(str(item["width_mm"]))
                precision = max(0, -width.as_tuple().exponent)
                accepted_widths = {f"{width:.{places}f} mm" for places in range(precision, 4)}
                if not any(value in line for value in accepted_widths):
                    flag("REVIEW-WIDTH-MISMATCH", item["id"], f"expected {item['width_mm']} mm")
            if item.get("weight_g") is not None and f"{item['weight_g']} g" not in line:
                flag("REVIEW-WEIGHT-MISMATCH", item["id"], f"expected {item['weight_g']} g")
            if item.get("price") is not None:
                mark = {"USD": "$", "EUR": "€"}.get(item["currency"], item["currency"] + " ")
                price = Decimal(str(item["price"]))
                accepted = {f"{mark}{price:,.2f}", f"{mark}{price:,.0f}"}
                if not any(value in line for value in accepted):
                    flag("REVIEW-PRICE-MISMATCH", item["id"], f"expected one of {sorted(accepted)}")

    build_text = (root / "tools" / "build_site.py").read_text()
    if any(item.get("weight_basis") for item in items) and "weight_basis" not in build_text:
        for item in items:
            if item.get("weight_basis"):
                flag("WEIGHT-CONTEXT-NOT-RENDERED", item["id"], item["weight_basis"])

    published = root / "docs" if (root / "docs" / "index.html").exists() else root
    index_text = (published / "index.html").read_text()
    report_text = (root / "reports" / "qa-report.md").read_text()
    if "not run yet" in index_text and "RESULT: PASS" in report_text:
        flag("QA-STATUS-CONTRADICTION", "site/index", "Landing says checks not run; embedded report says PASS")
    if "Nothing on this site is invented" in index_text:
        flag("ABSOLUTE-TRUTH-CLAIM", "site/index", "Policy is written as an absolute guarantee")
    if "Verified solid-gold" in index_text and any(not i["solid_gold_explicit"] for i in items):
        flag("SOLID-META-OVERSTATEMENT", "site metadata", "No listing has explicit solid-gold evidence")
    if "three things still outstanding on every row" in norm(index_text) and any(
        item.get("weight_g") is not None for item in items
    ):
        flag("WEIGHT-SUMMARY-CONTRADICTION", "site/index", "VRAI has a published weight, so weight is not outstanding on every row")

    retailers = json.loads((root / "data" / "retailers.json").read_text())["retailers"]
    if "exclusions recorded per retailer" in index_text and any(
        r.get("return_excludes_resized") is None or r.get("return_excludes_custom") is None
        for r in retailers
    ):
        flag("RETURNS-SUMMARY-OVERSTATEMENT", "site/index", "Some resized/custom exclusion fields are null")

    prices = (published / "prices.html").read_text()
    if 'for="w">Ring weight (g)' in prices and "wt * kk / 24" in prices:
        flag("GROSS-WEIGHT-CALCULATION-RISK", "calculator", "Ring weight is not explicitly metal-only; stones could be counted")
    if 'for="ask">Asking price (optional)' in prices and "USD / troy oz" in prices:
        flag("ASK-CURRENCY-MISSING", "calculator", "Ask input can be compared with a USD quote without an ask-currency label")
    for phrase in ("normal retail", "would mean sold at scrap", "Melt is a floor"):
        if phrase in prices:
            flag("UNSOURCED-MARKET-GUIDANCE", "calculator", phrase)
    inline_scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", prices, re.S)
    calc_script = "\n".join(inline_scripts)
    script_source = re.search(r'<script[^>]*\bsrc="([^"]+)"[^>]*>', prices)
    if script_source:
        source = script_source.group(1)
        if source.startswith(("https://", "http://", "//", "/")):
            flag("CALCULATOR-SCRIPT-NOT-LOCAL", "calculator", source)
        else:
            script_path = (published / source).resolve()
            try:
                script_path.relative_to(published.resolve())
                calc_script += "\n" + script_path.read_text()
            except (ValueError, OSError) as exc:
                flag("CALCULATOR-SCRIPT-UNREADABLE", "calculator", f"{source}: {exc}")
    if not calc_script.strip():
        flag("CALCULATOR-SCRIPT-MISSING", "calculator", "No inline or readable local external script")
    if "Number.isFinite" not in calc_script:
        flag("NONFINITE-INPUT-CHECK-MISSING", "calculator", "parseFloat and >0 checks do not reject Infinity")

    gold = json.loads((root / "data" / "gold-price.json").read_text())
    for quote in gold.get("evidence_quotes", []):
        date_match = re.fullmatch(r"Data as of (\d{1,2} [A-Za-z]+, \d{4})", quote)
        if date_match:
            source_date = datetime.strptime(date_match.group(1), "%d %B, %Y").date().isoformat()
            if source_date != gold.get("quote_date"):
                flag(
                    "GOLD-QUOTE-DATE-MISMATCH",
                    "data/gold-price.json",
                    f"quote_date={gold.get('quote_date')} but official excerpt says {source_date}; retrieved_at is a separate field",
                )
    grams_per_oz = Decimal(str(gold["grams_per_troy_ounce"]))
    spot = Decimal(str(gold["usd_per_troy_oz"]))
    for item in items:
        if item.get("weight_g") is None:
            continue
        fine = Decimal(str(item["weight_g"])) * Decimal(item["karat"]) / Decimal(24)
        melt = fine / grams_per_oz * spot
        expected_fine = f"{fine:.3f} g"
        expected_melt = f"${melt:,.2f}"
        if expected_fine in prices and expected_melt in prices:
            passes.append(f"ARITHMETIC {item['id']}: {expected_fine}; {expected_melt}")
        else:
            flag("ARITHMETIC-MISMATCH", item["id"], f"expected {expected_fine}; {expected_melt}")

    for karat in (10, 14, 18, 22, 24):
        row_match = re.search(rf'<tr><td class="num">{karat}K</td>(.*?)</tr>', prices)
        if not row_match:
            flag("QUICK-REFERENCE-ROW-MISSING", "calculator", f"{karat}K")
            continue
        cells = [f"{karat}K"] + re.findall(r'<td class="num">(.*?)</td>', row_match.group(1))
        ratio = Decimal(karat) / Decimal(24)
        expected = [f"{karat}K", f"{ratio * 100:.2f}%"]
        for ring_weight in (2, 4, 6):
            expected.append(f"{Decimal(ring_weight) * ratio:.3f} g")
        expected.append(f"${Decimal(6) * ratio / grams_per_oz * spot:,.2f}")
        if cells == expected:
            passes.append(f"QUICK-REFERENCE {karat}K: {' | '.join(expected)}")
        else:
            flag("QUICK-REFERENCE-MISMATCH", "calculator", f"{karat}K expected {expected}; got {cells}")

    print(f"INDEPENDENT REVIEW: {len(findings)} findings; {len(passes)} arithmetic controls passed")
    for code, item, detail in findings:
        print(f"FLAG [{code}] {item}: {detail}")
    for detail in passes:
        print(f"PASS [{detail}]")
    print("LIMITATION: these static negative checks do not replace official-page retrieval or prove truth.")
    print("NEXT: manually recheck every flag and rerun hallucination/security review after each edit.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
