#!/usr/bin/env python3
"""Deterministic builder for the GOLD2 Solid-Gold Engagement Ring Dashboard (`dashboard/`).

Generates from canonical, dated primary-source records (no network request):
  - `dashboard/data/{gold-reference,retailers,flags,rings}.json`
  - `dashboard/evidence/{rings,retailers}.md`
  - 14 accessible, CSP-hardened HTML pages:
      * `index.html` (Front-page Executive Summary + prominent No-Hallucinations Banner)
      * 6 category subpages (`solid-gold.html`, `solitaire.html`, `halo-pave.html`,
        `three-stone-vintage.html`, `high-karat.html`, `budget.html`)
      * `rings.html` (Filterable all-listings comparison matrix)
      * `calculator.html` (Conditional g/dwt/ozt + gemstone carat deduction calculator)
      * `retailers.html` (11 source-linked sellers + policy/reputation evidence)
      * `checklist.html` (12-point solid-gold buying checklist & walk-away rules)
      * `flagged.html` (Flagged for Review register with official source links)
      * `methodology.html` & `reference.html` (Standards, anti-hallucination protocol & QA)
"""

from __future__ import annotations

import html
import json
from decimal import Decimal
from pathlib import Path

from canonical import build_gold_reference, build_retailers, build_rings

DASH_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = DASH_DIR.parent
DATA_DIR = DASH_DIR / "data"
EVIDENCE_DIR = DASH_DIR / "evidence"

GOLD_REFERENCE = build_gold_reference(REPO_ROOT)
TROY_OZ_G = Decimal(str(GOLD_REFERENCE["troy_ounce"]["grams"]))
SPOT_USD = Decimal(str(GOLD_REFERENCE["spot_usd_per_troy_oz"]))
VERIFIED_DATE = GOLD_REFERENCE["retrieved_at"]
EXPLORE_PRODUCTS = len(json.loads((REPO_ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))["products"])

CATEGORIES = [
    ("solid-gold", "Explicit Solid Gold", "Editorial group for rows whose canonical record explicitly states solid gold. This is seller wording, not physical authentication; unknown fields remain blank."),
    ("solitaire", "Solitaire Rings", "Solitaire and solitaire-setting research across different stated karats, configurations, and evidence gaps."),
    ("halo-pave", "Halo & Pavé", "Halo, hidden-halo, pavé, and cluster designs; review stone mass, metal-weight scope, and order-specific terms separately."),
    ("three-stone-vintage", "Three-Stone & Signet", "Three-stone, bezel/signet, eternity, and vintage-inspired designs with listing-specific evidence links."),
    ("high-karat", "High-Karat (18K–24K)", "Higher nominal-karat research. Karat/24 supplies a calculation ratio only; it does not establish actual purity or value by itself."),
    ("budget", "Budget / Lower-Price Research", "Editorial grouping only: a row may have no assigned current price, and inclusion is not a claim that every configuration is below a fixed threshold."),
]

