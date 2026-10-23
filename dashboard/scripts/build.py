#!/usr/bin/env python3
"""Deterministic builder for the GOLD2 Solid-Gold Engagement Ring Dashboard (`dashboard/`).

Generates from verified primary-source records (`2026-10-23` live audit):
  - `dashboard/data/{gold-reference,retailers,flags,rings}.json`
  - `dashboard/evidence/{rings,retailers}.md`
  - 14 accessible, CSP-hardened HTML pages:
      * `index.html` (Front-page Executive Summary + prominent No-Hallucinations Banner)
      * 6 category subpages (`solid-gold.html`, `solitaire.html`, `halo-pave.html`,
        `three-stone-vintage.html`, `high-karat.html`, `budget.html`)
      * `rings.html` (Filterable all-listings comparison matrix)
      * `calculator.html` (Live NIST g/dwt/ozt + gemstone carat deduction melt calculator)
      * `retailers.html` (11 official sellers + BBB profiles + return/resize/payment audit)
      * `checklist.html` (12-point solid-gold buying checklist & walk-away rules)
      * `flagged.html` (Flagged for Review register with official source links)
      * `methodology.html` & `reference.html` (Standards, anti-hallucination protocol & QA)
"""

from __future__ import annotations

import html
import json
from decimal import Decimal
from pathlib import Path

DASH_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = DASH_DIR.parent
DATA_DIR = DASH_DIR / "data"
EVIDENCE_DIR = DASH_DIR / "evidence"

TROY_OZ_G = Decimal("31.1034768")
SPOT_USD = Decimal("4024.45")
VERIFIED_DATE = "2026-10-23"

CATEGORIES = [
    ("solid-gold", "Explicit Solid Gold", "Listings whose primary product page explicitly states solid gold purity (`14K`–`24K`), cross-checked for gram weight, hallmark disclosures, and BBB history."),
    ("solitaire", "Solitaire Rings", "Classic four- and six-prong solitaire diamond engagement rings and settings across `14K` and `18K` gold."),
    ("halo-pave", "Halo & Pavé", "Halo, hidden-halo, twisting pavé, and cluster diamond rings — including thin-shank mass warnings."),
    ("three-stone-vintage", "Three-Stone & Signet", "Three-stone, bezel/signet, eternity, and vintage-inspired gold ring designs."),
    ("high-karat", "High-Karat (18K–24K)", "Higher-purity `18K` (75.0%), `22K` (91.7%), and `24K` (99.99–100%) gold rings with substantially higher intrinsic bullion share."),
    ("budget", "Under $1,500 & Value", "Lower-ticket `10K`/`14K`/`24K` options audited against raw melt value, final-sale traps, and currency disclosures."),
]

GOLD_REFERENCE = {
    "retrieved_at": VERIFIED_DATE,
    "spot_usd_per_troy_oz": 4024.45,
    "chart_as_of_date": "2026-10-22",
    "quote_timestamp_confirmed": False,
    "usd_per_fine_gram": round(float(SPOT_USD / TROY_OZ_G), 6),
    "spot_source_name": "World Gold Council — Goldhub Gold Prices",
    "spot_source_url": "https://www.gold.org/goldhub/data/gold-prices",
    "spot_quotes": ["USD /oz - 4,024.45", "Data as of 22 October, 2026"],
    "troy_ounce": {
        "grams": 31.1034768,
        "pennyweight_grams": 1.55517384,
        "carat_grams": 0.2,
        "sources": [
            "https://www.nist.gov/pml/owm/approximate-conversions-us-customary-measures-metric",
            "https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf",
        ],
    },
    "lbma_price_method": {
        "sources": [
            "https://www.gold.org/goldhub/data/gold-prices",
            "https://www.lbma.org.uk/prices-and-data/precious-metal-prices",
        ]
    },
    "karat_definition": {
        "manual_review_links": [
            "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
        ]
    },
    "hallmark_law": [
        {
            "title": "FTC Guides for the Jewelry Industry — 16 CFR § 23.3 (Misrepresentation as to gold content)",
            "source": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
        },
        {
            "title": "National Stamping Act — 15 U.S.C. §§ 294–300 (3 ppt unsoldered / 7 ppt soldered tolerance; trademark required alongside quality mark)",
            "source": "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8",
        },
    ],
}

