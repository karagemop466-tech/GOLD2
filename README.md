# GOLD2 — evidence-first engagement-ring research

**No hallucinations. No invented prices.** Record only supported observations, leave unconfirmed values blank and flagged, and distinguish seller statements from independent tests. This is a publication policy—not a guarantee that a seller, source, or automated check is infallible.

## Start here

- **[Combined 32-entry dashboard](https://karagemop466-tech.github.io/GOLD2/explore/)** — nine retailers, six evidence-aware categories, searchable tables, analysis and official product links.
- **[All researched entries](https://karagemop466-tech.github.io/GOLD2/explore/catalog/)** · **[Flagged for Review](https://karagemop466-tech.github.io/GOLD2/explore/review/)**
- **[Buying checklist](https://karagemop466-tech.github.io/GOLD2/explore/standards/)** · **[Conditional calculator](https://karagemop466-tech.github.io/GOLD2/explore/calculator/)** · **[Source records](https://karagemop466-tech.github.io/GOLD2/explore/sources/)**
- **[Root category dashboard (`20` entries across `6` categories)](https://karagemop466-tech.github.io/GOLD2/)**, **[Explicit Solid 14k Gold rings (`solid-gold.html`)](https://karagemop466-tech.github.io/GOLD2/solid-gold.html)**, **[Root Flagged for Review (`30` flags)](https://karagemop466-tech.github.io/GOLD2/flags.html)**, **[Gold weight & melt calculator (`g`/`dwt`/`ozt`)](https://karagemop466-tech.github.io/GOLD2/prices.html)**, and [initial two-setting dashboard](https://karagemop466-tech.github.io/GOLD2/site/) remain available. Every root page links to the combined `explore/` dashboard and official sources.

GitHub Pages is configured as legacy publishing from **`main` / repository root**, with HTTPS enforced. The verification workflows do not replace that deployment mechanism.

## What the research establishes

Research observations were collected on **22 October 2026 UTC**. The combined register contains **32 unique product URLs, nine sellers, 60 structured publisher records and 20 findings**. The initial 18-page product batch and the original 16-entry register share two Blue Nile settings; deduplication retains each product URL exactly once.

- **10 native-currency price observations:** nine USD displays and one EUR setting price. These are dated page observations, not live prices, exact-size checkout quotes or purchase recommendations.
- **22 unconfirmed numeric prices remain blank.** A dollar sign does not by itself establish ISO USD. Raw display observations are retained in evidence, not converted into verified prices.
- Seven approximate Automic **item weights**, two undefined Auvere **“Fine Weight”** ranges and VRAI’s **2.86g metal-weight claim for size 6** are preserved with their distinct bases. None is independently verified net gold.
- **Zero independently verified ring fine-gold weights; zero approved purchases.** No physical ring, stamp, purity or scale test was performed. Seller contact details were recorded, not tested by calls or emails.
- Categories distinguish natural/lab-grown accent or stone wording, gemstones, alternatives, bare settings/unselected centers, and diamond origin unconfirmed. They do not infer an unselected center or missing gemological facts.

Examples requiring review include incomplete Catbird specifications and conflicting displays, mixed-metal Quince and Blue Nile configurations, category-specific return exceptions, VRAI’s Plain-band/pavé-field inconsistency and $300 engagement-ring return fee, undefined weight bases and missing paired marks/testing permission. Independent review-platform data are scoped opinions/complaints, not purity tests or trust verdicts.

### Gold-reference boundaries

The expanded calculator records a **dated JM Bullion dealer body/table observation**, not an LBMA benchmark or live feed. It distinguishes nominal `karat / 24` from explicit decimal fineness and uses the NIST **31.1034768 grams per troy ounce** conversion. Product valuation remains blocked; a separate acknowledged hypothetical scenario never writes values back to product data.

The root register preserves an earlier WGC header observation. Its **quote-as-of timestamp is unconfirmed and blank**; the chart’s 21 October date is stored separately. Neither chart metadata nor retrieval date is silently assigned to a moving header. Root reference calculations are conditional arithmetic, not current valuations or guaranteed resale floors. See root **F-025/F-026** and the expanded review register.

## Repository layout

| Files | Purpose |
| --- | --- |
| `data/catalog.json`, `research/evidence.json`, `data/review.json` | Canonical combined products, field references, dated observations and findings |
| `explore/` | Generated 13-page combined dashboard; private, self-hosted assets and public data copies |
| `scripts/build.mjs`, `explore/assets/{domain,app}.mjs` | Deterministic generator, evidence-gated arithmetic, filters and progressive enhancement |
| `scripts/{verify,check-links,security,browser-tests,source-monitor}.mjs` | Evidence consistency, links, risk checks, real Chromium/axe and non-updating source signals |
| `tests/*.test.mjs` | Mutation, null, numeric, integration, deterministic-build and preview-server controls |
| `data/solid-gold-verified.json`, `data/listings/*.json`, `data/retailers.json`, `data/flags.json` | Root category register (`20` entries across `6` categories, `6` official retailers + BBB profiles, and `30` bidirectional flags `F-001`–`F-031`) |
| `audit/8c810c15/**` | Independent live line-by-line verification log, NIST `g`/`dwt`/`ozt` calculator edge-case tests, and security/WCAG/hallucination scanner |
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

`npm run check` covers combined evidence consistency, 23 Node tests, deterministic generation, local links/fragments and official links in every table row, root small-text contrast controls, all 29 HTML pages’ static security, npm auditing, desktop/mobile Chromium, filters, all 32 valuation gates, acknowledged scenarios, nonfinite-input rejection, staleness, no-JavaScript research and automated axe checks in exercised states.

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