RETAILERS = build_retailers(REPO_ROOT)
FLAGS = [
    {
        "id": "DF-001",
        "severity": "high",
        "title": "Stone and Strand `SS-MIA` / `SS-RITA`: Karat Conflict and Final-Sale Findings",
        "detail": "The canonical dated evidence records a 14K specification versus 10K image-alt conflict for SS-MIA and final-sale/non-returnable wording for the linked rows. Raw price displays remain unassigned where ISO currency or configuration support is absent. These rows fail the walk-away rule unless the exact order has a qualifying return after independent verification.",
        "action": "Do not purchase final-sale jewelry without qualifying return rights; require written karat and configuration clarification and preserve the official evidence.",
        "sources": [
            "https://www.stoneandstrand.com/products/the-mia-ring",
            "https://www.stoneandstrand.com/products/the-rita-ring",
            "https://www.stoneandstrand.com/pages/returns-exchanges",
        ],
    },
    {
        "id": "DF-002",
        "severity": "high",
        "title": "Factory Direct Jewelry `FDJ-GR0001`: Weight Scope, Stone Mass, and Reputation Evidence Require Review",
        "detail": "The canonical evidence records a displayed item weight alongside diamond carat weight without confirming a stone-free metal weight. The companion therefore leaves metal-only weight blank and does not subtract stones to create a product fact. Seller solid-gold wording, a stamp, and review/complaint allegations are not independent purity or durability findings; consult the canonical retailer record for current dated metrics and policy terms rather than duplicating them here.",
        "action": "Do not treat solid-gold wording, a stamp, or complaints as proof of durability or purity. Resolve the ambiguous weight and obtain an independent inspection.",
        "sources": [
            "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
            "https://www.factorydirectjewelry.com/return-policy",
            "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648/complaints",
        ],
    },
    {
        "id": "DF-003",
        "severity": "high",
        "title": "Missing Metal Weight in Grams on Mainstream Settings (`Blue Nile`, `Brilliant Earth`, `Mejuri`, `Zales`, `Stone & Strand`, `Menē` PDP)",
        "detail": "Most mass-market engagement ring PDPs omit gram weight entirely (`weight_g: null`). Under the No-Hallucinations Policy, missing weights are never estimated from band width.",
        "action": "Request size-specific metal gram weight in writing from customer support before checkout, then verify on an independent jeweler's calibrated scale upon arrival.",
        "sources": [
            "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
            "https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/",
        ],
    },
    {
        "id": "DF-004",
        "severity": "medium",
        "title": "Sarraf Jewelry Inc. (`SAR-*`): Internal Policy Contradictions & Size-10 Weight Benchmark Variance",
        "detail": "The canonical dated Sarraf evidence records policy-wording differences, size-specific weight questions, and buyer-review statements. Review statements are not independent measurements of the selected order, and seller weights are not calibrated-scale results. Consult the linked official product, policy, and reputation evidence for the exact dated wording; this flag does not duplicate mutable amounts or metrics.",
        "action": "Confirm exact gram weight for your ring size in writing before ordering, avoid engraving before XRF/scale inspection, and pay by credit card.",
        "sources": [
            "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html",
            "https://www.sarraf.com/about-sarraf/",
            "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977/customer-reviews",
        ],
    },
    {
        "id": "DF-005",
        "severity": "medium",
        "title": "Gross Item Weight vs Stone-Free Metal Weight (`AG-SAPPHIRE-RING`, `AV-BRIDGE`, `AV-CLEAN`)",
        "detail": "The canonical evidence distinguishes seller-reported metal weight from gross gemstone-ring item weight and selected-size ranges. The companion uses only a supported single metal weight in calculations; gross displays and ranges remain explanatory text, never an inferred product fine-gold mass.",
        "action": "Use the gemstone carat deduction input (`1 ct = 0.200 g`) in the calculator when weighing set rings; never plug gross stone+metal mass directly into pure alloy melt.",
        "sources": [
            "https://www.automicgold.com/products/sapphire-ring",
            "https://auvere.com/product/diamond-bridge-ring-tall/",
        ],
    },
    {
        "id": "DF-006",
        "severity": "medium",
        "title": "Zales Currency and Price-Label Render Instability",
        "detail": "Dated captures across the four canonical Zales rows alternate between labeled and unlabeled displays. The companion preserves raw displays only as unassigned text and leaves structured price/currency blank because the captured pages do not establish an ISO currency. It does not choose current/original roles from amount position.",
        "action": "Keep every Zales amount unassigned until the exact selected configuration, price role, and native currency are confirmed on the official page and at checkout.",
        "sources": [
            "https://www.zales.com/12-ct-tw-multidiamond-cushion-frame-engagement-ring-10k-gold/p/V-20046552",
            "https://www.zales.com/12-ct-tw-diamond-frame-vintagestyle-twist-shank-engagement-ring-10k-gold/p/V-20303279",
        ],
    },
    {
        "id": "DF-007",
        "severity": "low",
        "title": "Zero Physical XRF or Calibrated Scale Assays Performed Remotely",
        "detail": "The registers contain dated web observations with different re-read coverage. No physical ring, stamp, purity, or scale measurement was independently examined. Seller text and stamps can differ from the delivered piece.",
        "action": "Upon arrival — before wearing, resizing, or removing tags — ask an independent jeweler to weigh the ring and select an appropriate purity assessment, potentially including XRF and additional tests where surface readings are insufficient.",
        "sources": [
            "https://www.gia.edu/gems-gemology/summer-2025-lab-notes-gold-plated-gold",
            "https://www.gold.org/goldhub/data/gold-prices",
        ],
    },
    {
        "id": "DF-008",
        "severity": "high",
        "title": "BN-316238 Product-Identity Mismatch; Former Companion Price Removed",
        "detail": "The canonical 2026-10-23 review records that this URL served 'Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen', stock 505097w14, rather than the stored Petite Micropavé record. An earlier companion row nevertheless assigned $1,240 USD to BN-316238. The companion now follows the canonical blank price and does not attach the served amount to the stored item. This is a documentation correction, not a claim about a current offer.",
        "action": "Do not use the stored row for a purchase decision. Reopen the official URL, resolve the product identity and configuration, and review canonical F-041/F-042 before considering any amount.",
        "sources": [
            "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238",
        ],
    },
    {
        "id": "DF-009",
        "severity": "medium",
        "title": "Unconfirmed Seller Fields Stay Blank",
        "detail": "The companion seller table is generated from canonical records and leaves unsupported return windows, payment methods, contact details, and independent-reputation fields blank. In particular, the combined Menē record does not establish a return window; an earlier companion value is not repeated. Blank is an evidence gap, not a negative finding about a seller.",
        "action": "Obtain the exact order's return, payment, contact, and independent-inspection terms in writing. Review the linked canonical evidence and do not treat a generic policy or review profile as order-specific permission.",
        "sources": [
            "https://mene.com/customer-care",
            "https://www.vrai.com/pages/returns-exchanges",
            "https://www.zales.com/return-policy",
        ],
    },
    {
        "id": "DF-010",
        "severity": "high",
        "title": "Explicit Solid-Gold Wording Is Not Confirmed",
        "detail": "Karat alone does not meet this project's qualifying-ring rule. A row with blank or false explicit-solid-gold status is not represented as qualifying, even when a nominal karat calculation is possible. Plated, vermeil, filled, overlay, and gold-tone items do not qualify.",
        "action": "Require explicit solid-gold wording for the exact product and configuration, then independently verify the delivered piece; do not infer solid gold from a karat stamp.",
        "sources": [
            "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry",
            "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
        ],
    },
    {
        "id": "DF-011",
        "severity": "medium",
        "title": "Configuration-Specific ISO-USD Price Is Unassigned",
        "detail": "The structured price is blank because the canonical record does not support an assigned positive USD amount for the exact item/configuration. A raw dollar display may be retained only as unassigned text; it is not converted into a current price by position, guesswork, or formatting.",
        "action": "Reopen the official listing, select the exact configuration, confirm native currency and price scope, and save dated evidence before using any amount in a purchase comparison.",
        "sources": [
            "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
            "https://www.zales.com/12-ct-tw-multidiamond-cushion-frame-engagement-ring-10k-gold/p/V-20046552",
        ],
    },
]