RETAILERS = [
    {
        "id": "sarraf",
        "name": "Sarraf Jewelry Inc.",
        "site_url": "https://www.sarraf.com/",
        "contact_url": "https://www.sarraf.com/contact-us/",
        "returns_url": "https://www.sarraf.com/about-sarraf/",
        "jewelry_notes_url": "https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html",
        "bbb_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977",
        "contact_summary": "888-472-7723 · service@sarraf.com · 650 S. Hill St. #728, Los Angeles, CA 90014",
        "return_window": "30 days (unworn; insured signature shipping paid by buyer)",
        "resized_custom_rule": "Third-party resized, altered, or special-order items excluded; internal conflict on engraved rings (product tab vs /about-sarraf/).",
        "payment_protection": "Major credit cards accepted (refunds credited to original card within 7 business days).",
        "bbb_summary": "BBB Accredited Since 3/18/1998 · A+ · 2.33/5 (3 reviews; weight variance disputes noted) · 6 complaints / 3 yrs (0 in 12 mos)",
    },
    {
        "id": "automic-gold",
        "name": "Automic Gold",
        "site_url": "https://www.automicgold.com/",
        "contact_url": "https://www.automicgold.com/pages/help",
        "returns_url": "https://www.automicgold.com/pages/help",
        "jewelry_notes_url": "https://www.automicgold.com/products/coffin-ring",
        "bbb_url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/automic-gold-inc-0121-87150445",
        "contact_summary": "info@automicgold.com · NYC studio",
        "return_window": "14 days from delivery (free US return label; unworn)",
        "resized_custom_rule": "Custom sizes, personalized, and final-sale items excluded from return.",
        "payment_protection": "Credit cards, Shop Pay, PayPal accepted (`cart.js` verified USD).",
        "bbb_summary": "Not BBB Accredited · B- · 0 complaints / 3 yrs",
    },
    {
        "id": "mejuri",
        "name": "Mejuri",
        "site_url": "https://mejuri.com/",
        "contact_url": "https://mejuri.com/pages/contact-us",
        "returns_url": "https://mejuri.com/pages/returns-and-exchanges",
        "jewelry_notes_url": "https://mejuri.com/products/bold-lab-grown-diamond-eternity-ring",
        "bbb_url": "https://www.bbb.org/ca/on/toronto/profile/jewelry-stores/mejuri-0107-1347952",
        "contact_summary": "contact@mejuri.com · Toronto & US retail stores",
        "return_window": "30 days (unworn, original packaging; free returns)",
        "resized_custom_rule": "Engraved, monogrammed, and final-sale pieces non-returnable.",
        "payment_protection": "Credit cards, PayPal, Apple Pay, Klarna accepted.",
        "bbb_summary": "Not BBB Accredited · F rating on BBB Toronto profile · check complaints carefully",
    },
    {
        "id": "stone-and-strand",
        "name": "Stone and Strand",
        "site_url": "https://www.stoneandstrand.com/",
        "contact_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
        "returns_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
        "jewelry_notes_url": "https://www.stoneandstrand.com/products/the-clara-ring",
        "bbb_url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934",
        "contact_summary": "(855) 775-3935 · hello@stoneandstrand.com · NYC",
        "return_window": "100 days less $12.50 fee ONLY on full-price items; >=50% off is Final Sale!",
        "resized_custom_rule": "Made-to-order, custom, engraved, and >=50%-off sale items are strictly Final Sale (blocks return after XRF test!).",
        "payment_protection": "Credit cards & standard checkout; verify non-final-sale status in writing first.",
        "bbb_summary": "Not BBB Accredited · 0 complaints / 3 yrs (NYC file opened 3/26/2020)",
    },
    {
        "id": "auvere",
        "name": "Auvere LLC",
        "site_url": "https://auvere.com/",
        "contact_url": "https://auvere.com/help/auvere-concierge/",
        "returns_url": "https://auvere.com/help/auvere-concierge/",
        "jewelry_notes_url": "https://auvere.com/product/diamond-bridge-ring-tall/",
        "bbb_url": "https://www.bbb.org/us/ny/new-york/profile/online-retailer/auvere-llc-0121-87168132",
        "contact_summary": "(866) 317-7779 · concierge@auvere.com · 485 Lexington Ave #304, NY",
        "return_window": "15 days from delivery (free US return label; tag untouched)",
        "resized_custom_rule": "Altered pieces, removed tags, sale pieces, and Rare Collection excluded.",
        "payment_protection": "Credit card checkout with fraud-prevention verification.",
        "bbb_summary": "Not BBB Accredited · 0 complaints / 3 yrs (NYC file opened 6/21/2023)",
    },
    {
        "id": "mene",
        "name": "Menē",
        "site_url": "https://mene.com/",
        "contact_url": "https://mene.com/customer-care",
        "returns_url": "https://mene.com/customer-care/en-US/articles/returns-319505",
        "jewelry_notes_url": "https://mene.com/products/rose-ring-gold",
        "bbb_url": "https://www.bbb.org/ca/on/toronto/profile/jewelry-designers/mene-0107-1378080",
        "contact_summary": "1-833-MENE-24K · service@mene.com",
        "return_window": "7 days from delivery (tight window — schedule XRF check immediately!)",
        "resized_custom_rule": "Unworn condition required; lifetime buyback program subject to fee terms.",
        "payment_protection": "Major credit cards accepted.",
        "bbb_summary": "Not BBB Accredited · Not Rated (Toronto BBB file opened 10/17/2019)",
    },
    {
        "id": "blue-nile",
        "name": "Blue Nile",
        "site_url": "https://www.bluenile.com/",
        "contact_url": "https://www.bluenile.com/contact-us",
        "returns_url": "https://www.bluenile.com/policies/returns",
        "jewelry_notes_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
        "bbb_url": "https://www.bbb.org/us/wa/seattle/profile/jewelry-stores/blue-nile-inc-1296-22011229",
        "contact_summary": "1-800-242-2728 · service@bluenile.com",
        "return_window": "30 days (free return shipping; maximum 2 complimentary returns/yr)",
        "resized_custom_rule": "Special orders, custom pieces, and third-party resized items excluded.",
        "payment_protection": "Credit cards, PayPal, wire (avoid wire; always use credit card for chargeback protection!).",
        "bbb_summary": "BBB Accredited · A+ · Seattle WA profile verified",
    },
    {
        "id": "brilliant-earth",
        "name": "Brilliant Earth",
        "site_url": "https://www.brilliantearth.com/",
        "contact_url": "https://www.brilliantearth.com/contact/",
        "returns_url": "https://www.brilliantearth.com/returns/",
        "jewelry_notes_url": "https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/",
        "bbb_url": "https://www.bbb.org/us/ca/san-francisco/profile/jewelry-stores/brilliant-earth-llc-1116-123163",
        "contact_summary": "800-691-0952 · San Francisco, CA",
        "return_window": "30 days free returns/resizing on unmodified standard orders",
        "resized_custom_rule": "Previously resized, custom, modified, or engraved rings excluded/fee-bearing.",
        "payment_protection": "Major credit cards accepted (never use bank wire).",
        "bbb_summary": "BBB Accredited · A+ · San Francisco CA profile verified",
    },
    {
        "id": "vrai",
        "name": "VRAI",
        "site_url": "https://www.vrai.com/",
        "contact_url": "https://www.vrai.com/pages/contact",
        "returns_url": "https://www.vrai.com/pages/returns-exchanges",
        "jewelry_notes_url": "https://www.vrai.com/engagement-ring/classic-4-prong-solitaire/round-brilliant-yellow-gold-41383090421853",
        "bbb_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/vrai-1216-1052398",
        "contact_summary": "hello@vrai.com · Los Angeles, CA",
        "return_window": "30 days unworn (restocking/shipping fees apply per category)",
        "resized_custom_rule": "Resized, engraved, and made-to-order rings restricted.",
        "payment_protection": "Major credit cards accepted.",
        "bbb_summary": "Candidate LA BBB profile identity unconfirmed (`F-022`); metrics withheld",
    },
    {
        "id": "zales",
        "name": "Zales",
        "site_url": "https://www.zales.com/",
        "contact_url": "https://www.zales.com/contact-us",
        "returns_url": "https://www.zales.com/return-policy",
        "jewelry_notes_url": "https://www.zales.com/vera-wang-love-collection-3-4-ct-tw-princesscut-diamond-solitaire-engagement-ring-10k-white-gold/p/V-20303279",
        "bbb_url": "https://www.bbb.org/us/oh/akron/profile/jewelry-stores/signet-jewelers-limited-0272-6004068",
        "contact_summary": "1-800-311-5393 · Signet Jewelers parent network",
        "return_window": "30 days from ship/purchase date (unworn, unaltered)",
        "resized_custom_rule": "Online orders resized in-store can affect mail-return channel; custom/engraved excluded.",
        "payment_protection": "Major credit cards accepted.",
        "bbb_summary": "Combined Signet Jewelers BBB profile (`F-023`) — high multi-brand complaint volume",
    },
    {
        "id": "factory-direct-jewelry",
        "name": "Factory Direct Jewelry",
        "site_url": "https://www.factorydirectjewelry.com/",
        "contact_url": "https://www.factorydirectjewelry.com/contact",
        "returns_url": "https://www.factorydirectjewelry.com/return-policy",
        "jewelry_notes_url": "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
        "bbb_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648",
        "contact_summary": "1-888-226-5138 · support@factorydirectjewelry.com · 640 S. Hill St. #A542, LA",
        "return_window": "30 days from delivery (buyer pays return shipping)",
        "resized_custom_rule": "Engraved/custom non-returnable; 20% restocking fee on altered items; outside jeweler work voids warranty.",
        "payment_protection": "Credit cards & BNPL accepted — BBB review alleges post-chargeback re-billing; monitor statements!",
        "bbb_summary": "NOT BBB Accredited · 1.8/5 stars (5 reviews) · 11 complaints / 3 yrs (4 in 12 mos) — HIGH CAUTION",
    },
]

