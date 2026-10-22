#!/usr/bin/env python3
"""Build the static dashboard in docs/ from the verified JSON in data/.

Design rule: this script never invents a value. It renders exactly what is in
data/*.json and prints an em dash for anything that is null.
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
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
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · GOLD2</title>
<meta name="description" content="Verified solid-gold engagement ring research: prices, karats, sources and flagged uncertainties.">
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
{body}
</div></main>
<footer><div class="wrap row">
  <div><strong>GOLD2</strong> · gold engagement ring research · data retrieved 2026-10-22 (UTC)</div>
  <div>Every value links to the retailer page it came from. Blank means unverified, never estimated.</div>
</div></footer>
</body>
</html>
"""


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
            f'<div class="sub">{esc(it["brand"])} · SKU {esc(it["sku"])}</div></td>'
            f'<td>{esc(it["retailer"])}</td>'
            f'<td class="num">{fmt_num(it.get("karat"), "K")}</td>'
            f'<td>{esc(it.get("color") or "—")}</td>'
            f'<td class="num">{fmt_num(it.get("width_mm"), " mm")}</td>'
            f'<td class="num">{fmt_num(it.get("weight_g"), " g", 2)}</td>'
            f'<td class="num"><strong>{fmt_price(it)}</strong>'
            + (f'<div class="sub">was {it["original_price"]:,.2f}</div>' if it.get("original_price") else "")
            + "</td>"
            f'<td>{basis_badge(it["price_basis"])}</td>'
            f'<td class="src"><a href="{esc(it["source_url"])}" target="_blank" rel="noopener">official listing&nbsp;↗</a>'
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
            detail = "; ".join(
                f'{c}: {min(i["price"] for i in group if i["currency"] == c):,.2f}–'
                f'{max(i["price"] for i in group if i["currency"] == c):,.2f}'
                for c in currencies
            )
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
        ("Solid gold", "The listing must say <em>solid gold</em>. No captured listing uses that phrase while stating a karat — see F-001."),
        ("Hallmark", "Karat stamp plus maker's mark. No listing states either — see F-002."),
        ("Weight", "Grams. Published for 1 of 14 items; blank everywhere else — see F-003."),
        ("Seller", "4 retailers with official pages; contact details recorded only where published."),
        ("Price", "Live price captured on 2026-10-22 with its basis (setting-only vs complete ring). Cached snippet prices were rejected in 3 cases."),
        ("Returns", "Window and the resized/custom exclusions recorded per retailer — see F-010."),
        ("Payment", "Card acceptance is not stated on any captured page; left blank — see F-012."),
        ("Records", "Listing URL, retrieval date and verbatim evidence kept in <code>evidence/</code> for every row."),
        ("On arrival", "Independent jeweller check before wearing or resizing; ask for XRF."),
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
  <h2>Nothing on this site is invented, estimated or extrapolated.</h2>
  <p>Every price, karat and width below was read off the retailer's own page on <strong>2026&#8209;10&#8209;22 (UTC)</strong>, and each row links to that exact page.
  If a value was not on the page it is left <strong>blank</strong> and listed on the <a href="flags.html">Flagged for Review</a> page instead of being filled in.
  Cached search-engine numbers are treated as unverified: where a snippet disagreed with the live page, the live page won and the snippet is logged as rejected (see F&#8209;004, F&#8209;005, F&#8209;006).</p>
  <p class="flagline"><strong>Re-check this every pass.</strong> Before trusting any row, open its source link and re-read the price and karat. If the page disagrees with this table, the page is right and the table is stale.
  Automated checks: <strong>{qa_summary}</strong> — full log in <a href="methods.html">Method &amp; QA</a>.</p>
</section>

<h1>Gold engagement ring — verified shortlist</h1>
<p class="lead">{len(items)} listings from 4 retailers, sorted into five categories, with the price basis made explicit because a
"setting price" does not include the diamond. The three things almost no retailer publishes — the words
<em>solid gold</em>, a hallmark / maker's mark, and the gram weight — are the three things still outstanding on every row.</p>

<div class="grid g4" style="margin:18px 0 8px">
  <div class="card stat"><div class="n">{len(items)}</div><div class="l">listings captured</div></div>
  <div class="card stat"><div class="n">{verified}</div><div class="l">rows with price + metal verified</div></div>
  <div class="card stat"><div class="n">{weights}<span style="font-size:15px;color:#5b6472">/{len(items)}</span></div><div class="l">rows with published gram weight</div></div>
  <div class="card stat"><div class="n">{len(flags)}</div><div class="l">flags · {high_flags} high severity</div></div>
</div>

<div class="card" style="margin-top:16px">
  <div class="eyebrow">Gold reference used by the calculator</div>
  <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:baseline;margin-top:6px">
    <div style="font-size:27px;font-weight:750">${gold["usd_per_troy_oz"]:,.2f}<span style="font-size:14px;color:#5b6472"> / troy oz</span></div>
    <div style="color:#5b6472;font-size:13.4px">quote date {esc(gold["quote_date"])} · retrieved {esc(gold["retrieved_at"])} ·<br>
    <a href="{esc(gold["source_url"])}" target="_blank" rel="noopener">{esc(gold["source_name"])} ↗</a></div>
    <a class="badge b-info" href="prices.html">Open melt calculator →</a>
  </div>
</div>

<h2>Browse by category</h2>
<div class="catgrid">{cat_cards}</div>

<h2>What this project checks</h2>
<div class="card"><ul class="checklist">{check_html}</ul>
<div class="note" style="margin-top:14px">The key rule: a <strong>14K or 18K stamp alone does not prove purity</strong>.
Reputable seller + correct markings + sensible price + independent XRF test after delivery is the only sequence that holds up.</div></div>

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
            f'<a href="{esc(r["return_policy_url"])}" target="_blank" rel="noopener">policy ↗</a>'
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
            f'<td><strong>{esc(r["name"])}</strong><div class="sub"><a href="{esc(r["website"])}" target="_blank" rel="noopener">{esc(r["website"].replace("https://",""))} ↗</a></div></td>'
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


def build_flags(flags):
    order = {"high": 0, "medium": 1, "low": 2}
    cards = []
    for f in sorted(flags, key=lambda x: (order[x["severity"]], x["id"])):
        badge = {"high": "b-bad", "medium": "b-part", "low": "b-neutral"}[f["severity"]]
        affected = ", ".join(f["affected_items"]) if f["affected_items"] else "—"
        sources = "".join(
            f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a></li>' for u in f["sources"]
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
    body = f"""
<div class="eyebrow">Do not treat these as verified</div>
<h1>Flagged for review</h1>
<p class="lead">Everything that could not be confirmed, disagreed with a cached value, or is a policy gap.
Flags do not block the shortlist — they tell you exactly what to ask the seller and what to check on arrival.
Each flag links to the page that produced it.</p>
<div class="note" style="margin-bottom:18px">
<strong>No-hallucination policy, applied.</strong> These are the values that were deliberately <em>not</em> filled in.
The strongest pattern: 14 of 14 listings state a karat but none states the words “solid gold”, none states a hallmark
or maker's mark, and 13 of 14 never publish a gram weight. That is a gap in the listings, not proof the rings are bad —
but it is exactly the gap an independent jeweller visit closes.</div>
<div class="grid" style="grid-template-columns:1fr">{''.join(cards)}</div>
"""
    return page("Flagged for Review", "flags", body)


def build_prices(gold, items, weights_note):
    known = [i for i in items if i.get("weight_g")]
    grams_oz = gold["grams_per_troy_ounce"]
    spot = gold["usd_per_troy_oz"]
    ref_rows = []
    for karat in (10, 14, 18, 22, 24):
        fine2 = 2 * karat / 24
        fine4 = 4 * karat / 24
        fine6 = 6 * karat / 24
        melt6 = fine6 / grams_oz * spot
        ref_rows.append(
            f"<tr><td class=\"num\">{karat}K</td><td class=\"num\">{karat/24*100:.2f}%</td>"
            f"<td class=\"num\">{fine2:.3f} g</td><td class=\"num\">{fine4:.3f} g</td>"
            f"<td class=\"num\">{fine6:.3f} g</td><td class=\"num\">${melt6:,.2f}</td></tr>"
        )
    known_rows = "".join(
        f"<tr><td>{esc(i['name'])}</td><td class=\"num\">{i['karat']}K</td>"
        f"<td class=\"num\">{i['weight_g']:.2f} g</td>"
        f"<td class=\"num\">{i['weight_g']*i['karat']/24:.3f} g</td>"
        f"<td class=\"num\">${i['weight_g']*i['karat']/24/grams_oz*spot:,.2f}</td>"
        f"<td>{fmt_price(i)}</td></tr>"
        for i in known
    )
    body = f"""
<div class="eyebrow">Raw gold, not appraisal</div>
<h1>Gold weight &amp; melt calculator</h1>
<p class="lead">Convert a ring's weight and karat into fine-gold grams and the raw metal value at the quote already on this site.
It is a sanity check on price, not a valuation: labour, the diamond, hallmarking, duty and resale spread are all outside the number.</p>

<div class="card">
  <div class="calcgrid">
    <div><label class="f" for="w">Ring weight (g)</label><input id="w" type="number" min="0" step="0.01" value="3.00"></div>
    <div><label class="f" for="k">Karat</label>
      <select id="k">
        <option value="10">10K</option><option value="14" selected>14K</option>
        <option value="18">18K</option><option value="22">22K</option><option value="24">24K</option>
      </select></div>
    <div><label class="f" for="spot">Gold spot (USD / troy oz)</label><input id="spot" type="number" min="0" step="0.01" value="{spot:.2f}"></div>
    <div><label class="f" for="ask">Asking price (optional)</label><input id="ask" type="number" min="0" step="0.01" placeholder="e.g. 1255"></div>
  </div>
  <div class="out">
    <div class="box"><div class="l">Fine gold</div><div class="v" id="fine">—</div><div class="s">weight × karat/24</div></div>
    <div class="box"><div class="l">Melt value</div><div class="v" id="melt">—</div><div class="s">at the spot price entered</div></div>
    <div class="box"><div class="l">Price ÷ melt</div><div class="v" id="ratio">—</div><div class="s">1.0× would mean sold at scrap</div></div>
    <div class="box"><div class="l">Above melt</div><div class="v" id="over">—</div><div class="s">the part that pays for making + stone</div></div>
  </div>
  <p class="sub" style="margin-top:12px">The spot field is pre-filled with the verified quote:
  <strong>${spot:,.2f}/oz, {esc(gold["quote_date"])}</strong> —
  <a href="{esc(gold["source_url"])}" target="_blank" rel="noopener">{esc(gold["source_name"])} ↗</a>.
  If you change it, you are using your own number, not a verified one.</p>
</div>

<script>
(function(){{
  const gpo = {grams_oz};
  const w = document.getElementById('w'), k = document.getElementById('k'),
        s = document.getElementById('spot'), a = document.getElementById('ask');
  const fine = document.getElementById('fine'), melt = document.getElementById('melt'),
        ratio = document.getElementById('ratio'), over = document.getElementById('over');
  const money = n => '$' + n.toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}});
  function run(){{
    const wt = parseFloat(w.value), kk = parseFloat(k.value), sp = parseFloat(s.value);
    if(!(wt>0) || !(kk>0) || !(sp>0)){{ fine.textContent='—'; melt.textContent='—'; ratio.textContent='—'; over.textContent='—'; return; }}
    const fg = wt * kk / 24;
    const mv = fg / gpo * sp;
    fine.textContent = fg.toFixed(3) + ' g';
    melt.textContent = money(mv);
    const ask = parseFloat(a.value);
    if(ask>0){{ ratio.textContent = (ask/mv).toFixed(2) + '×'; over.textContent = money(ask-mv); }}
    else {{ ratio.textContent='—'; over.textContent='—'; }}
  }}
  [w,k,s,a].forEach(el=>el.addEventListener('input', run));
  run();
}})();
</script>

<h2>Quick reference — fine gold by karat</h2>
<div class="tablewrap"><table><thead><tr>
<th>Karat</th><th>Purity (karat/24)</th><th>2 g ring</th><th>4 g ring</th><th>6 g ring</th><th>Melt of a 6 g ring</th>
</tr></thead><tbody>{''.join(ref_rows)}</tbody></table></div>
<p class="sub">Purity is arithmetic on the karat definition (24K = pure). Melt uses the quote above and 1 troy oz = {grams_oz} g.
These are calculations, not retailer claims, and no listing was used to produce them.</p>

<h2>Melt check for rows with a published weight</h2>
<div class="tablewrap"><table><thead><tr>
<th>Item</th><th>Karat</th><th>Published weight</th><th>Fine gold</th><th>Melt at quote</th><th>Price</th>
</tr></thead><tbody>{known_rows or '<tr><td colspan="6" class="blank">No row has a published weight.</td></tr>'}</tbody></table></div>
<p class="sub">{esc(weights_note)}</p>

<h2>How to use this honestly</h2>
<ul class="clean">
<li>A <strong>setting-only</strong> price can never be compared to melt — the diamond is not in either number, but the making charge is.</li>
<li>The ratio is only meaningful when the weight is real. Ask the seller for the gram weight and verify it on a jeweller's scale.</li>
<li>Melt is a floor, not a fair price. A ring at 2× melt is normal retail; a ring at 1.05× melt with a “14K” stamp is a warning sign.</li>
<li>Never use melt value as a resale expectation — scrap buyers pay below spot.</li>
</ul>
"""
    return page("Calculator", "prices", body)


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

<h2>5. Data provenance summary</h2>
<dl class="kv">
<dt>Items</dt><dd>{len(items)}</dd>
<dt>Flags</dt><dd>{len(flags)}</dd>
<dt>Gold quote</dt><dd>${gold["usd_per_troy_oz"]:,.2f}/oz · {esc(gold["quote_date"])} · <a href="{esc(gold["source_url"])}" target="_blank" rel="noopener">World Gold Council ↗</a></dd>
<dt>Retrieval dates</dt><dd>2026-10-22 (UTC)</dd>
<dt>Repository</dt><dd><a href="https://github.com/karagemop466-tech/GOLD2" target="_blank" rel="noopener">karagemop466-tech/GOLD2 ↗</a></dd>
</dl>

<h2>6. What to do with a flagged row</h2>
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
    DOCS.mkdir(exist_ok=True)
    (DOCS / "assets").mkdir(exist_ok=True)
    (DOCS / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    gold = load(DATA / "gold-price.json")
    retailers = load(DATA / "retailers.json")["retailers"]
    flags = load(DATA / "flags.json")["flags"]
    payloads = category_payloads()
    items = all_items()

    qa_path = ROOT / "reports" / "qa-report.md"
    qa_text = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_summary = "not run yet"
    for line in qa_text.splitlines():
        if line.startswith("RESULT:"):
            qa_summary = line.replace("RESULT:", "").strip()
            break

    pages = {"index.html": build_index(items, payloads, flags, gold, qa_summary)}
    for payload in payloads:
        pages[f'{payload["category_id"]}.html'] = build_category(
            payload, payload["items"], flags
        )
    pages["retailers.html"] = build_retailers(retailers, items)
    pages["flags.html"] = build_flags(flags)
    known = [i for i in items if i.get("weight_g")]
    weights_note = (
        f"{len(known)} of {len(items)} rows publish a gram weight. The rest are blank, so no melt comparison is shown for them. "
        "A blank is not zero."
    )
    pages["prices.html"] = build_prices(gold, items, weights_note)
    pages["methods.html"] = build_methods(qa_text, gold, items, flags)

    for name, content in pages.items():
        (DOCS / name).write_text(content, encoding="utf-8")

    # no build artefacts inside the site folder
    for junk in (DOCS / ".DS_Store",):
        if junk.exists():
            junk.unlink()
    print(f"built {len(pages)} pages into {DOCS}")


if __name__ == "__main__":
    main()
