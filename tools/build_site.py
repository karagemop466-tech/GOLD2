#!/usr/bin/env python3
"""Build the static dashboard in docs/ from the verified JSON in data/.

Design rule: this script never invents a value. It renders exactly what is in
data/*.json and prints an em dash for anything that is null.
"""
from __future__ import annotations

import html
import json
import shutil
import re
import hashlib
INLINE_STYLES = {}
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT  # GitHub Pages serves main "/" (legacy build), so pages live at the root
CATEGORY_FILES = [
    ("solitaire", "solitaire.json"),
    ("halo-pave", "halo-pave.json"),
    ("three-stone-vintage", "three-stone-vintage.json"),
    ("18k", "18k.json"),
    ("budget", "budget.json"),
]
DASH = "&mdash;"

CSS = """
:root{
  --bg:#fbfaf7; --card:#ffffff; --ink:#14161a; --muted:#5b6472; --line:#e8e3d8;
  --gold:#a9791c; --gold-soft:#f4ead2; --ok:#1c7a4a; --ok-soft:#e6f4ec;
  --warn:#8a5a00; --warn-soft:#fdf1dc; --bad:#a3261d; --bad-soft:#fbeae8; --info:#1d4d8f; --info-soft:#e8f0fb;
  --radius:14px; --shadow:0 1px 2px rgba(20,22,26,.05),0 8px 24px rgba(20,22,26,.05);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
a{color:var(--info);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:30;background:rgba(251,250,247,.92);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar{display:flex;align-items:center;gap:18px;min-height:62px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.2px}
.brand .dot{width:22px;height:22px;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,#f6d98a,#a9791c);box-shadow:inset 0 0 0 2px rgba(255,255,255,.5)}
nav.main{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
nav.main a{padding:7px 11px;border-radius:9px;color:var(--muted);font-weight:600;font-size:13.5px}
nav.main a:hover{background:#f2efe7;text-decoration:none;color:var(--ink)}
nav.main a.active{background:var(--ink);color:#fff}
main{padding:26px 0 60px}
h1{font-size:31px;line-height:1.18;margin:6px 0 10px;letter-spacing:-.5px}
h2{font-size:20px;margin:34px 0 12px;letter-spacing:-.2px}
h3{font-size:15px;margin:0 0 6px}
p.lead{color:var(--muted);max-width:74ch;margin:0 0 18px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:20px}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.g4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.stat{padding:16px 18px}
.stat .n{font-size:26px;font-weight:750;letter-spacing:-.5px;line-height:1.1}
.stat .l{font-size:12.5px;color:var(--muted);margin-top:4px}
.banner{background:linear-gradient(180deg,#fffdf7,#fdf6e6);border:1px solid #ecd9a8;
  border-radius:var(--radius);padding:22px 24px;box-shadow:var(--shadow)}
.banner h2{margin:0 0 8px;font-size:19px}
.banner p{margin:0;color:#4a3a18;max-width:86ch}
.banner .pill{display:inline-block;background:var(--bad);color:#fff;font-size:11px;font-weight:800;
  letter-spacing:.1em;padding:4px 9px;border-radius:999px;margin-bottom:10px}
.flagline{margin-top:12px;padding-top:12px;border-top:1px dashed #e3cf9b;font-size:13.5px;color:#5c4a20}
.badge{display:inline-block;font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:999px;white-space:nowrap}
.b-ok{background:var(--ok-soft);color:var(--ok)}
.b-part{background:var(--warn-soft);color:var(--warn)}
.b-bad{background:var(--bad-soft);color:var(--bad)}
.b-info{background:var(--info-soft);color:var(--info)}
.b-neutral{background:#f1efe9;color:#5b6472}
.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--card);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;font-size:13.4px;min-width:900px}
th,td{text-align:left;padding:11px 13px;border-bottom:1px solid #f0ece2;vertical-align:top}
th{background:#faf8f2;font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  position:sticky;top:0;z-index:2;white-space:nowrap;border-bottom:1px solid var(--line)}
tbody tr:hover{background:#fffdf8}
tbody tr:last-child td{border-bottom:none}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{color:#a7a29a}
.itemname{font-weight:650;line-height:1.35}
.sub{color:var(--muted);font-size:12.3px;margin-top:2px}
.src{font-size:12.3px;white-space:nowrap}
.chip{display:inline-block;background:#f4f1e9;border:1px solid var(--line);border-radius:7px;
  padding:1px 6px;font-size:11.5px;color:var(--muted);margin-right:4px}
.catgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.catlink{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:18px;box-shadow:var(--shadow);color:inherit}
.catlink:hover{border-color:#d9c99b;text-decoration:none;transform:translateY(-1px)}
.catlink .c{font-size:12px;color:var(--gold);font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.catlink .t{font-size:17px;font-weight:700;margin:6px 0 3px}
.catlink .d{font-size:12.7px;color:var(--muted)}
ul.clean{margin:8px 0 0;padding-left:18px;color:#333a44}
ul.clean li{margin:4px 0}
.checklist{list-style:none;margin:0;padding:0}
.checklist li{display:flex;gap:10px;padding:9px 0;border-bottom:1px dashed #efeade;font-size:13.8px}
.checklist li:last-child{border-bottom:none}
.checklist .k{flex:0 0 22px;font-weight:800;color:var(--gold)}
.note{background:#faf8f2;border:1px solid var(--line);border-left:3px solid var(--gold);
  border-radius:8px;padding:12px 14px;font-size:13.4px;color:#4a5260}
.flag{padding:18px;border-radius:var(--radius);border:1px solid var(--line);background:var(--card);box-shadow:var(--shadow)}
.flag.high{border-left:4px solid var(--bad)}
.flag.medium{border-left:4px solid #c98b12}
.flag.low{border-left:4px solid #8a95a6}
.flag h3{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.flag p{margin:6px 0;color:#3d4552;font-size:13.6px}
.flag .meta{font-size:12.2px;color:var(--muted);margin-top:8px}
label.f{display:block;font-size:12.3px;font-weight:700;color:var(--muted);margin:0 0 4px;letter-spacing:.03em}
input,select{width:100%;padding:10px 11px;border:1px solid #ddd6c6;border-radius:9px;font-size:14px;
  background:#fff;color:var(--ink);font-variant-numeric:tabular-nums}
input:focus,select:focus{outline:2px solid #e6cf95;outline-offset:1px;border-color:#cbb271}
.calcgrid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.out{margin-top:16px;display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.out .box{background:#fbf7ec;border:1px solid #ecdfbd;border-radius:10px;padding:13px 15px}
.out .box .l{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:#7a6a44;font-weight:700}
.out .box .v{font-size:21px;font-weight:750;letter-spacing:-.4px;margin-top:3px}
.out .box .s{font-size:11.8px;color:#7a6a44;margin-top:2px}
pre.qa{background:#1c1f24;color:#e8e6df;padding:16px;border-radius:12px;overflow:auto;
  font-size:12.3px;line-height:1.5}
footer{border-top:1px solid var(--line);padding:24px 0 40px;color:var(--muted);font-size:12.6px}
footer .row{display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between}
.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:13.4px}
.kv dt{color:var(--muted)}
.kv dd{margin:0;font-weight:600}
@media(max-width:640px){h1{font-size:25px}.topbar{min-height:auto;padding:10px 0}nav.main{margin-left:0}}
"""


