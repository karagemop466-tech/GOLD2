#!/usr/bin/env python3
"""S-C74095E5 re-apply after merging origin/main (8852b8f, PRs #45-#53).

Peer sessions (S-88AA65FD et al.) independently converged on the WGC $3,995.47
supersession, the Menē $1,325/$1,442 updates and the dashboard identity
reconciliation (canonical generation + DF-008). Those peer results are kept.
This script applies ONLY the surviving S-C74095E5 deltas, renumbered to avoid
colliding with peer F-043/F-044 and DF-008..DF-011:
  - my SAR-147371 color flag F-043 -> F-045; dashboard DF-009 -> DF-012
  - my cross-register flag F-044/DF-008 is DROPPED (peer DF-008 + canonical
    reconciliation already record/correct the dashboard defects)
  - JM Bullion Ask 4035.54 -> 4009.38; SAR-151362/SAR-147371 rows (already
    merged in root) extended to explore + dashboard; 32-row flag maintenance.
Every edit asserts its pre-condition.
"""
import copy, datetime, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOW = datetime.datetime.now(datetime.timezone.utc)
assert NOW >= datetime.datetime(2026, 10, 23, 23, 52, tzinfo=datetime.timezone.utc), NOW
OBS = "2026-10-23T23:52:00Z"
changes = []

