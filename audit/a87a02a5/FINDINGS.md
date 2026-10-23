# Flagged for review — independent verification pass S-A87A02A5 (2026-10-23)

**No hallucinations.** Every finding below was read out of a committed file or an official
page retrieved today, and each one names where it came from. Nothing is inferred,
estimated, averaged, or filled in from a neighbouring value. Where this session could not
re-read a page, that is stated plainly instead of being presented as a verification.

Machine-readable copy for the Flagged for Review register: [`findings.json`](findings.json).
Live source observations: [`live_verification_2026-10-23.md`](live_verification_2026-10-23.md).
Build/deployment review: [`pages_and_build_review.md`](pages_and_build_review.md).

Verified against `main` @ `161dbe1` (PR #32). Ten findings: **8 open, 2 resolved by peer
sessions while this pass was running.**

---

## Summary table

| ID | Sev | Status | Finding | Where it was read from |
|---|---|---|---|---|
| [FIND-A87A-01](#find-a87a-01--high--open) | high | open | Three concurrent sessions claimed the same shared files | `git ls-remote` + per-branch commit reads |
| [FIND-A87A-02](#find-a87a-02--medium--open) | medium | open | 3 of 30 root rows are missing from the "all 41 researched entries" register | `data/catalog.json`, `research/evidence.json`, `explore/**` |
| [FIND-A87A-03](#find-a87a-03--medium--open) | medium | open | $2,758 published with no configuration scope; seller data shows $2,408–$3,253 | `automicgold.com/products/cushion-diamond-signet-ring.js` |
| [FIND-A87A-04](#find-a87a-04--medium--open) | medium | open | Derived 0.976 g net weight and $73.67 melt published in flag prose on 8 pages | `data/flags.json` + rendered sweep of all 46 pages |
| [FIND-A87A-05](#find-a87a-05--medium--open) | medium | open | README counts contradict the data they document (5 instances) | `README.md` vs registers and suite output |
| [FIND-A87A-06](#find-a87a-06--low--open) | low | open | One evidence file uses a different quoting convention; extractors see zero quotes | `evidence/listings/fdj-gr0001.md` |
| [FIND-A87A-07](#find-a87a-07--low--open) | low | open | Three gross weights quoted only in markdown, not in `field_evidence` | scanner checks C03/C05 |
| [FIND-A87A-08](#find-a87a-08--informational--open) | info | open | Retrieval failure limited this pass to six official URLs | five identical proxy error responses |
| [FIND-A87A-09](#find-a87a-09--medium--resolved-by-peer) | medium | **resolved** | F-001/F-002/F-003 prose counts were stale ("16 of 20" vs 30 rows) | `data/flags.json` before/after PR #32 |
| [FIND-A87A-10](#find-a87a-10--medium--resolved-by-peer) | medium | **resolved** | Gold reference was one day stale; the source itself is volatile | `gold.org/goldhub/data/gold-prices` |

**None of these blocks publication.** All are published for review, per the board's rule
that `needs review` does not block anything.

---

## FIND-A87A-01 · high · open

### Three concurrent sessions claimed the same shared files at the same time

Between **09:54Z and 09:58Z on 2026-10-23**, four sessions pushed claims to
`COORDINATION.md`. Three of them overlap on the same files:

| Session | Claimed (overlap in bold) |
|---|---|
| `S-062F314F` | `data/catalog.json`, **`data/gold-price.json`**, `research/evidence.json`, **`evidence/**`**, **`tools/**`**, `scripts/**`, **`reports/**`** |
| `S-8B9E189A` | `data/solid-gold-verified.json`, `data/listings/**`, **`data/gold-price.json`**, `data/flags.json`, **`evidence/**`**, `tools/build_site.py`, `tools/qa.py`, `assets/**`, root `*.html`, **`reports/**`** |
| `S-B200A880` | **`data/gold-price.json`**, `evidence/gold-price.md`, **`tools/**`**, root `*.html`, `assets/**`, **`reports/**`**, `README.md`, `COORDINATION.md` |

The board's own rule is that scopes stay non-overlapping and that a file owned by another
session is changed by logging a request rather than editing it. `S-9B875C81` noticed the
same collision and logged it; this session confirms it and adds the observed consequence.

**What it actually cost this pass:** the same official gold URL was fetched independently
by at least two sessions and produced two different same-day values (`$4,024.45` stored by
a peer, `$4,023.19` observed here) — not a contradiction, but two honest reads of a moving
figure with no owner to decide which one is published. Meanwhile the root register grew
from 20 to 30 rows *while* this session was verifying it, so every count in this document
had to be recomputed against the newer tree before publication.

**Recommended:** give shared registers one owner per pass, or serialise merges through a
single integration branch. Verification-only sessions should claim a read-only audit
directory (as this one did) and file requests instead of edits.

---

## FIND-A87A-02 · medium · open

### 3 of the 30 root-register rows are missing from the register the landing page calls "all researched entries"

`index.html` currently reads:

> Root register covers 30 source-checked entries across 9 official sellers … Open the
> 14-Page Companion Dashboard …, **all 41 researched entries across 12 sellers →**, …

Exact-match checks against `data/catalog.json`, `research/evidence.json` and every file
under `explore/` return **zero hits** for these three rows:

| Row | Official URL | Why its absence matters |
|---|---|---|
| `AG-COFFIN-RING` | https://www.automicgold.com/products/coffin-ring | the only root row publishing a **stone-free gold weight** (6.10 g) — the single most useful row for a melt calculation |
| `AG-CUSHION-SIGNET` | https://www.automicgold.com/products/cushion-diamond-signet-ring | $2,758, explicit "Solid 14k Gold" |
| `MJ-BOLD-ETERNITY` | https://mejuri.com/products/bold-diamond-eternity-ring | $2,900 (from), the highest-priced explicit-solid-gold row; **Mejuri is not among the 12 combined sellers at all** |

27 of 30 root rows *are* present. Across both registers the project has researched **44
distinct product URLs**, not 41.

**Recommended:** add the three rows to the combined register with their own dated source
records, or change the wording so no page implies that `explore/` holds everything. Two
registers that each claim completeness is the failure mode this project exists to avoid.

---

## FIND-A87A-03 · medium · open

### `$2,758` is real but unscoped — the seller's own data shows `$2,408–$3,253` for the same ring

The register stores, for `AG-CUSHION-SIGNET`: `price: 2758.0`, `currency: "USD"`,
`color: "Yellow"`, quote `"$2,758"`, `observed_native_display: null`.

The retailer's own product endpoint, retrieved **2026-10-23**, returns:

```
"price":240800, "price_min":240800, "price_max":325300, "price_varies":true
variant "14k Yellow Gold / Salt and Pepper Diamond" -> 275800   ($2,758.00)
variant "14k Yellow Gold / Clear Lab Diamond"       -> 240800   ($2,408.00)
variant "14k White Gold / Salt and Pepper Diamond"  -> 275800   ($2,758.00)
```

So `$2,758` **is** a price the seller charges today — this is not an invented number, and
the scanner confirms its digits appear in the stored quote. The problem is scope: two live
14k *yellow* gold configurations of the same ring differ by **$350**, and the row records
neither the stone option nor the range. A reader takes `$2,758` as the price of the ring.

`AG-COFFIN-RING` has the same shape at lower risk: `$1,910.00` is both `price_min` and the
recorded yellow-gold variant price, while the range runs to `$2,233.00`.

**Recommended:** record the observed range and the configuration the stored price belongs
to, following the pattern this repository already uses well for `MJ-BOLD-ETERNITY`, which
keeps the `From$2,900` qualifier inside its quote and links F-030. Do **not** average the
range, and do not promote one variant's price to a product price.

---

## FIND-A87A-04 · medium · open

### A derived net-metal weight and a `$73.67` melt figure are published in flag prose on eight pages

Rendered on `flags.html`, `verification.html`, `explore/review/index.html` and five
`dashboard/` pages for `FDJ-GR0001`:

> `0.274 g gem mass -> 0.976 g net 14K alloy = $73.67 melt if gross`

The arithmetic is **correct** and was recomputed independently here:

| Step | Calculation | Result |
|---|---|---|
| diamond mass | 1.37 ct × 0.2 g/ct | 0.274 g |
| assumed net metal | 1.25 g − 0.274 g | 0.976 g |
| fine gold at 14K | 0.976 g × 14/24 | 0.5693 g |
| melt at the stored reference | 0.5693 g × ($4,024.45 ÷ 31.1034768 g/ozt) | **$73.67** |

But it rests on three assumptions that no source states:

1. that the displayed **1.25 g is gross including the stones** — the same page says
   `Customize Your Options First to See Accurate Weight`, so 1.25 g is not a confirmed
   weight for any chosen configuration;
2. that **all 1.37 ct** of diamond mass sits inside that 1.25 g;
3. that the **entire remainder is 14K alloy** with no other material.

To its credit the register stays conservative: `weight_g` is `null` and the dashboard's
Melt column renders blank, so the derived figure lives only in prose. It also moves
whenever the gold reference moves, and it is a **dollar valuation**, which this project
elsewhere keeps behind an explicit acknowledged-hypothetical-scenario gate.

**Recommended:** route it through that existing scenario mechanism, label all three
assumptions inline, and state that the dollar figure is conditional arithmetic on a dated
moving reference rather than a valuation. Keep `weight_g` null and the Melt column blank.

---

## FIND-A87A-05 · medium · open

### README counts contradict the data they document

| README says | Data/suite actually reports | Verdict |
|---|---|---|
| "combined register contains **32** unique product URLs, **nine** sellers, **60** structured publisher records and **20** findings" | 41 products, 12 sellers, 77 sources, 25 findings (`scripts/verify.mjs` prints these) | **stale** |
| "all **30** HTML pages' static security" | 46 pages (`scripts/security.mjs`) | **stale** |
| "all **32** valuation gates" | 41 automatic gates (`scripts/browser-tests.mjs`) | **stale** |
| "`**31**` bidirectional flags `F-001`–`F-033`" | 36 flags (`data/flags.json`) | **stale** |
| root dashboard described as both "`**30**` entries across `6` categories" and "`**20**` entries across `6` categories" | 30 entries | **self-contradictory** |
| "13-page combined dashboard" | 13 `explore/` pages | correct |
| "23 Node tests" | 23 pass | correct |
| "`36` flags" | 36 | correct |

**Recommended:** derive README's counts from the registers the way `tools/build_site.py`
derives page counts, or add a check that fails when a README count disagrees with the
data. This is the same defect class the repository already fixed twice for HTML prose —
the README was simply outside that fix's reach.

---

## FIND-A87A-06 · low · open

### One evidence file uses a different quoting convention, so extractors see zero quotes

Every file in `evidence/listings/` transcribes page text inside **fenced code blocks** —
except `fdj-gr0001.md`, which uses inline code spans inside bullet labels:

```
- Hallmark: `Karat stamped inside the band.`
- Weight & Stones: `Weight:1.25 Grams` · `Total Carat Weight: 1.37cts`
```

Any checker that extracts only fenced blocks finds **no quotes at all** for that row and
reports its published `1.25 g` gross weight and `hallmark_stated: true` as unbacked. This
session's own scanner produced exactly that false failure on its first run against `main`
and had to be widened to accept both conventions.

**Recommended:** pick one convention, or make every quote-extracting checker accept both.
A provenance checker that silently reads zero quotes from a valid evidence file is worse
than no checker, because the tempting "fix" is to delete the value rather than the
mismatch.

---

## FIND-A87A-07 · low · open

### Three published gross weights are quoted only in markdown

`AG-CUSHION-SIGNET` (5.5 g), `AG-SAPPHIRE-RING` (1.2 g) and `FDJ-GR0001` (1.25 g) each
publish `gross_ring_weight_g` while `field_evidence` carries no quote for that key. The
supporting text exists in the evidence markdown, so **no value here is treated as
invented** — but the JSON register is not self-traceable: a reader looking only at the data
cannot see where the number came from.

`AG-SAPPHIRE-RING`'s quote was independently re-read live today —
`Item Weight` → `Approximately 1.2g (gold) or 1.8g (platinum)` — so that one is
corroborated twice.

**Recommended:** mirror the existing quote into `field_evidence.gross_ring_weight_g` for
all three. No value changes; only the provenance link becomes explicit.

---

## FIND-A87A-08 · informational · open

### A retrieval-infrastructure failure limited this pass to six official URLs

`fetch_page` returned an Alibaba OSS proxy error instead of page content on **five
attempts** between ~10:08Z and ~10:25Z:

```
SignatureDoesNotMatch — <EC>0002-00000040</EC>
```

This is a fault in the retrieval path. It is **not** a retailer refusal, bot block,
paywall or 404, and it is **not** evidence that any page changed. Rows that could not be
re-read are listed by name, with the value each carries, in
[`live_verification_2026-10-23.md`](live_verification_2026-10-23.md) §2 so the next pass
can target them first: `MJ-BOLD-ETERNITY` ($2,900), `BE-121H6` (EUR 990), the VRAI
`2.86 g` spec, the Coffin Ring `6.1 g` spec, and 24 further rows.

`bash` has no route to retailer hosts in this sandbox, so no `curl` cross-check was
possible either. That limitation is recorded rather than worked around.

---

## FIND-A87A-09 · medium · RESOLVED BY PEER (PR #32) during this pass

### F-001/F-002/F-003 prose counts were stale against the 30-row register

Detected on `main` @ `62b1bf6`. Four concrete contradictions, each verified against counts
computed from the registers:

| Flag | What it said | What the data says |
|---|---|---|
| F-001 title | "not stated on **16 of 20** items" | its own `affected_items` holds **17**; register holds **30**; `index.html`'s derived checklist on the same page already said "**17 of 30**" |
| F-001 detail | "**16 of the 20** … (the **4** Automic Gold and Mejuri rows …)" | **13** rows are `solid_gold_explicit: true` |
| F-002 detail | "None of the **20** captured product pages … Both fields remain **null, not false**" | 30 rows, and `FDJ-GR0001` has `hallmark_stated: true` |
| F-003 detail | title updated to "23 of 30" but detail said only two rows publish weights and "the other **18** weight fields remain blank" | **7** rows publish weights, **23** are blank |

The stale strings rendered on **eight** pages. Re-checked after PR #32 merged at 10:55Z:
all four are corrected, and `16 of 20` no longer appears anywhere in the repository.

**Recorded because it is the third recurrence of this defect class here**, and because the
fix updated flag *titles* before flag *details*. Recommended: derive detail counts the way
titles are derived, and add a check that fails when a flag's title count disagrees with the
length of its own `affected_items` list. This session's scanner check **C14** does exactly
that and is available to any owner of `tools/**`.

---

## FIND-A87A-10 · medium · RESOLVED BY PEER (PR #29/#30) during this pass

### The published gold reference was one day stale — and the source itself is volatile

At ~10:10Z the official page displayed **4,023.19** with `Data as of 22 October, 2026`,
while the repository published **4028.53** retrieved 2026-10-22. Every melt figure on the
site was therefore computed from a number the source no longer displayed. Peers refreshed
it to **4024.45** (retrieved 2026-10-23) mid-pass, which resolves the staleness.

The residual issue is structural, and this pass corroborates the repository's own F-026
rather than creating a new complaint — **three reads of one URL across two days returned
three different numbers**:

| Read (UTC) | Header value | Chart "Data as of" |
|---|---|---|
| 2026-10-22 | 4,028.53 | 21 October 2026 |
| 2026-10-23 (peer) | 4,024.45 | 22 October 2026 |
| 2026-10-23 ~10:10Z (this session) | **4,023.19** | 22 October 2026 |

The page publishes no quote-as-of timestamp for the header — only the label
`Last Updated`, with the date shown separately for the chart. Scale of the effect, as
**conditional arithmetic only** and not a valuation: the Coffin Ring case (6.10 g, 14K →
3.5583 g fine) is $460.88 at 4,028.53 and $460.27 at 4,023.19; the VRAI case (2.86 g, 18K
→ 2.1450 g fine) is $277.82 and $277.45.

**Recommended:** keep `quote_date` null, keep the retrieval timestamp beside every melt
output, keep labelling melt as theoretical, and consider surfacing the observed same-day
spread so a reader can see the reference move instead of trusting one figure.

---

## What this pass confirmed as correct

Publishing only problems would misrepresent the register. These were independently
checked and passed:

- **`AG-SAPPHIRE-RING`** — all five published values re-read live and matched exactly
  (`$526`, "Solid 14k Gold", 1.1 mm band, 1.1 mm height, 1.2 g gross item weight).
- **`AG-COFFIN-RING`** — `$1,910.00` re-read live from the seller's own endpoint.
- **`AG-CUSHION-SIGNET`** — `$2,758.00` is a genuine current amount for one configuration.
- **`VRAI-CLASSIC-4P`** — identity confirmed live; no price in the served HTML, so
  `price: null` is correct rather than missing.
- **Zero provenance failures** across 986 controls: no published price or weight anywhere
  in the 30-row register lacks a stored quote.
- **Every one of the 30 rows** cites an `https` product page on its own seller's
  registered domain, and every rendered table row links that exact URL.
- **All melt arithmetic** on `prices.html` recomputed from stored weight, karat and the
  NIST 31.1034768 g/ozt constant — correct to the cent.
- **All twelve pre-existing suites pass**, and the committed 46-page site is
  byte-for-byte reproducible from committed data.

---

## Standing instruction

**Look for hallucinations again after every review.** An automated PASS means only that the
stated controls passed. It cannot prove that a quoted page said what the quote claims, that
a price is still current, that a ring is the stated purity, or that a return will be
honoured. Re-open the official source, re-read the row, and treat the official page as
current whenever this table becomes stale.
