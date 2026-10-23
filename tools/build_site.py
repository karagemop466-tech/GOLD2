#!/usr/bin/env python3
"""Build the root GitHub Pages dashboard from source-backed JSON.

The generator renders recorded values only. Missing or ambiguous values remain
blank and link to the flag register. Calculated gold values are labeled as
nominal arithmetic, never as retrieved product facts or physical assays.
"""
from __future__ import annotations

import html
import json
import re
import hashlib
INLINE_STYLES = {}
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT  # Pages is configured as legacy main /.
CATEGORY_FILES = [
    ("solid-gold", DATA / "solid-gold-verified.json"),
    ("solitaire", DATA / "listings" / "solitaire.json"),
    ("halo-pave", DATA / "listings" / "halo-pave.json"),
    ("three-stone-vintage", DATA / "listings" / "three-stone-vintage.json"),
    ("18k", DATA / "listings" / "18k.json"),
    ("budget", DATA / "listings" / "budget.json"),
]
DASH = "&mdash;"

# Counts shown in the shared page shell. They are filled from the data in main()
# so a template can never carry a stale total.
SHELL = {"items": 0, "sellers": 0, "flags": 0, "explore_products": 0, "explore_sellers": 0, "quotes": 0}

CSS = r"""
:root{
  --bg:#fbfaf7;--card:#fff;--ink:#14161a;--muted:#5b6472;--line:#e8e3d8;
  --gold:#8a5f0f;--ok:#1c7a4a;--ok-soft:#e6f4ec;--warn:#8a5a00;--warn-soft:#fdf1dc;
  --bad:#a3261d;--bad-soft:#fbeae8;--info:#1d4d8f;--info-soft:#e8f0fb;
  --radius:14px;--shadow:0 1px 2px rgba(20,22,26,.05),0 8px 24px rgba(20,22,26,.05)
}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--info);text-decoration:none}p a,li a,.note a,dd a,td a{text-decoration:underline;text-underline-offset:2px}a:hover{text-decoration:underline}a:focus-visible{outline:3px solid #c4932d;outline-offset:3px}
.wrap{max-width:1220px;margin:0 auto;padding:0 20px}.skip-link{position:absolute;left:-9999px;top:0;background:#fff;padding:10px;z-index:100}.skip-link:focus{left:10px}
header.top{position:sticky;top:0;z-index:30;background:rgba(251,250,247,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar{display:flex;align-items:center;gap:18px;min-height:62px;flex-wrap:wrap}.brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.2px;color:var(--ink)}
.brand .dot{width:22px;height:22px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#f6d98a,#a9791c);box-shadow:inset 0 0 0 2px rgba(255,255,255,.5)}
nav.main{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}nav.main a{padding:7px 10px;border-radius:9px;color:var(--muted);font-weight:600;font-size:13px}nav.main a:hover{background:#f2efe7;text-decoration:none;color:var(--ink)}nav.main a.active{background:var(--ink);color:#fff}
main{padding:26px 0 60px}h1{font-size:31px;line-height:1.18;margin:6px 0 10px;letter-spacing:-.5px}h2{font-size:20px;margin:34px 0 12px;letter-spacing:-.2px}h3{font-size:15px;margin:0 0 6px}p.lead{color:var(--muted);max-width:78ch;margin:0 0 18px}.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:20px}.grid{display:grid;gap:16px}.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.stat{padding:16px 18px}.stat .n{font-size:26px;font-weight:750;letter-spacing:-.5px;line-height:1.1}.stat .l{font-size:12.5px;color:var(--muted);margin-top:4px}
.banner{background:linear-gradient(180deg,#fffdf7,#fdf6e6);border:1px solid #ecd9a8;border-radius:var(--radius);padding:22px 24px;box-shadow:var(--shadow)}.banner h2{margin:0 0 8px;font-size:19px}.banner p{margin:0 0 10px;color:#4a3a18;max-width:92ch}.banner p:last-child{margin-bottom:0}.banner .pill{display:inline-block;background:var(--bad);color:#fff;font-size:11px;font-weight:800;letter-spacing:.1em;padding:4px 9px;border-radius:999px;margin-bottom:10px}.flagline{margin-top:12px;padding-top:12px;border-top:1px dashed #e3cf9b;font-size:13.5px;color:#5c4a20}
.badge{display:inline-block;font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:999px;white-space:nowrap}.b-ok{background:var(--ok-soft);color:var(--ok)}.b-part{background:var(--warn-soft);color:var(--warn)}.b-bad{background:var(--bad-soft);color:var(--bad)}.b-info{background:var(--info-soft);color:var(--info)}.b-neutral{background:#f1efe9;color:#5b6472}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--card);box-shadow:var(--shadow)}table{border-collapse:collapse;width:100%;font-size:13.2px;min-width:960px}th,td{text-align:left;padding:11px 13px;border-bottom:1px solid #f0ece2;vertical-align:top}th{background:#faf8f2;font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);white-space:nowrap;border-bottom:1px solid var(--line)}tbody tr:hover{background:#fffdf8}tbody tr:last-child td{border-bottom:none}td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}td.blank,.blank{color:#6d685f}.itemname{font-weight:650;line-height:1.35}.sub{color:var(--muted);font-size:12.1px;margin-top:3px;overflow-wrap:anywhere}.src{font-size:12.2px}.chip{display:inline-block;background:#f4f1e9;border:1px solid var(--line);border-radius:7px;padding:1px 6px;font-size:11.5px;color:var(--muted);margin-right:4px}
.catgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}.catlink{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow);color:inherit}.catlink:hover{border-color:#d9c99b;text-decoration:none;transform:translateY(-1px)}.catlink .c{font-size:12px;color:var(--gold);font-weight:700;letter-spacing:.08em;text-transform:uppercase}.catlink .t{font-size:17px;font-weight:700;margin:6px 0 3px}.catlink .d{font-size:12.7px;color:var(--muted)}
ul.clean{margin:8px 0 0;padding-left:18px;color:#333a44}ul.clean li{margin:4px 0}.checklist{list-style:none;margin:0;padding:0}.checklist li{display:flex;gap:10px;padding:9px 0;border-bottom:1px dashed #efeade;font-size:13.8px}.checklist li:last-child{border-bottom:none}.checklist .k{flex:0 0 22px;font-weight:800;color:var(--gold)}.note{background:#faf8f2;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:8px;padding:12px 14px;font-size:13.4px;color:#4a5260}.flag{padding:18px;border-radius:var(--radius);border:1px solid var(--line);background:var(--card);box-shadow:var(--shadow)}.flag.high{border-left:4px solid var(--bad)}.flag.medium{border-left:4px solid #c98b12}.flag.low{border-left:4px solid #8a95a6}.flag h3{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}.flag p{margin:6px 0;color:#3d4552;font-size:13.6px}.flag .meta{font-size:12.2px;color:var(--muted);margin-top:8px}.flag details{margin-top:8px}.flag summary{cursor:pointer;color:var(--info);font-size:12.5px;font-weight:650}
label.f{display:block;font-size:12.3px;font-weight:700;color:var(--muted);margin:0 0 4px;letter-spacing:.03em}input,select{width:100%;padding:10px 11px;border:1px solid #ddd6c6;border-radius:9px;font-size:14px;background:#fff;color:var(--ink);font-variant-numeric:tabular-nums}input[type=checkbox]{width:auto;margin:8px 8px 16px 0}input:focus,select:focus{outline:2px solid #e6cf95;outline-offset:1px;border-color:#cbb271}.calcgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}.out{margin-top:16px;display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}.out .box{background:#fbf7ec;border:1px solid #ecdfbd;border-radius:10px;padding:13px 15px}.out .box .l{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:#7a6a44;font-weight:700}.out .box .v{font-size:21px;font-weight:750;letter-spacing:-.4px;margin-top:3px}.out .box .s{font-size:11.8px;color:#7a6a44;margin-top:2px}pre.qa{background:#1c1f24;color:#e8e6df;padding:16px;border-radius:12px;overflow:auto;font-size:12.3px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}footer{border-top:1px solid var(--line);padding:24px 0 40px;color:var(--muted);font-size:12.6px}footer .row{display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between}.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:13.4px}.kv dt{color:var(--muted)}.kv dd{margin:0;font-weight:600;overflow-wrap:anywhere}.goldref{display:flex;gap:28px;flex-wrap:wrap;align-items:baseline;margin-top:6px}.goldref .quote{font-size:27px;font-weight:750}.goldref .unit{font-size:14px;color:var(--muted)}.mt16{margin-top:16px}.mt18{margin-top:18px}.small{font-size:12.5px}.nowrap{white-space:nowrap}
@media(max-width:640px){h1{font-size:25px}.topbar{min-height:auto;padding:10px 0}nav.main{margin-left:0}.wrap{padding:0 14px}.banner,.card{padding:17px}.kv{grid-template-columns:1fr}}
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blank(reason: str = "not confirmed") -> str:
    return f'<span class="blank" title="{esc(reason)}">{DASH}</span>'


def fmt_price(item: dict) -> str:
    if item.get("price") is None:
        return blank("No explicitly assigned current price; see linked flag")
    currency = item.get("currency")
    symbol = {"USD": "$", "EUR": "€"}.get(currency)
    if symbol is None:
        return blank("Price currency not confirmed")
    return f"{symbol}{item['price']:,.2f}"


def fmt_num(value, suffix: str = "", digits: int | None = None) -> str:
    if value is None:
        return blank("Not published in the retrieved item-specific text")
    if digits is not None:
        text = f"{value:.{digits}f}"
    elif isinstance(value, int):
        text = f"{value:d}"
    else:
        text = f"{value:g}"
    return f"{text}{suffix}"


def basis_label(basis: str) -> str:
    return {"setting_price": "Setting / configurator", "complete_ring": "Complete ring"}.get(basis, basis)


def basis_badge(basis: str) -> str:
    cls = "b-neutral" if basis == "setting_price" else "b-info"
    return f'<span class="badge {cls}">{esc(basis_label(basis))}</span>'


def status_badge(status: str, karat: int = 14) -> str:
    if status == "verified_solid_gold_and_weight":
        return f'<span class="badge b-ok">Solid {karat}k + weight</span>'
    if status.startswith("verified_solid_gold"):
        return f'<span class="badge b-ok">Explicit Solid {karat}k</span>'
    labels = {
        "partial_official_fields": "official fields · gaps flagged",
        "partial_eur_price": "EUR official price · gaps flagged",
        "partial_price_unverified": "price blank · gaps flagged",
        "partial_price_unassigned": "price unassigned · review",
        "partial_identity_mismatch": "identity mismatch · review",
    }
    return f'<span class="badge b-part">{esc(labels.get(status, status.replace("_", " ")))}</span>'


def external_link(url: str, label: str) -> str:
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}&nbsp;↗</a>'


def all_items() -> list[dict]:
    items = []
    for _, lpath in CATEGORY_FILES:
        payload = load(lpath)
        for item in payload["items"]:
            item["_category_id"] = payload["category_id"]
            item["_category_label"] = payload["category_label"]
            items.append(item)
    return items


def category_payloads() -> list[dict]:
    return [load(lpath) for _, lpath in CATEGORY_FILES]


def retrieval_dates(items: list[dict]) -> list[str]:
    return sorted({item["retrieved_at"] for item in items})


def page(title: str, active: str, body: str, retrieved: str, include_calculator: bool = False) -> str:
    nav_items = [
        ("index.html", "Dashboard", "dashboard"),
        ("solid-gold.html", "Solid Gold", "solid-gold"),
        ("solitaire.html", "Solitaire", "solitaire"),
        ("halo-pave.html", "Halo & Pavé", "halo-pave"),
        ("three-stone-vintage.html", "Three-Stone", "three-stone-vintage"),
        ("18k.html", "18K", "18k"),
        ("budget.html", "10K", "budget"),
        ("retailers.html", "Retailers", "retailers"),
        ("analysis.html", "Analysis", "analysis"),
        ("verification.html", "Checks", "verification"),
        ("prices.html", "Calculator", "prices"),
        ("flags.html", "Flagged", "flags"),
        ("methods.html", "Method", "methods"),
    ]
    def nav_link(href, label, key):
        attrs = ' class="active" aria-current="page"' if key == active else ""
        return f'<a href="{href}"{attrs}>{esc(label)}</a>'

    links = "".join(nav_link(href, label, key) for href, label, key in nav_items)
    script = '<script src="assets/calculator.js" defer></script>' if include_calculator else ""
    result = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · GOLD2</title>
<meta name="description" content="Source-backed gold engagement-ring research with dated prices, official links, explicit gaps, and a nominal fine-gold calculator.">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<link rel="stylesheet" href="assets/style.css">
{script}
</head>
<body>
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="top"><div class="wrap topbar">
  <a class="brand" href="index.html"><span class="dot" aria-hidden="true"></span>GOLD2 <span class="chip">research</span></a>
  <nav class="main" aria-label="Main navigation">{links}</nav>
</div></header>
<main id="main-content"><div class="wrap">
<section class="note"><strong>No hallucinations. No invented prices.</strong> Root register covers {SHELL["items"]} source-checked entries across {SHELL["sellers"]} official sellers (including <a href="solid-gold.html"><strong>Explicit Solid Gold</strong></a>) and {SHELL["flags"]} published flags. Open the <a href="dashboard/index.html"><strong>14-Page Companion Dashboard &amp; Gemstone Mass Calculator →</strong></a>, <a href="explore/"><strong>all {SHELL["explore_products"]} researched entries across {SHELL["explore_sellers"]} sellers →</strong></a>, <a href="verification.html">dated re-verification log</a>, or <a href="flags.html">Flagged for Review</a>. Keep checking primary pages for hallucinations after every review.</section>
{body}
</div></main>
<footer><div class="wrap row">
  <div><strong>GOLD2</strong> · remote document research · retrieved {esc(retrieved)} (UTC)</div>
  <div>Blank means unverified, never zero or estimated. No physical assay was performed.</div>
</div></footer>
</body>
</html>
"""


    def externalize(match):
        tag = match.group(0)
        style = match.group(1)
        key = 'legacy-' + hashlib.sha256(style.encode()).hexdigest()[:12]
        INLINE_STYLES[key] = style
        tag = re.sub(r'\sstyle="[^"]*"', '', tag)
        if 'class="' in tag:
            tag = tag.replace('class="', 'class="' + key + ' ', 1)
        else:
            tag = tag[:-1] + ' class="' + key + '">'
        return tag
    return re.sub(r'<[^>]+\sstyle="([^"]*)"[^>]*>', externalize, result)


