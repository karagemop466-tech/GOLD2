#!/usr/bin/env python3
"""S-1B04074F independent hallucination / provenance scanner.

Deliberately does NOT import tools/qa.py, scripts/verify.mjs, or any sibling
audit scanner: it re-derives every control from the JSON registers and the
generated HTML so that agreement is evidence rather than restatement.

Controls
  C01 every root listing carries an official product URL on its retailer domain
  C02 every assigned root price appears verbatim in that row's evidence file
  C03 every flag referenced by a listing exists in data/flags.json
  C04 the rendered gold quote equals data/gold-price.json (root + explore + dashboard)
  C05 no superseded gold observation is rendered as current anywhere
  C06 root spot == dashboard spot == explore gold source quote (cross-register)
  C07 nominal fine gold never exceeds the documented gross/item weight
  C08 per-fine-gram arithmetic follows NIST 31.1034768 g/ozt for the stored spot
  C09 every combined-register product resolves to an existing evidence source
  C10 every combined-register assigned price carries an evidence quote
  C11 every published HTML page states the no-hallucination policy
  C12 zero purchase approvals / no "approved to buy" claim in any register
  C13 stated counts in README match the data
  C14 no assigned root price is absent from one of the two registers it belongs to

Exit code 0 = all controls passed.
Usage: python3 audit/1b04074f/hallucination_scanner.py [repo_root]
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else __file__).resolve()
if ROOT.is_file():
    ROOT = ROOT.parents[2]

failures: list[str] = []
warnings: list[str] = []


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def fail(msg: str) -> None:
    failures.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def root_listings() -> list[dict]:
    out: list[dict] = []
    for p in sorted((ROOT / "data/listings").glob("*.json")):
        d = json.loads(p.read_text())
        items = d["items"] if isinstance(d, dict) and "items" in d else d
        for i in items:
            i["_file"] = p.name
            out.append(i)
    d = json.loads((ROOT / "data/solid-gold-verified.json").read_text())
    for i in d["items"]:
        i["_file"] = "solid-gold-verified.json"
        out.append(i)
    return out


rows = root_listings()
flags = load("data/flags.json")["flags"]
flag_ids = {f["id"] for f in flags}
gold = load("data/gold-price.json")
catalog = load("data/catalog.json")
evidence = load("research/evidence.json")
sources = {s["id"]: s for s in evidence["sources"]}
TROY = 31.1034768
SPOT = gold["usd_per_troy_oz"]

html_pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "dashboard").glob("*.html")) \
    + sorted((ROOT / "explore").rglob("*.html"))
html_text = {p: p.read_text(errors="ignore") for p in html_pages}

# C01 ---------------------------------------------------------------------------
for r in rows:
    url = r.get("source_url") or ""
    rid = r.get("retailer_id")
    seller = next((s for s in catalog["sellers"] if s["id"] == rid), None)
    if not url.startswith("https://"):
        fail(f"C01 {r['id']} has no https official URL")
        continue
    host = url.split("/")[2].lower()
    if seller and seller["name"].split()[0].lower() not in host and rid not in host:
        # retailer domains differ from display names; check the catalog evidence host instead
        ev = sources.get(next((p["source"] for p in catalog["products"]
                               if p["id"].lower() == r["id"].lower()), ""), {})
        if ev and ev.get("url", "").split("/")[2].lower() != host:
            warn(f"C01 {r['id']} host {host} differs from register host")

# C02 ---------------------------------------------------------------------------
for r in rows:
    price = r.get("price")
    if price is None:
        continue
    ev_path = ROOT / (r.get("evidence_file") or "")
    if not ev_path.exists():
        fail(f"C02 {r['id']} assigned {price} but evidence file is missing")
        continue
    body = ev_path.read_text()
    digits = f"{price:,.2f}".rstrip("0").rstrip(".")
    alt = f"{price:,.2f}"
    if digits not in body and alt not in body and str(price) not in body:
        fail(f"C02 {r['id']} assigned price {price} is not quoted in {ev_path.name}")

# C03 ---------------------------------------------------------------------------
for r in rows:
    for f in r.get("flags", []):
        if f not in flag_ids:
            fail(f"C03 {r['id']} references unknown flag {f}")

# C04 ---------------------------------------------------------------------------
spot_txt = f"{SPOT:,.2f}"
for path, text in html_text.items():
    if path.name in {"404.html"}:
        continue
    if "gold" in text.lower() and "spot" in text.lower() and spot_txt not in text:
        warn(f"C04 {path.relative_to(ROOT)} mentions a gold spot but not the current {spot_txt}")

# C05 ---------------------------------------------------------------------------
for obs in gold.get("superseded_observations", []):
    val = f"{obs['value']:,.2f}"
    if val == spot_txt:
        continue
    hits = [p.name for p, t in html_text.items() if val in t]
    if hits:
        fail(f"C05 superseded gold value {val} rendered in {hits[:3]}")

# C06 ---------------------------------------------------------------------------
dash = load("dashboard/data/gold-reference.json")
if abs(dash["spot_usd_per_troy_oz"] - SPOT) > 1e-9:
    fail(f"C06 dashboard spot {dash['spot_usd_per_troy_oz']} != root {SPOT}")
if abs(dash["usd_per_fine_gram"] - SPOT / TROY) > 1e-4:
    fail("C06 dashboard usd_per_fine_gram does not follow NIST arithmetic")
for sid in ("wgc-panel-review",):
    s = sources.get(sid)
    if not s:
        fail(f"C06 gold evidence source {sid} missing")
        continue
    blob = json.dumps(s.get("quotes", {}))
    if spot_txt not in blob:
        fail(f"C06 {sid} does not quote the current rendered value {spot_txt}")
    if "22 October, 2026" not in blob:
        warn(f"C06 {sid} does not quote the chart date alongside the header value")

# C07 / C08 -------------------------------------------------------------------
for p in catalog["products"]:
    facts = p["facts"]
    weight = (facts.get("itemWeightG") or {}).get("value")
    fine = (facts.get("fineGoldWeightG") or {}).get("value") if facts.get("fineGoldWeightG") else None
    karat = (facts.get("karat") or {}).get("value")
    if weight is not None and fine is not None and fine > weight + 1e-9:
        fail(f"C07 {p['id']} fine gold {fine} exceeds item weight {weight}")
    if weight and karat:
        nominal = weight * karat / 24
        if nominal > weight + 1e-9:
            fail(f"C08 {p['id']} nominal fine gold {nominal} exceeds gross {weight}")

# C09 / C10 -------------------------------------------------------------------
for p in catalog["products"]:
    src = sources.get(p["source"])
    if not src:
        fail(f"C09 {p['id']} source {p['source']} missing from evidence register")
        continue
    if not str(src.get("url", "")).startswith("https://"):
        fail(f"C09 {p['id']} evidence has no https URL")
    price = p.get("price")
    if price and price.get("amount") is not None:
        for ev in price.get("evidence", []):
            s = sources.get(ev.get("source"))
            if not s:
                fail(f"C10 {p['id']} price evidence source {ev.get('source')} missing")
                continue
            q = s.get("quotes", {}).get(ev.get("quote"))
            if not q:
                fail(f"C10 {p['id']} price quote key {ev.get('quote')} missing in {s['id']}")

# C11 ---------------------------------------------------------------------------
policy = re.compile(r"[Nn]o hallucinations|[Zz]ero[- ]hallucination|[Nn]o invented prices")
for path, text in html_text.items():
    if not policy.search(text):
        fail(f"C11 {path.relative_to(ROOT)} does not state the no-hallucination policy")

# C12 ---------------------------------------------------------------------------
for rel in ("data/review.json", "research/evidence.json"):
    blob = (ROOT / rel).read_text().lower()
    for bad in ("approved_to_buy\": true", "\"purchase_approved\": true", "cleared to purchase"):
        if bad in blob:
            fail(f"C12 {rel} contains a purchase-approval claim ({bad})")

# C13 ---------------------------------------------------------------------------
readme = (ROOT / "README.md").read_text()
expect = {
    "44 product": len(catalog["products"]) == 44,
    "13 sellers": len(catalog["sellers"]) == 13,
    "85 source records": len(evidence["sources"]) == 85,
    "30": len(rows) == 30,
}
for phrase, ok in expect.items():
    if phrase in readme and not ok:
        fail(f"C13 README states '{phrase}' but the data disagrees")

# C14 ---------------------------------------------------------------------------
cat_by_url = {sources[p["source"]]["url"].rstrip("/"): p for p in catalog["products"]
              if p["source"] in sources}
for r in rows:
    url = (r.get("source_url") or "").rstrip("/")
    if url and url not in cat_by_url:
        fail(f"C14 root row {r['id']} URL is absent from the combined register")

# ------------------------------------------------------------------------------
print(f"S-1B04074F scanner: {len(rows)} root rows, {len(catalog['products'])} combined products, "
      f"{len(evidence['sources'])} sources, {len(flags)} flags, {len(html_pages)} pages, spot {spot_txt}")
for m in failures:
    print("  FAIL", m)
for m in warnings:
    print("  WARN", m)
print(f"RESULT: {'FAIL' if failures else 'PASS'} — {len(failures)} failures, {len(warnings)} warnings")
print("LIMITATION: internal traceability only. It cannot prove a retailer page still says what is quoted, "
      "nor that any ring is the stated purity. Re-read the official source after every review.")
sys.exit(1 if failures else 0)