RINGS = build_rings(REPO_ROOT)
CHECKLIST_ITEMS = [
    ("Gold purity (karat)", "Confirm the exact stated karat (10K, 14K, 18K, 22K, or 24K). Karat/24 is a nominal calculation ratio, not an assay; seller-declared decimal fineness is a separate input.", "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3"),
    ("Explicit 'solid gold' wording", "Require explicit solid-gold wording on the exact product page. Do not substitute plating, vermeil, gold-filled, overlay, or gold-tone wording, and do not infer solid gold from karat alone.", "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry"),
    ("Hallmark + maker's mark", "Look for a karat quality mark and the accompanying manufacturer responsibility/trademark evidence required by the cited marking rules. A stamp alone does not prove actual purity.", "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8"),
    ("Ring weight in grams (metal-only)", "Request the selected-size metal weight in grams, excluding stones and non-gold components. Never infer grams from bandwidth or substitute gemstone carats; 1 ct = 0.200 g is a mass conversion, not a purity test.", "https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf"),
    ("Seller reputation & contact", "Research independent reviews and complaints and verify real contact information. Review scores and allegations are not authenticity findings; no call or email is treated as completed unless documented.", "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry"),
    ("Price vs raw gold melt value", "For a documented metal-only weight, compare the exact configuration's native-currency price with conditional `metal_g × nominal_fineness × dated_spot / 31.1034768` arithmetic. An unusually cheap price is a review flag, not proof of plating or a guaranteed resale floor.", "https://www.gold.org/goldhub/data/gold-prices"),
    ("Return policy & resizing traps", "Confirm the exact order's return deadline, refund method, fees, and exclusions for resizing, customization, engraving, alteration, and final sale. Do not substitute a generic banner for order-specific eligibility.", "https://www.stoneandstrand.com/pages/returns-exchanges"),
    ("Credit card purchase protection", "Prefer a credit card for applicable purchase protection and avoid irreversible payment methods. Card-network acceptance and dispute outcomes are not guaranteed.", "https://consumer.ftc.gov/articles/online-shopping"),
    ("Save written pre-purchase documentation", "Preserve the dated listing, URL, selected configuration, seller claims, receipt, and correspondence. Screenshots support later comparison but do not authenticate the metal.", "https://consumer.ftc.gov/articles/online-shopping"),
    ("Post-arrival independent jeweler inspection", "Before wearing, resizing, engraving, or removing tags, ask an independent jeweler to inspect the piece and verify its weight and markings. Do not perform a test that voids return eligibility.", "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry"),
    ("Professional purity testing", "Ask for XRF or another professional gold-purity assessment. Surface XRF can be misleading for gold-over-gold construction, so a professional must decide whether additional testing is needed.", "https://www.gia.edu/gems-gemology/summer-2025-lab-notes-gold-plated-gold"),
    ("Walk-away rule", "Do not buy if the seller will not permit independent verification and a qualifying return. Missing evidence remains a reason to ask questions, not permission to invent an answer.", "https://www.stoneandstrand.com/products/the-mia-ring"),
]

def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def ext(url: str, label: str) -> str:
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}&nbsp;↗</a>'


def cell(value) -> str:
    return esc(value) if value not in (None, "") else '<span class="blank">— (unconfirmed)</span>'


def optional_ext(url, label: str) -> str:
    return ext(url, label) if url else '<span class="blank">— (no confirmed profile URL)</span>'


def compute_ring_metrics(ring: dict) -> tuple[str, str, str]:
    w = ring.get("weight_g")
    if w is None:
        return "—", "—", "—"
    fine = Decimal(str(w)) * Decimal(ring["karat"]) / Decimal(24)
    melt = fine * (SPOT_USD / TROY_OZ_G)
    fine_str = f"{fine:.3f} g"
    melt_str = f"${melt:,.2f}"
    p = ring.get("price_usd")
    if p is not None:
        mult = Decimal(str(p)) / melt
        share = (melt / Decimal(str(p))) * Decimal(100)
        mult_str = f"{mult:.2f}× ({share:.1f}% nominal gold value)"
    else:
        mult_str = "—"
    return fine_str, melt_str, mult_str


def render_shell(title: str, active: str, body: str, extra_js: list[str] | None = None) -> str:
    nav = [
        ("index.html", "Overview", "index"),
        ("solid-gold.html", "Solid Gold", "solid-gold"),
        ("solitaire.html", "Solitaire", "solitaire"),
        ("halo-pave.html", "Halo & Pavé", "halo-pave"),
        ("three-stone-vintage.html", "Three-Stone", "three-stone-vintage"),
        ("high-karat.html", "18K–24K", "high-karat"),
        ("budget.html", "Under $1.5k", "budget"),
        ("rings.html", "All Rings", "rings"),
        ("calculator.html", "Calculator", "calculator"),
        ("retailers.html", "Retailers & BBB", "retailers"),
        ("checklist.html", "12-Pt Checklist", "checklist"),
        ("flagged.html", "Flagged", "flagged"),
        ("methodology.html", "Methodology", "methodology"),
    ]
    nav_items = []
    for href, lbl, key in nav:
        active_attr = ' class="active" aria-current="page"' if key == active else ""
        nav_items.append(f'<a href="{href}"{active_attr}>{esc(lbl)}</a>')
    nav_html = "".join(nav_items)
    scripts = "".join(f'<script src="assets/{js}" defer></script>' for js in (extra_js or []))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · GOLD2 Source-Linked Ring Dashboard</title>