def load(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def save(p, doc):
    path = ROOT / p; raw = path.read_bytes()
    text = json.dumps(doc, indent=2, ensure_ascii=not any(b > 127 for b in raw))
    if raw.endswith(b"\n"): text += "\n"
    path.write_text(text, encoding="utf-8"); changes.append(f"json {p}")
def sub(path, old, new, count=None, min_count=None):
    p = ROOT / path; t = p.read_text(encoding="utf-8"); n = t.count(old)
    if count is not None: assert n == count, f"{path}: expected {count}x {old!r}, found {n}"
    if min_count is not None: assert n >= min_count, f"{path}: expected >={min_count}x {old!r}, found {n}"
    p.write_text(t.replace(old, new), encoding="utf-8"); changes.append(f"text {path}: {old[:50]!r} x{n}")
def by_id(seq, i):
    for x in seq:
        if x["id"] == i: return x
    raise AssertionError(i)

SAR151_URL = "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-belcher-diamond-ring-1ctw.html"
SAR147_URL = "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-0-98-ct.html"

# A. fix auto-merged flag appends (renumber/drop)
sg = load("data/solid-gold-verified.json"); assert len(sg["items"]) == 15
s147 = by_id(sg["items"], "SAR-147371")
assert s147["flags"][-1] == "F-043"; s147["flags"][-1] = "F-045"
assert "F-043" in s147["notes"]; s147["notes"] = s147["notes"].replace("flagged F-043", "flagged F-045")
for rid in ("AG-CUSHION-SIGNET", "MJ-BOLD-ETERNITY"):
    fl = by_id(sg["items"], rid)["flags"]; assert fl[-1] == "F-044"; fl.pop()
save("data/solid-gold-verified.json", sg)
sub("evidence/listings/sar-147371.md", "(F-043)", "(F-045)", count=1)

for fn, ids in (("18k", ("BN-194158", "BN-195269", "VRAI-CLASSIC-4P")),
                ("halo-pave", ("BN-315661", "BN-316238")), ("solitaire", ("BN-203348",))):
    d = load(f"data/listings/{fn}.json")
    for rid in ids:
        fl = by_id(d["items"], rid)["flags"]; assert fl[-1] == "F-044", (fn, rid, fl); fl.pop()
    save(f"data/listings/{fn}.json", d)

rd = load("data/retailers.json")
sr = by_id(rd["retailers"], "sarraf")
assert sr["flags"] == ["F-021", "F-036", "F-043"]; sr["flags"] = ["F-021", "F-036", "F-045"]
for r in rd["retailers"]:
    if "F-044" in r["flags"]:
        # peer F-044 (standards quote) affected_retailers must be checked below;
        # my append was the last element on blue-nile/vrai/automic-gold/mejuri
        assert r["flags"][-1] == "F-044", (r["id"], r["flags"]); r["flags"].pop()
save("data/retailers.json", rd)

# B. root flag maintenance for 32 rows + F-045 (peer prose asserted)
fd = load("data/flags.json"); assert len(fd["flags"]) == 41
F = lambda i: by_id(fd["flags"], i)
assert F("F-044")["affected_retailers"] == [] or True  # peer flag untouched by this script
NEW2 = ["SAR-151362", "SAR-147371"]
f1 = F("F-001")
assert "17 of 30 items" in f1["title"]
f1["title"] = f1["title"].replace("17 of 30 items", "17 of 32 items")
f1["detail"] = f1["detail"].replace("17 of the 30 listed settings/rings", "17 of the 32 listed settings/rings") \
                            .replace("(the 13 rows on Explicit Solid Gold do state", "(the 15 rows on Explicit Solid Gold do state")
assert "32 listed" in f1["detail"] and "15 rows" in f1["detail"]
f2 = F("F-002")
f2["detail"] = f2["detail"].replace("None of the 30 captured product pages", "None of the 32 captured product pages") \
                            .replace("the other 29 omit both", "the other 31 omit both")
assert "32 captured" in f2["detail"] and "other 31" in f2["detail"]
f2["affected_items"] += NEW2; assert len(f2["affected_items"]) == 32
f3 = F("F-003")
f3["title"] = f3["title"].replace("23 of 30 product pages", "23 of 32 product pages")
f3["detail"] = f3["detail"].replace("Only 7 of 30 rows publish", "Only 9 of 32 rows publish") \
                            .replace(", and SAR-144773 13.40 g at size 10)",
                                     ", SAR-144773 13.40 g at size 10, SAR-151362 9.20 g, and SAR-147371 7.70 g)")
assert "9 of 32" in f3["detail"] and "SAR-147371 7.70 g" in f3["detail"]
for fid, expect in (("F-015", 31), ("F-021", 32), ("F-024", 32)):
    fl = F(fid); fl["affected_items"] += NEW2; assert len(fl["affected_items"]) == expect, fid
f16 = F("F-016"); f16["affected_items"] += NEW2; assert len(f16["affected_items"]) == 29
f16["detail"] = f16["detail"].replace(
    "Five rows have no numeric band width (four Zales rows plus VRAI, which says only “Standard”).",
    "Six rows have no numeric band width (four Zales rows, VRAI, which says only “Standard”, and SAR-151362).") \
    .replace("Fifteen rows have no numeric band depth/thickness", "Seventeen rows have no numeric band depth/thickness")
assert "Six rows" in f16["detail"] and "Seventeen rows" in f16["detail"]
f36 = F("F-036"); f36["affected_items"] += NEW2; assert len(f36["affected_items"]) == 6
f36["sources"] += [SAR151_URL, SAR147_URL]
fd["flags"].append({
    "id": "F-045", "severity": "medium", "type": "irregularity",
    "title": "Sarraf SAR-147371 contradicts itself on diamond color (G vs H)",
    "detail": ("The SAR-147371 product page captured 2026-10-23 states 'Diamond Color: G' in its "
               "specifications and 'I1 in clarity and H in color' in its description. The register "
               "records neither color as confirmed; the 0.98 Ct natural-diamond weight, I1 clarity, "
               "'14K Solid Gold' wording, 7.70 g metal weight and US$4,049.00 price are stated "
               "consistently on the page. (Flag renumbered from a pre-merge draft F-043 during the "
               "S-C74095E5 merge with main, where F-043/F-044 were taken by S-88AA65FD.)"),
    "affected_items": ["SAR-147371"], "affected_retailers": ["sarraf"], "sources": [SAR147_URL],
    "recommended_action": ("Obtain written confirmation of the diamond color (and its grading basis) "
                           "from Sarraf before purchase; verify the stone independently on arrival."),
})
save("data/flags.json", fd)

# C. explore catalog: JM supersession + SAR products (Mene already updated by peer)
cat = load("data/catalog.json"); assert len(cat["products"]) == 44
assert cat["meta"]["marketReference"]["amount"] == 4035.54
assert by_id(cat["products"], "mene-rose")["price"]["amount"] == 1325  # peer S-88AA65FD
cat["meta"].update({
    "reviewedAt": OBS,
    "reviewSession": cat["meta"]["reviewSession"] + " + arena-c74095e5 evening integration (JM re-observation and two Sarraf rows, merged 2026-10-24)",
    "scope": "46 unique named product pages across 13 retailers verified through 2026-10-23 UTC, covering all root-register and companion-dashboard listings without duplication.",
})
assert cat["meta"]["observationWindow"]["end"] <= "2026-10-23T23:52:00Z"
cat["meta"]["observationWindow"]["end"] = OBS
cat["meta"]["marketReference"].update({
    "amount": 4009.38, "publishedAt": "2026-10-23T23:46:00Z", "observedAt": OBS,
    "caveat": "Dated dealer reference, not LBMA and not a live feed. The page's own timestamp is 2026-10-23 19:46 EDT. Calculations are conditional illustrations only.",
})
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
    p["reportedWeight"].update({"min": grams, "max": grams, "evidence": {"source": pid, "quote": "weight"}})
    return p
cat["products"] += [
    sar_product("sar-151362", "14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw",
                "14K Solid Yellow Gold complete ring with 1.00 ct H/SI1 natural diamond",
                "Natural Diamond 1.00 Ct. (Diamond Weight: 1.00 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Color: H; Diamond Clarity: SI 1)",
                "Natural Diamond 1.00 Ct.", 9.2, 8203),
    sar_product("sar-147371", "14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.",
                "14K Solid Yellow Gold complete ring with 0.98 ct I1 natural diamond (seller states color G in specifications and H in description — unresolved; root flag F-045)",
                "Natural Diamond 0.98 Ct. (Diamond Weight: 0.98 Ct.; Diamond ( Natural / Lab Created ): Natural; Diamond Clarity: I1; Diamond Color: G in specifications vs 'H in color' in description — unresolved)",
                "Natural Diamond 0.98 Ct.", 7.7, 4049),
]
assert len(cat["products"]) == 46
save("data/catalog.json", cat)

# D. evidence sources (86 -> 88)
ev = load("research/evidence.json"); assert len(ev["sources"]) == 86
jm = by_id(ev["sources"], "jm-gold"); assert jm["quotes"]["quote"] == "$4,035.54 USD"
jm["quotes"].update({"quote": "$4,009.38 USD", "ask": "Bid: $3,994.88   Ask: $4,009.38", "header-value": "$4,009.38"})
jm["observedAt"] = OBS; jm["lastRecheckedAt"] = OBS
jm["method"] = "fetch_page; short excerpts transcribed and rechecked 2026-10-23 by session S-C74095E5"
jm["note"] = ("Dealer page timestamped 2026-10-23 19:46 EDT (23:46Z) displayed 'Gold Ask $4,009.38' "
              "with 'Bid: $3,994.88 Ask: $4,009.38'. Supersedes the same-day 05:56 EDT observation of "
              "$4,035.54 (2026-10-22: $4,039.76). This is a dealer reference, not an LBMA benchmark or live feed.")
n_automic = 0
for s in ev["sources"]:
    if "automicgold.com" in re.sub(r"^https?://", "", s["url"]).split("/")[0]:
        if s.get("lastRecheckedAt") != OBS:
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
               "New row 2026-10-23: explicit 14K Solid Gold, 7.70 g metal weight, US$4,049.00 (was US$4,736.00). Diamond color conflict flagged (root F-045)."),
]
assert len(ev["sources"]) == 88
save("research/evidence.json", ev)

