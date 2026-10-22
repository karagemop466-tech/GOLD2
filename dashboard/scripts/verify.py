#!/usr/bin/env python3
"""GOLD2 hallucination security passes (dashboard scope).

Data passes (always):  P1 sources, P2 prices, P3 blanks, P4 cross-refs,
P5 retailers, P8 evidence quotes.
Build passes (--check-build): P6 data<->site sync, P7 link integrity.

Appends every run to verification-log.json. Exit code 0 = all passes green.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOG = ROOT / "verification-log.json"

OFFICIAL_DOMAINS = {
    "bluenile.com", "www.bluenile.com",
    "jamesallen.com", "www.jamesallen.com",
    "costco.com", "www.costco.com",
    "customerservice.costco.com",
    "lbma.org.uk", "www.lbma.org.uk",
    "ecfr.gov", "www.ecfr.gov",
    "govinfo.gov", "www.govinfo.gov",
    "nist.gov", "www.nist.gov",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FAILURES: list[str] = []
PASSES: dict[str, str] = {}


def fail(msg: str) -> None:
    FAILURES.append(msg)


def check(name: str, fn) -> None:
    before = len(FAILURES)
    fn()
    PASSES[name] = "PASS" if len(FAILURES) == before else "FAIL"


def is_official(url: str) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False
    return p.scheme == "https" and (p.hostname or "") in OFFICIAL_DOMAINS


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def norm(text: str) -> str:
    for ch in "\u200b\u200c\u200d\ufeff\u00a0":
        text = text.replace(ch, " " if ch == "\u00a0" else "")
    return re.sub(r"\s+", " ", text).strip().lower()


def main() -> int:
    check_build = "--check-build" in sys.argv
    rings_doc = load_json(DATA / "rings.json")
    retailers_doc = load_json(DATA / "retailers.json")
    flags_doc = load_json(DATA / "flags.json")
    ref_doc = load_json(DATA / "gold-reference.json")

    rings = rings_doc["rings"]
    retailers = {r["id"]: r for r in retailers_doc["retailers"]}
    flags = flags_doc["flags"]
    flag_ids = [f["id"] for f in flags]
    ring_ids = {r["id"] for r in rings}

    today = datetime.now(timezone.utc).date().isoformat()

    # ---- P1: every data URL is https on an official domain ----
    def p1():
        urls = []
        for r in rings:
            urls.append((f"rings.{r['id']}.product_url", r.get("product_url")))
        for r in retailers.values():
            for k in ("site_url", "contact_url", "returns_url", "jewelry_notes_url"):
                urls.append((f"retailers.{r['id']}.{k}", r.get(k)))
        for u in ref_doc["troy_ounce"]["sources"]:
            urls.append(("gold-reference.troy_ounce.sources", u))
        for u in ref_doc["lbma_price_method"]["sources"]:
            urls.append(("gold-reference.lbma_price_method.sources", u))
        for u in ref_doc["karat_definition"]["manual_review_links"]:
            urls.append(("gold-reference.karat_definition.manual_review_links", u))
        for h in ref_doc["hallmark_law"]:
            urls.append((f"gold-reference.hallmark_law.{h['title'][:30]}", h.get("source")))
        for field, url in urls:
            if not url or not is_official(url):
                fail(f"P1 {field}: not an https URL on an allowlisted official domain: {url!r}")
    check("P1-sources", p1)

    # ---- P2: prices require positive number + capture date + note ----
    def p2():
        for r in rings:
            p = r.get("price_usd")
            d = r.get("capture_date", "")
            if p is not None:
                if not isinstance(p, (int, float)) or p <= 0:
                    fail(f"P2 {r['id']}: price_usd must be a positive number, got {p!r}")
                if not DATE_RE.match(d or ""):
                    fail(f"P2 {r['id']}: priced row needs capture_date YYYY-MM-DD, got {d!r}")
                elif d > today:
                    fail(f"P2 {r['id']}: capture_date {d} is in the future (today {today})")
            if not r.get("price_note"):
                fail(f"P2 {r['id']}: price_note is required (blank prices must explain why)")
    check("P2-prices", p2)

    # ---- P3: blanks must be unverified + flagged; filled values need sources ----
    def p3():
        for r in rings:
            if r.get("weight_g") is None:
                if r.get("weight_status") != "unverified":
                    fail(f"P3 {r['id']}: null weight_g needs weight_status='unverified'")
            elif not r.get("weight_source"):
                fail(f"P3 {r['id']}: non-null weight_g needs weight_source (never infer)")
            if r.get("hallmark_stated") is None:
                if r.get("hallmark_status") != "unverified":
                    fail(f"P3 {r['id']}: null hallmark needs hallmark_status='unverified'")
            elif not r.get("hallmark_source"):
                fail(f"P3 {r['id']}: non-null hallmark needs hallmark_source (never infer)")
            if not r.get("solid_gold_wording_observed") and "F-SOLID-WORDING" not in r.get("flags", []):
                fail(f"P3 {r['id']}: solid wording unobserved but F-SOLID-WORDING flag missing")
            if r.get("price_usd") is None and not any(
                f.startswith("F-PRICE") for f in r.get("flags", [])
            ):
                fail(f"P3 {r['id']}: blank price needs an F-PRICE* flag")
            for f in r.get("flags", []):
                if f not in flag_ids:
                    fail(f"P3 {r['id']}: unknown flag {f!r}")
    check("P3-blanks", p3)

    # ---- P4: cross-references resolve ----
    def p4():
        if len(flag_ids) != len(set(flag_ids)):
            fail("P4: duplicate flag ids")
        specials = {"calculator", "all-rings"}
        for r in rings:
            if r.get("retailer_id") not in retailers:
                fail(f"P4 {r['id']}: unknown retailer_id {r.get('retailer_id')!r}")
        for f in flags:
            for ref in f.get("applies_to", []):
                if ref not in ring_ids and ref not in retailers and ref not in specials:
                    fail(f"P4 {f['id']}: applies_to unknown ref {ref!r}")
            for k in ("title", "issue", "evidence", "resolution"):
                if not f.get(k):
                    fail(f"P4 {f['id']}: missing required field {k}")
    check("P4-crossref", p4)

    # ---- P5: retailers have dated official contact/returns ----
    def p5():
        for r in retailers.values():
            for k in ("contact_url", "returns_url"):
                if not is_official(r.get(k, "")):
                    fail(f"P5 {r['id']}: {k} not official: {r.get(k)!r}")
            for k in ("contact_verified", "returns_verified"):
                if not DATE_RE.match(r.get(k, "") or ""):
                    fail(f"P5 {r['id']}: {k} must be YYYY-MM-DD, got {r.get(k)!r}")
            for f in r.get("flags", []):
                if f not in flag_ids:
                    fail(f"P5 {r['id']}: unknown flag {f!r}")
    check("P5-retailers", p5)

    # ---- P8: every value traces to a verbatim quote in its evidence file ----
    def p8():
        cache: dict[str, str] = {}

        def evidence_text(rel: str) -> str:
            if rel not in cache:
                p = ROOT / rel
                if not p.exists():
                    fail(f"P8: missing evidence file {rel}")
                    cache[rel] = ""
                else:
                    cache[rel] = norm(p.read_text(encoding="utf-8"))
            return cache[rel]

        subjects = [("ring", r) for r in rings] + [("retailer", r) for r in retailers.values()]
        for kind, obj in subjects:
            rel = obj.get("evidence_file", "")
            quotes = obj.get("evidence_quotes") or []
            label = obj.get("id", "?")
            if not rel:
                fail(f"P8 {kind} {label}: missing evidence_file")
                continue
            text = evidence_text(rel)
            if not quotes:
                fail(f"P8 {kind} {label}: no evidence_quotes")
            for q in quotes:
                if norm(q) not in text:
                    fail(f"P8 {kind} {label}: quote not found in {rel}: {q!r}")
            for key in ("product_url", "site_url", "contact_url", "returns_url"):
                u = obj.get(key)
                if u and norm(u) not in text:
                    fail(f"P8 {kind} {label}: URL not echoed in {rel}: {u}")
            if kind == "ring" and obj.get("price_usd") is not None:
                digits = f"{obj['price_usd']:,}".replace(",", "")
                if digits not in text.replace(",", "").replace(" ", ""):
                    fail(f"P8 ring {label}: price digits {digits} not in {rel}")
    check("P8-evidence", p8)

    # ---- P6/P7: build checks ----
    if check_build:
        def p6():
            rings_html = (ROOT / "rings.html").read_text(encoding="utf-8")
            retailers_html = (ROOT / "retailers.html").read_text(encoding="utf-8")
            flagged_html = (ROOT / "flagged.html").read_text(encoding="utf-8")
            index_html = (ROOT / "index.html").read_text(encoding="utf-8")
            for r in rings:
                if r["id"] not in rings_html:
                    fail(f"P6: ring {r['id']} missing from rings.html (run build.py?)")
                if r.get("price_usd") is not None and f"${r['price_usd']:,}" not in rings_html:
                    fail(f"P6: price ${r['price_usd']:,} for {r['id']} missing from rings.html")
            for rid, r in retailers.items():
                if r["name"] not in retailers_html:
                    fail(f"P6: retailer {r['name']} missing from retailers.html")
            for f in flags:
                if f["id"] not in flagged_html:
                    fail(f"P6: flag {f['id']} missing from flagged.html")
            if "NO HALLUCINATIONS" not in index_html:
                fail("P6: index.html missing NO HALLUCINATIONS banner")
            # ensure every page was rendered by build.py (closing region markers exist)
            for page, markers in (
                ("rings.html", ("BUILD:RINGS_ROWS",)),
                ("retailers.html", ("BUILD:RETAILERS_ROWS",)),
                ("flagged.html", ("BUILD:FLAGS",)),
                ("index.html", ("BUILD:STATS", "BUILD:VERIFY_SUMMARY")),
            ):
                text = (ROOT / page).read_text(encoding="utf-8")
                for marker in markers:
                    if f"<!-- /{marker} -->" not in text:
                        fail(f"P6: {page} missing rendered region {marker} (run build.py?)")
        check("P6-build", p6)

        def p7():
            href_re = re.compile(r'href="([^"]+)"')
            for page in ("index.html", "checklist.html", "rings.html", "retailers.html",
                          "calculator.html", "reference.html", "methodology.html", "flagged.html"):
                text = (ROOT / page).read_text(encoding="utf-8")
                for href in href_re.findall(text):
                    if href.startswith(("mailto:", "#")):
                        continue
                    if "://" in href:
                        if not href.startswith("https://"):
                            fail(f"P7 {page}: external link must be https: {href}")
                        continue
                    target = href.split("#")[0].split("?")[0]
                    if target and not (ROOT / target).exists():
                        fail(f"P7 {page}: internal link target missing: {href}")
        check("P7-links", p7)

    result = "FAIL" if FAILURES else "PASS"
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "verify.py --check-build" if check_build else "verify.py",
        "result": result,
        "passes": PASSES,
        "failures": FAILURES,
        "counts": {
            "rings": len(rings),
            "retailers": len(retailers),
            "flags": len(flags),
            "verified_prices": sum(1 for r in rings if r.get("price_usd") is not None),
            "blank_prices": sum(1 for r in rings if r.get("price_usd") is None),
        },
    }
    log = []
    if LOG.exists():
        log = json.loads(LOG.read_text(encoding="utf-8"))
    log.append(entry)
    LOG.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")

    print(f"GOLD2 verification: {result}")
    for name, status in PASSES.items():
        print(f"  {name}: {status}")
    for f in FAILURES:
        print(f"  !! {f}")
    print("Counts:", json.dumps(entry["counts"]))
    print("Log appended to verification-log.json")
    print("REMINDER: recommend looking for hallucinations — any value without a")
    print("same-row official source link must be treated as unverified.")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