def listing_table(items: list[dict]) -> str:
    rows = []
    for item in items:
        iid = item["id"]
        flag_links = " ".join(
            f'<a href="flags.html#{flag.lower()}">{esc(flag)}</a>' for flag in item.get("flags", [])
        )
        metal_bits = [f'<strong>{esc(item["metal"])}</strong>']
        metal_sub = f'karat {item["karat"]}K · colour ' + (esc(item["color"]) if item.get("color") else DASH)
        metal_bits.append(f'<div class="sub">{metal_sub}</div>')
        if item.get("prong_metal"):
            metal_bits.append(f'<div class="sub">prongs: {esc(item["prong_metal"])}</div>')
        if item.get("surface_finish"):
            metal_bits.append(f'<div class="sub">surface finish: {esc(item["surface_finish"])}</div>')

        width = fmt_num(item.get("width_mm"), " mm")
        if item.get("band_width_text"):
            width += f'<div class="sub">published wording: {esc(item["band_width_text"])}</div>'
        dimensions = f'<div><span class="nowrap">width {width}</span></div><div class="sub">depth {fmt_num(item.get("depth_mm"), " mm")}</div>'

        weight = fmt_num(item.get("weight_g"), " g", 2)
        if item.get("weight_basis"):
            weight += f'<div class="sub">{esc(item["weight_basis"])}</div>'

        price = f'<strong>{fmt_price(item)}</strong>'
        displayed = item.get("observed_native_display") or []
        if displayed:
            verbatim = " · ".join(f"“{esc(text)}”" for text in displayed)
            price += f'<div class="sub">page display, verbatim: {verbatim}</div>'
        if item.get("original_price") is not None:
            symbol = {"USD": "$", "EUR": "€"}.get(item.get("currency"), "")
            price += f'<div class="sub">original {symbol}{item["original_price"]:,.2f}</div>'
        if item.get("unassigned_price_text"):
            price += f'<div class="sub">unassigned official text:<br>“{esc(item["unassigned_price_text"])}”</div>'
        elif item.get("price") is None:
            price += '<div class="sub">no price assigned; see flag</div>'

        stone_scope = (
            "all-metal solid gold ring (no stones)"
            if item.get("all_metal_design")
            else ("centre stone not included" if item.get("center_stone_included") is False else "complete ring as listed")
        )
        source = external_link(item["source_url"], "official listing")
        source += f'<div class="sub">retrieved {esc(item["retrieved_at"])}</div>'
        source += f'<div class="sub"><a href="{esc(item["evidence_file"])}">field evidence</a></div>'
        rows.append(
            f'<tr class="item-row" id="item-{iid.lower()}" data-item-id="{esc(iid)}" data-source-url="{esc(item["source_url"])}">'
            f'<td><div class="itemname">{esc(item["name"])}</div><div class="sub">{esc(item["brand"])} · {esc(iid)}<br>SKU/source ID {esc(item["sku"])}</div></td>'
            f'<td>{esc(item["retailer"])}</td>'
            f'<td>{"".join(metal_bits)}</td>'
            f'<td>{dimensions}</td>'
            f'<td class="num">{weight}</td>'
            f'<td class="num">{price}</td>'
            f'<td>{basis_badge(item["price_basis"])}<div class="sub">{esc(stone_scope)}</div></td>'
            f'<td class="src">{source}</td>'
            f'<td>{status_badge(item["verification_status"], item["karat"])}<div class="sub">{flag_links}</div></td>'
            '</tr>'
        )
    return (
        '<div class="tablewrap"><table><thead><tr>'
        '<th>Item</th><th>Retailer</th><th>Metal / karat</th><th>Width / depth</th><th>Metal weight</th>'
        '<th>Price</th><th>Price basis</th><th>Source / evidence</th><th>Review</th>'
        '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'
    )