<meta name="description" content="No-hallucination gold engagement-ring research using dated canonical records and official-source links. Unknown prices, weights, and seller fields remain blank.">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<link rel="stylesheet" href="assets/style.css">
{scripts}
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="site-header">
  <div class="wrap topbar">
    <a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span>GOLD2 Solid-Gold Audit</a>
    <nav class="nav-links" aria-label="Primary navigation">{nav_html}</nav>
  </div>
</header>
<main id="main-content"><div class="wrap">
<section class="policy-banner" aria-labelledby="no-hallucination-heading">
  <span class="policy-pill">Strict No-Hallucinations Policy</span>
  <h2 id="no-hallucination-heading">No hallucinations. No invented prices. Dated evidence; blanks for unknowns.</h2>
  <p>This companion is generated from the canonical root/combined registers and links their stored official-source evidence. It does <strong>not</strong> claim that every page was freshly fetched in this build. Whenever currency, configuration, gram weight, product identity, hallmark details, or seller terms are unconfirmed, the structured field is left <strong>blank (<code>—</code>)</strong> and linked to <a href="flagged.html"><strong>Flagged for Review</strong></a>. <strong>Keep checking for hallucinations after every review pass and site build.</strong></p>
  <p class="sub">Dated WGC header observation: <strong>${SPOT_USD:,.2f} / troy oz</strong> (retrieved {VERIFIED_DATE}; exact header quote time unconfirmed) · <a href="../index.html">Root 13-Page Register</a> · <a href="../explore/index.html">{EXPLORE_PRODUCTS}-Item Evidence Explorer</a> · <a href="reference.html">Standards &amp; Logs</a></p>
</section>
{body}
</div></main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <div><strong>GOLD2 Companion Dashboard</strong> · Canonical dated observations through {VERIFIED_DATE} (UTC) · Reopen official sources before purchase.</div>
    <div>Prefer applicable credit-card protection and obtain independent weight/purity verification within the exact order's return window.</div>
  </div>
