# S-F3B0B698 pre-fix companion and inherited-baseline findings

Date: 2026-10-23  
Scope: offline line-by-line review of the repository, canonical root/combined registers, companion generator/verifier, rendered pages, tests, workflows, and prior audit artifacts. No retailer, product, policy, or gold-price page was freshly fetched in this pass. Observations below are repository-state findings, not current-source or physical-purity claims.

## Companion/canonical drift

The companion contained separately hardcoded product, seller, and gold-reference blocks rather than deriving them from the newer canonical records. Exact-source comparison found these assigned-price mismatches, shown as **old companion → canonical at audit start**:

| Product | Old companion | Canonical |
|---|---:|---:|
| VRAI-CLASSIC-4P | 1470 | `null` |
| AG-CUSHION-SIGNET | 2408 | 2758 |
| MJ-BOLD-ETERNITY | 2900 | `null` |
| BN-194158 | 1125 | `null` |
| BN-195269 | 1155 | `null` |
| BN-316238 | 1240 | `null` |
| BN-315661 | 2210 | `null` |
| BN-203348 | 1145 | `null` |
| Z-20046552 | 909.30 | `null` |

Except for Automic's differing numeric USD price, these rows also supplied companion `USD` where the canonical currency was blank. BN-316238 retained an assigned amount despite its canonical product-identity mismatch; its `$1,240(Setting Price)` text could not be attached to the stored item.

Nine same-ID/different-URL warnings required identity resolution rather than automatic copying: `VRAI-CLASSIC-4P`, `AG-CUSHION-SIGNET`, `MJ-BOLD-ETERNITY`, `BN-194158`, `BN-195269`, `BN-315661`, `BN-203348`, `Z-20303279`, and `Z-20046552`.

Four companion-only IDs had exact combined-register mappings: `MENE-ROSE`, `MENE-KNOT`, `AV-BRIDGE`, and `AV-CLEAN`.

## Seller and narrative defects

- Automic's old companion wording said 14 days; the canonical wording says free US returns within 30 days of delivery, with a separate 14-day mailing condition to avoid a recycling fee.
- Menē's old companion wording supplied seven days; the combined canonical `returnDays` is `null`.
- Automic, Mejuri, Blue Nile, Brilliant Earth, VRAI, and Zales reputation references or summaries diverged from canonical records. In particular, old companion Automic `B-` and Mejuri `F` grades were absent from canonical records that leave rating blank.
- AG-24K contained stale derived text (`40.4%`) inconsistent with its then-displayed inputs (approximately `40.2%`).
- Broad or unsupported generalizations included “every value” support, a universal `<1.8 g` bend/snap threshold, a generic 14–100 day return window, overbroad credit-card legal language, and below/near-melt arithmetic treated too conclusively as counterfeit/plating evidence.

## Verifier and rendering gaps

- P1 checked for HTTPS but did not establish that the product host matched the claimed seller.
- P2 checked positivity/date/note presence, not exact canonical amount parity, explicit ISO-USD evidence, or null-price evidence leakage.
- P3 accepted almost any flag for a missing weight and did not require all physical/qualification limitations.
- P5 required seller summaries to be nonblank, conflicting with the requirement to preserve unsupported values as blank/`null`.
- P8 checked companion-generated quotes against companion-generated Markdown, a closed loop that did not prove canonical provenance.
- Rendered checks did not independently recompute every ring's fine-gold/nominal-value cells or prove that each table row had an official/standards source.

## Inherited disposable-copy baseline

Before these edits, a disposable-copy baseline recorded:

- Calculator tests: 16/16 passed; combined verification passed.
- `npm run check`: exit 2 after root `tools/qa.py` emitted 42 error lines involving known null-bearing `ss-rita`, `ext-z-20303279`, and `z-20303279` records. The correct resolution is validator/data-evidence reconciliation, never inventing values.
- Root build: 45 warnings involving those products and missing-key/null evidence patterns. Direct root QA reproduced errors in that baseline state. A later direct run against the unchanged canonical root registers passed 12 checks with three coverage/gold warnings, so final order-dependent integration checks remain mandatory.
- Browser tests: 16/16 passed. Security: 151 files scanned, PASS.
- Link checking completed with six nonfatal warnings involving a README directory link, stale registry paths in coordination/reports, and calculator WGC/NIST/GIA references.

These were inherited baseline observations, not certificates of current source truth. Final results are recorded separately only after the repaired companion and all applicable repository suites are run together.

## Disposition implemented after this report

The companion now derives its 26 product rows, 11 seller rows, and gold reference from canonical records; preserves blank/`null`; retains raw displays only as unassigned text; suppresses the BN-316238 amount; distinguishes metal weight from gross/range displays; and adds explicit flags for missing weight, missing assigned price, nonconfirmed solid-gold wording, seller blanks, and zero physical testing. Its verifier and a separate independent scanner now check seller hosts, canonical parity, amount/currency evidence, nulls, rendered arithmetic, official row links, CSP/link integrity, and repeat-review language.
