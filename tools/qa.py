#!/usr/bin/env python3
"""Field-scoped hallucination, consistency, security, and built-link audit.

Run after every review/build:
    python3 tools/build_site.py
    python3 tools/qa.py
    node tools/test_calculator.js

PASS means internal records and generated pages are consistent with their stored
field evidence. It does not prove a seller's physical claims or guarantee that
an external page remains available.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT
REPORTS = ROOT / "reports"
PAGE_NAMES = [
    "index.html", "solitaire.html", "halo-pave.html", "three-stone-vintage.html",
    "18k.html", "budget.html", "retailers.html", "prices.html", "flags.html", "methods.html",
]
CATEGORY_PAGES = ["solitaire.html", "halo-pave.html", "three-stone-vintage.html", "18k.html", "budget.html"]
LISTING_FILES = ["solitaire.json", "halo-pave.json", "three-stone-vintage.json", "18k.json", "budget.json"]

issues: list[tuple[str, str]] = []
checks: list[tuple[str, str, int]] = []


def fail(check: str, message: str) -> None:
    issues.append(("FAIL", f"[{check}] {message}"))


def warn(check: str, message: str) -> None:
    issues.append(("WARN", f"[{check}] {message}"))


def record(name: str, before: int) -> None:
    failures = [issue for issue in issues[before:] if issue[0] == "FAIL"]
    checks.append((name, "FAIL" if failures else "PASS", len(failures)))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    for char in "\u200b\u200c\u200d\ufeff\u00a0":
        text = text.replace(char, " " if char == "\u00a0" else "")
    return re.sub(r"\s+", " ", text).strip().lower()


def digits(text: str) -> str:
    return re.sub(r"\D", "", text)


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_date(value: str, label: str) -> None:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
        if parsed > date.today():
            fail("dates", f"{label} is in the future: {value}")
    except (ValueError, TypeError) as exc:
        fail("dates", f"{label} is not YYYY-MM-DD: {value!r} ({exc})")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.scripts: list[dict] = []
        self.metas: list[dict] = []
        self.tags: list[str] = []
        self.event_attributes: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.hrefs.append(attributes["href"])
        if tag == "script":
            self.scripts.append(attributes)
        if tag == "meta":
            self.metas.append(attributes)
        for name in attributes:
            if name.lower().startswith("on"):
                self.event_attributes.append(name)


def main() -> int:
    if not DATA.exists():
        print("no data directory")
        return 1

    gold = load(DATA / "gold-price.json")
    retailers = load(DATA / "retailers.json")["retailers"]
    flags = load(DATA / "flags.json")["flags"]
    items = []
    for filename in LISTING_FILES:
        payload = load(DATA / "listings" / filename)
        for item in payload["items"]:
            item["_file"] = filename
            item["_category"] = payload["category_id"]
            items.append(item)
    by_item = {item["id"]: item for item in items}
    by_retailer = {retailer["id"]: retailer for retailer in retailers}
    by_flag = {flag["id"]: flag for flag in flags}

    evidence_cache: dict[str, str] = {}

    def evidence_text(relative: str) -> str:
        if relative not in evidence_cache:
            path = ROOT / relative
            if not path.is_file():
                fail("evidence", f"missing evidence file {relative}")
                evidence_cache[relative] = ""
            else:
                evidence_cache[relative] = norm(path.read_text(encoding="utf-8"))
        return evidence_cache[relative]

    # 1 — schema, identifiers, dates, and basic types.
    before = len(issues)
    required_item_keys = {
        "id", "retailer_id", "retailer", "brand", "name", "sku", "sku_basis", "metal", "karat",
        "color", "width_mm", "depth_mm", "weight_g", "price", "currency", "price_basis",
        "center_stone_included", "original_price", "source_url", "retrieved_at", "evidence_file",
        "field_evidence", "solid_gold_explicit", "hallmark_stated", "makers_mark_stated",
        "return_policy_url", "verification_status", "rejected_values", "flags",
        "physical_test_status", "independent_test_permission", "unassigned_price_text",
    }
    for item in items:
        missing = sorted(required_item_keys - set(item))
        if missing:
            fail("schema", f"{item.get('id', '?')} missing keys: {missing}")
        for key in ("id", "retailer_id", "retailer", "name", "sku", "metal", "source_url", "retrieved_at", "evidence_file"):
            if not item.get(key):
                fail("schema", f"{item.get('id', '?')} has empty required {key}")
        if not isinstance(item.get("karat"), int) or not 1 <= item.get("karat", 0) <= 24:
            fail("schema", f"{item.get('id', '?')} invalid karat")
        for key in ("price", "original_price", "weight_g", "width_mm", "depth_mm"):
            value = item.get(key)
            if value is not None and (not is_number(value) or value <= 0):
                fail("schema", f"{item['id']} invalid {key}: {value!r}")
        if item.get("price_basis") not in ("setting_price", "complete_ring"):
            fail("schema", f"{item['id']} invalid price_basis")
        if not isinstance(item.get("center_stone_included"), bool):
            fail("schema", f"{item['id']} center_stone_included must be boolean")
        if item.get("physical_test_status") != "not_tested":
            fail("schema", f"{item['id']} unexpected physical_test_status")
        parse_date(item["retrieved_at"], f"{item['id']} retrieved_at")
        expected_evidence = f"evidence/listings/{item['id'].lower()}.md"
        if item["evidence_file"] != expected_evidence:
            fail("schema", f"{item['id']} evidence is not item-scoped: {item['evidence_file']}")
    ids = [item["id"] for item in items]
    if len(items) < 16:
        fail("schema", f"only {len(items)} inherited listings remain; expected at least 16")
    if len(ids) != len(set(ids)):
        fail("ids", "duplicate item id")
    if len({item["source_url"] for item in items}) != len(items):
        fail("ids", "duplicate item source_url")
    if len({item["evidence_file"] for item in items}) != len(items):
        fail("ids", "items share an evidence file")
    if len(by_retailer) != len(retailers):
        fail("ids", "duplicate retailer id")
    if len(by_flag) != len(flags):
        fail("ids", "duplicate flag id")
    for item in items:
        retailer = by_retailer.get(item["retailer_id"])
        if retailer and item["retailer"] != retailer["name"]:
            fail("schema", f"{item['id']} retailer label does not match registry")
    for key in ("retrieved_at", "usd_per_troy_oz", "source_url", "evidence_file", "grams_per_troy_ounce", "field_evidence"):
        if not gold.get(key):
            fail("gold", f"gold-price.json missing {key}")
    if not is_number(gold.get("usd_per_troy_oz")) or gold["usd_per_troy_oz"] <= 0:
        fail("gold", "spot quote must be positive")
    if not is_number(gold.get("grams_per_troy_ounce")) or gold["grams_per_troy_ounce"] <= 0:
        fail("gold", "grams_per_troy_ounce must be positive")
    if gold.get("quote_date"):
        parse_date(gold["quote_date"], "gold quote_date")
    elif "F-026" not in by_flag:
        fail("gold", "Unconfirmed header quote time requires F-026")
    else:
        warn("gold", "Header quote-as-of is unconfirmed; chart/retrieval dates are not substituted (F-026)")
    parse_date(gold["retrieved_at"], "gold retrieved_at")
    if gold.get("quote_date") and gold["quote_date"] > gold["retrieved_at"]:
        fail("gold", "quote_date is after retrieved_at")
    record("JSON schema, item-scoped records, unique IDs, and dates", before)

    # 2 — every field-specific quote exists in its own evidence file.
    before = len(issues)
    quote_count = 0
    subjects = [("item", item) for item in items] + [("retailer", retailer) for retailer in retailers] + [("gold", gold)]
    for kind, subject in subjects:
        relative = subject.get("evidence_file")
        if not relative:
            fail("evidence", f"{kind} {subject.get('id', '?')} has no evidence_file")
            continue
        text = evidence_text(relative)
        field_evidence = subject.get("field_evidence")
        if not isinstance(field_evidence, dict) or not field_evidence:
            fail("evidence", f"{kind} {subject.get('id', '?')} has no field_evidence")
            continue
        for field, quotes in field_evidence.items():
            if not isinstance(quotes, list) or not quotes:
                fail("evidence", f"{subject.get('id')} {field} has no quotes")
                continue
            for quote in quotes:
                quote_count += 1
                if not isinstance(quote, str) or not quote.strip():
                    fail("evidence", f"{subject.get('id')} {field} has an empty quote")
                elif norm(quote) not in text:
                    fail("evidence", f"{subject.get('id')} {field}: quote absent from {relative}: {quote!r}")
    record(f"Field-scoped verbatim quotes resolve in their own files ({quote_count} quotes)", before)

    # 3 — every published item field has evidence and the quote carries its value.
    before = len(issues)
    published_fields = [
        "name", "sku", "metal", "karat", "color", "width_mm", "band_width_text", "depth_mm",
        "weight_g", "weight_basis", "price", "original_price", "currency", "price_basis",
        "center_stone_included", "unassigned_price_text", "prong_metal", "surface_finish",
    ]

    def combined_quotes(subject, field):
        return norm(" ".join(subject.get("field_evidence", {}).get(field, [])))

    def numeric_candidates(value, comma=False):
        candidates = {f"{value:g}", f"{value:.1f}", f"{value:.2f}"}
        if comma:
            candidates |= {f"{value:,.2f}", f"{value:,.0f}"}
        return {norm(candidate) for candidate in candidates}

    def quote_has_number(value, text, comma=False):
        compact = text.replace(" ", "")
        return any(candidate in text or candidate in compact for candidate in numeric_candidates(value, comma))

    for item in items:
        for field in published_fields:
            value = item.get(field)
            if value is not None and not item.get("field_evidence", {}).get(field):
                fail("field-backing", f"{item['id']} non-null {field} has no field-specific evidence")
        for field in ("name", "sku", "metal", "band_width_text", "weight_basis", "unassigned_price_text", "prong_metal", "surface_finish"):
            value = item.get(field)
            if value is not None:
                text = combined_quotes(item, field)
                if norm(str(value)) not in text:
                    fail("field-backing", f"{item['id']} {field} value is not present in its own field quotes")
        if item.get("color") is not None and norm(item["color"]) not in combined_quotes(item, "color"):
            fail("field-backing", f"{item['id']} colour is absent from colour evidence")
        if item.get("karat") is not None and f"{item['karat']}k" not in combined_quotes(item, "karat").replace(" ", ""):
            fail("field-backing", f"{item['id']} karat is absent from karat evidence")
        for field in ("width_mm", "depth_mm", "weight_g"):
            value = item.get(field)
            if value is not None:
                text = combined_quotes(item, field)
                unit = "g" if field == "weight_g" else "mm"
                if not quote_has_number(value, text) or unit not in text:
                    fail("field-backing", f"{item['id']} {field} lacks matching numeric/unit evidence")
        for field in ("price", "original_price"):
            value = item.get(field)
            if value is not None:
                text = combined_quotes(item, field)
                symbol = {"USD": "$", "EUR": "€"}.get(item.get("currency"))
                if not symbol or symbol not in text or not quote_has_number(value, text, comma=True):
                    fail("field-backing", f"{item['id']} {field} lacks matching amount/currency evidence")
        if item.get("currency") is not None:
            text = combined_quotes(item, "currency")
            symbol = {"USD": "$", "EUR": "€"}.get(item["currency"])
            if not symbol or symbol not in text:
                fail("field-backing", f"{item['id']} currency symbol missing from currency evidence")
        basis_text = combined_quotes(item, "price_basis")
        if item["price_basis"] == "setting_price" and "setting" not in basis_text:
            fail("field-backing", f"{item['id']} setting basis lacks setting wording")
        if item["price_basis"] == "complete_ring" and not ("diamond" in basis_text and "ring" in basis_text):
            fail("field-backing", f"{item['id']} complete-ring basis lacks diamond-ring title evidence")
        scope_text = combined_quotes(item, "center_stone_included")
        if item["center_stone_included"] is False and "setting" not in scope_text:
            fail("field-backing", f"{item['id']} centre-stone exclusion lacks setting evidence")
        if item["center_stone_included"] is True and not ("diamond" in scope_text and "ring" in scope_text):
            fail("field-backing", f"{item['id']} listed-diamond scope lacks title evidence")
    record("Item name, SKU, metal, dimensions, price, basis, and scope match field quotes", before)

    # 4 — retailer policy/payment/contact and independent metrics have field backing.
    before = len(issues)
    retailer_fields = [
        "contact_phone", "contact_email", "contact_channels", "return_window_days", "return_window_basis",
        "return_free_shipping", "return_free_shipping_basis", "return_free_shipments_per_year",
        "return_excludes_resized", "return_excludes_custom", "return_exclusions_detail", "resize_policy",
        "payment_methods_verified", "payment_note",
    ]
    for retailer in retailers:
        for field in retailer_fields:
            if retailer.get(field) is not None and not retailer.get("field_evidence", {}).get(field):
                fail("retailer-backing", f"{retailer['id']} {field} has no field evidence")
        if retailer.get("contact_phone"):
            if digits(retailer["contact_phone"])[-10:] not in digits(combined_quotes(retailer, "contact_phone")):
                fail("retailer-backing", f"{retailer['id']} phone digits do not match evidence")
        if retailer.get("contact_email") and norm(retailer["contact_email"]) not in combined_quotes(retailer, "contact_email"):
            fail("retailer-backing", f"{retailer['id']} email does not match evidence")
        if retailer.get("return_window_days") is not None and not quote_has_number(retailer["return_window_days"], combined_quotes(retailer, "return_window_days")):
            fail("retailer-backing", f"{retailer['id']} return-window number missing from evidence")
        if retailer.get("return_free_shipments_per_year") is not None:
            value = retailer["return_free_shipments_per_year"]
            text = combined_quotes(retailer, "return_free_shipments_per_year")
            words = {1: "one", 2: "two", 3: "three"}
            if not quote_has_number(value, text) and words.get(value, "") not in text:
                fail("retailer-backing", f"{retailer['id']} yearly return count missing from evidence")
        methods_text = combined_quotes(retailer, "payment_methods_verified")
        for method in retailer.get("payment_methods_verified") or []:
            if norm(method) not in methods_text:
                fail("retailer-backing", f"{retailer['id']} payment method {method!r} missing from payment quotes")
        reputation = retailer["independent_reputation"]
        reputation_map = {
            "bbb_rating": "reputation_rating", "bbb_accredited": "reputation_accreditation",
            "review_average_out_of_5": "reputation_reviews", "review_count": "reputation_reviews",
            "complaints_last_3_years": "reputation_complaints", "complaints_last_12_months": "reputation_complaints",
        }
        for field, evidence_field in reputation_map.items():
            value = reputation.get(field)
            if value is None:
                continue
            text = combined_quotes(retailer, evidence_field)
            if not text:
                fail("reputation-backing", f"{retailer['id']} {field} has no independent evidence")
            elif field == "bbb_rating" and norm(value) not in text:
                fail("reputation-backing", f"{retailer['id']} BBB rating mismatch")
            elif field == "bbb_accredited":
                expected = "bbb accredited business" if value else "not bbb accredited"
                if expected not in text.replace("**", ""):
                    fail("reputation-backing", f"{retailer['id']} BBB accreditation mismatch")
            elif field != "bbb_rating" and not quote_has_number(value, text, comma=True):
                fail("reputation-backing", f"{retailer['id']} {field} not found in independent evidence")
        if reputation.get("profile_scope") and not retailer.get("field_evidence", {}).get("reputation_scope"):
            fail("reputation-backing", f"{retailer['id']} profile scope has no evidence")
    record("Retailer policy, payment, contact, and independent metrics are field-backed", before)

    # 5 — official domains and source URL safety.
    before = len(issues)
    for item in items:
        retailer = by_retailer.get(item["retailer_id"])
        if not retailer:
            fail("domain", f"{item['id']} unknown retailer")
            continue
        parsed = urlsplit(item["source_url"])
        host = parsed.hostname or ""
        allowed = {domain.lower().replace("www.", "") for domain in retailer["domains"]}
        if parsed.scheme != "https" or (host or "").lower().replace("www.", "") not in allowed:
            fail("domain", f"{item['id']} non-official product URL: {item['source_url']}")
        policy = urlsplit(item["return_policy_url"])
        if policy.scheme != "https" or (policy.hostname or "").lower().replace("www.", "") not in allowed:
            fail("domain", f"{item['id']} non-official return-policy URL")
    for retailer in retailers:
        allowed = {domain.lower().replace("www.", "") for domain in retailer["domains"]}
        for field in ("website", "contact_source_url", "return_policy_url", "payment_source_url"):
            url = retailer.get(field)
            parsed = urlsplit(url)
            if not url or parsed.scheme != "https" or (parsed.hostname or "").lower().replace("www.", "") not in allowed:
                fail("domain", f"{retailer['id']} invalid official {field}: {url}")
        reputation = retailer["independent_reputation"]
        for field in ("profile_url", "candidate_profile_url", "reviews_url", "complaints_url"):
            url = reputation.get(field)
            if url is not None and (urlsplit(url).scheme != "https" or urlsplit(url).hostname != "www.bbb.org"):
                fail("domain", f"{retailer['id']} non-BBB reputation URL: {url}")
    for flag in flags:
        if not flag.get("sources"):
            fail("domain", f"{flag['id']} has no source links")
        for url in flag.get("sources", []):
            if urlsplit(url).scheme != "https":
                fail("domain", f"{flag['id']} non-HTTPS source: {url}")
    for field, expected_host in (("source_url", "www.gold.org"), ("conversion_source_url", "www.nist.gov"), ("karat_source_url", "www.ecfr.gov")):
        parsed = urlsplit(gold[field])
        if parsed.scheme != "https" or parsed.hostname != expected_host:
            fail("domain", f"gold {field} has unexpected host {parsed.hostname}")
    record("Official product/policy domains and independent-source URLs are constrained", before)

    # 6 — null-to-flag coverage and two-way item/retailer references.
    before = len(issues)
    for item in items:
        applied = set(item["flags"])
        for flag_id in applied:
            if flag_id not in by_flag:
                fail("flag-link", f"{item['id']} references unknown {flag_id}")
            elif item["id"] not in by_flag[flag_id]["affected_items"]:
                fail("flag-link", f"{item['id']} applies {flag_id}, but flag does not list the item")
        required = []
        if item.get("solid_gold_explicit") is not True:
            required.append("F-001")
        if item.get("hallmark_stated") is not True or item.get("makers_mark_stated") is not True:
            required.append("F-002")
        if item.get("weight_g") is None:
            required.append("F-003")
        if item.get("width_mm") is None or item.get("depth_mm") is None:
            required.append("F-016")
        if item.get("color") is None:
            required.append("F-017")
        if item.get("price") is None:
            required.append("F-025" if item.get("superseded_normalization") else "F-018" if item.get("unassigned_price_text") else "F-008")
        if item.get("currency") not in (None, "USD"):
            required.append("F-007")
        if item.get("independent_test_permission") is not True:
            required.append("F-021")
        if item.get("physical_test_status") == "not_tested":
            required.append("F-024")
        for flag_id in required:
            if flag_id not in applied:
                fail("null-coverage", f"{item['id']} requires {flag_id} for its blank/unconfirmed state")
        if item.get("price") is not None and not item.get("currency"):
            fail("null-coverage", f"{item['id']} assigned price lacks currency")
        if item.get("unassigned_price_text") and (item.get("price") is not None or item.get("original_price") is not None):
            fail("null-coverage", f"{item['id']} has unassigned price text but structured prices are populated")
    for flag in flags:
        for key in ("id", "severity", "type", "title", "detail", "recommended_action", "sources"):
            if not flag.get(key):
                fail("flags", f"{flag.get('id', '?')} missing {key}")
        if flag["severity"] not in ("high", "medium", "low"):
            fail("flags", f"{flag['id']} invalid severity")
        for item_id in flag["affected_items"]:
            if item_id not in by_item:
                fail("flag-link", f"{flag['id']} unknown affected item {item_id}")
            elif flag["id"] not in by_item[item_id]["flags"]:
                fail("flag-link", f"{flag['id']} lists {item_id}, but item does not apply the flag")
        for retailer_id in flag.get("affected_retailers", []):
            if retailer_id not in by_retailer:
                fail("flag-link", f"{flag['id']} unknown affected retailer {retailer_id}")
            elif flag["id"] not in by_retailer[retailer_id]["flags"]:
                fail("flag-link", f"{flag['id']} lists {retailer_id}, but retailer does not apply the flag")
    for retailer in retailers:
        for flag_id in retailer["flags"]:
            if flag_id not in by_flag:
                fail("flag-link", f"{retailer['id']} references unknown {flag_id}")
            elif retailer["id"] not in by_flag[flag_id].get("affected_retailers", []):
                fail("flag-link", f"{retailer['id']} applies {flag_id}, but flag does not list retailer")
        if retailer.get("independent_test_permission") is not True and "F-021" not in retailer["flags"]:
            fail("null-coverage", f"{retailer['id']} lacks independent-testing flag")
    record("Blank states are flagged and item/retailer flag references are bidirectional", before)

    # 7 — rejected and superseded values cannot become current values.
    before = len(issues)
    for item in items:
        for rejected in item.get("rejected_values", []):
            if not rejected.get("reason") or not rejected.get("source") or rejected.get("value") is None:
                fail("rejected", f"{item['id']} incomplete rejected-value record")
            if rejected.get("value") in (item.get("price"), item.get("original_price")):
                fail("rejected", f"{item['id']} rejected value equals a current structured price")
    for observation in gold.get("superseded_observations", []):
        if observation.get("value") == gold["usd_per_troy_oz"]:
            fail("rejected", "superseded gold observation equals current quote")
        if observation.get("status") != "superseded_intraday" or not observation.get("reason"):
            fail("rejected", "invalid superseded gold observation")
    record("Rejected snippets and superseded gold quotes are not current values", before)

    # 8 — calculator constants and published derived rows.
    before = len(issues)
    grams_oz = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    expected_derived = {}
    for item in items:
        if item.get("weight_g") is not None:
            fine = item["weight_g"] * item["karat"] / 24
            melt = fine / grams_oz * spot
            expected_derived[item["id"]] = (fine, melt)
            if item.get("price") is not None and item.get("currency") == "USD" and item["price"] < melt:
                warn("melt", f"{item['id']} Asking below conditional theoretical value needs review; not a publication blocker or guaranteed scrap floor")
    prices_path = SITE / "prices.html"
    prices_text = prices_path.read_text(encoding="utf-8") if prices_path.exists() else ""
    for item_id, (fine, melt) in expected_derived.items():
        if f"{fine:.3f} g" not in prices_text or f"${melt:,.2f}" not in prices_text:
            fail("melt", f"{item_id} derived fine-gold/melt values are absent or stale in prices.html")
    for item in items:
        if item.get("weight_g") is None and item["name"] in prices_text:
            fail("melt", f"{item['id']} has no weight but appears in the calculator page")
    if f'value="{spot:.2f}"' not in prices_text:
        fail("melt", "calculator spot input does not match current gold quote")
    record("Nominal fine-gold and melt calculations use current constants", before)

    # 9 — generated HTML, row identity, links/fragments, and CSP.
    before = len(issues)
    missing_pages = [name for name in PAGE_NAMES if not (SITE / name).is_file()]
    if missing_pages:
        fail("html", f"missing built pages: {missing_pages}")
    parsed_pages = {}
    link_total = 0
    external_total = 0
    for name in PAGE_NAMES:
        path = SITE / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        parsed_pages[name] = (text, parser)
        if "<title>" not in text or "assets/style.css" not in text:
            fail("html", f"{name} lacks title or stylesheet")
        for token in (">None<", ">nan<", "undefined", "TODO", "{{", "}}"):
            if token in text:
                fail("html", f"{name} contains suspicious token {token!r}")
        if parser.event_attributes:
            fail("security", f"{name} has inline event handlers: {parser.event_attributes}")
        if any(tag in parser.tags for tag in ("iframe", "object", "embed")):
            fail("security", f"{name} contains iframe/object/embed")
        csp = next((meta.get("content", "") for meta in parser.metas if meta.get("http-equiv", "").lower() == "content-security-policy"), "")
        if "script-src 'self'" not in csp or "connect-src 'none'" not in csp or "object-src 'none'" not in csp:
            fail("security", f"{name} has missing/weak CSP")
        for script in parser.scripts:
            src = script.get("src")
            if not src:
                fail("security", f"{name} contains an inline script")
            elif src != "assets/calculator.js":
                fail("security", f"{name} contains unexpected script {src}")
        if len(parser.ids) != len(set(parser.ids)):
            fail("html", f"{name} contains duplicate HTML ids")
        for href in parser.hrefs:
            link_total += 1
            parsed = urlsplit(href)
            if parsed.scheme in ("http", "https", "mailto", "tel"):
                external_total += 1
                if parsed.scheme == "http" or parsed.scheme == "javascript":
                    fail("security", f"{name} unsafe link {href}")
                continue
            if parsed.scheme or href.startswith("//"):
                fail("security", f"{name} unsafe/protocol-relative link {href}")
                continue
            target_name = unquote(parsed.path) or name
            target = SITE / target_name
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                fail("links", f"{name} broken internal link {href}")
                continue
            if parsed.fragment and target.suffix == ".html":
                target_text = target.read_text(encoding="utf-8")
                target_parser = PageParser()
                target_parser.feed(target_text)
                if parsed.fragment not in target_parser.ids:
                    fail("links", f"{name} missing fragment target {href}")
    item_rows = {}
    for name in CATEGORY_PAGES:
        if name not in parsed_pages:
            continue
        text = parsed_pages[name][0]
        rows = re.findall(r'<tr class="item-row"([^>]*)>(.*?)</tr>', text, flags=re.S)
        for attributes, row in rows:
            id_match = re.search(r'data-item-id="([^"]+)"', attributes)
            source_match = re.search(r'data-source-url="([^"]+)"', attributes)
            if not id_match or not source_match:
                fail("html-rows", f"{name} row lacks data identity/source")
                continue
            item_id = id_match.group(1)
            if item_id in item_rows:
                fail("html-rows", f"duplicate rendered item {item_id}")
            item_rows[item_id] = (name, row, source_match.group(1))
    if set(item_rows) != set(by_item):
        fail("html-rows", f"rendered item IDs differ from data: missing={sorted(set(by_item)-set(item_rows))}, extra={sorted(set(item_rows)-set(by_item))}")
    for item_id, (name, row, rendered_source) in item_rows.items():
        item = by_item[item_id]
        if rendered_source != item["source_url"] or f'href="{item["source_url"]}"' not in row:
            fail("html-rows", f"{item_id} rendered source is not its official URL")
        if f'href="{item["evidence_file"]}"' not in row:
            fail("html-rows", f"{item_id} row lacks its item-scoped evidence link")
        if item["name"] not in row or item["sku"] not in row or item["metal"] not in row:
            fail("html-rows", f"{item_id} name/SKU/metal output is stale")
        if item.get("price") is not None:
            symbol = {"USD": "$", "EUR": "€"}[item["currency"]]
            if f"{symbol}{item['price']:,.2f}" not in row:
                fail("html-rows", f"{item_id} current price output is stale")
        for rejected in item.get("rejected_values", []):
            value = rejected["value"]
            for rendered in (f"${value:,.2f}", f"${value:,.0f}"):
                if rendered in row:
                    fail("html-rows", f"{item_id} rejected value {rendered} appears in its item row")
    for flag in flags:
        if flag["id"].lower() not in parsed_pages.get("flags.html", ("", PageParser()))[1].ids:
            fail("html", f"flags.html missing anchor for {flag['id']}")
    for observation in gold.get("superseded_observations", []):
        stale = f"{observation['value']:,.2f}"
        for name, (text, _) in parsed_pages.items():
            if stale in text:
                fail("stale", f"{name} exposes superseded gold quote {stale}")
    record(f"Built pages: row/source identity, CSP, internal destinations/fragments, and external URL structure ({link_total} link occurrences, {external_total} external). External retrieval is documented separately; future availability is not guaranteed.", before)

    # 10 — explicit open coverage, never hidden by a PASS.
    before = len(issues)
    with_price = sum(1 for item in items if item.get("price") is not None)
    with_weight = sum(1 for item in items if item.get("weight_g") is not None)
    if with_price < len(items):
        warn("coverage", f"{len(items)-with_price} of {len(items)} rows have no explicitly assigned current price (F-008/F-018/F-025)")
    if with_weight < len(items):
        warn("coverage", f"{len(items)-with_weight} of {len(items)} rows have no published metal weight (F-003)")
    record("Coverage limitations remain visible", before)

    # Report.
    REPORTS.mkdir(exist_ok=True)
    failures = [issue for issue in issues if issue[0] == "FAIL"]
    warnings = [issue for issue in issues if issue[0] == "WARN"]
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# QA / hallucination and integration audit", "",
        f"- Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"- Items audited: {len(items)} · retailers: {len(retailers)} · flags: {len(flags)} · field-scoped quotes: {quote_count}",
        f"- **RESULT: {status}** — {len(checks)} checks, {len(failures)} failures, {len(warnings)} warnings", "",
        "## Checks", "", "| # | Check | Result | Findings |", "|---|-------|--------|----------|",
    ]
    for number, (name, check_status, count) in enumerate(checks, 1):
        lines.append(f"| {number} | {name} | {'✅ PASS' if check_status == 'PASS' else '❌ FAIL'} | {count} |")
    lines += ["", "## Failures", ""]
    lines += [f"- {message}" for _, message in failures] or ["- none"]
    lines += ["", "## Warnings", ""]
    lines += [f"- {message}" for _, message in warnings] or ["- none"]
    lines += [
        "", "## What this audit proves, and what it does not", "",
        "It checks internal consistency: published fields resolve to field-specific quotes in each subject's own evidence file; blank states are flagged; product/policy domains are constrained; generated rows carry their exact official URLs; calculations use the dated constants; and internal links/fragments and browser-security constraints hold.",
        "It does **not** prove that a retailer is truthful, that a physical ring matches its listing, that BBB allegations are established, or that an external URL will remain available. External sources were directly fetched during research and the dated inventory is in `reports/source-link-review.md`; this local structural audit is not a live network monitor. No physical inspection or XRF assay was performed.",
        "**Look for hallucinations again after every review.** Re-read the official source and generated page after every edit. A PASS is a guardrail, never a guarantee of factual truth.",
    ]
    (REPORTS / "qa-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RESULT: {status} — {len(checks)} checks, {len(failures)} failures, {len(warnings)} warnings")
    for severity, message in issues:
        if severity == "FAIL":
            print("  FAIL", message)
    for severity, message in issues:
        if severity == "WARN":
            print("  WARN", message)
    print(f"report -> {REPORTS / 'qa-report.md'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