</footer>
</body>
</html>
"""


def render_rings_table(rings: list[dict]) -> str:
    rows_html = []
    for r in rings:
        fine_s, melt_s, mult_s = compute_ring_metrics(r)
        if r["solid_gold_explicit"] is True:
            solid_badge = '<span class="badge b-ok">Seller Says Explicit Solid Gold</span>'
        elif r["solid_gold_explicit"] is False:
            solid_badge = '<span class="badge b-bad">Does Not Meet Explicit Solid-Gold Rule</span>'
        else:
            solid_badge = '<span class="badge b-warn">Explicit Solid-Gold Wording Unconfirmed</span>'
        stamp_note = "Karat stamp stated (maker's mark unconfirmed)" if r["hallmark_stated"] else "Physical stamp unconfirmed"
        price_cell = f'<strong>${r["price_usd"]:,.2f} USD</strong>' if r["price_usd"] is not None else '<span class="blank">— (blank)</span>'
        weight_cell = f'<strong>{r["weight_g"]:.2f} g</strong>' if r["weight_g"] is not None else '<span class="blank">— (blank)</span>'
        calc_q = (
            f'calculator.html?w={r["weight_g"]}&k={r["karat"]}'
            + (f'&ask={r["price_usd"]}' if r["price_usd"] is not None else "")
            if r["weight_g"] is not None
            else f'calculator.html?k={r["karat"]}'
        )
        flag_links = " ".join(f'<a href="flagged.html#{f.lower()}">{esc(f)}</a>' for f in r["flags"])
        canonical_links = " ".join(
            f'<a href="../flags.html#{f.lower()}">{esc(f)}</a>' for f in r.get("canonical_flags") or []
        )
        review_links = " ".join(
            f'<a href="../explore/review/#{esc(f)}">{esc(f)}</a>' for f in r.get("review_flags") or []
        )
        rows_html.append(
            f'<tr data-ring-row="1" id="ring-{esc(r["id"].lower())}" data-karat="{r["karat"]}" '
            f'data-solid="{"yes" if r["solid_gold_explicit"] else "no"}" '
            f'data-has-weight="{"yes" if r["weight_g"] is not None else "no"}">'
            f'<td><strong>{esc(r["name"])}</strong><div class="sub">{esc(r["retailer"])} · ID <code>{esc(r["id"])}</code></div></td>'
            f'<td><strong>{r["karat"]}K</strong> ({r["karat"]/24*100:.1f}%)<div>{solid_badge}</div><div class="sub">{esc(stamp_note)}</div></td>'
            f'<td class="num">{weight_cell}<div class="sub">{esc(r["weight_note"])}</div></td>'
            f'<td class="num">{price_cell}<div class="sub">{esc(r["price_note"])}</div></td>'
            f'<td class="num"><strong>{fine_s}</strong><div class="sub">Nominal reference: {melt_s}</div><div class="sub">{mult_s}</div>'
            + ('' if r["solid_gold_explicit"] is True else '<div class="sub">Conditional arithmetic only; not a qualifying-row determination.</div>')
            + '</td>'
            f'<td>{ext(r["product_url"], "Official listing")}<div class="sub">Dated observation: {esc(r["capture_date"])}</div>'
            f'<div class="sub"><a href="{esc(r["evidence_link"])}">{esc(r["evidence_label"])}</a></div>'
            f'<div class="sub"><a href="{esc(calc_q)}">Open in calculator →</a> · Companion flags: {flag_links}</div>'
            + (f'<div class="sub">Canonical flags: {canonical_links}</div>' if canonical_links else "")
            + (f'<div class="sub">Combined findings: {review_links}</div>' if review_links else "")
            + '</td>'
            f"</tr>"
        )
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Listing &amp; Seller</th><th>Purity &amp; Solid Claim</th><th class=\"num\">Metal Weight (g)</th>"
        f"<th class=\"num\">Observed Price</th><th class=\"num\">Nominal Fine Gold &amp; Melt (${SPOT_USD:,.2f}/oz)</th>"
        "<th>Official Source &amp; Audit</th>"
        "</tr></thead><tbody>" + "".join(rows_html) + "</tbody></table></div>"
    )


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write structured JSON data files
    (DATA_DIR / "gold-reference.json").write_text(json.dumps(GOLD_REFERENCE, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "retailers.json").write_text(json.dumps({"retrieved_at": VERIFIED_DATE, "retailers": RETAILERS}, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "flags.json").write_text(json.dumps({"retrieved_at": VERIFIED_DATE, "flags": FLAGS}, indent=2) + "\n", encoding="utf-8")
    (DATA_DIR / "rings.json").write_text(json.dumps({"retrieved_at": VERIFIED_DATE, "rings": RINGS}, indent=2) + "\n", encoding="utf-8")

    # 2. Write evidence pointers and exact stored passages. This build is not a fresh fetch.
    rings_ev = [
        f"# Dashboard Canonical Ring Evidence (observations through `{VERIFIED_DATE}`)\n",
        "These passages are copied from the existing canonical evidence records. "
        "The companion build performs no network request and does not refresh observation dates.\n",
    ]
    for r in RINGS:
        rings_ev.append(
            f"## {r['id']} — {r['name']}\n"
            f"- Official URL: {r['product_url']}\n"
            f"- Observation date: `{r['capture_date'] or 'unconfirmed'}`\n"
            f"- Canonical evidence: {r['evidence_link']}\n"
            f"- Verification scope: `{r['verification_status']}`\n"
            "### Stored product-name passage\n\n```text\n"
            f"{r['quote']}\n```\n"
        )
        for field in ("price_quotes", "currency_quotes", "weight_quotes"):
            for quote in r[field]:
                rings_ev.append(f"### Stored {field.replace('_', ' ')} passage\n\n```text\n{quote}\n```\n")
    (EVIDENCE_DIR / "rings.md").write_text("\n".join(rings_ev), encoding="utf-8")

    ret_ev = [
        f"# Dashboard Canonical Seller Evidence (observations through `{VERIFIED_DATE}`)\n",
        "Summaries are generated from canonical structured records. Blank fields are unconfirmed; "
        "review-platform allegations are not established facts or physical tests.\n",
    ]
    for ret in RETAILERS:
        ret_ev.append(
            f"## {ret['id']} — {ret['name']}\n"
            f"- Official Site: {ret['site_url']}\n"
            f"- Returns Policy: {ret['returns_url']}\n"
            f"- Canonical evidence: {ret['evidence_link']}\n"
            f"- Observation date: `{ret['capture_date'] or 'unconfirmed'}`\n"
            f"- Return window: `{ret['return_window'] or 'unconfirmed'}`\n"
            f"- Exclusions / policy summary: `{ret['resized_custom_rule'] or 'unconfirmed'}`\n"
            f"- Published contact (not tested): `{ret['contact_summary'] or 'unconfirmed'}` ({ret['contact_url']})\n"
            f"- Payment methods: `{ret['payment_protection'] or 'unconfirmed'}`\n"
            f"- Independent reputation: `{ret['bbb_summary'] or 'unconfirmed'}` ({ret['bbb_url'] or 'no confirmed profile URL'})\n"
            f"- Unverified fields: `{'; '.join(ret['unverified_fields'])}`\n"
        )
    (EVIDENCE_DIR / "retailers.md").write_text("\n".join(ret_ev), encoding="utf-8")

    # 3. Build 14 clean, accessible HTML pages
    solid_count = sum(1 for r in RINGS if r["solid_gold_explicit"])
    weight_count = sum(1 for r in RINGS if r["weight_g"] is not None)
    priced_count = sum(1 for r in RINGS if r["price_usd"] is not None)
    weight_rings = [r for r in RINGS if r["weight_g"] is not None]

    cat_cards_html = "".join(
        f'<a class="card cat-card" href="{cid}.html">'
        f'<div class="eyebrow">{sum(1 for r in RINGS if cid in r["categories"])} source-linked listings</div>'
        f'<div class="cat-title">{esc(clabel)} →</div>'
        f'<div class="sub">{esc(cdesc)}</div></a>'
        for cid, clabel, cdesc in CATEGORIES
    )

    checklist_preview = "".join(
        f'<tr><td><strong>{idx:02d}. {esc(title)}</strong></td><td>{esc(desc)}</td><td>{ext(url, "Official reference")}</td></tr>'
        for idx, (title, desc, url) in enumerate(CHECKLIST_ITEMS, 1)
    )

    index_body = f"""
<div class="eyebrow">Executive Research Overview · Canonical observations through {VERIFIED_DATE}</div>
<h1>Solid Gold Engagement Ring Buying Guide &amp; Conditional Price-to-Melt Dashboard</h1>
<p class="lead">Comparing <strong>{len(RINGS)} source-linked listings</strong> across <strong>{len(RETAILERS)} jewelry sellers</strong> against our 12-point solid-gold buying checklist, NIST precious-metals conversion constants, and a dated World Gold Council header observation (<strong>${SPOT_USD:,.2f} / troy oz</strong>). This is not a live price feed.</p>

