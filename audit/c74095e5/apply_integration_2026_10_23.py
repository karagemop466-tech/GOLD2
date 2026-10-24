#!/usr/bin/env python3
"""S-C74095E5 evening integration apply script (2026-10-23).

Applies ONLY the changes recorded in audit/c74095e5/live_verification_2026-10-23.md.
Every edit asserts its pre-condition before writing. Idempotency is NOT claimed:
re-running after a successful run will fail its asserts by design.
"""
import copy, datetime, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOW = datetime.datetime.now(datetime.timezone.utc)
assert NOW >= datetime.datetime(2026, 10, 23, 23, 52, tzinfo=datetime.timezone.utc), NOW
OBS = "2026-10-23T23:52:00Z"
changes = []

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

def save(p, doc):
    path = ROOT / p
    raw = path.read_bytes()
    ensure_ascii = not any(b > 127 for b in raw)
    text = json.dumps(doc, indent=2, ensure_ascii=ensure_ascii)
    if raw.endswith(b"\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    changes.append(f"json {p}")

def sub(path, old, new, count=None, min_count=None):
    p = ROOT / path
    t = p.read_text(encoding="utf-8")
    n = t.count(old)
    if count is not None:
        assert n == count, f"{path}: expected {count}x {old!r}, found {n}"
    if min_count is not None:
        assert n >= min_count, f"{path}: expected >={min_count}x {old!r}, found {n}"
    p.write_text(t.replace(old, new), encoding="utf-8")
    changes.append(f"text {path}: {old[:60]!r} x{n}")

def by_id(seq, i):
    for x in seq:
        if x["id"] == i:
            return x
    raise AssertionError(f"id not found: {i}")

# ---------------------------------------------------------------- gold (root)
gp = load("data/gold-price.json")
assert gp["usd_per_troy_oz"] == 3996.31
assert [o["value"] for o in gp["superseded_observations"]] == [4028.53, 4024.36, 4024.45]
gp["superseded_observations"].append({
    "value": 3996.31, "currency": "USD", "quote_date": None,
    "retrieved_at": "2026-10-23", "chart_as_of_date": "2026-10-22",
    "status": "superseded_moving_header",
    "reason": "Header value observed earlier the same day (2026-10-23). The moving header is not a fixed benchmark; only the latest 2026-10-23 observation (3,995.47, evening re-read) is used in calculations.",
})
gp["usd_per_troy_oz"] = 3995.47
assert gp["evidence_quotes"][0] == "3,996.31"
gp["evidence_quotes"][0] = "3,995.47"
gp["field_evidence"]["usd_per_troy_oz"] = ["USD\n\n/oz\n\n-\n\n3,995.47"]
assert gp["quote_scope"].startswith("Moving-header observation retrieved 2026-10-23T20:")
gp["quote_scope"] = ("Moving-header observation retrieved 2026-10-23T23:40Z; exact quote-as-of "
    "timestamp is unconfirmed (F-026). The chart's stated date (22 October 2026) is stored "
    "separately and is not assigned to the header.")
save("data/gold-price.json", gp)

norm = lambda s: " ".join(str(s).split()).lower()
# Surgical edits only — the NIST/eCFR/LBMA quote sections stay untouched.
sub("evidence/gold-price.md", "3,996.31\nLast Updated", "3,995.47\nLast Updated", count=1)
sub("evidence/gold-price.md",
    "**Retrieved:** 2026-10-23 (UTC). This is the later of two direct fetches of the same page on that day.",
    "**Retrieved:** 2026-10-23 (UTC). This is the latest direct fetch of the same page on that day (evening pass, about 23:40Z).",
    count=1)
sub("evidence/gold-price.md",
    "| 4,024.45 | 2026-10-23 |",
    "| 3,996.31 | 2026-10-23 | 2026-10-22 | `superseded_moving_header` | Earlier same-day fetch of the same moving header; superseded by the evening re-read (3,995.47). |\n| 4,024.45 | 2026-10-23 |",
    count=1)
sub("evidence/gold-price.md",
    "## Revision note — 2026-10-23\n",
    ("## Revision note — 2026-10-23 (evening)\n\n"
     "Session S-C74095E5 re-read the same page at about 23:40Z; the header displayed 3,995.47 "
     "with the same chart date (22 October 2026). The 3,996.31 observation moved to the history "
     "table above; no other quoted text, URL, or stored value in this file changed.\n\n"
     "## Revision note — 2026-10-23\n"),
    count=1)

# ------------------------------------------------- root: two new Sarraf rows
sg = load("data/solid-gold-verified.json")
assert len(sg["items"]) == 13
tpl = copy.deepcopy(by_id(sg["items"], "SAR-145362"))

def sar_root(**kw):
    it = copy.deepcopy(tpl)
    it.update(kw)
    return it

sar151362 = sar_root(
    id="SAR-151362",
    name="14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
    sku="3552G", color="Yellow", width_mm=None,
    weight_g=9.2, weight_basis="Approximate Metal Weight: 9.20 grams",
    price=8203.0, original_price=9594.0,
    source_url="https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-belcher-diamond-ring-1ctw.html",
    evidence_file="evidence/listings/sar-151362.md",
    flags=["F-002", "F-015", "F-016", "F-021", "F-024", "F-036"],
    notes=("Complete natural-diamond solitaire (Belcher) ring disclosing explicit '14K Solid Gold', "
           "separate 'Approximate Metal Weight: 9.20 grams', 'Diamond Weight: 1.00 Ct.' (Natural, H, SI 1), "
           "and explicit 'Now: US$8,203.00'. No band width is stated in the captured text. Seller claims "
           "are dated observations, not independent testing."),
    field_evidence={
        "name": ["14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw"],
        "sku": ["SKU:3552G"],
        "metal": ["14K Solid Gold"], "karat": ["14K Solid Gold"],
        "color": ["14k Yellow gold"],
        "weight_g": ["Approximate Metal Weight: 9.20 grams"],
        "weight_basis": ["Approximate Metal Weight: 9.20 grams"],
        "price": ["Now: US$8,203.00"], "original_price": ["Was: US$9,594.00"],
        "currency": ["Now: US$8,203.00"],
        "price_basis": ["14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw"],
        "center_stone_included": ["14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
                                   "Diamond Weight: 1.00 Ct."],
    },
)
sar147371 = sar_root(
    id="SAR-147371",
    name="14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
    sku="9422-100-14ky", color="Yellow", width_mm=10.0,
    weight_g=7.7, weight_basis="Approximate Metal Weight: 7.70 grams",
    price=4049.0, original_price=4736.0,
    source_url="https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-0-98-ct.html",
    evidence_file="evidence/listings/sar-147371.md",
    flags=["F-002", "F-015", "F-016", "F-021", "F-024", "F-036", "F-043"],
    notes=("Complete natural-diamond solitaire ring disclosing explicit '14K Solid Gold', separate "
           "'Approximate Metal Weight: 7.70 grams', 'Diamond Weight: 0.98 Ct.' (Natural, I1), and explicit "
           "'Now: US$4,049.00'. The page contradicts itself on diamond color — specifications state "
           "'Diamond Color: G' while the description states 'I1 in clarity and H in color' — flagged F-043. "
           "Seller claims are dated observations, not independent testing."),
    field_evidence={
        "name": ["14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct."],
        "sku": ["SKU:9422-100-14ky"],
        "metal": ["14K Solid Gold"], "karat": ["14K Solid Gold"],
        "color": ["14k Yellow gold"],
        "width_mm": ["measures approximately 10.0mm"],
        "weight_g": ["Approximate Metal Weight: 7.70 grams"],
        "weight_basis": ["Approximate Metal Weight: 7.70 grams"],
        "price": ["Now: US$4,049.00"], "original_price": ["Was: US$4,736.00"],
        "currency": ["Now: US$4,049.00"],
        "price_basis": ["14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct."],
        "center_stone_included": ["14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
                                   "Diamond Weight: 0.98 Ct."],
    },
)
sg["items"] += [sar151362, sar147371]

# F-044 linkage on the two solid-gold register anchors
for rid in ("AG-CUSHION-SIGNET", "MJ-BOLD-ETERNITY"):
    by_id(sg["items"], rid)["flags"].append("F-044")
save("data/solid-gold-verified.json", sg)

SAR151_URL = sar151362["source_url"]; SAR147_URL = sar147371["source_url"]

# evidence files for the new rows
ev151 = f"""# Evidence — SAR-151362

- Source URL: {SAR151_URL}
- Retrieved: 2026-10-23 (UTC) — evening pass, S-C74095E5
- Retailer: Sarraf Jewelry Inc.
- Title: `14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw`

## Verbatim captures (fetch_page, chunk 0)

> 14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw

> SKU:3552G

> 14K Solid Gold

> 14k Yellow gold

> Approximate Metal Weight: 9.20 grams

> Diamond Weight: 1.00 Ct.

> Diamond Color: H · Diamond Clarity: SI 1 · Diamond ( Natural / Lab Created ): Natural

> MSRP: US$31,899.00 · Was: US$9,594.00 · Now: US$8,203.00

## Field mapping

- `name`, `color` ← product title. `sku` 3552G ← "SKU:3552G" (stock number 151362).
- `metal` / `karat` 14 / `solid_gold_explicit` true ← "14K Solid Gold".
- `weight_g` 9.2 ← "Approximate Metal Weight: 9.20 grams" (metal-only wording; seller-stated, approximate).
- `price` 8203.0 USD ← "Now: US$8,203.00"; `original_price` 9594.0 ← "Was: US$9,594.00".
- `width_mm` / `depth_mm` null — no width or depth stated in the captured text (F-016).
- Hallmark / maker's mark / independent-test permission: not stated (F-002, F-021, F-024).
- Seller claims are dated observations, not independent testing. No melt value is stated
  here because it is generated from the dated gold reference.
"""
ev147 = f"""# Evidence — SAR-147371

- Source URL: {SAR147_URL}
- Retrieved: 2026-10-23 (UTC) — evening pass, S-C74095E5
- Retailer: Sarraf Jewelry Inc.
- Title: `14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.`

## Verbatim captures (fetch_page, chunk 0)

> 14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.

> SKU:9422-100-14ky

> 14K Solid Gold

> 14k Yellow gold

> Approximate Metal Weight: 7.70 grams

> Diamond Weight: 0.98 Ct.

> Diamond Color: G

> I1 in clarity and H in color

> measures approximately 10.0mm

> MSRP: US$15,747.00 · Was: US$4,736.00 · Now: US$4,049.00

## Field mapping

- `name`, `color` ← product title. `sku` 9422-100-14ky ← "SKU:9422-100-14ky" (stock number 147371).
- `metal` / `karat` 14 / `solid_gold_explicit` true ← "14K Solid Gold".
- `weight_g` 7.7 ← "Approximate Metal Weight: 7.70 grams" (metal-only wording; seller-stated, approximate).
- `width_mm` 10.0 ← "measures approximately 10.0mm" (seller's approximate dimension).
- `price` 4049.0 USD ← "Now: US$4,049.00"; `original_price` 4736.0 ← "Was: US$4,736.00".
- Diamond color is recorded nowhere as confirmed: the specifications state
  "Diamond Color: G" while the description states "I1 in clarity and H in color" (F-043).
- Hallmark / maker's mark / independent-test permission: not stated (F-002, F-021, F-024).
- Seller claims are dated observations, not independent testing. No melt value is stated
  here because it is generated from the dated gold reference.
"""
for fn, txt, item in (("sar-151362.md", ev151, sar151362), ("sar-147371.md", ev147, sar147371)):
    tn = norm(txt)
    for qs in item["field_evidence"].values():
        for q in qs:
            assert norm(q) in tn, f"{fn}: quote missing {q!r}"
    (ROOT / "evidence/listings" / fn).write_text(txt, encoding="utf-8")
    changes.append(f"text evidence/listings/{fn} created")

# F-044 linkage in category files + collect root canonical URLs for dashboard fixes
F044_ITEMS = ["AG-CUSHION-SIGNET", "MJ-BOLD-ETERNITY", "VRAI-CLASSIC-4P",
              "BN-194158", "BN-195269", "BN-203348", "BN-315661", "BN-316238"]
root_url = {}
all_root_items = list(sg["items"])
for fn in ("18k", "budget", "halo-pave", "solitaire", "three-stone-vintage"):
    d = load(f"data/listings/{fn}.json")
    dirty = False
    for it in d["items"]:
        all_root_items.append(it)
        if it["id"] in F044_ITEMS:
            assert "F-044" not in it["flags"]
            it["flags"].append("F-044"); dirty = True
    if dirty:
        save(f"data/listings/{fn}.json", d)
for it in all_root_items:
    root_url[it["id"]] = (it["source_url"], it["retailer_id"])
assert len(all_root_items) == 32, len(all_root_items)

# ------------------------------------------------------------------ root flags
fd = load("data/flags.json")
assert len(fd["flags"]) == 39
F = lambda i: by_id(fd["flags"], i)
NEW2 = ["SAR-151362", "SAR-147371"]

f1 = F("F-001")
f1["title"] = f1["title"].replace("17 of 30 items", "17 of 32 items"); assert "17 of 32" in f1["title"]
f1["detail"] = f1["detail"].replace("17 of the 30 listed settings/rings", "17 of the 32 listed settings/rings") \
                          .replace("(the 13 rows on Explicit Solid Gold do state", "(the 15 rows on Explicit Solid Gold do state")
assert "32 listed" in f1["detail"] and "15 rows" in f1["detail"]

f2 = F("F-002")
f2["detail"] = f2["detail"].replace("None of the 30 captured product pages", "None of the 32 captured product pages") \
                            .replace("the other 29 omit both", "the other 31 omit both")
assert "32 captured" in f2["detail"] and "other 31" in f2["detail"]
f2["affected_items"] += NEW2; assert len(f2["affected_items"]) == 32

f3 = F("F-003")
f3["title"] = f3["title"].replace("23 of 30 product pages", "23 of 32 product pages"); assert "23 of 32" in f3["title"]
f3["detail"] = f3["detail"].replace("Only 7 of 30 rows publish", "Only 9 of 32 rows publish") \
                            .replace(", and SAR-144773 13.40 g at size 10)",
                                     ", SAR-144773 13.40 g at size 10, SAR-151362 9.20 g, and SAR-147371 7.70 g)")
assert "9 of 32" in f3["detail"] and "SAR-147371 7.70 g" in f3["detail"]

for fid, expect in (("F-015", 31), ("F-021", 32), ("F-024", 32)):
    fl = F(fid); fl["affected_items"] += NEW2
    assert len(fl["affected_items"]) == expect, (fid, len(fl["affected_items"]))

f16 = F("F-016"); f16["affected_items"] += NEW2; assert len(f16["affected_items"]) == 29
f16["detail"] = f16["detail"].replace(
    "Five rows have no numeric band width (four Zales rows plus VRAI, which says only “Standard”).",
    "Six rows have no numeric band width (four Zales rows, VRAI, which says only “Standard”, and SAR-151362).") \
    .replace("Fifteen rows have no numeric band depth/thickness",
             "Seventeen rows have no numeric band depth/thickness")
assert "Six rows" in f16["detail"] and "Seventeen rows" in f16["detail"]

f36 = F("F-036"); f36["affected_items"] += NEW2; assert len(f36["affected_items"]) == 6
f36["sources"] += [SAR151_URL, SAR147_URL]

fd["flags"].append({
    "id": "F-043", "severity": "medium",
    "title": "Sarraf SAR-147371 contradicts itself on diamond color (G vs H)",
    "detail": ("The SAR-147371 product page captured 2026-10-23 states 'Diamond Color: G' in its "
               "specifications and 'I1 in clarity and H in color' in its description. The register "
               "records neither color as confirmed; the 0.98 Ct natural-diamond weight, I1 clarity, "
               "'14K Solid Gold' wording, 7.70 g metal weight and US$4,049.00 price are stated "
               "consistently on the page."),
    "recommended_action": ("Obtain written confirmation of the diamond color (and its grading basis) "
                           "from Sarraf before purchase; verify the stone independently on arrival."),
    "type": "irregularity", "affected_items": ["SAR-147371"],
    "affected_retailers": ["sarraf"], "sources": [SAR147_URL],
})
f44_retailers = sorted({root_url[i][1] for i in F044_ITEMS})
fd["flags"].append({
    "id": "F-044", "severity": "high",
    "title": ("Companion dashboard carried dead/wrong product URLs, wrong Blue Nile names and "
              "unsupported USD assignments (corrected 2026-10-23)"),
    "detail": ("Live cross-register audit on 2026-10-23 found the companion dashboard (dashboard/) "
               "linking three dead product URLs — AG-CUSHION-SIGNET to a 404 lab-grown slug, "
               "MJ-BOLD-ETERNITY to a 'Page Not Found' lab-grown slug, and VRAI-CLASSIC-4P to a "
               "non-existent configuration path — and showing wrong product names for all five "
               "Blue Nile item IDs (194158, 195269, 203348, 315661, 316238): those names came from "
               "non-canonical URL slugs while the live pages render different titles (Blue Nile "
               "serves the product by item ID regardless of slug). The dashboard also published "
               "USD prices for those five settings although no captured Blue Nile page states "
               "'USD'; under the No-Hallucinations Policy the dashboard prices are now blank with "
               "the verbatim '$(Setting Price)' displays preserved in notes, matching this register. "
               "The root-register rows listed here were themselves verified correct (canonical "
               "slugs, live titles, blank prices) and appear only as the cross-reference anchor; "
               "dashboard flag DF-008 carries the same correction."),
    "recommended_action": ("Re-derive product identity from the live page title, never the URL slug, "
                           "and assign a currency only where the page or a stored currency proof states it."),
    "type": "irregularity", "affected_items": F044_ITEMS,
    "affected_retailers": f44_retailers,
    "sources": [root_url[i][0] for i in F044_ITEMS],
})
save("data/flags.json", fd)

# retailer-side flag linkage
rd = load("data/retailers.json")
by_id(rd["retailers"], "sarraf")["flags"] += ["F-043"]  # F-044 has no Sarraf anchor item
for rid in f44_retailers:
    if rid == "sarraf":
        continue
    r = by_id(rd["retailers"], rid)
    assert "F-044" not in r["flags"]; r["flags"].append("F-044")
save("data/retailers.json", rd)

# verification log
vl = load("data/verification-log.json")
vl["pass"] = {
    "session": "S-C74095E5", "checked_at": "2026-10-23", "timezone": "UTC",
    "method": ("Live fetch_page re-verification on 2026-10-23 (23:39–23:59Z) of the World Gold Council "
               "spot page, Menē Rose/Knot, Automic Gold (product HTML, Shopify JSON extracts and the "
               "cart.js currency endpoint), all stored Sarraf rows plus two newly added Sarraf "
               "solitaires (SAR-151362, SAR-147371), Factory Direct Jewelry GR0001, Brilliant Earth "
               "BE121H6, the Mejuri natural-diamond eternity page, the VRAI configurator, Stone and "
               "Strand, Catbird, Quince, Auvere, Zales V-19957449, all five dashboard Blue Nile item "
               "IDs, and 16 CFR 23.3. Rows not re-read in this pass are listed in "
               "audit/c74095e5/live_verification_2026-10-23.md §9 and keep their earlier dated entries."),
    "rule": vl["pass"]["rule"], "limits": vl["pass"]["limits"],
}
gq = by_id(vl["entries"], "GOLD-QUOTE")
gq["observed"][0] = "3,995.47"
gq["note"] = ("Evening re-read on 2026-10-23 (about 23:40Z) replaced the earlier same-day header "
              observation. The header is moving; quote_date stays null because it carries "
              "no timestamp (F-026). Superseded values are retained only as history in data/gold-price.json.")
for item, obs, note in (
    (sar151362, ["14K Solid Gold", "Approximate Metal Weight: 9.20 grams", "Now: US$8,203.00"],
     "New row added 2026-10-23 by S-C74095E5 from the official Sarraf product page: explicit 14K Solid Gold, 9.20 g metal weight, US$8,203.00."),
    (sar147371, ["14K Solid Gold", "Approximate Metal Weight: 7.70 grams", "Now: US$4,049.00"],
     "New row added 2026-10-23 by S-C74095E5 from the official Sarraf product page: explicit 14K Solid Gold, 7.70 g metal weight, US$4,049.00. Diamond color conflict G (specifications) vs H (description) flagged F-043."),
):
    vl["entries"].append({"id": item["id"], "kind": "listing", "label": item["name"],
                          "retailer": "Sarraf Jewelry Inc.", "url": item["source_url"],
                          "checked_at": "2026-10-23", "status": "verified_match",
                          "observed": obs, "note": note})
save("data/verification-log.json", vl)

# ------------------------------------------------------------- explore register
cat = load("data/catalog.json")
assert len(cat["products"]) == 44 and cat["meta"]["marketReference"]["amount"] == 4035.54
cat["meta"].update({
    "reviewedAt": OBS,
    "reviewSession": "arena-c74095e5 evening integration (live re-verification 2026-10-23 23:39–23:59Z) on base records from arena-1eb9f828 / arena-062f314f",
    "scope": "46 unique named product pages across 13 retailers verified through 2026-10-23 UTC, covering all root-register and companion-dashboard listings without duplication.",
})
cat["meta"]["observationWindow"]["end"] = OBS
cat["meta"]["marketReference"].update({
    "amount": 4009.38, "publishedAt": "2026-10-23T23:46:00Z", "observedAt": OBS,
    "caveat": "Dated dealer reference, not LBMA and not a live feed. The page's own timestamp is 2026-10-23 19:46 EDT. Calculations are conditional illustrations only.",
})
for pid, amt in (("mene-rose", 1325), ("mene-knot", 1442)):
    pr = by_id(cat["products"], pid)
    pr["observedAt"] = OBS
    pr["price"]["amount"] = amt; pr["price"]["observedAt"] = OBS

def sar_product(pid, name, scope, stone_q, stone_v, grams, amount):
    p = copy.deepcopy(by_id(cat["products"], "sar-145362"))
    p["id"] = pid; p["source"] = pid
    p["name"] = {"value": name, "source": pid, "quote": "name"}
    p["observedAt"] = OBS; p["scope"] = scope
    for f in ("karat", "solidGold", "stone", "itemWeightG"):
        p["facts"][f]["source"] = pid
    p["facts"]["stone"]["value"] = stone_v
    p["facts"]["itemWeightG"]["value"] = grams
    p["price"].update({"amount": amount, "observedAt": OBS, "scope": scope,
                       "evidence": [{"source": pid, "quote": "price"}]})
    p["reportedWeight"].update({"min": grams, "max": grams,
                                "evidence": {"source": pid, "quote": "weight"}})
    return p

cat["products"] += [
    sar_product("sar-151362", "14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
                "14K Solid Yellow Gold complete ring with 1.00 ct H/SI1 natural diamond",
                "Natural Diamond 1.00 Ct. (Diamond Weight: 1.00 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Color: H; Diamond Clarity: SI 1)",
                "Natural Diamond 1.00 Ct.", 9.2, 8203),
    sar_product("sar-147371", "14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
                "14K Solid Yellow Gold complete ring with 0.98 ct I1 natural diamond (seller states color G in specifications and H in description — unresolved; root flag F-043)",
                "Natural Diamond 0.98 Ct. (Diamond Weight: 0.98 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Clarity: I1; Diamond Color: G in specifications vs 'H in color' in description — unresolved)",
                "Natural Diamond 0.98 Ct.", 7.7, 4049),
]
assert len(cat["products"]) == 46
save("data/catalog.json", cat)

ev = load("research/evidence.json")
assert len(ev["sources"]) == 85
jm = by_id(ev["sources"], "jm-gold")
jm["quotes"].update({"quote": "$4,009.38 USD", "ask": "Bid: $3,994.88   Ask: $4,009.38",
                     "header-value": "$4,009.38"})
jm["observedAt"] = OBS; jm["lastRecheckedAt"] = OBS
jm["method"] = "fetch_page; short excerpts transcribed and rechecked 2026-10-23 by session S-C74095E5"
jm["note"] = ("Dealer page timestamped 2026-10-23 19:46 EDT (23:46Z) displayed 'Gold Ask $4,009.38' "
              "with 'Bid: $3,994.88 Ask: $4,009.38'. Supersedes the same-day 05:56 EDT observation of "
              "$4,035.54 (2026-10-22: $4,039.76). This is a dealer reference, not an LBMA benchmark "
              "or live feed.")
for sid, price, chain in (("mene-rose", "$1,325", "$1,336 earlier on 2026-10-23 and $1,346 on 2026-10-22"),
                          ("mene-knot", "$1,442", "$1,454 earlier on 2026-10-23 and $1,465 on 2026-10-22")):
    s = by_id(ev["sources"], sid)
    s["quotes"]["price"] = price; s["observedAt"] = OBS; s["lastRecheckedAt"] = OBS
    s["method"] = "fetch_page; short excerpts transcribed and rechecked 2026-10-23 by session S-C74095E5"
    s["note"] = (f"Evening re-read on 2026-10-23 rendered {price} USD, superseding {chain}; "
                 "Menē prices these Crafted-on-Demand pieces from metal value, so earlier amounts "
                 "are superseded, not additive.")

n_automic = 0
for s in ev["sources"]:
    host = re.sub(r"^https?://", "", s["url"]).split("/")[0]
    if "automicgold.com" in host:
        s["lastRecheckedAt"] = OBS; n_automic += 1
assert n_automic >= 5, n_automic

def sar_source(pid, url, name, stone_q, weight_q, price_q, note):
    return {"id": pid, "publisher": "Sarraf Jewelry Inc.", "kind": "product", "url": url,
            "observedAt": OBS, "method": "fetch_page live primary verification by S-C74095E5",
            "access": "fetched", "note": note,
            "quotes": {"name": name, "material": "14K Solid Gold", "stone": stone_q,
                       "weight": weight_q, "price": price_q}}

ev["sources"] += [
    sar_source("sar-151362", SAR151_URL, "14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
               "Natural Diamond 1.00 Ct. (Diamond Weight: 1.00 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Color: H; Diamond Clarity: SI 1)",
               "Approximate Metal Weight: 9.20 grams", "Now: US$8,203.00",
               "New row 2026-10-23: explicit 14K Solid Gold, 9.20 g metal weight, US$8,203.00 (was US$9,594.00)."),
    sar_source("sar-147371", SAR147_URL, "14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
               "Natural Diamond 0.98 Ct. (Diamond Weight: 0.98 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Clarity: I1; Diamond Color: G in specifications vs 'H in color' in description — unresolved)",
               "Approximate Metal Weight: 7.70 grams", "Now: US$4,049.00",
               "New row 2026-10-23: explicit 14K Solid Gold, 7.70 g metal weight, US$4,049.00 (was US$4,736.00). Diamond color conflict flagged (root F-043)."),
]
assert len(ev["sources"]) == 87
save("research/evidence.json", ev)

rv = load("data/review.json")
assert len(rv["findings"]) == 26
sp = by_id(rv["findings"], "sarraf-policy-and-size10")
sp["scope"] = "sar-147370, sar-145362, sar-145364, sar-144773, sar-151362, sar-147371"
src_ids = {s["id"] for s in ev["sources"]}
eve_sources = ["jm-gold", "mene-rose", "mene-knot"] + (["wgc-panel-review"] if "wgc-panel-review" in src_ids else [])
rv["findings"] += [
    {"id": "reobservation-2026-10-23-evening",
     "title": "Evening 2026-10-23 re-observation supersedes same-day gold and Menē values",
     "scope": "mene-rose, mene-knot, jm-gold, data/gold-price.json (root register)",
     "finding": ("A second live pass on 2026-10-23 (23:39–23:59Z) superseded three dated references: "
                 "JM Bullion dealer Ask $4,035.54 → $4,009.38 (page timestamp 2026-10-23 19:46 EDT); "
                 "Menē Rose Ring $1,336 → $1,325 and Knot Ring $1,454 → $1,442; and the root register's "
                 "World Gold Council header $3,996.31 → $3,995.47 (chart data as of 22 October 2026). "
                 "Superseded amounts remain only in dated notes/history, never as current values."),
     "action": "Treat all gold-linked display prices as dated snapshots; re-read the official page before any purchase decision.",
     "sources": eve_sources},
    {"id": "sar-147371-color-conflict",
     "title": "Sarraf SAR-147371 states diamond color G and H on the same page",
     "scope": "sar-147371",
     "finding": ("The SAR-147371 product page states 'Diamond Color: G' in its specifications and "
                 "'I1 in clarity and H in color' in its description. Neither color is recorded as "
                 "confirmed; see root flag F-043."),
     "action": "Obtain written confirmation of the diamond color from Sarraf before purchase and verify the stone independently on arrival.",
     "sources": ["sar-147371"]},
]
assert len(rv["findings"]) == 28
save("data/review.json", rv)

# --------------------------------------------------------- dashboard build.py
B = "dashboard/scripts/build.py"
fine_g = 3995.47 / 31.1034768
sub(B, 'SPOT_USD = Decimal("3996.31")', 'SPOT_USD = Decimal("3995.47")', count=1)
sub(B, '"spot_usd_per_troy_oz": 3996.31,', '"spot_usd_per_troy_oz": 3995.47,', count=1)
sub(B, '"USD /oz - 3,996.31"', '"USD /oz - 3,995.47"', count=1)
sub(B, '$3,996.31', '$3,995.47', min_count=5)
sub(B, 'value="3996.31"', 'value="3995.47"', min_count=1)
sub(B, '$128.48', f'${fine_g:,.2f}', min_count=1)

# Menē
sub(B, '"price_usd": 1336.00,', '"price_usd": 1325.00,', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $1,336.00 USD (updated from $1,346 on 2026-10-22 with spot drift).",',
    '"price_note": "Verified live 2026-10-23 (evening re-read): $1,325.00 USD (moved from $1,336 earlier the same day and $1,346 on 2026-10-22 with spot drift).",', count=1)
sub(B, 'pure 24 karat jewelry by gram weight | $1,336"', 'pure 24 karat jewelry by gram weight | $1,325"', count=1)
sub(B, '"price_usd": 1454.00,', '"price_usd": 1442.00,', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $1,454.00 USD (updated from $1,465 on 2026-10-22 with spot drift).",',
    '"price_note": "Verified live 2026-10-23 (evening re-read): $1,442.00 USD (moved from $1,454 earlier the same day and $1,465 on 2026-10-22 with spot drift).",', count=1)
sub(B, 'pure 24 karat jewelry by gram weight | $1,454"', 'pure 24 karat jewelry by gram weight | $1,442"', count=1)

# Automic cushion: canonical identity
sub(B, '"name": "Lab-Grown Cushion Diamond Signet Ring (Solid 14k Gold)",',
    '"name": "Cushion Diamond Signet Ring (Solid 14k Gold and 950 Platinum)",', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $2,758.00 USD (`cart.js` verified USD).",',
    '"price_note": "Verified live 2026-10-23: $2,758.00 USD (`cart.js` verified USD) for the page\'s default display; the earlier dashboard URL (lab-grown slug) returns 404 — corrected, see DF-008. Lab-grown variant price not re-read.",', count=1)
sub(B, 'https://www.automicgold.com/products/lab-grown-cushion-diamond-signet-ring',
    'https://www.automicgold.com/products/cushion-diamond-signet-ring', min_count=1)
sub(B, '"quote": "Solid 14k Gold | Lab-Grown Cushion Diamond Signet Ring | $2,758",',
    '"quote": "Solid 14k Gold and 950 Platinum | Cushion Diamond Signet Ring | $2,758",', count=1)

# Mejuri: live natural-diamond page, from-price unassigned
sub(B, '"name": "Bold Lab Grown Diamond Eternity Ring (Solid 14k White Gold)",',
    '"name": "Bold Diamond Eternity Ring (Solid 14k White Gold, Natural Diamond)",', count=1)
sub(B, '"price_usd": 2900.00,', '"price_usd": None,', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $2,900.00 USD complete ring.",',
    '"price_note": "Blank: live page 2026-10-23 displays \'From$2,900\' (a from-price; no ISO currency captured) — not assigned as a USD amount. Earlier dashboard URL (lab-grown slug) is \'Page Not Found\' — corrected, see DF-008.",', count=1)
sub(B, 'https://mejuri.com/products/bold-lab-grown-diamond-eternity-ring',
    'https://mejuri.com/products/bold-diamond-eternity-ring', min_count=1)
sub(B, '"quote": "Solid White Gold (14k) | 14k solid gold | $2,900",',
    '"quote": "Solid White Gold (14k), Natural Diamond | 14k solid gold | From$2,900",', count=1)

# VRAI: canonical configurator URL from the root register
vrai_url = root_url["VRAI-CLASSIC-4P"][0]
# appears twice: the ring product_url and the vrai retailer jewelry_notes_url
sub(B, 'https://www.vrai.com/engagement-ring/classic-4-prong-solitaire/round-brilliant-yellow-gold-41383090421853',
    vrai_url, min_count=2)
sub(B, '"price_note": "Blank: VRAI configurator withholds standalone setting price until lab diamond is chosen.",',
    '"price_note": "Blank: VRAI configurator withholds standalone setting price until lab diamond is chosen. Earlier dashboard configuration URL no longer exists — corrected, see DF-008.",', count=1)

# Blue Nile x5: live titles, canonical URLs, blank prices with verbatim displays
BN = {
    "BN-194158": ("Classic Four Prong Solitaire Engagement Ring in 18k Yellow Gold",
                  "Petite Solitaire Engagement Ring Setting in 18k Yellow Gold", 1125,
                  "Classic Four Prong Solitaire Engagement Ring in 18k Yellow Gold | $1,125(Setting Price)",
                  '"Petite Solitaire Engagement Ring in 18k Yellow Gold | $1,125 (Setting Price)"', None),
    "BN-195269": ("Petite Solitaire Engagement Ring in 18k Yellow Gold",
                  "Classic Four-Prong Solitaire Setting in 18k Rose Gold", 1155,
                  "Petite Solitaire Engagement Ring in 18k Yellow Gold | $1,155(Setting Price)",
                  '"Classic Four-Prong Solitaire Engagement Ring in 18k Rose Gold | $1,155 (Setting Price)"', None),
    "BN-316238": ("Comfort Fit Solitaire Engagement Ring in 14K White Gold By James Allen",
                  "Petite Micropavé Engagement Ring Setting in 14k White Gold", 1240,
                  "Comfort Fit Solitaire Engagement Ring in 14K White Gold By James Allen | $1,240(Setting Price)",
                  '"Petite Micropavé Engagement Ring in 14k White Gold | $1,240 (Setting Price)"',
                  ('"categories": ["halo-pave", "budget"],\n        "name": "Comfort Fit',
                   '"categories": ["solitaire", "budget"],\n        "name": "Comfort Fit')),
    "BN-315661": ("Pavé Contour Diamond Engagement Ring in 14K White Gold By James Allen",
                  "French Pavé Halo Engagement Ring Setting in 14k White Gold (1/5 ctw)", 2210,
                  "Pavé Contour Diamond Engagement Ring in 14K White Gold By James Allen | $2,210(Setting Price)",
                  '"French Pavé Halo Engagement Ring in 14k White Gold (1/5 ct. tw.) | $2,210"', None),
    "BN-203348": ("Classic Simple Solitaire Engagement Ring in 14K Yellow Gold",
                  "Three-Stone Trellis Engagement Ring Setting in 14k Yellow Gold", 1145,
                  "Classic Simple Solitaire Engagement Ring in 14K Yellow Gold | $1,145(Setting Price)",
                  '"Three-Stone Trellis Engagement Ring in 14k Yellow Gold | $1,145"',
                  ('"categories": ["three-stone-vintage"],\n        "name": "Classic Simple',
                   '"categories": ["solitaire"],\n        "name": "Classic Simple')),
}
old_bn_urls = {
    "BN-194158": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
    "BN-195269": "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-rose-gold-item-195269",
    "BN-316238": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238",
    "BN-315661": "https://www.bluenile.com/engagement-rings/design-your-own-ring/french-pave-halo-engagement-ring-in-14k-white-gold-1-5-ct-tw-item-315661",
    "BN-203348": "https://www.bluenile.com/engagement-rings/design-your-own-ring/three-stone-trellis-engagement-ring-in-14k-yellow-gold-item-203348",
}
for bid, (title, old_name, amt, quote, old_quote, cat_fix) in BN.items():
    sub(B, f'"name": "{old_name}",', f'"name": "{title}",', count=1)
    sub(B, f'"price_usd": {amt}.00,', '"price_usd": None,', count=1)
    sub(B, f'"quote": {old_quote},', f'"quote": "{quote}",', count=1)
    sub(B, old_bn_urls[bid], root_url[bid][0], min_count=1)
    if cat_fix:
        sub(B, cat_fix[0], cat_fix[1], count=1)

# BN price notes (each unique)
sub(B, '"price_note": "Verified live 2026-10-23: $1,125.00 USD (setting price, excludes center diamond).",',
    '"price_note": "Blank per No-Hallucinations Policy: live page 2026-10-23 displays \'$1,125(Setting Price)\' with no \'USD\' statement — amount preserved verbatim, currency not assigned (excludes center diamond). Earlier dashboard name came from a non-canonical slug — corrected, see DF-008.",', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $1,155.00 USD (setting price).",',
    '"price_note": "Blank per No-Hallucinations Policy: live page 2026-10-23 displays \'$1,155(Setting Price)\' with no \'USD\' statement — amount preserved verbatim, currency not assigned. Earlier dashboard name came from a non-canonical slug — corrected, see DF-008.",', count=1)
sub(B, '"price_note": "Verified live 2026-10-23 (preserved from S-70B76800): $1,240.00 USD (setting price).",',
    '"price_note": "Blank per No-Hallucinations Policy: live page 2026-10-23 displays \'$1,240(Setting Price)\' with no \'USD\' statement — amount preserved verbatim, currency not assigned. The live title is a Comfort Fit Solitaire, not the Petite Micropavé named in the slug (root flag F-041) — corrected, see DF-008.",', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $2,210.00 USD (setting price).",',
    '"price_note": "Blank per No-Hallucinations Policy: live page 2026-10-23 displays \'$2,210(Setting Price)\' with no \'USD\' statement — amount preserved verbatim, currency not assigned. Earlier dashboard name came from a non-canonical slug — corrected, see DF-008.",', count=1)
sub(B, '"price_note": "Verified live 2026-10-23: $1,145.00 USD (setting price).",',
    '"price_note": "Blank per No-Hallucinations Policy: live page 2026-10-23 displays \'$1,145(Setting Price)\' with no \'USD\' statement — amount preserved verbatim, currency not assigned. Earlier dashboard name came from a non-canonical slug — corrected, see DF-008.",', count=1)

# DF-008 linkage on the eight corrected rings (scoped per-block edits via regex)
bp = ROOT / B
bt = bp.read_text(encoding="utf-8")
for rid in ("AG-CUSHION-SIGNET", "MJ-BOLD-ETERNITY", "VRAI-CLASSIC-4P",
            "BN-194158", "BN-195269", "BN-316238", "BN-315661", "BN-203348"):
    m = re.search(r'(\{\n\s+"id": "' + rid + r'".*?"flags": \[)([^\]]*)(\])', bt, re.S)
    assert m, rid
    bt = bt[:m.start()] + m.group(1) + m.group(2).rstrip() + ', "DF-008"' + m.group(3) + bt[m.end():]
    changes.append(f"text {B}: DF-008 on {rid}")

# DF-008 + DF-009 flag definitions, inserted at end of FLAGS list
df_new = '''    {
        "id": "DF-008",
        "severity": "high",
        "title": "Dashboard identity defects corrected 2026-10-23: dead URLs, slug-derived Blue Nile names, unsupported USD (root F-044)",
        "detail": "Evening live audit (S-C74095E5, 2026-10-23 23:39-23:59Z) found three dead product URLs (AG-CUSHION-SIGNET 404 lab-grown slug, MJ-BOLD-ETERNITY 'Page Not Found' lab-grown slug, VRAI-CLASSIC-4P non-existent configuration path) and wrong names for all five Blue Nile item IDs taken from non-canonical URL slugs — Blue Nile serves the product by item ID regardless of slug, so the pages rendered different rings than their dashboard names. No captured Blue Nile page states 'USD', so the five dashboard USD prices are now blank with the verbatim '$...(Setting Price)' displays preserved in price notes, matching the root register. Mejuri's live natural-diamond page shows only a 'From$2,900' from-price and stays blank.",
        "action": "Identity comes from the live page title, never the URL slug; assign a currency only where the page or a stored currency proof states it.",
        "sources": [
            "https://www.automicgold.com/products/cushion-diamond-signet-ring",
            "https://mejuri.com/products/bold-diamond-eternity-ring",
            "%s",
        ],
    },
    {
        "id": "DF-009",
        "severity": "medium",
        "title": "Sarraf SAR-147371 diamond color contradiction: G (specifications) vs H (description) (root F-043)",
        "detail": "The SAR-147371 page captured 2026-10-23 states 'Diamond Color: G' in its specifications and 'I1 in clarity and H in color' in its description. Neither color is published as confirmed on this dashboard.",
        "action": "Obtain written color confirmation from Sarraf before purchase; verify the stone independently on arrival.",
        "sources": [
            "%s",
        ],
    },
''' % (vrai_url, SAR147_URL)
i = bt.index("FLAGS = [")
j = bt.index("\n]\n", i)
bt = bt[:j] + "\n" + df_new.rstrip("\n") + bt[j:]
changes.append(f"text {B}: DF-008/DF-009 inserted")

# two new Sarraf dashboard rings after the SAR-145362 block
sar_new = '''    {
        "id": "SAR-151362",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "solitaire"],
        "name": "14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 9.20,
        "weight_note": "9.20 g metal-only (1.00 Ct. H/SI1 natural diamond separate; no band width stated)",
        "price_usd": 8203.00,
        "price_note": "Verified live 2026-10-23: explicit US$8,203.00 complete ring (was US$9,594.00).",
        "capture_date": VERIFIED_DATE,
        "product_url": "''' + SAR151_URL + '''",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 9.20 grams | Diamond Weight: 1.00 Ct. | Now: US$8,203.00",
        "flags": ["DF-004", "DF-007"],
    },
    {
        "id": "SAR-147371",
        "retailer_id": "sarraf",
        "retailer": "Sarraf Jewelry Inc.",
        "categories": ["solid-gold", "solitaire"],
        "name": "14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
        "karat": 14,
        "solid_gold_explicit": True,
        "hallmark_stated": False,
        "weight_g": 7.70,
        "weight_note": "7.70 g metal-only · ~10.0 mm wide (0.98 Ct. I1 natural diamond separate; color G vs H conflict — DF-009)",
        "price_usd": 4049.00,
        "price_note": "Verified live 2026-10-23: explicit US$4,049.00 complete ring (was US$4,736.00).",
        "capture_date": VERIFIED_DATE,
        "product_url": "''' + SAR147_URL + '''",
        "quote": "Material: 14K Solid Gold | Approximate Metal Weight: 7.70 grams | Diamond Weight: 0.98 Ct. | Now: US$4,049.00",
        "flags": ["DF-004", "DF-007", "DF-009"],
    },
'''
m = re.search(r'\{\n\s+"id": "SAR-145362".*?\n    \},\n', bt, re.S)
assert m
bt = bt[:m.end()] + sar_new + bt[m.end():]
bp.write_text(bt, encoding="utf-8")
changes.append(f"text {B}: SAR-151362/SAR-147371 rings inserted")

# ------------------------------------------------------------------- calc-test
per_g = 3995.47 / 31.1034768
sar_melt = 13.4 * 14 / 24 * per_g
sar_share = sar_melt / 1362 * 100
gem_melt = 0.976 * 14 / 24 * per_g
CT = "dashboard/scripts/calc-test.js"
sub(CT, "// 2. Live 2026-10-23 spot ($3,996.31/oz) across units & asking-price multiples",
    "// 2. Dated 2026-10-23 spot ($3,995.47/oz, latest WGC observation) across units & asking-price multiples", count=1)
sub(CT, "3996.31", "3995.47", min_count=10)
sub(CT, '"1 ozt == 20 dwt == $3,996.31 exact"', '"1 ozt == 20 dwt == $3,995.47 exact"', count=1)
sub(CT, f'"SAR-144773 13.40g 14K melt $1,004.32 & 73.74% gold share"',
    f'"SAR-144773 13.40g 14K melt ${sar_melt:,.2f} & {sar_share:.2f}% gold share"', count=1)
sub(CT, "Math.abs(sarBand.melt - 1004.319336) < 1e-3 && Math.abs(sarBand.goldSharePct - 73.7386) < 1e-2",
    f"Math.abs(sarBand.melt - {sar_melt:.6f}) < 1e-3 && Math.abs(sarBand.goldSharePct - {sar_share:.4f}) < 1e-2", count=1)
sub(CT, '"FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K ($73.15)"',
    f'"FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K (${gem_melt:.2f})"', count=1)
sub(CT, "Math.abs(gemDeduct.melt - 73.1477) < 1e-2",
    f"Math.abs(gemDeduct.melt - {gem_melt:.4f}) < 1e-2", count=1)

# dashboard verify.py session stamp
sub("dashboard/scripts/verify.py", "S-9B875C81", "S-C74095E5", min_count=1)

print("APPLIED:")
for c in changes:
    print(" -", c)
print(f"automic sources re-stamped: {n_automic}; fine-g = {fine_g:.4f}")
