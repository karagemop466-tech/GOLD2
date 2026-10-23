# Live line-by-line verification — session S-E0D6DD62 (2026-10-23 UTC)

**Rule applied:** a stored value is reused only if the official page rendered it again during this pass.
Everything not re-read keeps its original observation date and is named below as *not re-read*. No value was
inferred, averaged, converted, or taken from a search snippet.

**Method:** `fetch_page` against the seller's own host. Where the seller publishes a JSON product endpoint on the
same host (`/products/<handle>.js`), it was used only to confirm that a displayed amount is configuration-scoped.

## 0. What this branch contains after reconciling with a parallel session

While this branch's pull request was in CI, a parallel session (**S-1EB9F828**, merged as PR #39) landed an
equivalent integration on `main`: the same three missing products, the same Cushion Signet / Coffin price ranges,
the same refreshed World Gold Council value, and the same re-derived README counts.

The conflict rule on this project's board says to resolve without discarding the other session's work, so the
duplicate implementation was **not** re-applied on top of theirs. This branch was reset onto `main` and keeps:

1. the peer's merged implementation as the single source of truth for the data changes; and
2. this session's additive work — the independent scanner, its mutation controls, this verification log, and one
   evidence-file defect that `main` still carried (see §4).

Because two sessions produced the same conclusions independently, `main`'s register now has an extra,
independent check behind it: this session's scanner (12 check families) passes against the merged tree, and its
8 mutation controls prove the checks actually fire.

## 1. Pages re-read in this pass

| # | Official URL | What re-rendered | Stored value | Outcome |
|---|---|---|---|---|
| 1 | https://www.automicgold.com/products/coffin-ring | `Coffin Ring`, `$1,910`, `Solid 14k Gold and 950 Platinum`, `950 platinum and/or Solid 14k gold`, `Band is 3mm`, `Approximately 6.1g (gold) or 9.2g (platinum)`, `Returns can be made within 30 days of the delivery date.` | 6.1 g, $1,910, 14K, 3.0 mm | **match** |
| 2 | https://www.automicgold.com/products/coffin-ring.js (same host) | `"price_min":191000`, `"price_max":223300`, `"price_varies":true` | range 1,910.00–2,233.00 | **match** against the published F-039 range |
| 3 | https://www.automicgold.com/products/cushion-diamond-signet-ring | `Cushion Diamond Signet Ring`, `$2,758`, `Solid 14k Gold and 950 Platinum`, `Salt and Pepper Diamond`, `Clear Lab Diamond` | $2,758, 14K | **match** |
| 4 | https://www.automicgold.com/products/cushion-diamond-signet-ring.js (same host) | `"price_min":240800`, `"price_max":325300`, `"price_varies":true` | range 2,408.00–3,253.00 | **match** against the published F-039 range |
| 5 | https://www.automicgold.com/products/24k-band.js (same host) | `"price":352000` | $3,520 | **match** |
| 6 | https://mejuri.com/products/bold-diamond-eternity-ring | `Bold Diamond Eternity Ring`, `From$2,900`, `Solid White Gold (14k)`, `handcrafted in 14k solid gold`, `Band Width: 2.6 mm`, `23 round brilliant cut diamonds`, `We offer free 30-day returns…`, engraving not returnable | price null (no ISO code), 2.6 mm, 14K | **match**; stays unassigned (F-025/F-030) |
| 7 | https://www.gold.org/goldhub/data/gold-prices | Header `3,996.31` USD/oz; chart `Data as of 22 October, 2026`; `Market Data: Provided by ICE Data Services.` | 3,996.31 | **match** |

Dead end: `https://www.automicgold.com/products/cushion-signet-ring.js` returned an empty document — a guessed
handle, not a seller page. It was not used as evidence and no value was taken from it.

## 2. Not re-read in this pass (no value changed)

