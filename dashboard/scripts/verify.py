#!/usr/bin/env python3
"""Independent consistency, provenance, link, and security checks for dashboard/.

The canonical root/combined registers are the comparison source. This script does
not fetch pages and a PASS is not source freshness, physical authentication, or
proof that every possible hallucination is absent. Run the repository-wide review,
security, and hallucination passes again after every review.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date, datetime
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from canonical import COMBINED_IDS, RETAILER_METADATA, RING_METADATA, ROOT_LISTING_FILES

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"
LOG_PATH = ROOT / "verification-log.json"

ALLOWED_DOMAINS = {
    "sarraf.com", "www.sarraf.com",
    "automicgold.com", "www.automicgold.com",
    "mejuri.com", "www.mejuri.com",
    "stoneandstrand.com", "www.stoneandstrand.com",
    "auvere.com", "www.auvere.com",
    "mene.com", "www.mene.com",
    "bluenile.com", "www.bluenile.com",
    "brilliantearth.com", "www.brilliantearth.com",
    "vrai.com", "www.vrai.com",
    "zales.com", "www.zales.com",
    "factorydirectjewelry.com", "www.factorydirectjewelry.com",
    "gold.org", "www.gold.org",
    "lbma.org.uk", "www.lbma.org.uk",
    "nist.gov", "www.nist.gov",
    "ecfr.gov", "www.ecfr.gov",
    "govinfo.gov", "www.govinfo.gov",
    "consumer.ftc.gov", "www.consumer.ftc.gov",
    "gia.edu", "www.gia.edu",
    "bbb.org", "www.bbb.org",
    "trustpilot.com", "www.trustpilot.com",
}
INDEPENDENT_ONLY_DOMAINS = {"bbb.org", "www.bbb.org", "trustpilot.com", "www.trustpilot.com"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
USD_RE = re.compile(r"\bUSD\b|US\$", re.IGNORECASE)
GRAM_RE = re.compile(r"(?<![a-z])(?:g|grams?)\b", re.IGNORECASE)
NUMBER_RE = re.compile(r"(?<![\d.])\d[\d,]*(?:\.\d+)?(?![\d.])")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def positive_number(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def quote_has_number(quote: str, value) -> bool:
    if not positive_number(value) or not isinstance(quote, str):
        return False
    expected = Decimal(str(value))
    for token in NUMBER_RE.findall(quote):
        try:
            if Decimal(token.replace(",", "")) == expected:
                return True
        except Exception:
            continue
    return False


def quotes(row: dict, field: str) -> list[str]:
    return list((row.get("field_evidence") or {}).get(field) or [])


def valid_date(value) -> bool:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() <= date.today()
    except ValueError:
        return False


def host(url: str | None) -> str:
    return (urlparse(url).hostname or "").lower() if url else ""


def is_official(url: str | None) -> bool:
    """Backward-compatible name: an allowlisted HTTPS evidence destination."""
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and host(url) in ALLOWED_DOMAINS


def is_primary_or_standard(url: str | None) -> bool:
    return is_official(url) and host(url) not in INDEPENDENT_ONLY_DOMAINS


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


class LinkAndRowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.rows: list[dict] = []
        self.has_csp = False
        self.csp = ""
        self.event_attributes: list[str] = []
        self.inline_scripts: list[str] = []
        self.script_sources: list[str] = []
        self._row: dict | None = None
        self._cell: list[str] | None = None
        self._in_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {key.lower(): (value or "") for key, value in attrs}
        if amap.get("id"):
            self.ids.append(amap["id"])
        for key in amap:
            if key.startswith("on"):
                self.event_attributes.append(key)
        if tag == "meta" and amap.get("http-equiv", "").lower() == "content-security-policy":
            self.has_csp = True
            self.csp = amap.get("content", "")
        elif tag == "script":
            self._in_script = True
            if amap.get("src"):
                self.script_sources.append(amap["src"])
        elif tag == "a":
            href = amap.get("href", "")
            self.hrefs.append(href)
            if self._row is not None:
                self._row["links"].append(href)
        elif tag == "tr":
            self._row = {"id": amap.get("id"), "attrs": amap, "links": [], "cells": []}
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)
        if self._in_script and data.strip():
            self.inline_scripts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_script = False
        elif tag == "td" and self._row is not None and self._cell is not None:
            self._row["cells"].append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
            self._cell = None


def main() -> int:
    check_build = "--check-build" in sys.argv
    failures: list[str] = []
    passes: dict[str, str] = {}

    rings_doc = load_json(DATA / "rings.json")
    retailers_doc = load_json(DATA / "retailers.json")
    flags_doc = load_json(DATA / "flags.json")
    rings = rings_doc["rings"]
    retailers = retailers_doc["retailers"]
    flags = flags_doc["flags"]
    ref = load_json(DATA / "gold-reference.json")
    rings_ev = (EVIDENCE / "rings.md").read_text(encoding="utf-8")
    ret_ev = (EVIDENCE / "retailers.md").read_text(encoding="utf-8")

    root_rows = []
    for relative in ROOT_LISTING_FILES:
        root_rows.extend(load_json(REPO_ROOT / relative)["items"])
    root_by_id = {row["id"]: row for row in root_rows}
    root_retailers = {
        retailer["id"]: retailer
        for retailer in load_json(REPO_ROOT / "data/retailers.json")["retailers"]
    }
    catalog = load_json(REPO_ROOT / "data/catalog.json")
    product_by_id = {product["id"]: product for product in catalog["products"]}
    seller_by_id = {seller["id"]: seller for seller in catalog["sellers"]}
    evidence = load_json(REPO_ROOT / "research/evidence.json")
    sources = {source["id"]: source for source in evidence["sources"]}
    findings = load_json(REPO_ROOT / "data/review.json")["findings"]
    canonical_flag_ids = {flag["id"] for flag in load_json(REPO_ROOT / "data/flags.json")["flags"]}
    gold = load_json(REPO_ROOT / "data/gold-price.json")
    ring_by_id = {ring["id"]: ring for ring in rings}
    retailer_by_id = {retailer["id"]: retailer for retailer in retailers}
    flag_ids = {flag["id"] for flag in flags}

    def run_pass(code: str, function) -> None:
        before = len(failures)
        function()
        passes[code] = "PASS" if len(failures) == before else "FAIL"

    def expected_ring(ring_id: str) -> dict:
        categories = next(categories for candidate, categories in RING_METADATA if candidate == ring_id)
        if ring_id in root_by_id:
            row = root_by_id[ring_id]
            retailer = root_retailers[row["retailer_id"]]
            currency_quotes = [quote for quote in quotes(row, "currency") if USD_RE.search(quote)]
            price_supported = (
                row.get("currency") == "USD"
                and positive_number(row.get("price"))
                and any(quote_has_number(quote, row["price"]) for quote in quotes(row, "price"))
                and bool(currency_quotes)
            )
            weight_supported = positive_number(row.get("weight_g")) and any(
                quote_has_number(quote, row["weight_g"]) and GRAM_RE.search(quote)
                for quote in quotes(row, "weight_g")
            )
            mismatch = row.get("verification_status") == "partial_identity_mismatch"
            displays = []
            if not price_supported and not mismatch:
                if row.get("unassigned_price_text"):
                    displays.append(row["unassigned_price_text"])
                displays.extend(row.get("observed_native_display") or [])
            return {
                "canonical": row,
                "seller": retailer,
                "domains": set(retailer.get("domains") or []),
                "expected": {
                    "id": ring_id,
                    "retailer_id": row["retailer_id"],
                    "retailer": row["retailer"],
                    "categories": list(categories),
                    "name": row["name"],
                    "karat": row["karat"],
                    "solid_gold_explicit": row.get("solid_gold_explicit") if isinstance(row.get("solid_gold_explicit"), bool) else None,
                    "hallmark_stated": row.get("hallmark_stated") if isinstance(row.get("hallmark_stated"), bool) else None,
                    "weight_g": row["weight_g"] if weight_supported else None,
                    "price_usd": row["price"] if price_supported else None,
                    "unassigned_display": "; ".join(unique(displays)) or None,
                    "capture_date": row["retrieved_at"],
                    "product_url": row["source_url"],
                    "quote": quotes(row, "name")[0],
                    "price_quotes": quotes(row, "price") if price_supported else [],
                    "currency_quotes": currency_quotes[:1] if price_supported else [],
                    "currency_source_url": (row.get("currency_source_url") or row["source_url"]) if price_supported else None,
                    "weight_quotes": quotes(row, "weight_g") if weight_supported else [],
                    "weight_source_url": row["source_url"] if weight_supported else None,
                    "evidence_link": "../" + row["evidence_file"],
                    "verification_status": row.get("verification_status"),
                    "canonical_flags": list(row.get("flags") or []),
                    "review_flags": [],
                    "canonical_product_id": None,
                },
            }

        product = product_by_id[COMBINED_IDS[ring_id]]
        seller = seller_by_id[product["seller"]]
        primary = sources[product["source"]]
        facts = product["facts"]
        price = product.get("price")
        amount_quotes = []
        currency_quotes = []
        currency_url = None
        if price:
            for reference in price.get("evidence") or []:
                source = sources[reference["source"]]
                quote = source["quotes"][reference["quote"]]
                if quote_has_number(quote, price.get("amount")):
                    amount_quotes.append(quote)
                if USD_RE.search(quote):
                    currency_quotes.append(quote)
                    currency_url = source["url"]
        price_supported = bool(
            price
            and price.get("currency") == "USD"
            and positive_number(price.get("amount"))
            and amount_quotes
            and currency_quotes
        )
        weight = None
        weight_quotes = []
        weight_url = None
        net = facts.get("netMetalWeightG")
        if net:
            source = sources[net["source"]]
            quote = source["quotes"][net["quote"]]
            if positive_number(net.get("value")) and quote_has_number(quote, net["value"]) and GRAM_RE.search(quote):
                weight = net["value"]
                weight_quotes = [quote]
                weight_url = source["url"]
        elif product.get("reportedWeight"):
            reported = product["reportedWeight"]
            source = sources[reported["evidence"]["source"]]
            quote = source["quotes"][reported["evidence"]["quote"]]
            if (
                reported.get("basis") == "seller-metal"
                and reported.get("min") == reported.get("max")
                and positive_number(reported.get("min"))
                and quote_has_number(quote, reported["min"])
                and GRAM_RE.search(quote)
            ):
                weight = reported["min"]
                weight_quotes = [quote]
                weight_url = source["url"]
        solid = facts["solidGold"]["value"] if facts.get("solidGold") else None
        hallmark = facts["hallmark"]["value"] if facts.get("hallmark") else None
        review_flags = [finding["id"] for finding in findings if product["source"] in (finding.get("sources") or [])]
        return {
            "canonical": product,
            "seller": seller,
            "domains": set(seller.get("domains") or []) or {host(primary["url"])},
            "expected": {
                "id": ring_id,
                "retailer_id": product["seller"],
                "retailer": seller["name"],
                "categories": list(categories),
                "name": product["name"]["value"],
                "karat": facts["karat"]["value"],
                "solid_gold_explicit": solid if isinstance(solid, bool) else None,
                "hallmark_stated": hallmark if isinstance(hallmark, bool) else None,
                "weight_g": weight,
                "price_usd": price["amount"] if price_supported else None,
                "unassigned_display": None,
                "capture_date": product["observedAt"][:10],
                "product_url": primary["url"],
                "quote": primary["quotes"][product["name"]["quote"]],
                "price_quotes": amount_quotes if price_supported else [],
                "currency_quotes": currency_quotes if price_supported else [],
                "currency_source_url": currency_url if price_supported else None,
                "weight_quotes": weight_quotes,
                "weight_source_url": weight_url,
                "evidence_link": f"../explore/sources/#{product['source']}",
                "verification_status": "canonical_combined_record",
                "canonical_flags": [],
                "review_flags": review_flags,
                "canonical_product_id": product["id"],
            },
        }

    expected_rings = {ring_id: expected_ring(ring_id) for ring_id, _ in RING_METADATA}

    def p1() -> None:
        for ring in rings:
            expected = expected_rings.get(ring["id"])
            if not is_official(ring.get("product_url")):
                failures.append(f"P1 non-allowlisted ring URL: {ring['id']}")
            elif expected and host(ring["product_url"]) not in expected["domains"]:
                failures.append(f"P1 seller/product host mismatch: {ring['id']} -> {host(ring['product_url'])}")
            for field in ("currency_source_url", "weight_source_url"):
                url = ring.get(field)
                if url is not None and (not is_official(url) or expected and host(url) not in expected["domains"]):
                    failures.append(f"P1 bad {field}: {ring['id']} -> {url}")
        for retailer in retailers:
            root_id = next((root for dash, root, _ in RETAILER_METADATA if dash == retailer["id"]), None)
            combined_id = next((combined for dash, _, combined in RETAILER_METADATA if dash == retailer["id"]), None)
            canonical_seller = root_retailers.get(root_id) or seller_by_id.get(combined_id) or {}
            domains = set(canonical_seller.get("domains") or [])
            if not domains and combined_id:
                for product in catalog["products"]:
                    if product["seller"] == combined_id:
                        domains.add(host(sources[product["source"]]["url"]))
                for field in ("policy", "contact"):
                    source_id = canonical_seller.get(field)
                    if source_id:
                        domains.add(host(sources[source_id]["url"]))
            for field in ("site_url", "contact_url", "returns_url", "jewelry_notes_url"):
                url = retailer.get(field)
                if not is_official(url) or host(url) not in domains:
                    failures.append(f"P1 seller host mismatch: {retailer['id']}.{field} -> {url}")
            if retailer.get("bbb_url") is not None and not is_official(retailer["bbb_url"]):
                failures.append(f"P1 non-allowlisted reputation URL: {retailer['id']}")
        if not is_official(ref.get("spot_source_url")) or host(ref.get("spot_source_url")) not in {"gold.org", "www.gold.org"}:
            failures.append("P1 bad gold-reference URL")

    def p2() -> None:
        for ring in rings:
            if not valid_date(ring.get("capture_date")):
                failures.append(f"P2 invalid observation date: {ring['id']}")
            price = ring.get("price_usd")
            note = ring.get("price_note")
            if not isinstance(note, str) or not note.strip():
                failures.append(f"P2 missing price note: {ring['id']}")
            if price is None:
                if "DF-011" not in ring.get("flags", []):
                    failures.append(f"P2 unflagged null price: {ring['id']}")
                if ring.get("price_quotes") or ring.get("currency_quotes") or ring.get("currency_source_url") is not None:
                    failures.append(f"P2 null price retains assigned-price evidence: {ring['id']}")
                if ring.get("unassigned_display") is not None and not isinstance(ring.get("unassigned_display"), str):
                    failures.append(f"P2 invalid unassigned display: {ring['id']}")
                continue
            if not positive_number(price):
                failures.append(f"P2 invalid assigned price: {ring['id']}")
                continue
            amount_quotes = ring.get("price_quotes") or []
            currency_quotes = ring.get("currency_quotes") or []
            if not amount_quotes or not any(quote_has_number(quote, price) for quote in amount_quotes):
                failures.append(f"P2 price lacks exact amount evidence: {ring['id']}")
            if not currency_quotes or not any(USD_RE.search(quote) for quote in currency_quotes):
                failures.append(f"P2 price lacks explicit USD evidence: {ring['id']}")
            if not is_official(ring.get("currency_source_url")):
                failures.append(f"P2 price lacks official currency source: {ring['id']}")
            formatted = f"${price:,.2f}"
            if formatted not in note or "USD" not in note or ring["capture_date"] not in note or "Not a live checkout total" not in note:
                failures.append(f"P2 price note is not dated/scoped: {ring['id']}")

    def p3() -> None:
        for ring in rings:
            weight = ring.get("weight_g")
            if weight is None:
                if "DF-003" not in ring.get("flags", []) or "Blank" not in ring.get("weight_note", ""):
                    failures.append(f"P3 unflagged/unlabelled null weight: {ring['id']}")
                if ring.get("weight_quotes") or ring.get("weight_source_url") is not None:
                    failures.append(f"P3 null weight retains assigned-weight evidence: {ring['id']}")
            else:
                if not positive_number(weight):
                    failures.append(f"P3 invalid weight: {ring['id']}")
                if not any(quote_has_number(quote, weight) and GRAM_RE.search(quote) for quote in ring.get("weight_quotes") or []):
                    failures.append(f"P3 weight lacks exact gram evidence: {ring['id']}")
                if not is_official(ring.get("weight_source_url")):
                    failures.append(f"P3 weight lacks official source: {ring['id']}")
                if "Not independently weighed" not in ring.get("weight_note", ""):
                    failures.append(f"P3 seller weight lacks measurement limitation: {ring['id']}")
            if ring.get("solid_gold_explicit") is not True and "DF-010" not in ring.get("flags", []):
                failures.append(f"P3 unflagged nonqualifying solid-gold wording: {ring['id']}")
            if "DF-007" not in ring.get("flags", []):
                failures.append(f"P3 physical-test limitation not linked: {ring['id']}")
            for field in ("solid_gold_explicit", "hallmark_stated"):
                if ring.get(field) is not None and not isinstance(ring.get(field), bool):
                    failures.append(f"P3 invalid {field}: {ring['id']}")

    def p4() -> None:
        expected_ids = [ring_id for ring_id, _ in RING_METADATA]
        if [ring["id"] for ring in rings] != expected_ids or len(ring_by_id) != len(rings):
            failures.append("P4 companion ring IDs/order/duplicates differ from editorial canonical mapping")
        expected_retailers = [dash for dash, _, _ in RETAILER_METADATA]
        if [retailer["id"] for retailer in retailers] != expected_retailers or len(retailer_by_id) != len(retailers):
            failures.append("P4 retailer IDs/order/duplicates differ from canonical mapping")
        if len(flag_ids) != len(flags):
            failures.append("P4 duplicate companion flag IDs")
        for ring in rings:
            if ring.get("retailer_id") not in retailer_by_id:
                failures.append(f"P4 unknown retailer on {ring['id']}")
            if any(flag_id not in flag_ids for flag_id in ring.get("flags", [])):
                failures.append(f"P4 unknown companion flag on {ring['id']}")
            if any(flag_id not in canonical_flag_ids for flag_id in ring.get("canonical_flags", [])):
                failures.append(f"P4 unknown canonical flag on {ring['id']}")
            finding_ids = {finding["id"] for finding in findings}
            if any(flag_id not in finding_ids for flag_id in ring.get("review_flags", [])):
                failures.append(f"P4 unknown combined finding on {ring['id']}")
        for flag in flags:
            if flag.get("severity") not in {"low", "medium", "high"} or not flag.get("sources"):
                failures.append(f"P4 invalid flag definition: {flag.get('id')}")
            for url in flag.get("sources", []):
                if not is_official(url):
                    failures.append(f"P4 non-allowlisted flag source: {flag.get('id')} -> {url}")

    def expected_retailer(dashboard_id: str) -> tuple[dict, dict]:
        _, root_id, combined_id = next(item for item in RETAILER_METADATA if item[0] == dashboard_id)
        if root_id and root_id in root_retailers:
            retailer = root_retailers[root_id]
            reputation = retailer["independent_reputation"]
            exclusions = retailer.get("return_exclusions_detail")
            if retailer.get("resize_policy"):
                exclusions = (exclusions + " " if exclusions else "") + retailer["resize_policy"]
            expected = {
                "name": retailer["name"],
                "site_url": retailer["website"],
                "contact_url": retailer["contact_source_url"],
                "returns_url": retailer["return_policy_url"],
                "bbb_url": reputation.get("profile_url") or reputation.get("candidate_profile_url"),
                "return_window": retailer.get("return_window_basis"),
                "resized_custom_rule": exclusions,
                "payment_protection": retailer.get("payment_note") if retailer.get("payment_methods_verified") else None,
                "evidence_link": "../" + retailer["evidence_file"],
                "reputation_evidence_link": "../" + retailer["evidence_file"],
                "capture_date": reputation.get("retrieved_at"),
            }
            return retailer, expected
        seller = seller_by_id[combined_id]
        policy = sources.get(seller.get("policy")) if seller.get("policy") else None
        contact = sources.get(seller.get("contact")) if seller.get("contact") else None
        independent = sources.get(seller.get("independent")) if seller.get("independent") else None
        origin = policy or contact or independent
        if origin is None:
            product = next(product for product in catalog["products"] if product["seller"] == seller["id"])
            origin = sources[product["source"]]
        parsed = urlparse(origin["url"])
        return_days = seller.get("returnDays")
        related = [source for source in (policy, contact, independent) if source]
        expected = {
            "name": seller["name"],
            "site_url": f"{parsed.scheme}://{parsed.netloc}/",
            "contact_url": (contact or policy or origin)["url"],
            "returns_url": (policy or contact or origin)["url"],
            "bbb_url": independent["url"] if independent else None,
            "return_window": f"{return_days['value']} days from {seller.get('returnFrom') or 'unconfirmed trigger'}" if return_days else None,
            "resized_custom_rule": seller.get("summary"),
            "payment_protection": None,
            "evidence_link": f"../explore/sources/#{origin['id']}",
            "reputation_evidence_link": f"../explore/sources/#{independent['id']}" if independent else None,
            "capture_date": max((source["observedAt"][:10] for source in related), default=None),
        }
        return seller, expected

    def p5() -> None:
        required = {
            "id", "name", "site_url", "contact_url", "returns_url", "jewelry_notes_url", "bbb_url",
            "contact_summary", "return_window", "resized_custom_rule", "payment_protection", "bbb_summary",
            "unverified_fields", "evidence_link", "evidence_label", "reputation_evidence_link", "capture_date",
        }
        for retailer in retailers:
            if not required.issubset(retailer):
                failures.append(f"P5 missing retailer keys: {retailer['id']}")
                continue
            _, expected = expected_retailer(retailer["id"])
            for field, value in expected.items():
                if retailer.get(field) != value:
                    failures.append(f"P5 canonical seller mismatch: {retailer['id']}.{field}")
            reputation_pointer = retailer.get("reputation_evidence_link")
            if retailer.get("bbb_url") and not reputation_pointer:
                failures.append(f"P5 confirmed reputation record lacks an internal evidence pointer: {retailer['id']}")
            if reputation_pointer is not None and (urlparse(reputation_pointer).scheme or not reputation_pointer.startswith("../")):
                failures.append(f"P5 invalid internal reputation evidence pointer: {retailer['id']}")
            if not isinstance(retailer["unverified_fields"], list) or not all(isinstance(item, str) and item for item in retailer["unverified_fields"]):
                failures.append(f"P5 invalid unverified-fields list: {retailer['id']}")
            blank_markers = {
                "return_window": "return window",
                "resized_custom_rule": "exclusion",
                "payment_protection": "payment",
                "contact_summary": "contact",
                "bbb_summary": "reputation",
            }
            for field, marker in blank_markers.items():
                if retailer.get(field) is None and not any(marker in item for item in retailer["unverified_fields"]):
                    failures.append(f"P5 blank {field} not flagged: {retailer['id']}")
            if retailer.get("capture_date") is not None and not valid_date(retailer["capture_date"]):
                failures.append(f"P5 invalid seller observation date: {retailer['id']}")
            for value in retailer.values():
                if isinstance(value, str) and re.search(r"\bNone\b", value):
                    failures.append(f"P5 stringified null in seller output: {retailer['id']}")
            root_id = next(root for dash, root, _ in RETAILER_METADATA if dash == retailer["id"])
            if root_id and root_id in root_retailers:
                reputation = root_retailers[root_id]["independent_reputation"]
                summary = retailer.get("bbb_summary") or ""
                rating = reputation.get("bbb_rating")
                if rating is None and re.search(r"BBB rating\s+\S", summary):
                    failures.append(f"P5 invented BBB rating: {retailer['id']}")
                if rating is not None and f"BBB rating {rating}" not in summary:
                    failures.append(f"P5 BBB rating mismatch: {retailer['id']}")
                if reputation.get("identity_status") == "candidate_name_match_not_confirmed":
                    if "identity unconfirmed" not in summary or not any("reputation identity" in item for item in retailer["unverified_fields"]):
                        failures.append(f"P5 candidate profile not flagged: {retailer['id']}")
                average = reputation.get("review_average_out_of_5")
                count = reputation.get("review_count")
                if average is not None and count is not None and f"{average:g}/5 across {count} reviews" not in summary:
                    failures.append(f"P5 review metrics mismatch: {retailer['id']}")

    def p8() -> None:
        for ring in rings:
            marker = f"## {ring['id']} —"
            if marker not in rings_ev:
                failures.append(f"P8 missing ring evidence section: {ring['id']}")
                continue
            section = rings_ev.split(marker, 1)[1].split("\n## ", 1)[0]
            for quote in [ring["quote"], *(ring.get("price_quotes") or []), *(ring.get("currency_quotes") or []), *(ring.get("weight_quotes") or [])]:
                if quote not in section:
                    failures.append(f"P8 quote absent from own ring section: {ring['id']}")
            for text in (ring["product_url"], ring["evidence_link"]):
                if text not in section:
                    failures.append(f"P8 evidence pointer absent: {ring['id']}")
        for retailer in retailers:
            marker = f"## {retailer['id']} —"
            if marker not in ret_ev:
                failures.append(f"P8 missing seller evidence section: {retailer['id']}")
                continue
            section = ret_ev.split(marker, 1)[1].split("\n## ", 1)[0]
            for field in ("site_url", "returns_url", "evidence_link"):
                if retailer[field] not in section:
                    failures.append(f"P8 seller pointer absent: {retailer['id']}.{field}")
            if retailer.get("reputation_evidence_link") and retailer["reputation_evidence_link"] not in section:
                failures.append(f"P8 reputation evidence pointer absent: {retailer['id']}")
            if "; ".join(retailer["unverified_fields"]) not in section:
                failures.append(f"P8 seller limitations absent: {retailer['id']}")

    def p9() -> None:
        for ring in rings:
            expected = expected_rings.get(ring["id"], {}).get("expected")
            if expected is None:
                failures.append(f"P9 no canonical product mapping: {ring['id']}")
                continue
            for field, value in expected.items():
                if ring.get(field) != value:
                    failures.append(f"P9 canonical product mismatch: {ring['id']}.{field}: {ring.get(field)!r} != {value!r}")

    def p10() -> None:
        if ref.get("retrieved_at") != gold["retrieved_at"] or ref.get("spot_usd_per_troy_oz") != gold["usd_per_troy_oz"]:
            failures.append("P10 gold reference differs from canonical observation")
        if ref.get("chart_as_of_date") != gold.get("chart_as_of_date"):
            failures.append("P10 chart date differs from canonical observation")
        if ref.get("quote_timestamp_confirmed") is not (gold.get("quote_date") is not None):
            failures.append("P10 quote-time confirmation status mismatch")
        if ref.get("spot_quotes") != list(gold["evidence_quotes"]):
            failures.append("P10 gold evidence quotes mismatch")
        troy = Decimal(str(gold["grams_per_troy_ounce"]))
        spot = Decimal(str(gold["usd_per_troy_oz"]))
        expected_per_gram = round(gold["usd_per_troy_oz"] / gold["grams_per_troy_ounce"], 6)
        if ref.get("usd_per_fine_gram") != expected_per_gram or Decimal(str(ref["troy_ounce"]["grams"])) != troy:
            failures.append("P10 gold conversion mismatch")
        for ring in rings:
            if ring.get("weight_g") is None:
                continue
            fine = Decimal(str(ring["weight_g"])) * Decimal(ring["karat"]) / Decimal(24)
            nominal = fine * spot / troy
            if not math.isfinite(float(nominal)) or nominal <= 0:
                failures.append(f"P10 invalid nominal arithmetic: {ring['id']}")
            if ring.get("price_usd") is not None and Decimal(str(ring["price_usd"])) / nominal <= 0:
                failures.append(f"P10 invalid price/reference ratio: {ring['id']}")
        calculator = (ROOT / "assets/calculator.js").read_text(encoding="utf-8")
        for source in (calculator, (ROOT / "scripts/build.py").read_text(encoding="utf-8")):
            if "high counterfeit/plating risk" in source or "<1.0× signals counterfeit" in source:
                failures.append("P10 overconfident below-reference authenticity language")
        for constant in ("31.1034768", "1.55517384", "0.2"):
            if constant not in calculator:
                failures.append(f"P10 missing calculator constant {constant}")

    run_pass("P1-sources-and-seller-hosts", p1)
    run_pass("P2-strict-price-currency-evidence", p2)
    run_pass("P3-blanks-weight-and-qualification", p3)
    run_pass("P4-cross-refs", p4)
    run_pass("P5-canonical-retailers", p5)
    run_pass("P8-evidence-quotes", p8)
    run_pass("P9-canonical-product-parity", p9)
    run_pass("P10-gold-and-arithmetic", p10)

    parsed_map: dict[Path, LinkAndRowParser] = {}
    if check_build:
        html_pages = sorted(ROOT.glob("*.html"))

        def parse_page(path: Path) -> LinkAndRowParser:
            if path not in parsed_map:
                parser = LinkAndRowParser()
                parser.feed(path.read_text(encoding="utf-8"))
                parsed_map[path] = parser
            return parsed_map[path]

        def p6() -> None:
            if len(html_pages) != 14:
                failures.append(f"P6 expected 14 HTML pages, found {len(html_pages)}")
            required_csp = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
            for path in html_pages:
                parser = parse_page(path)
                if "undefined" in path.read_text(encoding="utf-8").lower():
                    failures.append(f"P6 unrendered/ambiguous undefined token: {path.name}")
                if not parser.has_csp or parser.csp != required_csp:
                    failures.append(f"P6 missing/incorrect CSP: {path.name}")
                if parser.event_attributes or parser.inline_scripts:
                    failures.append(f"P6 inline script/event handler: {path.name}")
                if len(parser.ids) != len(set(parser.ids)):
                    failures.append(f"P6 duplicate HTML IDs: {path.name}")
                for row in parser.rows:
                    if row["cells"] and not any(is_primary_or_standard(url) for url in row["links"]):
                        failures.append(f"P6 table row without official/standards source: {path.name} {row.get('id')}")
                for src in parser.script_sources:
                    if urlparse(src).scheme:
                        failures.append(f"P6 external script source: {path.name} -> {src}")
            all_rings = parse_page(ROOT / "rings.html")
            rendered = [row for row in all_rings.rows if (row.get("id") or "").startswith("ring-")]
            if len(rendered) != len(rings):
                failures.append(f"P6 rings.html row count {len(rendered)} != {len(rings)}")
            for path in html_pages:
                for row in parse_page(path).rows:
                    row_id = row.get("id") or ""
                    if not row_id.startswith("ring-"):
                        continue
                    ring_id = next((candidate for candidate in ring_by_id if row_id == f"ring-{candidate.lower()}"), None)
                    if ring_id is None:
                        failures.append(f"P6 unknown rendered ring row: {path.name} {row_id}")
                        continue
                    ring = ring_by_id[ring_id]
                    if len(row["cells"]) != 6:
                        failures.append(f"P6 malformed ring row: {path.name} {ring_id}")
                        continue
                    attrs = row["attrs"]
                    if attrs.get("data-karat") != str(ring["karat"]):
                        failures.append(f"P6 rendered karat mismatch: {ring_id}")
                    if attrs.get("data-solid") != ("yes" if ring["solid_gold_explicit"] is True else "no"):
                        failures.append(f"P6 rendered solid-gold status mismatch: {ring_id}")
                    if attrs.get("data-has-weight") != ("yes" if ring["weight_g"] is not None else "no"):
                        failures.append(f"P6 rendered weight status mismatch: {ring_id}")
                    if ring["product_url"] not in row["links"] or ring["evidence_link"] not in row["links"]:
                        failures.append(f"P6 rendered source/evidence missing: {ring_id}")
                    weight_text, price_text, metric_text = row["cells"][2], row["cells"][3], row["cells"][4]
                    if ring["weight_g"] is None:
                        if "— (blank)" not in weight_text:
                            failures.append(f"P6 blank weight not rendered: {ring_id}")
                    elif f"{ring['weight_g']:.2f} g" not in weight_text:
                        failures.append(f"P6 weight mismatch in HTML: {ring_id}")
                    if ring["price_usd"] is None:
                        if "— (blank)" not in price_text or re.search(r"\$\s*[\d,]+(?:\.\d+)?\s+USD", price_text):
                            failures.append(f"P6 null price rendered as assigned: {ring_id}")
                    elif f"${ring['price_usd']:,.2f} USD" not in price_text:
                        failures.append(f"P6 price mismatch in HTML: {ring_id}")
                    if ring["weight_g"] is not None:
                        fine = Decimal(str(ring["weight_g"])) * Decimal(ring["karat"]) / Decimal(24)
                        nominal = fine * Decimal(str(ref["spot_usd_per_troy_oz"])) / Decimal(str(ref["troy_ounce"]["grams"]))
                        if f"{fine:.3f} g" not in metric_text or f"${nominal:,.2f}" not in metric_text:
                            failures.append(f"P6 nominal arithmetic mismatch in HTML: {ring_id}")
            calculator = (ROOT / "calculator.html").read_text(encoding="utf-8")
            if 'id="calc-weight" type="number" min="0.01" step="0.01" value=""' not in calculator or 'id="calc-ask" type="number" min="0" step="0.01" value=""' not in calculator:
                failures.append("P6 calculator contains an unsourced default weight/price")
            if f'id="calc-spot" type="number" min="1" step="0.01" value="{ref["spot_usd_per_troy_oz"]:.2f}"' not in calculator:
                failures.append("P6 calculator gold reference is stale")
            for path in (ROOT / "assets").glob("*.js"):
                source = path.read_text(encoding="utf-8")
                if re.search(r"\b(?:innerHTML|outerHTML)\s*=|\beval\s*\(|\bnew\s+Function\b|\bdocument\s*\.\s*write\s*\(|\binsertAdjacentHTML\s*\(", source):
                    failures.append(f"P6 dangerous script sink: {path.name}")

        def p7() -> None:
            for path in html_pages:
                parser = parse_page(path)
                for href in parser.hrefs + parser.script_sources:
                    parsed = urlparse(href)
                    if parsed.scheme in ("https", "mailto", "tel"):
                        if parsed.scheme == "https" and not is_official(href):
                            failures.append(f"P7 non-allowlisted external link: {path.name} -> {href}")
                        continue
                    if parsed.scheme:
                        failures.append(f"P7 unsafe scheme: {path.name} -> {href}")
                        continue
                    clean_path = unquote(parsed.path)
                    target = (path.parent / clean_path).resolve() if clean_path else path.resolve()
                    try:
                        target.relative_to(REPO_ROOT)
                    except ValueError:
                        failures.append(f"P7 link escapes repository: {path.name} -> {href}")
                        continue
                    if target.is_dir():
                        target = target / "index.html"
                    if not target.is_file():
                        failures.append(f"P7 broken internal link: {path.name} -> {href}")
                        continue
                    if parsed.fragment and target.suffix == ".html":
                        target_parser = parse_page(target)
                        if parsed.fragment not in target_parser.ids:
                            failures.append(f"P7 broken fragment: {path.name} -> {href}")

        run_pass("P6-rendered-data-security-sync", p6)
        run_pass("P7-link-integrity", p7)

    observations = [ring["capture_date"] for ring in rings if valid_date(ring.get("capture_date"))]
    if valid_date(ref.get("retrieved_at")):
        observations.append(ref["retrieved_at"])
    log_doc = {
        "canonical_observations_through": max(observations) if observations else None,
        "verification_scope": "companion offline canonical parity, generated HTML, links, security invariants, and nominal arithmetic",
        "network_fetch_performed": False,
        "physical_authentication": "not_tested",
        "spot_usd_per_troy_oz": ref["spot_usd_per_troy_oz"],
        "counts": {
            "html_pages": len(list(ROOT.glob("*.html"))),
            "rings": len(rings),
            "retailers": len(retailers),
            "flags": len(flags),
        },
        "passes": passes,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "limitations": "PASS is not source freshness, physical purity, or proof that all hallucinations are absent.",
        "recommendation": "Look for hallucinations again after every review; rerun repository-wide verification and security scans.",
    }
    LOG_PATH.write_text(json.dumps(log_doc, indent=2) + "\n", encoding="utf-8")
    print(f"dashboard verify: {log_doc['status']} — passes={passes}")
    for failure in failures:
        print("  FAIL:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
