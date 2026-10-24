# Independent live re-verification — S-F03AB52D — 2026-10-23

Session `S-F03AB52D` (branch `arena/f03ab52d-gold2`). This is an **audit-only,
read-first** pass. It re-read a sample of published values directly from official
publisher pages and cross-checked every committed value against its own evidence
quote. It did **not** edit any data, evidence, generator, page or stylesheet.

Scope: `audit/f03ab52d/**` + the `COORDINATION.md` claim block. No peer file was
modified. All values below are transcribed exactly as retrieved.

## 1. Live official re-reads (2026-10-23)

| # | Item | Official URL | Live value read | Stored value | Verdict |
|---|------|--------------|-----------------|--------------|---------|
| 1 | World Gold Council gold spot header | https://www.gold.org/goldhub/data/gold-prices | `3,995.47` USD/oz, chart "Data as of 22 October, 2026" | `3,996.31` USD/oz at the time this session read the page (retrieved 2026-10-23) | **Moved, not a hallucination.** The header is a moving intraday quote. While this audit was in progress, `main` advanced and `S-1B04074F` (PR #45) refreshed the stored observation to the same `3,995.47` this session read live — the two independent reads agree. Quote-as-of timestamp still unconfirmed (F-026). |
| 2 | Mejuri Bold Diamond Eternity Ring | https://mejuri.com/products/bold-diamond-eternity-ring | `From$2,900`, `Solid White Gold (14k)`, `14k solid gold`, band `2.6 mm` | price unassigned `From $2,900`; solidGold true; karat 14 | **Confirmed.** |
| 3 | Automic Gold Coffin Ring (Shopify product JSON) | https://www.automicgold.com/products/coffin-ring.js | `"price":191000,"price_min":191000,"price_max":223300,"price_varies":true` | `$1,910` default; range to `$2,233` (F-039) | **Confirmed.** |
| 4 | Brilliant Earth Classic Six-Prong Solitaire (BE121H6) | https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/ | `$890(Setting Only)`, `14K Yellow Gold`, `Width: 2.5 mm`, `Prong metal: 14K White Gold`, USD selector | `$890` USD, kind `setting-only` | **Confirmed.** |

No live read contradicted a stored value. The only difference (row 1) is the normal
intraday movement of a moving spot header, which the project already treats as a
dated observation rather than a live feed.

## 2. What was NOT re-read this pass

The remaining 40 combined-catalog rows and 26 root-only rows were not individually
re-fetched in this pass. Their stored values were instead re-checked **against their
own evidence quotes** by the independent scanner (`hallucination_audit.py`, C2), which
verifies that every non-null value appears in the quote the record cites. That is a
provenance check, not a re-fetch; it does not certify that a seller's page still reads
the same today. The not-re-read list is the same coverage gap the project already
discloses (root QA warns that 20 of 30 root rows carry no assigned price and 23 of 30
no published metal weight).

## 3. Independent scanner result

`audit/f03ab52d/hallucination_audit.py` — 9 checks, written from scratch (it does not
import `tools/qa.py`, `scripts/verify.mjs` or any other session's scanner):

| Check | Result |
|-------|--------|
| C1 catalog product sources exist and are official https | PASS |
| C2 every non-null fact value and price amount is in its evidence quote | PASS |
| C3 root register: official https source_url + existing evidence file | PASS |
| C4 root <-> catalog URL parity (price/weight) — 30 pairs | PASS |
| C5 gold reference JSON matches evidence, no unrecorded figure | PASS (one documented non-observational mention exempt: 4,025.54) |
| C6 derived / assay fields null unless explicitly evidenced | PASS |
| C7 no hallmark / maker-mark claim without evidence | PASS |
| C8 generated HTML renders headline gold value + product count | PASS |
| C9 review findings cite at least one source | PASS |

**Result: PASS — 9 checks, 0 failures, 0 warnings.**

Mutation controls (`test_audit.py`) inject one defect at a time into a temp copy and
assert the scanner fails the right check: **9/9 behaved as expected** (invented price,
karat mismatch, unbacked solidGold, non-https source, unrecorded gold figure, gold-JSON
mismatch, unbacked hallmark, root/catalog price conflict, unbacked derived value).

## 4. Irregularities / flags raised by this pass

- **F-026 (carried forward, not resolved):** the WGC header renders no quote-as-of
  timestamp; the chart date is stored separately and is not assigned to the header.
- **Fresh-observation note (not a defect):** the live WGC header read `3,995.47` on this
  pass against the stored `3,996.31`. Both are same-day (2026-10-23) readings of a moving
  quote. Recommend a **dated** refresh by the integration session; do not silently overwrite
  the stored observation.
- **Documented non-observational mention:** `evidence/gold-price.md` line 131 mentions
  `4,025.54` only to state that no such figure exists in any data file. The scanner
  exempts it; it is recorded here so it is not mistaken for an observation.
- **Coverage gaps (disclosed, non-blocking):** 20 of 30 root rows have no assigned price;
  23 of 30 have no published metal weight; zero rows have independent physical/XRF/scale
  verification; zero purchase approvals.

## 5. Boundary

Automated PASS proves only that the stated controls passed. It cannot prove a seller's
claim is true, that a page still reads the same tomorrow, or that any ring is actually
the purity stamped on it. Re-open primary sources and look for hallucinations again after
every review.
