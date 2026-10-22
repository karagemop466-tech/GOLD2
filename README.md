# GOLD2 — source-backed gold engagement-ring research

**No hallucinations. Publish only what a retrieved source supports. If a value is absent or ambiguous, leave it blank and flag it—never infer it from another item, a photograph, price position, discount arithmetic, a search snippet, or currency conversion.**

Live dashboard: **https://karagemop466-tech.github.io/GOLD2/**
Publishing: GitHub Pages legacy source, `main` branch, repository root.

## What this repository contains

An auditable register of **16 engagement-ring listings from 4 retailers**, organized into five categories. It separates:

- official product facts from seller policy claims;
- official seller pages from independent BBB profile data;
- explicitly assigned prices from blank or unlabeled amounts;
- setting/configurator prices from complete-ring prices;
- retrieved facts from nominal gold calculations; and
- remote document review from physical verification, which has **not** been performed.

Current coverage: **13 assigned prices**, **1 published metal weight**, and **23 open flags**. No item-specific capture states the required “solid gold” wording or documents a physical hallmark plus maker’s mark. Those are evidence gaps, not findings that a ring is fake.

## Dashboard pages

| Path | Contents |
|------|----------|
| `index.html` | No-hallucination rule, coverage counts, dated gold quote, category links, review checklist |
| `solitaire.html` | Solitaire settings and the Brilliant Earth EUR-priced row |
| `halo-pave.html` | Halo/pavé settings, including two re-verified earlier-pass listings |
| `three-stone-vintage.html` | Three-stone/vintage rows, including two unlabeled Zales price displays |
| `18k.html` | 18K settings and VRAI’s published size-6 metal weight |
| `budget.html` | 10K / lower-price complete-ring rows |
| `retailers.html` | Official returns/payments/contact details plus independently sourced, scope-labeled BBB metrics |
| `prices.html` | Metal-only weight → nominal fine-gold → theoretical melt calculator |
| `flags.html` | **Flagged for Review:** missing evidence, discrepancies, source limits, and material policy restrictions |
| `methods.html` | Evidence method, source hierarchy, limitations, security notes, and QA summary |
| `site/` | Earlier two-listing dashboard, preserved with its own generator, audit, and calculator tests |

Every current listing row links its **official product page** and its **own field-scoped evidence file**.

## Repository layout

```text
data/
  listings/*.json       five categories; nullable fields and field_evidence per row
  retailers.json        official policies plus scoped independent reputation data
  flags.json            23 findings with affected rows/retailers and source links
  gold-price.json       dated WGC quote, NIST conversion, eCFR context, limitations
evidence/
  listings/<item>.md    authoritative item-scoped excerpts and capture limits
  listings/README.md    explains inherited shared-category files (history only)
  retailers/*.md        official policy evidence and independent-profile excerpts
  gold-price.md         current/superseded quotes and calculation sources
assets/
  calculator.js         dependency-free, testable nominal-gold calculator
  style.css             shared dashboard styling
tools/
  build_site.py         renders 10 root HTML pages from data
  qa.py                 field-level provenance, integration, link, and security audit
  test_calculator.js    calculator unit tests
reports/qa-report.md    latest automated audit result
reports/source-link-review.md  dated external-source retrieval inventory
scripts/, site/         preserved earlier-pass implementation
COORDINATION.md         shared task board, source log, integration/deployment record
```

## Build and verify

```bash
python3 tools/build_site.py
python3 tools/qa.py
node tools/test_calculator.js
python3 tools/build_site.py  # refresh the rendered QA summary after the audit
```

Run all three after every review. The audit checks:

- item-scoped schema, IDs, dates, and official domains;
- field-specific quote existence and value/currency/unit consistency;
- retailer policy, contact, payment, and independent-metric backing;
- blank-to-flag coverage and two-way item/retailer flag references;
- rejected/superseded values not becoming current values;
- nominal fine-gold and melt calculations;
- rendered row/source identity, internal links and fragments, CSP, and script constraints; and
- explicit price/weight coverage warnings.

The preserved earlier pass remains runnable:

```bash
python3 scripts/build.py
python3 scripts/audit.py
node scripts/test.js
```

**A PASS is not proof of physical truth or external-site availability.** Look for hallucinations again after every review and re-read the official source and generated page after every edit.

## Source hierarchy

1. **Product and policy facts:** the retailer’s official product, return, payment, and contact pages.
2. **Independent reputation context:** BBB profile/review/complaint pages, dated and labeled by identity and coverage. Blue Nile and Brilliant Earth have linked profiles; Zales figures are combined Signet figures; VRAI candidate metrics are withheld pending identity confirmation. BBB allegations are not treated as proven facts, and BBB does not endorse businesses.
3. **Gold quote:** World Gold Council spot page with an explicit quote date and ICE Data Services attribution. LBMA’s tabulated data requires licensed portal access (F-013).
4. **Calculation sources:** NIST’s troy-ounce conversion chart (`31.103 476 8 g`) and eCFR gold-labeling context. Nominal karat/24 arithmetic is not an assay.
5. **Rejected as product evidence:** snippets, aggregators, blogs, coupon pages, unrelated page text, and values borrowed from another item.

## Using the research safely

1. Open both the official listing and the row’s field evidence; recheck the exact configuration, price basis, currency, and retrieval date.
2. Ask in writing whether the item is solid gold (not plated/filled), its metal-only gram weight, its physical karat/maker’s marks, and whether independent non-destructive XRF is permitted without voiding returns.
3. Review the seller’s accepted payment methods and your own card/provider protection terms. Official acceptance does not prove a dispute outcome.
4. Read the exact return and resizing policy. Zales rules depend on where resizing occurred; Blue Nile, VRAI, and Brilliant Earth have their own resized/custom exclusions; VRAI fees and Brilliant Earth engraving terms are published separately.
5. Keep the item unworn and unaltered until independent inspection and the keep/return decision are complete. Do not resize before understanding the consequences.
6. If the seller refuses independent verification or a return, do not buy.

## Calculator boundaries

Use **metal-only weight**, excluding stones and non-gold components. The formulas are:

```text
nominal fine-gold grams = metal-only grams × listed karat ÷ 24
theoretical melt USD    = nominal fine-gold grams ÷ 31.1034768 × dated USD/troy oz
```

The result is not an appraisal, fair-retail estimate, resale offer, or refiner payout. Do not enter EUR prices into the USD asking-price field. No fine-gold or melt result is generated for rows without a published metal weight.

## Independent review and repository controls

- `data/requirements.json` records buyer and publication requirements in machine-readable form.
- `docs/REPOSITORY_AUDIT.md` preserves the exact initial-tree audit.
- `reviews/` preserves the independent review protocol, official terminology/calculation baseline, commit-specific evidence reviews, raw audit output, and machine-readable findings. These dated reports are review inputs, not a substitute for rerunning current official-source and hallucination/security checks.
- The independent R9-01 finding correctly identified that `2026-10-22` was a retrieval date, not the WGC source's as-of date. This integration retains the supported **$4,028.53** number and restores **quote date 2026-10-21** from “Data as of 21 October, 2026.” Historical raw reports remain unchanged.
- PR #8's merge/deployment evidence and post-merge errata are preserved in `reviews/2026-10-22-pr8-publication.md`; its old row/price counts are commit-specific, not current-dashboard counts.

## Disclaimer

Prices and policies can change after the stated retrieval date. Nothing here is financial, legal, or appraisal advice, and no purchase recommendation is made for rows with unresolved checklist evidence.