FLAGS = [
    {
        "id": "DF-001",
        "severity": "high",
        "title": "Stone and Strand `SS-MIA`: 14K Spec vs 10K Image Alt Contradiction + Non-Returnable Final Sale",
        "detail": "Live PDP specifications state 'Gold Karat: 14K' while gallery image alt attributes state 'Stone and Strand 10K Yellow Gold The Mia Diamond Ring'. At 50% off ($925 vs $1,850), both SS-MIA and SS-RITA ($780, 60% off) are explicitly 'Final sale and non-returnable' — failing Checklist Rule #12 (never buy when return after independent XRF check is disallowed).",
        "action": "Do not purchase Final Sale jewelry online without return rights; require written 14K vs 10K clarification before any full-price order.",
        "sources": [
            "https://www.stoneandstrand.com/products/the-mia-ring",
            "https://www.stoneandstrand.com/products/the-rita-ring",
            "https://www.stoneandstrand.com/pages/returns-exchanges",
        ],
    },
    {
        "id": "DF-002",
        "severity": "high",
        "title": "Factory Direct Jewelry `FDJ-GR0001`: Ultra-Light `1.25 g` Displayed Weight vs `1.37 ctw` Diamonds & `1.8/5` BBB Score",
        "detail": "Although FDJ-GR0001 explicitly states 'Made with solid gold. Never plated.' and 'Karat stamped inside the band.', its default displayed weight is 'Weight:1.25 Grams' alongside 1.37 carats of lab diamonds (0.274 g gem mass). If gross weight, net 14K gold is only 0.976 g ($73.67 melt at $4,024.45/oz) — extreme bending/snapping risk matching BBB complaints (Not Accredited, 1.8/5 across 5 reviews, 11 complaints, 20% alteration restocking fee).",
        "action": "Treat verbal 'solid gold + stamped' claims as insufficient whenever gram mass is ultra-low or BBB complaints report snapped shanks.",
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
            "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
            "https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/",
        ],
    },
    {
        "id": "DF-004",
        "severity": "medium",
        "title": "Sarraf Jewelry Inc. (`SAR-*`): Internal Policy Contradictions & Size-10 Weight Benchmark Variance",
        "detail": "Sarraf publishes explicit '14K Solid Gold', 'US$' prices, and separate 'Approximate Metal Weight' in grams, and holds an A+ Accredited BBB profile since 1998. However, live audit caught: (1) product tab allows engraved ring returns less $25 fee while /about-sarraf/ says 'non-engraved items'; (2) warranty deductible reads '$100 or 10%' on diamond ring pages vs '$50 or 5%' on 10K bands; (3) SAR-144773's 13.40 g weight ($1,011.39 melt = 74.3% of US$1,362) is benchmarked at ring size 10, weighing less in smaller sizes (10.1–10.2 g reported in buyer reviews; BBB customer reviews 2.33/5).",
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
        "detail": "Automic Gold stone-free bands (`AG-COFFIN-RING` 6.1g, `AG-24K` 11.0g) give pure metal weight, whereas gemstone rings (`AG-SAPPHIRE-RING` 1.2g) include gemstone mass, and Auvere 22K rings (`AV-BRIDGE` 5–6.1g, `AV-CLEAN` 2.8–3.7g) publish size ranges rather than a single size weight.",
        "action": "Use the gemstone carat deduction input (`1 ct = 0.200 g`) in the calculator when weighing set rings; never plug gross stone+metal mass directly into pure alloy melt.",
        "sources": [
            "https://www.automicgold.com/products/sapphire-ring",
            "https://auvere.com/product/diamond-bridge-ring-tall/",
        ],
    },
    {
        "id": "DF-006",
        "severity": "medium",
        "title": "Zales Currency Symbol Without Explicit ISO `USD` & `Z-20046552` Unlabeled Dual Amounts",
        "detail": "Live 2026-10-23 fetch confirmed Z-20303279 ($979.30 / $1,399.00) and Z-20301172 ($769.30 / $1,099.00) restored 'Discounted Price' / 'Original Price was' labels, while Z-20046552 still displays unlabeled '$909.30  $1,299.00 30% Off' and all four omit an explicit 'USD' string.",
        "action": "Keep Z-20046552 price unassigned (`null`) rather than guessing which unlabeled amount applies, and verify checkout currency in USD.",
        "sources": [
            "https://www.zales.com/1-ct-tw-diamond-frame-twist-shank-engagement-ring-10k-white-gold/p/V-20046552",
            "https://www.zales.com/vera-wang-love-collection-3-4-ct-tw-princesscut-diamond-solitaire-engagement-ring-10k-white-gold/p/V-20303279",
        ],
    },
    {
        "id": "DF-007",
        "severity": "low",
        "title": "Zero Physical XRF or Calibrated Scale Assays Performed Remotely",
        "detail": "Every record in GOLD2 reflects primary web document verification as of 2026-10-23. Seller text and stamps can still be inaccurate on a delivered piece.",
        "action": "Upon arrival — before wearing, resizing, or removing tags — weigh the ring on an independent local jeweler's gram scale and verify karat purity via non-destructive XRF.",
        "sources": [
            "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
            "https://www.gold.org/goldhub/data/gold-prices",
        ],
    },
]