def price_summary(items: list[dict]) -> str:
    groups: dict[tuple[str, str], list[dict]] = {}
    for item in items:
        if item.get("price") is not None and item.get("currency"):
            groups.setdefault((item["price_basis"], item["currency"]), []).append(item)
    parts = []
    for (basis, currency), group in sorted(groups.items()):
        values = [item["price"] for item in group]
        low, high = min(values), max(values)
        symbol = {"USD": "$", "EUR": "€"}.get(currency, currency + " ")
        span = f"{symbol}{low:,.2f}" if low == high else f"{symbol}{low:,.2f}–{high:,.2f}"
        parts.append(f"{len(group)} {basis_label(basis).lower()} · {currency} {span}")
    missing = sum(1 for item in items if item.get("price") is None)
    if missing:
        parts.append(f"{missing} price(s) blank/flagged")
    return " · ".join(parts) if parts else "No assigned current price"



def register_relationship(items):
    """Derive how the root register relates to the companion explorer register.

    Counts come from the data files, never from prose. If the companion files are
    missing, the note is omitted instead of being guessed.
    """
    try:
        catalog = load(DATA / "catalog.json")
        evidence = json.loads((ROOT / "research" / "evidence.json").read_text(encoding="utf-8"))
    except Exception:
        return ""
    # Only product-source URLs belong in this cross-register count; policy, cart and
    # independent-platform records would otherwise inflate it (e.g. the Automic cart endpoint).
    urls = {source["id"]: (source.get("url") or "").rstrip("/")
            for source in evidence.get("sources", []) if source.get("kind") == "product"}
    companion = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "source" and isinstance(value, str) and value in urls and urls[value]:
                    companion.add(urls[value])
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for product in catalog.get("products", []):
        walk(product)
    root = {item.get("source_url", "").rstrip("/") for item in items}
    only_root = sorted(item["id"] for item in items if item.get("source_url", "").rstrip("/") not in companion)
    if not companion or not root:
        return ""
    shared = len(root & companion)
    union = len(root | companion)
    names = ", ".join(only_root) if only_root else "none"
    return (
        f'<div class="note mt16"><strong>Two registers, not one.</strong> This page registers {len(items)} listings. '
        f'The companion <a href="explore/index.html">Evidence Explorer</a> is a separate register of '
        f'{len(catalog.get("products", []))} entries. {shared} official product URLs appear in both; '
        f'{len(only_root)} root rows are recorded only here ({names}). Across both registers {union} distinct official '
        f'product URLs were researched. Counts are not transferable between the two registers, and neither register is '
        f'a market-wide list.</div>'
    )

def build_index(items, payloads, flags, gold, qa_summary, retrieved):
    priced = sum(1 for item in items if item.get("price") is not None)
    weights = sum(1 for item in items if item.get("weight_g") is not None)
    high_flags = sum(1 for flag in flags if flag["severity"] == "high")
    solid_missing = sum(1 for item in items if item.get("solid_gold_explicit") is not True)
    hallmark_missing = sum(1 for item in items if item.get("hallmark_stated") is not True or item.get("makers_mark_stated") is not True)
    ambiguous = sum(1 for item in items if item.get("unassigned_price_text"))
    displayed_only = sum(
        1 for item in items
        if item.get("price") is None and (item.get("observed_native_display") or item.get("unassigned_price_text"))
    )
    rejected = sum(1 for flag in flags if flag["type"] == "price_discrepancy")
    cat_cards = "".join(
        f'<a class="catlink" href="{payload["category_id"]}.html"><div class="c">{len(payload["items"])} item(s)</div>'
        f'<div class="t">{esc(payload["category_label"])}</div><div class="d">{esc(price_summary(payload["items"]))}</div></a>'
        for payload in payloads
    )
    checklist = [
        ("Purity", "Karat is quoted only where the retailer states it. It is a seller claim, not an XRF result."),
        ("Solid gold", f"{solid_missing} of {len(items)} item-specific captures do not state the required phrase; all remain flagged (F-001)."),
        ("Hallmark", f"{hallmark_missing} of {len(items)} rows lack documented physical karat/maker’s marks; stock and source IDs are not hallmarks (F-002)."),
        ("Weight", f"A size-specific seller metal-weight claim is published for {weights} of {len(items)} rows; every other weight is blank (F-003)."),
        ("Seller", "Official contact, payment, and return policies are separated from scoped independent BBB profile data. Neither is an endorsement."),
        ("Price", f"{priced} rows have an explicitly assigned price. {displayed_only} more show the page's amount verbatim but leave the structured price blank because the ISO currency or the label is unresolved ({ambiguous} of those render an unlabeled amount). {len(items)-priced-displayed_only} row(s) publish no price in the retrieved text. {rejected} cached-price discrepancies are logged as rejected evidence."),
        ("Returns", "Resized/custom exclusions, VRAI fees, Brilliant Earth engraving terms, and Zales resizing-channel rules are shown per retailer."),
        ("Payment", "Accepted methods are linked to official payment/terms pages. Acceptance does not prove chargeback or purchase-protection outcomes."),
        ("Records", "Every row links its official product page and its own field-scoped evidence file with retrieval date."),
        ("On arrival", "No item was physically tested. Obtain written testing permission, then use independent non-destructive XRF and weighing before wearing or resizing."),
    ]
    check_html = "".join(
        f'<li><span class="k">{number:02d}</span><span><strong>{esc(label)}.</strong> {esc(text)}</span></li>'
        for number, (label, text) in enumerate(checklist, 1)
    )
    top_flags = sorted(flags, key=lambda flag: ({"high": 0, "medium": 1, "low": 2}[flag["severity"]], flag["id"]))[:4]
    flag_cards = "".join(
        f'<div class="flag {flag["severity"]}"><h3>{esc(flag["id"])} · {esc(flag["title"])}</h3>'
        f'<p>{esc(flag["detail"][:260])}{"…" if len(flag["detail"])>260 else ""}</p>'
        f'<div class="meta"><a href="flags.html#{flag["id"].lower()}">Read full flag →</a></div></div>'
        for flag in top_flags
    )
    body = f"""
<section class="banner" aria-labelledby="no-hallucination">
  <span class="pill">NO HALLUCINATIONS</span>
  <h2 id="no-hallucination">Rule: do not invent, estimate, or extrapolate values.</h2>
  <p>A published fact must be supported by a field-scoped excerpt from a page actually retrieved. If a value is absent or ambiguous, it remains <strong>blank</strong> and is linked to <a href="flags.html">Flagged for Review</a>. Search snippets are not product facts; unlabeled amounts are not assigned by position or arithmetic.</p>
  <p class="flagline"><strong>Look for hallucinations again after every review.</strong> Re-open the official source, re-read the row, and treat the official page as current if this table becomes stale. Automated checks: <strong>{esc(qa_summary)}</strong> — see <a href="methods.html">Method &amp; QA</a>.</p>
</section>

<h1>Gold engagement-ring research dashboard</h1>
<p class="lead">{len(items)} researched listings from {len({item['retailer_id'] for item in items})} official retailers, organized into {len(payloads)} categories (including {len(items)-solid_missing} explicit <em>Solid Gold</em> (14k–24k) rings). Official page claims are not physical verification: full physical hallmark + maker’s-mark stamps remain unverified across all {hallmark_missing} pages, while {weights} rows publish stone-free metal weights.</p>

<div class="grid g4 mt18">
  <div class="card stat"><div class="n">{len(items)}</div><div class="l">researched listings</div></div>
  <div class="card stat"><div class="n">{priced}</div><div class="l">explicitly assigned prices</div></div>
  <div class="card stat"><div class="n">{weights}<span class="small"> / {len(items)}</span></div><div class="l">published metal weights</div></div>
  <div class="card stat"><div class="n">{len(flags)}</div><div class="l">flags · {high_flags} high severity</div></div>
</div>

<div class="card mt16">
  <div class="eyebrow">Dated gold reference used by the calculator</div>
  <div class="goldref"><div class="quote">${gold['usd_per_troy_oz']:,.2f}<span class="unit"> / troy oz</span></div>
    <div class="sub">quote date {esc(gold['quote_date'] or 'unconfirmed — F-026')} · retrieved {esc(gold['retrieved_at'])}<br>{external_link(gold['source_url'], gold['source_name'])}</div>
    <a class="badge b-info" href="prices.html">Open nominal melt calculator →</a></div>
</div>

<h2>Browse by category</h2><div class="catgrid">{cat_cards}</div>
{register_relationship(items)}
<h2>What this project checks</h2><div class="card"><ul class="checklist">{check_html}</ul>
<div class="note mt16">A karat description or stamp alone does not prove purity. Seller documentation, correct markings, and independent physical testing answer different questions; none is silently substituted for another.</div></div>
<h2>Priority flags</h2><div class="grid g2">{flag_cards}</div>
<p class="mt16"><a href="flags.html"><strong>See all {len(flags)} flags →</strong></a></p>
"""
    return page("Dashboard", "dashboard", body, retrieved)


