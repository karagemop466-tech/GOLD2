# PR #8 publication, live verification, and review errata

**Date:** 2026-10-22 UTC  
**Reviewer:** `5ff05cf9-gold2`  
**Primary reviewed merge:** `73a98fe1338f901b6c85452b237469d3bde29327`

## Exact integration and deployment evidence

| Event | Result |
|---|---|
| Review PR | [#8 — Independent evidence, calculator, and publication review](https://github.com/karagemop466-tech/GOLD2/pull/8) |
| Final PR head | `779020d40bc328decb6240044da7a305366ef856` |
| PR checks | `GOLD2 verify` run `39872116197` and `Verify GOLD` run `39872116200`: success |
| Merge | `73a98fe1338f901b6c85452b237469d3bde29327` at 2026-10-22T23:29:48Z |
| Main checks for exact merge | `GOLD2 verify` run `39872158608` and `Verify GOLD` run `39872158539`: success |
| Pages for exact merge | `pages-build-deployment` run `39872158049`: build/report/deploy success |
| Tree comparison | No difference between PR head `779020d` and merge `73a98fe` |
| Subsequent main delta | PR #13 / `7a453927ac410c45894c480bef47494322798e1f` changed only `reports/qa-report.md`; its verification and Pages runs `39872212871`, `39872212900`, and `39872212893` succeeded |

The merged PR preserved the implementation files and added the independent requirements/review artifacts. It did not discard the earlier dashboard, later quote update, or any session's coordination log.

## Final isolated checks

An archive of exact merge `73a98fe` passed:

```text
python tools/build_site.py   -> 10 root pages built
python tools/qa.py           -> PASS, 11 checks, 0 failures, 2 coverage warnings
python scripts/build.py      -> legacy 6 pages and data.json built
python scripts/audit.py      -> PASS for its limited legacy dataset; open gaps disclosed
node scripts/test.js         -> synthetic calculator controls passed
```

The independent reviewer reported 31 implementation findings and six passing arithmetic controls on the PR #9 quote state. The supplied PASS and the independent findings measure different things; neither is hidden.

## Live routes checked after deployment

Cache-busted live retrieval after the exact merge confirmed:

- `/GOLD2/?review=73a98fe` — current 16-row dashboard, 15 priced rows, 1/16 published weights, and 4,028.53 quote.
- `/GOLD2/prices.html?review=73a98fe` — VRAI 2.145 g / $277.82 and all five quick-reference rows match independent decimal arithmetic.
- `/GOLD2/flags.html?review=73a98fe` — 16/16 solid-gold and 15/16 weight gaps are displayed; F-015 still has the stale 8-Blue-Nile sentence.
- `/GOLD2/solitaire.html?review=73a98fe` and `/GOLD2/18k.html?review=73a98fe` — category tables and official row links load.
- `/GOLD2/methods.html?review=73a98fe` — QA report and limitations load.
- `/GOLD2/reviews/2026-10-22-6ca03571.md?review=73a98fe` and `/GOLD2/reviews/findings.json?review=73a98fe` — independent review artifacts are publicly retrievable.

The live dashboard and calculator still showed `quote date 2026-10-22` while the [official World Gold Council page](https://www.gold.org/goldhub/data/gold-prices) said `Data as of 21 October, 2026`. R9-01 therefore remains open and visibly documented. The supported number is 4,028.53; the unsupported part is its as-of date.

## R8-01 — review-only errata found and corrected

The final live/self-consistency pass caught errors in the **review report itself**, not in the implementation data:

- Five report widths were transcribed incorrectly. Direct official re-fetch confirmed these correct values: BN-203348 **2.40 mm**, BN-194548 **2.00 mm**, BN-192506 **1.60 mm**, BN-315661 **1.75 mm**, and BN-193625 **1.80 mm**.
- Three report source URLs pointed to the wrong Blue Nile slug. The corrected URLs are the exact structured-record/official URLs for BN-194548 (Solitaire Compass Set), BN-315661 (Pavé Contour), and BN-193625 (Petite Three-Stone).
- Unrelated platinum-prong wording was removed from the BN-194548 finding, and BN-193625 is described as side-stone rather than pavé evidence.

The implementation's structured values matched the official pages; no product-data edit was needed for these errata. The review table and R6-03 official reference were corrected instead.

To make this repeatable, `independent_snapshot_audit.py` now compares each report row with the structured record's exact source URL, price, width, and published weight. Equivalent trailing-zero forms such as 1.7 and 1.70 are accepted; rounded or different widths are not.

- `reviews/pr8-73a98fe-pre-errata-checks.txt`: **39 findings**, six arithmetic controls — retains the eight report-row errors alongside the 31 implementation findings.
- `reviews/final-post-errata-checks.txt`: **31 findings**, six arithmetic controls — no remaining report-row mismatch.

R8-01 is marked resolved in `reviews/findings.json`, with both outputs preserved. This is why review prose also needs automated checks and repeated official-source reading.

## Current finding disposition

- **Resolved:** R39-01 (category subpages now exist), R39-03 (usable calculator inputs now exist), and R8-01 (review errata corrected).
- **Open:** 17 findings — **5 high, 9 medium, 3 low**. R6-07 remains open even though the original no-input calculator finding R39-03 is resolved.
- **Most immediate factual correction:** R9-01 quote as-of date.
- **Other material open work:** unsupported Zales colors and secondary claims, solid/verification overclaims, payment/policy/contact evidence, VRAI size context, calculator validation and unsourced guidance, QA false-negative paths, narrative consistency, seller/documentation scope, and one archived-excerpt mismatch.

## Publication conclusion

The static site, review artifacts, PR checks, merge, and Pages deployment are operational. This is **not** a conclusion that every ring is solid gold, every seller is independently reputable, or every published statement is fully verified. No ring is purchase-qualified without the missing evidence and independent professional purity/weight verification. Further hallucination/security review is required after R9/R6 corrective edits and after every subsequent integration.
