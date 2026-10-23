# Audit — Session S-305FDD02 (2026-10-23 UTC)

Independent live re-verification and integration pass over the GOLD2 repository.

**Headline:** every one of the 30 root-register rows was re-read from its own official product
URL in this session. 29 rendered the stored values. One URL (`BN-316238`) now serves a different
product, which is published as **F-041/F-042** rather than quietly "fixed". The World Gold
Council header was re-read twice and moved again, so the gold reference was refreshed to the
latest observation and every derived number on all three dashboards was recomputed.

## Files

- `live_verification.md` — the line-by-line record: each row, the URL read, the verbatim text
  seen, whether it matched the stored value, and what was changed as a result.
- `../data/flags.json` — the published flag register (now `F-001`–`F-042`), rendered on
  `flags.html` and linked from every affected row.

## What was checked, and against what

| Check | Official source | Result |
|---|---|---|
| Gold spot reference | `https://www.gold.org/goldhub/data/gold-prices` | Two reads, both `3,996.31` USD/oz; chart label still `Data as of 22 October, 2026` |
| 30 root rows | Each row's own `source_url` (Automic Gold, Sarraf, Blue Nile, Zales, Brilliant Earth, VRAI, Mejuri, Stone and Strand, Factory Direct Jewelry) | 29 exact matches, 1 identity drift |
| Gram / karat claims | Same product pages | Unchanged; no weight was estimated |
| Return / currency claims | Product pages and previously recorded policy pages | Unchanged (F-008, F-018, F-025 still hold) |

## Repairs made to this session's own work

- The first version of the Zales change added a displayed-amount string without a matching
  `field_evidence` quote. `tools/qa.py` failed it (`unassigned_price_text has no field-specific
  evidence`). The evidence key was added rather than the check weakened.
- The first version of the `BN-316238` log entry used a status value the QA gate does not accept
  (`verified_irregularity`). The entry was reclassified to the existing `verified_correction`
  rather than expanding the accepted set.
- Two dashboard constants derived from the old spot price were initially missed; the legacy
  calculator test caught one of them (`SAR-144773 melt`) and the values were recomputed.

## Suites run after the final edit

```
tools/qa.py ................................. PASS 11 checks, 0 failures, 3 warnings
node tools/test_calculator.js ............... PASS
node scripts/build.mjs ...................... 13 pages, 41 products, 77 sources
node scripts/verify.mjs ..................... PASS (0 purchase approvals)
node --test tests/*.test.mjs ................ 23/23
dashboard/scripts/build.py + calc-test.js ... 14 pages / PASS
scripts/build.py + audit.py + test.js ....... PASS
reviews/independent_snapshot_audit.py ....... 12 PASS controls
node scripts/check-links.mjs ................ PASS 46 pages, 102 local targets, 177 external URLs
node scripts/security.mjs ................... PASS 46 pages, 104 source files
npm audit --audit-level=low ................. 0 vulnerabilities
audit/a87a02a5 provenance scanner ........... PASS 0 failures, 13 warnings, 994 controls
audit/8c810c15 scanner ...................... 0 findings, 202 controls
audit/b200a880 scanner ...................... 4,264 controls, 0 failures
```

## Standing rule

A karat stamp is a claim, not an assay. Nothing in this repository has been physically tested.
Re-read the official page after every review; this pass is one review, not a certificate.