def build_category(payload, flags, retrieved):
    items = payload["items"]
    relevant = {flag for item in items for flag in item.get("flags", [])}
    flag_defs = sorted((flag for flag in flags if flag["id"] in relevant), key=lambda flag: ({"high": 0, "medium": 1, "low": 2}[flag["severity"]], flag["id"]))
    flag_list = "".join(
        f'<li><strong><a href="flags.html#{flag["id"].lower()}">{esc(flag["id"])}</a></strong> {esc(flag["title"])} <span class="badge b-neutral">{esc(flag["severity"])}</span></li>'
        for flag in flag_defs
    )
    body = f"""
<div class="eyebrow">{esc(payload['category_label'])}</div><h1>{esc(payload['category_label'])} gold engagement rings</h1>
<p class="lead">{len(items)} researched listing(s). {esc(price_summary(items))}. Blank cells are unconfirmed values, not zero or estimates.</p>
<div class="note" style="margin-bottom:16px"><strong>Read price basis before comparing.</strong> Setting/configurator prices exclude the centre stone; complete-ring rows list diamond rings. No cross-basis ranking or currency conversion is applied.</div>
{listing_table(items)}
<h2>Flags touching these items</h2><ul class="clean">{flag_list or '<li>None.</li>'}</ul>
<p class="mt16"><a href="index.html">← Back to dashboard</a></p>
"""
    return page(payload["category_label"], payload["category_id"], body, retrieved)


def yes_no_unknown(value, yes="excluded", no="not excluded") -> str:
    if value is True:
        return esc(yes)
    if value is False:
        return esc(no)
    return blank("Not confirmed in captured policy")


def build_retailers(retailers, items, retrieved):
    policy_rows = []
    reputation_rows = []
    detail_cards = []
    for retailer in retailers:
        count = sum(1 for item in items if item["retailer_id"] == retailer["id"])
        contact = " · ".join(filter(None, [retailer.get("contact_phone"), retailer.get("contact_email")]))
        contact_html = esc(contact) if contact else blank("No direct contact captured")
        contact_html += f'<div class="sub">{esc(", ".join(retailer.get("contact_channels", [])))}<br>{external_link(retailer["contact_source_url"], "contact source")}</div>'
        payments = ", ".join(retailer.get("payment_methods_verified") or [])
        payment_html = esc(payments) if payments else blank("Payment methods not captured")
        payment_html += f'<div class="sub">{external_link(retailer["payment_source_url"], "payment source")}</div>'
        exclusions = f'resized: {yes_no_unknown(retailer.get("return_excludes_resized"))}<br>custom: {yes_no_unknown(retailer.get("return_excludes_custom"))}'
        exclusions += f'<div class="sub">{external_link(retailer["return_policy_url"], "official policy")}</div>'
        test_permission = blank("Written independent-testing permission not captured")
        test_permission += '<div class="sub"><a href="flags.html#f-021">F-021</a></div>'
        policy_rows.append(
            f'<tr><td><strong>{esc(retailer["name"])}</strong><div class="sub">{count} researched row(s)<br>{external_link(retailer["website"], "retailer site")}</div></td>'
            f'<td>{retailer["return_window_days"]} days<div class="sub">{esc(retailer["return_window_basis"])}</div></td>'
            f'<td>{exclusions}</td><td>{payment_html}</td><td>{contact_html}</td><td>{test_permission}</td></tr>'
        )
        detail_cards.append(
            f'<div class="card"><h3>{esc(retailer["name"])}</h3><p class="small"><strong>Return exclusions:</strong> {esc(retailer["return_exclusions_detail"])}</p>'
            f'<p class="small"><strong>Resize terms:</strong> {esc(retailer["resize_policy"])}</p>'
            f'<p class="small"><strong>Return shipping:</strong> {esc(retailer["return_free_shipping_basis"])}</p>'
            f'<p class="small"><strong>Payment scope:</strong> {esc(retailer["payment_note"])}</p>'
            f'<a href="{esc(retailer["evidence_file"])}">Read field-scoped policy evidence</a></div>'
        )
        reputation = retailer["independent_reputation"]
        if reputation.get("bbb_rating") is not None:
            bbb_status = f'{esc(reputation["bbb_rating"])} · ' + ("accredited" if reputation.get("bbb_accredited") else "not accredited")
        else:
            bbb_status = blank("Metrics withheld; identity not confirmed")
        if reputation.get("review_average_out_of_5") is not None:
            reviews = f'{reputation["review_average_out_of_5"]:g}/5 · {reputation["review_count"]} reviews'
        else:
            reviews = blank("Not assigned")
        if reputation.get("complaints_last_3_years") is not None:
            complaints = f'3 years: {reputation["complaints_last_3_years"]:,}<br>12 months: {reputation["complaints_last_12_months"]:,}'
        else:
            complaints = blank("Not assigned")
        profile_url = reputation.get("profile_url") or reputation.get("candidate_profile_url")
        profile_label = "BBB profile" if reputation.get("profile_url") else "candidate BBB profile"
        rep_sources = external_link(profile_url, profile_label)
        if reputation.get("reviews_url"):
            rep_sources += f'<div class="sub">{external_link(reputation["reviews_url"], "reviews")} · {external_link(reputation["complaints_url"], "complaints")}</div>'
        rep_sources += f'<div class="sub">retrieved {esc(reputation["retrieved_at"])}</div>'
        reputation_rows.append(
            f'<tr><td><strong>{esc(retailer["name"])}</strong><div class="sub">{esc(reputation["profile_scope"])}</div></td>'
            f'<td>{bbb_status}</td><td>{reviews}</td><td>{complaints}</td><td>{rep_sources}</td></tr>'
        )
    body = f"""
<div class="eyebrow">Seller due diligence</div><h1>Retailers, policies &amp; reputation scope</h1>
<p class="lead">Official retailer pages support policy, payment, and contact fields. Independent BBB pages are shown separately with their identity and coverage limitations. Blank fields are not inferred.</p>
<h2>Official retailer policies</h2>
<div class="tablewrap"><table><thead><tr><th>Retailer</th><th>Return window</th><th>Return exclusions</th><th>Accepted methods</th><th>Contact</th><th>Independent testing</th></tr></thead><tbody>{''.join(policy_rows)}</tbody></table></div>
<h2>Policy details that change the return decision</h2><div class="grid g2">{''.join(detail_cards)}</div>
<div class="note mt16"><strong>Safe sequence:</strong> obtain written permission for independent non-destructive inspection; keep the item unworn and unaltered; inspect and weigh it; then follow the exact seller/channel policy. Do not resize until you have decided to keep the ring and understand the return/warranty consequences.</div>
<h2>Independent BBB profile data</h2>
<p class="lead">Dated profile metrics are not a seller scorecard or endorsement. Complaint narratives contain third-party allegations, not established facts. Scopes differ, so no cross-retailer ranking is made.</p>
<div class="tablewrap"><table><thead><tr><th>Retailer / profile scope</th><th>BBB label</th><th>Customer reviews</th><th>Complaints</th><th>Independent sources</th></tr></thead><tbody>{''.join(reputation_rows)}</tbody></table></div>
<div class="note mt16">VRAI’s candidate metrics are withheld because identity is not confirmed (F-022). Zales figures belong to a combined Signet profile covering other brands (F-023). BBB states that it does not endorse businesses and does not guarantee third-party information.</div>
<h2>Marketplace note</h2><div class="note"><strong>James Allen:</strong> the captured item-41515 URL redirected to a sold-out Blue Nile page. Included James Allen designs are sold through Blue Nile, so seller policies and contacts are Blue Nile’s. See <a href="flags.html#f-009">F-009</a>.</div>
"""
    return page("Retailers", "retailers", body, retrieved)


