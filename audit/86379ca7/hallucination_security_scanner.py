#!/usr/bin/env python3
"""
Independent Hallucination, Provenance, Cross-Register & Security Scanner
Session S-86379CA7 (2026-10-23 UTC)

Standalone zero-dependency Python 3 verifier that audits:
  1. Front-page & site-wide No-Hallucinations policy + post-review re-check recommendation
  2. Official https:// source link coverage & anchor security on every table row
  3. Field-scoped evidence provenance & null-safety across all 30 root rows
  4. Combined 44-product catalog & 85+ source quote-key provenance
  5. Gold spot reference, NIST 31.1034768 g/ozt melt arithmetic & superseded-quote leakage
  6. Root flag & verification-log referential integrity (including F-031/F-004/F-015/F-016/F-032/F-042 checks)
  7. Cross-register identity, 404-URL, stone-type & currency-strictness audit (dashboard/ vs root)
  8. Static code/HTML/workflow security & self-hosting hygiene
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

NIST_GRAMS_PER_TROY_OZ = 31.1034768

ROOT_HTML_PAGES = [
    "index.html",
    "solid-gold.html",
    "solitaire.html",
    "halo-pave.html",
    "three-stone-vintage.html",
    "18k.html",
    "budget.html",
    "retailers.html",
    "prices.html",
    "flags.html",
    "verification.html",
    "analysis.html",
    "methods.html",
]

KNOWN_404_COMPANION_URLS = {
    "https://www.automicgold.com/products/lab-grown-cushion-diamond-signet-ring",
    "https://mejuri.com/products/bold-lab-grown-diamond-eternity-ring",
    "https://www.vrai.com/engagement-ring/classic-4-prong-solitaire/round-brilliant-yellow-gold-41383090421853",
    "https://mejuri.com/pages/returns-and-exchanges",
    "https://mejuri.com/pages/contact-us",
    "https://www.vrai.com/pages/returns-exchanges",
    "https://www.vrai.com/pages/contact",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_scan(repo_root: Path, strict_cross_register: bool = False) -> Tuple[List[str], List[str], Dict[str, int]]:
    failures: List[str] = []
    warnings: List[str] = []
    metrics: Dict[str, int] = {
        "checks_run": 8,
        "root_html_pages": 0,
        "explore_html_pages": 0,
        "dashboard_html_pages": 0,
        "root_items": 0,
        "catalog_products": 0,
        "dashboard_rings": 0,
    }

    def add_cross_register_issue(msg: str) -> None:
        if strict_cross_register:
            failures.append(msg)
        else:
            warnings.append(msg)

    # -------------------------------------------------------------------------
    # Check 1: No-Hallucinations policy & post-review re-check recommendation
    # -------------------------------------------------------------------------
    for page_name in ROOT_HTML_PAGES:
        p = repo_root / page_name
        if not p.is_file():
            failures.append(f"[Check 1] Missing root HTML page: {page_name}")
            continue
        metrics["root_html_pages"] += 1
        html = p.read_text(encoding="utf-8")
        lower = html.lower()
        if "no hallucination" not in lower:
            failures.append(f"[Check 1] {page_name} is missing the No Hallucinations policy banner/rule")
        if "after every review" not in lower and "look for hallucinations" not in lower:
            failures.append(f"[Check 1] {page_name} is missing the recommendation to check for hallucinations after every review")
        if "flags.html" not in html:
            failures.append(f"[Check 1] {page_name} does not link to flags.html (Flagged for Review)")

    explore_pages = sorted(repo_root.glob("explore/**/*.html"))
    for p in explore_pages:
        metrics["explore_html_pages"] += 1
        html = p.read_text(encoding="utf-8")
        if "no hallucination" not in html.lower():
            failures.append(f"[Check 1] {p.relative_to(repo_root)} is missing No Hallucinations text")

    dashboard_pages = sorted(repo_root.glob("dashboard/*.html"))
    for p in dashboard_pages:
        metrics["dashboard_html_pages"] += 1
        html = p.read_text(encoding="utf-8")
        if "no hallucination" not in html.lower():
            failures.append(f"[Check 1] {p.relative_to(repo_root)} is missing No Hallucinations text")

    # -------------------------------------------------------------------------
    # Check 2: Every table row links to an official https:// source safely
    # -------------------------------------------------------------------------
    all_html_files = (
        [repo_root / name for name in ROOT_HTML_PAGES if (repo_root / name).is_file()]
        + explore_pages
        + dashboard_pages
    )
    tbody_re = re.compile(r"<tbody[^>]*>(.*?)</tbody>", re.DOTALL | re.IGNORECASE)
    tr_re = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
    href_re = re.compile(r'<a\b([^>]*?)\bhref=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)

    for p in all_html_files:
        rel = str(p.relative_to(repo_root))
        html = p.read_text(encoding="utf-8")
        for m_Attr in href_re.finditer(html):
            before, href, after = m_Attr.group(1), m_Attr.group(2).strip(), m_Attr.group(3)
            attrs = f"{before} {after}".lower()
            if href.lower().startswith(("javascript:", "data:", "vbscript:", "http://")):
                failures.append(f"[Check 2] Unsafe or non-HTTPS href in {rel}: {href}")
            if 'target="_blank"' in attrs or "target='_blank'" in attrs:
                if "noopener" not in attrs:
                    failures.append(f"[Check 2] target=_blank link without rel=noopener in {rel}: {href}")

        for tbody in tbody_re.findall(html):
            for idx, tr in enumerate(tr_re.findall(tbody), start=1):
                if "<td" not in tr.lower():
                    continue
                if "https://" not in tr:
                    failures.append(f"[Check 2] Table row #{idx} in {rel} lacks an external https:// official source link")

    # -------------------------------------------------------------------------
    # Check 3: Root 30-row register field-scoped evidence provenance & nulls
    # -------------------------------------------------------------------------
    sg_path = repo_root / "data" / "solid-gold-verified.json"
    if not sg_path.is_file():
        failures.append("[Check 3] Missing data/solid-gold-verified.json")
        return failures, warnings, metrics

    sg_data = load_json(sg_path)
    root_items = list(sg_data.get("items", []))
    for lp in sorted((repo_root / "data" / "listings").glob("*.json")):
        ldata = load_json(lp)
        root_items.extend(ldata.get("items", []))

    metrics["root_items"] = len(root_items)
    if len(root_items) != 30:
        failures.append(f"[Check 3] Expected 30 root items, found {len(root_items)}")

    forbidden_placeholders = {"", "0", "0.0", "n/a", "na", "none", "null", "tbd", "unknown", "unverified"}
    root_by_id = {}
    for item in root_items:
        iid = item.get("id", "<missing>")
        if iid in root_by_id:
            failures.append(f"[Check 3] Duplicate root item ID: {iid}")
        root_by_id[iid] = item

        src_url = item.get("source_url", "")
        if not isinstance(src_url, str) or not src_url.startswith("https://"):
            failures.append(f"[Check 3] {iid} has invalid source_url: {src_url!r}")

        ev_rel = item.get("evidence_file", "")
        ev_path = repo_root / ev_rel if ev_rel else None
        if not ev_path or not ev_path.is_file():
            failures.append(f"[Check 3] {iid} missing evidence_file: {ev_rel!r}")
            ev_text = ""
        else:
            ev_text = ev_path.read_text(encoding="utf-8")
            if src_url not in ev_text:
                failures.append(f"[Check 3] {iid} source_url {src_url} not found in {ev_rel}")

        for num_field in ("karat", "weight_g", "price", "original_price", "width_mm", "depth_mm", "fine_gold_g"):
            val = item.get(num_field)
            if isinstance(val, str) and val.strip().lower() in forbidden_placeholders:
                failures.append(f"[Check 3] {iid}.{num_field} uses string placeholder {val!r} instead of null")
            if isinstance(val, (int, float)) and val <= 0:
                failures.append(f"[Check 3] {iid}.{num_field} has non-positive number {val!r} (blank must be null, never 0)")

        if item.get("fine_gold_g") is not None:
            failures.append(f"[Check 3] {iid}.fine_gold_g must be null (no physical assay performed)")

        if item.get("hallmark_verified") is not None or item.get("makers_mark_verified") is not None:
            failures.append(f"[Check 3] {iid} claims hallmark/makers_mark verification without physical inspection")

        price = item.get("price")
        if price is not None:
            if item.get("currency") != "USD":
                failures.append(f"[Check 3] {iid} assigns numeric price {price} without currency=='USD'")
            price_ev = " | ".join(item.get("field_evidence", {}).get("price", []))
            int_str = f"{int(price):,}"
            plain_str = f"{price:.2f}" if price % 1 else f"{int(price)}"
            if int_str not in price_ev and plain_str not in price_ev and str(price) not in price_ev:
                failures.append(f"[Check 3] {iid} price {price} not reflected in field_evidence.price {price_ev!r}")
            if ev_text and int_str not in ev_text and plain_str not in ev_text and str(price) not in ev_text:
                failures.append(f"[Check 3] {iid} price {price} not found in evidence file {ev_rel}")

        weight_g = item.get("weight_g")
        if weight_g is not None and ev_text:
            w_candidates = {str(weight_g), f"{weight_g:.2f}", f"{weight_g:.1f}"}
            if float(weight_g).is_integer():
                w_candidates.add(str(int(weight_g)))
            if not any(w in ev_text for w in w_candidates):
                failures.append(f"[Check 3] {iid} weight_g {weight_g} not found in evidence file {ev_rel}")

    # -------------------------------------------------------------------------
    # Check 4: Combined 44-product catalog & evidence.json quote resolution
    # -------------------------------------------------------------------------
    cat_path = repo_root / "data" / "catalog.json"
    ev_json_path = repo_root / "research" / "evidence.json"
    if not cat_path.is_file() or not ev_json_path.is_file():
        failures.append("[Check 4] Missing data/catalog.json or research/evidence.json")
    else:
        cat_data = load_json(cat_path)
        ev_data = load_json(ev_json_path)
        ev_by_id = {s["id"]: s for s in ev_data.get("sources", [])}
        products = cat_data.get("products", [])
        metrics["catalog_products"] = len(products)
        if len(products) < 44:
            failures.append(f"[Check 4] Expected at least 44 products in data/catalog.json, found {len(products)}")

        cat_urls = set()
        for prod in products:
            pid = prod.get("id", "<missing>")
            src_id = prod.get("source")
            if src_id not in ev_by_id:
                failures.append(f"[Check 4] catalog product {pid} references missing source {src_id!r}")
                continue
            src_obj = ev_by_id[src_id]
            cat_urls.add(src_obj.get("url", ""))
            facts = prod.get("facts", {})
            if facts.get("netMetalWeightG") is not None or facts.get("fineGoldWeightG") is not None:
                failures.append(f"[Check 4] catalog product {pid} asserts netMetalWeightG/fineGoldWeightG without physical test")
            if facts.get("independentTest") is not None:
                failures.append(f"[Check 4] catalog product {pid} asserts independentTest without physical assay")

            price_obj = prod.get("price")
            if price_obj and price_obj.get("amount") is not None:
                amt = price_obj["amount"]
                ev_list = price_obj.get("evidence", [])
                if not ev_list:
                    failures.append(f"[Check 4] catalog product {pid} has price {amt} without evidence references")
                for ref in ev_list:
                    r_src = ev_by_id.get(ref.get("source"))
                    r_q = (r_src or {}).get("quotes", {}).get(ref.get("quote"))
                    if not r_q:
                        failures.append(f"[Check 4] catalog product {pid} price quote ref {ref} does not resolve")

        for iid, ritem in root_by_id.items():
            if ritem["source_url"] not in cat_urls:
                failures.append(f"[Check 4] Root item {iid} URL {ritem['source_url']} missing from data/catalog.json")

    # -------------------------------------------------------------------------
    # Check 5: Gold spot reference, NIST arithmetic & superseded-quote leakage
    # -------------------------------------------------------------------------
    gp_path = repo_root / "data" / "gold-price.json"
    dgp_path = repo_root / "dashboard" / "data" / "gold-reference.json"
    if not gp_path.is_file() or not dgp_path.is_file():
        failures.append("[Check 5] Missing data/gold-price.json or dashboard/data/gold-reference.json")
    else:
        gp = load_json(gp_path)
        dgp = load_json(dgp_path)
        spot_root = gp["usd_per_troy_oz"]
        spot_dash = dgp["spot_usd_per_troy_oz"]
        if abs(spot_root - spot_dash) > 1e-6:
            failures.append(
                f"[Check 5] Spot mismatch between data/gold-price.json ({spot_root}) and dashboard/data/gold-reference.json ({spot_dash})"
            )
        nist_root = gp["grams_per_troy_ounce"]
        if abs(nist_root - NIST_GRAMS_PER_TROY_OZ) > 1e-9:
            failures.append(f"[Check 5] Invalid NIST constant in data/gold-price.json: {nist_root}")

        expected_fine_g = spot_dash / NIST_GRAMS_PER_TROY_OZ
        if abs(dgp["usd_per_fine_gram"] - expected_fine_g) > 1e-3:
            failures.append(
                f"[Check 5] dashboard/data/gold-reference.json usd_per_fine_gram={dgp['usd_per_fine_gram']} != {expected_fine_g:.5f}"
            )

        # Verify superseded quotes do not leak into rendered HTML pages
        superseded = [
            f"{obs['value']:,.2f}"
            for obs in gp.get("superseded_observations", [])
            if "value" in obs
        ]
        for p in all_html_files:
            rel = str(p.relative_to(repo_root))
            html = p.read_text(encoding="utf-8")
            for sup_str in superseded:
                if sup_str in html:
                    failures.append(f"[Check 5] Superseded gold quote {sup_str} leaked into rendered page {rel}")

        # Verify prices.html conditional melt table matches NIST arithmetic
        prices_html = (repo_root / "prices.html").read_text(encoding="utf-8")
        for iid, ritem in root_by_id.items():
            if ritem.get("weight_g") is not None and ritem.get("karat") is not None:
                w = float(ritem["weight_g"])
                k = float(ritem["karat"])
                fine_g = w * (k / 24.0)
                melt_usd = fine_g / NIST_GRAMS_PER_TROY_OZ * spot_root
                expected_melt_str = f"${melt_usd:,.2f}"
                if expected_melt_str not in prices_html:
                    failures.append(
                        f"[Check 5] prices.html missing expected melt {expected_melt_str} for {iid} ({w}g {int(k)}K @ ${spot_root:,.2f}/oz)"
                    )

    # -------------------------------------------------------------------------
    # Check 6: Root flags.json & verification-log.json referential integrity
    # -------------------------------------------------------------------------
    flags_path = repo_root / "data" / "flags.json"
    vlog_path = repo_root / "data" / "verification-log.json"
    if not flags_path.is_file() or not vlog_path.is_file():
        failures.append("[Check 6] Missing data/flags.json or data/verification-log.json")
    else:
        flags_data = load_json(flags_path).get("flags", [])
        vlog_data = load_json(vlog_path)
        flags_by_id = {f["id"]: f for f in flags_data}

        for iid, ritem in root_by_id.items():
            for fid in ritem.get("flags", []):
                if fid not in flags_by_id:
                    failures.append(f"[Check 6] Root item {iid} references non-existent flag {fid}")

        for fobj in flags_data:
            fid = fobj["id"]
            for aid in fobj.get("affected_items", []):
                if aid not in root_by_id:
                    failures.append(f"[Check 6] Flag {fid} references unknown affected_item {aid}")

        # Specific cross-reference checks uncovered by S-86379CA7
        f031 = flags_by_id.get("F-031")
        if f031:
            wrong_f031 = [
                aid
                for aid in f031.get("affected_items", [])
                if root_by_id.get(aid, {}).get("retailer_id") not in set(f031.get("affected_retailers", []))
            ]
            if wrong_f031:
                add_cross_register_issue(
                    f"[Check 6 / S8637-F07] F-031 (scoped to {f031.get('affected_retailers')}) lists non-matching items {wrong_f031}"
                )

        f004 = flags_by_id.get("F-004")
        if f004 and "BN-316238" in f004.get("affected_items", []):
            add_cross_register_issue(
                "[Check 6 / S8637-F08] F-004 (Zales V-19957449 rejected snippet) lists BN-316238 in affected_items"
            )

        f015 = flags_by_id.get("F-015")
        if f015 and ("(12 rows)" in f015.get("detail", "") or len(f015.get("affected_items", [])) < 30):
            add_cross_register_issue(
                f"[Check 6 / S8637-F09] F-015 has stale 16-row detail text or omits items ({len(f015.get('affected_items', []))}/30)"
            )

        f016 = flags_by_id.get("F-016")
        if f016 and "Fifteen rows have no numeric band depth/thickness; only VRAI publishes 1.6 mm depth" in f016.get("detail", ""):
            add_cross_register_issue(
                "[Check 6 / S8637-F09] F-016.detail still states 16-row width/depth counts ('only VRAI publishes 1.6 mm depth')"
            )

        for entry in vlog_data.get("entries", []):
            eid = entry.get("id")
            note = entry.get("note", "")
            for ref_fid in re.findall(r"\bF-\d{3}\b", note):
                if ref_fid not in flags_by_id:
                    add_cross_register_issue(
                        f"[Check 6 / S8637-F10] verification-log entry {eid} references removed flag {ref_fid} in note"
                    )
            if eid in root_by_id and entry.get("label") != root_by_id[eid].get("name"):
                add_cross_register_issue(
                    f"[Check 6 / S8637-F10] verification-log entry {eid} label {entry.get('label')!r} != item name {root_by_id[eid].get('name')!r}"
                )

    # -------------------------------------------------------------------------
    # Check 7: Companion dashboard vs Root Register cross-check
    # -------------------------------------------------------------------------
    drings_path = repo_root / "dashboard" / "data" / "rings.json"
    dret_path = repo_root / "dashboard" / "data" / "retailers.json"
    if drings_path.is_file() and dret_path.is_file():
        drings = load_json(drings_path).get("rings", [])
        dret = load_json(dret_path).get("retailers", [])
        metrics["dashboard_rings"] = len(drings)

        for d in drings:
            did = d.get("id")
            durl = d.get("product_url", "")
            if durl in KNOWN_404_COMPANION_URLS:
                add_cross_register_issue(
                    f"[Check 7 / S8637-F02] dashboard/data/rings.json {did} uses confirmed-404 URL {durl}"
                )
            if did == "AG-SAPPHIRE-RING" and "lab sapphire" in d.get("name", "").lower():
                add_cross_register_issue(
                    "[Check 7 / S8637-F01] dashboard/data/rings.json AG-SAPPHIRE-RING says 'Lab Sapphire' vs official PDP 'Natural sapphire'"
                )
            if did == "AG-24K" and "40.4%" in d.get("price_note", ""):
                add_cross_register_issue(
                    "[Check 7 / S8637-F06] dashboard/data/rings.json AG-24K.price_note hardcodes stale '40.4% pure bullion share'"
                )
            if did in root_by_id:
                r = root_by_id[did]
                if durl != r["source_url"]:
                    add_cross_register_issue(
                        f"[Check 7 / S8637-F03] {did} URL mismatch: dashboard={durl} vs root={r['source_url']}"
                    )
                if d.get("price_usd") is not None and r.get("price") is None:
                    add_cross_register_issue(
                        f"[Check 7 / S8637-F04] {did} assigns price_usd={d.get('price_usd')} in dashboard while root price is null (currency/identity unconfirmed)"
                    )

        for r in dret:
            rid = r.get("id")
            for ufield in ("site_url", "contact_url", "returns_url", "jewelry_notes_url", "bbb_url"):
                uval = r.get(ufield, "")
                if uval in KNOWN_404_COMPANION_URLS:
                    add_cross_register_issue(
                        f"[Check 7 / S8637-F02] dashboard/data/retailers.json {rid}.{ufield} uses confirmed-404 URL {uval}"
                    )
            if rid == "automic-gold" and "B-" in r.get("bbb_summary", ""):
                add_cross_register_issue(
                    "[Check 7 / S8637-F05] dashboard/data/retailers.json automic-gold asserts unverified 'B-' BBB rating"
                )
            if rid == "mejuri" and "F rating" in r.get("bbb_summary", ""):
                add_cross_register_issue(
                    "[Check 7 / S8637-F05] dashboard/data/retailers.json mejuri asserts unverified 'F' BBB rating"
                )

    # -------------------------------------------------------------------------
    # Check 8: Static security & workflow hygiene
    # -------------------------------------------------------------------------
    inline_handler_re = re.compile(r"\bon(?:click|load|error|mouseover|focus|submit|change|input|keyup|keydown)\s*=", re.IGNORECASE)
    ext_script_re = re.compile(r'<script\b[^>]*\bsrc=["\']https?://', re.IGNORECASE)
    ext_style_re = re.compile(r'<link\b[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\']https?://', re.IGNORECASE)
    secret_re = re.compile(r"(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16})")

    for p in all_html_files:
        rel = str(p.relative_to(repo_root))
        html = p.read_text(encoding="utf-8")
        if inline_handler_re.search(html):
            failures.append(f"[Check 8] Inline DOM event handler found in {rel}")
        if ext_script_re.search(html):
            failures.append(f"[Check 8] External runtime <script src=http...> found in {rel}")
        if ext_style_re.search(html):
            failures.append(f"[Check 8] External runtime stylesheet found in {rel}")
        if secret_re.search(html):
            failures.append(f"[Check 8] Potential hardcoded secret token found in {rel}")

    for wf in sorted((repo_root / ".github" / "workflows").glob("*.yml")):
        wf_text = wf.read_text(encoding="utf-8")
        if secret_re.search(wf_text):
            failures.append(f"[Check 8] Potential secret token in workflow {wf.name}")

    return failures, warnings, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="S-86379CA7 Independent Hallucination & Security Scanner")
    parser.add_argument("--root", default=".", help="Path to repository root")
    parser.add_argument(
        "--strict-cross-register",
        action="store_true",
        help="Treat cross-register companion/flag drift warnings as hard failures",
    )
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    failures, warnings, metrics = run_scan(repo_root, strict_cross_register=args.strict_cross_register)

    print("========================================================================")
    print("GOLD2 Independent Hallucination, Provenance & Security Scanner (S-86379CA7)")
    print("========================================================================")
    print(
        f"Scanned: {metrics['root_html_pages']} root pages | {metrics['explore_html_pages']} explore pages | "
        f"{metrics['dashboard_html_pages']} dashboard pages | {metrics['root_items']} root items | "
        f"{metrics['catalog_products']} catalog items | {metrics['dashboard_rings']} companion rings"
    )
    print(f"Checks run: {metrics['checks_run']} | Hard failures: {len(failures)} | Advisory warnings: {len(warnings)}")
    for w in warnings:
        print(f"  WARN: {w}")
    for f in failures:
        print(f"  FAIL: {f}")

    if failures:
        print("RESULT: FAIL — resolve hard failures before merging.")
        return 1
    print("RESULT: PASS — 0 hard failures. Keep looking for hallucinations after every review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
