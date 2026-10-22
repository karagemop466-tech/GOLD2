# COORDINATION — GOLD2

Shared task board for parallel agent sessions working on this repository.
**Read this file before starting any work. Claim a task before editing files.**

- Repository: `karagemop466-tech/GOLD2`
- Session branch in use: `arena/6ca03571-gold2`
- Session ID for this session: **S-6CA03571**
- Last updated: 2026-10-22 (UTC)

---

## 0. Environment constraint on branches (important)

The instructions for this project describe per-task branches named
`session-<id>/<task>`. The execution environment for this session is bound to a
single branch, `arena/6ca03571-gold2`, and does not permit creating or pushing
other branches. To keep the *intent* of the rule (no two sessions editing the
same file at the same time) while respecting the environment:

- Every task has an explicit, non-overlapping **file scope** (listed below).
- Sessions commit only inside their claimed scope, on the session branch.
- Shared entry points (`site/index.html`, `site/assets/nav.js`, `data/manifest.json`)
  are owned by the integration task only.
- Anything that would require editing a file outside a claimed scope is logged in
  section 5 (Requests / handoffs) instead of being edited.

This deviation is recorded here rather than silently ignored.

---

## 1. Ground rules

1. **No hallucinations.** Every factual value in `data/` must be copied from a page
   that was actually retrieved, and must carry the `source_url` + `retrieved_at`
   (UTC date) it came from. If a value is not present on the retrieved page it stays
   `null` and is added to the flags list. Values are never inferred, averaged,
   estimated, or carried over from a search-result snippet.
2. **Price currency of record is USD.** Non-USD prices are recorded with their
   currency and not converted unless an official FX rate is captured and cited.
3. **Price basis must be labelled.** A "setting price" excludes the center stone.
   It is never compared with a complete-ring price.
4. **Tier-1 sources only for product facts:** the retailer's own product page.
   Policies: the retailer's own policy page. Gold price: World Gold Council
   (ICE Data Services) quote with date, or LBMA if a citable value is available.
   Search snippets, aggregators, blogs and marketplaces are **not** sources of record.
5. **Evidence archive.** Every retrieved page is echoed into `evidence/` with its
   URL, retrieval timestamp and the exact text used. The JSON records point at the
   evidence file. This is what makes the "no hallucination" claim auditable.
6. Small, frequent commits. `git pull --rebase` before every push.
7. Never mark a row `verified` without a source URL that a human can open.

---

## 2. Task board

Status values: `unclaimed` · `in progress` · `done` · `needs review` · `blocked`

| ID  | Task | Status | Owner | File scope (exclusive) |
|-----|------|--------|-------|------------------------|
| T01 | Gold price reference + melt-value calculator data | in progress | S-6CA03571 | `data/gold-price.json`, `evidence/gold-price.md`, `site/calculator.html` |
| T02 | Retailer policies (returns, contact, payment, hallmark statements) | in progress | S-6CA03571 | `data/retailers.json`, `evidence/retailers/**` |
| T03 | Listings: solitaire | in progress | S-6CA03571 | `data/listings/solitaire.json`, `evidence/listings/solitaire/**` |
| T04 | Listings: halo & pavé | in progress | S-6CA03571 | `data/listings/halo-pave.json`, `evidence/listings/halo-pave/**` |
| T05 | Listings: three-stone & vintage | in progress | S-6CA03571 | `data/listings/three-stone-vintage.json`, `evidence/listings/three-stone-vintage/**` |
| T06 | Listings: 18K / high-karat | in progress | S-6CA03571 | `data/listings/18k.json`, `evidence/listings/18k/**` |
| T07 | Listings: 10K/14K lower-price band | in progress | S-6CA03571 | `data/listings/budget.json`, `evidence/listings/budget/**` |
| T08 | Flagged-for-review dataset + unverified register | in progress | S-6CA03571 | `data/flags.json`, `site/flags.html` |
| T09 | Site build: generator, templates, styles, nav | in progress | S-6CA03571 | `tools/**`, `site/assets/**`, `site/*.html` (except `site/calculator.html`, `site/flags.html`) |
| T10 | QA: hallucination audit, link check, build check | in progress | S-6CA03571 | `tools/qa.py`, `reports/qa-report.md` |
| T11 | Final integration: merge, re-verify, publish, PR | in progress | S-6CA03571 | `COORDINATION.md`, `README.md`, `.github/workflows/**`, `data/manifest.json` |

> Why everything is claimed by one session: this session is the only active agent
> in this environment. The tasks are still split into disjoint scopes so a second
> session can take over any single task without file conflicts. A task whose claim
> is older than 60 minutes with no commits may be taken over (see section 4).

---

## 3. Verification log (append-only)

| UTC timestamp | Task | What was checked | Source | Result |
|---------------|------|------------------|--------|--------|
| 2026-10-22 | T01 | World Gold Council gold spot page reachable; USD/oz quote read | https://www.gold.org/goldhub/data/gold-prices | Quote captured with date; see `data/gold-price.json` |
| 2026-10-22 | T01 | LBMA public price table | https://www.lbma.org.uk/prices-and-data/precious-metal-prices | **Blocked**: LBMA moved tabulated data to MyLBMA portal behind IBA licence. No free citable value. Recorded as limitation, not guessed. |
| 2026-10-22 | T03 | Blue Nile product page renders live price + karat + width | https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639 | Price shown as "(Setting Price)" → `price_basis=setting_price` |

---

## 4. Crash / takeover log

_None yet._

---

## 5. Requests / handoffs / conflicts

_None yet._

---

## 6. Integration record

- PR: _pending_
- Merge commit: _pending_
- Pages deployment: _pending_
- Post-deploy URL check: _pending_