def build_flags(flags, items, retrieved):
    order = {"high": 0, "medium": 1, "low": 2}
    item_map = {item["id"]: item for item in items}
    cards = []
    for flag in sorted(flags, key=lambda entry: (order[entry["severity"]], entry["id"])):
        badge = {"high": "b-bad", "medium": "b-part", "low": "b-neutral"}[flag["severity"]]
        affected = " ".join(
            f'<a class="chip" href="{item_map[iid]["_category_id"]}.html#item-{iid.lower()}">{esc(iid)}</a>'
            for iid in flag["affected_items"]
        ) or DASH
        affected_retailers = ", ".join(flag.get("affected_retailers", [])) or "—"
        sources = "".join(f'<li>{external_link(url, url)}</li>' for url in flag["sources"])
        open_attr = " open" if len(flag["sources"]) <= 3 else ""
        cards.append(f"""
<article class="flag {flag['severity']}" id="{flag['id'].lower()}">
<h3>{esc(flag['id'])} · {esc(flag['title'])} <span class="badge {badge}">{esc(flag['severity'])}</span><span class="badge b-neutral">{esc(flag['type'].replace('_',' '))}</span></h3>
<p>{esc(flag['detail'])}</p><p><strong>Recommended action:</strong> {esc(flag['recommended_action'])}</p>
<p class="meta"><strong>Affected rows:</strong><br>{affected}</p><p class="meta"><strong>Affected retailer records:</strong> {esc(affected_retailers)}</p>
<details{open_attr}><summary>{len(flag['sources'])} source link(s)</summary><ul class="clean small">{sources}</ul></details>
</article>""")
    solid_n = sum(1 for item in items if item.get("solid_gold_explicit") is not True)
    hallmark_n = sum(1 for item in items if item.get("hallmark_stated") is not True or item.get("makers_mark_stated") is not True)
    weight_missing = sum(1 for item in items if item.get("weight_g") is None)
    body = f"""
<div class="eyebrow">Open limitations, discrepancies, and policy cautions</div><h1>Flagged for review</h1>
<p class="lead">Every unresolved value, ambiguity, source-scope limit, and material policy restriction is kept visible. Flagged rows remain published with sources; no gap is silently filled and no row is presented as physically verified.</p>
<div class="note" style="margin-bottom:18px"><strong>No-hallucination policy, applied.</strong> {solid_n} of {len(items)} rows lack item-specific “solid gold” wording; {hallmark_n} of {len(items)} lack complete physical hallmark + maker’s-mark documentation; {weight_missing} lack published metal weight. These are evidence gaps, not findings that a ring is fake. No physical inspection or XRF assay was performed (F-024).</div>
<div class="grid" style="grid-template-columns:1fr">{''.join(cards)}</div>
"""
    return page("Flagged for Review", "flags", body, retrieved)


