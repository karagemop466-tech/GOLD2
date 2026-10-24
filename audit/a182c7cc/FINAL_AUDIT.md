# S-A182C7CC — final research, QA and security report

**Review date:** 2026-10-23 UTC for official seller/WGC observations. Automated final checks ran in a clean scratch copy after data integration. This is a dated research snapshot, not a live quote, purchase recommendation, physical test, or certificate of truth.

> **No hallucinations. No invented prices. Look for hallucinations again after every review.** A passing automated control proves only that its stated checks passed.

## Executive summary

- Re-opened all **17** assigned-price product rows at their official seller pages. **15 matched** their saved amounts; Menē Rose changed from `$1,336` to **`$1,325 USD`**, and Menē Knot from `$1,454` to **`$1,442 USD`**. The earlier values remain dated in evidence history. See [`live_price_verification_2026-10-23.md`](live_price_verification_2026-10-23.md) for product-by-product source links and exact configuration limits.
- The other **27 of 44** combined-catalog prices remain blank. No displayed string was converted, averaged, inferred from a neighboring item, or assigned to an unconfirmed currency.
- The WGC page’s moving header displayed **`$3,995.47 USD/ozt`** on 2026-10-23. The same page separately said **“Data as of 22 October, 2026.”** The header quote-as-of timestamp remains unknown; `quote_date` is deliberately `null` (F-026). No chart date or retrieval date was substituted for a quote timestamp.
- Automated source/provenance/security/build/calculator checks found **no passing-control failures** in the final snapshot. The known exceptions are non-blocking coverage/freshness warnings listed below; these are preserved for review rather than suppressed.
- **No physical ring, hallmark, purity, or scale/XRF test was performed. No purchase was approved.** Seller statements about metal, marks, mass, returns and payment remain separate claims; a karat stamp alone does not prove purity.

## Integration and review corrections

1. Updated the two Menē assigned prices only after direct official-page reads; preserved their same-day superseded observations. Other 15 assigned-price amounts matched.
2. Kept the WGC moving-header quote date null. Updated the README’s chart-date description to match the direct page text (“Data as of 22 October, 2026”) and corrected a historical JSON note that had named a quote already superseded by the later stored observation.
3. An earlier build rendered the superseded WGC amount in the Explore review prose. The finding now refers readers to the gold-price history instead of repeating that amount as page copy. The exact old quote and date remain in `data/gold-price.json` and `evidence/gold-price.md`; current rendered pages do not present it as current.
4. Root QA initially rejected the two Menē verification entries because its official-host allowlist omitted the directly verified canonical `mene.com` host. After checking the coordination board, added only that official host to `tools/qa.py` under A182-05. Root QA then passed with its three expected warnings.
5. Built and tested in `/tmp/gold2-a182c7cc-final`. Only A182-claimed generated outputs were copied back. **`data/flags.json`, `flags.html`, and all `dashboard/**` files were excluded**; their active peer scope was not touched.

## Build, evidence and calculator checks

| Check | Result |
|---|---|
| `npm run check` | **PASS.** Evidence consistency: 44 products, 85 source records, 26 findings, zero purchase approvals; 23/23 Node tests; deterministic 13-page Explore build; 46 HTML pages / 102 local targets / 179 external publisher URLs (external HTTP status not certified); static security over 46 pages, 6 runtime files, 104 source files and 4 pinned workflows; `npm audit` found 0 vulnerabilities; browser pass covered 13 expanded + 33 companion/root/preserved pages, desktop/mobile, all 44 automatic gates, filters, conditional and gemstone calculators, stale warning, no-JavaScript research and zero external runtime requests. Automated axe found no WCAG A/AA violations in the exercised states. |
| `python3 tools/build_site.py` + `python3 tools/qa.py` | **PASS: 12 checks, 0 failures, 3 warnings.** Generated 13 root pages. The warnings are F-026 (unknown WGC header timestamp), 20/30 root rows with no assigned price, and 23/30 with no published metal weight. |
| `node tools/test_calculator.js` | **PASS.** Formula, dated VRAI case, asking-price comparisons, blank/invalid inputs, negative difference and formatting. |
| `python3 reviews/independent_snapshot_audit.py .` | **0 findings; 12 arithmetic controls passed.** It cannot replace source retrieval or physical inspection. |
| A182 independent provenance scanner | **PASS.** 44 products; 17 source/currency-linked assigned prices; 27 blanks; WGC `quote_date` null; 18 official-source verification entries resolve. Its five mutation tests all passed, including tests that reject invented prices, filling a blank, inventing a WGC quote date, and partial timestamp placeholders. |
| Preserved legacy `scripts/build.py`, `scripts/audit.py`, `node scripts/test.js` | **PASS.** Six legacy pages / two records; links, evidence, blank unknowns and static checks pass. The legacy audit still openly reports missing product evidence and a gold quote; its synthetic-input calculator tests pass. |

