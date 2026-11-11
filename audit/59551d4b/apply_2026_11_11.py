#!/usr/bin/env python3
"""S-59551D4B — apply the 2026-11-11 live re-verification to the data files.

Inputs : audit/59551d4b/obs_batch*.json (raw excerpts transcribed from pages fetched 2026-11-11 UTC).
Rule   : NO HALLUCINATIONS. A value is written only if it appears in an excerpt of a page fetched in
         this pass. Anything not re-read keeps its older date. Old values are kept as dated history.
Guards : every edit asserts the value it expects to replace, so the script fails loudly instead of
         overwriting peer work. It is NOT idempotent by design; run once on main@9819787 + claim.
"""
import glob, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = "2026-11-11"
SESSION = "S-59551D4B"
changes = []

def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def save(p, obj, indent=2):
    (ROOT / p).write_text(json.dumps(obj, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
def collapse(t): return re.sub(r"\s+", " ", t).strip()

OBS = {}
for f in sorted(glob.glob(str(ROOT / "audit/59551d4b/obs_batch*.json"))):
    for o in json.loads(Path(f).read_text(encoding="utf-8")):
        OBS[o["key"]] = o
def ex(key, n=7):
    return [collapse(x) for x in OBS[key]["excerpts"]][:n]
def has(key, needle):
    return any(needle in collapse(x) for x in OBS[key]["excerpts"])

# ───────────────────────── A. gold reference (root) ─────────────────────────
g = load("data/gold-price.json")
assert g["usd_per_troy_oz"] == 3995.47 and g["retrieved_at"] == "2026-10-23", g["usd_per_troy_oz"]
assert has("gold-wgc", "4,059.49") and has("gold-wgc", "Data as of 10 November, 2026")
g["superseded_observations"].insert(0, {
    "value": 3995.47, "currency": "USD", "quote_date": None, "retrieved_at": "2026-10-23",
    "chart_as_of_date": "2026-10-22", "status": "superseded_moving_header",
    "reason": "Moving-header observation from 2026-10-23T23:41Z. Superseded by the 2026-11-11 re-read of the same page; kept as dated history only and never used in calculations.",
})
g["usd_per_troy_oz"] = 4059.49
g["retrieved_at"] = D
g["evidence_quotes"] = ["4,059.49", "Data as of 10 November, 2026"]
g["chart_as_of_date"] = "2026-11-10"
g["field_evidence"]["usd_per_troy_oz"] = ["USD\n\n/oz\n\n-\n\n4,059.49"]
g["field_evidence"]["chart_as_of_date"] = ["Data as of 10 November, 2026"]
g["quote_scope"] = ("Moving-header observation retrieved 2026-11-11T07:55Z; exact quote-as-of timestamp is unconfirmed (F-026). "
                    "The chart's stated date (10 November 2026) is stored separately and is not assigned to the header.")
save("data/gold-price.json", g); changes.append("data/gold-price.json: WGC header 4,059.49 (2026-11-11); previous value moved to superseded_observations")

p = ROOT / "evidence/gold-price.md"; t = p.read_text(encoding="utf-8")
old_cur = "**Retrieved:** 2026-10-23T23:41Z (UTC). This is the latest direct fetch of the same page on that day; every earlier reading of the moving header is kept only in the dated history table below."
assert old_cur in t and "- **Current observation retrieved:** 2026-10-23 (UTC), direct page fetch." in t
t = t.replace("- **Current observation retrieved:** 2026-10-23 (UTC), direct page fetch.", f"- **Current observation retrieved:** {D} (UTC), direct page fetch by {SESSION}.")
t = t.replace(old_cur, "**Retrieved:** 2026-11-11T07:55Z (UTC) by S-59551D4B. Every earlier reading of the moving header is kept only in the dated history table below.")
assert t.count("```\nUSD\n\n/oz\n\n-\n\n3,995.47\nLast Updated\n```") == 1
t = t.replace("```\nUSD\n\n/oz\n\n-\n\n3,995.47\nLast Updated\n```", "```\nUSD\n\n/oz\n\n-\n\n4,059.49\nLast Updated\n```")
assert t.count("```\nData as of 22 October, 2026\n```") == 1
t = t.replace("```\nData as of 22 October, 2026\n```", "```\nData as of 10 November, 2026\n```")
hdr = "| --- | --- | --- | --- | --- |\n"
assert t.count(hdr) == 1
t = t.replace(hdr, hdr + "| 3,995.47 | 2026-10-23T23:41Z | 2026-10-22 | `superseded_moving_header` | Previous current value. Superseded by the 2026-11-11T07:55Z re-read (4,059.49, chart date 10 November 2026). |\n")
p.write_text(t, encoding="utf-8"); changes.append("evidence/gold-price.md: current block + history row")

# ───────────────────────── B. root listings ─────────────────────────
BN_NEW = {  # id -> (old display, new display, obs key)
    "BN-194158": ("$1,125(Setting Price)", "$1,125$900(Setting Price)"),
    "BN-195269": ("$1,155(Setting Price)", "$1,155$924(Setting Price)"),
    "BN-192506": ("$1,255(Setting Price)", "$1,255$1,004(Setting Price)"),
    "BN-195402": ("$1,300(Setting Price)", "$1,300$1,040(Setting Price)"),
    "BN-302868": ("$1,050(Setting Price)", "$1,050$840(Setting Price)"),
    "BN-316238": ("$1,240(Setting Price)", "$1,240$992(Setting Price)"),
    "BN-203348": ("$1,145(Setting Price)", "$1,145$916(Setting Price)"),
    "BN-195639": ("$1,000(Setting Price)", "$1,000$800(Setting Price)"),
    "BN-194548": ("$1,045(Setting Price)", "$1,045$836(Setting Price)"),
    "BN-193625": ("$1,950(Setting Price)", "$1,950$1,560(Setting Price)"),
}
Z_NEW = {
    "Z-20046552": ("$909.30  $1,299.00 30% Off", "Discounted Price $1,299.00"),
    "Z-20303279": ("Discounted Price $979.30  Original Price was $1,399.00 30% Off", "Discounted Price $1,399.00"),
    "Z-20301172": ("Discounted Price $769.30  Original Price was $1,099.00 30% Off", "Discounted Price $1,099.00"),
}
def okey(iid):
    if iid.startswith("BN-"): return "ext-bn-" + iid[3:]
    if iid.startswith("Z-"): return "ext-z-" + iid[2:]
    return {"BE-121H6": "ext-be-121h6", "VRAI-CLASSIC-4P": "ext-vrai-classic-4p", "AG-COFFIN-RING": "ag-coffin-ring",
            "AG-24K": "ag-24k", "AG-SAPPHIRE-RING": "ag-sapphire", "AG-CUSHION-SIGNET": "ag-cushion-signet",
            "MJ-BOLD-ETERNITY": "mj-bold-eternity", "FDJ-GR0001": "fdj-gr0001"}.get(iid, iid.lower())

# scope sentence for the per-row "price re-read" line (what was actually re-read on 2026-11-11)
SCOPE = {
    "BE-121H6": "Official product page: “$890” setting price beside the USD selector re-read; unchanged. Metal specification block not re-read this pass.",
    "AG-COFFIN-RING": "Official product page: default display “$1,910” and “Approximately 6.1g (gold)” re-read; unchanged.",
    "AG-24K": "Official product page and product JSON: price and “Approximate item weight: 11g” re-read; unchanged.",
    "AG-SAPPHIRE-RING": "Official product .oembed endpoint: price re-read; unchanged. Dimension lines not re-read this pass.",
    "AG-CUSHION-SIGNET": "Official product .oembed endpoint: price re-read; unchanged. Dimension lines not re-read this pass.",
    "FDJ-GR0001": "Official product page: “SALE $1,299.99” re-read; unchanged. A new Black Friday block shows only $0.00 placeholders (F-051).",
    "VRAI-CLASSIC-4P": "Official configurator page: “Metal weight:2.86g (Ring size 6)” re-read; unchanged. The page still renders no price for this setting.",
    "MJ-BOLD-ETERNITY": "Official product page: “From$2,900” re-read; unchanged, still no ISO currency. Holiday return window newly stated (F-053).",
    "SS-CLARA": "Official product .oembed endpoint: offers 2200.0 USD (sizes 5 and 6) and 2000.0 USD (size 7). Amount depends on size, so the price stays unassigned (F-049). Product HTML not re-read.",
    "SS-RITA": "Official product .oembed endpoint: 780.0 USD, every size out of stock, final sale (F-050). Product HTML not re-read.",
    "SS-MIA": "Official product .oembed endpoint: 925.0 USD, every size out of stock, final sale (F-050). Product HTML not re-read.",
    "Z-19957449": "Official product page: “Discounted Price $899.00” re-read; unchanged, still no ISO currency.",
    "BN-315661": "Official product page now reads “This popular style is sold out” and renders no setting price for this item (F-047). The earlier display is withdrawn.",
}
for i in ("SAR-147370", "SAR-145362", "SAR-145364", "SAR-144773", "SAR-151362", "SAR-147371"):
    SCOPE[i] = "Official product page: US$ price and approximate metal weight re-read; unchanged."
for i, (o, n) in BN_NEW.items():
    SCOPE[i] = f"Official product page: display changed to “{n}” with “-20%” (site promotion, F-046); the earlier single-amount display is kept only as dated history. No ISO currency; price stays unassigned."
SCOPE["BN-316238"] += " The URL still serves a differently named product (F-041)."
for i, (o, n) in Z_NEW.items():
    SCOPE[i] = f"Official product page: display changed to “{n}”; the earlier promotional amount is no longer rendered (F-048). No ISO currency; price stays unassigned."

WEIGHT_REREAD = {"AG-COFFIN-RING": ("ag-coffin-ring-html4", "6.1g"), "AG-24K": ("ag-24k", "11g"), "VRAI-CLASSIC-4P": ("ext-vrai-classic-4p", "2.86g"),
                 "SAR-147370": ("sar-147370", "3.80"), "SAR-145362": ("sar-145362", "10.0"), "SAR-145364": ("sar-145364", "8.0"),
                 "SAR-144773": ("sar-144773", "13.4"), "SAR-151362": ("sar-151362", "9.2"), "SAR-147371": ("sar-147371", "7.7")}
NEWFLAGS = {
    "F-046": list(BN_NEW), "F-047": ["BN-315661"], "F-048": list(Z_NEW), "F-049": ["SS-CLARA"],
    "F-050": ["SS-RITA", "SS-MIA"], "F-051": ["FDJ-GR0001"], "F-053": ["MJ-BOLD-ETERNITY"],
}
EVID_APPEND = {}   # evidence file -> list of verbatim strings to append
seen_rows = {}
files = sorted(glob.glob(str(ROOT / "data/listings/*.json"))) + [str(ROOT / "data/solid-gold-verified.json")]
for f in files:
    rel = str(Path(f).relative_to(ROOT)); payload = load(rel)
    for it in payload["items"]:
        iid = it["id"]; k = okey(iid)
        assert k in OBS, (iid, k)
        assert iid in SCOPE, iid
        it["price_checked_at"] = D
        it["price_check_note"] = SCOPE[iid]
        if it.get("weight_g") is not None:
            assert iid in WEIGHT_REREAD, iid
            wk, needle = WEIGHT_REREAD[iid]
            assert has(wk, needle), (iid, wk, needle)
            it["weight_checked_at"] = D
        quotes = []
        if iid in BN_NEW or iid in Z_NEW:
            old, new = (BN_NEW.get(iid) or Z_NEW.get(iid))
            assert has(k, new), (iid, new)
            n = 0
            for key, vals in it["field_evidence"].items():
                for j, v in enumerate(vals):
                    if v == old: vals[j] = new; n += 1
            assert n >= 1, (iid, "old display not found in field_evidence")
            if it.get("observed_native_display"):
                assert it["observed_native_display"] == [old], (iid, it["observed_native_display"])
                it["observed_native_display"] = [new]
            if it.get("unassigned_price_text"):
                assert it["unassigned_price_text"] == old, iid
                it["unassigned_price_text"] = new
            it.setdefault("superseded_displays", []).append({"text": old, "last_observed": it["retrieved_at"], "superseded_at": D,
                "reason": "The official page rendered a different price display on 2026-11-11. Kept as dated history; not a current value."})
            quotes = [new] + (["-20%", "*Discount code is applied automatically"] if iid in BN_NEW else
                              ["Flash Sale: Save $75-$750 off your purchase starting at $250 or more - Discount Applied in Bag."])
        if iid == "BN-315661":
            assert it["observed_native_display"] == ["$2,210(Setting Price)"] and has(k, "This popular style is sold out")
            it["superseded_displays"] = [{"text": "$2,210(Setting Price)", "last_observed": it["retrieved_at"], "superseded_at": D,
                "reason": "On 2026-11-11 the official page rendered “This popular style is sold out” and no setting price for this item. Kept as dated history; not a current value."}]
            it["observed_native_display"] = None
            for key in ("price", "currency"):
                it["field_evidence"].pop(key, None)
            it["availability_note"] = "This popular style is sold out"
            it["field_evidence"]["availability_note"] = ["This popular style is sold out"]
            it["flags"] = sorted(set(it["flags"]) - {"F-025"} | {"F-008"})
            quotes = ["This popular style is sold out"]
        for fid, ids in NEWFLAGS.items():
            if iid in ids and fid not in it["flags"]:
                it["flags"] = sorted(set(it["flags"]) | {fid})
        if quotes:
            EVID_APPEND.setdefault(it["evidence_file"], (iid, it["source_url"], quotes))
        seen_rows[iid] = it
    save(rel, payload)
assert len(seen_rows) == 32, len(seen_rows)
changes.append("data/listings/*.json + data/solid-gold-verified.json: price_checked_at / price_check_note on 32 rows; 13 displays replaced; BN-315661 display withdrawn")

for evf, (iid, url, quotes) in EVID_APPEND.items():
    p = ROOT / evf; t = p.read_text(encoding="utf-8")
    t = t.rstrip("\n") + f"\n\n## Re-verification — {D} (UTC), {SESSION}\n\n- **URL:** {url}\n- **Result:** the official page rendered a different price display than the stored observation. The stored record was updated to the text below; the earlier text is kept in the data as `superseded_displays`. No amount was assigned, converted or inferred.\n\n"
    for q in quotes:
        t += f"```\n{q}\n```\n\n"
    p.write_text(t, encoding="utf-8")
changes.append(f"evidence/listings: {len(EVID_APPEND)} files appended with 2026-11-11 excerpts")

# ───────────────────────── C. root flags ─────────────────────────
fl = load("data/flags.json"); ids = [x["id"] for x in fl["flags"]]
assert ids[-1] == "F-045" and "F-046" not in ids
byf = {x["id"]: x for x in fl["flags"]}
assert "BN-315661" in byf["F-025"]["affected_items"]
byf["F-025"]["affected_items"].remove("BN-315661")
byf["F-008"]["affected_items"].append("BN-315661")
byf["F-008"]["title"] = "No price in the retrieved product text (VRAI configurator; Blue Nile BN-315661 sold-out page)"
byf["F-008"]["detail"] += " Added 2026-11-11: the Blue Nile BN-315661 page now reads “This popular style is sold out” and renders no setting price for the item, so its earlier displayed amount was withdrawn (see F-047)."
byf["F-008"]["sources"].append(seen_rows["BN-315661"]["source_url"])
U = lambda i: seen_rows[i]["source_url"]
NEW = [
 {"id": "F-046", "severity": "medium", "type": "price_ambiguity",
  "title": "Blue Nile settings now show two amounts under a 20%-off promotion (re-read 2026-11-11)",
  "detail": "On 2026-11-11 each of ten Blue Nile setting pages rendered a struck list amount directly followed by a lower amount, the label “(Setting Price)”, “-20%” and the line “*Discount code is applied automatically”, under a site banner “20% Off* Engagement Ring Settings” (for example “$1,125$900(Setting Price)”). The register shows the page text verbatim and assigns neither amount: no ISO currency is printed, the promotion's end date and terms were not retrieved, and which amount applies at checkout was not tested. The earlier single-amount displays are kept as dated history only.",
  "affected_items": list(BN_NEW), "affected_retailers": [], "sources": [U(i) for i in BN_NEW],
  "recommended_action": "Re-open the official page before budgeting; read the promotion terms and confirm the cart total, currency and end date in writing."},
 {"id": "F-047", "severity": "high", "type": "irregularity",
  "title": "Blue Nile BN-315661 is shown as sold out; its earlier displayed price is withdrawn",
  "detail": "On 2026-11-11 the official BN-315661 page rendered “This popular style is sold out” and showed prices only for other products. It no longer rendered a setting price, stock number, metal or width block for this item. The row is kept with its 2026-10-23 description for traceability, but the earlier “(Setting Price)” display is withdrawn from the current view and is not offered as a price.",
  "affected_items": ["BN-315661"], "affected_retailers": [], "sources": [U("BN-315661")],
  "recommended_action": "Do not plan a purchase around this row. Ask Blue Nile whether the style will return; treat any later price as a new observation."},
 {"id": "F-048", "severity": "medium", "type": "price_ambiguity",
  "title": "Zales: three price displays changed; item numbers on two pages differ from the URL id",
  "detail": "On 2026-11-11 the pages for Z-20046552, Z-20303279 and Z-20301172 each rendered a single amount labelled “Discounted Price” ($1,299.00, $1,399.00 and $1,099.00). The lower promotional amounts stored on 2026-10-22 are no longer rendered. Each page also showed “Flash Sale: Save $75-$750 off your purchase starting at $250 or more - Discount Applied in Bag.” with “Until 11/12/26 at 08:00 AM CST”; a bag-level discount is not a product price and none was computed. Separately, the V-20303279 page prints “Item #: 20615545” and the V-20301172 page prints “Item #: 20301161”, which differ from the identifiers in their URLs. No ISO currency is printed, so every amount stays unassigned.",
  "affected_items": list(Z_NEW), "affected_retailers": [], "sources": [U(i) for i in Z_NEW],
  "recommended_action": "Confirm the item number, the bag total and the currency on the official page and in the cart before purchase."},
 {"id": "F-049", "severity": "medium", "type": "price_ambiguity",
  "title": "Stone and Strand Clara: the amount depends on ring size (re-read 2026-11-11)",
  "detail": "On 2026-11-11 the official .oembed endpoint for the Clara ring listed three offers in USD: sizes 5 and 6 at 2200.0 and size 7 at 2000.0, all in stock. Because the amount depends on the size and no size was chosen for this row, the structured price stays blank. The endpoint's USD statement is new evidence about currency; it does not settle which size-specific amount applies.",
  "affected_items": ["SS-CLARA"], "affected_retailers": [], "sources": [U("SS-CLARA"), U("SS-CLARA") + ".oembed"],
  "recommended_action": "Choose the ring size on the official page and record the amount, currency and return terms shown for that size."},
 {"id": "F-050", "severity": "high", "type": "irregularity",
  "title": "Stone and Strand Rita and Mia: every size out of stock and marked final sale (2026-11-11)",
  "detail": "On 2026-11-11 the official .oembed endpoints for the Rita and Mia rings reported every listed size as not in stock, with the description stating “Final sale and non-returnable”. The amounts returned were 780.0 USD (Rita) and 925.0 USD (Mia); they are not assigned as prices for rows that cannot currently be bought and cannot be returned.",
  "affected_items": ["SS-RITA", "SS-MIA"], "affected_retailers": [], "sources": [U("SS-RITA"), U("SS-MIA"), U("SS-RITA") + ".oembed", U("SS-MIA") + ".oembed"],
  "recommended_action": "Do not buy a final-sale ring that cannot be returned after an independent test. Recheck stock and terms on the official page."},
 {"id": "F-051", "severity": "low", "type": "irregularity",
  "title": "Factory Direct Jewelry GR0001: a Black Friday block renders only $0.00 placeholders",
  "detail": "On 2026-11-11 the GR0001 page still rendered “SALE $1,299.99” and also a “Black Friday Sale” block (code BF26) whose amounts were all “$0.00”. A placeholder is not a price: no discounted amount is recorded and the stored price is unchanged.",
  "affected_items": ["FDJ-GR0001"], "affected_retailers": [], "sources": [U("FDJ-GR0001")],
  "recommended_action": "Ignore the placeholder block; confirm the payable amount in the cart on the day of purchase."},
 {"id": "F-052", "severity": "high", "type": "verification_limit",
  "title": "Staleness: the register was 19 days old before the 2026-11-11 pass; several facts were not re-read",
  "detail": "Before this pass every row was dated 2026-10-22 or 2026-10-23. On 2026-11-11 session S-59551D4B re-read the price (or the absence of one) for all 32 root rows and the gold reference; each row now carries a “price re-read” date. NOT re-read in this pass, and therefore still dated October: band width/depth lines on most rows, the Brilliant Earth metal block, the Stone and Strand product HTML, retailer policy pages (returns, payment, contact, BBB profiles) and the regulatory references. In the companion explorer, product pages for Catbird, Auvere, Quince and the Automic gram weights other than the Coffin Ring and 24k Band were not re-read. A dated row is a record of what a page said on that date, not a live quote.",
  "affected_items": [], "affected_retailers": [], "sources": ["https://www.gold.org/goldhub/data/gold-prices"],
  "recommended_action": "Look for hallucinations again after every review: re-open each official link, compare it with the row, and treat the official page as current whenever they differ."},
 {"id": "F-053", "severity": "low", "type": "policy",
  "title": "Mejuri product page states a holiday return window (read 2026-11-11)",
  "detail": "On 2026-11-11 the Mejuri Bold Diamond Eternity Ring page stated that orders placed from November 1 to December 31, 2026 can be returned through January 31, 2027, alongside the standard free 30-day returns; engraved items remain non-returnable. The dedicated Mejuri returns page was not re-read in this pass, so the retailer-level policy record keeps its October date.",
  "affected_items": ["MJ-BOLD-ETERNITY"], "affected_retailers": [], "sources": [U("MJ-BOLD-ETERNITY")],
  "recommended_action": "Read the return terms shown at checkout and keep a dated copy; do not engrave before independent verification."},
]
fl["flags"].extend(NEW); fl["generated_at"] = D; fl["retrieved_at"] = D
save("data/flags.json", fl); changes.append("data/flags.json: F-046..F-053 added; F-008/F-025 membership updated")

# ───────────────────────── D. root verification log ─────────────────────────
v = load("data/verification-log.json")
assert v["pass"]["session"] == "S-88AA65FD" and len(v["entries"]) == 59
v["generated_at"] = D
v["previous_passes"] = v.get("previous_passes", []) + [dict(v["pass"])]
v["pass"] = {
  "session": SESSION, "checked_at": D, "timezone": "UTC",
  "method": "Staleness review and live re-read on 2026-11-11 between 07:55 and 08:40 UTC. The World Gold Council spot page, the JM Bullion gold-price page and the official product page (or the product's own official .js/.oembed endpoint) of all 32 root rows were fetched and compared with the stored record. Excerpts are verbatim with line breaks collapsed to spaces; the raw transcriptions are in audit/59551d4b/obs_batch1..8.json. Retailer policy pages and regulatory references were NOT re-read and keep their earlier date.",
  "rule": "A stored value is reused only if the official page rendered it again during the pass that recorded it. Rows or fields not re-read this pass keep their earlier date. No value is inferred, averaged, converted, or copied from a search snippet.",
  "limits": "A successful retrieval is not an assay, not a hallmark or maker's-mark check, and not proof of stock or future price. No ring was weighed or XRF-tested. Promotional displays change daily; pages can change after this pass.",
}
CORR = set(BN_NEW) | set(Z_NEW) | {"BN-315661"}
NOPRICE = {"VRAI-CLASSIC-4P", "BN-315661"}
done = set()
for e in v["entries"]:
    if e["kind"] == "listing":
        iid = e["id"]; assert iid in seen_rows, iid
        k = okey(iid)
        obs = ex(k)
        if iid == "AG-COFFIN-RING": obs = ex("ag-coffin-ring-html4", 5)
        e["checked_at"] = D
        e["status"] = "verified_no_price" if iid in NOPRICE else ("verified_correction" if iid in CORR else "verified_match")
        e["observed"] = obs
        e["note"] = SCOPE[iid]
        done.add(iid)
assert len(done) == 32
PRICE_SNAP = {"A182-PRICE-AG-NATURAL": "ag-natural", "A182-PRICE-AG-CLUSTER": "ag-cluster", "A182-PRICE-AG-PETAL": "ag-petal", "A182-PRICE-AG-RUBY": "ag-ruby",
  "A182-PRICE-AG-SAPPHIRE": "ag-sapphire", "A182-PRICE-AG-MOISSANITE": "ag-moissanite", "A182-PRICE-AG-24K": "ag-24k", "A182-PRICE-AG-COFFIN-RING": "ag-coffin-ring",
  "A182-PRICE-AG-CUSHION-SIGNET": "ag-cushion-signet", "A182-PRICE-MENE-ROSE": "mene-rose", "A182-PRICE-MENE-KNOT": "mene-knot", "A182-PRICE-EXT-BE-121H6": "ext-be-121h6",
  "A182-PRICE-SAR-147370": "sar-147370", "A182-PRICE-SAR-145362": "sar-145362", "A182-PRICE-SAR-145364": "sar-145364", "A182-PRICE-SAR-144773": "sar-144773",
  "A182-PRICE-FDJ-GR0001": "fdj-gr0001", "AUTOMIC-CURRENCY": "automic-currency"}
for e in v["entries"]:
    if e["id"] in PRICE_SNAP:
        k = PRICE_SNAP[e["id"]]
        e["checked_at"] = D; e["observed"] = ex(k, 5)
        if k in ("mene-rose", "mene-knot"):
            e["status"] = "verified_correction"
            e["note"] = "Companion-explorer price re-read on the official page: the displayed amount changed and the record was updated; the earlier amount is kept as dated history."
        else:
            e["status"] = "verified_match"
            e["note"] = "Re-read on 2026-11-11 from the official page or its official product endpoint; the stored amount is unchanged."
    elif e["id"] == "GOLD-QUOTE":
        e["checked_at"] = D; e["status"] = "verified_correction"; e["observed"] = ex("gold-wgc", 3)
        e["note"] = "Moving header re-read: 4,059.49 USD per troy ounce, chart block dated 10 November 2026. The October value is kept only as a superseded observation. The header still shows no quote-as-of time (F-026)."
    elif e["kind"] == "market_snapshot":
        e["id"] = "S595-MARKET-WGC-2026-11-11"; e["checked_at"] = D; e["status"] = "verified_correction"; e["observed"] = ex("gold-wgc", 3)
        e["note"] = "World Gold Council header observation used by the calculator, re-read 2026-11-11."
    elif e["kind"] in ("retailer", "reference") and e["id"] != "AUTOMIC-CURRENCY":
        prev = e["status"]
        if prev != "dead_end":
            e["status"] = "not_re_read"
            e["note"] = f"Not re-read on 2026-11-11. Last result ({e['checked_at']}): {prev.replace('_', ' ')}. " + e["note"]
# (JM Bullion is recorded in the companion explorer only: www.jmbullion.com is not an allowed host of the root verification log.)
save("data/verification-log.json", v); changes.append("data/verification-log.json: new pass S-59551D4B; 32 listings + 20 snapshots re-dated; policy rows marked not_re_read")

print("\n".join(changes))