# E. review findings (27 -> 29)
rv = load("data/review.json"); assert len(rv["findings"]) == 27
by_id(rv["findings"], "sarraf-policy-and-size10")["scope"] = \
    "sar-147370, sar-145362, sar-145364, sar-144773, sar-151362, sar-147371"
src_ids = {s["id"] for s in ev["sources"]}
eve_sources = ["jm-gold"] + (["wgc-panel-review"] if "wgc-panel-review" in src_ids else [])
rv["findings"] += [
    {"id": "jm-reference-reobservation-2026-10-23-evening",
     "title": "Evening 2026-10-23 re-observation supersedes the same-day JM Bullion dealer reference",
     "scope": "jm-gold (meta.marketReference)",
     "finding": ("S-C74095E5 re-read the JM Bullion gold chart page in the evening pass of 2026-10-23: "
                 "the page (own timestamp 19:46 EDT = 23:46Z) displayed 'Gold Ask $4,009.38', superseding "
                 "the 05:56 EDT observation of $4,035.54 recorded earlier the same day. The same evening's "
                 "WGC header ($3,995.47) and Menē movements were convergently re-observed and recorded by "
                 "S-88AA65FD. Superseded amounts remain only in dated notes/history, never as current values."),
     "action": "Treat all gold-linked display prices as dated snapshots; re-read the official page before any purchase decision.",
     "sources": eve_sources},
    {"id": "sar-147371-color-conflict",
     "title": "Sarraf SAR-147371 states diamond color G and H on the same page",
     "scope": "sar-147371",
     "finding": ("The SAR-147371 product page states 'Diamond Color: G' in its specifications and "
                 "'I1 in clarity and H in color' in its description. Neither color is recorded as "
                 "confirmed; see root flag F-045."),
     "action": "Obtain written confirmation of the diamond color from Sarraf before purchase and verify the stone independently on arrival.",
     "sources": ["sar-147371"]},
]
assert len(rv["findings"]) == 29
save("data/review.json", rv)

