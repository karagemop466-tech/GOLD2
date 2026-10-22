#!/usr/bin/env python3
"""Hallucination audit + link check for GOLD2.

Run after EVERY review pass:  python3 tools/qa.py && python3 tools/build_site.py

The audit is deliberately strict: a published value that cannot be traced to a
verbatim quote inside its own evidence file is treated as a hallucination and
the run fails.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT  # Pages serves main "/"
PAGE_NAMES = [
    "index.html", "solitaire.html", "halo-pave.html", "three-stone-vintage.html",
    "18k.html", "budget.html", "retailers.html", "prices.html", "flags.html", "methods.html",
]
REPORTS = ROOT / "reports"
LISTING_FILES = ["solitaire.json", "halo-pave.json", "three-stone-vintage.json", "18k.json", "budget.json"]

issues: list[tuple[str, str]] = []   # (severity, message) severity: FAIL | WARN | INFO
checks: list[tuple[str, str, int]] = []  # (name, status, findings)


def fail(check: str, msg: str) -> None:
    issues.append(("FAIL", f"[{check}] {msg}"))


def warn(check: str, msg: str) -> None:
    issues.append(("WARN", f"[{check}] {msg}"))


def record(name: str, before: int) -> None:
    new = [i for i in issues[before:] if i[0] == "FAIL"]
    checks.append((name, "FAIL" if new else "PASS", len(new)))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    for ch in "\u200b\u200c\u200d\ufeff\u00a0":
        text = text.replace(ch, " " if ch == "\u00a0" else "")
    return re.sub(r"\s+", " ", text).strip().lower()


# ------------------------------------------------------------------ data load
def main() -> int:
    if not DATA.exists():
        print("no data directory")
        return 1

    gold = load(DATA / "gold-price.json")
    retailers = load(DATA / "retailers.json")["retailers"]
    flags_payload = load(DATA / "flags.json")
    flags = flags_payload["flags"]
    items = []
    for fname in LISTING_FILES:
        payload = load(DATA / "listings" / fname)
        for it in payload["items"]:
            it["_file"] = fname
            it["_category"] = payload["category_id"]
            items.append(it)

    flag_ids = [f["id"] for f in flags]
    by_retailer = {r["id"]: r for r in retailers}

    # ---------------------------------------------------------- 1 integrity
    m = len(issues)
    for key in ("quote_date", "retrieved_at", "usd_per_troy_oz", "source_url", "evidence_file"):
        if not gold.get(key):
            fail("gold-price", f"gold-price.json missing {key}")
    if isinstance(gold.get("usd_per_troy_oz"), (int, float)) and gold["usd_per_troy_oz"] <= 0:
        fail("gold-price", "spot price is not positive")
    try:
        qd = datetime.strptime(gold["quote_date"], "%Y-%m-%d").date()
        rd = datetime.strptime(gold["retrieved_at"], "%Y-%m-%d").date()
        if qd > rd:
            fail("gold-price", "quote_date is after retrieved_at")
        if rd > date.today():
            fail("gold-price", "retrieved_at is in the future")
    except Exception as exc:  # noqa: BLE001
        fail("gold-price", f"unparseable date: {exc}")
    ids = [i["id"] for i in items]
    if len(ids) != len(set(ids)):
        fail("ids", "duplicate item id")
    urls = [i["source_url"] for i in items]
    if len(urls) != len(set(urls)):
        fail("ids", "duplicate source_url across items")
    if len(flag_ids) != len(set(flag_ids)):
        fail("ids", "duplicate flag id")
    for r in retailers:
        for key in ("id", "name", "website", "domains", "evidence_file", "verification_status"):
            if not r.get(key):
                fail("retailers", f"{r.get('name','?')} missing {key}")
    record("JSON schema & unique ids", m)

    # ---------------------------------------------------------- 2 evidence quotes
    m = len(issues)
    evidence_cache: dict[str, str] = {}

    def evidence_text(rel: str) -> str:
        if rel not in evidence_cache:
            p = ROOT / rel
            evidence_cache[rel] = norm(p.read_text(encoding="utf-8")) if p.exists() else ""
            if not p.exists():
                fail("evidence", f"missing evidence file {rel}")
        return evidence_cache[rel]

    subjects = [("gold", gold)] + [("retailer", r) for r in retailers] + [("item", i) for i in items]
    quote_count = 0
    for kind, obj in subjects:
        rel = obj.get("evidence_file")
        quotes = obj.get("evidence_quotes") or []
        if not rel:
            continue
        text = evidence_text(rel)
        if not quotes:
            fail("evidence", f"{kind} {obj.get('id', obj.get('name','?'))} has no evidence_quotes")
        for q in quotes:
            quote_count += 1
            if norm(q) not in text:
                fail("evidence", f"{kind} {obj.get('id', obj.get('name','?'))}: quote not found in {rel}: {q!r}")
        extra = [obj.get("source_url"), obj.get("return_policy_url"), obj.get("contact_source_url")]
        for u in extra:
            if u and norm(u) not in text:
                warn("evidence", f"{kind} {obj.get('id', obj.get('name','?'))}: URL not echoed in {rel}: {u}")
    record(f"Every value traces to a verbatim quote ({quote_count} quotes)", m)

    # ---------------------------------------------------------- 3 field backing
    m = len(issues)

    def has_any(rel: str, candidates: list[str]) -> bool:
        text = evidence_text(rel)
        return any(norm(c) in text for c in candidates)

    for it in items:
        rel = it["evidence_file"]
        if it.get("price") is not None:
            p = it["price"]
            cands = [f"{p:,.2f}", f"{p:,.0f}", f"{p:.2f}", f"{p:.0f}", f"{p:g}"]
            if not has_any(rel, cands):
                fail("price-backing", f"{it['id']}: price {p} not backed by any quote in {rel}")
            if it.get("price_basis") not in ("setting_price", "complete_ring"):
                fail("price-backing", f"{it['id']}: invalid price_basis {it.get('price_basis')}")
            if not it.get("currency"):
                fail("price-backing", f"{it['id']}: price without currency")
        if it.get("weight_g") is not None:
            w = it["weight_g"]
            if not has_any(rel, [f"{w:.2f}g", f"{w:g}g", f"{w:.2f} g", f"{w:g} g"]):
                fail("weight-backing", f"{it['id']}: weight {w} not backed by a quote")
        if it.get("width_mm") is not None:
            w = it["width_mm"]
            cands = [f"{w:.2f}mm", f"{w:g}mm", f"{w:.2f} mm", f"{w:g} mm", f"{w:.1f}mm", f"{w:.1f} mm"]
            if not has_any(rel, cands):
                fail("width-backing", f"{it['id']}: width {w} mm not backed by a quote")
        if it.get("karat") is not None:
            k = it["karat"]
            if not has_any(rel, [f"{k}K", f"{k}k", f"{k} k"]):
                fail("karat-backing", f"{it['id']}: karat {k} not backed by a quote")
        if not it.get("source_url", "").startswith("https://"):
            fail("url", f"{it['id']}: source_url is not https")
    record("Price / weight / width / karat backed by quotes", m)

    # ---------------------------------------------------------- 4 domain allowlist
    m = len(issues)
    for it in items:
        r = by_retailer.get(it.get("retailer_id"))
        if not r:
            fail("domain", f"{it['id']}: unknown retailer_id {it.get('retailer_id')}")
            continue
        host = urlparse(it["source_url"]).netloc.lower().replace("www.", "")
        allowed = [d.lower().replace("www.", "") for d in r["domains"]]
        if host not in allowed:
            fail("domain", f"{it['id']}: {host} is not an official domain of {r['name']}")
    for f in flags:
        if not f.get("sources"):
            fail("domain", f"{f['id']}: flag has no source link")
        for u in f.get("sources", []):
            if not u.startswith("https://"):
                fail("domain", f"{f['id']}: source {u} is not https")
    record("Source links point at the seller's own domain", m)

    # ---------------------------------------------------------- 5 null -> flag
    m = len(issues)
    for it in items:
        applied = set(it.get("flags", []))
        for missing in applied:
            if missing not in flag_ids:
                fail("flag-link", f"{it['id']}: references unknown flag {missing}")
        if it.get("weight_g") is None and "F-003" not in applied:
            fail("null-coverage", f"{it['id']}: weight is blank but F-003 is not applied")
        if it.get("solid_gold_explicit") is False and "F-001" not in applied:
            fail("null-coverage", f"{it['id']}: no 'solid gold' wording but F-001 missing")
        if it.get("hallmark_stated") is False and "F-002" not in applied:
            fail("null-coverage", f"{it['id']}: no hallmark stated but F-002 missing")
        if it.get("currency") != "USD" and "F-007" not in applied and it.get("price") is not None:
            fail("null-coverage", f"{it['id']}: non-USD price without F-007")
        if it.get("price") is None and "F-008" not in applied:
            fail("null-coverage", f"{it['id']}: blank price without an unverified flag")
        if it.get("hallmark_stated") is False and it.get("makers_mark_stated") is False:
            pass
    record("Blank values are covered by an explicit flag", m)

    # ---------------------------------------------------------- 6 rejected values
    m = len(issues)
    for it in items:
        for rv in it.get("rejected_values", []):
            if it.get("price") is not None and rv.get("value") == it["price"]:
                fail("rejected", f"{it['id']}: rejected value equals the published price")
            if not rv.get("reason"):
                fail("rejected", f"{it['id']}: rejected value without a reason")
    # cached numbers must never appear as a published price anywhere
    for it in items:
        for rv in it.get("rejected_values", []):
            v = rv.get("value")
            for other in items:
                if other.get("price") == v and other["id"] != it["id"]:
                    warn("rejected", f"rejected value {v} of {it['id']} equals published price of {other['id']}")
    record("Cached/contradictory values are rejected, not published", m)

    # ---------------------------------------------------------- 7 flags sanity
    m = len(issues)
    for f in flags:
        for key in ("id", "severity", "type", "title", "detail", "recommended_action", "sources"):
            if not f.get(key):
                fail("flags", f"{f.get('id','?')} missing {key}")
        if f["severity"] not in ("high", "medium", "low"):
            fail("flags", f"{f['id']}: bad severity")
        for iid in f.get("affected_items", []):
            if iid not in ids:
                fail("flags", f"{f['id']}: affected item {iid} does not exist")
    for f in flags:
        if f["severity"] == "high" and not f.get("affected_items") and f["type"] not in ("source_limitation", "comparability"):
            warn("flags", f"{f['id']}: high severity with no affected rows")
    record("Flag definitions are complete and consistent", m)

    # ---------------------------------------------------------- 8 no negative melt
    m = len(issues)
    grams_oz = gold.get("grams_per_troy_ounce") or 31.1034768
    spot = gold.get("usd_per_troy_oz") or 0
    ratios = []
    for it in items:
        if it.get("price") and it.get("weight_g"):
            melt = it["weight_g"] * it["karat"] / 24 / grams_oz * spot
            ratio = it["price"] / melt
            ratios.append((it["id"], ratio))
            if ratio < 1:
                fail("melt", f"{it['id']}: price {it['price']} is BELOW melt {melt:.2f} - red flag")
    record("Price vs melt sanity check", m)

    # ---------------------------------------------------------- 9 build output
    m = len(issues)
    missing = [n for n in PAGE_NAMES if not (SITE / n).exists()]
    if missing:
        fail("html", f"missing built pages: {missing} - run tools/build_site.py")
    else:
        pages = [SITE / n for n in PAGE_NAMES]
        if len(pages) < 10:
            fail("html", f"only {len(pages)} pages built")
        link_total = 0
        external = 0
        for p in pages:
            txt = p.read_text(encoding="utf-8")
            if "<title>" not in txt:
                fail("html", f"{p.name}: no title")
            if "assets/style.css" not in txt:
                fail("html", f"{p.name}: stylesheet not linked")
            for bad in (">None<", ">nan<", "undefined", "TODO", "{{", "}}"):
                if bad in txt:
                    fail("html", f"{p.name}: contains suspicious token {bad!r}")
            for href in re.findall(r'href="([^"]+)"', txt):
                link_total += 1
                if href.startswith(("http://", "https://", "mailto:", "tel:")):
                    external += 1
                    continue
                if href.startswith("#"):
                    continue
                target = href.split("#")[0]
                if not target:
                    continue
                if not (SITE / target).exists():
                    fail("html", f"{p.name}: broken internal link {href}")
            for anchor in re.findall(r'id="(f-\d{3})"', txt):
                pass
        # every listing row must expose an external official link
        total_rows = 0
        m_rows = len(issues)
        for p in pages:
            txt = p.read_text(encoding="utf-8")
            rows = re.findall(r'<tr class="item-row">(.*?)</tr>', txt, flags=re.S)
            total_rows += len(rows)
            for row in rows:
                if not re.search(r'href="https://[^"]+"', row):
                    fail("html", f"{p.name}: a listing row has no external source link")
        if total_rows != len(items):
            fail("html", f"{total_rows} table rows rendered for {len(items)} items")
        record(f"Every table row carries an official source link ({total_rows} rows)", m_rows)
    record(f"Built site: no broken internal links ({link_total} links, {external} external)", m)

    # ---------------------------------------------------------- 10 coverage report
    m = len(issues)
    with_weight = sum(1 for i in items if i.get("weight_g") is not None)
    with_price = sum(1 for i in items if i.get("price") is not None)
    if with_price < len(items):
        warn("coverage", f"{len(items) - with_price} of {len(items)} rows have no verified price")
    if with_weight < len(items):
        warn("coverage", f"{len(items) - with_weight} of {len(items)} rows have no published gram weight")
    record("Coverage summary", m)

    # ---------------------------------------------------------- write report
    REPORTS.mkdir(exist_ok=True)
    fails = [i for i in issues if i[0] == "FAIL"]
    warns = [i for i in issues if i[0] == "WARN"]
    status = "PASS" if not fails else "FAIL"
    lines = [
        "# QA / hallucination audit",
        "",
        f"- Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Items audited: {len(items)} · flags: {len(flags)} · evidence quotes checked: {quote_count}",
        f"- **RESULT: {status}** — {len(checks)} checks, {len(fails)} failures, {len(warns)} warnings",
        "",
        "## Checks",
        "",
        "| # | Check | Result | Findings |",
        "|---|-------|--------|----------|",
    ]
    for n, (name, st, cnt) in enumerate(checks, 1):
        lines.append(f"| {n} | {name} | {'✅ PASS' if st == 'PASS' else '❌ FAIL'} | {cnt} |")
    lines += ["", "## Failures", ""]
    lines += [f"- {msg}" for _, msg in fails] or ["- none"]
    lines += ["", "## Warnings", ""]
    lines += [f"- {msg}" for _, msg in warns] or ["- none"]
    lines += [
        "",
        "## What this audit proves, and what it does not",
        "",
        "It proves that every published number is present in the stored evidence for that item, that the source URL belongs to the seller, "
        "and that every blank is covered by a flag. It cannot prove the retailer told the truth, and it does not replace an XRF test "
        "or an appraisal after delivery.",
        "",
        "**Run this again after every review pass.** A stale table is the most likely way a wrong number enters this project.",
    ]
    (REPORTS / "qa-report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"RESULT: {status} — {len(checks)} checks, {len(fails)} failures, {len(warns)} warnings")
    for sev, msg in issues:
        if sev == "FAIL":
            print("  FAIL", msg)
    for sev, msg in issues:
        if sev == "WARN":
            print("  WARN", msg)
    print(f"report -> {REPORTS/'qa-report.md'}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
