#!/usr/bin/env python3
"""S-B200A880 independent hallucination & security scanner.

Standalone, standard-library-only control suite written from the project's
no-hallucination policy rather than imported from tools/qa.py. It re-derives
expectations from the JSON data and checks the built HTML against them.

Usage:
    python3 audit/b200a880/hallucination_security_scanner.py [repo_root]

Exit code is non-zero if any FAIL control fires. WARNs never fail the run but
are printed. A PASS means the stated controls found no defect; it is not proof
that an external seller is truthful or that a page cannot change later.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

LISTING_FILES = [
    "data/solid-gold-verified.json",
    "data/listings/solitaire.json",
    "data/listings/halo-pave.json",
    "data/listings/three-stone-vintage.json",
    "data/listings/18k.json",
    "data/listings/budget.json",
]
CATEGORY_PAGES = [
    "solid-gold.html", "solitaire.html", "halo-pave.html",
    "three-stone-vintage.html", "18k.html", "budget.html",
]
ALL_PAGES = CATEGORY_PAGES + [
    "index.html", "retailers.html", "prices.html", "flags.html", "methods.html",
    "verification.html", "analysis.html",
]
PUBLISHED_NUMERIC = ("price", "original_price", "width_mm", "depth_mm", "weight_g")
CURRENCY_SYMBOL = {"USD": "$", "EUR": "€"}


def norm(text: str) -> str:
    for char in "\u200b\u200c\u200d\ufeff\u00a0":
        text = text.replace(char, " " if char == "\u00a0" else "")
    return re.sub(r"\s+", " ", text).strip().lower()


def number_variants(value: float) -> set[str]:
    variants = {f"{value:g}", f"{value:.1f}", f"{value:.2f}"}
    variants |= {f"{value:,.2f}", f"{value:,.0f}"}
    return {norm(v) for v in variants}


def quote_contains_number(value: float, quote_text: str) -> bool:
    compact = quote_text.replace(" ", "")
    return any(v in quote_text or v.replace(" ", "") in compact for v in number_variants(value))


def required_item_flags(item: dict) -> list:
    """Flags an item must carry for its blank/unconfirmed state.

    Mirrors the authoritative rule in tools/qa.py (2026-10-23 one-currency
    model): unassigned price text -> F-018; native display without an ISO
    currency statement -> F-025; no price string at all -> F-008.
    """
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
        if item.get("unassigned_price_text"):
            required.append("F-018")
        elif item.get("observed_native_display"):
            required.append("F-025")
        else:
            required.append("F-008")
    if item.get("currency") not in (None, "USD"):
        required.append("F-007")
    if item.get("independent_test_permission") is not True:
        required.append("F-021")
    if item.get("physical_test_status") == "not_tested":
        required.append("F-024")
    return required


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().replace("www.", "")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.scripts: list[dict] = []
        self.metas: list[dict] = []
        self.events: list[str] = []
        self.tags: list[str] = []

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
                self.events.append(name)


class Scanner:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[tuple[str, str]] = []
        self.control_count = 0

    def fail(self, control: str, message: str):
        self.findings.append(("FAIL", f"[{control}] {message}"))

    def warn(self, control: str, message: str):
        self.findings.append(("WARN", f"[{control}] {message}"))

    def check(self, condition: bool, control: str, message: str):
        self.control_count += 1
        if not condition:
            self.fail(control, message)

    def load(self, relative: str):
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def run(self) -> int:
        gold = self.load("data/gold-price.json")
        retailers = self.load("data/retailers.json")["retailers"]
        flags = self.load("data/flags.json")["flags"]
        items = []
        for relative in LISTING_FILES:
            payload = self.load(relative)
            for item in payload["items"]:
                item["_file"] = relative
                items.append(item)
        by_id = {item["id"]: item for item in items}
        by_flag = {flag["id"]: flag for flag in flags}
        by_retailer = {r["id"]: r for r in retailers}
        today = date.today().isoformat()

        # C1 — identity, dates, official domains, item-scoped evidence files.
        self.check(len(items) == 20, "C1-identity", f"expected 20 items, found {len(items)}")
        self.check(len(by_id) == len(items), "C1-identity", "duplicate item ids")
        seen_urls = set()
        for item in items:
            self.check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["retrieved_at"])),
                       "C1-dates", f"{item['id']} bad retrieved_at")
            self.check(item["retrieved_at"] <= today, "C1-dates",
                       f"{item['id']} retrieved_at in the future")
            retailer = by_retailer.get(item["retailer_id"])
            self.check(retailer is not None, "C1-domain", f"{item['id']} unknown retailer")
            if retailer:
                allowed = {d.lower().replace("www.", "") for d in retailer["domains"]}
                self.check(urlsplit(item["source_url"]).scheme == "https"
                           and host_of(item["source_url"]) in allowed,
                           "C1-domain", f"{item['id']} source not on an official domain")
                self.check(host_of(item["return_policy_url"]) in allowed,
                           "C1-domain", f"{item['id']} return policy not on official domain")
            self.check(item["source_url"] not in seen_urls, "C1-identity",
                       f"{item['id']} duplicate source URL")
            seen_urls.add(item["source_url"])
            expected_evidence = f"evidence/listings/{item['id'].lower()}.md"
            self.check(item["evidence_file"] == expected_evidence
                       and (self.root / item["evidence_file"]).is_file(),
                       "C1-evidence", f"{item['id']} evidence file missing or not item-scoped")

        # C2 — every field-scoped quote resolves verbatim in its own evidence file.
        quote_total = 0
        for item in items:
            text = norm((self.root / item["evidence_file"]).read_text(encoding="utf-8"))
            for field, quotes in item.get("field_evidence", {}).items():
                self.check(isinstance(quotes, list) and quotes, "C2-quotes",
                           f"{item['id']} field {field} has no quote list")
                for quote in quotes:
                    quote_total += 1
                    self.check(isinstance(quote, str) and norm(quote) in text,
                               "C2-quotes", f"{item['id']} {field}: quote absent from evidence: {quote!r}")
        for retailer in retailers:
            text = norm((self.root / retailer["evidence_file"]).read_text(encoding="utf-8"))
            for field, quotes in retailer.get("field_evidence", {}).items():
                for quote in quotes:
                    quote_total += 1
                    self.check(norm(quote) in text, "C2-quotes",
                               f"{retailer['id']} {field}: quote absent from evidence")
        self.check(quote_total >= 300, "C2-quotes", f"only {quote_total} field quotes resolved")

        # C3 — non-null published values are backed by matching quotes.
        for item in items:
            for field in PUBLISHED_NUMERIC:
                value = item.get(field)
                quotes = item.get("field_evidence", {}).get(field)
                if value is not None:
                    self.check(bool(quotes), "C3-backing",
                               f"{item['id']} non-null {field} lacks field evidence")
                    combined = norm(" ".join(quotes or []))
                    self.check(quote_contains_number(value, combined), "C3-backing",
                               f"{item['id']} {field}={value} not found in its quotes")
                    if field == "weight_g":
                        self.check("g" in combined, "C3-backing",
                                   f"{item['id']} weight quote lacks gram unit")
                    if field in ("price", "original_price"):
                        symbol = CURRENCY_SYMBOL.get(item.get("currency"))
                        self.check(bool(symbol) and symbol in combined, "C3-backing",
                                   f"{item['id']} {field} lacks currency symbol evidence")
            for text_field in ("name", "sku", "metal", "unassigned_price_text", "weight_basis"):
                value = item.get(text_field)
                if value is not None:
                    combined = norm(" ".join(item.get("field_evidence", {}).get(text_field, [])))
                    self.check(norm(str(value)) in combined, "C3-backing",
                               f"{item['id']} {text_field} value not present in its quotes")

        # C4 — flags are bidirectional and blank states carry their required flags.
        for item in items:
            applied = set(item["flags"])
            for flag_id in applied:
                self.check(flag_id in by_flag and item["id"] in by_flag[flag_id]["affected_items"],
                           "C4-flags", f"{item['id']} -> {flag_id} is not bidirectional")
            required = required_item_flags(item)
            for flag_id in required:
                self.check(flag_id in applied, "C4-flags",
                           f"{item['id']} missing required {flag_id} for its blank state")
            if item.get("price") is not None and not item.get("currency"):
                self.check(False, "C4-flags",
                           f"{item['id']} assigned price lacks a currency")
            if item.get("price") is not None and item.get("currency"):
                currency_quotes = " ".join(item.get("field_evidence", {}).get("currency", []))
                if item["currency"].lower() not in currency_quotes.lower() and not item.get("currency_source_url"):
                    self.check(False, "C4-flags",
                               f"{item['id']} currency lacks an official quote or source URL")
        for flag in flags:
            self.check(flag.get("sources") and all(urlsplit(u).scheme == "https" for u in flag["sources"]),
                       "C4-flags", f"{flag['id']} lacks https sources")
            for item_id in flag["affected_items"]:
                self.check(item_id in by_id and flag["id"] in by_id[item_id]["flags"],
                           "C4-flags", f"{flag['id']} -> {item_id} is not bidirectional")

        # C5 — rejected/superseded values can never be current or rendered.
        for item in items:
            for rejected in item.get("rejected_values", []):
                self.check(rejected.get("value") not in (item.get("price"), item.get("original_price")),
                           "C5-rejected", f"{item['id']} rejected value is a current price")
        for observation in gold.get("superseded_observations", []):
            self.check(observation["value"] != gold["usd_per_troy_oz"],
                       "C5-rejected", "superseded gold quote equals current quote")

        # C6 — built pages: row identity, official source, evidence link, price rendering.
        rendered_ids = set()
        stale_tokens = (">None<", ">nan<", "undefined", "TODO", "{{", "}}")
        for page_name in CATEGORY_PAGES:
            text = (self.root / page_name).read_text(encoding="utf-8")
            parser = LinkParser()
            parser.feed(text)
            rows = re.findall(r'<tr class="item-row"([^>]*)>(.*?)</tr>', text, flags=re.S)
            for attributes, row in rows:
                id_match = re.search(r'data-item-id="([^"]+)"', attributes)
                source_match = re.search(r'data-source-url="([^"]+)"', attributes)
                self.check(id_match and source_match, "C6-rows",
                           f"{page_name} row missing data identity")
                if not (id_match and source_match):
                    continue
                item_id = id_match.group(1)
                rendered_ids.add(item_id)
                item = by_id.get(item_id)
                self.check(item is not None, "C6-rows", f"{page_name} renders unknown {item_id}")
                if not item:
                    continue
                self.check(source_match.group(1) == item["source_url"], "C6-rows",
                           f"{item_id} data-source-url differs from JSON")
                self.check(f'href="{item["source_url"]}"' in row, "C6-rows",
                           f"{item_id} row lacks official-source href")
                self.check(f'href="{item["evidence_file"]}"' in row, "C6-rows",
                           f"{item_id} row lacks evidence href")
                self.check(item["name"] in row and item["sku"] in row and item["metal"] in row,
                           "C6-rows", f"{item_id} stale name/SKU/metal rendering")
                if item.get("price") is not None:
                    symbol = CURRENCY_SYMBOL[item["currency"]]
                    expected = f"{symbol}{item['price']:,.2f}"
                    self.check(expected in row, "C6-rows",
                               f"{item_id} rendered price differs from data ({expected})")
            for token in stale_tokens:
                self.check(token not in text, "C6-tokens", f"{page_name} contains {token!r}")
        self.check(rendered_ids == set(by_id), "C6-rows",
                   f"rendered id set mismatch: missing={set(by_id) - rendered_ids}")

        # C7 — browser security on every built page.
        for page_name in ALL_PAGES:
            path = self.root / page_name
            self.check(path.is_file(), "C7-security", f"missing page {page_name}")
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            parser = LinkParser()
            parser.feed(text)
            self.check(not parser.events, "C7-security",
                       f"{page_name} inline event handlers: {parser.events}")
            self.check(not any(tag in parser.tags for tag in ("iframe", "object", "embed")),
                       "C7-security", f"{page_name} contains iframe/object/embed")
            csp = next((m.get("content", "") for m in parser.metas
                        if m.get("http-equiv", "").lower() == "content-security-policy"), "")
            for required in ("script-src 'self'", "connect-src 'none'", "object-src 'none'", "base-uri 'none'"):
                self.check(required in csp, "C7-security", f"{page_name} CSP missing {required}")
            for script in parser.scripts:
                src = script.get("src")
                self.check(src == "assets/calculator.js", "C7-security",
                           f"{page_name} unexpected script {src!r}")
            for href in parser.hrefs:
                parsed = urlsplit(href)
                if parsed.scheme in ("http", "javascript"):
                    self.fail("C7-security", f"{page_name} unsafe link {href}")
                elif parsed.scheme in ("https", "mailto", "tel"):
                    continue
                elif parsed.scheme or href.startswith("//"):
                    self.fail("C7-security", f"{page_name} protocol-relative/odd link {href}")
                else:
                    target = unquote(parsed.path) or page_name
                    target_path = self.root / target
                    if target_path.is_dir():
                        target_path = target_path / "index.html"
                    self.check(target_path.is_file(), "C7-links",
                               f"{page_name} broken internal link {href}")
                    if parsed.fragment and target_path.suffix == ".html":
                        target_parser = LinkParser()
                        target_parser.feed(target_path.read_text(encoding="utf-8"))
                        self.check(parsed.fragment in target_parser.ids, "C7-links",
                                   f"{page_name} missing fragment {href}")
            self.check(len(parser.ids) == len(set(parser.ids)), "C7-links",
                       f"{page_name} duplicate HTML ids")

        # C8 — gold arithmetic is reproduced exactly on prices.html.
        prices_text = (self.root / "prices.html").read_text(encoding="utf-8")
        grams_oz = gold["grams_per_troy_ounce"]
        spot = gold["usd_per_troy_oz"]
        self.check(f'value="{spot:.2f}"' in prices_text, "C8-arithmetic",
                   "calculator spot input does not match gold-price.json")
        for item in items:
            if item.get("weight_g") is None:
                continue
            fine = item["weight_g"] * item["karat"] / 24
            melt = fine / grams_oz * spot
            self.check(f"{fine:.3f} g" in prices_text and f"${melt:,.2f}" in prices_text,
                       "C8-arithmetic", f"{item['id']} fine/melt strings stale on prices.html")
        for observation in gold.get("superseded_observations", []):
            for page_name in ALL_PAGES:
                self.check(f"{observation['value']:,.2f}" not in (self.root / page_name).read_text(encoding="utf-8"),
                           "C8-stale", f"{page_name} renders superseded quote {observation['value']}")

        # C9 — index headline counts are data-derived, not typed.
        index_text = (self.root / "index.html").read_text(encoding="utf-8")
        priced = sum(1 for item in items if item.get("price") is not None)
        weighted = sum(1 for item in items if item.get("weight_g") is not None)
        for expected in (len(items), priced, weighted, len(flags)):
            self.check(f'<div class="n">{expected}' in index_text, "C9-counts",
                       f"index stat {expected} not rendered from data")
        self.check(f"${spot:,.2f}" in index_text, "C9-counts", "index gold quote stale")

        # C10 — flags page anchors and evidence retrieval metadata.
        flags_text = (self.root / "flags.html").read_text(encoding="utf-8")
        for flag in flags:
            self.check(f'id="{flag["id"].lower()}"' in flags_text, "C10-flags",
                       f"flags.html missing anchor {flag['id']}")
        for item in items:
            evidence_text = (self.root / item["evidence_file"]).read_text(encoding="utf-8")
            self.check(item["source_url"] in evidence_text, "C10-evidence",
                       f"{item['id']} evidence omits official URL")
            self.check("Retrieved:" in evidence_text or "retrieved" in evidence_text.lower(),
                       "C10-evidence", f"{item['id']} evidence lacks retrieval metadata")
        return 0 if not any(level == "FAIL" for level, _ in self.findings) else 1


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    scanner = Scanner(root)
    exit_code = scanner.run()
    failures = [m for level, m in scanner.findings if level == "FAIL"]
    warnings = [m for level, m in scanner.findings if level == "WARN"]
    print(f"S-B200A880 scanner: {scanner.control_count} controls, "
          f"{len(failures)} failures, {len(warnings)} warnings, "
          f"{'PASS' if exit_code == 0 else 'FAIL'}")
    for message in scanner.findings:
        print(" ", *message)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