Root register (30 rows): every row except `AG-COFFIN-RING`, `AG-CUSHION-SIGNET`, `AG-24K`, `MJ-BOLD-ETERNITY`:
`BN-194158`, `BN-195269`, `VRAI-CLASSIC-4P`, `Z-19957449`, `Z-20046552`, `BN-192506`, `BN-315661`, `BN-195402`,
`BN-302868`, `BN-316238`, `BN-203348`, `BN-195639`, `BN-194548`, `BE-121H6`, `BN-193625`, `Z-20303279`,
`Z-20301172`, `SAR-147370`, `SAR-145362`, `SAR-145364`, `SAR-144773`, `FDJ-GR0001`, `AG-SAPPHIRE-RING`.

Combined register (44 products): the same shortfall applies to the Catbird, Auvere, Quince, Menē, Blue Nile,
Zales, VRAI, Brilliant Earth, Sarraf, Factory Direct and Stone and Strand rows, except where they are the same
product page as a root row re-read above. **Not re-read is not the same as unverified and not the same as
invalidated** — each value keeps its own dated observation and evidence file.

Also not re-read this pass: every return, payment and contact policy page. Those observations keep their
2026-10-22 and 2026-10-23 dates.

## 3. Independent checks run against the merged tree

| Check family | What it proves | Result |
|---|---|---|
| C1 product-name provenance | every catalog name is a substring of its own cited passage | PASS (44) |
| C2 price/currency support | every assigned amount and currency appears in a cited passage | PASS |
| C3 root evidence files | every root price, weight and `field_evidence` quote appears in that row's own evidence file | PASS (30 rows) |
| C4 flag-title counts | a stated "N of M" equals the flag's own `affected_items` and the register size | PASS (37 flags) |
| C5 superseded values | no HTML page renders a superseded gold value | PASS (46 pages) |
| C6 gold JSON ↔ evidence file | the file carries the same current value and quotes as the JSON | PASS |
| C7 README counts | every published count equals the data | PASS |
| C8 USD labels | a USD label traces to a passage containing `USD`/`US$` | PASS |
| C9 arithmetic | published fine-gold grams and melt values re-derived from the dated reference | PASS |
| C10 placeholders | no TODO/FIXME/NaN/placeholder in any page | PASS |
| C11 official links | table rows link official publisher hosts | PASS (118 unique) |
| C12 gold figures | every gold amount named in the evidence file is a recorded observation | PASS |

`test_scanner.py` injects **8** realistic defects into a copy of the tree (invented price, missing currency
statement, superseded value left on a page, stale README count, flag-count mismatch, missing evidence quote,
placeholder text, unsupported gold figure) and confirms each is caught: **8/8 detected**.

## 4. The one defect this pass fixed on top of `main`

`evidence/gold-price.md` had accumulated **three stacked "current observation" sections** — 4,028.53 at the top
(retrieved 2026-10-22), 4,024.45 in the middle, and 3,996.31 at the bottom. A reader who stopped at the top of the
file got a value two observations out of date while the machine-readable JSON held the current one, and no
automated check caught it because each stacked block was individually well-formed. The file was re-ordered
newest-first with a single current block and one dated history table; no quoted text, URL or stored value was
changed.

The same file also stated that a header reading of **4,025.54** was "recorded separately in
`research/evidence.json`". No such figure exists anywhere in the repository's data files. That pointer was removed
rather than restated, because a reference to a record that does not exist is the same class of defect as an
invented number. It is flagged here for review.

## 5. Flagged, not fixed (published on the Flagged for Review page)

1. **F-026** — the WGC moving header has no quote-as-of timestamp; `quote_date` stays `null`.
2. **Coverage** — 20 of 30 root rows have no assigned current amount and 23 of 30 publish no metal weight.
3. **Retrieval shortfall** — see §2. The next pass should start with the rows listed there.
4. **No physical verification** — zero rings, stamps, scale weights or XRF assays were examined by this session.

## 6. What this pass does *not* prove

An HTTP 200 and a matching sentence prove that a page displayed that sentence during this pass. They do not prove
purity, net gold mass, hallmark existence, stock, return eligibility, or that the page will still say the same
thing tomorrow. No purchase decision is approved by this document.