# ---------------------------------------------------------------- helpers
def esc(value) -> str:
    return html.escape(str(value), quote=True)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_price(item) -> str:
    if item.get("price") is None:
        return f'<span class="blank" title="not present on the retrieved page">{DASH}</span>'
    cur = item.get("currency", "USD")
    sym = {"USD": "$", "EUR": "€"}.get(cur, cur + " ")
    return f"{sym}{item['price']:,.2f}"


def fmt_num(value, suffix="", digits=None):
    if value is None:
        return f'<span class="blank" title="not published on the source page">{DASH}</span>'
    if digits is None:
        text = f"{value:d}" if isinstance(value, int) else f"{value:g}"
    else:
        text = f"{value:.{digits}f}"
    return f"{text}{suffix}"


def basis_label(basis: str) -> str:
    return {
        "setting_price": "Setting only",
        "complete_ring": "Complete ring",
    }.get(basis, basis)


def basis_badge(basis: str) -> str:
    cls = "b-neutral" if basis == "setting_price" else "b-info"
    return f'<span class="badge {cls}">{esc(basis_label(basis))}</span>'


def status_badge(status: str) -> str:
    if status.startswith("verified_price_and_metal"):
        return '<span class="badge b-ok">price + metal verified</span>'
    if status.startswith("verified_price_karat"):
        return '<span class="badge b-ok">price + karat verified</span>'
    if status.startswith("verified_price_non_usd"):
        return '<span class="badge b-part">price verified (EUR)</span>'
    if status.startswith("weight_verified"):
        return '<span class="badge b-part">weight verified · price blank</span>'
    return f'<span class="badge b-part">{esc(status)}</span>'


def page(title: str, active: str, body: str, root: str = "") -> str:
    nav_items = [
        ("index.html", "Dashboard", "dashboard"),
        ("solitaire.html", "Solitaire", "solitaire"),
        ("halo-pave.html", "Halo & Pavé", "halo-pave"),
        ("three-stone-vintage.html", "Three-Stone", "three-stone-vintage"),
        ("18k.html", "18K", "18k"),
        ("budget.html", "10K", "budget"),
        ("retailers.html", "Retailers", "retailers"),
        ("prices.html", "Calculator", "prices"),
        ("flags.html", "Flagged", "flags"),
        ("methods.html", "Method", "methods"),
    ]
    def nav_link(href, label, key):
        cls = ' class="active"' if key == active else ""
        return f'<a href="{root}{href}"{cls}>{esc(label)}</a>'

    links = "".join(nav_link(href, label, key) for href, label, key in nav_items)
    result = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · GOLD2</title>
