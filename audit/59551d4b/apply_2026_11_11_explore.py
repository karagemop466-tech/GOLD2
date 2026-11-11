#!/usr/bin/env python3
"""S-59551D4B — apply the 2026-11-11 re-read to the companion explorer (data/catalog.json,
research/evidence.json, data/review.json). Same rules and guards as apply_2026_11_11.py."""
import glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = "2026-11-11"; SESSION = "S-59551D4B"
def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def collapse(t): return re.sub(r"\s+", " ", t).strip()
OBS = {}
for f in sorted(glob.glob(str(ROOT / "audit/59551d4b/obs_batch*.json"))):
    for o in json.loads(Path(f).read_text(encoding="utf-8")): OBS[o["key"]] = o
def has(key, needle): return any(needle in collapse(x) for x in OBS[key]["excerpts"])

cat_text = (ROOT / "data/catalog.json").read_text(encoding="utf-8")
ev_text = (ROOT / "research/evidence.json").read_text(encoding="utf-8")
def indent_of(text):
    m = re.search(r"\n( +)\"", text); return len(m.group(1)) if m else None
c = json.loads(cat_text); e = json.loads(ev_text); rv = load("data/review.json")
S = {s["id"]: s for s in e["sources"]}; P = {p["id"]: p for p in c["products"]}
assert len(P) == 46 and len(S) == 88 and len(rv["findings"]) == 29
METHOD = f"; re-read {D} by session {SESSION} (short excerpts; date-level precision)"
def recheck(sid, note=None):
    s = S[sid]; s["lastRecheckedAt"] = D
    if METHOD not in s["method"]: s["method"] += METHOD
    if note: s["note"] = (s.get("note") or "").rstrip() + " " + note
    return s

# 1. market reference (JM Bullion) ------------------------------------------------
ref = c["meta"]["marketReference"]
assert ref["amount"] == 4009.38 and S["jm-gold"]["quotes"]["quote"] == "$4,009.38 USD"
assert has("gold-jm", "$4,072.47 USD") and has("gold-jm", "Bid: $4,057.97 Ask: $4,072.47") and has("gold-jm", "$4,073.34")
j = S["jm-gold"]
j["quotes"].update({"quote": "$4,072.47 USD", "ask": "Bid: $4,057.97   Ask: $4,072.47", "header-value": "$4,073.34",
                    "as-of": "As of Nov 11, 2026 at 3:03 AM EST, the live Gold spot price for 1 ounce of Gold in U.S. dollars (USD) is $4,072.47"})
j["observedAt"] = D; j["lastRecheckedAt"] = D
j["method"] = f"fetch_page; short excerpts transcribed and rechecked {D} by session {SESSION}"
j["note"] = ("Dealer page timestamped Nov 11, 2026 at 3:03 AM EST (08:03Z) displayed '$4,072.47 USD' in the body with 'Bid: $4,057.97 Ask: $4,072.47'. "
             "The page-top ticker on the same fetch read 'Gold Ask $4,073.34'; the body quote, which carries the explicit 'As of' sentence, is recorded and the two are not averaged. "
             "Supersedes the 2026-10-23 19:46 EDT observation (kept as dated history in data/review.json). This is a dealer reference, not an LBMA benchmark or live feed.")
ref.update({"amount": 4072.47, "publishedAt": "2026-11-11T08:03:00Z", "observedAt": D,
            "caveat": "Dated dealer reference, not LBMA and not a live feed. The page's own timestamp is Nov 11, 2026 at 3:03 AM EST. Calculations are conditional illustrations only."})

# 2. WGC context source -------------------------------------------------------------
w = S["wgc-panel-review"]; assert w["quotes"]["quote"] == "3,995.47" and has("gold-wgc", "4,059.49")
w["quotes"].update({"header": "Gold Spot price USD /oz - 4,059.49", "chart-as-of": "Data as of 10 November, 2026", "quote": "4,059.49"})
w["observedAt"] = D; w["lastRecheckedAt"] = D
w["method"] += METHOD
w["note"] = ("Moving header read 4,059.49 USD/oz on the 2026-11-11 re-read by session S-59551D4B; the page's data blocks were dated 10 November, 2026. "
             "Earlier readings are retained only inside data/gold-price.json as superseded observations and are not rendered as current values anywhere. "
             "The header carries no quote-as-of timestamp, so chart metadata is stored separately and not bound to the header.")