## Independent scanner results

| Audit | Final result | Notes |
|---|---|---|
| S-1B04074F | **0 failures, 2 warnings** | Warnings: `flags.html` does not display the combined catalog’s `$3,995.47` spot and `explore/calculator/index.html` mentions a spot input/link without auto-filling a reference. `flags.html` remained outside this session’s edit/copy scope. The Explore calculator deliberately has no invented fallback: its reference is user-entered and dated. 25 helper/arithmetic controls passed. |
| S-E0D6DD62 | **12 checks, 0 failures, 0 warnings** | Six mutation tests passed. Superseded WGC values do not appear in rendered HTML; gold JSON/evidence, counts, arithmetic, links and page placeholders agree. |
| S-A87A02A5 | **995 controls, 0 failures, 4 warnings** | Four Zales rows show discount/original-price-like text while their assigned `price` remains blank (F-018). That is the correct no-inference state, but a reader could mistake the text for a confirmed price; retain for manual review. Its mutation suite caught 9/9 defects. |
| S-B200A880 | **4,306 controls, 0 failures, 0 warnings** | Its 22 scanner/math tests passed. |
| S-9B875C81 | **2,009 controls, 0 findings** | Its four calculator/scanner tests passed. |
| S-8C810C15 | **220 controls, 0 findings** | Six calculator/scanner tests passed. |
| S-A182C7CC | **PASS** | Five purpose-built mutation controls passed against the final snapshot. |

A historical warning-count inconsistency in an earlier A87 report remains unresolved; this run’s read-only scanner is the current result (four warnings), and no historical count is treated as current.

## Items that remain open for manual verification

1. **WGC timestamp (F-026):** the page does not bind a quote-as-of time to its moving header. The chart date remains separate. The stored amount is a dated observation, not a live price.
2. **Date-only price freshness:** the fetch tool does not expose request seconds, so seller-price observations are stored at date precision. The final evidence verifier ran just after the UTC date boundary and conservatively emitted **17 “price older than 24h” warnings** for those 17 rows because date-only values parse at midnight. This is a precision/freshness limitation, not a claim that the pages were not re-opened in this review. The observations remain dated and must be re-opened before a purchase; no artificial timestamp was added.
3. **Coverage:** 27 combined-catalog prices remain blank; 20/30 root prices and 23/30 root metal weights remain unassigned/unpublished. These blanks and their flags are intentional.
4. **Displayed but unassigned Zales amounts:** four rows retain seller display text but no assigned price/currency; review the exact selector/price role and currency before assigning any value.
5. **Physical authenticity:** no actual ring was obtained, weighed, tested, or inspected. Solid-gold wording, fineness, hallmark, maker mark, component weights, return/inspection permission, seller identity, payment method and policies still need their own evidence and, where appropriate, independent checks.
6. **Source access:** the evidence verifier still reports one unavailable Auvere source and one partially accessed Brilliant Earth context source. These were not converted into facts.

**Recommended next action:** re-open the exact official listing and terms immediately before purchase, obtain a size/configuration-specific quote, confirm the paired karat and maker marks plus metal-only weight, obtain independent inspection permission and qualifying return terms, and rerun source/provenance/security checks after any further review. Do not buy if independent verification and a qualifying return are disallowed.

**Look for hallucinations again after every review.** No automated pass can prove a seller page is truthful, a product will match its listing, a price will remain available, a ring is actually the stated purity, or a return will be honored.