<div class="grid g4">
  <div class="card"><div class="stat-val">{len(RINGS)}</div><div class="stat-lbl">Source-linked companion listings (records through {VERIFIED_DATE})</div></div>
  <div class="card"><div class="stat-val">{solid_count} / {len(RINGS)}</div><div class="stat-lbl">Explicitly state <em>Solid Gold</em> on PDP</div></div>
  <div class="card"><div class="stat-val">{weight_count} / {len(RINGS)}</div><div class="stat-lbl">Publish metal-only weight in grams (<code>g</code>)</div></div>
  <div class="card"><div class="stat-val">{len(FLAGS)}</div><div class="stat-lbl">Irregularities &amp; policy traps on <a href="flagged.html">Flagged</a></div></div>
</div>

<h2>Browse by Engagement Ring Category</h2>
<div class="grid g3">{cat_cards_html}</div>

<h2>Seller-Reported Metal-Weight &amp; Solid-Gold Comparisons ({VERIFIED_DATE})</h2>
<p class="lead">Only seller-reported metal-only gram weights enter these nominal calculations; none is an independent scale result. Every row links to its official seller listing and opens in the <a href="calculator.html">conditional gold-melt calculator</a>.</p>
{render_rings_table(weight_rings)}

<h2>12-Point Solid Gold Online Buying Checklist</h2>
<div class="table-wrap"><table><thead><tr><th>Checklist Criterion</th><th>Verification Standard</th><th>Official Authority</th></tr></thead><tbody>{checklist_preview}</tbody></table></div>
"""
    (DASH_DIR / "index.html").write_text(render_shell("Executive Overview", "index", index_body), encoding="utf-8")

    # Build all 6 category subpages
    for cid, clabel, cdesc in CATEGORIES:
        sub_rings = [r for r in RINGS if cid in r["categories"]]
        c_body = f"""
<div class="eyebrow">Category Subpage · {len(sub_rings)} Source-Linked Listings</div>
<h1>{esc(clabel)}</h1>
<p class="lead">{esc(cdesc)}</p>
<div class="note-box"><strong>Anti-Hallucination Check:</strong> Unconfirmed weights and unconfirmed currency codes remain blank (<code>—</code>) and link directly to <a href="flagged.html">Flagged for Review</a>. Compare setting-only prices separately from complete diamond rings.</div>
{render_rings_table(sub_rings)}
<p class="mt-16"><a href="index.html">← Back to Executive Overview</a> · <a href="rings.html">Filter all {len(RINGS)} listings →</a></p>
"""
        (DASH_DIR / f"{cid}.html").write_text(render_shell(clabel, cid, c_body), encoding="utf-8")

    # Build rings.html (interactive filterable master table)
    rings_body = f"""
<div class="eyebrow">Master Comparison Register · {priced_count} Priced · {weight_count} Metal-Weight Disclosed</div>
<h1>All {len(RINGS)} Source-Linked Gold Ring Listings (records through {VERIFIED_DATE})</h1>
<p class="lead">Filter by search keyword, karat fineness, explicit <em>Solid Gold</em> wording, or published gram weight. Every single table row links directly to its official retailer page.</p>
<div class="card">
  <div class="filter-bar">
    <div><label class="field-label" for="filter-query">Search seller, ring, or note</label><input id="filter-query" type="search" placeholder="e.g. Sarraf, solitaire, 24k, halo..."></div>
    <div><label class="field-label" for="filter-karat">Gold Karat</label><select id="filter-karat"><option value="all">All Karats (10K–24K)</option><option value="24">24K (99.99–100%)</option><option value="22">22K (91.7%)</option><option value="18">18K (75.0%)</option><option value="14">14K (58.3%)</option><option value="10">10K (41.7%)</option></select></div>
    <div><label class="field-label" for="filter-solid">Explicit "Solid Gold"</label><select id="filter-solid"><option value="all">All Listings</option><option value="yes">Explicit Solid Gold Only</option><option value="no">Missing Phrase (Flagged)</option></select></div>
    <div><label class="field-label" for="filter-weight">Metal Gram Weight</label><select id="filter-weight"><option value="all">All Listings</option><option value="yes">Disclosed Metal Weight Only</option><option value="no">Missing / Range Weight (Blank)</option></select></div>
  </div>
  <div id="filter-count" class="sub" aria-live="polite">Showing {len(RINGS)} of {len(RINGS)} source-linked listings</div>
</div>
<div class="mt-16">{render_rings_table(RINGS)}</div>
"""
    (DASH_DIR / "rings.html").write_text(render_shell("All Source-Linked Rings", "rings", rings_body, extra_js=["app.js"]), encoding="utf-8")

    # Build calculator.html
    preset_buttons = "".join(
        f'<button type="button" class="preset-btn" data-preset-weight="{r["weight_g"]}" '
        f'data-preset-karat="{r["karat"]}" data-preset-stone="0" '
        f'data-preset-ask="{r["price_usd"] if r["price_usd"] is not None else ""}">'
        f'{esc(r["id"])}: {r["weight_g"]}g {r["karat"]}K'
        + (f' (${r["price_usd"]:,.0f})' if r["price_usd"] is not None else "")
        + "</button>"
        for r in weight_rings
    )
    karat_table_rows = ""
    for k in (10, 14, 18, 22, 24):
        per_g = (Decimal(k) / Decimal(24)) * (SPOT_USD / TROY_OZ_G)
        karat_table_rows += (
            f'<tr><td class="num"><strong>{k}K</strong></td><td class="num">{k/24*100:.2f}%</td>'
            f'<td class="num">${per_g:,.2f} / g</td><td class="num">${per_g*4:,.2f}</td>'
            f'<td class="num">${per_g*8:,.2f}</td>'
            f'<td>{ext(GOLD_REFERENCE["spot_source_url"], "WGC Spot")} · {ext(GOLD_REFERENCE["troy_ounce"]["sources"][1], "NIST PDF")}</td></tr>'
        )
    calc_body = f"""