# 3. Menē ---------------------------------------------------------------------------
for pid, old, new in (("mene-rose", 1325, 1337), ("mene-knot", 1442, 1455)):
    s = S[pid]; p = P[pid]
    assert p["price"]["amount"] == old and s["quotes"]["price"] == f"${old:,}" and has(pid, f"${new:,} USD"), pid
    prev_obs = s["observedAt"]
    s["quotes"]["price"] = f"${new:,}"
    s["quotes"]["previous-price"] = f"${old:,} USD — direct official-page observation at {prev_obs}; superseded on {D}."
    s["supersededDisplay"] = {"amount": old, "currency": "USD", "observedAt": prev_obs,
        "reason": "Earlier observation of the same official page. The page is repriced from metal value, so only the later observation is current; the earlier amount is kept as dated history and is never averaged with the new one."}
    s["observedAt"] = D; s["lastRecheckedAt"] = D
    s["method"] = f"fetch_page; short excerpts transcribed and checked {D} by session {SESSION}"
    s["note"] = (f"Direct official-product fetch on {D} rendered ${new:,} USD on the page's default size display; the {prev_obs[:10]} observation was ${old:,}. "
                 "Menē prices these Crafted-on-Demand pieces from metal value, so the earlier amount is superseded, not additive. Sizes are sold by weight; no gram weight is published for this piece.")
    p["price"]["amount"] = new; p["price"]["observedAt"] = D; p["observedAt"] = D

# 4. priced products whose amount was re-read unchanged --------------------------------
UNCHANGED = {"ag-natural": 726, "ag-cluster": 2862, "ag-petal": 1774, "ag-ruby": 526, "ag-sapphire": 526, "ag-moissanite": 420, "ag-24k": 3520,
             "ag-coffin-ring": 1910, "ag-cushion-signet": 2758, "ext-be-121h6": 890, "sar-147370": 3004, "sar-145362": 2661, "sar-145364": 2858,
             "sar-144773": 1362, "sar-151362": 8203, "sar-147371": 4049, "fdj-gr0001": 1299.99}
for pid, amt in UNCHANGED.items():
    p = P[pid]; assert p["price"]["amount"] == amt, pid
    assert pid in OBS, pid
    p["price"]["observedAt"] = D
    recheck(pid, f"Price re-read {D} ({SESSION}): unchanged.")
recheck("automic-currency", f"Re-read {D} ({SESSION}): unchanged.")
assert sum(1 for p in c["products"] if p["price"]) == 19

# 5. unpriced rows whose display changed -----------------------------------------------
BN = {"194158": ("$1,125(Setting Price)", "$1,125$900(Setting Price)"), "195269": ("$1,155(Setting Price)", "$1,155$924(Setting Price)"),
      "192506": ("$1,255(Setting Price)", "$1,255$1,004(Setting Price)"), "203348": ("$1,145(Setting Price)", "$1,145$916(Setting Price)"),
      "195639": ("$1,000(Setting Price)", "$1,000$800(Setting Price)"), "194548": ("$1,045(Setting Price)", "$1,045$836(Setting Price)"),
      "193625": ("$1,950(Setting Price)", "$1,950$1,560(Setting Price)"), "316238": ("$1,240(Setting Price)", "$1,240$992(Setting Price)")}
for n, (old, new) in BN.items():
    s = S["ext-bn-" + n]; assert has("ext-bn-" + n, new)
    k = 0
    for key in ("display", "price"):
        if s["quotes"].get(key) == old: s["quotes"][key] = new; k += 1
    assert k >= 1, n
    s["quotes"]["promotion"] = "-20% — *Discount code is applied automatically"
    s["quotes"]["previous-display"] = f"{old} — observed {s['observedAt'][:10]}; superseded on {D}."
    recheck("ext-bn-" + n, f"Re-read {D} ({SESSION}): the page shows a struck list amount and a 20%-off promotional amount; neither is assigned (no ISO currency).")
s = S["ext-bn-315661"]; assert s["quotes"]["display"] == "$2,210(Setting Price)" and has("ext-bn-315661", "This popular style is sold out")
s["quotes"]["previous-display"] = f"$2,210(Setting Price) — observed {s['observedAt'][:10]}; withdrawn on {D} because the page no longer renders it."
s["quotes"]["display"] = "This popular style is sold out"; s["quotes"].pop("price")
recheck("ext-bn-315661", f"Re-read {D} ({SESSION}): the page reads 'This popular style is sold out' and renders no setting price, stock number, metal or width block for this item.")
Z = {"20046552": ("Discounted Price $909.30", "Discounted Price $1,299.00"), "20303279": ("Discounted Price $979.30", "Discounted Price $1,399.00"),
     "20301172": ("Discounted Price $769.30", "Discounted Price $1,099.00")}
