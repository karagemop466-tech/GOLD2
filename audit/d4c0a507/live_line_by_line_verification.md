# S-D4C0A507 — independent live line-by-line verification

- **Session:** `S-D4C0A507` on fixed Arena branch `arena/d4c0a507-gold2`
- **Started from:** `main` @ `22d9f85` (merge of PR #21); working tree was clean and identical to `main`
- **Date:** 2026-10-23 (UTC)
- **Method:** every value below was re-read from the official page named in the row. A value that could not be
  re-read is reported as *not re-confirmed*; nothing was inferred, averaged, or filled in.
- **Scope:** root register (20 rows across 6 category pages), gold/calculation reference, and the evidence trail that
  backs each row.

## 1. Gold / calculation reference

| Field | Published before | Re-read from official source | Verdict |
| --- | --- | --- | --- |
| `usd_per_troy_oz` | 4,028.53 | **4,024.45** — WGC header `USD /oz - 4,024.45 Last Updated` | **Stale → refreshed** |
| `retrieved_at` | 2026-10-22 | 2026-10-23 (this retrieval) | Refreshed |
| `chart_as_of_date` | 2026-10-21 | `Data as of 22 October, 2026` | Refreshed |
| `quote_date` | `null` | still `null` — header as-of time unconfirmed (F-026) | Unchanged |
| `grams_per_troy_ounce` | 31.1034768 | NIST chart `31.103 476 8` | Confirmed |

Source: <https://www.gold.org/goldhub/data/gold-prices> ("Market Data: Provided by ICE Data Services").

The WGC header is a **moving** quote. Across two retrieval days it was observed at four distinct values
(4,024.36 and 4,028.53 on 2026-10-22, 4,025.54 later on 2026-10-22, 4,024.45 on 2026-10-23). All values except the
latest are retained only in `superseded_observations`; none is presented as current. This is a freshness refresh of the
existing dated-observation model, not a new inference.

## 2. Row-by-row re-verification (root register, 20 rows)

| Row | Official source | Values re-read 2026-10-23 | Verdict |
| --- | --- | --- | --- |
| AG-COFFIN-RING | <https://www.automicgold.com/products/coffin-ring> | `$1,910`; `Solid 14k Gold and 950 Platinum`; `Band is 3mm`; `Height Approximately 1.8mm - 2.3mm`; `Approximately 6.1g (gold) or 9.2g (platinum)` | **Match** |
| AG-CUSHION-SIGNET | <https://www.automicgold.com/products/cushion-diamond-signet-ring> | `$2,758`; `Solid 14k Gold and 950 Platinum`; `Band width is tapered from 8.5mm - 2.5mm`; `Approximate item weight: gold 5.5g, platinum 8.3g`; `Approximately 0.65ct` | **Match** |
| AG-SAPPHIRE-RING | <https://www.automicgold.com/products/sapphire-ring> | `$526`; `Solid 14k Gold and 950 Platinum`; `Band is 1.1mm`; `Height Approximately 1.1mm`; `Approximately 1.2g (gold) or 1.8g (platinum)`; `Natural sapphire` | **Match** |
| MJ-BOLD-ETERNITY | <https://mejuri.com/products/bold-diamond-eternity-ring> | `From$2,900`; `Solid White Gold (14k), Natural Diamond`; `handcrafted in 14k solid gold`; `14k solid white gold pieces are finished with rhodium plating`; `Band Width: 2.6 mm`; no gram weight | **Match** |
| BN-203348 | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-simple-solitaire-engagement-ring-in-14k-yellow-gold-item-203348> | `$1,145(Setting Price)`; stock `502120y14`; `14K Yellow Gold`; `Width 2.40mm` | **Match** |
| VRAI-CLASSIC-4P | <https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-32797281484893> | title `Classic Round Brilliant Engagement Ring \| Plain Band \| 18k Yellow Gold`; `Metal:18k Yellow Gold`; URL resolves (HTTP 200) | **Match** — page is JS-rendered; the size-6 `2.86 g` weight line could not be re-extracted from the markdown, so it is *not re-confirmed by this pass* and remains backed by the 2026-10-22 evidence file |
| Z-20301172 | <https://www.zales.com/13-ct-tw-diamond-three-stone-engagement-ring-10k-gold/p/V-20301172> | `Discounted Price $769.30  Original Price was $1,099.00 30% Off`; `Free and easy 30-day returns` | **Amounts now labeled** (see finding 3) |
| Z-20303279 | <https://www.zales.com/12-ct-tw-diamond-frame-vintagestyle-twist-shank-engagement-ring-10k-gold/p/V-20303279> | `Discounted Price $979.30  Original Price was $1,399.00 30% Off`; `Free and easy 30-day returns` | **Amounts now labeled** (see finding 3) |
| BE-121H6 | <https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/> | page loads; currency selector lists AUD/CAD/GBP/USD; the `€ 990.00 (Setting Only)` amount block is rendered dynamically and was **not** present in the extracted markdown | **Not re-confirmed by this pass** — 2026-10-22 evidence retained, flagged as a retrieval limitation |
| Remaining 10 Blue Nile / Zales rows | see `data/listings/*.json` `source_url` per row | not individually re-fetched in this pass; their field-evidence quotes were re-checked against their evidence files (see §3) | **Partially verified** |

Rows not individually re-fetched are **not** claimed as verified. Their backing evidence was re-checked mechanically.

## 3. Evidence-trail integrity (automated, all 20 rows)

For every item in `data/listings/*.json` and `data/solid-gold-verified.json`:

- `source_url` in the data equals the `Official product URL` in its evidence file — **0 mismatches**
- every `field_evidence[*]` quote appears verbatim in its evidence file — **0 missing quotes**

This checks that no published value is unsupported by its own evidence trail. It does **not** prove the official page is
true, and it does not replace live retrieval.

## 4. Findings and irregularities

> **Integration note (2026-10-23):** while this pass was running, a parallel session (`S-8B9E189A`,
> merged as PR #23 at `fee89f0`) re-read the same official pages and published corrections for the same items.
> The conflicts raised by rebasing onto `fee89f0` were resolved by **taking the merged PR #23 content** and keeping
> this session's independent audit record. Nothing from either session was discarded. Where PR #23 had already
> documented a finding more completely, its wording stands and this report points at it.

### F-D4-01 — Gold reference was one retrieval day stale (confirmed; corrected by PR #23)
The published reference (4,028.53, retrieved 2026-10-22) no longer matched the official page, which shows 4,024.45
with chart data as of 22 October 2026. **Both this session and PR #23 independently read 4,024.45 from the same
official URL.** PR #23's merged `data/gold-price.json` and `evidence/gold-price.md` were kept; the earlier value is in
`superseded_observations` and `quote_date` stays `null`. **No hallucination** — the number was read directly from the
official page.

### F-D4-02 — F-018 premise was unstable across renders (confirmed; corrected by PR #23)
F-018 originally stated that two Zales pages render *unlabeled* price amounts. My live read showed labeled amounts
(`Discounted Price … Original Price was … 30% Off`). PR #23's merged F-018 records the fuller finding: **label presence
is not stable between renders** — the same URL rendered with and without labels across two parallel sessions, and
Z-20046552 behaved the same way. That wording is more accurate than mine and stands. The amounts still remain
**unassigned**: they carry a bare dollar sign with no confirmed ISO currency (F-025 / F-033).

### F-D4-03 — Two values could not be re-confirmed by this pass (retrieval limitation, not a data change)
- VRAI `2.86 g (Ring size 6)` — the configurator renders specs client-side; not present in this pass's markdown
  extraction. PR #23 recorded it as confirmed unchanged on the same day, so it stands on that re-read.
- Brilliant Earth — the price block is rendered dynamically and was not present in this pass's extraction. PR #23
  corrected the row to **USD 890 (Setting Only)** from a rendered USD currency selector and added F-032.

### F-D4-04 — No hallucinations found in this pass
No published value contradicted its own evidence file, and no value was found to be unsupported. The remaining open
flags are evidence gaps and scope limitations, not invented values.

### F-D4-05 — Currency rule inconsistency in the inherited register (found by PR #23; retained)
The inherited register assigned `currency: USD` to Automic Gold and Mejuri rows on the same dollar-sign evidence it
treated as unconfirmed for Blue Nile and Zales. PR #23 removed that inconsistency (F-033) and applied one rule to every
row: an assigned price now requires an official currency statement. This pass concurs — inferring USD from a bare
dollar sign is exactly the unsupported value this project forbids.

## 5. Checks run after the edits (all passing)

| Check | Result |
| --- | --- |
| `python3 tools/build_site.py` | 13 pages built; reproducible (no diff on rebuild) |
| `python3 tools/qa.py` | **PASS — 11 checks, 0 failures, 3 warnings** |
| `node tools/test_calculator.js` | PASS |
| `python3 reviews/independent_snapshot_audit.py .` | PASS — 0 findings, 6 arithmetic controls |
| `node --test tests/*.test.mjs` | 23/23 pass |
| `node scripts/check-links.mjs` | PASS — 30 pages, 71 local targets, 102 external publisher URLs |
| `python3 scripts/audit.py` | PASS |

## 6. Recommendation

Keep looking for hallucinations after every review. Re-open the official source, re-read the row, and treat the official
page as current if this table becomes stale. The 3 warnings (unconfirmed header quote time, 15/20 rows without an
assigned price, 18/20 rows without a published metal weight) are coverage gaps, not verification failures.