def build_prices(gold, items, retrieved):
    known = [item for item in items if item.get("weight_g") is not None]
    grams_oz = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    ref_rows = []
    for karat in (10, 14, 18, 22, 24):
        fine2 = 2 * karat / 24
        fine4 = 4 * karat / 24
        fine6 = 6 * karat / 24
        melt6 = fine6 / grams_oz * spot
        ref_rows.append(
            f'<tr><td class="num">{karat}K</td><td class="num">{karat/24*100:.2f}%</td><td class="num">{fine2:.3f} g</td>'
            f'<td class="num">{fine4:.3f} g</td><td class="num">{fine6:.3f} g</td><td class="num">${melt6:,.2f}</td><td>{external_link(gold["conversion_source_url"], "NIST units")} · {external_link(gold["karat_source_url"], "Karat context")} · {external_link(gold["source_url"], "Recorded input")}</td></tr>'
        )
    known_rows = "".join(
        f'<tr><td>{external_link(item["source_url"], item["name"])}</td><td class="num">{item["karat"]}K</td>'
        f'<td class="num">{item["weight_g"]:.2f} g</td><td class="num">{item["weight_g"]*item["karat"]/24:.3f} g</td>'
        f'<td class="num">${item["weight_g"]*item["karat"]/24/grams_oz*spot:,.2f}</td><td>{fmt_price(item)}</td></tr>'
        for item in known
    )
    body = f"""
<div class="eyebrow">Nominal gold arithmetic, not appraisal</div><h1>Gold weight &amp; theoretical melt calculator</h1>
<p class="lead">Enter a documented <strong>metal-only</strong> weight, excluding stones and non-gold components. The calculator applies nominal karat/24 and an earlier recorded WGC input whose exact quote-as-of time is unconfirmed (F-026). These are conditional assumptions, not verified product values. It does not measure purity or estimate resale, refiner payout, or fair retail price.</p>
<div class="card">
  <p><a href="explore/calculator/">Expanded evidence-gated calculator →</a></p>
  <label><input id="root-scenario-ack" type="checkbox"> I acknowledge this is a conditional USD scenario, not verified ring weight, purity or value.</label>
  <div class="calcgrid">
    <div><label class="f" for="w">Metal-only weight (g / unit)</label><input id="w" type="number" min="0" step="0.01" inputmode="decimal" placeholder="Documented mass"></div>
    <div><label class="f" for="unit">Unit (NIST)</label><select id="unit"><option value="g" selected>Grams (g)</option><option value="dwt">Pennyweights (dwt)</option><option value="ozt">Troy ounces (ozt)</option></select></div>
    <div><label class="f" for="k">Listed karat</label><select id="k"><option value="10">10K</option><option value="14" selected>14K</option><option value="18">18K</option><option value="22">22K</option><option value="24">24K</option></select></div>
    <div><label class="f" for="spot">Gold spot (USD / troy oz)</label><input id="spot" type="number" min="0" step="0.01" inputmode="decimal" value="{spot:.2f}"></div>
    <div><label class="f" for="ask">Asking price (optional, USD)</label><input id="ask" type="number" min="0" step="0.01" inputmode="decimal" placeholder="USD only"></div>
  </div>
  <div class="out" aria-live="polite">
    <div class="box"><div class="l">Nominal fine gold</div><div class="v" id="fine">—</div><div class="s">metal weight × karat/24</div></div>
    <div class="box"><div class="l">Theoretical melt value</div><div class="v" id="melt">—</div><div class="s">fine grams ÷ {grams_oz} × spot</div></div>
    <div class="box"><div class="l">Asking ÷ melt</div><div class="v" id="ratio">—</div><div class="s">arithmetic only, not a fair-price score</div></div>
    <div class="box"><div class="l">Asking − melt</div><div class="v" id="over">—</div><div class="s">not a workmanship or stone valuation</div></div>
  </div>
  <p class="sub mt16">Earlier recorded input, not live: <strong>${spot:,.2f}/oz, {esc(gold['quote_date'] or 'unconfirmed — F-026')}</strong> — {external_link(gold['source_url'], gold['source_name'])}. Changing the spot field uses your input, not a newly verified quote. Do not enter a EUR asking price in the USD field.</p>
</div>
<div class="note mt16"><strong>Constants and boundaries:</strong> 1 troy ounce = {grams_oz} g from the {external_link(gold['conversion_source_url'], 'NIST conversion chart')}. Karat labeling context comes from {external_link(gold['karat_source_url'], '16 CFR 23.3 (eCFR)')}. Nominal karat arithmetic is not an assay.</div>
<h2>Hypothetical quick reference — not listing data</h2>
<div class="tablewrap"><table><thead><tr><th>Karat</th><th>Nominal purity</th><th>2 g metal</th><th>4 g metal</th><th>6 g metal</th><th>Conditional theoretical value of 6 g</th><th>Official input / method</th></tr></thead><tbody>{''.join(ref_rows)}</tbody></table></div>
<p class="sub">These are hypothetical calculations at the quote above. They are not retailer claims, product weights, or appraisals.</p>
<h2>Rows with a published metal-only weight</h2>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Karat</th><th>Published metal weight</th><th>Conditional nominal fine gold</th><th>Conditional theoretical value</th><th>Assigned price</th></tr></thead><tbody>{known_rows or '<tr><td colspan="6" class="blank">No row has a published metal weight.</td></tr>'}</tbody></table></div>
<p class="sub">{len(known)} of {len(items)} rows publish a stone-free metal weight (Automic Gold Coffin Ring 6.10 g 14K; VRAI Classic 4-Prong Dome 2.86 g at size 6 18K). This is a conditional calculation using seller-published weights and nominal listed karat, not independently tested weight/purity. Verified product fine-gold values remain blank; blank is not zero.</p>
<h2>How to use this honestly</h2><ul class="clean">
<li>Do not use gross ring weight if it includes diamonds, gemstones, platinum prongs, or other non-gold components.</li>
<li>Keep setting/configurator and complete-ring prices separate. A price-to-melt ratio does not appraise craftsmanship, stones, brand, duties, fees, or resale spread.</li>
<li>A result below or above the asking price is only an arithmetic observation for review, not proof of fraud or value.</li>
<li>Verify weight and purity with an independent jeweller under the seller’s written return terms before wearing or resizing.</li></ul>
"""
    return page("Calculator", "prices", body, retrieved, include_calculator=True)


def build_methods(qa_summary, gold, items, flags, retailers, retrieved):
    quote_count = sum(len(quotes) for item in items for quotes in item.get("field_evidence", {}).values())
    quote_count += sum(len(quotes) for retailer in retailers for quotes in retailer.get("field_evidence", {}).values())
    quote_count += sum(len(quotes) for quotes in gold.get("field_evidence", {}).values())
    limitation_ids = [fid for fid in ("F-007", "F-008", "F-013", "F-018", "F-021", "F-022", "F-023", "F-024", "F-025", "F-026", "F-032", "F-033") if any(flag["id"] == fid for flag in flags)]
    limitations = "".join(
        f'<li><a href="flags.html#{fid.lower()}">{fid}</a> — {esc(next(flag["title"] for flag in flags if flag["id"] == fid))}</li>'
        for fid in limitation_ids
    )
    body = f"""
<div class="eyebrow">Method, sources, audit</div><h1>Method &amp; QA</h1>
<p class="lead">This page is designed to make the dataset challengeable. It distinguishes retrieved facts, rejected values, calculated values, independent profile data, and physical verification that has not occurred.</p>
<h2>1. The no-hallucination rule</h2><div class="banner" style="padding:18px 20px"><p><strong>Publish only what a retrieved source supports.</strong> Each row stores an official URL, UTC retrieval date, per-item evidence file, and field-specific quote lists. A missing or ambiguous value is <code>null</code> and flagged. Null never means zero, false, or a negative physical finding. No price is inferred from position, discount arithmetic, currency conversion, or a search snippet.</p></div>
<h2>2. Source hierarchy and scope</h2><ul class="clean">
<li><strong>Product facts and seller policies:</strong> the retailer’s own product, policy, payment, and contact pages.</li>
<li><strong>Independent reputation context:</strong> BBB profile/review/complaint pages with dated counts, identity scope, and BBB disclaimers. Allegations are not treated as proven; combined-parent and candidate profiles are not silently relabeled.</li>
<li><strong>Gold reference:</strong> World Gold Council spot page with quote date and ICE Data Services attribution.</li>
<li><strong>Calculation constants/context:</strong> NIST troy-ounce conversion chart and eCFR gold-labeling guidance.</li>
<li><strong>Rejected as product evidence:</strong> search snippets, aggregators, blogs, coupon pages, unrelated page text, and values from other items in the same category.</li></ul>
<h2>3. Field-scoped evidence</h2><p>The current audit resolves <strong>{quote_count}</strong> field-specific quotes across {len(items)} item files, {len(retailers)} retailer files, and the gold/calculation evidence. A price, width, or karat in one item’s file cannot support another item. Shared category files are retained only as inherited audit history and are not authoritative inputs.</p>
<h2>4. Current limitations</h2><ul class="clean">{limitations}</ul>
<h2>5. Dated live re-verification</h2><p>The <a href="verification.html">verification log</a> records each official page that was actually re-read, the verbatim values it rendered, the date, and what changed in the register. A value is reused only when the page renders it again; anything that could not be re-read keeps its older date and is labelled. Pages that returned 404 or did not state the fact being sought are recorded as dead ends instead of being treated as evidence.</p>
<h2>6. Automated checks after every review</h2><p>Run <code>python3 tools/build_site.py</code>, <code>python3 tools/qa.py</code>, <code>node tools/test_calculator.js</code>, and <code>python3 reviews/independent_snapshot_audit.py .</code>. The audits check schema, field-level quote backing, numeric/currency consistency, null-to-flag coverage, two-way flag references, official product domains, calculator arithmetic, built-row/source identity, internal links and fragments, CSP/script constraints, small-text contrast, stale generated values, and independent cross-schema contradictions.</p>
<pre class="qa">RESULT: {esc(qa_summary)}
Full timestamped log: reports/qa-report.md</pre>
<p>Current local result: <strong>{len(items)} items</strong>, <strong>{len(flags)} flags</strong>, <strong>{quote_count}</strong> field-scoped quotes. The root suite now runs 12 checks; run <code>python3 audit/8c810c15/security_and_hallucination_scanner.py</code> for the independent 202-control HTML/security scan after every edit.</p>
<p><a href="reports/qa-report.md">Open the complete timestamped QA report</a> · <a href="reports/source-link-review.md">Open the dated external source-link retrieval review</a></p>
<div class="note"><strong>Recommendation:</strong> look for hallucinations again after every review and after any generator change. Automated checks reduce risk; they cannot prove a retailer’s claim or replace physical testing.</div>
<h2>7. Earlier pass preserved</h2><p>The <code>site/</code> folder holds the earlier two-listing dashboard with its own audit and calculator tests: <a href="site/index.html">open the earlier dashboard</a>. Its two Blue Nile settings were re-fetched in this integration and appear as <code>BN-195402</code> and <code>BN-302868</code> on the <a href="halo-pave.html">Halo &amp; Pavé</a> page.</p>
<h2>8. Data provenance summary</h2><dl class="kv">
<dt>Items</dt><dd>{len(items)}</dd><dt>Flags</dt><dd>{len(flags)}</dd><dt>Field-scoped quotes</dt><dd>{quote_count}</dd>
<dt>Gold quote</dt><dd>${gold['usd_per_troy_oz']:,.2f}/oz · {esc(gold['quote_date'] or 'unconfirmed — F-026')} · {external_link(gold['source_url'], 'World Gold Council')}</dd>
<dt>Retrieval dates</dt><dd>{esc(retrieved)} (UTC)</dd><dt>Repository</dt><dd>{external_link('https://github.com/karagemop466-tech/GOLD2', 'karagemop466-tech/GOLD2')}</dd></dl>
<h2>9. What to do with a flagged row</h2><ol class="clean">
<li>Open the official source and item evidence; re-read the exact field and price basis.</li>
<li>Ask the seller in writing about solid-gold construction, metal-only gram weight, physical hallmark/maker’s mark, and independent non-destructive testing permission.</li>
<li>Keep the written response and the dated checkout record. Do not rely on a cached snippet or an unlabeled amount.</li>
<li>Before wearing or resizing, use an independent jeweller for XRF, markings, and weight, subject to the seller’s return terms.</li>
<li>If the seller refuses independent verification or a return, do not buy.</li></ol>
"""
    return page("Method & QA", "methods", body, retrieved)



