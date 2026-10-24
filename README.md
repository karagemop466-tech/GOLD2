# GOLD2 — evidence-first engagement-ring research

**No hallucinations. No invented prices.** Record only supported observations, leave unconfirmed values blank and flagged, and distinguish seller statements from independent tests. This is a publication policy—not a guarantee that a seller, source, or automated check is infallible.

**Coverage note:** the combined Explore catalog now carries **44 product records across 13 sellers**, including every source-checked URL in the separate 30-row root dashboard. The three root-only pages (Automic Gold Coffin Ring, Automic Gold Cushion Diamond Signet Ring and Mejuri Bold Diamond Eternity Ring) were integrated on 2026-10-23 with their own dated field evidence; `tools/qa.py` check 12 now fails CI if any root URL is missing from the combined register.

## Start here

- **[Companion 14-page solid-gold dashboard (`dashboard/`)](https://karagemop466-tech.github.io/GOLD2/dashboard/)** — executive overview with prominent **No Hallucinations Policy**, 6 category subpages (`solid-gold.html`, `solitaire.html`, `halo-pave.html`, `three-stone-vintage.html`, `high-karat.html`, `budget.html`), NIST `g`/`dwt`/`ozt` + gemstone carat deduction calculator (`1 ct = 0.200 g`), 11 official sellers + BBB audit, 12-point buying checklist, and Flagged for Review register.
- **[Combined 44-entry dashboard](https://karagemop466-tech.github.io/GOLD2/explore/)** — 13 sellers, six evidence-aware categories, searchable tables, analysis and official product links. Every source-checked root URL is now included.
- **[All researched entries](https://karagemop466-tech.github.io/GOLD2/explore/catalog/)** · **[Flagged for Review](https://karagemop466-tech.github.io/GOLD2/explore/review/)**
- **[Buying checklist](https://karagemop466-tech.github.io/GOLD2/explore/standards/)** · **[Conditional calculator](https://karagemop466-tech.github.io/GOLD2/explore/calculator/)** · **[Source records](https://karagemop466-tech.github.io/GOLD2/explore/sources/)**
- **[Root category dashboard (`30` entries across `6` categories & `9` official product sellers)](https://karagemop466-tech.github.io/GOLD2/)**, **[Explicit Solid Gold rings (`solid-gold.html` · `13` listings)](https://karagemop466-tech.github.io/GOLD2/solid-gold.html)**, **[dated re-verification log](https://karagemop466-tech.github.io/GOLD2/verification.html)**, **[nominal gold-content analysis](https://karagemop466-tech.github.io/GOLD2/analysis.html)**, **[Root Flagged for Review (`39` flags)](https://karagemop466-tech.github.io/GOLD2/flags.html)**, **[Gold weight & melt calculator (`g`/`dwt`/`ozt`)](https://karagemop466-tech.github.io/GOLD2/prices.html)**, and [initial two-setting dashboard](https://karagemop466-tech.github.io/GOLD2/site/) remain available. Every root page links to the companion `dashboard/`, combined `explore/`, and official sources.

GitHub Pages is configured as legacy publishing from **`main` / repository root**, with HTTPS enforced. The verification workflows do not replace that deployment mechanism.

## What the research establishes

Research observations were collected on **22 October 2026 UTC** and re-verified on **23 October 2026 UTC**. The combined register contains **44 unique product URLs across 13 sellers, 85 source records and 26 review findings**. The separate root register contains 30 product entries across 6 categories and 9 sellers; every one of its source URLs is now present in the combined catalog, and `tools/qa.py` check 12 enforces that coverage in CI.

- **Combined `explore/` register (44 products across 13 sellers):** 17 rows carry a dated USD display amount and 27 keep `price` null because no ISO currency statement or no rendered amount was captured; nothing is converted, averaged, or filled from a neighbouring row. Brilliant Earth's setting re-rendered in a USD locale at $890 (Setting Only), and the earlier EUR 990 render is kept only as superseded history. Menē Rose Ring moved $1,346 → $1,336 → $1,325 USD and Knot Ring $1,465 → $1,454 → $1,442 USD; only the latest dated observations are assigned. Automic Gold's Coffin Ring ($1,910 default, range to $2,233) and Cushion Signet ($2,758 default, $2,408–$3,253) plus Mejuri's Bold Diamond Eternity Ring (From $2,900, price unassigned) were added on 2026-10-23 with F-039. The $4,035.54 JM Bullion dealer reference is an earlier dated observation not re-read in the later pass; it is not the WGC spot quote.
- **Later dated pass (2026-10-23 ~20:2xZ):** ten official URLs were re-read for this integration pass (WGC; Automic Coffin page/JSON, Cushion page/JSON and cart; Mejuri product, returns FAQ and BBB profile; Zales V-19957449). Values, the 40-row not-re-read list and five irregularities are in `audit/1eb9f828/live_verification_2026-10-23.md`.
- **10 assigned prices in the root register**, each backed by an official currency statement. Other displayed amounts remain unassigned when the retailer's ISO currency or the amount's price role cannot be confirmed; the root table preserves the display text and links the flag.
- **Live re-verification on 23 October 2026:** 29 records re-read or attempted, 18 unchanged, 6 corrections, 1 re-read with no price shown, 3 dead ends, 1 row not re-read. Every page, verbatim value and date is on `verification.html`. Corrections: Brilliant Earth served EUR €990 on 22 October but USD $890 with a USD selector on 23 October (F-007); all four Zales pages rendered with and without Discounted/Original labels on the same day (F-018); and the World Gold Council header moved repeatedly within the same day (4,028.53 → 4,024.36 → 4,024.45 → 3,996.31), with S-1B04074F’s later **2026-10-23** re-read returning **$3,995.47/oz** against a chart still stating 22 October 2026; S-A182C7CC independently re-read the same display. The header quote-as-of time remains unconfirmed, and the fetch tool exposes no exact request seconds (F-026). Only the latest dated observation is used; every earlier capture remains superseded history and is not rendered.
- **Follow-up price pass (S-A182C7CC, 2026-10-23):** all 17 product rows with assigned USD prices were opened at their official product pages; 15 matched and the two Menē amounts were corrected as shown above. Brilliant Earth’s $890 setting-only amount was independently re-read. The WGC header matched $3,995.47/oz already integrated by PR #45; F-026 remains open because the quote time is not displayed. Other product fields, seller policies, checkout totals, and the 27 unassigned price fields were not recertified or filled. New price observations use date-only precision because the fetch tool does not report request seconds. See `audit/a182c7cc/live_price_verification_2026-10-23.md`.
- **One evidence rule now applies to every row:** an amount is assigned to a currency only when the retailer itself states it. Automic Gold is supported by its public cart endpoint (`"currency":"USD"`), Brilliant Earth by a rendered USD selector, and every other dollar amount stays displayed-but-unassigned. This replaced an inherited inconsistency where some dollar-sign prices were labelled USD and others were not (F-033).
- Seven approximate Automic **item weights**, two undefined Auvere **“Fine Weight”** ranges and VRAI’s **2.86g metal-weight claim for size 6** are preserved with their distinct bases. None is independently verified net gold.
- **Zero independently verified ring fine-gold weights; zero approved purchases.** No physical ring, stamp, purity or scale test was performed. Seller contact details were recorded, not tested by calls or emails.
- Categories distinguish natural/lab-grown accent or stone wording, gemstones, alternatives, bare settings/unselected centers, and diamond origin unconfirmed. They do not infer an unselected center or missing gemological facts.

Examples requiring review include incomplete Catbird specifications and conflicting displays, mixed-metal Quince and Blue Nile configurations, category-specific return exceptions, VRAI’s Plain-band/pavé-field inconsistency and $300 engagement-ring return fee, undefined weight bases and missing paired marks/testing permission. Independent review-platform data are scoped opinions/complaints, not purity tests or trust verdicts.

### Gold-reference boundaries

The expanded calculator records a **dated JM Bullion dealer body/table observation**, not an LBMA benchmark or live feed. It distinguishes nominal `karat / 24` from explicit decimal fineness and uses the NIST **31.1034768 grams per troy ounce** conversion. Product valuation remains blocked; a separate acknowledged hypothetical scenario never writes values back to product data.

The root register records a dated observation of the WGC moving header: **$3,995.47 USD/ozt, retrieved 2026-10-23 UTC**. Its exact **quote-as-of timestamp remains unconfirmed (`quote_date: null`)**; the page separately stated “Data as of 22 October, 2026” for the chart. Neither chart metadata nor retrieval date is assigned to the moving header. The stored observation is not a live quote. Root reference calculations are conditional arithmetic, not current valuations or guaranteed resale floors. See root **F-025/F-026** and the expanded review register.

## Repository layout

| Files | Purpose |
| --- | --- |
| `data/catalog.json`, `research/evidence.json`, `data/review.json` | Canonical combined products, field references, dated observations and findings |
| `explore/` | Generated 13-page combined dashboard; private, self-hosted assets and public data copies |
| `scripts/build.mjs`, `explore/assets/{domain,app}.mjs` | Deterministic generator, evidence-gated arithmetic, filters and progressive enhancement |
| `scripts/{verify,check-links,security,browser-tests,source-monitor}.mjs` | Evidence consistency, links, risk checks, real Chromium/axe and non-updating source signals |
| `tests/*.test.mjs` | Mutation, null, numeric, integration, deterministic-build and preview-server controls |
| `data/solid-gold-verified.json`, `data/listings/*.json`, `data/retailers.json`, `data/flags.json`, `data/verification-log.json` | Root category register (`30` entries across `6` categories, `9` product sellers plus BBB profiles, `39` bidirectional flags `F-001`–`F-042` (no `F-012`, `F-032` merged into `F-007`), and the dated re-verification log) |
| `analysis.html`, `verification.html`, `tools/build_site.py` | Generated nominal fine-gold analysis, dated verification log, and the data-derived generator (no typed counts) |
| `audit/062f314f/**` | 2026-10-23 live re-verification log from the parallel session: sources fetched, observed amounts, and which rows were not re-fetched |
| `audit/8c810c15/**` | Independent live line-by-line verification log, NIST `g`/`dwt`/`ozt` calculator edge-case tests, and security/WCAG/hallucination scanner |
| `audit/b200a880/**` | Independent 2026-10-23 live re-verification of all 20 root rows, the gold quote and six policy sources (machine-readable JSON + narrative), plus a second hallucination/security scanner (3,056 controls) with 25 unit tests; its corroborated data findings were already integrated by the parallel sessions, so the folder is audit-only |
| `audit/a182c7cc/**` | Independent repository review, date-precision official price recheck of all 17 assigned-price products and the WGC moving header, plus final security, hallucination, build, calculator, and browser test results |
| `evidence/**`, `tools/**`, root HTML/`assets/**` | Peer research and original dashboard, preserved with documented safety corrections |
| `site/`, `scripts/{build.py,audit.py,test.js}` | Initial two-setting implementation, still reproducible |
| `reviews/**`, `docs/REPOSITORY_AUDIT.md` | Historical, commit-specific independent reviews and initial-tree audit; not certificates for later revisions |
| `docs/REVIEW.md`, `COORDINATION.md` | Integration review, execution limits and multi-session ownership log |

## Build and verify

Node **22+**, npm and Python 3.12 are used in CI. The browser and axe tooling are exact-pinned development dependencies; browser-facing code has no runtime package dependencies, external scripts/fonts, trackers or affiliate links.

```sh
npm ci --ignore-scripts
python3 tools/build_site.py
python3 tools/qa.py
node tools/test_calculator.js
python3 tools/build_site.py
python3 reviews/independent_snapshot_audit.py .
python3 scripts/build.py
python3 scripts/audit.py
node scripts/test.js
npm run check
```

`npm run check` covers combined evidence consistency, 23 Node tests, deterministic generation, local links/fragments and official links in every table row, root small-text contrast controls, all 46 published HTML pages’ static security, npm auditing, desktop/mobile Chromium, filters, all 44 automatic valuation gates, acknowledged scenarios, nonfinite-input rejection, staleness, no-JavaScript research and automated axe checks in exercised states. The root Python suite adds 12 checks over the same data, including the dated verification log, nominal fine-gold arithmetic and derived shell counts.

```sh
npm run dev            # read-only preview on 0.0.0.0:4173; open /GOLD2/explore/
npm run sources:check  # writes ignored test-results/source-monitor.json; never updates facts/prices
```

The scheduled/manual source workflow reports HTTP/identity-word signals and capped-content sample hashes. Bot blocks, regions and JavaScript rendering cause false alarms. A successful request does not certify a price or product identity; there is no automatic baseline comparison. Source observations are never refreshed just by building or monitoring. Runtime test reports/screenshots are ignored and retained as CI artifacts, not committed datasets.

**Repeat source/hallucination-risk and security checks after every review or combined-session change.** Automated PASS means only the stated controls passed. It cannot prove source truth, actual gold purity, complete security/accessibility or future return eligibility. Open flagged evidence is published, not treated as a broken build.

## Before buying

1. Reopen the exact official product and obtain a native-currency, size/configuration-specific all-in quote. Do not infer missing values.
2. Require explicit **solid gold**, not plating/vermeil/filled/overlay/gold-tone; stated karat; paired **karat and maker/manufacturer marks**; and gold-alloy-only grams excluding stones and other materials. A stamp alone proves no actual purity.
3. Review independent complaints and verify real contact details. A BBB rating, accreditation or seller statement is not a physical authentication.
4. Obtain written independent inspection/testing permission and return eligibility, deadline and fees, including resizing, custom work, engraving and third-party alterations.
5. Prefer applicable credit-card purchase protection; avoid irreversible transfers. Network acceptance does not guarantee a dispute outcome.
6. Preserve the exact listing/claims, receipt, seller correspondence, selected configuration, certificates and mark photos.
7. Before wear or resizing, have an independent professional assess weight and purity, using XRF or an appropriate test. Surface XRF can mislead in gold-over-gold cases; a professional must select the assessment.
8. **Do not buy if independent verification and a qualifying return are disallowed.**

Primary guidance: [FTC jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry), [FTC online shopping](https://consumer.ftc.gov/articles/online-shopping), [GIA testing caveat](https://www.gia.edu/gems-gemology/summer-2025-lab-notes-gold-plated-gold), [NIST units](https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf). Each product and policy observation links its own official publisher.

This is a bounded research register, not an exhaustive market survey, appraisal, financial/legal advice or purchase endorsement.
