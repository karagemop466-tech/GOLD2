#!/usr/bin/env python3
"""Build the companion dashboard from the canonical GOLD2 registers.

This module deliberately contains no product prices, weights, seller metrics, or
policy observations. Those values live in the root/combined evidence registers.
The companion keeps only its editorial category membership and maps that metadata
to canonical records. Unknown values remain ``None``; a dollar sign is never
silently promoted to USD.

No network request is made and no observation is described as freshly verified.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT_LISTING_FILES = (
    "data/solid-gold-verified.json",
    "data/listings/solitaire.json",
    "data/listings/halo-pave.json",
    "data/listings/three-stone-vintage.json",
    "data/listings/18k.json",
    "data/listings/budget.json",
)

# Editorial grouping only. Product facts are not stored here.
RING_METADATA = (
    ("SAR-147370", ("solid-gold", "solitaire")),
    ("SAR-145362", ("solid-gold", "solitaire")),
    ("SAR-145364", ("solid-gold", "solitaire")),
    ("SAR-144773", ("solid-gold", "budget")),
    ("SAR-151362", ("solid-gold", "solitaire")),
    ("SAR-147371", ("solid-gold", "solitaire")),
    ("AG-24K", ("solid-gold", "high-karat")),
    ("AG-COFFIN-RING", ("solid-gold",)),
    ("VRAI-CLASSIC-4P", ("solitaire", "high-karat")),
    ("FDJ-GR0001", ("solid-gold", "halo-pave", "budget")),
    ("MENE-ROSE", ("solid-gold", "high-karat", "budget")),
    ("MENE-KNOT", ("solid-gold", "high-karat", "budget")),
    ("AV-BRIDGE", ("solid-gold", "high-karat")),
    ("AV-CLEAN", ("solid-gold", "high-karat")),
    ("AG-CUSHION-SIGNET", ("solid-gold", "three-stone-vintage")),
    ("AG-SAPPHIRE-RING", ("solid-gold", "three-stone-vintage", "budget")),
    ("MJ-BOLD-ETERNITY", ("solid-gold", "three-stone-vintage")),
    ("SS-CLARA", ("solid-gold", "halo-pave")),
    ("SS-RITA", ("solid-gold", "halo-pave", "budget")),
    ("SS-MIA", ("solid-gold", "halo-pave", "budget")),
    ("BE-121H6", ("solitaire", "budget")),
    ("BN-194158", ("solitaire", "high-karat")),
    ("BN-195269", ("solitaire", "high-karat")),
    ("BN-316238", ("halo-pave", "budget")),
    ("BN-315661", ("halo-pave",)),
    ("BN-203348", ("three-stone-vintage",)),
    ("Z-20303279", ("solitaire", "budget")),
    ("Z-20046552", ("halo-pave", "budget")),
)

COMBINED_IDS = {
    "MENE-ROSE": "mene-rose",
    "MENE-KNOT": "mene-knot",
    "AV-BRIDGE": "av-bridge",
    "AV-CLEAN": "av-clean",
}

# dashboard id -> (root retailer id, combined seller id)
RETAILER_METADATA = (
    ("sarraf", "sarraf", "sarraf"),
    ("automic-gold", "automic-gold", "automic"),
    ("mejuri", "mejuri", "mejuri"),
    ("stone-and-strand", "stone-and-strand", "stone-and-strand"),
    ("auvere", None, "auvere"),
    ("mene", None, "mene"),
    ("blue-nile", "blue-nile", "bluenile"),
    ("brilliant-earth", "brilliant-earth", "brilliant-earth"),
    ("vrai", "vrai", "vrai"),
    ("zales", "zales", "zales"),
    ("factory-direct-jewelry", "factory-direct-jewelry", "factory-direct"),
)


def load_json(root: Path, relative: str):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def canonical(root: Path) -> dict:
    root = Path(root)
    rows = []
    for relative in ROOT_LISTING_FILES:
        rows.extend(load_json(root, relative)["items"])
    catalog = load_json(root, "data/catalog.json")
    evidence = load_json(root, "research/evidence.json")
    return {
        "root": root,
        "rows": rows,
        "row_by_id": {row["id"]: row for row in rows},
        "catalog": catalog,
        "product_by_id": {product["id"]: product for product in catalog["products"]},
        "seller_by_id": {seller["id"]: seller for seller in catalog["sellers"]},
        "sources": {source["id"]: source for source in evidence["sources"]},
        "review": load_json(root, "data/review.json")["findings"],
        "retailer_by_id": {
            retailer["id"]: retailer
            for retailer in load_json(root, "data/retailers.json")["retailers"]
        },
        "gold": load_json(root, "data/gold-price.json"),
    }


def numeric_tokens(text: str) -> list[float]:
    values = []
    for token in re.findall(r"(?<![\d.])\d[\d,]*(?:\.\d+)?(?![\d.])", text):
        try:
            values.append(float(token.replace(",", "")))
        except ValueError:
            pass
    return values


def is_positive_number(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def has_number(text: str, value) -> bool:
    if not is_positive_number(value):
        return False
    return any(abs(candidate - float(value)) < 0.005 for candidate in numeric_tokens(text))


def has_gram_unit(text: str) -> bool:
    return bool(re.search(r"(?<![a-z])(?:g|grams?)\b", text, re.IGNORECASE))


def quotes(root_row: dict, field: str) -> list[str]:
    return list((root_row.get("field_evidence") or {}).get(field) or [])


def explicit_currency_quote(root_row: dict) -> str | None:
    for quote in quotes(root_row, "currency"):
        if re.search(r"\bUSD\b|US\$", quote):
            return quote
    return None


def combined_price_quotes(product: dict, sources: dict) -> tuple[list[str], list[str], str | None]:
    price = product.get("price")
    if not price:
        return [], [], None
    amount_quotes = []
    currency_quotes = []
    currency_url = None
    for reference in price.get("evidence") or []:
        source = sources[reference["source"]]
        quote = source["quotes"][reference["quote"]]
        if has_number(quote, price["amount"]):
            amount_quotes.append(quote)
        if re.search(r"\bUSD\b|US\$", quote):
            currency_quotes.append(quote)
            currency_url = source["url"]
    return amount_quotes, currency_quotes, currency_url


def review_ids(product_source_id: str, findings: list[dict]) -> list[str]:
    return [
        finding["id"]
        for finding in findings
        if product_source_id in (finding.get("sources") or [])
    ]


def special_flags(row_id: str, weight_missing: bool) -> list[str]:
    flags = []
    if row_id in {"SS-MIA", "SS-RITA"}:
        flags.append("DF-001")
    if row_id == "FDJ-GR0001":
        flags.append("DF-002")
    if weight_missing:
        flags.append("DF-003")
    if row_id.startswith("SAR-"):
        flags.append("DF-004")
    if row_id in {"AG-SAPPHIRE-RING", "AV-BRIDGE", "AV-CLEAN"}:
        flags.append("DF-005")
    if row_id.startswith("Z-"):
        flags.append("DF-006")
    flags.append("DF-007")
    if row_id == "BN-316238":
        flags.append("DF-008")
    if row_id == "SAR-147371":
        flags.append("DF-012")
    return flags


def from_root(row: dict, categories: tuple[str, ...]) -> dict:
    currency_quote = explicit_currency_quote(row)
    price = (
        row.get("price")
        if row.get("currency") == "USD"
        and is_positive_number(row.get("price"))
        and currency_quote
        and any(has_number(quote, row["price"]) for quote in quotes(row, "price"))
        else None
    )
    weight = (
        row.get("weight_g")
        if is_positive_number(row.get("weight_g"))
        and any(
            has_number(quote, row["weight_g"]) and has_gram_unit(quote)
            for quote in quotes(row, "weight_g")
        )
        else None
    )
    gross = row.get("gross_ring_weight_g")
    if weight is not None:
        basis = row.get("weight_basis") or "Seller-reported metal weight"
        weight_note = f"Seller-reported metal weight: {weight:.2f} g. {basis}. Not independently weighed."
    elif gross is not None:
        weight_note = (
            f"Blank metal-only weight. A separate gross/item display of {gross:g} g is retained "
            "in canonical evidence but is not used for melt arithmetic."
        )
    else:
        weight_note = "Blank — no seller metal-only gram weight is confirmed in the canonical record."

    identity_mismatch = row.get("verification_status") == "partial_identity_mismatch"
    if price is not None:
        price_note = (
            f"Dated {row['retrieved_at']} seller display: USD ${price:,.2f}; "
            f"scope: {row['price_basis'].replace('_', ' ')}. Not a live checkout total."
        )
        unassigned = None
    else:
        displays = []
        if not identity_mismatch:
            if row.get("unassigned_price_text"):
                displays.append(row["unassigned_price_text"])
            displays.extend(row.get("observed_native_display") or [])
        unassigned = "; ".join(dict.fromkeys(displays)) or None
        if identity_mismatch:
            price_note = (
                "Blank — the canonical record flags a product-identity mismatch at this URL. "
                "No amount is assigned to this stored item; see F-041/F-042."
            )
        elif unassigned:
            price_note = (
                f"Blank structured price/currency. Unassigned dated display: {unassigned}. "
                "Its ISO currency, configuration, or price role is not confirmed."
            )
        else:
            price_note = "Blank — no configuration-specific ISO-USD price is assigned in the canonical record."

    currency_quote = currency_quote if price is not None else None
    return {
        "id": row["id"],
        "retailer_id": row["retailer_id"],
        "retailer": row["retailer"],
        "categories": list(categories),
        "name": row["name"],
        "karat": row["karat"],
        "solid_gold_explicit": row.get("solid_gold_explicit") if isinstance(row.get("solid_gold_explicit"), bool) else None,
        "hallmark_stated": row.get("hallmark_stated") if isinstance(row.get("hallmark_stated"), bool) else None,
        "weight_g": weight,
        "weight_note": weight_note,
        "price_usd": price,
        "price_note": price_note,
        "unassigned_display": unassigned,
        "capture_date": row["retrieved_at"],
        "product_url": row["source_url"],
        "quote": quotes(row, "name")[0],
        "price_quotes": quotes(row, "price") if price is not None else [],
        "currency_quotes": [currency_quote] if currency_quote else [],
        "currency_source_url": (row.get("currency_source_url") or row["source_url"]) if price is not None else None,
        "weight_quotes": quotes(row, "weight_g") if weight is not None else [],
        "weight_source_url": row["source_url"] if weight is not None else None,
        "evidence_link": "../" + row["evidence_file"],
        "evidence_label": "Canonical item evidence",
        "verification_status": row.get("verification_status"),
        "flags": special_flags(row["id"], weight is None),
        "canonical_flags": list(row.get("flags") or []),
        "review_flags": [],
        "canonical_product_id": None,
    }


def from_combined(product: dict, categories: tuple[str, ...], data: dict) -> dict:
    sources = data["sources"]
    primary = sources[product["source"]]
    seller = data["seller_by_id"][product["seller"]]
    facts = product["facts"]
    karat = facts["karat"]["value"]
    solid = facts["solidGold"]["value"] if facts["solidGold"] else None
    hallmark = facts["hallmark"]["value"] if facts["hallmark"] else None

    # Only an explicit net/seller-metal single value can populate the metal-weight cell.
    weight = None
    weight_quotes = []
    weight_source_url = None
    net = facts.get("netMetalWeightG")
    if net:
        candidate = net.get("value")
        source = sources[net["source"]]
        quote = source["quotes"][net["quote"]]
        if is_positive_number(candidate) and has_number(quote, candidate) and has_gram_unit(quote):
            weight = candidate
            weight_quotes = [quote]
            weight_source_url = source["url"]
    elif product.get("reportedWeight"):
        reported = product["reportedWeight"]
        candidate = reported.get("min")
        source = sources[reported["evidence"]["source"]]
        quote = source["quotes"][reported["evidence"]["quote"]]
        if (
            reported["basis"] == "seller-metal"
            and reported["min"] == reported["max"]
            and is_positive_number(candidate)
            and has_number(quote, candidate)
            and has_gram_unit(quote)
        ):
            weight = candidate
            weight_quotes = [quote]
            weight_source_url = source["url"]

    reported = product.get("reportedWeight")
    if weight is not None:
        weight_note = f"Seller-reported metal weight: {weight:.2f} g. Not independently weighed."
    elif reported:
        basis_note = (
            "with an unresolved 'Fine Weight' definition"
            if reported.get("basis") == "fine-undefined"
            else f"with reported basis {reported.get('basis')!r}"
        )
        weight_note = (
            f"Blank single metal weight. Seller publishes a {reported['min']:g}–{reported['max']:g} g "
            f"range {basis_note}; it is not converted into product fine-gold mass."
        )
    else:
        weight_note = "Blank — no seller metal-only gram weight is confirmed in the canonical record."

    price_quotes, currency_quotes, currency_url = combined_price_quotes(product, sources)
    price = None
    if (
        product.get("price")
        and product["price"]["currency"] == "USD"
        and is_positive_number(product["price"].get("amount"))
        and price_quotes
        and currency_quotes
    ):
        price = product["price"]["amount"]
    if price is not None:
        price_note = (
            f"Dated {product['price']['observedAt'][:10]} seller display: USD ${price:,.2f}; "
            f"scope: {product['price']['scope']}. Not a live checkout total."
        )
    else:
        price_note = "Blank — no configuration-specific ISO-USD price is assigned in the canonical record."

    return {
        "id": next(key for key, value in COMBINED_IDS.items() if value == product["id"]),
        "retailer_id": product["seller"],
        "retailer": seller["name"],
        "categories": list(categories),
        "name": product["name"]["value"],
        "karat": karat,
        "solid_gold_explicit": solid if isinstance(solid, bool) else None,
        "hallmark_stated": hallmark if isinstance(hallmark, bool) else None,
        "weight_g": weight,
        "weight_note": weight_note,
        "price_usd": price,
        "price_note": price_note,
        "unassigned_display": None,
        "capture_date": product["observedAt"][:10],
        "product_url": primary["url"],
        "quote": primary["quotes"][product["name"]["quote"]],
        "price_quotes": price_quotes if price is not None else [],
        "currency_quotes": currency_quotes if price is not None else [],
        "currency_source_url": currency_url if price is not None else None,
        "weight_quotes": weight_quotes,
        "weight_source_url": weight_source_url,
        "evidence_link": f"../explore/sources/#{product['source']}",
        "evidence_label": f"Combined evidence record {product['source']}",
        "verification_status": "canonical_combined_record",
        "flags": special_flags(
            next(key for key, value in COMBINED_IDS.items() if value == product["id"]),
            weight is None,
        ),
        "canonical_flags": [],
        "review_flags": review_ids(product["source"], data["review"]),
        "canonical_product_id": product["id"],
    }


def build_rings(repo_root: Path) -> list[dict]:
    data = canonical(repo_root)
    rings = []
    for row_id, categories in RING_METADATA:
        if row_id in data["row_by_id"]:
            ring = from_root(data["row_by_id"][row_id], categories)
        elif row_id in COMBINED_IDS:
            product = data["product_by_id"][COMBINED_IDS[row_id]]
            ring = from_combined(product, categories, data)
        else:
            raise ValueError(f"No canonical product record for {row_id}")
        if ring["solid_gold_explicit"] is not True:
            ring["flags"].append("DF-010")
        if ring["price_usd"] is None:
            ring["flags"].append("DF-011")
        ring["flags"] = list(dict.fromkeys(ring["flags"]))
        rings.append(ring)
    return rings


def reputation_summary(reputation: dict) -> tuple[str | None, str | None]:
    url = reputation.get("profile_url") or reputation.get("candidate_profile_url")
    if not url:
        return None, None
    if reputation.get("identity_status") == "candidate_name_match_not_confirmed":
        return "Candidate BBB profile identity unconfirmed; all metrics withheld.", url
    parts = []
    if reputation.get("bbb_accredited") is not None:
        parts.append("BBB accredited" if reputation["bbb_accredited"] else "Not BBB accredited")
    if reputation.get("bbb_rating"):
        parts.append(f"BBB rating {reputation['bbb_rating']}")
    if reputation.get("review_average_out_of_5") is not None:
        if reputation.get("review_count") is not None:
            parts.append(
                f"{reputation['review_average_out_of_5']:g}/5 across {reputation['review_count']} reviews"
            )
        else:
            parts.append(f"{reputation['review_average_out_of_5']:g}/5 review average; review count unconfirmed")
    if reputation.get("complaints_last_3_years") is not None:
        if reputation.get("complaints_last_12_months") is not None:
            parts.append(
                f"{reputation['complaints_last_3_years']} complaints/3 years; "
                f"{reputation['complaints_last_12_months']} in 12 months"
            )
        else:
            parts.append(f"{reputation['complaints_last_3_years']} complaints/3 years; 12-month count unconfirmed")
    if reputation.get("profile_scope"):
        parts.append(reputation["profile_scope"])
    parts.append("Profile metrics and allegations are not physical purity tests.")
    return "; ".join(parts), url


def root_retailer(retailer: dict, dashboard_id: str, product_url: str) -> dict:
    reputation = retailer["independent_reputation"]
    bbb_summary, bbb_url = reputation_summary(reputation)
    contact_parts = [retailer.get("contact_phone"), retailer.get("contact_email")]
    contact_parts.extend(retailer.get("contact_channels") or [])
    contact_summary = "; ".join(dict.fromkeys(part for part in contact_parts if part)) or None
    exclusions = retailer.get("return_exclusions_detail")
    if retailer.get("resize_policy"):
        exclusions = (exclusions + " " if exclusions else "") + retailer["resize_policy"]
    unverified = []
    if retailer.get("return_window_days") is None:
        unverified.append("return window")
    if not exclusions:
        unverified.append("return exclusions / resizing details")
    if not retailer.get("payment_methods_verified"):
        unverified.append("payment methods")
    if not contact_summary:
        unverified.append("contact details")
    if not bbb_url or reputation.get("identity_status") == "candidate_name_match_not_confirmed":
        unverified.append("independent reputation identity")
    unverified.append("order-specific independent inspection/return permission")
    return {
        "id": dashboard_id,
        "name": retailer["name"],
        "site_url": retailer["website"],
        "contact_url": retailer["contact_source_url"],
        "returns_url": retailer["return_policy_url"],
        "jewelry_notes_url": product_url,
        "bbb_url": bbb_url,
        "contact_summary": contact_summary,
        "return_window": retailer.get("return_window_basis"),
        "resized_custom_rule": exclusions,
        "payment_protection": retailer.get("payment_note") if retailer.get("payment_methods_verified") else None,
        "bbb_summary": bbb_summary,
        "unverified_fields": unverified,
        "evidence_link": "../" + retailer["evidence_file"],
        "evidence_label": "Canonical seller evidence",
        "reputation_evidence_link": "../" + retailer["evidence_file"],
        "capture_date": reputation.get("retrieved_at"),
    }


def combined_retailer(seller: dict, dashboard_id: str, data: dict, product_url: str) -> dict:
    sources = data["sources"]
    policy = sources.get(seller.get("policy")) if seller.get("policy") else None
    contact = sources.get(seller.get("contact")) if seller.get("contact") else None
    independent = sources.get(seller.get("independent")) if seller.get("independent") else None
    # Derive only the origin from an existing official source; no new destination is invented.
    origin_source = policy or contact or independent
    if origin_source is None:
        product = next(p for p in data["catalog"]["products"] if p["seller"] == seller["id"])
        origin_source = sources[product["source"]]
    parsed = urlsplit(origin_source["url"])
    site_url = f"{parsed.scheme}://{parsed.netloc}/"
    return_days = seller.get("returnDays")
    return_window = None
    if return_days:
        return_window = f"{return_days['value']} days from {seller.get('returnFrom') or 'unconfirmed trigger'}"
    related = [source for source in (policy, contact, independent) if source]
    capture_date = max((source["observedAt"][:10] for source in related), default=None)
    unverified = ["published contact details (not tested)", "payment methods", "order-specific independent inspection/return permission"]
    if not return_window:
        unverified.insert(0, "return window")
    if not seller.get("summary"):
        unverified.append("return exclusions / resizing details")
    if not independent:
        unverified.append("independent reputation")
    return {
        "id": dashboard_id,
        "name": seller["name"],
        "site_url": site_url,
        "contact_url": (contact or policy or origin_source)["url"],
        "returns_url": (policy or contact or origin_source)["url"],
        "jewelry_notes_url": product_url,
        "bbb_url": independent["url"] if independent else None,
        "contact_summary": None,
        "return_window": return_window,
        "resized_custom_rule": seller.get("summary"),
        "payment_protection": None,
        "bbb_summary": (
            f"Independent platform record linked ({independent['publisher']}); metrics are not normalized here. "
            "Reviews and complaints are not physical purity tests."
            if independent else None
        ),
        "unverified_fields": list(dict.fromkeys(unverified)),
        "evidence_link": f"../explore/sources/#{origin_source['id']}",
        "evidence_label": f"Combined evidence record {origin_source['id']}",
        "reputation_evidence_link": f"../explore/sources/#{independent['id']}" if independent else None,
        "capture_date": capture_date,
    }


def build_retailers(repo_root: Path) -> list[dict]:
    data = canonical(repo_root)
    products_by_seller = {}
    for product in data["catalog"]["products"]:
        products_by_seller.setdefault(product["seller"], data["sources"][product["source"]]["url"])
    retailers = []
    for dashboard_id, root_id, combined_id in RETAILER_METADATA:
        product_url = products_by_seller[combined_id]
        if root_id and root_id in data["retailer_by_id"]:
            retailers.append(root_retailer(data["retailer_by_id"][root_id], dashboard_id, product_url))
        else:
            retailers.append(combined_retailer(data["seller_by_id"][combined_id], dashboard_id, data, product_url))
    return retailers


def build_gold_reference(repo_root: Path) -> dict:
    gold = load_json(Path(repo_root), "data/gold-price.json")
    return {
        "retrieved_at": gold["retrieved_at"],
        "spot_usd_per_troy_oz": gold["usd_per_troy_oz"],
        "chart_as_of_date": gold.get("chart_as_of_date"),
        "quote_timestamp_confirmed": gold.get("quote_date") is not None,
        "usd_per_fine_gram": round(gold["usd_per_troy_oz"] / gold["grams_per_troy_ounce"], 6),
        "spot_source_name": gold["source_name"],
        "spot_source_url": gold["source_url"],
        "spot_quotes": list(gold["evidence_quotes"]),
        "troy_ounce": {
            "grams": gold["grams_per_troy_ounce"],
            "pennyweight_grams": 1.55517384,
            "carat_grams": 0.2,
            "sources": [
                "https://www.nist.gov/pml/owm/approximate-conversions-us-customary-measures-metric",
                gold["conversion_source_url"],
            ],
        },
        "lbma_price_method": {
            "sources": [
                gold["source_url"],
                "https://www.lbma.org.uk/prices-and-data/precious-metal-prices",
            ]
        },
        "karat_definition": {"manual_review_links": [gold["karat_source_url"]]},
        "hallmark_law": [
            {
                "title": "FTC Guides for the Jewelry Industry — 16 CFR § 23.3 (Misrepresentation as to gold content)",
                "source": gold["karat_source_url"],
            },
            {
                "title": "National Stamping Act — 15 U.S.C. §§ 294–300",
                "source": "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap8",
            },
        ],
    }