STATUS_LABELS = {
    "verified_match": ("b-ok", "re-read · matched"),
    "verified_correction": ("b-part", "re-read · register corrected"),
    "verified_no_price": ("b-part", "re-read · no price published"),
    "not_re_read": ("b-neutral", "not re-read this pass"),
    "dead_end": ("b-bad", "source unavailable / no statement"),
}


def build_analysis(gold, items, flags, retailers, retrieved):
    grams_oz = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    weighted = [item for item in items if item.get("weight_g") is not None]
    gross_only = [item for item in items if item.get("weight_g") is None and item.get("gross_ring_weight_g")]
    melt_rows = []
    comparisons = []
    for item in weighted:
        fine = item["weight_g"] * item["karat"] / 24
        melt = fine / grams_oz * spot
        ratio = None
        if item.get("price") is not None and item.get("currency") == "USD":
            ratio = item["price"] / melt
            comparisons.append((item, melt, ratio))
        melt_rows.append(
            f'<tr><td><div class="itemname">{esc(item["name"])}</div>'
            f'<div class="sub">{esc(item["brand"])} · {esc(item["id"])}<br>karat {item["karat"]}K</div></td>'
            f'<td class="num">{item["weight_g"]:.2f} g<div class="sub">{esc(item.get("weight_basis") or "")}</div></td>'
            f'<td class="num">{fine:.3f} g</td>'
            f'<td class="num"><strong>${melt:,.2f}</strong></td>'
            f'<td class="num">{fmt_price(item)}</td>'
            f'<td class="num">{(f"{ratio:.2f}× nominal melt" if ratio else blank("No assigned USD price"))}</td>'
            f'<td class="src">{external_link(item["source_url"], "official listing")}</td></tr>'
        )
    excluded = "".join(
        f'<li><strong>{esc(item["name"])}</strong> ({esc(item["id"])}) publishes '
        f'<strong>{item["gross_ring_weight_g"]:.2f} g</strong> as a gross item weight that includes the '
        f'stone. It is shown on the category page and deliberately excluded from fine-gold arithmetic '
        f'(<a href="flags.html#f-028">F-028</a>).</li>'
        for item in gross_only
    ) or "<li>None.</li>"
    solid = sum(1 for item in items if item.get("solid_gold_explicit") is True)
    hallmarks = sum(1 for item in items if item.get("hallmark_stated") is True)
    makers = sum(1 for item in items if item.get("makers_mark_stated") is True)
    priced = sum(1 for item in items if item.get("price") is not None)
    approved_tests = sum(1 for item in items if item.get("independent_test_permission") is True)
    retailer_sites = {retailer["id"]: retailer.get("website") for retailer in retailers}
    category_rows = []
    for payload in category_payloads():
        rows = payload["items"]
        seller_links = " · ".join(
            external_link(retailer_sites[retailer_id], retailer_id.replace("-", " ").title())
            for retailer_id in sorted({row["retailer_id"] for row in rows})
            if retailer_sites.get(retailer_id)
        )
        category_rows.append(
            f'<tr><td><a href="{payload["category_id"]}.html"><strong>{esc(payload["category_label"])}</strong></a></td>'
            f'<td class="num">{len(rows)}</td>'
            f'<td class="num">{sum(1 for r in rows if r.get("price") is not None)}</td>'
            f'<td class="num">{sum(1 for r in rows if r.get("weight_g") is not None)}</td>'
            f'<td class="num">{sum(1 for r in rows if r.get("solid_gold_explicit") is True)}</td>'
            f'<td class="src">{seller_links}</td>'
            f'<td>{esc(price_summary(rows))}</td></tr>'
        )
    ratio_note = ""
    if comparisons:
        item, melt, ratio = max(comparisons, key=lambda entry: entry[2])
        ratio_note = (
            f'<p>The only row with both a published stone-free metal weight and an assigned USD asking '
            f'price is <strong>{esc(item["name"])}</strong>: ${item["price"]:,.2f} against '
            f'${melt:,.2f} of nominal fine-gold content, i.e. {ratio:.2f}× the nominal metal value. '
            f'That multiple is arithmetic, not a valuation of the ring: design work, finishing, '
            f'manufacturing, taxes, fees and any resale spread are excluded.</p>'
        )
    body = f"""
<div class="eyebrow">Analysis</div>
<h1>Nominal gold content, price coverage, and what the register can actually compare</h1>
<p class="lead">Every figure below is arithmetic on a <em>published</em> weight and the <em>dated</em> gold
reference. A weight that is not published is never estimated, and a price whose currency is not stated is
never assigned. Blank means unverified.</p>

<div class="grid g4 mt18">
  <div class="card stat"><div class="n">{len(weighted)}<span class="small"> / {len(items)}</span></div><div class="l">rows with a published metal weight</div></div>
  <div class="card stat"><div class="n">{priced}</div><div class="l">rows with an assigned price</div></div>
  <div class="card stat"><div class="n">{solid}</div><div class="l">rows stating solid gold explicitly</div></div>
  <div class="card stat"><div class="n">{hallmarks + makers}<span class="small"> / {len(items)}</span></div><div class="l">rows documenting physical marks</div></div>
</div>

<h2>1. Nominal fine-gold content at the dated reference</h2>
<div class="note"><strong>Method.</strong> Nominal fine gold = published metal weight × karat ÷ 24.
Theoretical melt = nominal fine gold ÷ {grams_oz} g per troy ounce × ${spot:,.2f}/oz
({esc(gold["quote_date"] or "header quote date unconfirmed — F-026")}). Karat is the seller's stated
alloy, not an assay. Weight must exclude stones and non-gold components for this arithmetic to mean
anything about gold content.</div>
<div class="tablewrap mt16"><table><thead><tr>
<th>Item</th><th>Published metal weight</th><th>Nominal fine gold</th><th>Theoretical melt</th>
<th>Asking price</th><th>Asking ÷ nominal melt</th><th>Source</th>
</tr></thead><tbody>{"".join(melt_rows) or '<tr><td colspan="7">No row publishes a usable metal weight.</td></tr>'}</tbody></table></div>
{ratio_note}

<h2>2. Weights that exist but cannot be used</h2>
<ul class="clean">{excluded}</ul>

<h2>3. Coverage by category</h2>
<div class="tablewrap mt16"><table><thead><tr>
<th>Category</th><th>Rows</th><th>Assigned prices</th><th>Published metal weights</th><th>Explicit solid gold</th><th>Official retailer sites</th><th>Price summary</th>
</tr></thead><tbody>{"".join(category_rows)}</tbody></table></div>

<h2>4. Checklist coverage across the register</h2>
<div class="card"><ul class="checklist">
<li><span class="k">01</span><span><strong>Karat stated.</strong> {sum(1 for item in items if item.get("karat") is not None)} of {len(items)} rows publish a karat. None of those values is a measured purity.</span></li>
<li><span class="k">02</span><span><strong>Explicit solid gold.</strong> {solid} of {len(items)} rows use the words solid gold on their own product page. The other rows are still listed, because a karat alone is not evidence of solid construction (<a href="flags.html#f-001">F-001</a>).</span></li>
<li><span class="k">03</span><span><strong>Hallmark and maker’s mark.</strong> {hallmarks} of {len(items)} rows document a physical karat stamp inside the band, and {makers} document a maker’s/manufacturer’s mark (<a href="flags.html#f-002">F-002</a>).</span></li>
<li><span class="k">04</span><span><strong>Metal weight.</strong> {len(weighted)} of {len(items)} rows publish a stone-free metal weight; {len(gross_only)} more publish only a gross item weight that includes stones (<a href="flags.html#f-003">F-003</a>, <a href="flags.html#f-028">F-028</a>).</span></li>
<li><span class="k">05</span><span><strong>Price currency.</strong> {priced} of {len(items)} rows carry an assigned amount whose currency is supported by the retailer’s own statement. The rest show the page text verbatim and stay unassigned (<a href="flags.html#f-025">F-025</a>).</span></li>
<li><span class="k">06</span><span><strong>Independent testing permission.</strong> {approved_tests} of {len(items)} rows have written permission captured for third-party testing or return after testing (<a href="flags.html#f-021">F-021</a>).</span></li>
<li><span class="k">07</span><span><strong>Physical verification.</strong> 0 of {len(items)} rings were weighed, XRF-tested, or inspected in person (<a href="flags.html#f-024">F-024</a>).</span></li>
</ul></div>

<h2>5. What this analysis must not be used for</h2>
<div class="note">The melt figures are conditional arithmetic, not appraisals, offers, or resale floors.
A ring can legitimately cost several times its metal value because of design, labour, setting, brand and
margin — and a suspiciously <em>low</em> price is the direction that deserves the extra questions
(checklist item: unusually cheap pricing is a red flag). Nothing here establishes that a ring is solid
gold, that its stated karat is accurate, or that a seller will honour a return.</div>
<p class="mt16"><a href="prices.html"><strong>Open the calculator to test your own weight and karat →</strong></a> · <a href="verification.html">Dated re-verification log</a></p>
"""
    return page("Analysis", "analysis", body, retrieved)


