#!/usr/bin/env python3
"""S-C74095E5 independent scanner: re-derives integration invariants from the
data files and generated HTML without importing any project checker.
Exit 0 only if every check passes."""
import json, pathlib, re, sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = pathlib.Path(__file__).resolve().parents[2]
fails = []
def chk(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond: fails.append(name)
def L(p): return json.loads((ROOT / p).read_text(encoding="utf-8"))
def T(p): return (ROOT / p).read_text(encoding="utf-8")
norm = lambda s: " ".join(str(s).split()).lower()

items = []
for fn in ("18k","budget","halo-pave","solitaire","three-stone-vintage"):
    items += L(f"data/listings/{fn}.json")["items"]
sg = L("data/solid-gold-verified.json")["items"]; items += sg
flags = L("data/flags.json")["flags"]
rets = L("data/retailers.json")["retailers"]
vl = L("data/verification-log.json")
gp = L("data/gold-price.json")
cat = L("data/catalog.json"); ev = L("research/evidence.json"); rv = L("data/review.json")
drings = L("dashboard/data/rings.json")
dflags = L("dashboard/data/flags.json") if (ROOT/"dashboard/data/flags.json").exists() else None
byid = lambda seq: {x["id"]: x for x in seq}
I, F, R, P, S, D = byid(items), byid(flags), byid(rets), byid(cat["products"]), byid(ev["sources"]), byid(drings if isinstance(drings, list) else drings["rings"])

# S1 counts & identity sets
chk("S1 root items = 32 (17 category + 15 solid-gold)", len(items) == 32 and len(sg) == 15, f"{len(items)}/{len(sg)}")
want_flags = {f"F-{i:03d}" for i in range(1, 46)} - {"F-012", "F-032", "F-040"}  # merged state: peer F-043/F-044 + my F-045
chk("S1 flags = 42, F-001..F-045 minus F-012/F-032/F-040", set(F) == want_flags, str(sorted(set(F) ^ want_flags)))
chk("S1 verification listing entries == root item ids",
    {e["id"] for e in vl["entries"] if e["kind"] == "listing"} == set(I))
chk("S1 explore 46/88/29", len(cat["products"]) == 46 and len(ev["sources"]) == 88 and len(rv["findings"]) == 29)
chk("S1 dashboard rings = 28", len(D) == 28, str(len(D)))
if dflags is not None:
    dl = dflags if isinstance(dflags, list) else dflags.get("flags", [])
    chk("S1 dashboard flags DF-001..DF-012", {f["id"] for f in dl} == {f"DF-{i:03d}" for i in range(1, 13)})

# S2 gold supersession
chk("S2 current gold = 3995.47", gp["usd_per_troy_oz"] == 3995.47)
chk("S2 superseded set", {o["value"] for o in gp["superseded_observations"]} == {4028.53, 4024.36, 4024.45, 3996.31})
chk("S2 JM reference = 4009.38 @2026-10-23T23:46Z",
    cat["meta"]["marketReference"]["amount"] == 4009.38 and cat["meta"]["marketReference"]["publishedAt"] == "2026-10-23T23:46:00Z")
chk("S2 Menē explore amounts", P["mene-rose"]["price"]["amount"] == 1325 and P["mene-knot"]["price"]["amount"] == 1442)
chk("S2 Menē dashboard amounts", D["MENE-ROSE"]["price_usd"] == 1325 and D["MENE-KNOT"]["price_usd"] == 1442)
chk("S2 dashboard BNx5 + MJ prices blank",
    all(D[b]["price_usd"] is None for b in ("BN-194158","BN-195269","BN-316238","BN-315661","BN-203348","MJ-BOLD-ETERNITY")))
root_html = " ".join(T(p) for p in ["index.html","prices.html","verification.html","analysis.html","flags.html"] if (ROOT/p).exists())
chk("S2 no superseded gold literal in root HTML", "3,996.31" not in root_html and "4,024.45" not in root_html)

# S3 new rows end-to-end
for rid, price, grams in (("SAR-151362", 8203.0, 9.2), ("SAR-147371", 4049.0, 7.7)):
    it = I[rid]
    chk(f"S3 {rid} root fields", it["price"] == price and it["weight_g"] == grams and it["currency"] == "USD"
        and it["solid_gold_explicit"] is True and it["physical_test_status"] == "not_tested")
    evt = norm(T(it["evidence_file"]))
    chk(f"S3 {rid} every field_evidence quote in evidence file",
        all(norm(q) in evt for qs in it["field_evidence"].values() for q in qs))
    pid = rid.lower(); pr = P[pid]; src = S[pr["source"]]
    chk(f"S3 {rid} explore product/source", pr["price"]["amount"] == price and src["url"] == it["source_url"]
        and "solid gold" in src["quotes"]["material"].lower()
        and str(int(price)) in src["quotes"]["price"].replace(",", ""))
    chk(f"S3 {rid} dashboard row", D[rid]["price_usd"] == price and D[rid]["weight_g"] == grams)
chk("S3 SAR-147371 carries F-045 + DF-012, color unconfirmed in scope",
    "F-045" in I["SAR-147371"]["flags"] and "DF-012" in D["SAR-147371"]["flags"] and "unresolved" in P["sar-147371"]["scope"])

# S4 flag arithmetic & bidirectionality (independent reimplementation)
chk("S4 F-001 affected == items without explicit solid wording",
    set(F["F-001"]["affected_items"]) == {i["id"] for i in items if i["solid_gold_explicit"] is not True})
chk("S4 F-003 affected == items with null weight (23)",
    set(F["F-003"]["affected_items"]) == {i["id"] for i in items if i["weight_g"] is None} and len(F["F-003"]["affected_items"]) == 23)
chk("S4 F-002/F-021/F-024 cover all 32", all(len(F[f]["affected_items"]) == 32 for f in ("F-002","F-021","F-024")))
bi = all((fid in it["flags"]) == (it["id"] in F[fid]["affected_items"]) for fid in F for it in items)
chk("S4 item<->flag bidirectionality (32x42)", bi)
br = all((fid in r["flags"]) == (r["id"] in F[fid]["affected_retailers"]) for fid in F for r in rets)
chk("S4 retailer<->flag bidirectionality", br)

# S5 cross-register identity for the corrected rows
# canonical generation: dashboard rows are derived from root rows, so name+URL must equal root exactly
ok5 = all(D[b]["product_url"] == I[b]["source_url"] and D[b]["name"] == I[b]["name"]
          for b in ("BN-194158","BN-195269","BN-316238","BN-315661","BN-203348"))
chk("S5 dashboard BN rows == root canonical (name+URL)", ok5)
chk("S5 dashboard AG/MJ/VRAI URLs == root",
    all(D[r]["product_url"] == I[r]["source_url"] for r in ("AG-CUSHION-SIGNET","MJ-BOLD-ETERNITY","VRAI-CLASSIC-4P")))
explore_urls = {s["url"] for s in ev["sources"]}
chk("S5 every root URL in explore sources", all(i["source_url"] in explore_urls for i in items))

# S6 derived melt spot-checks (Decimal, HALF_UP, from current gold only)
spot = Decimal("3995.47"); per_g = spot / Decimal("31.1034768")
prices = T("prices.html")
bad = []
for i in items:
    if i["weight_g"] and i["karat"]:
        fine = (Decimal(str(i["weight_g"])) * Decimal(i["karat"]) / 24).quantize(Decimal("0.001"), ROUND_HALF_UP)
        melt = (fine * per_g).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if f"{fine:.3f}" not in prices and f"{melt:,.2f}" not in prices:
            bad.append(i["id"])
chk("S6 derived fine-g/melt present in prices.html for weighted rows", not bad, str(bad))

# S7 README truthfulness
readme = T("README.md")
chk("S7 README current counts/values",
    all(s in readme for s in ("46 product records","32-row","88 source records","29 review findings",
                              "`42` bidirectional flags","4,009.38","19 rows carry","F-045"))
    and "44 product records" not in readme and "30 product entries" not in readme)

# S8 zero approvals everywhere
chk("S8 no physical test / permission claimed in root",
    all(i["physical_test_status"] == "not_tested" and i["independent_test_permission"] is not True for i in items))

# S9 dead-slug remnants purged from builder + generated dashboard
dead = ["lab-grown-cushion-diamond-signet-ring","bold-lab-grown-diamond-eternity-ring","41383090421853",
        "petite-solitaire-engagement-ring-in-18k-yellow-gold-item-194158",
        "classic-four-prong-solitaire-engagement-ring-in-18k-rose-gold-item-195269",
        # NB: petite-micropave-...-item-316238 is NOT dead — it is the root-canonical
        # BN-316238 URL (F-041: slug retained, live title corrected). Excluded on purpose.
        "french-pave-halo-engagement-ring-in-14k-white-gold-1-5-ct-tw-item-315661",
        "three-stone-trellis-engagement-ring-in-14k-yellow-gold-item-203348"]
hay = T("dashboard/scripts/build.py") + T("dashboard/scripts/canonical.py")
for hp in pathlib.Path(ROOT/"dashboard").glob("*.html"): hay += hp.read_text(encoding="utf-8")
for jp in pathlib.Path(ROOT/"dashboard/data").glob("*.json"): hay += jp.read_text(encoding="utf-8")
chk("S9 no dead slugs in dashboard builder/output", not [d for d in dead if d in hay],
    str([d for d in dead if d in hay]))

# S10 F-031 deliberately not propagated
chk("S10 F-031 not on new SAR rows; affected still 10",
    "F-031" not in I["SAR-151362"]["flags"] and "F-031" not in I["SAR-147371"]["flags"]
    and len(F["F-031"]["affected_items"]) == 10)

print(f"independent scanner: {'PASS' if not fails else 'FAIL ' + str(fails)}")
sys.exit(1 if fails else 0)