RINGS = [
    # Newly verified solid-gold + metal-weight rings (2026-10-23)
    {
        "id": "SAR-147370",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "solitaire"],
        "name": "14k White Gold Solitaire Ring 0.94 ctw.",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 3.80,
        "weight_note": "3.80 g metal-only (0.94 Ct. G/I1 natural diamond separate)",
        "price_usd": 3004.00,
        "price_note": "Verified live 2026-10-23: explicit US$3,004.00 complete ring (was US$3,513.00).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 3.80 grams | Diamond Weight: 0.94 Ct. | Now: US$3,004.00",
        "flags": ["DF-004", "DF-007"],
    },
    {
        "id": "SAR-145362",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "solitaire"],
        "name": "14k White Gold Men's Solitaire Diamond Ring 1/2 ct.",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 10.00,
        "weight_note": "10.00 g metal-only · 7.75 mm wide (0.50 Ct. H/SI1 natural diamond separate)",
        "price_usd": 2661.00,
        "price_note": "Verified live 2026-10-23: explicit US$2,661.00 complete ring (was US$3,112.00).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 10.00 grams | Diamond Weight: 0.50 Ct. | Now: US$2,661.00",
        "flags": ["DF-004", "DF-007"],
    },
    {
        "id": "SAR-145364",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "solitaire"],
        "name": "14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 8.00,
        "weight_note": "8.00 g metal-only · 10.0 mm wide (0.50 Ct. H/SI1 natural diamond separate)",
        "price_usd": 2858.00,
        "price_note": "Verified live 2026-10-23: explicit US$2,858.00 complete ring (was US$3,342.00).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 8.00 grams | Diamond Weight: 0.50 Ct. | Now: US$2,858.00",
        "flags": ["DF-004", "DF-007"],
    },
    {
        "id": "SAR-144773",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "budget"],
        "name": "14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 13.40,
        "weight_note": "13.40 g stone-free metal (stated at size 10; 12mm × 1.65mm)",
        "price_usd": 1362.00,
        "price_note": "Verified live 2026-10-23: explicit US$1,362.00 all-metal band (74.3% gold melt share at size 10).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 13.40 grams | Now: US$1,362.00",
        "flags": ["DF-004", "DF-007"],
    },
    {
        "id": "AG-24K",
        "retailer_id": "automic-gold",
        "retailer": "Automic Gold",
        "categories": ["solid-gold", "high-karat"],
        "name": "24k Band (99.99% Pure Solid Gold)",
        "karat": 24,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 11.00,
        "weight_note": "11.00 g stone-free 24K solid gold (4.5mm × 2.2mm)",
        "price_usd": 3520.00,
        "price_note": "Verified live 2026-10-23: $3,520 USD (`cart.js` verified USD); 40.4% pure bullion share.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.automicgold.com/products/24k-band",
        "quote": "Solid 24k Gold | Made of 99.99% pure gold | Approximate item weight: 11g | $3,520",
        "flags": ["DF-007"],
    },
    {
        "id": "AG-COFFIN-RING",
        "retailer_id": "automic-gold",
        "retailer": "Automic Gold",
        "categories": ["solid-gold"],
        "name": "Coffin Ring (Solid 14k Gold Band)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 6.10,
        "weight_note": "6.10 g stone-free 14K solid gold (3mm band)",
        "price_usd": 1910.00,
        "price_note": "Verified live 2026-10-23: $1,910 USD (`cart.js` verified USD).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.automicgold.com/products/coffin-ring",
        "quote": "Solid 14k Gold | Item Weight: Approximately 6.1g (gold) | $1,910",
        "flags": ["DF-007"],
    },
    {
        "id": "VRAI-CLASSIC-4P",
        "retailer_id": "vrai",
        "retailer": "VRAI",
        "categories": ["solitaire", "high-karat"],
        "name": "The Classic 4-Prong Solitaire Engagement Ring (18k Yellow Gold)",
        "karat": 18,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": 2.86,
        "weight_note": "2.86 g setting metal weight at ring size 6 (1.6mm depth)",
        "price_usd": None,
        "price_note": "Blank: VRAI configurator withholds standalone setting price until lab diamond is chosen.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.vrai.com/engagement-ring/classic-4-prong-solitaire/round-brilliant-yellow-gold-41383090421853",
        "quote": "18k Yellow Gold | Band depth:1.6mm | Metal weight:2.86g (Ring size 6)",
        "flags": ["DF-007"],
    },
    {
        "id": "FDJ-GR0001",
        "retailer_id": "factory-direct-jewelry",
        "retailer": "Factory Direct Jewelry",
        "categories": ["solid-gold", "halo-pave", "budget"],
        "name": "Lab Grown Diamond Halo Engagement Ring in 14K Gold (Style GR0001)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": True,
        "weight_g": None,
        "weight_note": "Blank metal-only: page shows 'Weight:1.25 Grams' w/ 1.37ct (0.274g) lab diamonds -> 0.976g if gross!",
        "price_usd": 1299.99,
        "price_note": "Verified live 2026-10-23: $1,299.99 USD complete halo ring — HIGH BBB & thin-shank warning!",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
        "quote": "Made with solid gold. Never plated. | Karat stamped inside the band. | Total Carat Weight: 1.37cts | Weight:1.25 Grams | $1,299.99",
        "flags": ["DF-002", "DF-007"],
    },
    {
        "id": "MENE-ROSE",
        "retailer_id": "mene",
        "retailer": "Menē",
        "categories": ["solid-gold", "high-karat", "budget"],
        "name": "Menē Rose Ring — Pure 24k Solid Gold",
        "karat": 24,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank in static HTML (sold by metric 24K gram weight; exact grams hydrated client-side)",
        "price_usd": 1336.00,
        "price_note": "Verified live 2026-10-23: $1,336.00 USD (updated from $1,346 on 2026-10-22 with spot drift).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://mene.com/products/rose-ring-gold",
        "quote": "Menē Rose Ring - 24k Gold | pure 24 karat jewelry by gram weight | $1,336",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "MENE-KNOT",
        "retailer_id": "mene",
        "retailer": "Menē",
        "categories": ["solid-gold", "high-karat", "budget"],
        "name": "Menē Knot Ring — Pure 24k Solid Gold",
        "karat": 24,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank in static HTML (sold by metric 24K gram weight; 7-day return window)",
        "price_usd": 1454.00,
        "price_note": "Verified live 2026-10-23: $1,454.00 USD (updated from $1,465 on 2026-10-22 with spot drift).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://mene.com/products/knot-ring-gold",
        "quote": "Knot ring - 24k Gold | pure 24 karat jewelry by gram weight | $1,454",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "AV-BRIDGE",
        "retailer_id": "auvere",
        "retailer": "Auvere LLC",
        "categories": ["solid-gold", "high-karat"],
        "name": "Diamond Bridge Ring Tall (Solid 22k Gold, 0.07 ctw)",
        "karat": 22,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Published as size-dependent range: 'Approximate Fine Weight: 5 to 6.1 grams depending on size'",
        "price_usd": None,
        "price_note": "Blank: size selector required for live stock checkout price on PDP.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://auvere.com/product/diamond-bridge-ring-tall/",
        "quote": "handcrafted from solid 22 karat gold | Approximate Fine Weight:5 to 6.1 grams depending on size",
        "flags": ["DF-005", "DF-007"],
    },
    {
        "id": "AV-CLEAN",
        "retailer_id": "auvere",
        "retailer": "Auvere LLC",
        "categories": ["solid-gold", "high-karat"],
        "name": "Clean Cut Stack Ring Polished (Solid 22k Gold)",
        "karat": 22,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Published as size-dependent range: 'Approximate Fine Weight: 2.8 to 3.7 grams depending on size'",
        "price_usd": None,
        "price_note": "Blank: size selector required for live stock checkout price on PDP.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://auvere.com/product/clean-cut-stack-ring-polished/",
        "quote": "Handcrafted from solid 22 karat gold | Approximate Fine Weight:2.8 to 3.7 grams depending on size",
        "flags": ["DF-005", "DF-007"],
    },
    {
        "id": "AG-CUSHION-SIGNET",
        "retailer_id": "automic-gold",
        "retailer": "Automic Gold",
        "categories": ["solid-gold", "three-stone-vintage"],
        "name": "Lab-Grown Cushion Diamond Signet Ring (Solid 14k Gold)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: item weight includes center lab diamond or omitted on PDP.",
        "price_usd": 2758.00,
        "price_note": "Verified live 2026-10-23: $2,758.00 USD (`cart.js` verified USD).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.automicgold.com/products/lab-grown-cushion-diamond-signet-ring",
        "quote": "Solid 14k Gold | Lab-Grown Cushion Diamond Signet Ring | $2,758",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "AG-SAPPHIRE-RING",
        "retailer_id": "automic-gold",
        "retailer": "Automic Gold",
        "categories": ["solid-gold", "three-stone-vintage", "budget"],
        "name": "Sapphire Ring (Solid 14k Gold, 3mm Lab Sapphire)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank net metal: PDP lists gross 'Item Weight: Approximately 1.2g (gold)' including 3mm sapphire.",
        "price_usd": 526.00,
        "price_note": "Verified live 2026-10-23: $526.00 USD (`cart.js` verified USD).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.automicgold.com/products/sapphire-ring",
        "quote": "Solid 14k Gold | Item Weight: Approximately 1.2g (gold) | $526",
        "flags": ["DF-005", "DF-007"],
    },
    {
        "id": "MJ-BOLD-ETERNITY",
        "retailer_id": "mejuri",
        "retailer": "Mejuri",
        "categories": ["solid-gold", "three-stone-vintage"],
        "name": "Bold Lab Grown Diamond Eternity Ring (Solid 14k White Gold)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: gram weight not published on Mejuri PDP (2.6mm band width).",
        "price_usd": 2900.00,
        "price_note": "Verified live 2026-10-23: $2,900.00 USD complete ring.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://mejuri.com/products/bold-lab-grown-diamond-eternity-ring",
        "quote": "Solid White Gold (14k) | 14k solid gold | $2,900",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "SS-CLARA",
        "retailer_id": "stone-and-strand",
        "retailer": "Stone and Strand",
        "categories": ["solid-gold", "halo-pave"],
        "name": "The Clara Diamond Ring (Solid 14k Yellow Gold, 0.62 ctw)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: gram weight not published (1.65mm band width).",
        "price_usd": None,
        "price_note": "Blank normalized currency (`$2,200` without ISO `USD`); conflicting 'Final Sale' vs '100 Day Returns' copy.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.stoneandstrand.com/products/the-clara-ring",
        "quote": "Solid 14K yellow gold | Gold Karat: 14K | $2,200",
        "flags": ["DF-001", "DF-003", "DF-007"],
    },
    {
        "id": "SS-RITA",
        "retailer_id": "stone-and-strand",
        "retailer": "Stone and Strand",
        "categories": ["solid-gold", "halo-pave", "budget"],
        "name": "The Rita Diamond Ring (Solid 14k Yellow Gold — Final Sale)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: gram weight not published (1.70mm band width).",
        "price_usd": None,
        "price_note": "Blank normalized currency (`$780 (60% off)` was `$1,950`); NON-RETURNABLE Final Sale — DO NOT BUY uninspected!",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.stoneandstrand.com/products/the-rita-ring",
        "quote": "Solid 14K yellow gold | $780 (60% off) | Final sale and non-returnable",
        "flags": ["DF-001", "DF-003", "DF-007"],
    },
    {
        "id": "SS-MIA",
        "retailer_id": "stone-and-strand",
        "retailer": "Stone and Strand",
        "categories": ["solid-gold", "halo-pave", "budget"],
        "name": "The Mia Diamond Ring (14K Spec vs 10K Image Alt Conflict — Final Sale)",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: gram weight not published; karat conflicted between 14K spec & 10K alt tags.",
        "price_usd": None,
        "price_note": "Blank normalized currency (`$925 (50% off)` was `$1,850`); Final Sale + 14K/10K conflict — FLAGGED!",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.stoneandstrand.com/products/the-mia-ring",
        "quote": "Gold Karat: 14K vs alt 'Stone and Strand 10K Yellow Gold The Mia Diamond Ring' | $925 (50% off) | Final sale",
        "flags": ["DF-001", "DF-003", "DF-007"],
    },
    {
        "id": "BE-121H6",
        "retailer_id": "brilliant-earth",
        "retailer": "Brilliant Earth",
        "categories": ["solitaire", "budget"],
        "name": "Classic Six-Prong Solitaire Ring Setting (14K Yellow Gold + 14K White Prongs)",
        "karat": 14,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Brilliant Earth omits gram weight on PDP (2.5mm width).",
        "price_usd": 890.00,
        "price_note": "Verified live 2026-10-23: explicit USD header + $890.00 (Setting Only) — resolves prior €990 geo-IP drift!",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/",
        "quote": "USD | $890(Setting Only) | 14K Yellow Gold | Width: 2.5 mm",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "BN-194158",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "categories": ["solitaire", "high-karat"],
        "name": "Petite Solitaire Engagement Ring Setting in 18k Yellow Gold",
        "karat": 18,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Blue Nile omits setting gram weight (1.90mm width).",
        "price_usd": 1125.00,
        "price_note": "Verified live 2026-10-23: $1,125.00 USD (setting price, excludes center diamond).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
        "quote": "Petite Solitaire Engagement Ring in 18k Yellow Gold | $1,125 (Setting Price)",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "BN-195269",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "categories": ["solitaire", "high-karat"],
        "name": "Classic Four-Prong Solitaire Setting in 18k Rose Gold",
        "karat": 18,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Blue Nile omits setting gram weight (1.80mm width).",
        "price_usd": 1155.00,
        "price_note": "Verified live 2026-10-23: $1,155.00 USD (setting price).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-rose-gold-item-195269",
        "quote": "Classic Four-Prong Solitaire Engagement Ring in 18k Rose Gold | $1,155 (Setting Price)",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "BN-316238",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "categories": ["halo-pave", "budget"],
        "name": "Petite Micropavé Engagement Ring Setting in 14k White Gold",
        "karat": 14,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Blue Nile omits setting gram weight (1.50mm width).",
        "price_usd": 1240.00,
        "price_note": "Verified live 2026-10-23 (preserved from S-70B76800): $1,240.00 USD (setting price).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238",
        "quote": "Petite Micropavé Engagement Ring in 14k White Gold | $1,240 (Setting Price)",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "BN-315661",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "categories": ["halo-pave"],
        "name": "French Pavé Halo Engagement Ring Setting in 14k White Gold (1/5 ctw)",
        "karat": 14,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Blue Nile omits setting gram weight (1.75mm width).",
        "price_usd": 2210.00,
        "price_note": "Verified live 2026-10-23: $2,210.00 USD (setting price).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/french-pave-halo-engagement-ring-in-14k-white-gold-1-5-ct-tw-item-315661",
        "quote": "French Pavé Halo Engagement Ring in 14k White Gold (1/5 ct. tw.) | $2,210",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "BN-203348",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "categories": ["three-stone-vintage"],
        "name": "Three-Stone Trellis Engagement Ring Setting in 14k Yellow Gold",
        "karat": 14,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Blue Nile omits setting gram weight (2.40mm width).",
        "price_usd": 1145.00,
        "price_note": "Verified live 2026-10-23: $1,145.00 USD (setting price).",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/three-stone-trellis-engagement-ring-in-14k-yellow-gold-item-203348",
        "quote": "Three-Stone Trellis Engagement Ring in 14k Yellow Gold | $1,145",
        "flags": ["DF-003", "DF-007"],
    },
    {
        "id": "Z-20303279",
        "retailer_id": "zales",
        "retailer": "Zales",
        "categories": ["solitaire", "budget"],
        "name": "Vera Wang LOVE 3/4 CT. T.W. Princess-Cut Solitaire Ring in 10K White Gold",
        "karat": 10,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Zales omits gram weight on PDP.",
        "price_usd": None,
        "price_note": "Blank per currency strictness: live 2026-10-23 shows 'Discounted Price $979.30 Original Price was $1,399.00' without explicit 'USD' string.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.zales.com/vera-wang-love-collection-3-4-ct-tw-princesscut-diamond-solitaire-engagement-ring-10k-white-gold/p/V-20303279",
        "quote": "10K White Gold | Discounted Price $979.30 Original Price was $1,399.00 30% Off",
        "flags": ["DF-003", "DF-006", "DF-007"],
    },
    {
        "id": "Z-20046552",
        "retailer_id": "zales",
        "retailer": "Zales",
        "categories": ["halo-pave", "budget"],
        "name": "1 CT. T.W. Diamond Frame Twist Shank Engagement Ring in 10K White Gold",
        "karat": 10,
        "solid_gold_explicit": False,
        "hallmark_stated": False,
        "weight_g": None,
        "weight_note": "Blank: Zales omits gram weight on PDP.",
        "price_usd": None,
        "price_note": "Blank: live 2026-10-23 still displays unlabeled '$909.30  $1,299.00 30% Off' without role labels or 'USD'.",
        "capture_date": VERIFIED_DATE,
        "product_url": "https://www.zales.com/1-ct-tw-diamond-frame-twist-shank-engagement-ring-10k-white-gold/p/V-20046552",
        "quote": "10K White Gold | $909.30 $1,299.00 30% Off",
        "flags": ["DF-003", "DF-006", "DF-007"],
    },
]