def build_verification(log, items, retrieved):
    entries = log["entries"]
    counts = {}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    rows = []
    for entry in entries:
        css, label = STATUS_LABELS.get(entry["status"], ("b-neutral", entry["status"]))
        observed = "<br>".join(f"“{esc(text)}”" for text in entry.get("observed") or []) or DASH
        rows.append(
            f'<tr id="check-{esc(entry["id"].lower())}">'
            f'<td><div class="itemname">{esc(entry["label"])}</div>'
            f'<div class="sub">{esc(entry["retailer"])} · {esc(entry["id"])}</div></td>'
            f'<td>{esc(entry["checked_at"])}</td>'
            f'<td><span class="badge {css}">{esc(label)}</span></td>'
            f'<td class="src">{observed}</td>'
            f'<td class="src">{external_link(entry["url"], "official page")}</td>'
            f'<td class="src">{esc(entry["note"])}</td></tr>'
        )
    pass_meta = log["pass"]
    body = f"""
<div class="eyebrow">Verification</div>
<h1>Dated re-verification log — {esc(pass_meta["checked_at"])} (UTC)</h1>
<p class="lead">{esc(pass_meta["rule"])}</p>

<section class="banner" aria-labelledby="pass-rule">
  <span class="pill">NO HALLUCINATIONS</span>
  <h2 id="pass-rule">A value is only reused if the official page renders it again.</h2>
  <p>{esc(pass_meta["method"])}</p>
  <p class="flagline"><strong>Look for hallucinations again after every review.</strong> This page is a
  dated record, not a live feed. Re-open each official link before acting on a row; a page that changed
  after this pass makes the row stale, not true.</p>
</section>

<div class="grid g5 mt18">
  <div class="card stat"><div class="n">{counts.get("verified_match", 0)}</div><div class="l">re-read · unchanged</div></div>
  <div class="card stat"><div class="n">{counts.get("verified_correction", 0)}</div><div class="l">re-read · register corrected</div></div>
  <div class="card stat"><div class="n">{counts.get("verified_no_price", 0)}</div><div class="l">re-read · no price published</div></div>
  <div class="card stat"><div class="n">{counts.get("not_re_read", 0)}</div><div class="l">not re-read this pass</div></div>
  <div class="card stat"><div class="n">{counts.get("dead_end", 0)}</div><div class="l">dead ends recorded</div></div>
</div>

<h2>Entry-by-entry record</h2>
<div class="tablewrap"><table><thead><tr>
<th>Record</th><th>Checked</th><th>Result</th><th>Observed on the official page (verbatim)</th><th>Official source</th><th>Effect on the register</th>
</tr></thead><tbody>{"".join(rows)}</tbody></table></div>

<h2>How to read the results</h2>
<div class="card"><ul class="clean">
<li><strong>re-read · unchanged</strong> — the page rendered the same values that were already stored. Nothing was added.</li>
<li><strong>re-read · register corrected</strong> — the page differed from the stored record, so the record was changed and the reason is written into the evidence file. Superseded values stay in the data as history and are never re-rendered as current.</li>
<li><strong>not re-read this pass</strong> — the stored observation keeps its own older date and is labelled as such; it is not silently refreshed.</li>
<li><strong>dead ends</strong> — a 404 or a page that does not state the fact being sought. Recorded so the same dead end is not mistaken for evidence later.</li>
</ul>
<div class="note mt16">{esc(pass_meta["limits"])}</div></div>
<p class="mt16"><a href="index.html">← Back to dashboard</a> · <a href="flags.html">Flagged for Review</a> · <a href="methods.html">Method &amp; automated checks</a></p>
"""
    return page("Verification log", "verification", body, retrieved)


def main():
    (SITE / "assets").mkdir(exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    gold = load(DATA / "gold-price.json")
    retailers = load(DATA / "retailers.json")["retailers"]
    flags = load(DATA / "flags.json")["flags"]
    payloads = category_payloads()
    items = all_items()
    dates = retrieval_dates(items)
    retrieved = ", ".join(dates)

    qa_path = ROOT / "reports" / "qa-report.md"
    qa_text = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_summary = "not run yet"
    for line in qa_text.splitlines():
        if "RESULT:" in line:
            qa_summary = line.split("RESULT:", 1)[1].replace("*", "").strip(" -—")
            break

    SHELL["items"] = len(items)
    SHELL["sellers"] = len({item["retailer_id"] for item in items})
    SHELL["flags"] = len(flags)
    catalog = load(DATA / "catalog.json")
    SHELL["explore_products"] = len(catalog["products"])
    SHELL["explore_sellers"] = len(catalog["sellers"])
    verification = load(DATA / "verification-log.json")
    pages = {"index.html": build_index(items, payloads, flags, gold, qa_summary, retrieved)}
    for payload in payloads:
        pages[f'{payload["category_id"]}.html'] = build_category(payload, flags, retrieved)
    pages["retailers.html"] = build_retailers(retailers, items, retrieved)
    pages["analysis.html"] = build_analysis(gold, items, flags, retailers, retrieved)
    pages["verification.html"] = build_verification(verification, items, retrieved)
    pages["flags.html"] = build_flags(flags, items, retrieved)
    pages["prices.html"] = build_prices(gold, items, retrieved)
    pages["methods.html"] = build_methods(qa_summary, gold, items, flags, retailers, retrieved)
    for name, content in pages.items():
        (SITE / name).write_text(content, encoding="utf-8")
    (SITE / "assets" / "style.css").write_text(CSS + "\n" + "\n".join("." + k + "{" + v + "}" for k,v in sorted(INLINE_STYLES.items())), encoding="utf-8")
    print(f"built {len(pages)} pages into {SITE}")


if __name__ == "__main__":
    main()
