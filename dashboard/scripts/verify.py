#!/usr/bin/env python3
"""GOLD2 Hallucination, Provenance, Link & Security Passes (`dashboard/` scope).

Runs deterministic passes P1..P8 across `dashboard/data/*.json`,
`dashboard/evidence/*.md`, `dashboard/assets/*`, and all 14 `dashboard/*.html` pages,
writes `dashboard/verification-log.json`, and exits 0 iff 0 failures occur.
"""

from __future__ import annotations

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
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
    "bbb.org", "www.bbb.org",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LinkAndRowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.has_csp = False
        self.in_tr = False
        self.tr_td = False
        self.tr_https: list[str] = []
        self.unlinked_rows = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {k.lower(): (v or "") for k, v in attrs}
        if amap.get("id"):
            self.ids.add(amap["id"])
        if tag == "meta" and amap.get("http-equiv", "").lower() == "content-security-policy":
            self.has_csp = True
        elif tag == "tr":
            self.in_tr = True
            self.tr_td = False
            self.tr_https = []
        elif tag == "td" and self.in_tr:
            self.tr_td = True
        elif tag == "a":
            href = amap.get("href", "")
            self.hrefs.append(href)
            if self.in_tr and href.startswith("https://"):
                self.tr_https.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_tr:
            if self.tr_td and not self.tr_https:
                self.unlinked_rows += 1
            self.in_tr = False


def is_official(url: str | None) -> bool:
    if not url:
        return False
    p = urlparse(url)
    return p.scheme == "https" and (p.hostname or "").lower() in ALLOWED_DOMAINS


def main() -> int:
    check_build = "--check-build" in sys.argv
    failures: list[str] = []
    passes: dict[str, str] = {}

    rings = json.loads((DATA / "rings.json").read_text(encoding="utf-8"))["rings"]
    retailers = json.loads((DATA / "retailers.json").read_text(encoding="utf-8"))["retailers"]
    flags = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))["flags"]
    ref = json.loads((DATA / "gold-reference.json").read_text(encoding="utf-8"))
    rings_ev = (EVIDENCE / "rings.md").read_text(encoding="utf-8")
    ret_ev = (EVIDENCE / "retailers.md").read_text(encoding="utf-8")

    def run_pass(code: str, fn) -> None:
        before = len(failures)
        fn()
        passes[code] = "PASS" if len(failures) == before else "FAIL"

    run_pass("P1-sources", lambda: [
        failures.append(f"P1 bad ring url {r['id']}") for r in rings if not is_official(r.get("product_url"))
    ] + [
        failures.append(f"P1 bad retailer url {ret['id']}.{k}")
        for ret in retailers
        for k in ("site_url", "contact_url", "returns_url", "jewelry_notes_url", "bbb_url")
        if not is_official(ret.get(k))
    ] + [
        failures.append("P1 bad spot url") for _ in ([1] if not is_official(ref.get("spot_source_url")) else [])
    ])

    run_pass("P2-prices", lambda: [
        failures.append(f"P2 invalid price/date {r['id']}")
        for r in rings
        if (r.get("price_usd") is not None and (r["price_usd"] <= 0 or not DATE_RE.match(r.get("capture_date", ""))))
        or not r.get("price_note")
    ])

    run_pass("P3-blanks", lambda: [
        failures.append(f"P3 unflagged missing weight {r['id']}")
        for r in rings
        if r.get("weight_g") is None and not r.get("flags")
    ])

    ret_ids = {r["id"] for r in retailers}
    flag_ids = {f["id"] for f in flags}
    run_pass("P4-cross-refs", lambda: [
        failures.append(f"P4 unknown retailer/flag on {r['id']}")
        for r in rings
        if r["retailer_id"] not in ret_ids or any(fid not in flag_ids for fid in r["flags"])
    ])

    run_pass("P5-retailers", lambda: [
        failures.append(f"P5 missing policy summary on {ret['id']}")
        for ret in retailers
        if not ret.get("return_window") or not ret.get("resized_custom_rule") or not ret.get("bbb_summary")
    ])

    run_pass("P8-evidence-quotes", lambda: [
        failures.append(f"P8 missing verbatim quote for {r['id']}")
        for r in rings
        if r["quote"] not in rings_ev
    ] + [
        failures.append(f"P8 missing retailer evidence for {ret['id']}")
        for ret in retailers
        if ret["bbb_summary"] not in ret_ev
    ])

    if check_build:
        html_pages = sorted(ROOT.glob("*.html"))
        parsed_map: dict[Path, LinkAndRowParser] = {}

        def p6() -> None:
            if len(html_pages) < 14:
                failures.append(f"P6 expected 14 HTML pages, found {len(html_pages)}")
            all_rings_html = (ROOT / "rings.html").read_text(encoding="utf-8")
            for r in rings:
                if r["product_url"] not in all_rings_html or html.escape(r["name"], quote=True) not in all_rings_html:
                    failures.append(f"P6 {r['id']} missing from rings.html")
            for p in html_pages:
                parser = LinkAndRowParser()
                parser.feed(p.read_text(encoding="utf-8"))
                parsed_map[p] = parser
                if not parser.has_csp:
                    failures.append(f"P6 missing CSP in {p.name}")
                if parser.unlinked_rows:
                    failures.append(f"P6 {p.name} has {parser.unlinked_rows} table rows without https:// links")

        def p7() -> None:
            for p, parser in parsed_map.items():
                for href in parser.hrefs:
                    u = urlparse(href)
                    if u.scheme in ("https", "mailto", "tel"):
                        if u.scheme == "https" and not is_official(href):
                            failures.append(f"P7 non-allowlisted external link in {p.name}: {href}")
                        continue
                    if u.scheme:
                        failures.append(f"P7 unsafe scheme in {p.name}: {href}")
                        continue
                    clean_path = unquote(u.path)
                    target = (p.parent / clean_path).resolve() if clean_path else p.resolve()
                    if not target.is_file():
                        failures.append(f"P7 broken internal link in {p.name}: {href}")
                        continue
                    if u.fragment and target in parsed_map and u.fragment not in parsed_map[target].ids:
                        failures.append(f"P7 broken fragment in {p.name}: {href}")

        run_pass("P6-data-site-sync", p6)
        run_pass("P7-link-integrity", p7)

    log_doc = {
        "verified_date": "2026-10-23",
        "session": "S-C74095E5",
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
    }
    LOG_PATH.write_text(json.dumps(log_doc, indent=2) + "\n", encoding="utf-8")
    print(f"dashboard verify: {log_doc['status']} — passes={passes}")
    for f in failures:
        print("  FAIL:", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
