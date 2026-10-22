# Coordination board

Last updated: 2026-10-22T23:08:49Z

## Session and branch rules

- Active session: `5ff05cf9-gold2` (Arena session `arena/5ff05cf9-gold2`).
- This Arena session is bound to `arena/5ff05cf9-gold2`; repository work, the integration PR, and pushes use that fixed branch. No other branch may be created or switched to by this session.
- Other sessions must claim non-overlapping file scopes below before editing. Do not edit a claimed scope; log a request instead.
- Run `git pull --rebase` before every push. Make small commits. Never discard another session's work.
- `needs review` means published on **Flagged for Review** and does not block completion.
- Blank or `null` means unverified. Never infer missing product facts or prices.

## Task board

| ID | Task | Status | Owner session | Started (UTC) | File scope |
|---|---|---|---|---|---|
| T1 | Repository and requirements audit | done | `5ff05cf9-gold2` | 2026-10-22T23:08:49Z | `README.md`, `data/requirements.json`, `docs/REPOSITORY_AUDIT.md` |
| T2 | Official-source ring research and evidence records | unclaimed | — | — | `data/products.json`, `data/sources.json`, `docs/SOURCES.md` |
| T3 | Reusable verification, hallucination, and security checks | unclaimed | — | — | `scripts/**`, `tests/**`, `docs/VERIFICATION.md` |
| T4 | Dashboard UI and category/calculator page components | unclaimed | — | — | `site/assets/**`, `site/*.html`, `site/*/index.html` (excluding generated `site/data/**`) |
| T5 | Final integration, generated site data, Pages workflow, PR and deploy | unclaimed | — | — | `site/data/**`, `.github/**`, `docs/INTEGRATION.md`, root workflow/config files not otherwise claimed |

`COORDINATION.md` is the shared board: sessions may update only their own task rows, handoff notes, requests, and completion records.

## Requests across scopes

None.

## Activity and handoff log

- 2026-10-22T23:08:49Z — `5ff05cf9-gold2`: initial repository inspection found only `README.md` (`# GOLD2`) at commit `b00633e9fd6d3b2e82dcf21cbd4a8a6aabb7afe7`. Created board and claimed T1. No product, price, purity, weight, seller, or deployment claims existed to verify.

## Completion records

### T1 — 2026-10-22

- **Sources:** exact starting [README](https://github.com/karagemop466-tech/GOLD2/blob/b00633e9fd6d3b2e82dcf21cbd4a8a6aabb7afe7/README.md), [tree](https://github.com/karagemop466-tech/GOLD2/tree/b00633e9fd6d3b2e82dcf21cbd4a8a6aabb7afe7), and [commit](https://github.com/karagemop466-tech/GOLD2/commit/b00633e9fd6d3b2e82dcf21cbd4a8a6aabb7afe7).
- **Verification:** inventoried the complete tracked starting tree, compared its only line with the exact-commit GitHub source, validated `data/requirements.json` with Python's JSON parser, and ran `git diff --check`.
- **Irregularities:** no existing product or price records; no legacy hallucinations to flag. Missing research, validation, and deployment infrastructure were recorded as work requirements, not as verified product findings.
- **Residual review:** future edits must be checked against official sources and followed by hallucination/security scans. See Flagged for Review once published.

## Pull request and deployment

Pending final integration.
