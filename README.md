# GOLD — engagement-ring evidence desk

> **No hallucinations:** no price, weight, purity, availability, seller claim, or specification is published unless it was observed in the linked official source. Missing facts stay blank and are flagged. A stamp alone is not treated as purity verification.

This repository organizes solid-gold engagement-ring research as a reviewable evidence ledger. It includes a source-linked catalog, current-price observation dates, a gold-weight calculator, a Flagged for Review queue, and repeatable verification/security checks.

## Core rules

- **Official sources only** for product facts and prices; every populated product field retains its own evidence.
- **No inferred values:** karat fineness used by the calculator is explicitly labeled as a mathematical ratio, never as a laboratory result.
- **Solid gold only:** plated, vermeil, gold-filled, gold overlay, and gold-tone listings are excluded from the eligible catalog.
- **Current prices are observations, not guarantees:** each displays the date and time it was checked and links to the seller's page.
- **Independent verification still matters:** seller metadata and hallmarks do not replace XRF or another professional purity test after delivery.
- **Flag, don't guess:** failed, stale, contradictory, or unavailable evidence is published for review rather than silently repaired.

## Repository map

- `data/requirements.json` — machine-readable buying and publication requirements.
- `data/products.json` — product records with field-level evidence (added during research).
- `data/sources.json` — official-source registry and retrieval log.
- `site/` — static GitHub Pages dashboard.
- `scripts/` and `tests/` — validation, hallucination/security scans, and link checks.
- `docs/` — audit trail, verification notes, and integration record.
- `COORDINATION.md` — shared multi-session task board.

## Review workflow

1. Read the buying checklist and evidence rules.
2. Compare the catalog using official listing links and observation dates.
3. Open **Flagged for Review** before treating any blank or disputed value as fact.
4. Use the calculator only with a verified gram weight and a separately sourced gold-price input.
5. Before wearing or resizing a purchase, ask an independent jeweler to verify purity and weight; request XRF or another professional test.

The site does not replace professional jewelry testing, seller terms, or a buyer's own review.
