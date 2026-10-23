#!/usr/bin/env python3
"""GOLD2 static-site builder: renders data/*.json into HTML placeholders.

Placeholders: <!-- BUILD:RINGS_ROWS --> (rings.html),
<!-- BUILD:RETAILERS_ROWS --> (retailers.html), <!-- BUILD:FLAGS --> (flagged.html),
<!-- BUILD:STATS --> + <!-- BUILD:VERIFY_SUMMARY --> (index.html).

Run verify.py BEFORE build.py, and verify.py --check-build AFTER.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOG = ROOT / "verification-log.json"


def e(s) -> str:
    return html.escape("" if s is None else str(s))


def flag_tags(flags: list[str]) -> str:
    return " ".join(f'<a class="tag flag" href="flagged.html#{e(f)}">{e(f)}</a>' for f in flags)


def unverified_cell(note: str = "") -> str:
    extra = f'<br><span class="small muted">{e(note)}</span>' if note else ""
    return f'— <span class="tag unverified">unverified</span>{extra}'


def ring_rows(rings, retailers) -> str:
    out = []
    for r in rings:
        retailer = retailers.get(r["retailer_id"], {}).get("name", r["retailer_id"])
        if r.get("price_usd") is not None:
            price_str = "${:,}".format(r["price_usd"])
            price = ('<span class="tag verified">' + e(price_str) + "</span>"
                     '<br><span class="small muted">' + e(r.get("price_note", "")) + "</span>")
        else:
            price = unverified_cell(r.get("price_note", ""))
        weight = (f"{e(r['weight_g'])} g" if r.get("weight_g") is not None
                  else unverified_cell("not published on product page"))
        hall = (e(r["hallmark_stated"]) if r.get("hallmark_stated") is not None
                else unverified_cell("not described on product page"))
        karat_norm = (r.get("karat_stated") or "").upper().replace("KT", "K")
        out.append(
            "<tr data-karat=\"" + e(karat_norm) + "\">"
            f"<td><code>{e(r['id'])}</code></td>"
            f"<td><a href=\"{e(r['product_url'])}\">{e(r['name'])}</a></td>"
            f"<td>{e(retailer)}</td>"
            f"<td>{e(r.get('karat_stated'))}<br><span class=\"small muted\">{e(r.get('metal_stated'))}</span></td>"
            f"<td class=\"num\">{price}</td>"
            f"<td>{e(r.get('capture_date'))}</td>"
            f"<td><code>{e(r.get('stock_number'))}</code>"
            + (f"<br><span class=\"small\">width {e(r['width'])}</span>" if r.get("width") else "")
            + "</td>"
            f"<td class=\"small\">{e(r.get('extra_specs'))}</td>"
            f"<td>{weight}</td>"
            f"<td>{hall}</td>"
            f"<td>{flag_tags(r.get('flags', []))}</td>"
            "</tr>"
        )
    return "\n".join(out)


def retailer_rows(retailers: dict) -> str:
    out = []
    none_cell = '<span class="muted small">none</span>'
    for r in retailers.values():
        site = e(r["site_url"])
        contact_url = e(r["contact_url"])
        returns_url = e(r["returns_url"])
        notes_url = e(r["jewelry_notes_url"])
        flags_cell = flag_tags(r.get("flags", [])) or none_cell
        out.append(
            "<tr>"
            "<td><strong>" + e(r["name"]) + '</strong><br><a class="small" href="' + site + '">' + site + "</a></td>"
            '<td class="small">' + e(r["contact"]) + '<br><a href="' + contact_url + '">official contact page</a> '
            '<span class="tag verified">verified ' + e(r.get("contact_verified")) + "</span></td>"
            '<td class="small">' + e(r["returns_summary"]) + '<br><a href="' + returns_url + '">official returns page</a> '
            '<span class="tag verified">verified ' + e(r.get("returns_verified")) + "</span></td>"
            '<td class="small">' + e(r["jewelry_notes"]) + '<br><a href="' + notes_url + '">official source</a></td>'
            "<td>" + flags_cell + "</td>"
            "</tr>"
        )
    return "\n".join(out)


def flag_cards(flags, ring_ids, retailer_ids) -> str:
    out = []
    for f in flags:
        links = []
        for ref in f.get("applies_to", []):
            if ref in ring_ids:
                links.append(f'<a class="tag" href="rings.html">{e(ref)}</a>')
            elif ref in retailer_ids:
                links.append(f'<a class="tag" href="retailers.html">{e(ref)}</a>')
            else:
                links.append(f'<span class="tag">{e(ref)}</span>')
        out.append(
            f"<div class=\"card\" id=\"{e(f['id'])}\">"
            f"<h3>{e(f['id'])} — {e(f['title'])}</h3>"
            f"<p><strong>Applies to:</strong> {' '.join(links)}</p>"
            f"<p><strong>Issue:</strong> {e(f['issue'])}</p>"
            f"<p><strong>Evidence:</strong> {e(f['evidence'])}</p>"
            f"<p><strong>How to resolve:</strong> {e(f['resolution'])}</p>"
            f"<p class=\"small muted\">Blocks merge: {'yes' if f.get('blocks_merge') else 'no (review after publish)'}</p>"
            "</div>"
        )
    return "\n".join(out)


def stats_block(n_rings, n_verified_prices, n_blank_prices, n_retailers, n_flags) -> str:
    return (
        '<div class="grid">'
        f'<div class="card"><div class="big">{n_rings}</div><h3>Rings tracked</h3>'
        '<p class="small muted">Each with an official source link + capture date.</p></div>'
        f'<div class="card"><div class="big">{n_verified_prices}</div><h3>Prices verified</h3>'
        f'<p class="small muted">{n_blank_prices} blank (unverified) — never inferred.</p></div>'
        f'<div class="card"><div class="big">{n_retailers}</div><h3>Retailers</h3>'
        '<p class="small muted">Official sites, contacts, return policies.</p></div>'
        f'<div class="card"><div class="big">{n_flags}</div><h3>Open flags</h3>'
        '<p class="small muted">Published for manual review; none block.</p></div>'
        "</div>"
    )


def verify_summary() -> str:
    if not LOG.exists():
        return '<div class="notice"><strong>No verification pass recorded yet.</strong> Run <code>scripts/verify.py</code>.</div>'
    log = json.loads(LOG.read_text(encoding="utf-8"))
    if not log:
        return '<div class="notice"><strong>No verification pass recorded yet.</strong></div>'
    last = log[-1]
    cls = "ok" if last["result"] == "PASS" else "banner"
    items = " · ".join(f"{k}: {v}" for k, v in last["passes"].items())
    fails = "".join(f"<li><code>{e(f)}</code></li>" for f in last.get("failures", []))
    return (
        f'<div class="{cls}"><p><strong>Latest published pass: {e(last["result"])}</strong> '
        f'(<code>{e(last["command"])}</code>; run timestamps live in <code>verification-log.json</code>, which is excluded from the reproducibility check)</p>'
        f"<p class=\"small\">{e(items)}</p>"
        + (f"<ul class=\"small\">{fails}</ul>" if fails else "")
        + "</div>"
    )


def replace_region(page: str, marker: str, content: str) -> None:
    """Idempotent region replacement. First build wraps content in
    <!-- BUILD:X --> ... <!-- /BUILD:X -->; later builds replace between them."""
    import re
    path = ROOT / page
    text = path.read_text(encoding="utf-8")
    open_tag = f"<!-- {marker} -->"
    close_tag = f"<!-- /{marker} -->"
    block = f"{open_tag}\n{content}\n{close_tag}"
    pattern = re.compile(re.escape(open_tag) + r".*?" + re.escape(close_tag), re.DOTALL)
    if pattern.search(text):
        text = pattern.sub(lambda _m: block, text, count=1)
    elif open_tag in text:
        text = text.replace(open_tag, block, 1)
    else:
        print(f"ERROR: marker {marker} not found in {page}")
        raise SystemExit(1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    rings = json.loads((DATA / "rings.json").read_text(encoding="utf-8"))["rings"]
    retailers = {r["id"]: r for r in
                 json.loads((DATA / "retailers.json").read_text(encoding="utf-8"))["retailers"]}
    flags = json.loads((DATA / "flags.json").read_text(encoding="utf-8"))["flags"]

    n_verified = sum(1 for r in rings if r.get("price_usd") is not None)
    n_blank = sum(1 for r in rings if r.get("price_usd") is None)

    replace_region("rings.html", "BUILD:RINGS_ROWS", ring_rows(rings, retailers))
    replace_region("retailers.html", "BUILD:RETAILERS_ROWS", retailer_rows(retailers))
    replace_region("flagged.html", "BUILD:FLAGS",
                   flag_cards(flags, {r["id"] for r in rings}, set(retailers)))
    replace_region("index.html", "BUILD:STATS",
                   stats_block(len(rings), n_verified, n_blank, len(retailers), len(flags)))
    replace_region("index.html", "BUILD:VERIFY_SUMMARY", verify_summary())
    print(f"Built: {len(rings)} rings, {len(retailers)} retailers, {len(flags)} flags → HTML.")
    print("Next: run scripts/verify.py --check-build to confirm data<->site sync + links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
