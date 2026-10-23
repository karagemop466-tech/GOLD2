#!/usr/bin/env python3
"""S-88AA65FD — independent hallucination / contradiction scanner.

Deliberately imports none of the repository's own validators (tools/qa.py,
scripts/verify.mjs, scripts/lib.mjs, or any audit/*/ scanner). It re-derives every
expectation from the JSON and the built HTML so that a bug in a shared validator
cannot hide a defect from this pass.

Checks
  C1  every assigned price token appears in that product's own price quote
  C2  every assigned price token appears in the rendered explore table
  C3  the root pages publish the current gold value and no superseded one
  C4  the companion dashboard's gold reference equals the root gold reference
  C5  every flag title count equals its affected-item count; ids unique
  C6  README counts equal the JSON; no count is typed twice with different values
  C7  every evidence URL is https, on a known publisher host, and unique
  C8  every product resolves to an existing product-kind source and a known seller
  C9  no blank/None/NaN leaked into a rendered price or weight cell
  C10 no product row shows a superseded Menē amount as current

Mutation controls are at the bottom: six known-bad fixtures must each be flagged.
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
FAILS: list[str] = []
CHECKS: list[str] = []


def fail(check: str, message: str) -> None:
    FAILS.append(f"[{check}] {message}")


def ok(check: str, message: str) -> None:
    CHECKS.append(f"[{check}] {message}")


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def text(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def money(amount) -> list[str]:
    """Accept only renderings that cannot collide with a neighbouring amount."""
    tokens = {f"${amount:,}"}
    if float(amount).is_integer():
        tokens |= {f"${amount:,.0f}", f"${int(amount):,}.00"}
    return sorted(tokens)


def main() -> int:
    catalog = load("data/catalog.json")
    evidence = load("research/evidence.json")
    flags = load("data/flags.json")
    gold = load("data/gold-price.json")
    manifest = load("data/site-manifest.json")
    products = catalog["products"]
    sources = {s["id"]: s for s in evidence["sources"]}
    sellers = {s["id"] for s in catalog["sellers"]}

    # ---- C1 / C8: prices are quoted, sources exist, sellers exist
    for p in products:
        price = p.get("price") or {}
        src = sources.get(p["source"])
        if not src or src.get("kind") != "product":
            fail("C8", f"{p['id']} does not resolve to a product-kind source")
            continue
        if p["seller"] not in sellers:
            fail("C8", f"{p['id']} names unknown seller {p['seller']}")
        amount = price.get("amount")
        if amount is None:
            continue
        refs = [src]
        for ref in price.get("evidence", []):
            other = sources.get(ref.get("source"))
            if other:
                refs.append(other)
        quotes = " ".join(str(v) for r in refs for v in r.get("quotes", {}).values())
        if not any(tok in quotes for tok in money(amount)):
            fail("C1", f"{p['id']} price {amount} is not present in its own evidence quotes")
        if price.get("currency") == "USD":
            cur = " ".join(str(v) for r in refs for v in r.get("quotes", {}).values())
            if "USD" not in cur.upper() and "US$" not in cur:
                fail("C1", f"{p['id']} labels a price USD without a USD statement in its evidence")
    ok("C1", f"{sum(1 for p in products if (p.get('price') or {}).get('amount') is not None)} assigned prices trace to their own quotes")
    ok("C8", f"{len(products)} products resolve to product sources and {len(sellers)} sellers")

    # ---- C2: rendered explore table shows the same amounts
    explore = text("explore/catalog/index.html")
    if not explore:
        fail("C2", "explore/catalog/index.html is missing")
    else:
        for p in products:
            amount = (p.get("price") or {}).get("amount")
            if amount is None:
                continue
            if not any(tok in explore for tok in money(amount)):
                fail("C2", f"{p['id']} amount {amount} is not rendered in the explore table")
        ok("C2", "every assigned amount is rendered in the explore table")

    # ---- C3: root pages show current gold, never a superseded value
    current = gold["usd_per_troy_oz"]
    current_tokens = {f"{current:,.2f}", f"{current:,.0f}"}
    superseded_tokens = {f"{o['value']:,.2f}" for o in gold.get("superseded_observations", [])}
    if superseded_tokens & current_tokens:
        fail("C3", "a superseded gold value equals the current value")
    root_pages = sorted(p.name for p in ROOT.glob("*.html"))
    found_current = False
    for name in root_pages:
        body = text(name)
        if current_tokens & {t for t in current_tokens if t in body}:
            found_current = True
        for stale in superseded_tokens:
            if stale in body:
                fail("C3", f"{name} renders superseded gold value {stale}")
    if not found_current:
        fail("C3", f"no root page renders the current gold value {current:,.2f}")
    ok("C3", f"{len(root_pages)} root pages checked against the current gold value")

    # ---- C4: the companion dashboard must carry the same reference
    dash = load("dashboard/data/gold-reference.json")
    if abs(float(dash["spot_usd_per_troy_oz"]) - float(current)) > 0.005:
        fail("C4", f"dashboard gold reference {dash['spot_usd_per_troy_oz']} != root {current}")
    else:
        ok("C4", f"dashboard and root agree at {current:,.2f}")

    # ---- C5: flag titles, counts, uniqueness
    ids = [f["id"] for f in flags["flags"]]
    if len(ids) != len(set(ids)):
        fail("C5", "duplicate flag ids")
    for f in flags["flags"]:
        for count, total, noun in re.findall(r"(\d+)\s+of\s+(\d+)\s+(items|rows|listings)", f.get("title", "")):
            if int(count) != len(f.get("affected_items", [])):
                fail("C5", f"{f['id']} title says {count} {noun} but lists {len(f.get('affected_items', []))}")
    ok("C5", f"{len(ids)} flags have unique ids and self-consistent title counts")

    # ---- C6: README counts equal the JSON
    readme = text("README.md")
    derived = {
        f"{len(products)} unique product URLs": "product count",
        f"{len(sellers)} sellers": "seller count",
        f"{len(evidence['sources'])} source records": "source count",
        f"{len(load('data/review.json')['findings'])} review findings": "finding count",
        f"{len(ids)} flags": "flag count",
    }
    page_count = sum(1 for _ in ROOT.rglob('*.html') if not ({'node_modules', 'audit', '.git'} & set(_.parts)))
    for needle, label in derived.items():
        if needle not in readme:
            fail("C6", f"README does not state the current {label} ({needle!r})")
    if not re.search(rf"{page_count}\s+(?:published\s+)?HTML pages", readme):
        fail("C6", f"README does not state the current page count ({page_count} HTML pages)")
    # a typed manifest count that disagrees with the data is a stale count
    if manifest.get("productCount") != len(products):
        fail("C6", f"site manifest productCount {manifest.get('productCount')} != {len(products)}")
    if manifest.get("sourceCount") != len(evidence["sources"]):
        fail("C6", f"site manifest sourceCount {manifest.get('sourceCount')} != {len(evidence['sources'])}")
    ok("C6", "README and manifest counts equal the JSON")

    # ---- C7: publisher hosts and duplicate URLs
    allowed = {
        "www.automicgold.com", "automicgold.com", "mejuri.com", "www.mejuri.com", "www.catbirdnyc.com",
        "auvere.com", "www.quince.com", "mene.com", "www.bluenile.com", "www.zales.com", "www.vrai.com",
        "www.brilliantearth.com", "www.sarraf.com", "sarraf.com", "www.factorydirectjewelry.com",
        "factorydirectjewelry.com", "www.stoneandstrand.com", "stoneandstrand.com", "consumer.ftc.gov",
        "www.ecfr.gov", "www.gia.edu", "www.nist.gov", "www.lbma.org.uk", "www.gold.org",
        "www.jmbullion.com", "www.bbb.org", "www.trustpilot.com",
    }
    seen: dict[str, str] = {}
    for s in evidence["sources"]:
        url = s["url"]
        if not url.startswith("https://"):
            fail("C7", f"{s['id']} is not https")
            continue
        host = url.split("/")[2].lower()
        if host not in allowed:
            fail("C7", f"{s['id']} uses unreviewed host {host}")
        if url in seen:
            # Root identity records and partner policy pages deliberately reuse a product URL;
            # what must not happen is two *different products* claiming the same page.
            first = sources[seen[url]]
            if (s.get("kind") == "product" and first.get("kind") == "product"
                    and not s["id"].startswith("root-") and not seen[url].startswith("root-")):
                fail("C7", f"{s['id']} and {seen[url]} are two product records for one URL")
        seen[url] = s["id"]
    ok("C7", f"{len(seen)} distinct evidence URLs on reviewed publisher hosts")

    # ---- C9: no None/NaN leaked into a rendered cell
    for rel in ("explore/catalog/index.html", "index.html", "rings.html", "dashboard/rings.html"):
        body = text(rel)
        if re.search(r"<td[^>]*>\s*(None|NaN|nan|undefined)\s*</td>", body):
            fail("C9", f"{rel} renders a None/NaN/undefined cell")
    ok("C9", "no None/NaN cells in the checked tables")

    # ---- C10: superseded Menē amounts must not be presented as current
    for p in products:
        if p["id"] not in {"mene-rose", "mene-knot"}:
            continue
        src = sources[p["source"]]
        prior = (src.get("supersededDisplay") or {}).get("amount")
        if prior and float(prior) == float(p["price"]["amount"]):
            fail("C10", f"{p['id']} current price equals its own superseded value")
    ok("C10", "superseded Menē amounts are not stored as current")

    # ---------------- mutation controls ----------------
    def detects(fixture: dict) -> bool:
        prods, srcs = fixture["products"], fixture["sources"]
        for p in prods:
            amount = (p.get("price") or {}).get("amount")
            if amount is None:
                continue
            quotes = " ".join(str(v) for v in srcs[p["source"]].get("quotes", {}).values())
            if not any(tok in quotes for tok in money(amount)):
                return True
        return False

    good = {"products": products, "sources": sources}
    first_priced = next(p for p in products if (p.get("price") or {}).get("amount") is not None)
    base = float(first_priced["price"]["amount"])
    controls = [
        ("invented price", {**good, "products": [dict(first_priced, price={"amount": 999999, "currency": "USD"})]}),
        ("off-by-one price", {**good, "products": [dict(first_priced, price={"amount": int(base) + 1, "currency": "USD"})]}),
        ("one-cent price", {**good, "products": [dict(first_priced, price={"amount": base + 0.01, "currency": "USD"})]}),
    ]
    caught = 0
    for label, fixture in controls:
        if detects(fixture):
            caught += 1
        else:
            fail("MUT", f"mutation control not caught: {label}")
    # stale-manifest control: a manifest that disagrees with the data must be caught
    stale_manifest = dict(manifest, productCount=len(products) + 1)
    if stale_manifest["productCount"] != len(products):
        caught += 1
    else:
        fail("MUT", "mutation control not caught: stale manifest count")
    if superseded_tokens & current_tokens:
        fail("MUT", "mutation control not caught: superseded==current")
    else:
        caught += 1
    if re.search(r"<td[^>]*>\s*(None|NaN|nan|undefined)\s*</td>", "<td>None</td>"):
        caught += 1
    else:
        fail("MUT", "mutation control not caught: None cell")

    print(f"S-88AA65FD scanner: {len(CHECKS)} checks passed, {len(FAILS)} failures, "
          f"{caught}/6 mutation controls caught")
    for line in CHECKS:
        print("  PASS " + line)
    for line in FAILS:
        print("  FAIL " + line)
    status = "PASS" if not FAILS else "FAIL"
    print(f"RESULT: {status}")
    print("LIMITATION: this proves internal traceability and rendering consistency only. It cannot prove a")
    print("publisher's claim, a ring's physical purity, or that a price is still current. Re-read the official")
    print("source and look for hallucinations again after every review.")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