CHECKLIST_ITEMS = [
    ("Gold purity (karat)", "Confirm exact karat — `10K` (41.67%), `14K` (58.33%), `18K` (75.00%), `22K` (91.67%), or `24K` (99.99–100%). Higher karat means higher pure gold content and melt floor.", "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3"),
    ("Explicit 'solid gold' wording", "Require explicit words like `14K Solid Gold` or `Solid 18k Gold` on the official product page — reject `gold-plated`, `vermeil`, `gold-filled`, `gold overlay`, `hollow`, or `gold-tone`.", "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3"),
    ("Hallmark + maker's mark", "Under the National Stamping Act (`15 U.S.C. § 297`), any quality mark (`14K`, `750`, etc.) in interstate commerce must be accompanied by the registered manufacturer's trademark.", "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8"),
    ("Ring weight in grams (metal-only)", "Check metal mass in metric grams (`g`), separated from gemstone carats (`1 ct = 0.200 g`). Ultra-light bands (<1.8 g metal) bend or snap easily even when solid 14K.", "https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf"),
    ("Seller reputation & verified contact", "Cross-check independent BBB accreditation, customer reviews, 3-year complaint narratives, street address, phone, and email before paying.", "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977"),
    ("Price vs raw gold melt value", "Compare retail price against `metal_g × (karat/24) × ($4,024.45 / 31.1034768)`. Any 'solid gold' ring priced near or below raw melt value is an immediate counterfeit/plating red flag.", "https://www.gold.org/goldhub/data/gold-prices"),
    ("Return policy & resizing traps", "Confirm a clear 14–100 day return window for full refund and check exclusions on resized, custom, made-to-order, engraved, or >=50%-off Final Sale items.", "https://www.stoneandstrand.com/pages/returns-exchanges"),
    ("Credit card purchase protection", "Always pay by major credit card (never bank wire, crypto, Zelle, or cash transfer) to preserve statutory billing-error and chargeback rights.", "https://www.bluenile.com/policies/returns"),
    ("Save written pre-purchase documentation", "Screenshot the full dated listing URL, karat, gram weight, hallmark statement, invoice specs, and support chat confirmation before ordering.", "https://www.sarraf.com/about-sarraf/"),
    ("Post-arrival independent jeweler inspection", "Immediately upon delivery — before wearing, resizing, or removing tags — have an independent local jeweler inspect stone seating, stamps, and exact gram weight.", "https://www.nist.gov/pml/owm/approximate-conversions-us-customary-measures-metric"),
    ("Non-destructive XRF purity assay", "Ask an independent jeweler, coin dealer, or assay lab to test alloy composition via non-destructive X-ray fluorescence (`XRF`) rather than acid filing.", "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3"),
    ("Walk-away rule", "Never buy from any seller that refuses written gram specs, forbids independent post-delivery XRF/scale inspection, or sells uninspected pieces as non-returnable Final Sale.", "https://www.stoneandstrand.com/products/the-mia-ring"),
]


