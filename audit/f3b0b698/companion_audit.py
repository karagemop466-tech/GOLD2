#!/usr/bin/env python3
"""Independent offline audit of the companion dashboard and canonical evidence.

This scanner intentionally imports none of tools/qa.py, scripts/verify.mjs, or
dashboard/scripts/{canonical,verify}.py. It performs no network requests. PASS
means only that the checks below found no internal contradiction; it is not a
source-freshness or physical-purity certificate.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT_FILES = (
    "data/solid-gold-verified.json",
    "data/listings/solitaire.json",
    "data/listings/halo-pave.json",
    "data/listings/three-stone-vintage.json",
    "data/listings/18k.json",
    "data/listings/budget.json",
)
COMBINED = {"MENE-ROSE": "mene-rose", "MENE-KNOT": "mene-knot", "AV-BRIDGE": "av-bridge", "AV-CLEAN": "av-clean"}
ALLOWED_HOSTS = {
    "sarraf.com", "www.sarraf.com", "automicgold.com", "www.automicgold.com",
    "mejuri.com", "www.mejuri.com", "stoneandstrand.com", "www.stoneandstrand.com",
    "auvere.com", "www.auvere.com", "mene.com", "www.mene.com", "bluenile.com", "www.bluenile.com",
    "brilliantearth.com", "www.brilliantearth.com", "vrai.com", "www.vrai.com", "zales.com", "www.zales.com",
    "factorydirectjewelry.com", "www.factorydirectjewelry.com", "gold.org", "www.gold.org",
    "lbma.org.uk", "www.lbma.org.uk", "nist.gov", "www.nist.gov", "ecfr.gov", "www.ecfr.gov",
    "govinfo.gov", "www.govinfo.gov", "consumer.ftc.gov", "www.consumer.ftc.gov", "gia.edu", "www.gia.edu",
    "bbb.org", "www.bbb.org", "trustpilot.com", "www.trustpilot.com",
}
INDEPENDENT_HOSTS = {"bbb.org", "www.bbb.org", "trustpilot.com", "www.trustpilot.com"}
NUMBER = re.compile(r"(?<![\d.])\d[\d,]*(?:\.\d+)?(?![\d.])")
USD = re.compile(r"\bUSD\b|US\$", re.I)
GRAM = re.compile(r"(?<![a-z])(?:g|grams?)\b", re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def hostname(url) -> str:
    return (urlparse(url).hostname or "").lower() if isinstance(url, str) else ""


def allowlisted(url) -> bool:
    return isinstance(url, str) and urlparse(url).scheme == "https" and hostname(url) in ALLOWED_HOSTS


def primary_or_standard(url) -> bool:
    return allowlisted(url) and hostname(url) not in INDEPENDENT_HOSTS


def positive(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def exact_number(quote, value) -> bool:
    if not isinstance(quote, str) or not positive(value):
        return False
    expected = Decimal(str(value))
    for token in NUMBER.findall(quote):
        try:
            if Decimal(token.replace(",", "")) == expected:
                return True
        except Exception:
            pass
    return False


def root_quotes(row, field) -> list[str]:
    return list((row.get("field_evidence") or {}).get(field) or [])


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.ids = []
        self.csp = None
        self.events = []
        self.inline_scripts = []
        self._row = None
        self._cell = None
        self._script = False

    def handle_starttag(self, tag, attrs):
        attrs = {key.lower(): value or "" for key, value in attrs}
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        self.events.extend(key for key in attrs if key.startswith("on"))
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "content-security-policy":
            self.csp = attrs.get("content", "")
        elif tag == "script":
            self._script = True
        elif tag == "tr":
            self._row = {"id": attrs.get("id", ""), "attrs": attrs, "links": [], "cells": []}
        elif tag == "a" and self._row is not None:
            self._row["links"].append(attrs.get("href", ""))
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)
        if self._script and data.strip():
            self.inline_scripts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self._script = False
        elif tag == "td" and self._cell is not None:
            self._row["cells"].append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
            self._cell = None


def scan(repo: Path) -> dict:
    repo = Path(repo)
    dash = repo / "dashboard"
    issues = []

    def fail(code, message):
        issues.append({"code": code, "message": message})

    try:
        rings = load(dash / "data/rings.json")["rings"]
        retailers = load(dash / "data/retailers.json")["retailers"]
        flags = load(dash / "data/flags.json")["flags"]
        reference = load(dash / "data/gold-reference.json")
        root_rows = []
        for relative in ROOT_FILES:
            root_rows.extend(load(repo / relative)["items"])
        root_by_id = {row["id"]: row for row in root_rows}
        root_retailers = {r["id"]: r for r in load(repo / "data/retailers.json")["retailers"]}
        catalog = load(repo / "data/catalog.json")
        products = {p["id"]: p for p in catalog["products"]}
        sellers = {s["id"]: s for s in catalog["sellers"]}
        sources = {s["id"]: s for s in load(repo / "research/evidence.json")["sources"]}
        gold = load(repo / "data/gold-price.json")
    except Exception as exc:
        return {"status": "FAIL", "issues": [{"code": "schema", "message": str(exc)}], "stats": {}}

    ring_ids = [ring.get("id") for ring in rings]
    if len(ring_ids) != len(set(ring_ids)):
        fail("identity", "duplicate companion product IDs")
    flag_ids = {flag.get("id") for flag in flags}
    if len(flag_ids) != len(flags):
        fail("identity", "duplicate companion flag IDs")

    expected = {}
    for ring in rings:
        ring_id = ring.get("id")
        if ring_id in root_by_id:
            row = root_by_id[ring_id]
            retailer = root_retailers[row["retailer_id"]]
            currency_quotes = [q for q in root_quotes(row, "currency") if USD.search(q)]
            price_ok = (
                row.get("currency") == "USD" and positive(row.get("price")) and currency_quotes
                and any(exact_number(q, row["price"]) for q in root_quotes(row, "price"))
            )
            weight_ok = positive(row.get("weight_g")) and any(
                exact_number(q, row["weight_g"]) and GRAM.search(q) for q in root_quotes(row, "weight_g")
            )
            expected[ring_id] = {
                "kind": "root", "canonical": row, "domains": set(retailer.get("domains") or []),
                "name": row["name"], "url": row["source_url"], "karat": row["karat"],
                "solid": row.get("solid_gold_explicit"), "hallmark": row.get("hallmark_stated"),
                "capture": row["retrieved_at"], "price": row["price"] if price_ok else None,
                "weight": row["weight_g"] if weight_ok else None,
                "currency_quotes": currency_quotes[:1] if price_ok else [],
                "price_quotes": root_quotes(row, "price") if price_ok else [],
                "weight_quotes": root_quotes(row, "weight_g") if weight_ok else [],
                "canonical_flags": list(row.get("flags") or []),
                "mismatch": row.get("verification_status") == "partial_identity_mismatch",
            }
        elif ring_id in COMBINED:
            product = products[COMBINED[ring_id]]
            primary = sources[product["source"]]
            facts = product["facts"]
            price = product.get("price")
            amount_quotes, currency_quotes = [], []
            if price:
                for pointer in price.get("evidence") or []:
                    quote = sources[pointer["source"]]["quotes"][pointer["quote"]]
                    if exact_number(quote, price.get("amount")):
                        amount_quotes.append(quote)
                    if USD.search(quote):
                        currency_quotes.append(quote)
            price_ok = bool(price and price.get("currency") == "USD" and positive(price.get("amount")) and amount_quotes and currency_quotes)
            weight, weight_quotes = None, []
            net = facts.get("netMetalWeightG")
            if net:
                quote = sources[net["source"]]["quotes"][net["quote"]]
                if positive(net.get("value")) and exact_number(quote, net["value"]) and GRAM.search(quote):
                    weight, weight_quotes = net["value"], [quote]
            elif product.get("reportedWeight"):
                reported = product["reportedWeight"]
                quote = sources[reported["evidence"]["source"]]["quotes"][reported["evidence"]["quote"]]
                if (
                    reported.get("basis") == "seller-metal" and reported.get("min") == reported.get("max")
                    and positive(reported.get("min")) and exact_number(quote, reported["min"]) and GRAM.search(quote)
                ):
                    weight, weight_quotes = reported["min"], [quote]
            expected[ring_id] = {
                "kind": "combined", "canonical": product, "domains": {hostname(primary["url"])},
                "name": product["name"]["value"], "url": primary["url"], "karat": facts["karat"]["value"],
                "solid": facts["solidGold"]["value"] if facts.get("solidGold") else None,
                "hallmark": facts["hallmark"]["value"] if facts.get("hallmark") else None,
                "capture": product["observedAt"][:10], "price": price["amount"] if price_ok else None,
                "weight": weight, "currency_quotes": currency_quotes if price_ok else [],
                "price_quotes": amount_quotes if price_ok else [], "weight_quotes": weight_quotes,
                "canonical_flags": [], "mismatch": False,
            }
        else:
            fail("identity", f"companion ID has no canonical root/combined mapping: {ring_id}")

    for ring in rings:
        ring_id = ring.get("id")
        if ring_id not in expected:
            continue
        exp = expected[ring_id]
        for field, key in (("name", "name"), ("product_url", "url"), ("karat", "karat"), ("capture_date", "capture"), ("canonical_flags", "canonical_flags")):
            if ring.get(field) != exp[key]:
                fail("identity", f"{ring_id}.{field} differs from canonical evidence")
        for field, key in (("solid_gold_explicit", "solid"), ("hallmark_stated", "hallmark")):
            if ring.get(field) != exp[key]:
                fail("qualification", f"{ring_id}.{field} differs from canonical evidence")
        if hostname(ring.get("product_url")) not in exp["domains"] or not allowlisted(ring.get("product_url")):
            fail("identity", f"{ring_id} product host does not match the canonical seller")
        if ring.get("price_usd") != exp["price"]:
            fail("price", f"{ring_id} assigned/null price differs from supported canonical value")
        if ring.get("price_usd") is None:
            if "DF-011" not in ring.get("flags", []) or ring.get("price_quotes") or ring.get("currency_quotes") or ring.get("currency_source_url") is not None:
                fail("price", f"{ring_id} null price is unflagged or retains assigned-price evidence")
            if exp["mismatch"] and ring.get("unassigned_display") is not None:
                fail("price", f"{ring_id} identity mismatch retains an unassigned amount")
        else:
            price = ring["price_usd"]
            if not positive(price) or not any(exact_number(q, price) for q in ring.get("price_quotes") or []):
                fail("price", f"{ring_id} lacks exact positive amount evidence")
            if not any(USD.search(q) for q in ring.get("currency_quotes") or []):
                fail("price", f"{ring_id} lacks explicit USD evidence")
            if hostname(ring.get("currency_source_url")) not in exp["domains"]:
                fail("price", f"{ring_id} currency source is outside the seller domain")
            note = ring.get("price_note", "")
            if f"${price:,.2f}" not in note or "USD" not in note or ring.get("capture_date", "") not in note:
                fail("price", f"{ring_id} price note lacks amount/currency/date scope")
        if ring.get("price_quotes") != exp["price_quotes"] or ring.get("currency_quotes") != exp["currency_quotes"]:
            fail("evidence", f"{ring_id} price/currency quotes differ from canonical evidence")
        if ring.get("weight_g") != exp["weight"]:
            fail("weight", f"{ring_id} metal weight differs from supported canonical value")
        if ring.get("weight_g") is None:
            if "DF-003" not in ring.get("flags", []) or "Blank" not in ring.get("weight_note", ""):
                fail("weight", f"{ring_id} blank weight is not flagged and labelled")
            if ring.get("weight_quotes") or ring.get("weight_source_url") is not None:
                fail("weight", f"{ring_id} blank weight retains assigned-weight evidence")
        else:
            if not any(exact_number(q, ring["weight_g"]) and GRAM.search(q) for q in ring.get("weight_quotes") or []):
                fail("weight", f"{ring_id} lacks exact gram evidence")
            if "Not independently weighed" not in ring.get("weight_note", ""):
                fail("weight", f"{ring_id} seller weight lacks an independent-measurement limitation")
        if ring.get("weight_quotes") != exp["weight_quotes"]:
            fail("evidence", f"{ring_id} weight quotes differ from canonical evidence")
        if ring.get("solid_gold_explicit") is not True and "DF-010" not in ring.get("flags", []):
            fail("qualification", f"{ring_id} does not link the explicit-solid-gold finding")
        if "DF-007" not in ring.get("flags", []):
            fail("qualification", f"{ring_id} does not link the no-physical-test finding")
        if any(flag not in flag_ids for flag in ring.get("flags", [])):
            fail("identity", f"{ring_id} references an unknown companion flag")

    retailer_map = {retailer.get("id"): retailer for retailer in retailers}
    for dashboard_id, root_id, combined_id in (
        ("sarraf", "sarraf", "sarraf"), ("automic-gold", "automic-gold", "automic"),
        ("mejuri", "mejuri", "mejuri"), ("stone-and-strand", "stone-and-strand", "stone-and-strand"),
        ("auvere", None, "auvere"), ("mene", None, "mene"), ("blue-nile", "blue-nile", "bluenile"),
        ("brilliant-earth", "brilliant-earth", "brilliant-earth"), ("vrai", "vrai", "vrai"),
        ("zales", "zales", "zales"), ("factory-direct-jewelry", "factory-direct-jewelry", "factory-direct"),
    ):
        retailer = retailer_map.get(dashboard_id)
        if retailer is None:
            fail("seller", f"missing seller {dashboard_id}")
            continue
        if root_id and root_id in root_retailers:
            canonical = root_retailers[root_id]
            reputation = canonical["independent_reputation"]
            direct = {
                "name": canonical["name"], "site_url": canonical["website"],
                "contact_url": canonical["contact_source_url"], "returns_url": canonical["return_policy_url"],
                "return_window": canonical.get("return_window_basis"),
                "bbb_url": reputation.get("profile_url") or reputation.get("candidate_profile_url"),
            }
            for field, value in direct.items():
                if retailer.get(field) != value:
                    fail("seller", f"{dashboard_id}.{field} differs from canonical seller evidence")
            summary = retailer.get("bbb_summary") or ""
            rating = reputation.get("bbb_rating")
            if rating is None and re.search(r"BBB rating\s+\S", summary):
                fail("seller", f"{dashboard_id} has an unsupported BBB rating")
            if rating is not None and f"BBB rating {rating}" not in summary:
                fail("seller", f"{dashboard_id} BBB rating differs from canonical evidence")
            if reputation.get("identity_status") == "candidate_name_match_not_confirmed" and "identity unconfirmed" not in summary:
                fail("seller", f"{dashboard_id} candidate profile identity is not labelled")
        else:
            seller = sellers[combined_id]
            expected_window = f"{seller['returnDays']['value']} days from {seller.get('returnFrom') or 'unconfirmed trigger'}" if seller.get("returnDays") else None
            if retailer.get("return_window") != expected_window or retailer.get("resized_custom_rule") != seller.get("summary"):
                fail("seller", f"{dashboard_id} combined return/exclusion fields differ from canonical evidence")
        markers = {"return_window": "return window", "resized_custom_rule": "exclusion", "payment_protection": "payment", "contact_summary": "contact", "bbb_summary": "reputation"}
        for field, marker in markers.items():
            if retailer.get(field) is None and not any(marker in item for item in retailer.get("unverified_fields") or []):
                fail("seller", f"{dashboard_id} blank {field} is not flagged")

    if reference.get("spot_usd_per_troy_oz") != gold["usd_per_troy_oz"] or reference.get("retrieved_at") != gold["retrieved_at"]:
        fail("gold", "companion gold observation differs from canonical data")
    if reference.get("spot_quotes") != list(gold["evidence_quotes"]):
        fail("gold", "companion gold quotes differ from canonical evidence")
    if reference.get("usd_per_fine_gram") != round(gold["usd_per_troy_oz"] / gold["grams_per_troy_ounce"], 6):
        fail("gold", "companion fine-gram conversion is incorrect")

    pages = {}
    for path in sorted(dash.glob("*.html")):
        parser = Page()
        text = path.read_text(encoding="utf-8")
        parser.feed(text)
        pages[path.name] = parser
        if not parser.csp or "default-src 'self'" not in parser.csp or "connect-src 'none'" not in parser.csp or "object-src 'none'" not in parser.csp:
            fail("security", f"{path.name} lacks required CSP restrictions")
        if parser.events or parser.inline_scripts:
            fail("security", f"{path.name} contains inline script or event handlers")
        if len(parser.ids) != len(set(parser.ids)):
            fail("security", f"{path.name} contains duplicate IDs")
        for row in parser.rows:
            if row["cells"] and not any(primary_or_standard(url) for url in row["links"]):
                fail("render", f"{path.name} has a table row without an official/standards link")
        if "high counterfeit/plating risk" in text or "<1.0× signals counterfeit" in text:
            fail("policy", f"{path.name} makes an overconfident authenticity inference")
    index_text = (dash / "index.html").read_text(encoding="utf-8")
    if "No hallucinations." not in index_text or "No invented prices." not in index_text:
        fail("policy", "companion landing page lacks the prominent no-hallucination/no-invented-price rule")
    if "Keep checking for hallucinations after every review" not in index_text:
        fail("policy", "companion landing page lacks the repeat-hallucination-review recommendation")

    all_page = pages.get("rings.html")
    if all_page:
        rendered = {row["id"]: row for row in all_page.rows if row["id"].startswith("ring-")}
        if len(rendered) != len(rings):
            fail("render", "rings.html row count or IDs do not match companion data")
        for ring in rings:
            row = rendered.get(f"ring-{ring['id'].lower()}")
            if row is None or len(row["cells"]) != 6:
                fail("render", f"{ring['id']} is missing/malformed in rings.html")
                continue
            if ring["product_url"] not in row["links"] or ring["evidence_link"] not in row["links"]:
                fail("render", f"{ring['id']} lacks its official or canonical evidence link")
            if row["attrs"].get("data-solid") != ("yes" if ring["solid_gold_explicit"] is True else "no"):
                fail("render", f"{ring['id']} solid-gold filter status is wrong")
            price_text, weight_text, metric_text = row["cells"][3], row["cells"][2], row["cells"][4]
            if ring["price_usd"] is None:
                if "— (blank)" not in price_text or re.search(r"\$\s*[\d,]+(?:\.\d+)?\s+USD", price_text):
                    fail("render", f"{ring['id']} null price is rendered as assigned")
            elif f"${ring['price_usd']:,.2f} USD" not in price_text:
                fail("render", f"{ring['id']} rendered price differs from data")
            if ring["weight_g"] is None:
                if "— (blank)" not in weight_text:
                    fail("render", f"{ring['id']} blank weight is not visible")
            else:
                fine = Decimal(str(ring["weight_g"])) * Decimal(ring["karat"]) / Decimal(24)
                nominal = fine * Decimal(str(gold["usd_per_troy_oz"])) / Decimal(str(gold["grams_per_troy_ounce"]))
                if f"{ring['weight_g']:.2f} g" not in weight_text or f"{fine:.3f} g" not in metric_text or f"${nominal:,.2f}" not in metric_text:
                    fail("render", f"{ring['id']} rendered weight/fine-gold/nominal arithmetic is wrong")

    evidence_text = (dash / "evidence/rings.md").read_text(encoding="utf-8")
    for ring in rings:
        marker = f"## {ring['id']} —"
        if marker not in evidence_text:
            fail("evidence", f"{ring['id']} lacks its own evidence section")
            continue
        section = evidence_text.split(marker, 1)[1].split("\n## ", 1)[0]
        for quote in [ring["quote"], *(ring.get("price_quotes") or []), *(ring.get("currency_quotes") or []), *(ring.get("weight_quotes") or [])]:
            if quote not in section:
                fail("evidence", f"{ring['id']} evidence quote is absent from its own section")
    for path in (dash / "assets").glob("*.js"):
        source = path.read_text(encoding="utf-8")
        if re.search(r"\b(?:innerHTML|outerHTML)\s*=|\beval\s*\(|\bnew\s+Function\b|\bdocument\s*\.\s*write\s*\(|\binsertAdjacentHTML\s*\(", source):
            fail("security", f"{path.name} contains a dangerous script sink")

    stats = {
        "rings": len(rings), "retailers": len(retailers), "html_pages": len(pages),
        "assigned_prices": sum(ring.get("price_usd") is not None for ring in rings),
        "null_prices": sum(ring.get("price_usd") is None for ring in rings),
        "seller_metal_weights": sum(ring.get("weight_g") is not None for ring in rings),
        "null_weights": sum(ring.get("weight_g") is None for ring in rings),
        "explicit_solid_gold_wording": sum(ring.get("solid_gold_explicit") is True for ring in rings),
        "nonqualifying_or_unconfirmed_solid_wording": sum(ring.get("solid_gold_explicit") is not True for ring in rings),
        "physical_tests": 0,
    }
    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
        "stats": stats,
        "scope": "offline internal consistency only; no live source fetch and no physical authentication",
        "recommendation": "Look for hallucinations again after every review and rerun all repository verification/security scans.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = scan(args.root)
    text = json.dumps(report, indent=2) + "\n"
    if args.json:
        args.json.write_text(text, encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
