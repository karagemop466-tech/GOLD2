# Combined repository and evidence review

Session `arena-24aeb4a8` · research date **22 October 2026 UTC**.

## Integration scope and preservation

The assigned baseline `b00633e9fd6d3b2e82dcf21cbd4a8a6aabb7afe7` contained a one-line README. Other sessions subsequently published the initial two-setting dashboard and the 16-entry root register. Their data, source files, audits, independent review reports and implementations are preserved.

Main was integrated first through `7a45392`, then through **`49a84cb` (PRs #14–#16 included)**. These integrations carry field-scoped product evidence, broader official policy/payment/contact research, scoped independent-profile metrics, root calculator tests and updated negative controls. PR #16’s additional small-text contrast controls and darker root colors are retained. Merge conflicts in inherited implementation/data were resolved from newer main, then bounded corrections below were reapplied—not by replacing the newer work with the earlier root generator. Historical commit-specific reports are retained without being relabeled as current certifications.

The combined `explore/` subsite is additive. It includes **all 32 unique products across nine sellers**, deduplicating two shared Blue Nile product URLs. All 14 additional main products were directly retrieved during this session, alongside the original 18-product batch. One unavailable Auvere discovery lead remains a source limitation, not a product silently added to the register. A test confirms that every original root product URL appears exactly once in the combined catalog.

The fixed Arena branch is `arena/24aeb4a8-gold2`; the multi-session branching exception and ownership are recorded in `COORDINATION.md`. No rebase/force-push or edit to another session’s branch is used.

## Source and hallucination-risk review

The combined catalog has **60 structured publisher records and 20 findings**. Canonical facts have field references and configuration/observation scope. The preserved root files contain additional field-scoped policy and independent-profile evidence; “60” is the expanded register’s count, not a claim that the repository has only 60 URLs.

| Review concern | Current treatment |
| --- | --- |
| Unsupported USD from dollar signs | Twelve remaining root USD normalizations were withheld under F-025; two other root Zales amounts were already unassigned. Historic normalization/display strings remain labeled research history. Combined numeric prices are blank unless native currency is supported. |
| Native EUR setting price | BE121H6 retains the directly observed €990 setting-only price with EUR context, unselected center/size and contrasting prong metal. No USD conversion is invented. |
| Category assumptions | Bare settings use their own category; Zales/Catbird diamond origins remain unconfirmed where not established. Natural/lab labels on Blue Nile accents do not choose the center. |
| Grams versus gold | Seven Automic approximate Item Weight figures, two Auvere undefined Fine Weight ranges and VRAI’s seller-reported size-6 metal weight retain their different bases. No gross/item/shipping-weight fallback is allowed for verified gold calculations. |
| VRAI configuration | Plain band and Pavé carat weight 0.18ctw appear together. The inconsistency is recorded, not silently resolved or used as stone mass. The 2.86g claim is explicitly size 6, not independent weighing. |
| Policies | Quince’s engagement-ring purchase-based exception, Blue Nile shipment-based returns/exclusions, VRAI’s $300 engagement-ring fee and modification exclusions, and other source limitations remain visible. No item-specific independent-testing/return permission is inferred. Newer main policy/payment research is preserved. |
| Moving WGC panels | Header amount, chart date and retrieval date are distinct. Header `quote_date` is null; `chart_as_of_date` retains 21 October. F-026 corrects the inherited assumption that the chart dated the header. The negative audit now compares chart metadata to the chart field, not to a guessed header timestamp. |
| Gold-reference arithmetic | Expanded scenarios use a separately dated JM Bullion dealer body/table reference, not an LBMA fix. NIST troy conversion and nominal K/24 versus explicit fineness are distinguished. Documented products remain blocked from automatic valuation. Root examples are explicitly conditional. |
| Reputation/contact | Official contact pages and independent platform records are separate. Published numbers/emails were not contacted. Ratings, complaints, accreditation and absence of accreditation do not certify truth, actual gold or fraud. No physical item was examined. |

There are **10 numeric native-currency snapshots** (nine USD, one EUR), **22 blank prices**, **zero independently verified fine-gold weights** and **zero purchase approvals** in the combined catalog. The market survey is bounded; no budget, size or style preference is invented.

Short structured passages may be normalized factual transcriptions rather than raw/verbatim page archives. Observation timestamps belong to the recorded research window, not to seller quote-effective times. Builds and monitors do not renew them. Price snapshots become visibly stale after the documented interval.

## Implementation and security review

- Root pages remain generated by `tools/build_site.py`, not hand-patched only. All ten have a durable combined-dashboard link and a no-hallucinations notice.
- Root inline styles were moved deterministically into self-hosted CSS so restrictive CSP needs no `unsafe-inline`. Inline executable scripts/events, external runtime resources and unnecessary persistence are not used.
- The newer root calculator is preserved, with explicit conditional acknowledgement and nonfinite arithmetic rejection added. Hypothetical reference table rows now link official units/method/input sources. There are no asserted normal-retail multiples or guaranteed scrap floors.
- Combined fields are escaped; runtime DOM updates use text, not HTML injection. Publisher URLs are exact-allowlisted HTTPS and reject embedded credentials.
- Preview server binds `0.0.0.0`, supports `/GOLD2/`, accepts proxied hosts, denies private/traversal/write paths and supplies a working 404 fallback. Browser code does not call sandbox localhost.
- Four workflow files use full official Action commit SHAs and read-only contents permissions. Existing legacy Pages publication settings are retained. The source monitor is separate from verification and never rewrites facts/prices.
- Runtime code is package-dependency-free; development packages are exact-pinned with a lockfile. No credentials were added. Test screenshots/reports, dependencies and large generated artifacts remain ignored.

## Executed local verification

The final integration run must repeat the sequence in README after any further changes. The following have actually executed successfully after integrating the newer main implementation:

- Combined evidence consistency: **32 products / 60 sources / 20 findings**, with missing evidence published as warnings rather than fabricated values.
- **23 Node tests**, including source-price mutation rejection, currency context, numeric token boundaries (`€990.00` correctly supports 990, not 990.01), root-URL inclusion/deduplication, no gross-weight fallback, nominal/explicit purity, stale observations, deterministic generation and preview protections.
- Root audit: **10 check groups, zero failures**, with unconfirmed quote time and price/weight coverage warnings; root calculator unit controls pass.
- Independent static negative audit: **zero findings / six arithmetic controls**. This is a programmatic negative check, not an independent human re-review or physical certification.
- Local links: **29 HTML pages**, including all 13 expanded, ten root and six initial pages; official publisher link in every data-table row; local targets/fragments checked. Current external HTTP reachability is not certified by this test.
- Static security: **29 HTML pages, four runtime files and four pinned workflows**; npm audit reported **zero known vulnerabilities** at execution.
- Real Chromium: all **29 pages** load; all **32 automatic valuation gates** remain blocked; filters, injection-like search input, explicit conditional modes, optional asking price, Infinity/overflow rejection, staleness and no-JavaScript research are exercised. Desktop/mobile screenshots were visually inspected.
- Automated axe: **zero WCAG A/AA violations in exercised expanded desktop/mobile/scenario states**. The root pages were functionally/security checked; no claim of full root/legacy accessibility certification, cross-browser or manual assistive-technology testing is made.
- Browser report recorded **zero external runtime requests, page errors or console errors**.

Errors caught and fixed during execution included missing minimal-sandbox browser libraries, a malformed nominal option, conflicting brand accessible naming, a NOSCRIPT assertion harness issue, outdated runtime publisher allowlists, preview tests pointing at pre-extension paths, and a CSS-font assertion that incorrectly required a specific font-stack token. These are not hidden behind earlier PASS results.

GitHub CI and Pages publication are verified separately in the integration PR/deployment records; no local test result alone asserts deployment success.

## Continuing controls

The scheduled/manual official-source workflow writes a reachability/identity-word signal report and capped-content sample hashes. It has no automatic baseline comparison or price ingestion. Redirects stay on the HTTPS publisher allowlist. Bot blocking, region selection and JavaScript rendering can produce false alarms; a 200 response is not proof of source identity or price correctness.

After every review or combined-session edit, rerun source/hallucination-risk, build/link and security checks. **Automated checks cannot establish factual truth, physical weight/purity, return entitlement, complete security/accessibility or purchase suitability.** Reopen official sources and obtain exact-configuration documentation, written inspection/return permission, protected payment and independent professional verification before wear/resizing. If verification and a qualifying return are disallowed, do not purchase.

## Publication verification

PR #17 merged as `c008aede2481b79f3f88159b0f9dda87868f5b3a`. Its PR checks and post-merge Evidence dashboard run passed. Actual legacy Pages build/deployment run `39875762776` succeeded for that commit; Pages API reported built/HTTPS/main-root, and public landing/catalog URLs returned the 32-entry register. A public-page wording check then clarified that supported setting-only snapshots exclude the center; it no longer incorrectly says every setting-only display is withheld. A regression test covers the EUR setting display and that scope notice.

Manual dispatch of the optional source-monitor workflow was denied with GitHub HTTP 403 Resource not accessible by integration. Its scheduled/manual configuration is published, but no executed live-monitor result is claimed. Existing direct source observations and build/link checks are distinct from that unexecuted optional monitor.
