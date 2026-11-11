# Freshness and integration review — 2026-11-11

## Scope and truth boundary

Reviewed the existing generators, workflow gates, stored-data provenance and published-site structure. This is not a new live official-source verification. Outbound access in this session is restricted to GitHub and package registries. No retailer, regulator, NIST or gold-price page was freshly fetched; no new product, price, availability or policy claim was added. Historical evidence and retrieval dates are unchanged. Current prices remain unverified. No physical testing or purchase approval occurred. The researched lists are not a complete market inventory.

The existing site has 32 root entries and 46 entries in the combined register. These different scopes are preserved, not summed. All 46 HTML pages now disclose the freshness limitation. An explicit `flags.html#freshness-review` explains the required follow-up without changing prior numbered product flags or claiming a new verified source observation.

## Official links for follow-up (not fetched in this session)

- Gold reference: https://www.gold.org/goldhub/data/gold-prices
- Gold-content guidance: https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3
- Each product/category table retains official product links and historical field-scoped evidence. Follow those links to confirm the exact configuration, currency and metal-only weight before use.

## Executed checks

- `npm ci --ignore-scripts`: installed pinned dependencies; audit found zero vulnerabilities at execution.
- `npm run check`: PASS; 24 tests, deterministic explore build, all 46 pages' local links, static security, npm audit, browser desktop/mobile/calculators/filters/no-JS and automated axe checks in exercised states. External HTTP status is not certified.
- Root QA: PASS, 12 checks, zero failures, three warnings: quote timestamp unconfirmed, 20/32 prices not explicitly assigned, 23/32 missing metal grams. This older scanner uses the phrase “current price” internally; its result is evidence consistency only, not proof of freshness.
- Root, preserved and companion builders, calculator tests, companion reproducibility, independent snapshot arithmetic audit: PASS.
- Existing independent scanners and regression/mutation suites in `audit/8c810c15`, `audit/b200a880`, `audit/88aa65fd`, `audit/9b875c81`: PASS. These compare stored claims with stored evidence, not remote truth.
- New freshness regression test checks all 46 pages and the review anchor; it runs in the normal npm test gate.

Full command output: `npm-check.txt` and `independent-checks.txt` in this directory. Automated security checks are not a guarantee against all vulnerabilities; automated provenance checks cannot detect a fabricated capture if both data and evidence agree. Keep looking for hallucinations and rerun source, provenance, security and regression passes after every review.

## Irregularities and unresolved work

1. All current product prices, availability and gold quotes remain unverified in this session. Historical amounts are retained as historical observations, not silently erased or re-dated.
2. Physical hallmark/maker marks, gold purity, testing permission and independent weighing still require direct verification. A stamp is not proof.
3. External destination liveness cannot be certified with this environment's access restrictions. Local links and row source-link presence passed.
4. Old PR #19 is untouched; this session does not merge another session's stale work.

Deployment and PR results are recorded in the session's final COORDINATION.md block after GitHub reports them.
