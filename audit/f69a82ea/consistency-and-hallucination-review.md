# S-F69A82EA — consistency and hallucination review

**Date:** 2026-10-23 UTC  
**Branch:** `arena/f69a82ea-gold2`  
**Scope:** correct stale README counts; accurately disclose a known cross-register completeness gap; publish it in the generated Flagged for Review page; rerun repository verification. This is not a physical product authentication or a full live re-fetch of every retailer page.

## Findings and changes

1. **Stale README counts** — corrected the combined catalog from 32 entries / 9 sellers / 60 sources / 20 findings to the current local data-derived counts: 41 product records, 12 sellers, 80 source records, 26 findings. Corrected root register prose to 30 entries, 9 product sellers and 36 flags; the full static check set scans 46 published HTML pages and all 41 automatic valuation gates. These counts are from the repository datasets and test output, not live retailer claims.
2. **Catalog completeness claim** — an independent provenance scan identified `AG-COFFIN-RING`, `AG-CUSHION-SIGNET`, and `MJ-BOLD-ETERNITY` in the root register but absent from the 41-product Explore catalog. The previous catalog scope text incorrectly said it covered all root and companion listings. Corrected that metadata and the README to state the gap plainly; did not silently fabricate combined product records.
3. **Published flag** — added `root-only-products-not-in-combined-register` to `data/review.json`, linked to the three official product pages, and rebuilt the Explore review/source pages. The finding is about project coverage only, not a claim about product quality. The root register remains available separately.
4. **Official page identity re-reads** — retrieved each exact official product page with `fetch_page` and recorded only identity/link evidence (plus Mejuri's verbatim visible display text, with no currency assignment):
   - [Automic Gold Coffin Ring](https://www.automicgold.com/products/coffin-ring)
   - [Automic Gold Cushion Diamond Signet Ring](https://www.automicgold.com/products/cushion-diamond-signet-ring)
   - [Mejuri Bold Diamond Eternity Ring](https://mejuri.com/products/bold-diamond-eternity-ring)

No price, karat, purity, alloy-only weight, hallmark, maker's mark, or test result was newly assigned by this pass. For Mejuri, the official page displayed `From$2,900`; the currency remains unassigned.

## Verification performed

- `npm run verify` — PASS; 41 products, 80 sources, 26 findings, 0 purchase approvals; 69 non-blocking review warnings remain.
- `npm run build` — PASS; 13 Explore pages regenerated, 41 rows and 80 sources; unknown gold values remain blank.
- `npm run check:links` — PASS; 46 published pages, 102 local targets, 177 external publisher links; every product table row has an official publisher link. This checks URL structure/link presence, not external HTTP availability.
- `npm run check` — PASS: 23/23 Node tests, build determinism, security review, npm audit (0 vulnerabilities), browser checks across 46 pages/41 automatic valuation gates, no external runtime requests, and axe WCAG A/AA checks with no violations in exercised states.
- `python3 tools/qa.py` — PASS, 11 checks / 0 failures / 3 coverage warnings.
- `node tools/test_calculator.js` — PASS.
- `python3 reviews/independent_snapshot_audit.py .` — PASS, 0 findings / 12 arithmetic controls.
- Legacy `python3 scripts/build.py`, `python3 scripts/audit.py`, `node scripts/test.js` — PASS (the legacy audit explicitly reports missing product evidence and gold quote as open items).
- Four existing independent provenance/security scanners — PASS with no failures: provenance scanner 984 controls / 10 warnings; B200A880 4,220 controls / 0 warnings; S-9B875C81 1,979 controls / 0 findings; S-8C810C15 202 controls / 0 findings. The scanner warnings are retained, not waived.
- Four existing scanner/calculator unittest suites — PASS, 32 tests.
- `git diff --check` — PASS.

## Remaining flagged items and limits

- The 10 provenance-scan warnings comprise three source quotes not mirrored into JSON field-evidence (AG-CUSHION-SIGNET, AG-SAPPHIRE-RING, FDJ-GR0001) and four unassigned Zales display strings that a reader could mistake for price values. They remain disclosed and unaltered.
- Root QA still warns that the WGC header quote-as-of time is unconfirmed, that 20/30 root listings have no explicitly assigned current price, and that 23/30 have no published metal weight.
- The separate combined register is still not exhaustive. The three root-only entries are now explicitly linked and flagged; integrating them requires a separate source-backed product-record task.
- Automated verification establishes consistency and test behavior, not external truth, current checkout prices, a seller's reputation, actual physical purity, hallmark authenticity, scale weight, or XRF results. No purchase is approved.

**Standing recommendation:** look for hallucinations again after every review; re-open official sources for each material field before treating any observation as current.
