# Independent peer-review protocol

Reviewer session: `5ff05cf9-gold2`  
Scope: read-only review of other session branches, their official evidence, combined output, and deployment. Review findings are written only under `reviews/**`.

## No-hallucinations rule

A passing automated schema check is not proof that a statement is true. Every populated product value must be traceable to text actually observed on the cited official page for the same product and variant. Missing, inaccessible, ambiguous, or contradictory evidence produces a blank/`null` value and a visible review flag. Search snippets and third-party pages are discovery aids, not product-fact evidence.

## 1. Line-by-line evidence review

For every catalog row, record the row ID, exact source URL, source-observation time, reviewer, and result for each field:

- Product name and URL identify the same item; variant/size/metal are not interchanged.
- Price and currency are copied exactly from an official page observation and labeled as setting-only or complete-ring where applicable. No snippet-only, stale, converted, averaged, or remembered prices.
- Karat and metal color come from official variant-specific text.
- “Solid gold” is explicit. Karat alone does not pass this gate; plated, vermeil, gold-filled, overlay, and gold-tone items are excluded from eligibility.
- Gram weight is exact and variant-specific. Width, diamond weight, and metal weight are not silently substituted for total ring weight.
- Karat hallmark and maker's mark are separate facts. Brand identity alone does not prove a maker's mark; a stamp alone does not prove purity.
- Return, payment, contact, custom/resized exclusions, availability, and shipping claims cite the applicable official policy/listing and are not generalized beyond their scope.
- Seller reputation is not marked verified solely by seller-authored content. Independent testing remains a post-purchase requirement.
- Every blank or disputed value has a corresponding Flagged for Review entry with a manual-review link.

Classifications: `pass` (evidence directly supports the exact value), `flag` (unsupported, ambiguous, contradictory, or inaccessible), `not observed` (blank and properly flagged). A reviewer never repairs a missing value by guessing.

## 2. Calculation review

- Recalculate representative and boundary cases independently.
- Nominal fine-gold weight is `ring weight in grams × karat ÷ 24`; label it as nominal mathematical content, not XRF/laboratory verification.
- Never calculate a precise raw-gold weight when total gram weight or karat is absent.
- If a metal-price input is supplied, show its source, currency, unit, and observation date; keep input metal value distinct from retail price, resale value, fees, stones, craftsmanship, and taxes.
- Reject non-finite numbers, negative weights, unsupported karats, and unit confusion. Preserve blank outputs for missing inputs rather than displaying zero as a fact.

## 3. Hallucination and content-security review

After every review or content edit:

1. Diff all product facts and prices against evidence, not merely against a prior dataset.
2. Scan the rendered site for unsupported certainty, hidden rows, unsourced badges, and “verified” labels that overstate the actual checks.
3. Check that dynamic rendering cannot inject executable HTML from listing/source data; prefer text nodes or sanitization.
4. Check workflows for excessive permissions, unpinned third-party actions, secret exposure, and unsafe script execution.
5. Check for credentials, private tokens, unexpected executable files, and external trackers.
6. Run all repository QA, then manually inspect any bot-blocked link instead of equating an HTTP block with a missing product.
7. Recommend another hallucination review after any subsequent edit, even when checks pass.

## 4. Site and publication review

- Landing page leads with the no-hallucinations summary.
- All entries and findings are readable in tables; category pages, calculator, sources, methodology, and Flagged for Review are navigable on desktop and mobile.
- Controls have labels, keyboard focus is visible, contrast is readable, and the site works with relative GitHub Pages paths.
- Build and internal-link checks pass; external source links point to the intended official page.
- The merged commit, successful Pages deployment, and live rendered content are matched. A green build alone is not proof of deployment.
- Flagged irregularities do not block publication, but they must remain visible and must not be converted into verified claims.

## Review reporting

Each finding receives a severity, exact file/row or live URL, quoted claim, evidence, and requested disposition. Findings are observations about evidence quality—not accusations of intent. Irregularities that cannot be resolved remain published for user review.