<meta name="description" content="Source-backed engagement-ring observations. Unverified construction, prices and inspection permission are flagged.">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="top">
  <div class="wrap topbar">
    <a class="brand" href="{root}index.html"><span class="dot"></span>GOLD2 <span class="chip">research</span></a>
    <nav class="main">{links}</nav>
  </div>
</header>
<main><div class="wrap">
<section class="note"><strong>No hallucinations. No invented prices.</strong> Dated source observations are not independent tests. This is the earlier 16-entry register; <a href="{root}explore/"><strong>open the combined 32-entry dashboard</strong></a> for all researched entries, explicit assumptions and field-level evidence. <a href="{root}explore/review/">Flagged for Review</a>.</section>
{body}
</div></main>
<footer><div class="wrap row">
  <div><strong>GOLD2</strong> · gold engagement ring research · data retrieved 2026-10-22 (UTC)</div>
  <div>Recorded observations link to their sources; automated consistency checks do not prove truth. Blank means unverified, never estimated.</div>
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


# ---------------------------------------------------------------- data
def all_items():
    items = []
    for key, fname in CATEGORY_FILES:
        payload = load(DATA / "listings" / fname)
        for item in payload["items"]:
            item["_category_id"] = payload["category_id"]
            item["_category_label"] = payload["category_label"]
            items.append(item)
    return items


def category_payloads():
    return [load(DATA / "listings" / fname) for _, fname in CATEGORY_FILES]