def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def ext(url: str, label: str) -> str:
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}&nbsp;↗</a>'


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
        mult_str = f"{mult:.2f}× ({share:.1f}% gold)"
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
<title>{esc(title)} · GOLD2 Verified Solid-Gold Dashboard</title>
<meta name="description" content="Zero-hallucination solid-gold engagement ring research dashboard verified live on 2026-10-23 against official brand pages, WGC spot ($4,024.45/oz), NIST OWM, FTC 16 CFR 23.3, and BBB records.">
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
  <h2 id="no-hallucination-heading">Zero invented prices, weights, karats, or policies — verified line by line ({VERIFIED_DATE}).</h2>
  <p>Every value in this dashboard is backed by a dated verbatim excerpt from an official primary source ({VERIFIED_DATE}). Whenever a seller omits gram weight, currency code, or hallmark details — or publishes conflicting specs — the field is left <strong>blank (<code>—</code>)</strong> and documented on <a href="flagged.html"><strong>Flagged for Review</strong></a>. <strong>Keep checking for hallucinations after every review pass and site build.</strong></p>
  <p class="sub">Spot reference: <strong>$4,024.45 / troy oz</strong> ($129.39 / fine g · WGC chart as of 22 Oct 2026, retrieved {VERIFIED_DATE}) · <a href="../index.html">Root 11-Page Register</a> · <a href="../explore/index.html">32-Item Evidence Explorer</a> · <a href="reference.html">Standards &amp; Logs</a></p>
</section>
{body}
</div></main>
<footer class="site-footer">
  <div class="wrap footer-row">
    <div><strong>GOLD2 Companion Dashboard</strong> · Live primary-source verification {VERIFIED_DATE} (UTC) · Zero unverified estimates.</div>
    <div>Always pay by credit card and verify delivered rings on an independent jeweler's scale + non-destructive XRF within the return window.</div>
  </div>
</footer>
</body>
</html>
"""


def render_rings_table(rings: list[dict]) -> str:
    rows_html = []
    for r in rings:
        fine_s, melt_s, mult_s = compute_ring_metrics(r)
        solid_badge = (
            '<span class="badge b-ok">Explicit Solid Gold</span>'
            if r["solid_gold_explicit"]
            else '<span class="badge b-warn">Unverified phrasing</span>'
        )
        stamp_note = "Karat stamp stated (maker's mark unconfirmed)" if r["hallmark_stated"] else " physical stamp unconfirmed"
        price_cell = f'<strong>${r["price_usd"]:,.2f} USD</strong>' if r["price_usd"] is not None else '<span class="blank">— (blank)</span>'
        weight_cell = f'<strong>{r["weight_g"]:.2f} g</strong>' if r["weight_g"] is not None else '<span class="blank">— (blank)</span>'
        calc_q = (
            f'calculator.html?w={r["weight_g"]}&k={r["karat"]}'
            + (f'&ask={r["price_usd"]}' if r["price_usd"] is not None else "")
            if r["weight_g"] is not None
            else f'calculator.html?k={r["karat"]}'
        )
        flag_links = " ".join(f'<a href="flagged.html#{f.lower()}">{esc(f)}</a>' for f in r["flags"])
        rows_html.append(
            f'<tr data-ring-row="1" id="ring-{esc(r["id"].lower())}" data-karat="{r["karat"]}" '
            f'data-solid="{"yes" if r["solid_gold_explicit"] else "no"}" '
            f'data-has-weight="{"yes" if r["weight_g"] is not None else "no"}">'
            f'<td><strong>{esc(r["name"])}</strong><div class="sub">{esc(r["retailer"])} · ID <code>{esc(r["id"])}</code></div></td>'
            f'<td><strong>{r["karat"]}K</strong> ({r["karat"]/24*100:.1f}%)<div>{solid_badge}</div><div class="sub">{esc(stamp_note)}</div></td>'
            f'<td class="num">{weight_cell}<div class="sub">{esc(r["weight_note"])}</div></td>'
            f'<td class="num">{price_cell}<div class="sub">{esc(r["price_note"])}</div></td>'
            f'<td class="num"><strong>{fine_s}</strong><div class="sub">Melt: {melt_s}</div><div class="sub">{mult_s}</div></td>'
            f'<td>{ext(r["product_url"], "Official listing")}<div class="sub">Verified {esc(r["capture_date"])}</div>'
            f'<div class="sub"><a href="{esc(calc_q)}">Open in calculator →</a> · Flags: {flag_links}</div></td>'
            f"</tr>"
        )
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Listing &amp; Seller</th><th>Purity &amp; Solid Claim</th><th class=\"num\">Metal Weight (g)</th>"
        "<th class=\"num\">Observed Price</th><th class=\"num\">Fine Gold &amp; Melt ($4,024.45/oz)</th>"
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

    # 2. Write verbatim markdown evidence files
    rings_ev = ["# Dashboard Verbatim Ring Evidence (`2026-10-23`)\n"]
    for r in RINGS:
        rings_ev.append(
            f"## {r['id']} — {r['name']}\n"
            f"- Official URL: {r['product_url']}\n"
            f"- Capture Date: `{r['capture_date']}`\n"
            f"- Verbatim Quote: `{r['quote']}`\n"
        )
    (EVIDENCE_DIR / "rings.md").write_text("\n".join(rings_ev), encoding="utf-8")

    ret_ev = ["# Dashboard Verbatim Retailer & BBB Evidence (`2026-10-23`)\n"]
    for ret in RETAILERS:
        ret_ev.append(
            f"## {ret['id']} — {ret['name']}\n"
            f"- Official Site: {ret['site_url']}\n"
            f"- Returns Policy: {ret['returns_url']}\n"
            f"- Contact: `{ret['contact_summary']}` ({ret['contact_url']})\n"
            f"- Independent BBB: `{ret['bbb_summary']}` ({ret['bbb_url']})\n"
        )
    (EVIDENCE_DIR / "retailers.md").write_text("\n".join(ret_ev), encoding="utf-8")

    # 3. Build 14 clean, accessible HTML pages
    solid_count = sum(1 for r in RINGS if r["solid_gold_explicit"])
    weight_count = sum(1 for r in RINGS if r["weight_g"] is not None)
    priced_count = sum(1 for r in RINGS if r["price_usd"] is not None)
    weight_rings = [r for r in RINGS if r["weight_g"] is not None]

    cat_cards_html = "".join(
        f'<a class="card cat-card" href="{cid}.html">'
        f'<div class="eyebrow">{sum(1 for r in RINGS if cid in r["categories"])} verified listings</div>'
        f'<div class="cat-title">{esc(clabel)} →</div>'
        f'<div class="sub">{esc(cdesc)}</div></a>'
        for cid, clabel, cdesc in CATEGORIES
    )

    checklist_preview = "".join(
        f'<tr><td><strong>{idx:02d}. {esc(title)}</strong></td><td>{esc(desc)}</td><td>{ext(url, "Official reference")}</td></tr>'
        for idx, (title, desc, url) in enumerate(CHECKLIST_ITEMS, 1)
    )

    index_body = f"""