for n, (old, new) in Z.items():
    s = S["ext-z-" + n]; assert s["quotes"]["display"] == old and has("ext-z-" + n, new), n
    s["quotes"]["display"] = new
    s["quotes"]["previous-display"] = f"{old} — observed {s['observedAt'][:10]}; superseded on {D}."
    s["quotes"]["bag-promotion"] = "Flash Sale: Save $75-$750 off your purchase starting at $250 or more - Discount Applied in Bag."
    recheck("ext-z-" + n, f"Re-read {D} ({SESSION}): single 'Discounted Price' amount; the earlier promotional amount is no longer rendered. No ISO currency; unassigned.")
recheck("ext-z-19957449", f"Re-read {D} ({SESSION}): 'Discounted Price $899.00' unchanged.")
recheck("ext-vrai-classic-4p", f"Re-read {D} ({SESSION}): 'Metal weight:2.86g (Ring size 6)' unchanged; no price rendered for this setting.")
recheck("mj-bold-eternity", f"Re-read {D} ({SESSION}): 'From$2,900' unchanged; page now also states a holiday return window (orders Nov 1 – Dec 31, 2026 returnable through Jan 31, 2027).")
S["ss-clara"]["quotes"]["offers-2026-11-11"] = "Official .oembed endpoint, currency USD: size 5 — 2200.0; size 6 — 2200.0; size 7 — 2000.0; all in stock."
S["ss-rita"]["quotes"]["offers-2026-11-11"] = "Official .oembed endpoint, currency USD: 780.0; every listed size in_stock false; description: Final sale and non-returnable."
S["ss-mia"]["quotes"]["offers-2026-11-11"] = "Official .oembed endpoint, currency USD: 925.0; every listed size in_stock false; description: Final sale and non-returnable."
for sid in ("ss-clara", "ss-rita", "ss-mia"):
    recheck(sid, f"Product .oembed endpoint re-read {D} ({SESSION}); product HTML not re-read. No price is assigned.")

# 6. meta -------------------------------------------------------------------------------
m = c["meta"]
m["reviewedAt"] = "2026-11-11T08:40:00Z"
m["reviewSession"] += f"; {SESSION} staleness review and live price re-read on {D} (19 priced rows, market reference, Blue Nile/Zales/Stone and Strand displays)"
m["scope"] = ("46 unique named product pages across 13 retailers. First captured 2026-10-22/23 UTC; on 2026-11-11 UTC the 19 priced rows, the market reference and the "
              "Blue Nile, Zales, VRAI, Mejuri and Stone and Strand rows were re-read. Rows not re-read keep their October dates and are labelled stale by the freshness rule.")
m["observationWindow"]["end"] = "2026-11-11T08:40:00Z"

# 7. review findings ------------------------------------------------------------------------
F = {f["id"]: f for f in rv["findings"]}
HIST = f"[Historical record — superseded by the {D} re-read; see finding reverification-{D}.] "
for fid in ("mene-final-price", "inherited-quote-date", "reobservation-2026-10-23", "jm-reference-reobservation-2026-10-23-evening"):
    assert fid in F, fid
    if not F[fid]["finding"].startswith("[Historical"): F[fid]["finding"] = HIST + F[fid]["finding"]
