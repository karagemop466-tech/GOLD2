#!/usr/bin/env python3
"""S-88AA65FD — apply the 2026-10-23 late-evening live re-verification.

Every change here is backed by a value read from the official page during this session and
recorded in audit/88aa65fd/verification_2026-10-23.md. Nothing is inferred, averaged or
converted. The script is idempotent: re-running it is a no-op once applied.

What it changes
  1. WGC gold reference 3,996.31 -> 3,995.47 (moving header re-read at 2026-10-23T23:41Z);
     the old value becomes a superseded observation and is never used by the calculator.
  2. Menē Rose 1,336 -> 1,325 and Knot 1,454 -> 1,442 (official pages re-read 23:46-23:47Z),
     with the prior amounts retained as superseded display observations.
  3. Removes a fabricated verbatim quote ("an item marked 18 k is made of 75 % gold") from the
     karat basis. It appears on neither 16 CFR 23.3 nor the FTC consumer page; the FTC sentence
     it was paraphrasing is stored verbatim instead, and the 75 % figure is labelled arithmetic.
  4. Adds the eCFR source record that the gold reference cited but never stored.
  5. Publishes two new flags: F-043 (Factory Direct founding-year self-contradiction) and
     F-044 (the misattributed quote), plus one review finding on explore/review.
  6. Refreshes the root verification log for the four root rows re-read now and rewrites the
     pass metadata so the not-re-read scope is stated on the page.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBSERVED_AT = "2026-10-23T23:41:00Z"
MENE_OBSERVED_AT = "2026-10-23T23:46:00Z"
RUN_DATE = "2026-10-23"

SPOT_OLD, SPOT_NEW = "3,996.31", "3,995.47"
FTC_18K = ("A piece of jewelry marked 18K gold is 18 parts gold mixed with six parts of another metal.")
FTC_URL = "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry"
ECFR_URL = "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3"
FDJ_URL = "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text and old not in text:
        return text            # already applied
    assert old in text, f"pattern not found ({label}): {old[:70]!r}"
    return text.replace(old, new, 1)


# ---------------------------------------------------------------- 1. gold reference
def gold_reference() -> None:
    path = ROOT / "data" / "gold-price.json"
    gold = load(path)
    if gold["usd_per_troy_oz"] != 3995.47:
        assert gold["usd_per_troy_oz"] == 3996.31, "unexpected prior gold value"
        gold["usd_per_troy_oz"] = 3995.47
        gold["retrieved_at"] = RUN_DATE
        gold["evidence_quotes"] = ["3,995.47", "Data as of 22 October, 2026"]
        gold["field_evidence"]["usd_per_troy_oz"] = ["USD\n\n/oz\n\n-\n\n3,995.47"]
        gold["quote_scope"] = (
            "Moving-header observation retrieved 2026-10-23T23:41Z; exact quote-as-of timestamp is "
            "unconfirmed (F-026). The chart's stated date (22 October 2026) is stored separately and is not "
            "assigned to the header."
        )
        superseded = gold.setdefault("superseded_observations", [])
        if not any(o.get("value") == 3996.31 for o in superseded):
            superseded.append({
                "value": 3996.31,
                "currency": "USD",
                "quote_date": None,
                "retrieved_at": RUN_DATE,
                "chart_as_of_date": "2026-10-22",
                "status": "superseded_moving_header",
                "reason": "Header value observed earlier the same day (2026-10-23T20:00Z). The moving header "
                          "is not a fixed benchmark; only the later 2026-10-23T23:41Z observation (3,995.47) "
                          "is used in calculations.",
            })
    # the fabricated verbatim quote is replaced by two quotes that are actually on 16 CFR 23.3
    gold["field_evidence"]["karat_basis"] = [
        "fine (24 karat) gold",
        "composed throughout of an alloy of gold (i.e., gold that is less than 24 karats)",
    ]
    gold["karat_basis"] = (
        "Nominal karat/24 arithmetic for a documented gold-alloy weight. The percentage is arithmetic on the "
        "listed karat, not a quoted percentage and not an assay. 16 CFR 23.3 (read 2026-10-23) distinguishes "
        "fine 24-karat gold, gold alloys and surface coatings; the FTC consumer page states the karat parts in "
        "words ('18 parts gold mixed with six parts of another metal')."
    )
    save(path, gold)


# ---------------------------------------------------------------- 2. evidence markdown
def gold_evidence_md() -> None:
    path = ROOT / "evidence" / "gold-price.md"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "**Retrieved:** 2026-10-23 (UTC). This is the later of two direct fetches of the same page on that day.",
        "**Retrieved:** 2026-10-23T23:41Z (UTC). This is the latest direct fetch of the same page on that day; "
        "every earlier reading of the moving header is kept only in the dated history table below.",
        "gold retrieved line",
    )
    text = replace_once(text, "\n3,996.31\nLast Updated", "\n3,995.47\nLast Updated", "gold value block")
    # history table: add the reading this pass superseded
    history_anchor = (
        "| Value (USD/oz) | Retrieved | Chart date on that page | Status | Why it is not current |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    assert history_anchor in text, "gold history table header missing"
    if "| 3,996.31 | 2026-10-23T20:00Z |" not in text:
        text = text.replace(
            history_anchor,
            history_anchor
            + "| 3,996.31 | 2026-10-23T20:00Z | 2026-10-22 | `superseded_moving_header` | Earlier same-day "
              "fetch of the same moving header. A later fetch at 23:41Z rendered 3,995.47 with the same chart "
              "date. |\n",
            1,
        )
    # karat basis: remove the fabricated quote and re-attribute the real one
    old_section = (
        "### `karat_basis` — NIST conversion chart\n\n"
        "```\n"
        "an item marked 18 k is made of 75 % gold\n"
        "```\n"
    )
    new_section = (
        "### `karat_basis` — FTC consumer guidance (verbatim)\n\n"
        f"**URL:** {FTC_URL}\n\n"
        "```\n"
        f"{FTC_18K}\n"
        "```\n\n"
        "The `75 %` the calculator uses for 18K is `18 / 24` arithmetic on that sentence. It is not a quoted\n"
        "percentage and it appears on neither the FTC page nor 16 CFR 23.3 as written. A previous revision of\n"
        "this file presented `an item marked 18 k is made of 75 % gold` as a verbatim NIST/eCFR excerpt; both\n"
        "pages were re-read on 2026-10-23 and neither contains that sentence, so it was removed rather than\n"
        "restated. Published as F-044.\n"
    )
    if old_section in text:
        text = text.replace(old_section, new_section, 1)
    text = replace_once(
        text,
        "the single current observation is now 3,996.31 from the later same-day fetch",
        "the single current observation is now 3,995.47 from the 2026-10-23T23:41Z fetch",
        "revision note value",
    )
    text += (
        "\n## Revision note — 2026-10-23T23:4xZ (S-88AA65FD)\n\n"
        "A later direct fetch of the same World Gold Council page rendered **3,995.47** with the chart still\n"
        "dated 22 October 2026, so the current observation moved forward and 3,996.31 was added to the dated\n"
        "history table. The `karat_basis` section was corrected: a sentence that had been presented as a\n"
        "verbatim NIST/eCFR quote appears on neither page and was replaced by the FTC sentence it paraphrased,\n"
        "with the 75 % figure labelled as arithmetic. Both changes are published as F-044.\n"
    )
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- 3. combined evidence json
def combined_evidence() -> None:
    path = ROOT / "research" / "evidence.json"
    data = load(path)
    by_id = {s["id"]: s for s in data["sources"]}

    wgc = by_id["wgc-panel-review"]
    wgc["observedAt"] = OBSERVED_AT
    wgc["lastRecheckedAt"] = OBSERVED_AT
    wgc["note"] = (
        "Moving header read 3,995.47 USD/oz on the 2026-10-23T23:41Z re-read. Earlier same-day readings are "
        "retained only inside data/gold-price.json as superseded observations and are not rendered as current "
        "values anywhere. The page's data blocks were dated 22 October, 2026. The header carries no quote-as-of "
        "timestamp, so chart metadata is stored separately and not bound to the header."
    )
    wgc["quotes"]["header"] = f"Gold Spot price USD /oz - {SPOT_NEW}"
    wgc["quotes"]["quote"] = SPOT_NEW

    for pid, amount, prior in (("mene-rose", 1325, 1336), ("mene-knot", 1442, 1454)):
        rec = by_id[pid]
        rec["observedAt"] = MENE_OBSERVED_AT
        rec["lastRecheckedAt"] = MENE_OBSERVED_AT
        rec["quotes"]["price"] = f"${amount:,}"
        rec["supersededDisplay"] = {
            "amount": prior,
            "currency": "USD",
            "observedAt": "2026-10-23T10:00:00Z",
            "reason": "Earlier same-day observation of the same official page. The page is repriced from metal "
                      "value, so only the later observation is current; the earlier amount is kept as dated "
                      "history and is never averaged with the new one.",
        }
        rec["note"] = (
            f"Direct official-product fetch on {MENE_OBSERVED_AT} rendered ${amount:,} USD on the page's default "
            f"size display; the 2026-10-23T10:00Z observation was ${prior:,}. Menē prices these Crafted-on-Demand "
            "pieces from metal value, so the earlier amount is superseded, not additive. Sizes are sold by weight; "
            "no gram weight is published for this piece."
        )

    # eCFR record: cited by the gold reference but never stored as provenance until now.
    if "ecfr-23-3" not in by_id:
        ecfr = {
            "id": "ecfr-23-3",
            "publisher": "Federal Trade Commission — 16 CFR Part 23 (eCFR, Office of the Federal Register)",
            "kind": "government",
            "url": ECFR_URL,
            "observedAt": "2026-10-23T23:48:00Z",
            "method": "fetch_page; section text read in full on 2026-10-23 by session S-88AA65FD",
            "access": "fetched",
            "note": (
                "Page banner on retrieval: 'up to date as of 10/21/2026'; 'Title 16 was last amended 10/19/2026'. "
                "Section 23.3(a)-(d) and its footnotes were read. The sentence previously stored in "
                "data/gold-price.json as a quotation of this section — 'an item marked 18 k is made of 75 % gold' — "
                "does not appear here; the omission is published as F-044."
            ),
            "quotes": {
                "unfair": "It is unfair or deceptive to misrepresent the presence of gold or gold alloy in an industry product",
                "fine-24k": "fine (24 karat) gold",
                "alloy": "composed throughout of an alloy of gold (i.e., gold that is less than 24 karats)",
                "solid-hollow": "Such products should not be marked or described as \"solid\" or as being solidly of gold or of a gold alloy.",
                "tolerance": "articles or parts made of gold or of gold alloy that contain no solder have a permissible tolerance of three parts per thousand",
            },
        }
        data["sources"].append(ecfr)
    data["meta"]["recordedAt"] = data["meta"].get("recordedAt") or OBSERVED_AT
    save(path, data)


# ---------------------------------------------------------------- 4. catalog
def catalog() -> None:
    path = ROOT / "data" / "catalog.json"
    data = load(path)
    for product in data["products"]:
        if product["id"] == "mene-rose":
            product["price"]["amount"] = 1325
            product["price"]["observedAt"] = MENE_OBSERVED_AT
            product["observedAt"] = MENE_OBSERVED_AT
        elif product["id"] == "mene-knot":
            product["price"]["amount"] = 1442
            product["price"]["observedAt"] = MENE_OBSERVED_AT
            product["observedAt"] = MENE_OBSERVED_AT
    data["meta"]["reviewedAt"] = "2026-10-23T23:50:00Z"
    data["meta"]["reviewSession"] = (
        "arena-88aa65fd late-evening re-verification on base records built by earlier sessions"
    )
    data["meta"]["observationWindow"]["end"] = "2026-10-23T23:50:00Z"
    save(path, data)


# ---------------------------------------------------------------- 5. flags + review finding
def flags_and_findings() -> None:
    path = ROOT / "data" / "flags.json"
    data = load(path)
    ids = {f["id"] for f in data["flags"]}
    if "F-043" not in ids:
        data["flags"].append({
            "id": "F-043",
            "severity": "low",
            "type": "irregularity",
            "title": "Factory Direct Jewelry states two different founding years on the same product page",
            "detail": (
                "The captured product page says 'Handcrafted in our Los Angeles factory since 1985' in its "
                "U.S.-made panel and 'We've been making jewelry in our Los Angeles factory since 1988' in its "
                "'From Our Factory To You' panel. Both sentences were read on 2026-10-23. The listing's price "
                "($1,299.99), stated weight (1.25 grams) and karat-stamp sentence are unaffected by this "
                "discrepancy, and no founding year is used anywhere in this register as a trust signal."
            ),
            "affected_items": [],
            "affected_retailers": [],
            "sources": [FDJ_URL],
            "recommended_action": (
                "Ask the seller in writing to confirm its founding year and its California manufacturing claims "
                "before relying on either. Treat a self-contradicting page as a documentation-quality signal, "
                "not as proof of fraud."
            ),
        })
    if "F-044" not in ids:
        data["flags"].append({
            "id": "F-044",
            "severity": "medium",
            "type": "irregularity",
            "title": "A sentence published as a verbatim standards quote appears on neither cited page",
            "detail": (
                "data/gold-price.json stored 'an item marked 18 k is made of 75 % gold' as a field-scoped "
                "quotation of 16 CFR 23.3, and evidence/gold-price.md labelled it a NIST conversion-chart quote. "
                "Both the regulation and the FTC consumer page were re-read on 2026-10-23: the regulation "
                "contains no percentage sentence, and the FTC page states the karat parts in words (18 parts "
                "gold, six parts another metal). The 75 % is 18/24 arithmetic. The fabricated quotation was "
                "removed, the verified FTC sentence is stored instead, and the arithmetic is labelled as "
                "arithmetic. No stored gold value changed because of this correction."
            ),
            "affected_items": [],
            "affected_retailers": [],
            "sources": [ECFR_URL, FTC_URL],
            "recommended_action": (
                "Keep quoting only text that a dated fetch actually contains, and keep derived percentages "
                "labelled as derived. Hallucination scans should compare every quoted string against its own "
                "evidence file rather than trusting a quotation mark."
            ),
        })
    data["generated_at"] = RUN_DATE
    save(path, data)

    review_path = ROOT / "data" / "review.json"
    review = load(review_path)
    if not any(f["id"] == "karat-quote-provenance" for f in review["findings"]):
        review["findings"].append({
            "id": "karat-quote-provenance",
            "title": "A karat sentence was published as a verbatim quote from pages that do not contain it",
            "scope": "Gold reference — karat basis (16 CFR 23.3 and FTC consumer guidance)",
            "sources": ["ecfr-23-3", "ftc-jewelry"],
            "finding": (
                "The stored karat basis carried 'an item marked 18 k is made of 75 % gold' as a field-scoped "
                "excerpt attributed to the eCFR section and, in the evidence file, to the NIST conversion chart. "
                "On 2026-10-23 both the regulation and the FTC article were re-read: the regulation contains no "
                "such sentence and the FTC article expresses the same fact in parts ('18 parts gold mixed with "
                "six parts of another metal'), which makes 75 % arithmetic rather than a quotation. The sentence "
                "was removed and replaced with verified text; the arithmetic stays, clearly labelled."
            ),
            "action": (
                "Quote only text present in a dated fetch, and label derived percentages as derived. Re-run a "
                "string-matching hallucination scan after every review — a plausible quotation is exactly what "
                "an unchecked pipeline propagates."
            ),
        })
    save(review_path, review)


# ---------------------------------------------------------------- 6. root verification log
def verification_log() -> None:
    path = ROOT / "data" / "verification-log.json"
    data = load(path)
    data["pass"] = {
        "session": "S-88AA65FD",
        "checked_at": RUN_DATE,
        "timezone": "UTC",
        "method": (
            "Independent re-read on 2026-10-23T23:41-23:49Z of nine official URLs: the World Gold Council spot "
            "page, both Automic Gold product JSON documents, Sarraf 147370, Factory Direct GR0001, both Menē "
            "rings, 16 CFR 23.3 and the FTC consumer article. The four root rows re-read are updated below; the "
            "other root rows were NOT re-read in this pass and keep their earlier dated result."
        ),
        "rule": (
            "A stored value is reused only if the official page rendered it again during the pass that recorded "
            "it. Rows not re-read this pass keep their earlier checked_at. No value is inferred, averaged, "
            "converted, or copied from a search snippet."
        ),
        "limits": (
            "A successful retrieval is not an assay, not a hallmark or maker's-mark check, and not proof of "
            "stock or future price. No ring was weighed or XRF-tested. Pages can change after this pass."
        ),
    }
    data["generated_at"] = RUN_DATE
    updates = {
        "AG-COFFIN-RING": {
            "status": "verified_match",
            "observed": ["$1,910", "price_max $2,233 (variant range, F-039)", "Approximately 6.1g (gold)"],
            "note": "Product JSON re-read 2026-10-23T23:42Z: price 191000, price_min 191000, price_max 223300 "
                    "cents — unchanged. The range top is still not attributed to a named variant.",
        },
        "AG-CUSHION-SIGNET": {
            "status": "verified_match",
            "observed": ["$2,758 (14k Yellow Gold / Salt and Pepper Diamond)", "price_min $2,408", "price_max $3,253",
                         "Approximate item weight: gold 5.5g"],
            "note": "Product JSON re-read 2026-10-23T23:43Z: price 240800, price_max 325300 cents; the default "
                    "variant rendered 275800. Unchanged.",
        },
        "SAR-147370": {
            "status": "verified_match",
            "observed": ["Now: US$3,004.00", "14K Solid Gold", "3.80 grams", "0.94 Ct. Natural"],
            "note": "Re-read 2026-10-23T23:44Z. 'Approximate Metal Weight' wording preserved: this is not a "
                    "scale-verified net gold weight.",
        },
        "FDJ-GR0001": {
            "status": "verified_match",
            "observed": ["$1,299.99", "Weight:1.25 Grams", "Karat stamped inside the band."],
            "note": "Re-read 2026-10-23T23:45Z. Price, weight and stamp sentence unchanged. The same page states "
                    "both 'since 1985' and 'since 1988' — published as F-043. The weight section also says weights "
                    "update after options are chosen, so 1.25 g remains a default-display figure.",
        },
        "GOLD-QUOTE": {
            "status": "verified_correction",
            "observed": ["3,995.47", "Data as of 22 October, 2026"],
            "note": "Re-read 2026-10-23T23:41Z. The moving header rendered 3,995.47; the earlier same-day "
                    "reading is now a superseded observation and is not used by the calculator. Quote time "
                    "remains unconfirmed (F-026).",
        },
    }
    for entry in data["entries"]:
        if entry["id"] in updates:
            entry.update(updates[entry["id"]])
            entry["checked_at"] = RUN_DATE
            entry["session"] = "S-88AA65FD"
    save(path, data)


# ---------------------------------------------------------------- 7. README prose
def readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "The combined register contains **44 unique product URLs across 13 sellers, 85 source records and 26 review findings**.",
        "The combined register contains **44 unique product URLs across 13 sellers, 86 source records and 27 review findings**.",
        "readme counts",
    )
    text = replace_once(
        text,
        "Menē Rose Ring moved $1,346 → $1,336 and Knot Ring $1,465 → $1,454.",
        "Menē Rose Ring moved $1,346 → $1,336 → $1,325 and Knot Ring $1,465 → $1,454 → $1,442, each step a dated observation on its own official page (the earlier amounts are superseded history, never averaged).",
        "readme mene",
    )
    text = replace_once(
        text,
        "before a later 2026-10-23 read showed **$3,996.31/oz** against a chart still stating 22 October 2026 (quote time still unconfirmed, F-026).",
        "before a late 2026-10-23 read (23:41Z) showed **$3,995.47/oz** against a chart still stating 22 October 2026 (quote time still unconfirmed, F-026).",
        "readme spot",
    )
    text = replace_once(
        text,
        "`39` bidirectional flags `F-001`–`F-042`",
        "`41` bidirectional flags `F-001`–`F-044`",
        "readme flag count",
    )
    text = replace_once(
        text,
        "Examples requiring review include",
        "- **41 flags now published.** Two were added on 2026-10-23 by the late S-88AA65FD pass: `F-043` "
        "(Factory Direct Jewelry states both a 1985 and a 1988 founding year on one page) and `F-044` (a karat "
        "sentence previously published as a verbatim standards quote appears on neither cited page; corrected, "
        "with the derived 75 % now labelled arithmetic).\n- **[Root category dashboard",
        "readme flags bullet",
    )
        "Two defects found in this late pass are published rather than smoothed: a sentence stored as a verbatim "
        "standards quote appears on neither cited page and was replaced with the verified FTC wording (F-044), "
        "and Factory Direct Jewelry's own page states two different founding years (F-043). Examples requiring "
        "review include",
        "readme findings",
    )
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- 8. dashboard generator
def dashboard_generator() -> None:
    path = ROOT / "dashboard" / "scripts" / "build.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('SPOT_USD = Decimal("3996.31")', 'SPOT_USD = Decimal("3995.47")')
    text = text.replace("3,996.31", "3,995.47").replace("3996.31", "3995.47")
    text = text.replace("128.48", "128.46")
    text = text.replace('"price_usd": 1336.00', '"price_usd": 1325.00')
    text = text.replace('"price_usd": 1454.00', '"price_usd": 1442.00')
    text = text.replace("Verified live 2026-10-23: $1,336.00 USD (updated from $1,346 on 2026-10-22 with spot drift).",
                        "Verified live 2026-10-23T23:46Z: $1,325.00 USD (earlier same-day $1,336 and 2026-10-22 $1,346 are superseded observations).")
    text = text.replace("Verified live 2026-10-23: $1,454.00 USD (updated from $1,465 on 2026-10-22 with spot drift).",
                        "Verified live 2026-10-23T23:47Z: $1,442.00 USD (earlier same-day $1,454 and 2026-10-22 $1,465 are superseded observations).")
    text = text.replace("$1,336\"", "$1,325\"").replace("$1,454\"", "$1,442\"")
    path.write_text(text, encoding="utf-8")

    calc_test = ROOT / "dashboard" / "scripts" / "calc-test.js"
    ct = calc_test.read_text(encoding="utf-8")
    ct = ct.replace("3996.31", "3995.47").replace("3,996.31", "3,995.47")
    calc_test.write_text(ct, encoding="utf-8")

    calc_js = ROOT / "dashboard" / "assets" / "calculator.js"
    if calc_js.exists():
        cj = calc_js.read_text(encoding="utf-8")
        cj = cj.replace("3996.31", "3995.47").replace("3,996.31", "3,995.47").replace("128.48", "128.46")
        calc_js.write_text(cj, encoding="utf-8")


def source_hosts() -> None:
    path = ROOT / "scripts" / "lib.mjs"
    text = path.read_text(encoding="utf-8")
    if "'www.ecfr.gov'" not in text:
        old = "'consumer.ftc.gov', 'www.gia.edu', 'www.nist.gov',"
        assert old in text, "SOURCE_HOSTS anchor missing"
        text = text.replace(old, "'consumer.ftc.gov', 'www.ecfr.gov', 'www.gia.edu', 'www.nist.gov',", 1)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    gold_reference()
    gold_evidence_md()
    combined_evidence()
    catalog()
    flags_and_findings()
    verification_log()
    readme()
    dashboard_generator()
    source_hosts()
    print("applied S-88AA65FD verification updates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
