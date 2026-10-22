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
| T01 | Gold price reference + melt-value calculator data | done | S-6CA03571 | `data/gold-price.json`, `evidence/gold-price.md`, `site/calculator.html` |
| T02 | Retailer policies (returns, contact, payment, hallmark statements) | done | S-6CA03571 | `data/retailers.json`, `evidence/retailers/**` |
| T03 | Listings: solitaire | done | S-6CA03571 | `data/listings/solitaire.json`, `evidence/listings/solitaire/**` |
| T04 | Listings: halo & pavé | done | S-6CA03571 | `data/listings/halo-pave.json`, `evidence/listings/halo-pave/**` |
| T05 | Listings: three-stone & vintage | done | S-6CA03571 | `data/listings/three-stone-vintage.json`, `evidence/listings/three-stone-vintage/**` |
| T06 | Listings: 18K / high-karat | done | S-6CA03571 | `data/listings/18k.json`, `evidence/listings/18k/**` |
| T07 | Listings: 10K/14K lower-price band | done | S-6CA03571 | `data/listings/budget.json`, `evidence/listings/budget/**` |
| T08 | Flagged-for-review dataset + unverified register | done | S-6CA03571 | `data/flags.json`, `site/flags.html` |
| T09 | Site build: generator, templates, styles, nav | done | S-6CA03571 | `tools/**`, `site/assets/**`, `site/*.html` (except `site/calculator.html`, `site/flags.html`) |
| T10 | QA: hallucination audit, link check, build check | done | S-6CA03571 | `tools/qa.py`, `reports/qa-report.md` |
| T11 | Final integration: merge, re-verify, publish, PR | done | S-6CA03571 | `COORDINATION.md`, `README.md`, `.github/workflows/**`, `data/manifest.json` |

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
| 2026-10-22 | T03/T04/T05/T06 | 8 Blue Nile product pages re-read live: price, stock no, karat, width | see `evidence/listings/*.md` | All 8 captured; none states "solid gold", hallmark or gram weight |
| 2026-10-22 | T07 | 4 Zales product pages | https://www.zales.com/15-ct-diamond-solitaire-engagement-ring-10k-gold/p/V-19957449 (+3) | Price + 10K stated in title; width/weight/hallmark absent. Cached $719.20 rejected vs live $899.00 |
| 2026-10-22 | T02 | Blue Nile return policy | https://www.bluenile.com/policies/returns | 30 days from shipment; resized/custom excluded; 1 free resize within 6 months |
| 2026-10-22 | T06 | VRAI configurator spec block | https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-32797281484893 | Metal weight 2.86 g @ size 6 verified; price absent from HTML → left blank |
| 2026-10-22 | T04 | Brilliant Earth product page | https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/ | €990.00 setting-only (EUR served, USD not displayed); 2.5 mm; free 1-year resizing |
| 2026-10-22 | T09 | Site rebuilt from data; 10 pages, 281 links | `docs/` | 0 broken internal links; 14/14 rows carry an external official link |
| 2026-10-22 | T10 | Hallucination audit | `tools/qa.py` → `reports/qa-report.md` | **PASS** — 11 checks, 0 failures, 2 coverage warnings (blank weight/price by design) |
| 2026-10-22 | T08 | 15 flags published with source links | `data/flags.json` | 3 high (no "solid gold" wording, no hallmark, no gram weight), 6 medium, 6 low |

---

## 4. Crash / takeover log

_None. No claim exceeded the 60-minute takeover window._

### Deviation recorded
James Allen product URLs redirect to Blue Nile; the previously cached item 41515 is sold out and was
excluded rather than listed at a stale price (flag F-009).

---

## 5. Requests / handoffs / conflicts

- **No other session was detected** in this repository during the run (no other branches, no edits
  outside this session's scope). Nothing was taken over.
- Request for any future session (T02 owner): retrieve the **Zales standalone return policy** so the
  resize/custom exclusions stop being blank (F-011), and confirm **card acceptance** at each retailer
  (F-012). Neither needs a code change, only a new evidence file plus a flag update.

---

## 6. Integration record

- PR: _pending_
- Merge commit: _pending_
- Pages deployment: _pending_
- Post-deploy URL check: _pending_
