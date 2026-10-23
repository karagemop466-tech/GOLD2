#!/usr/bin/env python3
"""Apply the 2026-10-23 live re-verification findings to the root register.

Every change below is tied to a page actually retrieved on 2026-10-23 (UTC) with
`fetch_page`. Quotes added to `field_evidence` are also appended verbatim to the
matching evidence/*.md file, because tools/qa.py requires every stored quote to
resolve inside its own evidence file.

Run from the repository root:
    python3 audit/8b9e189a/apply_reverification_2026-10-23.py

The script is idempotent: running it twice produces the same files.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
TODAY = "2026-10-23"

BLUE_NILE = "https://www.bluenile.com/engagement-rings/design-your-own-ring/"
ZALES = "https://www.zales.com/"
BE = "https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/"
VRAI = ("https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/"
        "round-brilliant-yellow-gold-32797281484893")
AG = "https://www.automicgold.com/products/"
CART = "https://www.automicgold.com/cart.js"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_item(payload: dict, item_id: str) -> dict:
    for item in payload["items"]:
        if item["id"] == item_id:
            return item
    raise SystemExit(f"missing item {item_id}")


def add_flag(item: dict, flag_id: str) -> None:
    if flag_id not in item["flags"]:
        item["flags"].append(flag_id)
        item["flags"].sort()


def drop_flag(item: dict, flag_id: str) -> None:
    if flag_id in item["flags"]:
        item["flags"].remove(flag_id)


def append_evidence(relative: str, heading: str, lines: list[str]) -> None:
    """Append a dated re-verification block once (idempotent by heading)."""
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if heading in text:
        return
    block = ["", heading, ""] + lines + [""]
    path.write_text(text.rstrip("\n") + "\n" + "\n".join(block), encoding="utf-8")


# ---------------------------------------------------------------- gold quote
gold_path = DATA / "gold-price.json"
gold = load(gold_path)
previous = gold.get("usd_per_troy_oz")
superseded = [entry for entry in gold.get("superseded_observations", []) if entry.get("value") != previous]
if previous is not None and previous != 4024.45 and not any(e.get("value") == previous for e in superseded):
    superseded.insert(0, {
        "value": previous,
        "currency": "USD",
        "quote_date": None,
        "retrieved_at": gold.get("retrieved_at"),
        "chart_as_of_date": gold.get("chart_as_of_date"),
        "status": "superseded_moving_header",
        "reason": ("Header value observed on the previous retrieval date. The moving header is not "
                   "a fixed benchmark; only the value observed on 2026-10-23 is used in calculations."),
    })
gold["usd_per_troy_oz"] = 4024.45
gold["retrieved_at"] = TODAY
gold["quote_date"] = None
gold["chart_as_of_date"] = "2026-10-22"
gold["evidence_quotes"] = ["4,024.45", "Data as of 22 October, 2026"]
gold["field_evidence"] = {
    "usd_per_troy_oz": ["USD\n\n/oz\n\n-\n\n4,024.45"],
    "source_name": ["Market Data: Provided by ICE Data Services."],
    "grams_per_troy_ounce": ["| 1 troy ounce | 1 | 20 | 480 | 31.103 476 8 | 31 103.476 8 |"],
    "karat_basis": ["fine (24 karat) gold", "an item marked 18 k is made of 75 % gold"],
    "chart_as_of_date": ["Data as of 22 October, 2026"],
}
gold["superseded_observations"] = superseded
gold["quote_scope"] = ("Moving-header observation retrieved 2026-10-23; exact quote-as-of timestamp is "
                       "unconfirmed (F-026). The chart's stated date is stored separately and is not "
                       "assigned to the header.")
gold["limits_note"] = gold.get("limits_note") or ""
save(gold_path, gold)

append_evidence("evidence/gold-price.md", "## Re-verification — 2026-10-23 (UTC)", [
    "Direct page fetch of https://www.gold.org/goldhub/data/gold-prices.",
    "",
    "### Current observation (`usd_per_troy_oz`) — retrieved 2026-10-23",
    "",
    "```",
    "USD",
    "",
    "/oz",
    "",
    "-",
    "",
    "4,024.45",
    "```",
    "",
    "### Chart date shown on the same page",
    "",
    "```",
    "Data as of 22 October, 2026",
    "```",
    "",
    "The moving header carries no rendered quote timestamp, so `quote_date` stays `null` (F-026).",
    "The prior observation, 4,028.53 with chart date 21 October 2026, is retained only inside",
    "`superseded_observations`; it is not used in any calculation and no page renders it.",
])

# ------------------------------------------------------- listing corrections
files = {path.stem: path for path in sorted((DATA / "listings").glob("*.json"))}
files["solid-gold-verified"] = DATA / "solid-gold-verified.json"
payloads = {stem: load(path) for stem, path in files.items()}

# Blue Nile: all ten rows re-read today; displayed setting prices and stock numbers matched.
blue_nile_rows = {
    "BN-203348": ("classic-simple-solitaire-engagement-ring-in-14k-yellow-gold-item-203348",
                  ["$1,145(Setting Price)"], "502120y14", "2.40mm"),
    "BN-195639": ("petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639",
                  ["$1,000(Setting Price)"], "501130y14", "1.80mm"),
    "BN-194548": ("solitaire-compass-set-engagement-ring-in-14k-white-gold-item-194548",
                  ["$1,045(Setting Price)"], "501290w14", "2.00mm"),
    "BN-192506": ("petite-hidden-halo-solitaire-plus-diamond-engagement-ring-in-14k-yellow-gold-item-192506",
                  ["$1,255(Setting Price)"], "502250y14", "1.60mm"),
    "BN-315661": ("pave-contour-diamond-engagement-ring-in-14k-white-gold-by-james-allen-item-315661",
                  ["$2,210(Setting Price)"], "505094w14", "1.75mm"),
    "BN-195402": ("petite-micropave-diamond-engagement-ring-in-14k-white-gold-1-10-ct-tw-item-195402",
                  ["$1,300(Setting Price)"], "501480w14", "1.70mm"),
    "BN-302868": ("petite-micropave-lab-grown-diamond-engagement-ring-in-14k-white-gold-1-10-ct-tw-item-302868",
                  ["$1,050(Setting Price)"], "501480w14l", "1.70mm"),
    "BN-194158": ("classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
                  ["$1,125(Setting Price)"], "500000y", "1.90mm"),
    "BN-195269": ("petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269",
                  ["$1,155(Setting Price)"], "501130y", "1.80mm"),
    "BN-193625": ("petite-three-stone-diamond-engagement-ring-in-14k-yellow-gold-item-193625",
                  ["$1,950(Setting Price)"], "502350y14", "1.80mm"),
}
for stem, payload in payloads.items():
    for item in payload["items"]:
        if item["id"] not in blue_nile_rows:
            continue
        slug, display, sku, width = blue_nile_rows[item["id"]]
        item["retrieved_at"] = TODAY
        item["observed_native_display"] = display
        assert item["sku"] == sku, (item["id"], item["sku"], sku)
        assert f"{item['width_mm']:.2f}mm" == width, (item["id"], item["width_mm"], width)
        append_evidence(item["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
            f"- **URL:** {BLUE_NILE}{slug}",
            "- **Result:** the page rendered the same stock number, metal, width and setting price as the",
            "  stored observation. No displayed value was changed, inferred or added.",
            "", "```", display[0], "```", "",
            f"```\nStock Number\n\n{sku}\n\nWidth\n\n{width}\n```", "",
            "- Product pages still do not state gram weight, the words \u201csolid gold\u201d, a hallmark, a",
            "  maker\u2019s mark, or an ISO currency code (F-001, F-002, F-003, F-025).",
        ])

# Zales rows -----------------------------------------------------------------
z_19957449 = find_item(payloads["budget"], "Z-19957449")
z_19957449["retrieved_at"] = TODAY

z_20046552 = find_item(payloads["budget"], "Z-20046552")
z_20046552["retrieved_at"] = TODAY
z_20046552["unassigned_price_text"] = "$909.30  $1,299.00 30% Off"
z_20046552["verification_status"] = "partial_price_unassigned"
z_20046552["observed_native_display"] = ["$909.30  $1,299.00 30% Off"]
z_20046552["field_evidence"]["price"] = ["$909.30  $1,299.00 30% Off"]
z_20046552["field_evidence"]["original_price"] = ["$909.30  $1,299.00 30% Off"]
z_20046552["field_evidence"]["currency"] = ["$909.30  $1,299.00 30% Off"]
z_20046552["field_evidence"]["unassigned_price_text"] = ["$909.30  $1,299.00 30% Off"]
z_20046552["render_history"] = [{
    "retrieved_at": "2026-10-22",
    "rendered": ["Discounted Price $909.30", "Original Price was $1,299.00"],
    "note": "Labeled amounts on the earlier render; the 2026-10-23 render of the same URL dropped the labels.",
}]
add_flag(z_20046552, "F-018")
append_evidence(z_20046552["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** " + ZALES + "12-ct-tw-multidiamond-cushion-frame-engagement-ring-10k-gold/p/V-20046552",
    "- **Result:** the page rendered two amounts and a discount with **no** Discounted/Original labels.",
    "  The earlier labeled render is kept only as dated render history; neither amount is assigned.",
    "", "```", "$909.30  $1,299.00 30% Off", "```",
])

z_20303279 = find_item(payloads["three-stone-vintage"], "Z-20303279")
z_20303279["retrieved_at"] = TODAY
z_20303279["verification_status"] = "partial_price_unverified"
z_20303279["unassigned_price_text"] = None
z_20303279["observed_native_display"] = ["Discounted Price $979.30  Original Price was $1,399.00 30% Off"]
z_20303279["field_evidence"].pop("unassigned_price_text", None)
z_20303279["field_evidence"]["price"] = ["Discounted Price $979.30  Original Price was $1,399.00 30% Off"]
z_20303279["field_evidence"]["currency"] = ["Discounted Price $979.30  Original Price was $1,399.00 30% Off"]
drop_flag(z_20303279, "F-018")
add_flag(z_20303279, "F-025")
append_evidence(z_20303279["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** " + ZALES + "12-ct-tw-diamond-frame-vintagestyle-twist-shank-engagement-ring-10k-gold/p/V-20303279",
    "- **Result:** the page now renders explicit labels. Both amounts stay unassigned because the page",
    "  states no ISO currency (F-025); no amount is placed into the current/original cells.",
    "", "```", "Discounted Price $979.30  Original Price was $1,399.00 30% Off", "```",
])

z_20301172 = find_item(payloads["three-stone-vintage"], "Z-20301172")
z_20301172["retrieved_at"] = TODAY
z_20301172["verification_status"] = "partial_price_unverified"
z_20301172["unassigned_price_text"] = None
z_20301172["observed_native_display"] = ["Discounted Price $769.30  Original Price was $1,099.00 30% Off"]
z_20301172["field_evidence"].pop("unassigned_price_text", None)
z_20301172["field_evidence"]["price"] = ["Discounted Price $769.30  Original Price was $1,099.00 30% Off"]
z_20301172["field_evidence"]["currency"] = ["Discounted Price $769.30  Original Price was $1,099.00 30% Off"]
drop_flag(z_20301172, "F-018")
add_flag(z_20301172, "F-025")
append_evidence(z_20301172["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** " + ZALES + "13-ct-tw-diamond-three-stone-engagement-ring-10k-gold/p/V-20301172",
    "- **Result:** the page now renders explicit labels. Both amounts stay unassigned because the page",
    "  states no ISO currency (F-025); no amount is placed into the current/original cells.",
    "", "```", "Discounted Price $769.30  Original Price was $1,099.00 30% Off", "```",
])

# Brilliant Earth ------------------------------------------------------------
be = find_item(payloads["solitaire"], "BE-121H6")
be["retrieved_at"] = TODAY
be["price"] = 890.0
be["currency"] = "USD"
be["verification_status"] = "partial_official_fields"
be["currency_source_url"] = BE
be["currency_evidence"] = ('The product page header renders a currency selector reading "USD", and the '
                           'setting price is labeled "$890(Setting Only)".')
be["field_evidence"]["price"] = ["$890(Setting Only)"]
be["field_evidence"]["currency"] = ["$890(Setting Only)", "USD"]
be["field_evidence"]["price_basis"] = ["$890(Setting Only)"]
be["field_evidence"]["center_stone_included"] = ["$890(Setting Only)"]
be["superseded_observations"] = [{
    "price": 990.0,
    "currency": "EUR",
    "display": "\u20ac 990.00(Setting Only)",
    "retrieved_at": "2026-10-22",
    "status": "superseded_region_currency",
    "reason": ("The 2026-10-22 retrieval was served a euro price while the 2026-10-23 retrieval was "
               "served a dollar price with a USD selector. Neither is converted; only the dated USD "
               "observation is used in calculations."),
}]
be["notes"] = ("Served currency changed between retrievals (EUR \u20ac990 on 2026-10-22; USD $890 on "
               "2026-10-23 with a USD selector). Setting-only price; centre stone excluded.")
add_flag(be, "F-032")
append_evidence(be["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** " + BE,
    "- **Result:** the page rendered a **USD** selector and a dollar setting price. The euro amount",
    "  recorded on 2026-10-22 is retained only as a superseded, non-converted observation.",
    "", "```", "$890(Setting Only)", "```", "", "```", "USD", "```", "",
    "```", "\u20ac 990.00(Setting Only)", "```", "",
    "Unchanged and re-confirmed on the same page: Style BE121H6-14KY, Metal 14K Yellow Gold,",
    "Prong metal 14K White Gold, Width 2.5 mm, Six-Prong setting.",
])

# VRAI ----------------------------------------------------------------------
vrai = find_item(payloads["18k"], "VRAI-CLASSIC-4P")
vrai["retrieved_at"] = TODAY
append_evidence(vrai["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** " + VRAI,
    "- **Result:** Setting Details re-rendered the same metal, band depth and size-6 metal weight.",
    "  No price string was present in the retrieved text; the price stays blank (F-008).",
    "", "```",
    "Metal:18k Yellow Gold",
    "Band width:Standard",
    "Band depth:1.6mm",
    "Metal weight:2.86g (Ring size 6)",
    "Pav\u00e9 carat weight:0.18ctw",
    "```", "",
    "The page still shows a pav\u00e9-carat line on a setting titled \u201cPlain Band\u201d; that",
    "inconsistency is preserved as observed and is not resolved by assumption (see F-033).",
])

# Automic Gold --------------------------------------------------------------
for item_id, payload_name, evidence, display in (
    ("AG-COFFIN-RING", "solid-gold-verified", "evidence/listings/ag-coffin-ring.md", "$1,910"),
    ("AG-SAPPHIRE-RING", "solid-gold-verified", "evidence/listings/ag-sapphire-ring.md", "$526"),
    ("AG-CUSHION-SIGNET", "solid-gold-verified", "evidence/listings/ag-cushion-signet.md", "$2,758"),
):
    item = find_item(payloads[payload_name], item_id)
    item["currency_source_url"] = CART
    item["currency_evidence"] = ('The store\u2019s public cart endpoint reports "currency":"USD"; the item '
                                 'price is displayed with a dollar sign.')
    quotes = item["field_evidence"].setdefault("currency", [])
    if '"currency":"USD"' not in quotes:
        quotes.append('"currency":"USD"')
    if item_id in ("AG-COFFIN-RING", "AG-SAPPHIRE-RING"):
        item["retrieved_at"] = TODAY
    append_evidence(evidence, "## Re-verification — 2026-10-23 (UTC)", [
        f"- **Currency source:** {CART}",
        "- **Result:** the public cart endpoint reports the store currency, which is the only formal",
        "  currency statement found for this retailer. It is quoted verbatim, not inferred.",
        "", "```", '"currency":"USD"', "```", "",
        f"- **Product page re-read 2026-10-23:** {AG}{item['sku']}"
        + ("" if item_id != "AG-CUSHION-SIGNET" else " (not re-read this pass; observation date unchanged)"),
        "", "```", display, "```",
    ])

# Mejuri --------------------------------------------------------------------
mj = find_item(payloads["solid-gold-verified"], "MJ-BOLD-ETERNITY")
mj["retrieved_at"] = TODAY
mj["price"] = None
mj["currency"] = None
mj["verification_status"] = "partial_price_unverified"
mj["observed_native_display"] = ["From$2,900"]
mj["field_evidence"]["currency"] = ["From$2,900"]
mj["notes"] = ("Product page re-read 2026-10-23: still \u201cFrom\u2009$2,900\u201d, 2.6\u202fmm band, "
               "23 round brilliant diamonds, 1.15\u20131.57 ct, GHI, SI\u2013I. No official Mejuri page "
               "retrieved states the ISO currency, so the amount is displayed verbatim but not assigned "
               "as a USD price (F-025).")
add_flag(mj, "F-025")
append_evidence(mj["evidence_file"], "## Re-verification — 2026-10-23 (UTC)", [
    "- **URL:** https://mejuri.com/products/bold-diamond-eternity-ring",
    "- **Result:** the page re-rendered the same starting price, band width and diamond specification.",
    "  No ISO currency statement was found on the product page, the payment FAQ, or the store cart",
    "  endpoint (which returned a 404 page), so the amount is **not** assigned as USD.",
    "", "```", "From$2,900", "```", "", "```",
    "Band Width: 2.6 mm",
    "Minimum Carat Weight: 1.15 ct - 1.57 ct",
    "Diamond Clarity: SI - I",
    "Diamond Color: GHI",
    "Stone Size: 2.5 mm",
    "```", "",
    "The page also states \u201cFree 30-day returns & exchanges \u2026 Some exclusions apply\u201d and",
    "\u201cEngraving is optional (complimentary) and not eligible for returns.\u201d",
])

for stem, payload in payloads.items():
    save(files[stem], payload)

# ------------------------------------------------------------------- flags
flags_path = DATA / "flags.json"
flags = load(flags_path)
by_id = {flag["id"]: flag for flag in flags["flags"]}

by_id["F-007"]["title"] = "Brilliant Earth served a different currency on different retrievals"
by_id["F-007"]["detail"] = (
    "The same official product URL rendered \u20ac990.00 (Setting Only) on 2026-10-22 and "
    "$890 (Setting Only) with a USD currency selector on 2026-10-23. The earlier record described the "
    "page as EUR-only, which was a region-served observation rather than a property of the listing. "
    "Both observations are preserved; only the dated USD observation is used, and no exchange "
    "conversion is applied. Prices from other retailers are not compared with either amount without a "
    "fresh native-currency quote."
)
by_id["F-007"]["recommended_action"] = (
    "Confirm the currency at checkout for the delivery country before comparing Brilliant Earth with "
    "any other row; re-read the page instead of reusing a cached amount."
)

by_id["F-018"]["title"] = "One Zales page renders unlabeled price amounts"
by_id["F-018"]["detail"] = (
    "On 2026-10-23 Z-20046552 rendered \u201c$909.30  $1,299.00 30% Off\u201d with no Discounted/Original "
    "labels. The earlier render of the same URL did carry labels; both renders are preserved as dated "
    "evidence and neither amount is assigned by position or by discount arithmetic. The two other "
    "Zales rows re-read on the same date did render explicit labels and are covered by F-025 (ISO "
    "currency unconfirmed) instead."
)
by_id["F-018"]["affected_items"] = ["Z-20046552"]
by_id["F-018"]["sources"] = [
    "https://www.zales.com/12-ct-tw-multidiamond-cushion-frame-engagement-ring-10k-gold/p/V-20046552"
]

f25 = by_id["F-025"]
f25["detail"] = (
    "The official excerpts establish displayed dollar-sign amounts, but not the ISO currency of the "
    "selected configuration. Those amounts are now shown verbatim in the register and are **not** "
    "copied into the assigned price/currency cells. Two exceptions are recorded only because the "
    "retailer publishes its own currency statement: Automic Gold\u2019s public cart endpoint reports "
    '"currency":"USD", and the Brilliant Earth page renders a USD selector next to the price. Mejuri '
    "shows \u201cFrom$2,900\u201d but no official currency statement was found, so its amount is displayed "
    "and left unassigned."
)
f25["recommended_action"] = (
    "Read the documented amount, then confirm the native ISO currency and the exact size/configuration "
    "price at checkout before comparing with the USD gold reference or with another retailer."
)
for extra, url in (
    ("Z-20303279", "https://www.zales.com/12-ct-tw-diamond-frame-vintagestyle-twist-shank-engagement-ring-10k-gold/p/V-20303279"),
    ("Z-20301172", "https://www.zales.com/13-ct-tw-diamond-three-stone-engagement-ring-10k-gold/p/V-20301172"),
    ("MJ-BOLD-ETERNITY", "https://mejuri.com/products/bold-diamond-eternity-ring"),
):
    if extra not in f25["affected_items"]:
        f25["affected_items"].append(extra)
    if url not in f25["sources"]:
        f25["sources"].append(url)

by_id["F-026"]["detail"] = (
    "The World Gold Council page renders a moving spot header without a quote timestamp next to it. "
    "On 2026-10-23 the header read 4,024.45 USD/oz while the chart on the same page stated \u201cData as "
    "of 22 October, 2026\u201d. The chart date is stored as chart_as_of_date and is **not** assigned to "
    "the header; quote_date stays null. Earlier header observations from previous days are retained "
    "only inside superseded_observations and are not rendered as current values. Calculations are "
    "conditional arithmetic at the retrieved value, not a valuation."
)
by_id["F-026"]["recommended_action"] = (
    "Read the live page and record both the header value and the chart date yourself before using the "
    "calculator; do not treat this register\u2019s dated value as a live quote."
)

new_flags = [
    {
        "id": "F-032",
        "severity": "medium",
        "type": "currency",
        "title": "Retailer-served currency varies between retrievals (Brilliant Earth)",
        "detail": (
            "The same Brilliant Earth URL returned a euro price on 2026-10-22 and a dollar price with a "
            "USD selector on 2026-10-23. Served currency can depend on region or session, so a single "
            "capture cannot establish the currency a buyer will be charged. The register keeps both "
            "dated observations and converts neither."
        ),
        "affected_items": ["BE-121H6"],
        "affected_retailers": ["brilliant-earth"],
        "sources": [BE],
        "recommended_action": (
            "Place the same configuration in the cart for the delivery country and record the charged "
            "currency and amount before comparing it with any other ring."
        ),
    },
    {
        "id": "F-033",
        "severity": "medium",
        "type": "irregularity",
        "title": "Inherited register assigned USD to some dollar-sign prices and blanked others",
        "detail": (
            "The inherited data assigned `currency: USD` to Automic Gold and Mejuri rows on the same "
            "dollar-sign evidence that was treated as unconfirmed for Blue Nile and Zales rows. That is "
            "an inconsistent evidence standard, so this pass applied one rule to every row: an assigned "
            "price now needs an official currency statement. Automic Gold is supported by the store\u2019s "
            "cart endpoint (\u201ccurrency\u201d:\u201cUSD\u201d); Brilliant Earth is supported by a rendered USD "
            "selector; Mejuri, Blue Nile and Zales have no retrieved currency statement, so only their "
            "verbatim displayed text is published. No amount was invented or converted."
        ),
        "affected_items": [],
        "affected_retailers": [],
        "sources": [
            CART,
            BE,
            "https://mejuri.com/products/bold-diamond-eternity-ring",
            "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-simple-solitaire-engagement-ring-in-14k-yellow-gold-item-203348",
            ZALES + "15-ct-diamond-solitaire-engagement-ring-10k-gold/p/V-19957449",
        ],
        "recommended_action": (
            "Keep the single documented rule. If a retailer later publishes an official currency "
            "statement, add it to that row\u2019s evidence before assigning the amount."
        ),
    },
]
existing_ids = {flag["id"] for flag in flags["flags"]}
for flag in new_flags:
    if flag["id"] not in existing_ids:
        flags["flags"].append(flag)
flags["generated_at"] = "2026-10-23"
save(flags_path, flags)

print("applied 2026-10-23 re-verification updates")
