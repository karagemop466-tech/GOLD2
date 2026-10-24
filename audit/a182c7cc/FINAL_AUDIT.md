# S-A182C7CC — final research, QA and security report

**Review date:** official seller and WGC observations were retrieved on **2026-10-23 UTC**. The integrated main snapshot was checked in a clean scratch tree on **2026-10-24 UTC** (evidence verifier timestamp `2026-10-24T00:37:55Z`). This is a dated research record, not a live quote, appraisal, purchase recommendation, physical test, or certificate of truth.

> **No hallucinations. No invented prices. Look for hallucinations again after every review.** A passing automated control proves only that its stated checks passed.

## Executive summary

- A182 re-opened all **17 product rows that had assigned prices** at their official seller pages. **15 matched**; Menē Rose changed from `$1,336` to **`$1,325 USD`** and Menē Knot from `$1,454` to **`$1,442 USD`**. Earlier amounts are preserved as dated history. Product-by-product URLs, captured text and limits are in [`live_price_verification_2026-10-23.md`](live_price_verification_2026-10-23.md).
- After the separately audited S-C74095E5 changes merged in PR #55, the combined catalog contains **46 products, 88 source records and 29 review findings**: **19 assigned prices and 27 blank prices**. A182 re-read the original 17 rows; C740 added two separately source-verified Sarraf rows. No blank was inferred, converted, averaged, or filled.
- The WGC moving header displayed **`$3,995.47 USD/ozt`** on 2026-10-23; the chart separately said **“Data as of 22 October, 2026.”** The quote-as-of time remains unknown, and `quote_date` remains `null` (F-026). This is a dated observation, not a current quote.
- The integrated front page keeps **“No hallucinations. No invented prices.”** prominent; the combined site retains its category pages, official-source-linked rows, conditional calculator and purchase checklist. Build, link, security, browser and accessibility checks passed as listed below.
- **No ring was obtained, weighed, physically inspected, hallmark-checked, XRF-tested or otherwise purity-tested. No purchase was approved.** Seller claims about gold content, marks, weight, returns and payment remain distinct and unverified claims; a karat stamp alone is not proof of purity.

## Integration and evidence decisions

1. Kept `origin/main`'s PR #55 work intact, including the two new Sarraf rows and the peer's independent verification/audit files. A182's 17-row price history is identified separately; the two additional Sarraf rows are attributed to [`audit/c74095e5/live_verification_2026-10-23.md`](../c74095e5/live_verification_2026-10-23.md).
2. Merged the 18 unique A182 verification-log entries (17 product-price snapshots plus one WGC snapshot) into the newer 41-entry main log, yielding 59 entries. The latest source set remains 88 records. Earlier Menē values are retained in both dated history and source quotes.
3. Advanced seven Automic price `observedAt` dates from 2026-10-22 to date-only `2026-10-23` because A182 directly re-read those pages and the fetch tool supplies no request seconds. Existing precise same-day observation times from the peer data were preserved; no request time was fabricated.
4. Updated the three dated review narratives for WGC, Menē and the 17-row follow-up, corrected the stale chart-date description to 22 October 2026, and added this audit path and the A182 follow-up to the README. The WGC moving-header timestamp remains blank.
5. Regenerated the Explore output, root `verification.html` and `reports/qa-report.md` from the combined data in scratch. **A182 did not edit or copy `data/flags.json`, `flags.html`, or any `dashboard/**` output.** Their peer changes arrived through the already-merged main history and were preserved as-is.

## Build, evidence, calculator and site checks

| Check | Result |
|---|---|
| `npm run check` | **PASS.** Evidence consistency: 46 products, 88 sources, 29 findings, zero purchase approvals; 23/23 Node tests; deterministic 13-page Explore build; link check: 46 pages, 104 local targets, 148 external publisher URLs (external HTTP status not certified); static security: 46 HTML pages, 6 runtime files, 106 source files and 4 pinned workflows; `npm audit`: 0 vulnerabilities; desktop/mobile Chromium and axe pass across 13 expanded plus 33 companion/root/preserved pages, all 46 automatic valuation gates, filters, conditional and gemstone calculators, stale warning and no-JavaScript research. No WCAG A/AA violations were found in the exercised states. |
| `npm run verify` (included in the above) | **PASS**, with **82 non-blocking review warnings**. Seven date-only Automic observations parse as older than 24 hours just after the UTC date boundary; this is a precision warning, not evidence that the pages were not re-opened. Other warnings preserve unknown prices, missing weights, marks/testing/return evidence and source-access limitations. No time was invented. |
| `python3 tools/build_site.py` + `python3 tools/qa.py` | **PASS: 12 checks, 0 failures, 3 warnings.** Generated 13 root pages. Warnings: F-026 (unknown WGC header timestamp), 20/32 root rows without an assigned price, and 23/32 without a published metal weight. |
| `node tools/test_calculator.js` | **PASS.** Formula, dated VRAI case, asking-price comparison, blank/invalid inputs, negative difference and formatting. |
| `python3 reviews/independent_snapshot_audit.py .` | **0 findings; 14 arithmetic controls passed.** This does not replace source retrieval or physical inspection. |
| A182 independent provenance scanner | **PASS.** Current combined catalog: 46 products, 19 assigned-price rows and 27 blanks. All 17 A182 rows resolve to official source/currency evidence and date-matched verification snapshots; Menē history is retained; WGC `quote_date` stays null; all **5/5** mutation controls passed. The scanner checks current added prices for source/currency provenance without retroactively claiming A182 re-read them. |
| Preserved legacy `scripts/build.py`, `scripts/audit.py`, `node scripts/test.js` | **PASS.** Six legacy pages / two legacy records and synthetic-input calculator tests pass. The legacy audit openly reports its missing product evidence and gold quote; those gaps are not silently presented as resolved. |
| C740 independent scanner | **PASS** on the merged 32-row root / 46-product combined / 42-flag snapshot, including row-to-source coverage and the current WGC reference. |

