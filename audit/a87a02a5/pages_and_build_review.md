# Site, build and deployment review — S-A87A02A5 (2026-10-23)

Scope: does the published GitHub Pages site build, serve, link and compute correctly, and
does it lead with the No-Hallucinations rule the project requires? Read-only review — no
generated page, stylesheet, generator or workflow was edited by this session.

Verified against `main` @ `161dbe1fe5529acb4ee491aa87f99abdb9d08823` (PR #32).
Exact archived command output: [`check_runs/`](check_runs/).

---

## 1. Deployment state (authoritative, from `api.github.com`)

| Property | Value |
|---|---|
| Pages status | `built` |
| Live URL | https://karagemop466-tech.github.io/GOLD2/ |
| Build type | `legacy` |
| Source | branch `main`, path `/` |
| HTTPS enforced | `true` |
| Latest build commit | `161dbe1fe5529acb4ee491aa87f99abdb9d08823` — **the current `main` HEAD** |
| Build timestamps | created 2026-10-23T10:55:39Z, updated 2026-10-23T10:55:58Z |

Workflow runs on `161dbe1`, all `completed/success`:

- `pages-build-deployment`
- `GOLD2 verify`
- `Legacy dashboard verify`
- `Evidence dashboard`

**Deployment is current:** the built commit is the same commit this review ran against, so
the bytes reviewed here are the bytes GitHub Pages is serving. No stale deployment.

---

## 2. Reproducibility — the strongest anti-hallucination control available offline

The committed pages were regenerated from the committed data in a scratch copy, then
compared byte for byte with what is committed:

```
python3 tools/build_site.py    -> built 11 pages
node scripts/build.mjs         -> Built 13 static pages; 41 product rows; 77 source records
python3 scripts/build.py       -> Built 6 pages and data.json
diff -rq <scratch> <repo>      -> IDENTICAL
```

**Result: the committed 46-page site is byte-for-byte reproducible from committed data.**
No page carries a number that its generator and data do not produce. This is the control
that catches the defect class this repository has been bitten by three times — a correct
data file with a stale typed number left in the rendered prose.

Why this matters for deployment review: `bash` in this sandbox cannot reach
`karagemop466-tech.github.io` (host allowlist), and `fetch_page` was failing during the
review window (FIND-A87A-08). So instead of claiming a browser inspection that did not
happen, the deployed bytes were verified indirectly and honestly: GitHub Pages reports
`built` for commit `161dbe1`, and the pages produced from `161dbe1`'s data are identical to
the pages committed at `161dbe1`.

---

## 3. Serving check — all 46 pages over HTTP

`node scripts/serve.mjs` bound `0.0.0.0:4173` and every committed page was requested:

```
200 OK: 46 pages | non-200: 0
```

No 404s, no redirects to a missing target, no page that fails to serve.

---

## 4. Link integrity

From `node scripts/check-links.mjs` (archived at `check_runs/check_links.txt`):

```
PASS links: 46 pages, 102 local targets, 177 external publisher URLs;
every data-table row has an official publisher link.
External HTTP status is not certified.
```

The requirement "every table row must have a source link to an official site" is met
structurally. This session re-verified it independently, without reusing that script:
scanner checks **C11/C13** confirm for all 30 root rows that (a) the row's rendered
`data-source-url` equals the registered `source_url`, (b) the row contains an `https://`
anchor to that exact URL, and (c) that URL's host is in the seller's own registered
`domains` list from `data/retailers.json`. Zero failures.

External HTTP status is *not* certified by that script, and this session does not certify
it either: six official URLs were re-read live today, and the rest are listed as not
re-read in [`live_verification_2026-10-23.md`](live_verification_2026-10-23.md) §2.

---

## 5. The No-Hallucinations rule on the front page

Requirement: the no-hallucinations statement must be in the front-page top summary, and
verification must refer back to it.

| Page | First text a reader meets in `<main>` |
|---|---|
| `/GOLD2/index.html` (front page) | "**No hallucinations. No invented prices.** Root register covers 30 source-checked entries across 9 official sellers … and 36 published flags." |
| `/GOLD2/explore/` | "! No hallucinations. No invented prices. Only source-backed observations. **Blank means unverified, never zero.** Seller claims are not independent tests." |
| `/GOLD2/dashboard/index.html` | "**Strict No-Hallucinations Policy** No hallucinations. No invented prices. Verified line by line (2026-10-23). Every value … is backed by a dated verbatim excerpt from an officia[l source]" |
| `/GOLD2/site/index.html` (preserved legacy) | "THE EVIDENCE EDIT / GOLD RESEARCH" — the rule appears early in the page but is not the first line |

A sweep of all **46** pages found the rule referenced near the top of every one
(46/46). The front page also carries a dedicated banner whose closing line is the standing
instruction: *"Look for hallucinations again after every review."*

Counts in that top summary are **derived**, not typed: 30 entries, 9 sellers, 36 flags,
17 of 30, 7 of 30, 23 of 30 all match values computed from the registers at review time.

---

## 6. Pre-existing check suites — all re-run unmodified on `161dbe1`

| Suite | Command | Result |
|---|---|---|
| Root QA / hallucination audit | `python3 tools/qa.py` | **PASS** — 11 checks, 0 failures, 3 warnings |
| Combined evidence consistency | `node scripts/verify.mjs` | **PASS** — 41 products, 77 source records, 25 findings, 0 purchase approvals |
| Node test suite | `npm test` | **PASS** — 23 pass, 0 fail |
| Local + external link check | `node scripts/check-links.mjs` | **PASS** — 46 pages, 102 local targets, 177 external URLs |
| Static security / CSP | `node scripts/security.mjs` | **PASS** — 46 HTML pages, 6 runtime files, 104 source files, 4 pinned workflows |
| Dependency audit | `npm audit --audit-level=low` | **0 vulnerabilities** |
| Real Chromium + axe (WCAG 2.1 AA) | `node scripts/browser-tests.mjs` | **PASS** — 13 expanded + 33 companion/root/preserved pages, desktop and mobile, 41 automatic gates, filters, calculators, stale warning, no-JS path, zero external runtime requests, no axe violations in exercised states |
| Calculator unit tests | `node tools/test_calculator.js` | **PASS** — formula, dated VRAI case, asking comparisons, blanks, invalid inputs, negative difference, formatting |
| Independent snapshot audit | `python3 reviews/independent_snapshot_audit.py .` | **PASS** — includes recomputed quick-reference rows (22K → $711.64, 24K → $776.33) |
| Peer security/hallucination scanner | `python3 audit/8c810c15/security_and_hallucination_scanner.py .` | **0 findings, 202 controls passed** |
| Peer calculator/scanner tests | `python3 audit/8c810c15/test_calculator_and_scanner.py` | **OK** — 6/6 |
| Legacy `site/` audit + tests | `python3 scripts/audit.py`, `node scripts/test.js` | **PASS** — 2 records, 6 pages; calculator null/invalid/nominal cases |

Three warnings from `tools/qa.py` are **intentional coverage disclosures, not defects**:
the gold header quote-as-of is unconfirmed (F-026); some rows have no explicitly assigned
price; some rows have no published metal weight.

### This session's own additions

| Suite | Command | Result |
|---|---|---|
| Independent provenance / hallucination scan | `python3 audit/a87a02a5/hallucination_provenance_scan.py .` | **PASS** — 0 failures, 13 warnings, **986 controls** |
| Its mutation controls | `python3 audit/a87a02a5/test_scan.py` | **OK — 22/22** |

---

## 7. Calculator review

`assets/calculator.js` and the dashboard calculators were reviewed for the one failure mode
that matters here: inventing a number the source did not give.

- Missing weights are **never** substituted. Where `weight_g` is null the row renders a
  blank marker and the Melt column renders `—`; the scanner enforces this (check C12) and
  a mutation control proves that rendering a gram figure for a null weight fails the scan.
- Output is labelled theoretical/conditional, not an appraisal or resale value.
- Unit handling uses the NIST constant `31.1034768 g` per troy ounce, matching
  `data/gold-price.json`; the scanner re-checks that constant and fails if it drifts.
- Every displayed melt figure on `prices.html` was **recomputed independently** from stored
  gross weight, karat and the stored reference, and matched to the cent (check C16),
  including both the 2 g / 4 g / 6 g quick-reference grid and the two product rows.

---

## 8. What this review does not certify

- **Not a browser inspection of the live URL.** `github.io` is outside this sandbox's
  outbound allowlist and `fetch_page` was failing during the window; deployment was
  confirmed through the GitHub Pages API plus byte-identical local reproduction of the
  built commit. Stated as a limitation rather than claimed as a live read.
- **Not a certification that external links will resolve later.** 177 external publisher
  URLs are structurally present and were retrieved by the sessions that recorded them;
  this session re-read six of them today.
- **Not an accessibility certification.** The axe run covers exercised states at WCAG 2.1
  A/AA in real Chromium; it is not a full audit and not a legal conformance claim.
- **Not proof of source truth.** Every suite above checks consistency, provenance and
  arithmetic. None can prove that a quoted page said what the quote claims, that a price is
  still current, or that any ring is actually the stated purity.
- **Not a purchase recommendation.** Zero rows in this repository are approved purchases.

**Look for hallucinations again after every review**, including after this one.
