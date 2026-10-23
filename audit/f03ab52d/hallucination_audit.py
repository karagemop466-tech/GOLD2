#!/usr/bin/env python3
"""
Independent hallucination / provenance audit for GOLD2.

Session S-F03AB52D. Written from scratch against the committed data files and
the generated HTML. It deliberately does NOT import tools/qa.py, scripts/verify.mjs,
or any other session's scanner, so a shared bug in one of those cannot mask a
defect here.

Policy enforced (from the project front page):
  * Every published fact must trace to an official source link.
  * A value with no evidence quote is UNVERIFIED -> blank/flag, never inferred.
  * No value is invented, averaged, or arithmetically derived from a neighbour
    and then presented as an observed fact.
  * A stamp/karat claim is not an assay; physical tests are out of scope.

Checks
  C1  source existence + official https URL for every catalog product
  C2  value <-> evidence-quote parity for every non-null fact and price amount
  C3  root register: official source_url + existing evidence_file per item
  C4  root <-> catalog URL parity (same URL, no contradictory price/weight)
  C5  gold reference: JSON value appears in evidence; no unrecorded gold figure
  C6  derived/assay fields stay null unless explicitly evidenced
  C7  no hallmark / maker-mark claim without evidence-file wording
  C8  generated HTML parity for the headline gold value and product count
  C9  review findings cite at least one source

Exit code 0 = no failures (warnings allowed). 1 = at least one failure.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def norm(text):
    """Normalize a string for tolerant matching: unicode NFKC, lower, collapse
    whitespace, strip curly quotes."""
    if text is None:
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = t.replace("\u00a0", " ")
    t = re.sub(r"[\u2018\u2019\u201c\u201d]", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def number_variants(x):
    """All the ways a number may be written in a quote: 1910, 1,910, $1,910,
    0.9999 / 99.99%. Comma-grouped and percentage forms are included so a
    correctly-backed value is not reported as a mismatch."""
    if isinstance(x, bool):
        return [str(x)]
    if isinstance(x, (int, float)):
        f = float(x)
        out = set()
        for fmt in (".0f", ".1f", ".2f", ".3f", ".4f"):
            out.add(format(f, fmt))
            out.add(format(f, "," + fmt))
        out.add(format(f, "g"))
        for s in list(out):
            out.add(s.replace(",", ""))
        # a fraction may be quoted as its percentage
        if 0 < abs(f) < 1:
            pct = format(f * 100, "g")
            out.add(pct)
            out.add(pct + "%")
        return sorted(out)
    return [norm(x)]


def contains_number(quote, value):
    q = norm(quote)
    for v in number_variants(value):
        if v and (v in q or norm(v) in q):
            return True
    return False


def norm_number(x):
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int, float)):
        return format(float(x), "g")
    return norm(x)


# wording required to back a boolean fact (alternatives unless noted)
BOOL_KEYWORDS = {
    "hallmark": ("stamp", "mark", "hallmark", "engrav"),
    "makerMark": ("maker", "manufacturer", "brand", "stamp", "mark"),
    "independentTest": ("test", "assay", "xrf", "verified", "inspect"),
    "independentInspectionReturnPermission": ("return", "inspect", "verify", "test", "appraisal"),
}


def bool_backed(field, val, quote):
    if not val:
        return True
    q = norm(quote)
    if field == "solidGold":
        return "solid" in q and "gold" in q
    kws = BOOL_KEYWORDS.get(field)
    if kws is None:
        return True
    return any(k in q for k in kws)


class Report:
    def __init__(self):
        self.checks = []
        self.failures = 0
        self.warnings = 0

    def add(self, cid, name, status, detail=""):
        self.checks.append({"id": cid, "name": name, "status": status, "detail": detail})
        if status == "FAIL":
            self.failures += 1
        elif status == "WARN":
            self.warnings += 1

    def summary(self):
        return (f"RESULT: {'FAIL' if self.failures else 'PASS'} — "
                f"{len(self.checks)} checks, {self.failures} failures, {self.warnings} warnings")


def run(root=None):
    root = Path(root) if root else DEFAULT_ROOT
    rep = Report()

    def load(rel):
        with open(root / rel, encoding="utf-8") as fh:
            return json.load(fh)

    catalog = load("data/catalog.json")
    evidence = load("research/evidence.json")
    gold = load("data/gold-price.json")
    review = load("data/review.json")
    solid = load("data/solid-gold-verified.json")
    listings = {f: load(f"data/listings/{f}.json")
                for f in ("18k", "budget", "halo-pave", "solitaire", "three-stone-vintage")}

    srcmap = {s["id"]: s for s in evidence["sources"]}
    products = catalog["products"]

    # ------------------------------------------------------------------ C1
    bad_src = []
    for p in products:
        sid = p.get("source")
        s = srcmap.get(sid)
        if s is None:
            bad_src.append((p["id"], sid, "source id not in evidence.json"))
            continue
        url = s.get("url", "")
        if not url.startswith("https://"):
            bad_src.append((p["id"], sid, f"non-https url: {url}"))
        if s.get("kind") == "review-platform":
            bad_src.append((p["id"], sid, f"fact source is a review platform: {url}"))
    status = "PASS" if not bad_src else "FAIL"
    rep.add("C1", "catalog product sources exist and are official https",
            status, "; ".join(f"{i}:{s}:{m}" for i, s, m in bad_src[:8]))

    # ------------------------------------------------------------------ C2
    mismatches = []
    unbacked = []
    for p in products:
        for fk, fv in p["facts"].items():
            if not isinstance(fv, dict):
                continue
            val = fv.get("value")
            if val is None:
                continue
            sid = fv.get("source")
            qk = fv.get("quote")
            s = srcmap.get(sid)
            if s is None:
                unbacked.append((p["id"], fk, sid, "missing source"))
                continue
            quotes = s.get("quotes", {})
            if qk not in quotes:
                unbacked.append((p["id"], fk, f"{sid}/{qk}", "missing quote key"))
                continue
            quote = quotes[qk]
            if isinstance(val, bool):
                if not bool_backed(fk, val, quote):
                    mismatches.append((p["id"], fk, val, quote[:80]))
            elif isinstance(val, (int, float)):
                if not contains_number(quote, val):
                    mismatches.append((p["id"], fk, val, quote[:80]))
            else:
                if norm(val) and norm(val) not in norm(quote):
                    mismatches.append((p["id"], fk, str(val)[:40], quote[:80]))
        # price amount must be present in one of its evidence quotes
        pr = p.get("price")
        if pr and isinstance(pr.get("amount"), (int, float)):
            okp = False
            for ev in pr.get("evidence", []):
                s2 = srcmap.get(ev.get("source"), {})
                q2 = s2.get("quotes", {}).get(ev.get("quote"), "")
                if contains_number(q2, pr["amount"]):
                    okp = True
                    break
            if not okp:
                mismatches.append((p["id"], "price.amount", pr["amount"],
                                   "not found in any price evidence quote"))
    status = "PASS" if not mismatches and not unbacked else "FAIL"
    detail = []
    if mismatches:
        detail.append("value/quote mismatch: " + "; ".join(
            f"{i}/{fk}={v!r} vs {q!r}" for i, fk, v, q in mismatches[:8]))
    if unbacked:
        detail.append("unbacked fact: " + "; ".join(
            f"{i}/{fk}->{s}" for i, fk, s, _ in unbacked[:8]))
    rep.add("C2", "every non-null fact value and price amount is in its evidence quote",
            status, " | ".join(detail))

    # ------------------------------------------------------------------ C3
    root_items = list(solid["items"])
    for lst in listings.values():
        root_items += lst["items"]
    bad_root = []
    for it in root_items:
        url = it.get("source_url", "")
        if not url.startswith("https://"):
            bad_root.append((it["id"], "non-https source_url", url))
        ev = it.get("evidence_file")
        if not ev or not (root / ev).exists():
            bad_root.append((it["id"], "missing evidence_file", str(ev)))
    status = "PASS" if not bad_root else "FAIL"
    rep.add("C3", "root register: official https source_url + existing evidence file",
            status, "; ".join(f"{i}:{m}:{u}" for i, m, u in bad_root[:8]))

    # ------------------------------------------------------------------ C4
    cat_by_url = {}
    for p in products:
        s = srcmap.get(p.get("source"), {})
        cat_by_url.setdefault(s.get("url"), []).append(p)
    conflicts = []
    missing = []
    checked = 0
    for it in root_items:
        url = it.get("source_url")
        matches = cat_by_url.get(url, [])
        if not matches:
            missing.append((it["id"], "root URL not present in combined catalog", url))
            continue
        for p in matches:
            checked += 1
            rprice = it.get("price")
            cprice = (p.get("price") or {}).get("amount")
            if isinstance(rprice, (int, float)) and isinstance(cprice, (int, float)):
                if abs(float(rprice) - float(cprice)) > 1e-6:
                    conflicts.append((it["id"], f"price differs root={rprice} catalog={cprice}", url))
            rw = it.get("weight_g")
            cw = (p.get("reportedWeight") or {}).get("min")
            if isinstance(rw, (int, float)) and isinstance(cw, (int, float)):
                if abs(float(rw) - float(cw)) > 1e-6:
                    conflicts.append((it["id"], f"weight differs root={rw} catalog={cw}", url))
    if conflicts:
        status = "FAIL"
    elif missing:
        status = "WARN"
    else:
        status = "PASS"
    detail = ("; ".join(f"{i}:{m}" for i, m, _ in conflicts[:8])
              or "; ".join(f"{i}:{m}" for i, m, _ in missing[:8])
              or f"{checked} pairs compared")
    rep.add("C4", "root <-> catalog URL parity (price/weight)", status, detail)

    # ------------------------------------------------------------------ C5
    gval = gold.get("usd_per_troy_oz")
    goldmd = (root / "evidence/gold-price.md").read_text(encoding="utf-8")
    ok = contains_number(goldmd, gval)
    superseded_ok = all(
        contains_number(goldmd, obs.get("value"))
        for obs in gold.get("superseded_observations", []))
    recorded = {norm_number(gval)} | {norm_number(o["value"]) for o in gold.get("superseded_observations", [])}
    negations = ("does not exist", "no such figure", "not presented", "removed rather than",
                 "not a recorded", "never was", "invented", "not an observation")
    unrecorded = []
    documented = []
    # comma-aware, alphanumeric-aware number matcher: matches standalone numbers
    # only, so a session id like S-1B04074F is not read as a gold figure.
    num_re = re.compile(r"(?<![A-Za-z0-9.,])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![A-Za-z0-9.,])")
    for line in goldmd.splitlines():
        ln = norm(line)
        is_negation = any(neg in ln for neg in negations)
        for m in num_re.finditer(line):
            num = m.group(1).replace(",", "")
            try:
                f = float(num)
            except ValueError:
                continue
            if 3000 <= f <= 5000:
                if norm_number(f) in recorded or norm(f) in recorded:
                    continue
                (documented if is_negation else unrecorded).append(num)
    status = "PASS" if (ok and superseded_ok and not unrecorded) else "FAIL"
    detail = []
    if not ok:
        detail.append(f"current value {gval} not found in evidence md")
    if not superseded_ok:
        detail.append("a superseded value is missing from the evidence md")
    if unrecorded:
        detail.append("unrecorded gold figure(s) in evidence md: " + ", ".join(sorted(set(unrecorded))))
    if documented:
        detail.append("documented non-observational mention(s) (exempt): " + ", ".join(sorted(set(documented))))
    rep.add("C5", "gold reference JSON matches evidence and has no unrecorded figure",
            status, " | ".join(detail))

    # ------------------------------------------------------------------ C6
    derived_fields = {"fineGoldWeightG", "netMetalWeightG", "declaredPurity",
                      "hallmark", "makerMark", "independentTest",
                      "independentInspectionReturnPermission"}
    bad_derived = []
    for p in products:
        for fk in derived_fields:
            fv = p["facts"].get(fk)
            if isinstance(fv, dict) and fv.get("value") is not None:
                sid = fv.get("source")
                qk = fv.get("quote")
                s = srcmap.get(sid)
                backed = bool(s and s.get("quotes", {}).get(qk))
                if not backed:
                    bad_derived.append((p["id"], fk, fv.get("value")))
    status = "PASS" if not bad_derived else "FAIL"
    rep.add("C6", "derived / assay fields are null unless explicitly evidenced",
            status, "; ".join(f"{i}/{fk}={v}" for i, fk, v in bad_derived[:8]))

    # ------------------------------------------------------------------ C7
    bad_hallmark = []
    for it in root_items:
        ev = it.get("evidence_file")
        evtext = norm((root / ev).read_text(encoding="utf-8")) if ev and (root / ev).exists() else ""
        for fld, kws in (("hallmark_stated", ("stamp", "mark", "hallmark", "engrav")),
                         ("makers_mark_stated", ("maker", "manufacturer", "brand", "stamp"))):
            if it.get(fld) is True and not any(k in evtext for k in kws):
                bad_hallmark.append((it["id"], fld, "claimed true; no matching wording in evidence file"))
    status = "PASS" if not bad_hallmark else "FAIL"
    rep.add("C7", "no hallmark / maker-mark claim without evidence",
            status, "; ".join(f"{i}:{f}" for i, f, _ in bad_hallmark[:8]))

    # ------------------------------------------------------------------ C8
    html_files = list((root).glob("*.html")) + list((root / "explore").rglob("*.html"))
    blob = "".join((f.read_text(encoding="utf-8", errors="ignore") for f in html_files))
    c8a = contains_number(blob, gval)
    c8b = str(len(products)) in blob
    status = "PASS" if (c8a and c8b) else "WARN"
    rep.add("C8", "generated HTML renders the headline gold value and product count",
            status, f"gold_value_rendered={c8a} product_count_rendered={c8b}")

    # ------------------------------------------------------------------ C9
    bad_finding = []
    for fn in review.get("findings", []):
        urls = fn.get("sources") or fn.get("source_urls") or []
        if not urls:
            bad_finding.append(fn.get("id", "?"))
    status = "PASS" if not bad_finding else "WARN"
    rep.add("C9", "review findings cite at least one source",
            status, "findings without source: " + ", ".join(bad_finding[:8]))

    return rep


def main():
    rep = run()
    for c in rep.checks:
        print(f"  [{c['status']:4}] {c['id']} {c['name']}")
        if c["detail"]:
            print(f"         {c['detail']}")
    print(rep.summary())
    out = DEFAULT_ROOT / "audit" / "f03ab52d" / "hallucination_audit_report.json"
    out.write_text(json.dumps({"checks": rep.checks, "failures": rep.failures,
                               "warnings": rep.warnings}, indent=2), encoding="utf-8")
    print(f"report -> {out}")
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