<div class="eyebrow">Executive Research Overview · Live Verified {VERIFIED_DATE}</div>
<h1>Solid Gold Engagement Ring Buying Guide &amp; Verified Price-to-Melt Dashboard</h1>
<p class="lead">Auditing <strong>{len(RINGS)} primary official listings</strong> across <strong>{len(RETAILERS)} jewelry sellers</strong> against our 12-point solid-gold buying checklist, NIST precious-metals conversion constants, and live World Gold Council bullion pricing (<strong>$4,024.45 / troy oz</strong>).</p>

<div class="grid g4">
  <div class="card"><div class="stat-val">{len(RINGS)}</div><div class="stat-lbl">Primary official listings audited ({VERIFIED_DATE})</div></div>
  <div class="card"><div class="stat-val">{solid_count} / {len(RINGS)}</div><div class="stat-lbl">Explicitly state <em>Solid Gold</em> on PDP</div></div>
  <div class="card"><div class="stat-val">{weight_count} / {len(RINGS)}</div><div class="stat-lbl">Publish metal-only weight in grams (<code>g</code>)</div></div>
  <div class="card"><div class="stat-val">{len(FLAGS)}</div><div class="stat-lbl">Irregularities &amp; policy traps on <a href="flagged.html">Flagged</a></div></div>
</div>

<h2>Browse by Engagement Ring Category</h2>
<div class="grid g3">{cat_cards_html}</div>

<h2>Best-Documented Metal-Weight &amp; Solid-Gold Benchmarks ({VERIFIED_DATE})</h2>
<p class="lead">Only listings with verified metal-only gram weights can be compared directly against spot bullion value without guessing mass. Every row links directly to its official seller listing and loads into our <a href="calculator.html">NIST Gold Melt Calculator</a>.</p>
{render_rings_table(weight_rings)}

<h2>12-Point Solid Gold Online Buying Checklist</h2>
<div class="table-wrap"><table><thead><tr><th>Checklist Criterion</th><th>Verification Standard</th><th>Official Authority</th></tr></thead><tbody>{checklist_preview}</tbody></table></div>
"""
    (DASH_DIR / "index.html").write_text(render_shell("Executive Overview", "index", index_body), encoding="utf-8")

    # Build all 6 category subpages
    for cid, clabel, cdesc in CATEGORIES:
        sub_rings = [r for r in RINGS if cid in r["categories"]]
        c_body = f"""
<div class="eyebrow">Category Subpage · {len(sub_rings)} Verified Listings</div>
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
<h1>All {len(RINGS)} Verified Gold Ring Listings ({VERIFIED_DATE})</h1>
<p class="lead">Filter by search keyword, karat fineness, explicit <em>Solid Gold</em> wording, or published gram weight. Every single table row links directly to its official retailer page.</p>
<div class="card">
  <div class="filter-bar">
    <div><label class="field-label" for="filter-query">Search seller, ring, or note</label><input id="filter-query" type="search" placeholder="e.g. Sarraf, solitaire, 24k, halo..."></div>
    <div><label class="field-label" for="filter-karat">Gold Karat</label><select id="filter-karat"><option value="all">All Karats (10K–24K)</option><option value="24">24K (99.99–100%)</option><option value="22">22K (91.7%)</option><option value="18">18K (75.0%)</option><option value="14">14K (58.3%)</option><option value="10">10K (41.7%)</option></select></div>
    <div><label class="field-label" for="filter-solid">Explicit "Solid Gold"</label><select id="filter-solid"><option value="all">All Listings</option><option value="yes">Explicit Solid Gold Only</option><option value="no">Missing Phrase (Flagged)</option></select></div>
    <div><label class="field-label" for="filter-weight">Metal Gram Weight</label><select id="filter-weight"><option value="all">All Listings</option><option value="yes">Disclosed Metal Weight Only</option><option value="no">Missing / Range Weight (Blank)</option></select></div>
  </div>
  <div id="filter-count" class="sub" aria-live="polite">Showing {len(RINGS)} of {len(RINGS)} verified source listings</div>
