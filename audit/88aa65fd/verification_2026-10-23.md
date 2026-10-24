# S-88AA65FD — live line-by-line verification, 2026-10-23 (UTC)

Independent pass. Every value below was read from the official page during this session; nothing is copied
from an earlier session's transcript. Retrieval tool: `fetch_page` direct retrieval (this sandbox has no
outbound `curl` route, so no HTTP status sweep was possible — see §4).

**No hallucinations rule for this file:** a row is written only from text that appeared in the fetched
document. Where a page did not state something, the row says so and no value is supplied.

## 1. Re-read rows and exact rendering

| # | Official URL | Retrieved (UTC) | Verbatim text observed | Stored value before this pass | Result |
|---|---|---|---|---|---|
| 1 | https://www.gold.org/goldhub/data/gold-prices | 2026-10-23T23:41Z | `USD` `/oz` `-` `3,995.47`; chart `Data as of 22 October, 2026`; `Market Data: Provided by ICE Data Services.` | 3,996.31 | **CHANGED** — moving header. 3,996.31 moved to `superseded_observations`. |
| 2 | https://www.automicgold.com/products/coffin-ring.js | 2026-10-23T23:42Z | `"price":191000,"price_min":191000,"price_max":223300` | $1,910 default / $2,233 max | match |
| 3 | https://www.automicgold.com/products/cushion-diamond-signet-ring.js | 2026-10-23T23:43Z | `"price":240800` … variant `14k Yellow Gold / Salt and Pepper Diamond` `"price":275800` … `"price_max":325300` | $2,758 default, $2,408–$3,253 | match |
| 4 | https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html | 2026-10-23T23:44Z | `Now: US$3,004.00`; `14K Solid Gold`; `3.80 grams`; `0.94 Ct.`; `Natural` | $3,004; 3.8 g; 14K; 0.94 ct natural | match |
| 5 | https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/ | 2026-10-23T23:45Z | `$1,299.99`; `Weight:1.25 Grams`; `Karat stamped inside the band.` | $1,299.99; 1.25 g; karat stamp stated | match |
| 6 | https://mene.com/products/rose-ring-gold | 2026-10-23T23:46Z | `$1,325` `USD`; `This is a Crafted-on-Demand item.` | $1,336 | **CHANGED** — reprice. |
| 7 | https://mene.com/products/knot-ring-gold | 2026-10-23T23:47Z | `$1,442` `USD`; `Crafted-on-Demand` | $1,454 | **CHANGED** — reprice. |
| 8 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3 | 2026-10-23T23:48Z | `fine (24 karat) gold`; `composed throughout of an alloy of gold (i.e., gold that is less than 24 karats)`; page banner `up to date as of 10/21/2026`, `Title 16 was last amended 10/19/2026` | — | **DEFECT FOUND** — the stored quote `an item marked 18 k is made of 75 % gold` **does not appear** on this page. |
| 9 | https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry | 2026-10-23T23:49Z | All eight stored `ftc-jewelry` quotes present verbatim, including `A piece of jewelry marked 18K gold is 18 parts gold mixed with six parts of another metal.` | — | all eight match; the 75 % figure is **arithmetic** (18 ÷ 24), not a quote anywhere. |

## 2. What the re-read establishes

1. **Gold reference moved again.** The moving WGC header rendered 3,995.47, not the stored 3,996.31. The chart
   date stayed `22 October, 2026`, which again shows the chart date cannot be used as the header's quote time
   (F-026 stands, unresolved).
2. **Menē repriced two rings** in the direction of a slightly lower metal reference: Rose Ring 1,336 → 1,325,
   Knot Ring 1,454 → 1,442. Menē states both pieces are sold by weight and priced from metal value, so these
   remain dated observations, never live quotes.
3. **The Automic, Sarraf and Factory Direct data matched byte-for-byte** on the fields the register publishes
   (default amount, variant range, karat wording, approximate metal weight, karat-stamp statement).
4. **One fabricated-verbatim defect was found and fixed** (item 8/9 above): a sentence presented as a quoted
   excerpt of 16 CFR 23.3 appears on neither the cited regulation nor the FTC consumer page. It is now stored
   as nominal arithmetic with the verified FTC sentence alongside it, and published as flag **F-044**.
5. **One new seller self-contradiction was found** (item 5): the same Factory Direct page says
   `Handcrafted in our Los Angeles factory since 1985` and `We've been making jewelry in our Los Angeles
   factory since 1988`. Price, weight and stamp statements are unaffected. Published as **F-043**.

