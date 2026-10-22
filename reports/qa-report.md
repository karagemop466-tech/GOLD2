# QA / hallucination audit

- Generated: 2026-10-22 23:47 UTC
- Items audited: 16 · flags: 17 · evidence quotes checked: 83
- **RESULT: PASS** — 11 checks, 0 failures, 2 warnings

## Checks

| # | Check | Result | Findings |
|---|-------|--------|----------|
| 1 | JSON schema & unique ids | ✅ PASS | 0 |
| 2 | Stored excerpts match evidence files (not a truth certificate) (83 quotes) | ✅ PASS | 0 |
| 3 | Price / weight / width / karat backed by quotes | ✅ PASS | 0 |
| 4 | Source links point at the seller's own domain | ✅ PASS | 0 |
| 5 | Blank values are covered by an explicit flag | ✅ PASS | 0 |
| 6 | Cached/contradictory values are rejected, not published | ✅ PASS | 0 |
| 7 | Flag definitions are complete and consistent | ✅ PASS | 0 |
| 8 | Price vs melt sanity check | ✅ PASS | 0 |
| 9 | Every table row carries an official source link (16 rows) | ✅ PASS | 0 |
| 10 | Built site: no broken internal links (370 links, 84 external) | ✅ PASS | 0 |
| 11 | Coverage summary | ✅ PASS | 0 |

## Failures

- none

## Warnings

- [coverage] 15 of 16 rows have no verified price
- [coverage] 15 of 16 rows have no published gram weight

## What this audit proves, and what it does not

It checks selected stored-excerpt/numeric consistency and publisher URLs, with specific null-coverage rules. It does not check every claim, prove the retailer told the truth, or replace professional assessment or an appraisal after delivery.

**Run this again after every review pass.** A stale table is the most likely way a wrong number enters this project.