<div class="eyebrow">NIST OWM Metrology · Dated reference ${SPOT_USD:,.2f} / oz t ({VERIFIED_DATE})</div>
<h1>Gold Weight, Gemstone Mass Deduction &amp; Nominal Spot-Value Calculator</h1>
<p class="lead">Compute nominal fine-gold content and a conditional bullion-reference value from grams (<code>g</code>), pennyweights (<code>dwt</code>), or troy ounces (<code>ozt</code>). The karat input is an assumption until independently tested. For a complete ring with a known total stone weight, enter stone carats (<code>1 ct = 0.200 g</code>) to avoid counting that mass as metal.</p>
<div class="card">
  <div class="filter-bar">
    <div><label class="field-label" for="calc-weight">Measured / Seller-Reported Weight</label><input id="calc-weight" type="number" min="0.01" step="0.01" value=""></div>
    <div><label class="field-label" for="calc-unit">Unit (NIST Exact)</label><select id="calc-unit"><option value="g" selected>Grams (g)</option><option value="dwt">Pennyweights (dwt · 1.55517384g)</option><option value="ozt">Troy Ounces (ozt · 31.1034768g)</option></select></div>
    <div><label class="field-label" for="calc-karat">Assumed Karat (not authenticated)</label><select id="calc-karat"><option value="10">10K (41.67%)</option><option value="14" selected>14K (58.33%)</option><option value="18">18K (75.00%)</option><option value="22">22K (91.67%)</option><option value="24">24K (100.00%)</option></select></div>
    <div><label class="field-label" for="calc-stone-ct">Deduct Set Stones (ct)</label><input id="calc-stone-ct" type="number" min="0" step="0.01" value="0"></div>
    <div><label class="field-label" for="calc-spot">Dated / User-Entered Gold Reference (USD / ozt)</label><input id="calc-spot" type="number" min="1" step="0.01" value="{SPOT_USD:.2f}"></div>
    <div><label class="field-label" for="calc-ask">Retail Price (USD, optional)</label><input id="calc-ask" type="number" min="0" step="0.01" value=""></div>
  </div>
  <div class="preset-row">{preset_buttons}</div>
  <div class="calc-outputs" aria-live="polite">
    <div class="out-box"><div class="k">Net Alloy Mass</div><div class="v" id="out-net-g">—</div><div class="s">Gross mass minus 0.200g/ct stones</div></div>
    <div class="out-box"><div class="k">Pure Fine Gold (24K eq.)</div><div class="v" id="out-pure-g">—</div><div class="s">Net metal × (karat ÷ 24)</div></div>
    <div class="out-box"><div class="k">Nominal Fine-Gold Spot Value</div><div class="v" id="out-melt">—</div><div class="s">Fine g × ($reference ÷ 31.1034768); not a resale offer</div></div>
    <div class="out-box"><div class="k">Retail ÷ Reference Multiple</div><div class="v" id="out-ratio">—</div><div class="s">&lt;1.0× requires source review, not an authenticity diagnosis</div></div>
    <div class="out-box"><div class="k">Nominal Gold-Value Share</div><div class="v" id="out-share">—</div><div class="s">Reference value ÷ retail price (%)</div></div>
  </div>
  <p id="calc-status" class="note-box"></p>
</div>

<h2>{VERIFIED_DATE} Nominal Karat Reference at ${SPOT_USD:,.2f} / Troy Ounce</h2>
<p class="sub">The 4 g and 8 g columns are arithmetic examples, not listing weights. Nominal karat is not independent purity authentication.</p>
<div class="table-wrap"><table><thead><tr><th class="num">Karat</th><th class="num">Nominal Purity</th><th class="num">Melt / Gram Alloy</th><th class="num">4.00 g Ring Melt</th><th class="num">8.00 g Ring Melt</th><th>Official Standards</th></tr></thead><tbody>{karat_table_rows}</tbody></table></div>
"""
    (DASH_DIR / "calculator.html").write_text(render_shell("NIST Melt Calculator", "calculator", calc_body, extra_js=["calculator.js"]), encoding="utf-8")

    # Build retailers.html
    ret_rows = "".join(
        f'<tr id="ret-{esc(r["id"])}">'
        f'<td><strong>{esc(r["name"])}</strong><div class="sub">{ext(r["site_url"], "Official website")}</div>'
        f'<div class="sub"><a href="{esc(r["evidence_link"])}">{esc(r["evidence_label"])}</a></div></td>'
        f'<td>{cell(r["return_window"])}<div class="sub">{ext(r["returns_url"], "Return policy")}</div></td>'
        f'<td>{cell(r["resized_custom_rule"])}</td>'
        f'<td>{cell(r["payment_protection"])}<div class="sub">{cell(r["contact_summary"])} · {ext(r["contact_url"], "Contact page")}</div></td>'
        f'<td>{cell(r["bbb_summary"])}<div class="sub">{optional_ext(r["bbb_url"], "Independent reputation profile")}</div>'
        f'<div class="sub">Unconfirmed: {esc(", ".join(r["unverified_fields"]))}</div></td>'
        f"</tr>"
        for r in RETAILERS
    )
    ret_body = f"""