# ---------------------------------------------------------------- fragments
def listing_table(items) -> str:
    rows = []
    for it in items:
        flag_links = " ".join(
            f'<a href="flags.html#{f.lower()}">{esc(f)}</a>' for f in it.get("flags", [])
        )
        rows.append(
            "<tr class=\"item-row\">"
            f'<td><div class="itemname">{esc(it["name"])}</div>'
            f'<div class="sub">{esc(it["brand"])} · SKU {esc(it["sku"] or "unverified")}</div></td>'
            f'<td>{esc(it["retailer"])}</td>'
            f'<td class="num">{fmt_num(it.get("karat"), "K")}</td>'
            f'<td>{esc(it.get("color") or "—")}</td>'
            f'<td class="num">{fmt_num(it.get("width_mm"), " mm")}</td>'
            f'<td class="num">{fmt_num(it.get("weight_g"), " g", 2)}<div class="sub">{esc(it.get("weight_basis") or "")}</div></td>'
            f'<td class="num"><strong>{fmt_price(it)}</strong>'
            + (f'<div class="sub">was {it["original_price"]:,.2f}</div>' if it.get("original_price") else "")
            + "</td>"
            f'<td>{basis_badge(it["price_basis"])}</td>'
            f'<td class="src"><a href="{esc(it["source_url"])}" target="_blank" rel="noopener noreferrer">official listing&nbsp;↗</a>'
            f'<div class="sub">retrieved {esc(it["retrieved_at"])}</div></td>'
            f'<td>{status_badge(it["verification_status"])}'
            f'<div class="sub">{flag_links}</div></td>'
            "</tr>"
        )
    return (
        '<div class="tablewrap"><table><thead><tr>'
        "<th>Item</th><th>Retailer</th><th>Karat</th><th>Colour</th><th>Band width</th>"
        "<th>Weight</th><th>Price</th><th>Price basis</th><th>Source</th><th>Verification</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def price_summary(items) -> str:
    by_basis = {}
    for it in items:
        if it.get("price") is None:
            continue
        by_basis.setdefault(it["price_basis"], []).append(it)
    parts = []
    for basis, group in by_basis.items():
        currencies = sorted({i["currency"] for i in group})
        if len(currencies) > 1:
            bits = []
            for c in currencies:
                vals = [i["price"] for i in group if i["currency"] == c]
                lo_c, hi_c = min(vals), max(vals)
                bits.append(
                    f"{c} {lo_c:,.2f}" if lo_c == hi_c else f"{c} {lo_c:,.2f}–{hi_c:,.2f}"
                )
            detail = "; ".join(bits)
            parts.append(f"{len(group)} {basis_label(basis).lower()} row(s) — {detail} (not converted)")
        else:
            lo = min(i["price"] for i in group)
            hi = max(i["price"] for i in group)
            sym = {"USD": "$", "EUR": "€"}.get(currencies[0], currencies[0] + " ")
            span = f"{sym}{lo:,.2f}" if lo == hi else f"{sym}{lo:,.2f} – {sym}{hi:,.2f}"
            parts.append(f"{len(group)} {basis_label(basis).lower()} row(s) — {span}")
    return " · ".join(parts)


# ---------------------------------------------------------------- pages
def build_index(items, payloads, flags, gold, qa_summary):
    verified = sum(1 for i in items if i["verification_status"].startswith("verified"))
    weights = sum(1 for i in items if i.get("weight_g") is not None)
    high_flags = sum(1 for f in flags if f["severity"] == "high")
    cat_cards = "".join(
        f'<a class="catlink" href="{p["category_id"]}.html">'
        f'<div class="c">{len(p["items"])} item(s)</div>'
        f'<div class="t">{esc(p["category_label"])}</div>'
        f'<div class="d">{esc(price_summary(p["items"]))}</div></a>'
        for p in payloads
    )
    checklist = [
        ("Purity", "Karat is recorded only where the retailer states it on the page. 10K, 14K and 18K rows are kept separate."),
        ("Solid gold", f"The listing must say <em>solid gold</em>. {sum(1 for i in items if not i.get('solid_gold_explicit'))} of {len(items)} captured listings state a karat but never that phrase — see F-001."),
        ("Hallmark", f"Karat stamp plus maker's mark. {sum(1 for i in items if not i.get('hallmark_stated'))} of {len(items)} listings state neither — see F-002."),
        ("Weight", f"Grams. Published for {sum(1 for i in items if i.get('weight_g') is not None)} of {len(items)} items; blank everywhere else — see F-003."),
        ("Seller", f"{len({i['retailer_id'] for i in items})} retailers with official pages; contact details recorded only where published."),
        ("Price", "Dated page displays observed on 2026-10-22; no live feed with its basis (setting-only vs complete ring). Cached snippet prices were rejected in 3 cases."),
        ("Returns", "Policy coverage is incomplete. Confirm the exact order, fees, resized/custom exclusions and inspection permission — see F-010/F-011."),
        ("Payment", "Blue Nile Credit Card offers are displayed; accepted networks and issuer protection terms remain unconfirmed — see F-012."),
        ("Records", "Keep research URL/date/evidence plus your receipt, exact selected configuration, seller replies, certificates, paired-mark photos and test report."),
        ("On arrival", "Independent professional weight/purity assessment before wear or resizing, within written return permission; surface XRF alone can mislead."),
    ]
    check_html = "".join(
        f'<li><span class="k">{n:02d}</span><span><strong>{esc(k)}.</strong> {v}</span></li>'
        for n, (k, v) in enumerate(checklist, 1)
    )
    top_flags = sorted(flags, key=lambda f: {"high": 0, "medium": 1, "low": 2}[f["severity"]])[:4]
    flag_cards = "".join(
        f'<div class="flag {f["severity"]}"><h3>{esc(f["id"])} · {esc(f["title"])}'
        f'<span class="badge {"b-bad" if f["severity"]=="high" else "b-part" if f["severity"]=="medium" else "b-neutral"}">'
        f'{esc(f["severity"])}</span></h3>'
        f'<p>{esc(f["detail"][:260])}{"…" if len(f["detail"])>260 else ""}</p>'
        f'<div class="meta"><a href="flags.html#{f["id"].lower()}">Read full flag →</a></div></div>'
        for f in top_flags
    )

    body = f"""
<section class="banner">
  <span class="pill">NO HALLUCINATIONS</span>
  <h2>No invented values: a policy, not a guarantee of perfect verification.</h2>
  <p>Every price, karat and width below was read off the retailer's own page on <strong>2026&#8209;10&#8209;22 (UTC)</strong>, and each row links to that exact page.
  If a value was not on the page it is left <strong>blank</strong> and listed on the <a href="flags.html">Flagged for Review</a> page instead of being filled in.
  Cached search-engine numbers are treated as unverified: where a snippet disagreed with the live page, the live page won and the snippet is logged as rejected (see F&#8209;004, F&#8209;005, F&#8209;006).</p>
  <p class="flagline"><strong>Re-check this every pass.</strong> Before trusting any row, open its source link and re-read the price and karat. If the page disagrees with this table, the page is right and the table is stale.
  Automated checks: <strong>{qa_summary}</strong> — full log in <a href="methods.html">Method &amp; QA</a>.</p>
</section>

<h1>Gold engagement-ring research — original category register</h1>
<p class="lead">{len(items)} listings from 4 retailers, sorted into five categories, with the price basis made explicit because a
"setting price" does not include the diamond. The three things almost no retailer publishes — the words
<em>solid gold</em>, a hallmark / maker's mark, and the gram weight — remain gaps: construction and paired marks are unconfirmed for all targets; one seller states a size-specific metal weight.</p>

<div class="grid g4" style="margin:18px 0 8px">
  <div class="card stat"><div class="n">{len(items)}</div><div class="l">listings captured</div></div>
  <div class="card stat"><div class="n">{verified}</div><div class="l">rows with sourced price + stated metal (not physical verification)</div></div>
  <div class="card stat"><div class="n">{weights}<span style="font-size:15px;color:#5b6472">/{len(items)}</span></div><div class="l">rows with published gram weight</div></div>
  <div class="card stat"><div class="n">{len(flags)}</div><div class="l">flags · {high_flags} high severity</div></div>
</div>

<div class="card" style="margin-top:16px">
  <div class="eyebrow">Gold reference used by the calculator</div>
  <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:baseline;margin-top:6px">
    <div style="font-size:27px;font-weight:750">${gold["usd_per_troy_oz"]:,.2f}<span style="font-size:14px;color:#5b6472"> / troy oz</span></div>
    <div style="color:#5b6472;font-size:13.4px">quote date {esc(gold["quote_date"] or "unconfirmed — see F-017")} · retrieved {esc(gold["retrieved_at"])} ·<br>
    <a href="{esc(gold["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(gold["source_name"])} ↗</a></div>
    <a class="badge b-info" href="prices.html">Open melt calculator →</a>
  </div>
</div>

<h2>Browse by category</h2>
<div class="catgrid">{cat_cards}</div>

<h2>What this project checks</h2>
<div class="card"><ul class="checklist">{check_html}</ul>
<div class="note" style="margin-top:14px">The key rule: a <strong>14K or 18K stamp alone does not prove purity</strong>.
No seller is certified trustworthy here. Require independent professional assessment and a qualifying return before purchase; see the expanded buying checklist and GIA testing caveat.</div></div>

<h2>Top flagged items</h2>
<div class="grid g2">{flag_cards}</div>
<p style="margin-top:14px"><a href="flags.html"><strong>See all {len(flags)} flags →</strong></a></p>
"""
    return page("Dashboard", "dashboard", body)


def build_category(payload, items, flags):
    flag_ids = {f["id"] for f in flags}
    relevant = sorted({f for it in items for f in it.get("flags", []) if f in flag_ids})
    flag_defs = [f for f in flags if f["id"] in relevant]
    flag_list = "".join(
        f'<li><strong><a href="flags.html#{f["id"].lower()}">{esc(f["id"])}</a></strong> {esc(f["title"])} '
        f'<span class="badge {"b-bad" if f["severity"]=="high" else "b-part" if f["severity"]=="medium" else "b-neutral"}">{esc(f["severity"])}</span></li>'
        for f in sorted(flag_defs, key=lambda f: {"high": 0, "medium": 1, "low": 2}[f["severity"]])
    )
    body = f"""
<div class="eyebrow">{esc(payload["category_label"])}</div>
<h1>{esc(payload["category_label"])} gold engagement rings</h1>
<p class="lead">{len(items)} verified listing(s). Price summary: {esc(price_summary(items))}.
Blank cells are values the retailer does not publish — they are not zero and not estimates.</p>
<div class="note" style="margin-bottom:16px">
<strong>Read the price basis column first.</strong> "Setting only" excludes the center diamond; "Complete ring" includes its diamonds.
The two are not comparable, so no cross-basis ranking is shown anywhere on this site.
</div>
{listing_table(items)}
<h2>Flags touching these items</h2>
<ul class="clean">{flag_list or "<li>None.</li>"}</ul>
<p style="margin-top:16px"><a href="index.html">← Back to dashboard</a></p>
"""
    return page(payload["category_label"], payload["category_id"], body)


def build_retailers(retailers, items):
    rows = []
    for r in retailers:
        n = sum(1 for i in items if i["retailer_id"] == r["id"])
        ret = (
            f'<a href="{esc(r["return_policy_url"])}" target="_blank" rel="noopener noreferrer">policy ↗</a>'
            if r["return_policy_url"]
            else '<span class="blank">not captured</span>'
        )
        window = f'{r["return_window_days"]} days' if r["return_window_days"] else '<span class="blank">not stated</span>'
        excl = []
        if r["return_excludes_resized"]:
            excl.append("resized")
        if r["return_excludes_custom"]:
            excl.append("custom")
        excl_s = ", ".join(excl) if excl else '<span class="blank">unknown</span>'
        contact = " · ".join(
            x for x in [
                esc(r["contact_phone"]) if r["contact_phone"] else None,
                esc(r["contact_email"]) if r["contact_email"] else None,
            ] if x
        ) or '<span class="blank">not captured</span>'
        rows.append(
            "<tr>"
            f'<td><strong>{esc(r["name"])}</strong><div class="sub"><a href="{esc(r["website"])}" target="_blank" rel="noopener noreferrer">{esc(r["website"].replace("https://",""))} ↗</a></div></td>'
            f'<td class="num">{n}</td>'
            f'<td>{window}<div class="sub">{ret}</div></td>'
            f'<td>{excl_s}</td>'
            f'<td>{contact}<div class="sub">{esc(r["price_display_basis"])}</div></td>'
            f'<td><span class="badge {"b-ok" if r["verification_status"].startswith("verified") else "b-part"}">{esc(r["verification_status"].replace("_"," "))}</span></td>'
            "</tr>"
        )
    body = f"""
<div class="eyebrow">Seller due diligence</div>
<h1>Retailers &amp; policies</h1>
<p class="lead">Only what the retailer's own pages state. A blank cell means the page did not say it — for example, no captured
page states which card networks are accepted, so that field is empty rather than assumed.</p>
<div class="tablewrap"><table><thead><tr>
<th>Retailer</th><th>Rows</th><th>Return window</th><th>Excludes</th><th>Contact / price basis</th><th>Status</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table></div>

<h2>Why the exclusions matter</h2>
<div class="note">A resize can void the return right. Blue Nile excludes <em>items resized after initial purchase</em> and
custom orders from returns, and offers one free resize within six months. The safe order is therefore:
receive → independent XRF test and weighing → only then resize. If the test is refused or the ring fails, return it untouched.</div>

<h2>Marketplace note</h2>
<div class="note"><strong>James Allen</strong> product URLs now redirect to Blue Nile and at least one cached James Allen ring
(item 41515) rendered as "This popular style is sold out". James Allen designs appear inside the Blue Nile catalogue,
so the brand on the ring and the company you buy from are no longer the same. See flag <a href="flags.html#f-009">F-009</a>.</div>
"""
    return page("Retailers", "retailers", body)


def build_flags(flags, items_in_flags):
    order = {"high": 0, "medium": 1, "low": 2}
    cards = []
    for f in sorted(flags, key=lambda x: (order[x["severity"]], x["id"])):
        badge = {"high": "b-bad", "medium": "b-part", "low": "b-neutral"}[f["severity"]]
        affected = ", ".join(f["affected_items"]) if f["affected_items"] else "—"
        sources = "".join(
            f'<li><a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{esc(u)}</a></li>' for u in f["sources"]
        )
        cards.append(f"""
<article class="flag {f["severity"]}" id="{f["id"].lower()}">
  <h3>{esc(f["id"])} · {esc(f["title"])}
    <span class="badge {badge}">{esc(f["severity"])}</span>
    <span class="badge b-neutral">{esc(f["type"].replace("_"," "))}</span></h3>
  <p>{esc(f["detail"])}</p>
  <p><strong>Recommended action:</strong> {esc(f["recommended_action"])}</p>
  <p class="meta"><strong>Affected rows:</strong> {esc(affected)}</p>
  <p class="meta"><strong>Source links:</strong></p>
  <ul class="clean" style="margin-top:0;font-size:12.6px">{sources}</ul>
</article>""")
    total = len(items_in_flags)
    solid_n = sum(1 for i in items_in_flags if not i.get("solid_gold_explicit"))
    weight_missing = sum(1 for i in items_in_flags if i.get("weight_g") is None)
    body = f"""
<div class="eyebrow">Do not treat these as verified</div>
<h1>Flagged for review</h1>
<p class="lead">Everything that could not be confirmed, disagreed with a cached value, or is a policy gap.
Flags do not block the shortlist — they tell you exactly what to ask the seller and what to check on arrival.
Each flag links to the page that produced it.</p>
<div class="note" style="margin-bottom:18px">
<strong>No-hallucination policy, applied.</strong> These are the values that were deliberately <em>not</em> filled in.
The strongest pattern: {solid_n} of {total} listings state a karat but none states the words “solid gold”, none states a
hallmark or maker's mark, and {weight_missing} of {total} never publish a gram weight. That is a gap in the listings, not proof
the rings are bad — but it is exactly the gap an independent jeweller visit closes.</div>
<div class="grid" style="grid-template-columns:1fr">{''.join(cards)}</div>
"""
    return page("Flagged for Review", "flags", body)


def build_prices(gold, items, weights_note):
    # Conditional reference calculations only. No product mass is physically verified.
    grams_oz = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    nist = 'https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf'
    ftc = 'https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry'
    context = f'<a href="{nist}" rel="noopener noreferrer">NIST units</a> · <a href="{ftc}" rel="noopener noreferrer">FTC karat definition</a> · <a href="{esc(gold["source_url"])}" rel="noopener noreferrer">Recorded WGC input</a>'
    ref_rows = ''.join(f'<tr><td>{k}K nominal</td><td>{k/24*100:.4f}%</td><td>{6*k/24:.3f} g</td><td>${6*k/24/grams_oz*spot:,.2f} USD</td><td>{context}</td></tr>' for k in (10,14,18,22,24))
    known_rows = ''.join(f'<tr><td>{esc(i["name"])}</td><td>{esc(i.get("weight_basis") or "Unconfirmed weight basis")}</td><td>{i["weight_g"]*i["karat"]/24:.3f} g conditional</td><td>${i["weight_g"]*i["karat"]/24/grams_oz*spot:,.2f} USD conditional</td><td><a href="{esc(i["source_url"])}" rel="noopener noreferrer">Official product</a> · {context}</td></tr>' for i in items if i.get('weight_g'))
    body = f'''
<div class="eyebrow">Conditional reference / not an appraisal</div>
<h1>Gold content without inferred product values</h1>
<p class="lead">No ring in this register has independently verified net-gold weight and purity. All product-specific verified fine-gold values remain blank. The former interactive calculator is replaced by the evidence-gated expanded calculator.</p>
<div class="card"><h2>Use the expanded calculator</h2><p><a href="explore/calculator/">Open documented products or an explicitly acknowledged conditional scenario →</a></p><p>Enter only gold-alloy-only grams, excluding stones and non-gold components, and a compatible USD reference. No imaginary retail thresholds, guaranteed scrap floor, or automatic weight fallback is used.</p></div>
<h2>Earlier recorded WGC input</h2><p>${spot:,.2f} USD per troy ounce was an earlier header observation retrieved {esc(gold['retrieved_at'])}, not a live quote. Its exact source quote-as-of date is unconfirmed and left blank. Chart metadata does not date a moving header. <a href="flags.html#f-017">F-017</a> · <a href="{esc(gold['source_url'])}">Official WGC page</a>.</p>
<h2>Conditional nominal reference — assumed 6g of gold alloy</h2><p>These are explicitly hypothetical arithmetic inputs, not researched ring weights or verified product gold. Nominal karat/24 is distinct from an explicitly supplied decimal fineness.</p><div class="tablewrap"><table><thead><tr><th>Nominal karat</th><th>Nominal fineness</th><th>Calculated fine mass</th><th>Theoretical spot value at recorded input</th><th>Official method / input context</th></tr></thead><tbody>{ref_rows}</tbody></table></div>
<h2>Size-specific seller claim — conditional illustration only</h2><p>VRAI's stated 2.86g metal weight applies to ring size 6. It is not independently weighed or assayed; the values below assume that entire stated metal mass has the nominal listed purity. This is not a verified ring valuation.</p><div class="tablewrap"><table><thead><tr><th>Item</th><th>Published basis</th><th>Conditional calculated mass</th><th>Conditional spot value</th><th>Source / method</th></tr></thead><tbody>{known_rows}</tbody></table></div>
<p>No allowance for stones, workmanship, taxes, refining loss or buyer spreads. There is no guaranteed resale floor or normal-retail multiple. <a href="explore/review/">Read all limitations</a> before using any result.</p>
'''
    return page('Conditional gold reference', 'prices', body)


def build_methods(qa_text, gold, items, flags):
    body = f"""
<div class="eyebrow">Method, sources, audit</div>
<h1>Method &amp; QA</h1>
<p class="lead">This page exists so the table can be challenged. It records how each value was obtained, what was
refused, and the result of the automated checks that run after every review.</p>

<h2>1. The no-hallucination rule</h2>
<div class="banner" style="padding:18px 20px">
<p><strong>A value is only published if it was read off a page that was actually retrieved.</strong>
Each row stores the URL, the UTC retrieval date, and a verbatim quote list in <code>evidence/</code>.
The build fails the audit if a quote cannot be found in its evidence file. Anything not on the page is <code>null</code>
and appears on the <a href="flags.html">Flagged</a> page. No value is derived by averaging, conversion or “reasonable assumption”.</p>
</div>

<h2>2. Source hierarchy</h2>
<ul class="clean">
<li><strong>Tier 1 — product facts:</strong> the retailer's own product page (Blue Nile, Zales, VRAI, Brilliant Earth).</li>
<li><strong>Tier 1 — policies:</strong> the retailer's own return policy page.</li>
<li><strong>Tier 1 — gold price:</strong> World Gold Council gold spot page, market data by ICE Data Services, with an explicit quote date.</li>
<li><strong>Rejected:</strong> search-engine snippets, aggregators, blogs, coupon sites, marketplace listings.
A snippet is never a source — it was caught disagreeing with the live page three times in this pass (F-004, F-005, F-006).</li>
</ul>

<h2>3. Known limitations</h2>
<ul class="clean">
<li>LBMA fix data now sits behind an IBA licence, so the free World Gold Council spot quote is used instead (F-013).</li>
<li>Brilliant Earth served EUR at retrieval; the USD price is not recorded and was not converted (F-007).</li>
<li>VRAI renders its price client-side; the retrieved HTML had no price, so that cell is blank (F-008).</li>
<li>Costco was probed and excluded: price and gram weight did not render (F-014).</li>
<li>No listing states a hallmark, a maker's mark, or the words “solid gold” (F-001, F-002).</li>
<li>Only one item publishes a gram weight, so price-per-gram comparison is not possible for the rest (F-003).</li>
</ul>

<h2>4. Automated checks after every review</h2>
<p>Run <code>python3 tools/qa.py</code> (then <code>python3 tools/build_site.py</code>) after any edit. The audit
re-reads every JSON file and fails on: a quote missing from its evidence file, a non-null price/weight/width without a
supporting quote, a source URL outside the retailer's own domain, a rejected cached value that matches the published value,
a flag pointing at a missing item, or a broken internal link in the built site.</p>
<pre class="qa">{esc(qa_text.strip()) if qa_text.strip() else "QA report not generated yet."}</pre>

<h2>5. Earlier pass preserved</h2>
<p>The <code>site/</code> folder holds the first dashboard built in this repository (session
<code>39da17c8</code>): two Blue Nile settings, its own audit script and calculator. It is preserved with a documented currency correction
and still works: <a href="site/index.html">open the earlier dashboard ↗</a>. Its two rings were re-fetched
live during integration and now appear as <code>BN-195402</code> and <code>BN-302868</code> on the
<a href="halo-pave.html">Halo &amp; Pavé</a> page.</p>

<h2>6. Data provenance summary</h2>
<dl class="kv">
<dt>Items</dt><dd>{len(items)}</dd>
<dt>Flags</dt><dd>{len(flags)}</dd>
<dt>Gold quote</dt><dd>${gold["usd_per_troy_oz"]:,.2f}/oz · {esc(gold["quote_date"] or "unconfirmed — see F-017")} · <a href="{esc(gold["source_url"])}" target="_blank" rel="noopener noreferrer">World Gold Council ↗</a></dd>
<dt>Retrieval dates</dt><dd>2026-10-22 (UTC)</dd>
<dt>Repository</dt><dd><a href="https://github.com/karagemop466-tech/GOLD2" target="_blank" rel="noopener noreferrer">karagemop466-tech/GOLD2 ↗</a></dd>
</dl>

<h2>7. What to do with a flagged row</h2>
<ol class="clean">
<li>Open the source link and re-read the price, karat and width yourself.</li>
<li>Ask the seller, in writing: <em>“Is this solid gold (not plated or filled), what is the gram weight, and what hallmark and maker's mark are stamped inside?”</em></li>
<li>Keep the reply with the order record.</li>
<li>On arrival, before wearing or resizing, have an independent jeweller XRF-test the metal and weigh it.</li>
<li>If the seller will not allow independent verification or a return, do not buy.</li>
</ol>
"""
    return page("Method & QA", "methods", body)


def main():
    (SITE / "assets").mkdir(exist_ok=True)
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    gold = load(DATA / "gold-price.json")
    retailers = load(DATA / "retailers.json")["retailers"]
    flags = load(DATA / "flags.json")["flags"]
    payloads = category_payloads()
    items = all_items()

    qa_path = ROOT / "reports" / "qa-report.md"
    qa_text = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_summary = "not run yet"
    for line in qa_text.splitlines():
        if "RESULT:" in line:
            qa_summary = line.split("RESULT:", 1)[1].replace("*", "").strip(" -—").strip()
            break

    pages = {"index.html": build_index(items, payloads, flags, gold, qa_summary)}
    for payload in payloads:
        pages[f'{payload["category_id"]}.html'] = build_category(
            payload, payload["items"], flags
        )
    pages["retailers.html"] = build_retailers(retailers, items)
    pages["flags.html"] = build_flags(flags, items)
    known = [i for i in items if i.get("weight_g")]
    weights_note = (
        f"{len(known)} of {len(items)} rows publish{'es' if len(known) == 1 else ''} a gram weight. "
        "The rest are blank, so no melt comparison is shown for them. A blank is not zero."
    )
    pages["prices.html"] = build_prices(gold, items, weights_note)
    pages["methods.html"] = build_methods(qa_text, gold, items, flags)

    for name, content in pages.items():
        (SITE / name).write_text(content, encoding="utf-8")

    # no build artefacts inside the site folder
    for junk in (SITE / ".DS_Store",):
        if junk.exists():
            junk.unlink()
    (SITE / "assets" / "style.css").write_text(CSS + "\n" + "\n".join("." + k + "{" + v + "}" for k,v in sorted(INLINE_STYLES.items())), encoding="utf-8")
    print(f"built {len(pages)} pages into {SITE}")


if __name__ == "__main__":
    main()