## Independent scanner and mutation-suite results

These are read-only reruns against the integrated snapshot. No other session's audit folder was edited.

| Audit | Result | Notes |
|---|---|---|
| S-88AA65FD | **PASS** | 19 assigned prices, 46 products, 42 flags, current source links and dated Menē amounts internally resolve. |
| S-8C810C15 | **PASS: 230 controls, 0 findings** | Six calculator/scanner tests passed. |
| S-9B875C81 | **PASS: 3,025 controls, 0 findings** | Four calculator/scanner tests passed. |
| S-B200A880 | **PASS: 4,516 controls, 0 findings/warnings** | 25 helper/arithmetic controls passed. |
| S-C74095E5 | **PASS** | Its post-merge cross-register scanner passed; the report and evidence remain in `audit/c74095e5/**`. |
| S-E0D6DD62 | Scanner **PASS: 12/0/0**; mutation suite **7/8** | One mutation expectation did not detect its injected defect on the expanded 32-row baseline; the scanner itself passes. This is recorded, not repaired in the peer-owned folder. |
| S-F03AB52D | **PASS: 9 checks, 0 findings** | 9/9 mutation controls passed. |
| S-F3B0B698 | **PASS** | Companion audit passed; 20/20 mutation tests passed. |
| S-FE7BA040 | Scanner **PASS: 7 families, 0 failures**; mutation suite **9/10** | The flag-count mutation was not detected by the test suite. |
| S-1B04074F | **1 failure, 2 warnings**; mutation suite **8/9** | C13 retains a pre-expansion 30-row literal while the current root register and README correctly contain 32 rows. Warnings: the peer-owned `flags.html` and the user-entered Explore calculator do not auto-display the WGC value. The stale count is a known scanner change request recorded in C740's integration log. |
| S-86379CA7 | **1 hard failure, 6 advisory warnings**; mutation baseline fails | Check 3 hardcodes 30 root items but the merged register has 32. Advisory findings include flag-scope/count and verification-label mismatches; see [`audit/86379ca7/FINDINGS.md`](../86379ca7/FINDINGS.md). Its owner already logged the stale-count change request. |
| S-A87A02A5 | **3 C18 failures, 5 warnings**; mutation baseline fails | The three “gold reference 4,049.00” failures are false positives: `$4,049.00` is SAR-147371's official **product asking price** in `solid-gold.html`, `prices.html` and the F-045 description—not a gold-reference quote. Warnings also note four Zales amounts correctly left unassigned and stale “of 16” prose in excluded `flags.html`. A182 made no edits or copies to flag/dashboard files; peer updates already on main were preserved. This run's false-positive result supersedes neither the peer's historical result nor its warning-count discrepancy. |

The stale-count and mutation-fixture failures are not hidden as green results. The third-party scanners remain separate from the passing CI/security gates; their findings and limits should be reviewed by their owners. Cross-register issues and the Sarraf color contradiction remain published for manual review rather than silently changing unsupported facts.

## Remaining manual verification and next pass

1. **WGC quote time (F-026):** the page does not bind a quote-as-of time to its moving header. The chart date is separate. The stored value is a dated display observation, not a live spot quote.
2. **Price freshness:** re-open each exact official listing immediately before purchase and obtain a size/configuration-specific all-in quote. The seven date-only Automic observations trigger conservative freshness warnings after the UTC date boundary; no artificial seconds were added.
3. **Coverage and displayed text:** 27 combined-catalog prices remain blank; 20/32 root prices and 23/32 root metal weights remain unassigned/unpublished. Four Zales rows retain displayed price-like text but no assigned price/currency. Keep the blanks; resolve only from a direct, official, configuration-specific source.
4. **Published irregularities:** consult the cross-register findings in `audit/86379ca7/FINDINGS.md` and the C740 live-verification report. In particular, the root flag-scope/count notes and the SAR-147371 G-vs-H color contradiction need owner/manual follow-up; the new Sarraf price, karat wording and weight are seller statements, not independent tests.
5. **Physical authenticity and purchase terms:** no actual ring was obtained, weighed or tested. Confirm explicit solid-gold wording, stated karat, paired karat and maker/manufacturer marks, gold-alloy-only grams excluding stones and other metals, inspection/testing permission, return deadline/fees, seller identity and payment protections as separate claims. A stamp alone does not prove purity.
6. **Source-access limits:** the evidence verifier still reports one unavailable Auvere source and one partially accessed Brilliant Earth context source. Neither was converted into a fact.

**Recommended next action:** re-open the exact official listing and terms before any purchase, obtain written confirmation of configuration-specific price and return/testing conditions, arrange independent professional weight and purity assessment, and run another source/provenance, hallucination and security pass after every subsequent review or edit. Do not buy if independent verification and a qualifying return are disallowed.

**Look for hallucinations again after every review.** No automated PASS proves seller truth, physical purity, availability, future pricing, complete accessibility/security, or that a return will be honored. GitHub Pages deployment/read-back for the A182 integration is recorded separately in the A182 block of `COORDINATION.md` after merge.
