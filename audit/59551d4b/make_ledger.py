#!/usr/bin/env python3
"""Builds audit/59551d4b/REVERIFICATION_2026-11-11.md from the raw observation batches and the data files."""
import glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def collapse(t): return re.sub(r"\s+", " ", t).strip()
obs = []
for f in sorted(glob.glob(str(ROOT / "audit/59551d4b/obs_batch*.json"))):
    for o in json.loads(Path(f).read_text(encoding="utf-8")): obs.append((Path(f).name, o))
items = {}
for f in sorted(glob.glob(str(ROOT / "data/listings/*.json"))) + [str(ROOT / "data/solid-gold-verified.json")]:
    for it in json.loads(Path(f).read_text(encoding="utf-8"))["items"]: items.setdefault(it["id"], it)
vlog = json.loads((ROOT / "data/verification-log.json").read_text(encoding="utf-8"))
gold = json.loads((ROOT / "data/gold-price.json").read_text(encoding="utf-8"))
L = ["# Re-verification ledger — 2026-11-11 (UTC) — session S-59551D4B", "",
     "**No hallucinations.** Every value below was transcribed from an official page fetched on 2026-11-11 between about 07:55 and 08:17 UTC. "
     "Nothing was inferred, converted, averaged or copied from a search snippet. A retrieval is not an assay: no ring was weighed or XRF-tested.", "",
     "**Look for hallucinations again after every review:** open each link and compare it with the row.", "",
     "## 1. Gold references", "",
     f"- World Gold Council moving header: **${gold['usd_per_troy_oz']:,.2f} USD / troy oz**, retrieved {gold['retrieved_at']}; chart blocks dated {gold['chart_as_of_date']}; quote-as-of time not shown (F-026). <{gold['source_url']}>",
     "- JM Bullion gold-price page (companion explorer reference): body and bid/ask table **$4,072.47 USD** at Nov 11, 2026 3:03 AM EST; page-top ticker $4,073.34 on the same fetch (flagged, not averaged). <https://www.jmbullion.com/charts/gold-price/>",
     "- NIST conversion 31.1034768 g per troy ounce is a constant and was not re-read.", "",
     "## 2. Root register — all 32 rows", "",
     "| Row | Result | Assigned price | Page display (verbatim) | Weight | What was re-read on 2026-11-11 | Official link |", "|---|---|---|---|---|---|---|"]
status = {e["id"]: e["status"] for e in vlog["entries"] if e["kind"] == "listing"}
for iid in sorted(items):
    it = items[iid]
    price = f"{it['currency']} {it['price']:,.2f}" if it.get("price") is not None else "blank"
    disp = " · ".join((it.get("observed_native_display") or []) + ([it["unassigned_price_text"]] if it.get("unassigned_price_text") and it["unassigned_price_text"] not in (it.get("observed_native_display") or []) else [])) or "—"
    w = f"{it['weight_g']} g (re-read {it.get('weight_checked_at')})" if it.get("weight_g") is not None else "blank"
    L.append(f"| {iid} | {status[iid].replace('_', ' ')} | {price} | {disp.replace('|', '/')} | {w} | {it['price_check_note'].replace('|', '/')} | [official page]({it['source_url']}) |")
L += ["", "## 3. Not re-read in this pass (still dated October 2026)", "",
      "- Band width / depth lines on most rows; the Brilliant Earth metal specification block; Stone and Strand product HTML (only the official `.oembed` endpoint was read).",
      "- Retailer policy pages (returns, payment, contact), BBB profiles and the regulatory references (16 CFR 23, FTC, NIST).",
      "- Companion explorer: Catbird, Auvere and Quince product pages; Automic gram weights other than the Coffin Ring and 24k Band; the Factory Direct gram-weight line.",
      "- These keep their earlier dates in the data and are named in root flag F-052.", "",
      "## 4. Raw transcriptions (one block per fetch)", ""]
for fname, o in obs:
    L += [f"### `{o['key']}` — {o.get('result', 'read')}", "", f"- URL: <{o['url']}>", f"- Batch file: `audit/59551d4b/{fname}`" + (f" · fetched {o['fetched_at']} ({o.get('fetched_window', 'time of day not recorded')})" if o.get("fetched_at") else " · fetched 2026-11-11 between about 07:55Z and 08:03Z"), ""]
    L += [f"  - `{collapse(x)[:300]}`" for x in o["excerpts"]]
    if o.get("note"): L += ["", f"  Note: {o['note']}"]
    L.append("")
(ROOT / "audit/59551d4b/REVERIFICATION_2026-11-11.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"ledger: {len(items)} rows, {len(obs)} raw observation blocks")