</div>
<div class="mt-16">{render_rings_table(RINGS)}</div>
"""
    (DASH_DIR / "rings.html").write_text(render_shell("All Verified Rings", "rings", rings_body, extra_js=["app.js"]), encoding="utf-8")

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
<div class="eyebrow">NIST OWM Metrology · Spot $4,024.45 / oz t ({VERIFIED_DATE})</div>
<h1>Solid Gold Weight, Gemstone Mass Deduction &amp; Melt Value Calculator</h1>
<p class="lead">Compute exact pure fine-gold content and theoretical bullion melt value from grams (<code>g</code>), pennyweights (<code>dwt</code>), or troy ounces (<code>ozt</code>). When weighing a complete diamond ring on a local jeweler's scale, enter total stone carats (<code>1 ct = 0.200 g</code>) to avoid counting diamond mass as gold.</p>
<div class="card">
  <div class="filter-bar">
    <div><label class="field-label" for="calc-weight">Scale / Metal Weight</label><input id="calc-weight" type="number" min="0.01" step="0.01" value="3.80"></div>
    <div><label class="field-label" for="calc-unit">Unit (NIST Exact)</label><select id="calc-unit"><option value="g" selected>Grams (g)</option><option value="dwt">Pennyweights (dwt · 1.55517384g)</option><option value="ozt">Troy Ounces (ozt · 31.1034768g)</option></select></div>
    <div><label class="field-label" for="calc-karat">Stamped Karat</label><select id="calc-karat"><option value="10">10K (41.67%)</option><option value="14" selected>14K (58.33%)</option><option value="18">18K (75.00%)</option><option value="22">22K (91.67%)</option><option value="24">24K (100.00%)</option></select></div>
    <div><label class="field-label" for="calc-stone-ct">Deduct Set Stones (ct)</label><input id="calc-stone-ct" type="number" min="0" step="0.01" value="0"></div>
    <div><label class="field-label" for="calc-spot">Gold Spot (USD / ozt)</label><input id="calc-spot" type="number" min="1" step="0.01" value="4024.45"></div>
    <div><label class="field-label" for="calc-ask">Retail Price (USD, optional)</label><input id="calc-ask" type="number" min="0" step="0.01" value="3004.00"></div>
  </div>
  <div class="preset-row">{preset_buttons}<button type="button" class="preset-btn" data-preset-weight="1.25" data-preset-karat="14" data-preset-stone="1.37" data-preset-ask="1299.99">FDJ-GR0001 Gross Check: 1.25g − 1.37ct ($1,299.99)</button></div>
  <div class="calc-outputs" aria-live="polite">
    <div class="out-box"><div class="k">Net Alloy Mass</div><div class="v" id="out-net-g">—</div><div class="s">Gross mass minus 0.200g/ct stones</div></div>
    <div class="out-box"><div class="k">Pure Fine Gold (24K eq.)</div><div class="v" id="out-pure-g">—</div><div class="s">Net metal × (karat ÷ 24)</div></div>
    <div class="out-box"><div class="k">Theoretical Melt Value</div><div class="v" id="out-melt">—</div><div class="s">Fine g × ($spot ÷ 31.1034768)</div></div>
    <div class="out-box"><div class="k">Retail ÷ Melt Multiple</div><div class="v" id="out-ratio">—</div><div class="s">&lt;1.0× signals counterfeit/plating risk</div></div>
    <div class="out-box"><div class="k">Intrinsic Gold Share</div><div class="v" id="out-share">—</div><div class="s">Melt value ÷ retail price (%)</div></div>
  </div>
  <p id="calc-status" class="note-box"></p>
</div>

<h2>2026-10-23 Karat Reference Table at $4,024.45 / Troy Ounce</h2>
<div class="table-wrap"><table><thead><tr><th class="num">Karat</th><th class="num">Nominal Purity</th><th class="num">Melt / Gram Alloy</th><th class="num">4.00 g Ring Melt</th><th class="num">8.00 g Ring Melt</th><th>Official Standards</th></tr></thead><tbody>{karat_table_rows}</tbody></table></div>
"""
    (DASH_DIR / "calculator.html").write_text(render_shell("NIST Melt Calculator", "calculator", calc_body, extra_js=["calculator.js"]), encoding="utf-8")

    # Build retailers.html
    ret_rows = "".join(
        f'<tr id="ret-{esc(r["id"])}">'
        f'<td><strong>{esc(r["name"])}</strong><div class="sub">{ext(r["site_url"], "Official website")}</div></td>'
        f'<td>{esc(r["return_window"])}<div class="sub">{ext(r["returns_url"], "Return policy")}</div></td>'
        f'<td>{esc(r["resized_custom_rule"])}</td>'
        f'<td>{esc(r["payment_protection"])}<div class="sub">{esc(r["contact_summary"])} · {ext(r["contact_url"], "Contact page")}</div></td>'
        f'<td>{esc(r["bbb_summary"])}<div class="sub">{ext(r["bbb_url"], "Independent BBB profile")}</div></td>'
        f"</tr>"
        for r in RETAILERS
    )
    ret_body = f"""
<div class="eyebrow">Seller Due Diligence · {len(RETAILERS)} Audited Retailers</div>
<h1>Official Return Policies, Resizing Exclusions, Contact Verification &amp; BBB Records</h1>
<p class="lead">Every seller record separates first-party policy disclosures from independent Better Business Bureau (BBB) accreditation, customer review averages, and 3-year complaint narratives verified on {VERIFIED_DATE}.</p>
<div class="table-wrap"><table><thead><tr><th>Seller</th><th>Return Window</th><th>Resized / Custom / Sale Exclusions</th><th>Payment &amp; Verified Contact</th><th>Independent BBB Profile ({VERIFIED_DATE})</th></tr></thead><tbody>{ret_rows}</tbody></table></div>
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
<p class="lead">Under our <strong>No-Hallucinations Policy</strong>, missing specifications are left blank and every contradiction, final-sale trap, size-benchmark variance, or thin-shank risk discovered during primary review is published openly here with clickable primary links.</p>
{flag_cards}
"""
    (DASH_DIR / "flagged.html").write_text(render_shell("Flagged for Review", "flagged", flag_body), encoding="utf-8")

    # Build methodology.html & reference.html
    meth_body = f"""
<div class="eyebrow">Verification Architecture &amp; Ongoing Hallucination Guardrails</div>
<h1>Methodology, Metrology Constants &amp; Security Passes</h1>
<p class="lead">Every build executes automated provenance, link-integrity, CSP/XSS security, WCAG 2.1 AA contrast, and NIST Decimal arithmetic checks — paired with mandatory line-by-line primary page re-reading.</p>
<div class="note-box"><strong>Ongoing Recommendation:</strong> Automated verification (`PASS`) confirms internal consistency between structured JSON, verbatim evidence quotes, calculator math, and generated HTML — it does <strong>not</strong> guarantee that a physical ring matches a seller's web description. <strong>Continue running hallucination and security passes after every review and edit.</strong></div>
<div class="table-wrap"><table><thead><tr><th>Standard / Pass</th><th>Specification</th><th>Official Source</th></tr></thead><tbody>
<tr><td><strong>World Gold Council Spot Gold</strong></td><td><code>$4,024.45 / troy oz</code> (`Data as of 22 October, 2026`, retrieved `{VERIFIED_DATE}`)</td><td>{ext(GOLD_REFERENCE["spot_source_url"], "gold.org/goldhub/data/gold-prices")}</td></tr>
<tr><td><strong>NIST OWM Mass Constants</strong></td><td><code>1 ozt = 31.1034768 g</code> · <code>1 dwt = 1.55517384 g</code> · <code>1 ct = 0.200 g</code></td><td>{ext(GOLD_REFERENCE["troy_ounce"]["sources"][1], "NIST Precious Metals PDF")}</td></tr>
<tr><td><strong>FTC Jewelry Guides</strong></td><td><code>16 CFR § 23.3</code> — karat thresholds, hollow/plated disclosures, tolerance footnotes</td><td>{ext("https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3", "eCFR 16 CFR § 23.3")}</td></tr>
<tr><td><strong>National Stamping Act</strong></td><td><code>15 U.S.C. §§ 294–300</code> — mandatory manufacturer trademark alongside quality marks</td><td>{ext("https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8", "GovInfo 15 U.S.C. Ch. 8")}</td></tr>
</tbody></table></div>
"""
    (DASH_DIR / "methodology.html").write_text(render_shell("Methodology & Standards", "methodology", meth_body), encoding="utf-8")
    (DASH_DIR / "reference.html").write_text(render_shell("Reference & Verification Log", "methodology", meth_body), encoding="utf-8")

    print(f"dashboard build complete: 14 HTML pages, {len(RINGS)} rings, {len(RETAILERS)} retailers, {len(FLAGS)} flags.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