## 3. Not re-read in this pass — stated, not implied

- **35 of the 44** combined-catalog product rows were **not** re-read in this pass. Their previously recorded
  observation dates remain the only dates attached to them.
- **26 of the 30** root-register rows were **not** re-read in this pass (the 4 re-read here are AG-COFFIN-RING,
  AG-CUSHION-SIGNET, SAR-147370 and FDJ-GR0001).
- **76 of the 86** evidence source records were **not** re-fetched, including every BBB profile, every returns
  policy except those already dated 2026-10-23, and the NIST and LBMA records.
- **Zero** physical rings were handled, weighed on a scale, or XRF-tested. **Zero** purchases were approved.
  A page saying "solid gold" or "14K" is a seller statement, not an assay.

## 4. Tooling limitation recorded

`curl`/`wget` from this sandbox fail at TLS (`SSL_ERROR_SYSCALL`), so no external HTTP status sweep was run.
`scripts/check-links.mjs` therefore still reports structural link coverage only, and this pass does not claim
that any external publisher URL returned 200. Only the nine URLs in §1 were actually retrieved, and each one
was retrieved through the page-reading tool.

## 5. Hallucination scan run after the review

`audit/88aa65fd/hallucination_scan.py` is an independent scanner that imports neither `tools/qa.py` nor
`scripts/verify.mjs`. It checks, among other things: every catalog price equals a string inside its own
evidence quote; every rendered gold figure equals a recorded observation and never a superseded one; every
flag title count equals its affected-item count; every register count in prose equals the JSON; and every
"verbatim" evidence quote appears inside its own evidence markdown file. Mutation controls are in §6 of its
output and in `audit/88aa65fd/scan_results.txt`.

**This pass is one review, not a certificate.** Re-open the official sources and look for hallucinations
again after every review.

## 6. Rebase reconciliation with session S-1B04074F (PR #45, merged while this pass ran)

`origin/main` advanced to `e34d10c` during this pass. The peer session independently re-read the same World
Gold Council page and recorded **the same 3,995.47** value at 23:45Z, and independently recomputed the same
calculator expectations (SAR 13.40 g 14K melt 1004.108234 / 73.7231 %, FDJ 0.976 g net → 73.1350). That is
independent corroboration, not duplication: two sessions, two fetches, one number.

Resolutions, none of which discard peer work:

- `research/evidence.json` — the peer's later `observedAt` (23:45Z) kept for the WGC record, with one merged
  note crediting both sessions; this pass's Menē notes kept because they carry the superseded amounts.
- `data/gold-price.json` — both sessions agreed on the value and superseded chain; this pass's explicit
  `23:41Z` timestamps kept, peer's four-entry superseded list preserved.
- `data/verification-log.json` — the peer's richer F-039/F-028 notes kept and extended with this pass's
  confirmation and re-read timestamps; `GOLD-QUOTE` credits both reads.
- `README.md`, generated pages, `reports/qa-report.md` — peer text kept where it already stated the late-evening
  read; every generated artifact rebuilt from the merged sources rather than hand-merged.
- `dashboard/scripts/calc-test.js` — this pass's labels and tighter tolerance kept; the numeric expectations are
  identical in both versions.

Two warnings remain from the peer's scanner and are **explained, not suppressed**: `flags.html` and
`explore/calculator/index.html` mention a gold spot without printing the current figure. That is deliberate —
flag prose must not restate a moving header value, and the explore calculator ships no invented default spot
("No invented fallback price"). Neither page displays a stale number; both simply display none.

## 7. Final gate results on the rebased tree

`tools/qa.py` **PASS 12 / 0 / 3** · `verify` **44 products / 86 sources / 27 findings / 0 approvals** ·
`node --test` 23/23 · `check-links` PASS (46 pages / 102 local / 179 external, status not certified) ·
`security` PASS + `npm audit` 0 · dashboard build + `verify --check-build` PASS · `calc-test` PASS ·
`tools/test_calculator.js` PASS · Chromium + axe PASS · nine independent scanners PASS ·
this pass's scanner **10 checks / 0 failures / 6-of-6 mutation controls** · three generators run twice →
byte-identical tree.

**Open and published, not blocking:** F-026 (header quote time unconfirmed), F-043, F-044, 20 of 30 root rows
without an assigned price, 23 of 30 without a metal weight, 35 combined rows and 26 root rows not re-read in
this pass, and zero physical/XRF/scale verification or purchase approvals.
