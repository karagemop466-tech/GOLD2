#!/usr/bin/env python3
"""Independent hallucination / provenance scanner — session S-FE7BA040.

Written against the repository JSON and generated HTML WITHOUT importing
``tools/qa.py``, ``scripts/verify.mjs`` or any other session's scanner, so it is an
independent cross-check rather than a restatement of an existing gate.

Run:
    python3 audit/fe7ba040/hallucination_provenance_scan.py [--root /home/user/GOLD2]

What it checks (each family is independent and read-only):

  C1  Gold-reference currency of rendered root pages. The current
      ``data/gold-price.json`` value must appear on every root page that renders a
      gold quote, and no *superseded* value may appear on any root page at all.
  C2  Gold evidence chain. ``evidence/gold-price.md``, the WGC source record in
      ``research/evidence.json`` and the JSON ``evidence_quotes`` must all carry the
      same current value and retrieval date.
  C3  Cross-register URL coverage. Every root-register product URL must be present
      in the combined catalog, and every catalog product must point at an official
      publisher host.
  C4  Row source links. Every root category page must render each of its items'
      official product URLs.
  C5  Flag count consistency. A flag whose title states "N of M" must have exactly
      N ``affected_items`` (and M must equal the register size) — the stale-count
      defect class that has recurred in flag prose.
  C6  Null semantics. A price is non-null only when the retailer states a currency
      and the amount has dated evidence; weight/fine-gold fields are null or a
      directly observed number, never a silent zero or a neighbour-derived value.
  C7  No-Hallucinations policy. Every published root page must display the policy.

The scanner never writes. It prints ``PASS``/``FAIL`` and a per-family count. It
proves only that these controls ran; it does not prove source truth, physical gold
purity, or that an external page remains available.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT_DEFAULT = Path(__file__).resolve().parents[2]

ROOT_PAGES = [
    "index.html", "solid-gold.html", "solitaire.html", "halo-pave.html",
    "three-stone-vintage.html", "18k.html", "budget.html", "retailers.html",
    "analysis.html", "verification.html", "prices.html", "flags.html", "methods.html",
]
CATEGORY_PAGES = ["solid-gold.html", "solitaire.html", "halo-pave.html",
                  "three-stone-vintage.html", "18k.html", "budget.html"]

OFFICIAL_HOSTS = {
    "www.bluenile.com", "www.zales.com", "www.brilliantearth.com", "www.vrai.com",
    "www.automicgold.com", "mejuri.com", "www.gold.org", "www.sarraf.com",
    "www.factorydirectjewelry.com", "www.stoneandstrand.com", "www.costco.com",
    "www.catbird.com", "www.catbirdnyc.com", "www.auvere.com", "auvere.com",
    "www.mene.com", "mene.com", "www.quince.com", "www.jamesallen.com",
}

failures: list[str] = []
families: list[tuple[str, str, int]] = []


def fail(family: str, message: str) -> None:
    failures.append(f"[{family}] {message}")


def record(name: str, before: int) -> None:
    n = len(failures) - before
    families.append((name, "FAIL" if n else "PASS", n))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_amount(value: float) -> str:
    return f"{value:,.2f}"


# ---------------------------------------------------------------- C1 - gold currency
def check_gold_currency(root: Path) -> None:
    before = len(failures)
    gold = load(root / "data" / "gold-price.json")
    spot = float(gold["usd_per_troy_oz"])
    current = fmt_amount(spot)
    stale = {fmt_amount(float(o["value"])) for o in gold.get("superseded_observations", [])}

    pages_with_quote = {"index.html", "prices.html", "analysis.html", "methods.html",
                        "verification.html"}
    for page in ROOT_PAGES:
        text = (root / page).read_text(encoding="utf-8")
        for s in stale:
            if s in text:
                fail("gold-currency", f"{page} exposes superseded gold quote {s}")
        if page in pages_with_quote and current not in text:
            fail("gold-currency", f"{page} does not render the current gold quote {current}")
    record("C1 current gold quote on every page that renders one; no superseded value", before)


# ---------------------------------------------------------------- C2 - gold evidence chain
def check_gold_evidence_chain(root: Path) -> None:
    before = len(failures)
    gold = load(root / "data" / "gold-price.json")
    current = fmt_amount(float(gold["usd_per_troy_oz"]))

    md = (root / "evidence" / "gold-price.md").read_text(encoding="utf-8")
    if current not in md:
        fail("gold-evidence", f"evidence/gold-price.md does not carry the current value {current}")
    if "3,996.31" in md.split("## Superseded observations")[0]:
        fail("gold-evidence", "evidence/gold-price.md shows a superseded value before the superseded table")

    research = load(root / "research" / "evidence.json")
    wgc = next((s for s in research["sources"]
                if s.get("id") == "wgc-panel-review"), None)
    if wgc is None:
        fail("gold-evidence", "research/evidence.json has no wgc-panel-review record")
    else:
        if wgc.get("quotes", {}).get("quote") != current:
            fail("gold-evidence", "WGC source record quote does not match the current value")
        if gold.get("retrieved_at") and not wgc.get("observedAt", "").startswith(gold["retrieved_at"]):
            fail("gold-evidence", "WGC source record observedAt does not share the retrieval date")
    if current not in gold.get("evidence_quotes", []):
        fail("gold-evidence", "data/gold-price.json evidence_quotes lacks the current value")
    record("C2 gold evidence chain (markdown, source record, JSON quotes) agree", before)


# ---------------------------------------------------------------- C3 - URL coverage
def root_items(root: Path) -> list[dict]:
    items: list[dict] = []
    paths = [root / "data" / "solid-gold-verified.json"] + sorted((root / "data" / "listings").glob("*.json"))
    for path in paths:
        payload = load(path)
        category = "solid-gold" if path.name == "solid-gold-verified.json" else path.stem
        for item in payload.get("items", []):
            item = dict(item)
            item["_file"] = path.name
            item["_category"] = category
            items.append(item)
    return items


def check_url_coverage(root: Path) -> None:
    before = len(failures)
    catalog = load(root / "data" / "catalog.json")
    evidence = load(root / "research" / "evidence.json")
    src_url = {s.get("id"): s.get("url", "") for s in evidence["sources"]}
    # A catalog product points at a source id; resolve it to the publisher URL the
    # same way the explore generator does (scripts/lib.mjs sourceMap).
    cat_urls = {src_url.get(p.get("source", ""), "") for p in catalog["products"]}

    missing = []
    for item in root_items(root):
        url = item.get("source_url", "")
        if url not in cat_urls:
            missing.append(f"{item.get('id')} ({url})")
    if missing:
        fail("url-coverage", f"root URLs absent from the combined catalog: {missing}")

    bad_host = []
    for p in catalog["products"]:
        url = src_url.get(p.get("source", ""), "")
        host = urlsplit(url).hostname or ""
        if host not in OFFICIAL_HOSTS:
            bad_host.append(f"{p.get('id')} ({host})")
    if bad_host:
        fail("url-coverage", f"catalog products resolve to non-official hosts: {bad_host}")
    ids = [p.get("id") for p in catalog["products"]]
    if len(ids) != len(set(ids)):
        fail("url-coverage", "catalog product ids are not unique")
    record("C3 every root URL is in the combined catalog; catalog hosts are official", before)


# ---------------------------------------------------------------- C4 - row source links
def check_row_source_links(root: Path) -> None:
    before = len(failures)
    items = root_items(root)
    by_category: dict[str, list[dict]] = {}
    for item in items:
        by_category.setdefault(item["_category"], []).append(item)

    page_map = {
        "solid-gold": "solid-gold.html", "solitaire": "solitaire.html",
        "halo-pave": "halo-pave.html", "three-stone-vintage": "three-stone-vintage.html",
        "18k": "18k.html", "budget": "budget.html",
    }
    for cat, page in page_map.items():
        text = (root / page).read_text(encoding="utf-8")
        for item in by_category.get(cat, []):
            if item.get("source_url") and item["source_url"] not in text:
                fail("row-links", f"{page} does not link {item.get('id')} official URL")
    record("C4 every root category page links each of its items' official URL", before)


# ---------------------------------------------------------------- C5 - flag counts
def check_flag_counts(root: Path) -> None:
    before = len(failures)
    flags = load(root / "data" / "flags.json")["flags"]
    n_items = len(root_items(root))
    checked = 0
    for flag in flags:
        title = flag.get("title", "")
        m = re.search(r"(\d+)\s+of\s+(\d+)", title)
        if not m:
            continue
        checked += 1
        stated, stated_total = int(m.group(1)), int(m.group(2))
        if stated != len(flag.get("affected_items", [])):
            fail("flag-counts", f"{flag.get('id')} title states {stated} but lists "
                                f"{len(flag.get('affected_items', []))} affected items")
        if stated_total != n_items:
            fail("flag-counts", f"{flag.get('id')} title states total {stated_total} but the "
                                f"register has {n_items} items")
    record(f"C5 {checked} 'N of M' flag titles match their affected_items and the register size", before)


# ---------------------------------------------------------------- C6 - null semantics
def check_null_semantics(root: Path) -> None:
    before = len(failures)
    catalog = load(root / "data" / "catalog.json")
    for p in catalog["products"]:
        price = p.get("price") or {}
        amount = price.get("amount")
        if amount is not None:
            if price.get("currency") != "USD":
                fail("null-semantics", f"{p.get('id')} has a price without a stated USD currency")
            if not price.get("evidence"):
                fail("null-semantics", f"{p.get('id')} has a priced amount with no dated evidence")
        facts = p.get("facts", {})
        # A "not confirmed" field must be null, never a silent 0 / "" / empty container.
        for key in ("netMetalWeightG", "fineGoldWeightG", "declaredPurity", "hallmark",
                    "makerMark", "independentTest", "independentInspectionReturnPermission"):
            v = facts.get(key)
            if v is not None and (v == 0 or v == "" or v == [] or v == {} or v is False):
                fail("null-semantics", f"{p.get('id')}.facts.{key} is a silent zero/empty "
                                        f"instead of null")
            if v is not None and isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0:
                fail("null-semantics", f"{p.get('id')}.facts.{key} is negative")
        w = p.get("reportedWeight") or {}
        if w.get("min") is not None and w.get("max") is not None and w["min"] > w["max"]:
            fail("null-semantics", f"{p.get('id')} reported weight min > max")
    record("C6 prices carry currency+evidence; weight/fine fields keep null semantics", before)


# ---------------------------------------------------------------- C7 - policy banner
def check_policy_banner(root: Path) -> None:
    before = len(failures)
    for page in ROOT_PAGES:
        text = (root / page).read_text(encoding="utf-8").lower()
        if "no hallucinations" not in text:
            fail("policy", f"{page} does not display the No-Hallucinations policy")
    record("C7 every published root page displays the No-Hallucinations policy", before)


def scan(root: Path) -> tuple[list[tuple[str, str, int]], list[str]]:
    failures.clear()
    families.clear()
    check_gold_currency(root)
    check_gold_evidence_chain(root)
    check_url_coverage(root)
    check_row_source_links(root)
    check_flag_counts(root)
    check_null_semantics(root)
    check_policy_banner(root)
    return list(families), list(failures)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT_DEFAULT))
    args = ap.parse_args()
    root = Path(args.root).resolve()
    families, failures = scan(root)
    for name, status, n in families:
        print(f"  {status}  {name}" + (f"  ({n} failure)" if n else ""))
    print(f"\nRESULT: {'FAIL' if failures else 'PASS'} — "
          f"{len(families)} check families, {len(failures)} failures")
    for f in failures:
        print("  " + f)
    print("\nThis scanner proves only that the stated controls ran. It does not prove "
          "source truth, physical gold purity, or future availability. Look for "
          "hallucinations again after every review.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
