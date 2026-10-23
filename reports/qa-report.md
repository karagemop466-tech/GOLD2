# QA / hallucination and integration audit

- Generated: 2026-10-23 10:33:22 UTC
- Items audited: 20 · retailers: 6 · flags: 31 · field-scoped quotes: 369
- **RESULT: PASS** — 11 checks, 0 failures, 3 warnings

## Checks

| # | Check | Result | Findings |
|---|-------|--------|----------|
| 1 | JSON schema, item-scoped records, unique IDs, and dates | ✅ PASS | 0 |
| 2 | Field-scoped verbatim quotes resolve in their own files (369 quotes) | ✅ PASS | 0 |
| 3 | Item name, SKU, metal, dimensions, price, basis, and scope match field quotes | ✅ PASS | 0 |
| 4 | Retailer policy, payment, contact, and independent metrics are field-backed | ✅ PASS | 0 |
| 5 | Official product/policy domains and independent-source URLs are constrained | ✅ PASS | 0 |
| 6 | Blank states are flagged and item/retailer flag references are bidirectional | ✅ PASS | 0 |
| 7 | Rejected snippets and superseded gold quotes are not current values | ✅ PASS | 0 |
| 8 | Nominal fine-gold and melt calculations use current constants | ✅ PASS | 0 |
| 9 | Built pages: row/source identity, CSP, small-text contrast, internal destinations/fragments, and external URL structure (1106 link occurrences, 308 external). External retrieval is documented separately; future availability is not guaranteed. | ✅ PASS | 0 |
| 10 | Coverage limitations remain visible | ✅ PASS | 0 |
| 11 | Dated verification log, analysis arithmetic, and derived shell counts (29 logged records) | ✅ PASS | 0 |

## Failures

- none

## Warnings

- [gold] Header quote-as-of is unconfirmed; chart/retrieval dates are not substituted (F-026)
- [coverage] 16 of 20 rows have no explicitly assigned current price (F-008/F-018/F-025)
- [coverage] 18 of 20 rows have no published metal weight (F-003)

## What this audit proves, and what it does not

It checks internal consistency: published fields resolve to field-specific quotes in each subject's own evidence file; blank states are flagged; product/policy domains are constrained; generated rows carry their exact official URLs; calculations use the dated constants; and internal links/fragments and browser-security constraints hold.
It does **not** prove that a retailer is truthful, that a physical ring matches its listing, that BBB allegations are established, or that an external URL will remain available. External sources were directly fetched during research and the dated inventory is in `reports/source-link-review.md`; this local structural audit is not a live network monitor. No physical inspection or XRF assay was performed.
**Look for hallucinations again after every review.** Re-read the official source and generated page after every edit. A PASS is a guardrail, never a guarantee of factual truth.
