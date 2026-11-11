#!/usr/bin/env python3
"""S-59551D4B hallucination + security scan for the 2026-11-11 pass.

Question asked of every published price: "can it be found, digit for digit, in the raw text
transcribed from the official page on the pass date?"  The raw text is audit/59551d4b/obs_batch*.json.
The scan cannot prove an external claim true and cannot see pages that changed after the pass.

Usage: python3 audit/59551d4b/hallucination_scan.py [repo_root]   (exit 0 = PASS)
"""
import copy, glob, json, re, sys
from datetime import date
from pathlib import Path

PASS_DATE = "2026-11-11"
ROOT_PAGES = ["index.html", "solid-gold.html", "solitaire.html", "halo-pave.html", "three-stone-vintage.html", "18k.html",
              "budget.html", "retailers.html", "prices.html", "analysis.html", "verification.html", "methods.html", "flags.html"]
OFFICIAL = {"www.bluenile.com", "www.zales.com", "www.vrai.com", "www.brilliantearth.com", "www.automicgold.com", "mejuri.com",
            "www.sarraf.com", "www.factorydirectjewelry.com", "www.stoneandstrand.com", "www.gold.org", "www.costco.com"}

def collapse(t): return re.sub(r"\s+", " ", t).strip()
def numbers(text):
    """All numeric tokens of a text as floats (commas removed); also cents/100 for Shopify integer cents."""
    out = set()
    for tok in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        try: v = float(tok.replace(",", ""))
        except ValueError: continue
        out.add(round(v, 2))
        if "." not in tok and v >= 10000: out.add(round(v / 100, 2))
    return out
def okey(iid):
    if iid.startswith("BN-"): return "ext-bn-" + iid[3:]
    if iid.startswith("Z-"): return "ext-z-" + iid[2:]
    return {"BE-121H6": "ext-be-121h6", "VRAI-CLASSIC-4P": "ext-vrai-classic-4p", "AG-COFFIN-RING": "ag-coffin-ring", "AG-24K": "ag-24k",
            "AG-SAPPHIRE-RING": "ag-sapphire", "AG-CUSHION-SIGNET": "ag-cushion-signet", "MJ-BOLD-ETERNITY": "mj-bold-eternity",
            "FDJ-GR0001": "fdj-gr0001"}.get(iid, iid.lower())

def load_state(root):
    root = Path(root); J = lambda p: json.loads((root / p).read_text(encoding="utf-8"))
    items = {}
    for f in sorted(glob.glob(str(root / "data/listings/*.json"))) + [str(root / "data/solid-gold-verified.json")]:
        for it in json.loads(Path(f).read_text(encoding="utf-8"))["items"]: items.setdefault(it["id"], it)
    obs = {}
    for f in sorted(glob.glob(str(root / "audit/59551d4b/obs_batch*.json"))):
        for o in json.loads(Path(f).read_text(encoding="utf-8")): obs[o["key"]] = o
    return {"items": items, "obs": obs, "gold": J("data/gold-price.json"), "catalog": J("data/catalog.json"), "evidence": J("research/evidence.json"),
            "flags": J("data/flags.json"), "vlog": J("data/verification-log.json"), "dash_gold": J("dashboard/data/gold-reference.json"),
            "pages": {n: (root / n).read_text(encoding="utf-8") for n in ROOT_PAGES}}

def obs_text(st, *keys):
    return " ".join(collapse(x) for k in keys if k in st["obs"] for x in st["obs"][k]["excerpts"])
def row_keys(iid):
    k = okey(iid); return (k, k + "-html", k + "-html4", k + "-chunk0", k + "-tile")