bn_ids = ["ext-bn-" + n for n in BN]
rv["findings"] += [
 {"id": f"reverification-{D}", "title": f"Staleness review and live re-read on {D}",
  "scope": "all 19 priced rows; market reference; World Gold Council context",
  "finding": "Every stored observation was 19 days old. On 2026-11-11 session S-59551D4B re-read the 19 priced rows at the official seller pages or their official product endpoints: 17 amounts were unchanged; Menē Rose Ring now displays $1,337 USD and Knot Ring $1,455 USD (earlier amounts kept as dated history). The JM Bullion page (own timestamp Nov 11, 2026 at 3:03 AM EST) displayed $4,072.47 USD with Bid $4,057.97 / Ask $4,072.47, and the World Gold Council moving header read 4,059.49 USD/oz with chart blocks dated 10 November 2026. Rows not re-read keep their October dates.",
  "action": "Treat every amount as a dated observation. Re-open the official page before acting; look for hallucinations again after every review.",
  "sources": ["jm-gold", "wgc-panel-review", "mene-rose", "mene-knot"] + sorted(UNCHANGED)},
 {"id": f"jm-ticker-vs-body-{D}", "title": "JM Bullion page shows two different gold numbers on one fetch",
  "scope": "market reference", "finding": "On the 2026-11-11 fetch the page body and the bid/ask table read $4,072.47 while the page-top ticker read 'Gold Ask $4,073.34'. The body quote, which carries the explicit 'As of Nov 11, 2026 at 3:03 AM EST' sentence, is the recorded reference; the ticker value is stored as header-value only. The two are not averaged or reconciled.",
  "action": "Use the reference only as a dated illustration; enter your own current quote in the calculator when it matters.", "sources": ["jm-gold"]},
 {"id": f"bluenile-promotion-{D}", "title": "Blue Nile settings show a struck amount and a 20%-off amount",
  "scope": "Blue Nile setting rows", "finding": "On 2026-11-11 the re-read Blue Nile setting pages rendered a struck list amount directly followed by a lower amount with '-20%' and '*Discount code is applied automatically' (for example '$1,125$900(Setting Price)'). Neither amount is assigned: no ISO currency is printed and the promotion terms were not retrieved. The ext-bn-316238 URL still serves a differently named product.",
  "action": "Confirm the cart total, currency and promotion end date on the official page.", "sources": sorted(bn_ids)},
 {"id": f"bluenile-315661-sold-out-{D}", "title": "Blue Nile item 315661 is shown as sold out",
  "scope": "ext-bn-315661", "finding": "On 2026-11-11 the official page rendered 'This popular style is sold out' and no setting price for this item; the earlier displayed amount was withdrawn from the current record and kept only as dated history.",
  "action": "Do not plan a purchase around this row.", "sources": ["ext-bn-315661"]},
 {"id": f"zales-display-change-{D}", "title": "Zales displays changed; two pages print a different item number",
  "scope": "Zales rows", "finding": "On 2026-11-11 three Zales pages rendered a single 'Discounted Price' ($1,299.00, $1,399.00, $1,099.00); the lower promotional amounts stored in October are no longer rendered. A bag-level flash-sale banner is shown and was not converted into a price. The V-20303279 page prints 'Item #: 20615545' and the V-20301172 page prints 'Item #: 20301161'. No ISO currency is printed; all amounts stay unassigned.",
  "action": "Confirm item number, bag total and currency in the cart.", "sources": ["ext-z-20046552", "ext-z-20303279", "ext-z-20301172", "ext-z-19957449"]},
 {"id": f"stone-strand-stock-and-size-{D}", "title": "Stone and Strand: Clara amount depends on size; Rita and Mia out of stock and final sale",
  "scope": "ss-clara; ss-rita; ss-mia", "finding": "On 2026-11-11 the official .oembed endpoints reported, in USD: Clara 2200.0 for sizes 5 and 6 and 2000.0 for size 7; Rita 780.0 and Mia 925.0 with every listed size out of stock and a 'Final sale and non-returnable' description. No price is assigned to these rows.",
  "action": "Select the size on the official page; do not buy a final-sale ring that cannot be returned after an independent test.", "sources": ["ss-clara", "ss-rita", "ss-mia"]},
 {"id": f"fdj-placeholder-{D}", "title": "Factory Direct Jewelry page shows a $0.00 Black Friday placeholder block",
  "scope": "fdj-gr0001", "finding": "On 2026-11-11 the GR0001 page still rendered the $1,299.99 sale price and also a 'Black Friday Sale' block whose amounts were all $0.00. A placeholder is not a price; nothing was recorded from it. The gram-weight line stored in October was not re-read in this pass.",
  "action": "Confirm the payable amount in the cart on the day of purchase.", "sources": ["fdj-gr0001"]},
]
assert len({f["id"] for f in rv["findings"]}) == len(rv["findings"]) == 36

(ROOT / "data/catalog.json").write_text(json.dumps(c, indent=indent_of(cat_text), ensure_ascii=("\\u" in cat_text)) + "\n", encoding="utf-8")
(ROOT / "research/evidence.json").write_text(json.dumps(e, indent=indent_of(ev_text), ensure_ascii=("\\u" in ev_text)) + "\n", encoding="utf-8")
rv_text = (ROOT / "data/review.json").read_text(encoding="utf-8")
(ROOT / "data/review.json").write_text(json.dumps(rv, indent=indent_of(rv_text), ensure_ascii=("\\u" in rv_text)) + "\n", encoding="utf-8")
print("explore data updated: 19 price dates, 2 Menē amounts, JM 4,072.47, WGC 4,059.49, 12 display changes, 7 findings")
