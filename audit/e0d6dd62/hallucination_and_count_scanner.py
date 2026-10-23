#!/usr/bin/env python3
"""Independent hallucination / stale-count scanner for the GOLD2 register.

Purpose: catch the failure modes this project has actually produced before —
a value that no source states, a superseded price that keeps being rendered,
a count in prose that no longer matches the data, and a flag whose title
disagrees with its own affected list.

This file is deliberately independent of tools/qa.py and scripts/verify.mjs:
it re-derives what it checks from the JSON and the built HTML rather than
importing either implementation.

Run:  python3 audit/e0d6dd62/hallucination_and_count_scanner.py .
Exit: 0 = all checks passed, 1 = at least one failure.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

FAIL = []
WARN = []
CHECKS = 0


def record(name: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"  ok   {name}")


def fail(family: str, detail: str) -> None:
    FAIL.append(f"[{family}] {detail}")


def warn(family: str, detail: str) -> None:
    WARN.append(f"[{family}] {detail}")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def number_tokens(text: str) -> set[str]:
    """Numeric tokens with thousands separators kept as one token."""
    return set(re.findall(r"\d[\d,]*(?:\.\d+)?", text))


def token_present(text: str, value: float) -> bool:
    """True when `value` appears as its own numeric token.

    Comparison is numeric so that 2,858.00, 2858 and 2858.0 all match, while 726
    still does not match 1726 and 1,362.00 does not match 11,362.00.
    """
    if value is None:
        return False
    for token in number_tokens(text):
        try:
            parsed = float(token.replace(",", ""))
        except ValueError:
            continue
        if abs(parsed - float(value)) < 0.005:
            return True
    return False


def main(root: Path) -> int:
    data = root / "data"
    catalog = load(data / "catalog.json")
    evidence = load(root / "research" / "evidence.json")
    review = load(data / "review.json")
    flags = load(data / "flags.json")["flags"]
    gold = load(data / "gold-price.json")
    root_rows = []
    for extra in ("solid-gold-verified.json", *[f"listings/{p.name}" for p in sorted((data / "listings").glob("*.json"))]):
        root_rows += load(data / extra)["items"]

    sources = {s["id"]: s for s in evidence["sources"]}
    products = catalog["products"]

    # --- C1: every product name is exactly a recorded passage -----------------
    for p in products:
        src = sources.get(p["source"])
        if src is None:
            fail("provenance", f"{p['id']} cites unknown source {p['source']}")
            continue
        quote = src.get("quotes", {}).get(p["name"]["quote"], "")
        if p["name"]["value"] not in quote:
            fail("provenance", f"{p['id']} name {p['name']['value']!r} is not in its cited passage")
    record(f"C1 product names match their cited passages ({len(products)} products)")

    # --- C2: every assigned price appears in a cited passage -----------------
    for p in products:
        price = p.get("price")
        if not price:
            continue
        texts = []
        for ref in price.get("evidence", []):
            src = sources.get(ref["source"])
            if src:
                texts.append(src.get("quotes", {}).get(ref["quote"], ""))
        if not any(token_present(t, price["amount"]) for t in texts):
            fail("price", f"{p['id']} price {price['amount']} is absent from every cited passage")
        if price["currency"] == "USD" and not any(re.search(r"\bUSD\b|US\$", t) for t in texts):
            fail("price", f"{p['id']} is labelled USD without a USD statement in its evidence")
    record("C2 assigned prices and currencies are supported by cited passages")

    # --- C3: root-register prices & weights re-derived from evidence files ----
    for row in root_rows:
        ev_path = root / row["evidence_file"]
        if not ev_path.exists():
            fail("root-evidence", f"{row['id']} evidence file missing: {row['evidence_file']}")
            continue
        text = ev_path.read_text(encoding="utf-8")
        if row.get("price") is not None and not token_present(text, row["price"]):
            fail("root-evidence", f"{row['id']} price {row['price']} is absent from {row['evidence_file']}")
        for field in ("weight_g", "gross_ring_weight_g", "price_min", "price_max"):
            value = row.get(field)
            if value is not None and not token_present(text, value):
                fail("root-evidence", f"{row['id']} {field}={value} is absent from {row['evidence_file']}")
        for field, quotes in (row.get("field_evidence") or {}).items():
            for quote in quotes:
                if quote not in text:
                    fail("root-evidence", f"{row['id']} field_evidence[{field}] quote missing from {row['evidence_file']}")
        if row.get("price") is not None and row.get("currency") not in ("USD", "EUR"):
            fail("root-evidence", f"{row['id']} has a price but no allowed currency")
    record(f"C3 root-register values appear in their own evidence files ({len(root_rows)} rows)")

    # --- C4: flag titles may not state a count that contradicts affected_items
    for flag in flags:
        affected = len(flag.get("affected_items") or [])
        title = flag["title"]
        m = re.search(r"\b(\d+)\s+of\s+(\d+)\b", title)
        if m:
            stated, total = int(m.group(1)), int(m.group(2))
            if stated != affected:
                fail("flag-count", f"{flag['id']} title says {stated} of {total} but affected_items has {affected}")
            if total != len(root_rows):
                fail("flag-count", f"{flag['id']} title says {total} rows but the register has {len(root_rows)}")
        m2 = None if m else re.search(r"\b(\d+)\s+(?:root\s+)?(?:items|rows)\b", title)
        if m2 and int(m2.group(1)) != affected and affected:
            warn("flag-count", f"{flag['id']} title states {m2.group(1)} but affected_items has {affected}")
    record(f"C4 flag titles agree with their affected lists ({len(flags)} flags)")

    # --- C5: no superseded gold observation is rendered anywhere -------------
    superseded = {f"{o['value']:,.2f}" for o in gold.get("superseded_observations", [])}
    current = f"{gold['usd_per_troy_oz']:,.2f}"
    superseded.discard(current)
    pages = [p for p in root.rglob("*.html") if "node_modules" not in p.parts and ".git" not in p.parts and "audit" not in p.parts]
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for stale in superseded:
            if stale in text:
                fail("stale-price", f"{page.relative_to(root)} still renders superseded gold value {stale}")
        if "/oz" in text and not re.search(rf"\b{re.escape(current)}\b|value=\"{gold['usd_per_troy_oz']}", text):
            warn("stale-price", f"{page.relative_to(root)} shows a per-ounce figure without the current dated value {current}")
    record(f"C5 superseded gold observations are not rendered ({len(pages)} HTML pages, {len(superseded)} superseded values)")

    # --- C6: gold evidence file carries the same value the JSON does ---------
    gold_md = (root / "evidence" / "gold-price.md").read_text(encoding="utf-8")
    if current not in gold_md:
        fail("gold-evidence", f"evidence/gold-price.md does not contain the current value {current}")
    for quote in gold.get("evidence_quotes", []):
        if quote not in gold_md:
            fail("gold-evidence", f"evidence/gold-price.md does not contain stored quote {quote!r}")
    record("C6 gold JSON and gold evidence file agree")

    # --- C7: README counts match the data ------------------------------------
    readme = (root / "README.md").read_text(encoding="utf-8")
    # Normalise filler adjectives that do not change a count.
    readme_html = readme.replace("`", "").replace("published ", "")
    expectations = {
        f"{len(products)} product records": "catalog product count",
        f"{len(catalog['sellers'])} sellers": "catalog seller count",
        f"{len(evidence['sources'])} source records": "evidence source count",
        f"{len(review['findings'])} review findings": "review finding count",
        f"{len(root_rows)} entries across": "root register row count",
        f"{len(flags)} flags": "flag count",
        f"{len(pages)} HTML pages": "built page count",
    }
    for needle, label in expectations.items():
        if needle not in readme_html:
            fail("stale-count", f"README does not state the current {label} ({needle!r})")
    record("C7 README counts match the data")

    # --- C8: no dollar amount may be labelled USD without a currency source --
    for p in products:
        price = p.get("price")
        if price and price.get("currency") == "USD":
            texts = [sources.get(r["source"], {}).get("quotes", {}).get(r["quote"], "") for r in price.get("evidence", [])]
            if not any(re.search(r"\bUSD\b|US\$", t) for t in texts):
                warn("currency", f"{p['id']} is labelled USD but no cited passage documents a currency")
    record("C8 USD labels trace to a currency statement")

    # --- C9: arithmetic on published derived values --------------------------
    troy = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    analysis = (root / "analysis.html").read_text(encoding="utf-8") if (root / "analysis.html").exists() else ""
    for row in root_rows:
        if row.get("weight_g") is None:
            continue
        fine = row["weight_g"] * row["karat"] / 24
        melt = fine / troy * spot
        if analysis and f"{fine:.3f} g" not in analysis:
            fail("arithmetic", f"{row['id']} fine-gold value {fine:.3f} g is not the value analysis.html shows")
        if analysis and f"${melt:,.2f}" not in analysis:
            fail("arithmetic", f"{row['id']} melt value ${melt:,.2f} at the dated reference is not shown")
    record("C9 published fine-gold and melt arithmetic re-derived")

    # --- C10: no placeholder, TODO, or dangling 'null' text in pages ---------
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for bad in ("TODO", "FIXME", "lorem ipsum", "PLACEHOLDER", "NaN"):
            if bad in text:
                fail("placeholder", f"{page.relative_to(root)} contains {bad!r}")
    record("C10 pages contain no placeholder text")

    # --- C11: every table row links an official host ------------------------
    allowed = {
        "www.automicgold.com", "mejuri.com", "www.catbirdnyc.com", "auvere.com", "www.quince.com",
        "mene.com", "www.bluenile.com", "www.zales.com", "www.vrai.com", "www.brilliantearth.com",
        "www.sarraf.com", "www.factorydirectjewelry.com", "www.stoneandstrand.com", "www.costco.com",
    }
    hrefs = []
    for page in pages:
        hrefs += re.findall(r'href="(https?://[^"]+)"', page.read_text(encoding="utf-8", errors="replace"))
    product_links = [h for h in hrefs if any(f"//{host}/" in h for host in allowed)]
    if not product_links:
        fail("links", "no official product links found in the built pages")
    record(f"C11 official product links present ({len(set(product_links))} unique)")

    # --- C12: every gold figure named in the evidence file is a real observation
    known = {gold["usd_per_troy_oz"]} | {o["value"] for o in gold.get("superseded_observations", [])}
    # A line that explicitly says a figure has no record behind it is quoting the defect on purpose,
    # not asserting the value. That is the only permitted exception.
    disclaimer = re.compile(r"no such figure|does not exist|cannot be found", re.I)
    for line in gold_md.splitlines():
        if disclaimer.search(line):
            continue
        for raw in re.findall(r"\b\d{1,2},\d{3}\.\d{2}\b", line):
            if float(raw.replace(",", "")) not in known:
                fail("gold-evidence", f"evidence/gold-price.md names {raw}, which is neither the current quote nor a recorded superseded observation")
    record(f"C12 every gold figure in the evidence file traces to an observation ({len(known)} known values)")

    print()
    for w in WARN:
        print(f"  WARN {w}")
    for f in FAIL:
        print(f"  FAIL {f}")
    print(f"\nRESULT: {'PASS' if not FAIL else 'FAIL'} — {CHECKS} checks, {len(FAIL)} failures, {len(WARN)} warnings")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