<div class="eyebrow">Seller Due Diligence · {len(RETAILERS)} Source-Linked Retailers</div>
<h1>Official Return Policies, Exclusions, Published Contacts &amp; Independent Reputation Records</h1>
<p class="lead">Canonical records through {VERIFIED_DATE} separate first-party policy disclosures from independent reputation entries. A blank is unconfirmed, contact details are published rather than tested, and reviews or complaints are not physical authentication.</p>
<div class="table-wrap"><table><thead><tr><th>Seller &amp; Evidence</th><th>Return Window</th><th>Resized / Custom / Sale Exclusions</th><th>Payment &amp; Published Contact</th><th>Independent Reputation</th></tr></thead><tbody>{ret_rows}</tbody></table></div>
"""
    (DASH_DIR / "retailers.html").write_text(render_shell("Retailers & BBB Audit", "retailers", ret_body), encoding="utf-8")

    # Build checklist.html
    chk_body = f"""
<div class="eyebrow">Buyer Protection Protocol</div>
<h1>12-Point Solid Gold Engagement Ring Buying Checklist</h1>
<p class="lead">Follow all 12 steps in sequence — before paying, at checkout, and immediately upon package delivery before wearing or resizing.</p>
<div class="table-wrap"><table><thead><tr><th>Step &amp; Criterion</th><th>Action Required &amp; Red Flags</th><th>Official Source</th></tr></thead><tbody>{checklist_preview}</tbody></table></div>
"""
    (DASH_DIR / "checklist.html").write_text(render_shell("12-Point Buying Checklist", "checklist", chk_body), encoding="utf-8")

    # Build flagged.html
    flag_cards = "".join(
        f'<article class="card flag-card {esc(f["severity"])}" id="{esc(f["id"].lower())}">'
        f'<span class="badge {"b-bad" if f["severity"] == "high" else ("b-warn" if f["severity"] == "medium" else "b-info")}">{esc(f["severity"].upper())} SEVERITY</span> '
        f'<h3>{esc(f["id"])} · {esc(f["title"])}</h3>'
        f'<p>{esc(f["detail"])}</p>'
        f'<p><strong>Recommended Buyer Action:</strong> {esc(f["action"])}</p>'
        f'<div class="sub"><strong>Official Sources:</strong> ' + " · ".join(ext(u, u) for u in f["sources"]) + "</div>"
        f"</article>"
        for f in FLAGS
    )
    flag_body = f"""
<div class="eyebrow">Open Irregularities, Unconfirmed Blanks &amp; Policy Traps</div>
<h1>Flagged for Review ({len(FLAGS)} Active Findings)</h1>
<p class="lead">Under our <strong>No-Hallucinations Policy</strong>, missing specifications are left blank and companion-specific irregularities are published openly here. These {len(FLAGS)} companion findings do not replace the <a href="../flags.html">canonical root Flagged for Review register</a> or the <a href="../explore/review/">combined research findings</a>; each companion ring row links its applicable canonical IDs.</p>
{flag_cards}
"""
    (DASH_DIR / "flagged.html").write_text(render_shell("Flagged for Review", "flagged", flag_body), encoding="utf-8")

    # Build methodology.html & reference.html
    meth_body = f"""
<div class="eyebrow">Verification Architecture &amp; Ongoing Hallucination Guardrails</div>
<h1>Methodology, Metrology Constants &amp; Security Passes</h1>
<p class="lead">The repository's separate review toolchain covers scoped provenance, link integrity, CSP/XSS checks, accessibility, and nominal arithmetic. A build alone does not freshly fetch or re-authenticate a listing.</p>
<div class="note-box"><strong>Ongoing Recommendation:</strong> Automated verification (`PASS`) checks only its stated internal-consistency and security scope. It does <strong>not</strong> guarantee source freshness, the absence of every hallucination, or that a physical ring matches a seller's description. <strong>Continue running hallucination and security passes after every review and edit, and independently inspect source evidence again.</strong></div>
<div class="table-wrap"><table><thead><tr><th>Standard / Pass</th><th>Specification</th><th>Official Source</th></tr></thead><tbody>
<tr><td><strong>Dated World Gold Council Header Observation</strong></td><td><code>${SPOT_USD:,.2f} / troy oz</code> (chart date `{GOLD_REFERENCE['chart_as_of_date']}`, retrieved `{VERIFIED_DATE}`; exact header quote time unconfirmed)</td><td>{ext(GOLD_REFERENCE["spot_source_url"], "gold.org/goldhub/data/gold-prices")}</td></tr>
<tr><td><strong>NIST OWM Mass Constants</strong></td><td><code>1 ozt = 31.1034768 g</code> · <code>1 dwt = 1.55517384 g</code> · <code>1 ct = 0.200 g</code></td><td>{ext(GOLD_REFERENCE["troy_ounce"]["sources"][1], "NIST Precious Metals PDF")}</td></tr>
<tr><td><strong>FTC Jewelry Guides</strong></td><td><code>16 CFR § 23.3</code> — karat thresholds, hollow/plated disclosures, tolerance footnotes</td><td>{ext("https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3", "eCFR 16 CFR § 23.3")}</td></tr>
<tr><td><strong>National Stamping Act</strong></td><td><code>15 U.S.C. §§ 294–300</code> — review quality-mark/trademark requirements and applicability; a stamp is not an assay</td><td>{ext("https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8", "GovInfo 15 U.S.C. Ch. 8")}</td></tr>
</tbody></table></div>
"""
    (DASH_DIR / "methodology.html").write_text(render_shell("Methodology & Standards", "methodology", meth_body), encoding="utf-8")
    (DASH_DIR / "reference.html").write_text(render_shell("Reference & Verification Log", "methodology", meth_body), encoding="utf-8")

    print(f"dashboard build complete: 14 HTML pages, {len(RINGS)} rings, {len(RETAILERS)} retailers, {len(FLAGS)} flags.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
