# Findings — S-F03AB52D independent audit (2026-10-23)

Read-only verification. No peer data, evidence, generator, page or stylesheet was edited.
Full detail: `live_verification_2026-10-23.md`; machine-readable: `findings.json`,
`verification-summary.json`, `hallucination_audit_report.json`.

## Verdict

**No hallucinations found. No values inferred or filled.** The independent 9-check
scanner passes with 0 failures / 0 warnings, and 9/9 mutation controls prove it catches
an injected defect. Four official pages were re-read live; none contradicted a stored value.

## Irregularities (non-blocking, published for review)

| ID | Severity | Status | Summary | Source |
|----|----------|--------|---------|--------|
| F03A-01 | info | superseded_by_S-1B04074F | WGC gold header moved intraday: live `3,995.47` vs stored `3,996.31` when this session read it. Moving quote, not a hallucination. S-1B04074F (PR #45) independently read the same `3,995.47` and refreshed the stored value; this session adopts that refresh. | https://www.gold.org/goldhub/data/gold-prices |
| F03A-02 | warning | open | WGC quote-as-of timestamp unconfirmed (carried forward as F-026). Chart date stored separately, not assigned to the header. | https://www.gold.org/goldhub/data/gold-prices |
| F03A-03 | info | documented_exemption | `evidence/gold-price.md` mentions `4,025.54` only to state no such figure exists. Scanner exempts negation contexts; recorded so it is not mistaken for an observation. | https://www.gold.org/goldhub/data/gold-prices |
| F03A-04 | warning | open | Coverage gaps: 20/30 root rows no assigned price; 23/30 no metal weight; zero physical/XRF/scale verification; zero purchase approvals. | — |

## Live re-reads (2026-10-23)

| Item | Live read | Stored | Verdict |
|------|-----------|--------|---------|
| WGC gold spot header | `3,995.47` USD/oz, chart 22 Oct 2026 | `3,996.31` at read time (now `3,995.47` after S-1B04074F) | moved intraday, then refreshed |
| Mejuri Bold Diamond Eternity Ring | `From$2,900`, 14k solid gold, 2.6mm | `From $2,900`, solidGold, karat 14 | confirmed |
| Automic Gold Coffin Ring (JSON) | `price 191000`, `price_max 223300` | `$1,910`, range to `$2,233` | confirmed |
| Brilliant Earth BE121H6 | `$890 (Setting Only)`, 14K YG, 2.5mm | `$890` USD setting-only | confirmed |

## Boundary

Automated PASS proves only that the stated controls passed. It cannot prove a seller's
claim is true, that a page still reads the same tomorrow, or that any ring is actually the
purity stamped on it. Re-open primary sources and look for hallucinations again after every
review.