def scan(st):
    F = []; stats = {}
    fail = lambda c, m: F.append(f"[{c}] {m}")
    items, gold = st["items"], st["gold"]
    # C1 every root row carries a price re-read date; every published weight a weight re-read date
    for iid, it in items.items():
        if it.get("price_checked_at") != PASS_DATE or not it.get("price_check_note"): fail("C1", f"{iid} lacks price re-read date/note for {PASS_DATE}")
        if it.get("weight_g") is not None and it.get("weight_checked_at") != PASS_DATE: fail("C1", f"{iid} weight not re-read on {PASS_DATE}")
    stats["rows"] = len(items)
    # C2 every published amount of a root row is found in the raw text of ITS OWN page on the pass date
    n = 0
    for iid, it in items.items():
        raw = obs_text(st, *row_keys(iid)); have = numbers(raw)
        if not raw: fail("C2", f"{iid} has no raw observation"); continue
        if it.get("price") is not None:
            n += 1
            if round(float(it["price"]), 2) not in have: fail("C2", f"{iid} assigned price {it['price']} not in raw observation")
        for text in (it.get("observed_native_display") or []) + ([it["unassigned_price_text"]] if it.get("unassigned_price_text") else []):
            n += 1
            for v in numbers(" ".join(re.findall(r"\$\d[\d,]*(?:\.\d+)?", text))):
                if v not in have: fail("C2", f"{iid} displayed amount {v} not in raw observation")
        if it.get("weight_g") is not None:
            n += 1
            if round(float(it["weight_g"]), 2) not in have: fail("C2", f"{iid} weight {it['weight_g']} g not in raw observation")
        if it.get("price") is None and it.get("currency") is not None: fail("C2", f"{iid} has a currency without a price")
    stats["root_values_traced"] = n
    # C3 gold references
    if round(gold["usd_per_troy_oz"], 2) not in numbers(obs_text(st, "gold-wgc")): fail("C3", "root gold value not in raw WGC observation")
    if gold["retrieved_at"] != PASS_DATE: fail("C3", "root gold value not dated to the pass")
    if gold.get("quote_date") is not None: fail("C3", "quote_date must stay null (F-026): the header shows no quote time")
    sup = [o["value"] for o in gold.get("superseded_observations", [])]
    if gold["usd_per_troy_oz"] in sup: fail("C3", "current gold value is also listed as superseded")
    for name, html in st["pages"].items():
        for v in sup:
            if f"{v:,.2f}" in html: fail("C3", f"{name} renders superseded gold value {v:,.2f}")
    if st["dash_gold"]["spot_usd_per_troy_oz"] != gold["usd_per_troy_oz"]: fail("C3", "dashboard gold reference differs from root")
    ref = st["catalog"]["meta"]["marketReference"]; src = {s["id"]: s for s in st["evidence"]["sources"]}
    if round(ref["amount"], 2) not in numbers(obs_text(st, "gold-jm")): fail("C3", "explorer market reference not in raw JM observation")
    if round(ref["amount"], 2) not in numbers(src["jm-gold"]["quotes"][ref["quote"]]): fail("C3", "explorer market reference not in its cited quote")
    if st["catalog"]["meta"]["benchmark"]["amount"] is not None: fail("C3", "no licensed benchmark was retrieved; must stay null")
    # C4 explorer priced products
    n = 0
    for p in st["catalog"]["products"]:
        if not p["price"]: continue
        n += 1
        if round(float(p["price"]["amount"]), 2) not in numbers(obs_text(st, p["id"], p["id"] + "-html", p["id"] + "-html4")):
            fail("C4", f"{p['id']} amount {p['price']['amount']} not in raw observation")
        if not p["price"]["observedAt"].startswith(PASS_DATE): fail("C4", f"{p['id']} price not dated to the pass")
        if not any(round(float(p["price"]["amount"]), 2) in numbers(src[e["source"]]["quotes"][e["quote"]]) for e in p["price"]["evidence"]):
            fail("C4", f"{p['id']} amount not in its cited quote")
    stats["explorer_prices_traced"] = n
    # C5 superseded / withdrawn displays are never rendered as the current display of their row
    for iid, it in items.items():
        cur = " ".join((it.get("observed_native_display") or []) + [it.get("unassigned_price_text") or ""])
        for old in it.get("superseded_displays") or []:
            if old["text"] in cur: fail("C5", f"{iid} still publishes superseded display {old['text']!r}")
            for name, html in st["pages"].items():
                m = re.search(r'<tr class="item-row" id="item-' + re.escape(iid.lower()) + r'".*?</tr>', html, re.S)
                if m and old["text"] in m.group(0).replace("&#x27;", "'"): fail("C5", f"{name} row {iid} renders superseded display")
    # C6 flags: bidirectional, official https sources, rendered
    byf = {f["id"]: f for f in st["flags"]["flags"]}
    for fid in ("F-046", "F-047", "F-048", "F-049", "F-050", "F-051", "F-052", "F-053"):
        if fid not in byf: fail("C6", f"{fid} missing"); continue
        f = byf[fid]
        for u in f["sources"]:
            m = re.match(r"https://([^/]+)/", u)
            if not m or m.group(1) not in OFFICIAL: fail("C6", f"{fid} source is not an official https URL: {u}")
        for iid in f["affected_items"]:
            if fid not in items[iid]["flags"]: fail("C6", f"{fid} lists {iid} but the row does not carry it")
        if f'id="{fid.lower()}"' not in st["pages"]["flags.html"]: fail("C6", f"{fid} not rendered on flags.html")
    for iid, it in items.items():
        for fid in it["flags"]:
            if fid not in byf or iid not in byf[fid]["affected_items"]: fail("C6", f"{iid} carries {fid} but the flag does not list it")
    # C7 front page + tables
    idx = st["pages"]["index.html"]
    for needle in ("NO HALLUCINATIONS", "do not invent, estimate, or extrapolate", f"re-read from the official pages on {PASS_DATE}",
                   f"${gold['usd_per_troy_oz']:,.2f}", "Look for hallucinations again after every review", "flags.html#f-052"):
        if needle not in idx: fail("C7", f"index.html lacks {needle!r}")
    rows = 0
    for name, html in st["pages"].items():
        for m in re.finditer(r'<tr class="item-row" id="item-([a-z0-9-]+)" data-item-id="([^"]+)" data-source-url="([^"]+)".*?</tr>', html, re.S):
            rows += 1; iid, url, row = m.group(2), m.group(3), m.group(0)
            if iid not in items or url != items[iid]["source_url"] or f'href="{url}"' not in row: fail("C7", f"{name} row {iid} lacks its official link")
            if f"price re-read {PASS_DATE}" not in row: fail("C7", f"{name} row {iid} lacks its price re-read date")
    stats["table_rows_checked"] = rows
    if rows < len(items): fail("C7", "fewer rendered rows than register rows")
    # C8 security of generated root pages
    for name, html in st["pages"].items():
        if "Content-Security-Policy" not in html: fail("C8", f"{name} lacks a CSP")
        if re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html): fail("C8", f"{name} has an inline script")
        if re.search(r"\son[a-z]+\s*=", html) or "javascript:" in html.lower(): fail("C8", f"{name} has an inline handler / javascript: URL")
        if re.search(r'(?:href|src)="http://', html): fail("C8", f"{name} links over plain http")
        if re.search(r"ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY", html): fail("C8", f"{name} contains a credential pattern")
    # C9 no future dates
    today = date.fromisoformat(PASS_DATE)
    def walk(node, where):
        if isinstance(node, dict):
            for k, v in node.items(): walk(v, f"{where}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node): walk(v, where)
        elif isinstance(node, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}(T[\d:.]+Z)?", node):
            if date.fromisoformat(node[:10]) > today: fail("C9", f"future date {node} at {where}")
    for k in ("items", "gold", "catalog", "evidence", "flags", "vlog"): walk(st[k], k)
    # C10 verification log: every listing re-dated, every observed excerpt found in the raw text
    allraw = " ".join(collapse(x) for o in st["obs"].values() for x in o["excerpts"])
    seen = set()
    for e in st["vlog"]["entries"]:
        if e["kind"] == "listing":
            seen.add(e["id"])
            if e["checked_at"] != PASS_DATE: fail("C10", f"log entry {e['id']} not dated to the pass")
        if e["checked_at"] == PASS_DATE:
            for q in e.get("observed") or []:
                if collapse(q) not in allraw: fail("C10", f"log entry {e['id']} quotes text absent from the raw observations: {q[:40]!r}")
        if e["status"] == "not_re_read" and e["checked_at"] == PASS_DATE: fail("C10", f"{e['id']} is not_re_read but dated to the pass")
    if seen != set(items): fail("C10", "verification log does not cover exactly the register rows")
    return F, stats

MUTATIONS = {
    "M01 assigned price +1": lambda s: s["items"]["SAR-147370"].__setitem__("price", s["items"]["SAR-147370"]["price"] + 1),
    "M02 invented Blue Nile amount": lambda s: s["items"]["BN-194158"].__setitem__("observed_native_display", ["$1,125$899(Setting Price)"]),
    "M03 superseded gold restored": lambda s: s["gold"].__setitem__("usd_per_troy_oz", 3995.47),
    "M04 quote_date invented": lambda s: s["gold"].__setitem__("quote_date", "2026-11-10"),
    "M05 explorer Menē amount reverted": lambda s: [p["price"].__setitem__("amount", 1325) for p in s["catalog"]["products"] if p["id"] == "mene-rose"],
    "M06 price re-read date removed": lambda s: s["items"]["AG-24K"].pop("price_checked_at"),
    "M07 future date": lambda s: s["items"]["Z-19957449"].__setitem__("price_checked_at", "2026-12-01"),
    "M08 withdrawn display restored": lambda s: s["items"]["BN-315661"].__setitem__("observed_native_display", ["$2,210(Setting Price)"]),
    "M09 banner removed": lambda s: s["pages"].__setitem__("index.html", s["pages"]["index.html"].replace("NO HALLUCINATIONS", "")),
    "M10 inline script injected": lambda s: s["pages"].__setitem__("flags.html", s["pages"]["flags.html"] + "<script>alert(1)</script>"),
    "M11 log excerpt altered": lambda s: [e["observed"].__setitem__(0, "US$1.00 invented") for e in s["vlog"]["entries"] if e["id"] == "SAR-144773"],
    "M12 weight changed": lambda s: s["items"]["VRAI-CLASSIC-4P"].__setitem__("weight_g", 3.86),
    "M13 market reference changed": lambda s: s["catalog"]["meta"]["marketReference"].__setitem__("amount", 4100.0),
    "M14 flag link broken": lambda s: s["items"]["SS-RITA"].__setitem__("flags", [f for f in s["items"]["SS-RITA"]["flags"] if f != "F-050"]),
    "M15 official link stripped from a row": lambda s: s["pages"].__setitem__("budget.html", s["pages"]["budget.html"].replace('href="https://www.zales.com/15-ct', 'href="https://example.invalid/15-ct')),
    "M16 currency without price": lambda s: s["items"]["SS-CLARA"].__setitem__("currency", "USD"),
}

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    st = load_state(root)
    failures, stats = scan(st)
    caught = 0; missed = []
    for name, mutate in MUTATIONS.items():
        m = copy.deepcopy(st); mutate(m)
        f, _ = scan(m)
        if len(f) > len(failures): caught += 1
        else: missed.append(name)
    print(f"S-59551D4B scan ({PASS_DATE}): {len(failures)} failure(s); mutation controls caught {caught}/{len(MUTATIONS)}")
    print("  " + "; ".join(f"{k}={v}" for k, v in stats.items()))
    for f in failures: print("  FAIL " + f)
    for m in missed: print("  MISSED MUTATION " + m)
    ok = not failures and not missed
    print("RESULT: " + ("PASS" if ok else "FAIL") + " — a pass means the published values match the raw transcriptions; it does not certify that a seller's claim is true.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