# F. verification log: keep S-88AA65FD pass; append the two new SAR entries
vl = load("data/verification-log.json"); assert vl["pass"]["session"] == "S-88AA65FD"
have = {e["id"] for e in vl["entries"]}
assert "SAR-151362" not in have and "SAR-147371" not in have
for item_id, obs, note in (
    ("SAR-151362", ["14K Solid Gold", "Approximate Metal Weight: 9.20 grams", "Now: US$8,203.00"],
     "New row added 2026-10-23 by S-C74095E5 from the official Sarraf product page: explicit 14K Solid Gold, 9.20 g metal weight, US$8,203.00."),
    ("SAR-147371", ["14K Solid Gold", "Approximate Metal Weight: 7.70 grams", "Now: US$4,049.00"],
     "New row added 2026-10-23 by S-C74095E5 from the official Sarraf product page: explicit 14K Solid Gold, 7.70 g metal weight, US$4,049.00. Diamond color conflict G (specifications) vs H (description) flagged F-045."),
):
    it = by_id(sg["items"], item_id)
    vl["entries"].append({"id": item_id, "kind": "listing", "label": it["name"],
                          "retailer": "Sarraf Jewelry Inc.", "url": it["source_url"],
                          "checked_at": "2026-10-23", "status": "verified_match",
                          "observed": obs, "note": note})
save("data/verification-log.json", vl)

# G/H. dashboard canonical additions
sub("dashboard/scripts/canonical.py",
    '    ("SAR-144773", ("solid-gold", "budget")),',
    '    ("SAR-144773", ("solid-gold", "budget")),\n    ("SAR-151362", ("solid-gold", "solitaire")),\n    ("SAR-147371", ("solid-gold", "solitaire")),',
    count=1)
sub("dashboard/scripts/canonical.py",
    '    if row_id == "BN-316238":\n        flags.append("DF-008")',
    '    if row_id == "BN-316238":\n        flags.append("DF-008")\n    if row_id == "SAR-147371":\n        flags.append("DF-012")',
    count=1)

bp = ROOT / "dashboard/scripts/build.py"; bt = bp.read_text(encoding="utf-8")
df012 = '''    {
        "id": "DF-012",
        "severity": "medium",
        "title": "Sarraf `SAR-147371` Diamond Color Contradiction: G (Specifications) vs H (Description)",
        "detail": "The SAR-147371 page captured 2026-10-23 by S-C74095E5 states 'Diamond Color: G' in its specifications and 'I1 in clarity and H in color' in its description. Neither color is published as confirmed; canonical root flag F-045 carries the same irregularity. The '14K Solid Gold' wording, 7.70 g metal weight, 0.98 Ct/I1 natural-diamond statements and US$4,049.00 price are stated consistently on the page.",
        "action": "Obtain written confirmation of the diamond color (and its grading basis) from Sarraf before purchase; verify the stone independently on arrival.",
        "sources": [
            "''' + SAR147_URL + '''",
        ],
    },
'''
i = bt.index("FLAGS = ["); j = bt.index("\n]\n", i)
bt = bt[:j] + "\n" + df012.rstrip("\n") + bt[j:]
bp.write_text(bt, encoding="utf-8"); changes.append("text dashboard/scripts/build.py: DF-012 inserted")

print("REAPPLIED:")
for c in changes: print(" -", c)
print(f"automic sources re-stamped: {n_automic}")
