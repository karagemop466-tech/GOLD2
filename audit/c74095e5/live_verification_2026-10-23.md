# Live line-by-line verification — Session S-C74095E5 — 2026-10-23 (UTC)

- **Window:** 2026-10-23 23:39Z–23:59Z. Method: `fetch_page` of official retailer/reference pages only
  (plus one `web_search` used **only** to discover candidate official URLs; no snippet value was used as a fact).
- **Rule applied:** a stored value changes only where the official page rendered a different value in this pass.
  Superseded values are kept as dated history. Blank stays blank. Search snippets, rail prices, alt text and
  shipping-weight fields are never product facts.
- **Baseline before edits (`ca39632`):** `tools/qa.py` PASS 12/0/3 · explore verify 44/85/26/0 · node tests 23/23 ·
  links 46 pages PASS · security PASS · dashboard P1–P8 PASS · legacy scanners 202 + 4,292 + 1,991 controls PASS.
  Outputs in `audit/c74095e5/check_runs/base_*`.

## 1 · Gold references (2 changes)

| Source | Stored | Observed live (verbatim) | Disposition |
| --- | --- | --- | --- |
| WGC `https://www.gold.org/goldhub/data/gold-prices` | 3,996.31 (retrieved 2026-10-23, quote date null, F-026) | Header `USD /oz - 3,995.47`; `Data as of 22 October, 2026`; `Market Data: Provided by ICE Data Services.`; `Prices are quoted in currency unit per troy ounce unless otherwise stated.` | **CHANGE** → current 3995.47; 3996.31 → superseded (same-day moving header) |
| JM Bullion `https://www.jmbullion.com/charts/gold-price/` | Ask 4,035.54 @ page time 2026-10-23 05:56 EDT | `Gold Ask $4,009.38`; `Bid: $3,994.88 Ask: $4,009.38`; `10/23/2026 7:46 PM EDT`; `Oct 23, 2026 at 19:46 EDT` | **CHANGE** → explore marketReference 4009.38, publishedAt 2026-10-23T23:46:00Z |

Derived check (calculator constants, not typed into prose by hand): 3995.47 ÷ 31.1034768 = **$128.4574…/fine g**.

## 2 · Root-register priced/weighted rows re-read (10 priced + VRAI weight)

| Row | Stored | Observed live | Disposition |
| --- | --- | --- | --- |
| AG-24K | $3,520 · 11.0 g | `$3,520` · `Solid 24k Gold` · `Approximate item weight: 11g` | match |
| AG-COFFIN-RING | $1,910 · 6.1 g | `$1,910` · `Solid 14k Gold and 950 Platinum` · `Approximately 6.1g (gold) or 9.2g (platinum)` | match |
| AG-CUSHION-SIGNET | $2,758 | `$2,758` · `Solid 14k Gold and 950 Platinum` (canonical slug `cushion-diamond-signet-ring`) | match |
| AG-SAPPHIRE-RING | $526 | Official JSON `sapphire-ring.js`: `"price":52600,"price_min":52600,"price_max":62500` | match (JSON shipping weights ignored) |
| SAR-147370 | US$3,004 · 3.80 g | `Now: US$3,004.00` · `14K Solid Gold` · `3.80 grams` · 0.94 Ct G/I1 Natural | match |
| SAR-145362 | US$2,661 · 10.00 g | `Now: US$2,661.00` · `10.00 grams` · 0.50 Ct H/SI1 Natural | match |
| SAR-145364 | US$2,858 · 8.00 g | `Now: US$2,858.00` · `8.00 grams` | match |
| SAR-144773 | US$1,362 · 13.40 g | `Now: US$1,362.00` · `13.40 grams` · `The weight listed is an approximate weight of ring in size 10` | match |
| BE-121H6 | $890 USD setting | `USD` selector · `$890(Setting Only)` · 14K Yellow Gold · prongs 14K White Gold · 2.5 mm | match |
| FDJ-GR0001 | $1,299.99 USD | `$1,299.99` + USD currency selector · `Made with solid gold. Never plated.` · `Karat stamped inside the band.` · `Weight:1.25 Grams` · `Total Carat Weight: 1.37cts` | match (F-035 stands) |
| VRAI-CLASSIC-4P | 2.86 g · price blank | `Metal weight:2.86g (Ring size 6)` · `Band depth:1.6mm` · `Pavé carat weight:0.18ctw` on Plain band · no price rendered | match (F-008 + vrai-plain-pave stand) |
| Automic currency | `"currency":"USD"` | `cart.js` re-read: `"currency":"USD"` (token not retained) | match — underpins all Automic USD prices |

## 3 · Explore-only priced rows re-read via official Shopify JSON (prices in cents)

| Row | Stored | Observed | Disposition |
| --- | --- | --- | --- |
| ag-natural | $726 | `diamond-ring.js` `"price":72600` | match |
| ag-cluster | $2,862 (Natural scope) | Variant `14k Yellow Gold / Natural Diamond` = `286200`; Lab variant = `163600` (= top-level min) | match **for the stored Natural-Diamond scope**; HTML item weight not re-read |
| ag-petal | $1,774 (Lab scope) | `14k Yellow Gold / Lab Created Diamond` = `177400`; Natural = `327400` | match for stored Lab scope |
| ag-ruby / ag-sapphire / ag-moissanite | $526 / $526 / $420 | `52600` / `52600` / `42000` | match |

## 4 · Menē (2 changes — metal-linked Crafted-on-Demand prices moved again)

| Row | Stored | Observed live | Disposition |
| --- | --- | --- | --- |
| mene-rose | $1,336 (2026-10-23T10:00Z) | `# Rose Ring` · `$1,325` · `USD` · `24K gold` · `Products are sold by weight, not size.` | **CHANGE** → 1325 |
| mene-knot | $1,454 | `# Knot Ring` · `$1,442` · `USD` · `crafted in 24k gold` · Width 6mm | **CHANGE** → 1442 |

Rail/“From” prices on those pages were **not** used; only each PDP's own price block.

## 5 · Unpriced rows spot-re-read (stored nulls remain correct)

- **SS-MIA** — `$1,850` / `$925 (50% off)` · `Final Sale — This product is non-returnable` next to `100 Day Returns` ·
  spec `Gold Karat 14K` vs image alt `Stone and Strand 10K Yellow Gold The Mia Diamond Ring` → F-034 re-confirmed live.
- **SS-RITA** (`.js`) — `78000` vs compare-at `195000` (60% off) · `Final sale and non-returnable` · `"available":false` (sold out).
- **SS-CLARA** (`.js`) — sizes 5/6 `220000`, size 7 `200000` · `set in 14K solid gold or platinum`.
- **Z-19957449** — minimal render `$899.00` + `Free and easy 30-day returns`, **no** “Discounted Price” label this time → F-018 label instability re-confirmed; price stays unassigned (F-025).
- **BN-316238** — still renders `Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen`, stock `505097w14`, `1.50mm`, `$1,240(Setting Price)` → F-041 re-confirmed live.
- **MJ-BOLD-ETERNITY (root URL)** — `# Bold Diamond Eternity Ring` · `From$2,900` · `Solid White Gold (14k), Natural Diamond` ·
  `handcrafted in 14k solid gold` · Band Width 2.6 mm · `free 30-day returns` · engraving `not eligible for returns` → root null price correct (F-030).
- **cb-sonnet** — now renders `$2,800.00`; no ISO currency statement in chunk read → stays blank (newly-rendered-amounts pattern).
- **quince-oval** — `$900.00` / `Originally $2,080.00` · `Offered in a 14k gold band with a platinum head` → mixed-metal finding stands; price stays blank.
- **av-bridge** — `handcrafted from solid 22 karat gold` · `Approximate Fine Weight: 5 to 6.1 grams depending on size` ·
  `Free returns and exchange within 15 days in the USA` · its own price not rendered in chunks 0–2 (chunk 3 not read) → stays blank.
- **eCFR 16 CFR 23.3** — live; `§ 23.3 Misrepresentation as to gold content.` (title/authority spot-check only).

## 6 · Cross-register defects found live (dashboard register) — corrected in this pass

Blue Nile serves product pages **by item ID; slug text is cosmetic** (proven: both item-203348 slugs render the
identical product, stock and price). Dashboard BN names were taken from non-canonical slugs, so **all five**
dashboard BN names disagree with the live official titles, while amounts/widths (ID-keyed) are right.
No BN page fetched states `USD`, so dashboard `price_usd` assignments also violate the shared currency rule
(root F-025/F-033). Root-register BN names/slugs are live-true.

| ID | Live official title / stock / price text (2026-10-23) | Dashboard stored (wrong part) |
| --- | --- | --- |
| BN-194158 | Classic Four Prong Solitaire…18k Yellow Gold · 500000y · 1.90mm · `$1,125(Setting Price)` | Name “Petite Solitaire…” · price_usd 1125 |
| BN-195269 | Petite Solitaire…18k **Yellow** Gold · 501130y · 1.80mm · `$1,155(Setting Price)` | Name “Classic Four-Prong…18k **Rose** Gold” · 1155 |
| BN-203348 | Classic Simple Solitaire…14K Yellow Gold · 502120y14 · 2.40mm · `$1,145(Setting Price)` | Name “Three-Stone Trellis…” · category three-stone · 1145 |
| BN-315661 | Pavé Contour Diamond…14K White Gold By James Allen · 505094w14 · 1.75mm · `$2,210(Setting Price)` | Name “French Pavé Halo…” · 2210 |
| BN-316238 | Comfort Fit Solitaire…By James Allen · 505097w14 · `$1,240(Setting Price)` | Name “Petite Micropavé…” · category halo-pave · 1240 |
| AG-CUSHION-SIGNET | Canonical slug live ($2,758, §2) | URL `…/lab-grown-cushion-diamond-signet-ring` → **`404 Not Found`** (HTML + `.js` empty) · name “Lab-Grown…” |
| MJ-BOLD-ETERNITY | Natural-diamond page live (`From$2,900`, §5) | URL `…/bold-lab-grown-diamond-eternity-ring` → **`Page Not Found`** · price_usd 2900 unsupported |
| VRAI-CLASSIC-4P | Root configurator URL live (§2) | Dashboard URL redirects to `…/classic-4-prong-solitaire/…` → **“The page you are looking for does not exist.”** |

**Corrections (dashboard `build.py` source):** canonical root URLs, live titles, BN/MJ `price_usd → None` with the
verbatim display preserved in `price_note`, category fixes (203348/316238 → solitaire), new flag **DF-008**,
root flag **F-044**. No root-register row value changed for these items.

## 7 · Other irregularities (flagged, not silently rewritten)

1. **F-040 gap:** root flags run F-001–F-042 with F-012 absent and F-032 merged into F-007 — but F-040 is also
   absent (39 flags), although merged PR #36's title cites “F-039/F-040”. No F-040 record exists in any data file.
   New flags in this pass are **F-043/F-044**; the gap is documented, not back-filled.
2. **F-031 mis-scope:** its detail concerns only Automic Gold + Mejuri BBB pages, yet `affected_items` also lists
   SAR-147370/145362/145364/144773 and FDJ-GR0001. Left as-is for owner review; **not** propagated to new rows.
3. **PR #19 superseded:** `arena/70b76800-gold2` (dashboard + BN-316238 + Costco) is still OPEN since
   2026-10-23T00:09Z, but `main` already contains `dashboard/`, `evidence/listings/bn-316238.md` and
   `evidence/retailers/costco.md` via later merges. Not merged/closed by this session — needs owner review.
4. **SAR-147371 color contradiction (new row, §8):** spec table `Diamond Color: G` vs description
   `I1 in clarity and H in color` → new flag **F-043**; no structured color grade is chosen.

## 8 · New listings verified from official PDPs (added this pass)

Discovery was by `web_search` for official `sarraf.com` URLs only; every stored value below comes from the
PDP fetch in this pass (chunk 0), never from the snippet.

### SAR-151362 — 14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw
URL: https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-belcher-diamond-ring-1ctw.html
`MSRP: US$31,899.00` · `Was: US$9,594.00` · `Now: US$8,203.00` · `SKU:3552G` · `Stock Number: 151362` ·
`Material: 14K Solid Gold` · `Approximate Metal Weight: 9.20 grams` · `Diamond Weight: 1.00 Ct.` ·
`Diamond Color: H` · `Diamond Clarity: SI 1` · `Diamond ( Natural / Lab Created ): Natural` ·
Desc: `Clarity of the Diamond is Si1 in clarity and H in color.` Width: not in chunk read → blank.

### SAR-147371 — 14k Yellow gold Mens Solitaire Diamond Ring 0.98 ct.
URL: https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-0-98-ct.html
`MSRP: US$15,747.00` · `Was: US$4,736.00` · `Now: US$4,049.00` · `SKU:9422-100-14ky` · `Stock Number: 147371` ·
`Material: 14K Solid Gold` · `Approximate Metal Weight: 7.70 grams` · `Diamond Weight: 0.98 Ct.` ·
spec `Diamond Color: G` / `Diamond Clarity: I1` / `Natural`; desc `measures approximately 10.0mm` +
`I1 in clarity and H in color` → **G-vs-H contradiction flagged (F-043)**. Note: distinct from SAR-147370.

Nominal arithmetic (generated by builders from the dated WGC quote, never hand-typed into data):
fine g = weight × 14/24 → SAR-151362 5.367 g · SAR-147371 4.492 g. Both asking prices exceed the conditional
melt illustration at $3,995.47/ozt (≈ $689 / ≈ $577) — no below-melt red flag; diamonds/workmanship dominate.

## 9 · Not re-read in this pass (stored dated captures retained; re-read before any purchase)

Root: BN-192506, BN-195402, BN-302868, BN-195639, BN-194548, BN-193625, Z-20046552, Z-20303279, Z-20301172.
Explore-only: cb-odile, cb-ballet, cb-pointelle, av-clean; Automic HTML item-weights (prices re-read via JSON only).
Policies/BBB: all retailer + BBB pages except incidental Auvere/Mejuri PDP return blocks. NIST PDF (eCFR spot-check only).
Dashboard Zales slug variants (ID-keyed per DF-006 captures; amounts already blank).

## 10 · Standing limits

Zero physical inspection, XRF, scale, hallmark or maker's-mark verification. Zero purchase approvals.
A fetch is a dated display observation, not stock, checkout, or purity proof.
**Look for hallucinations again after every review — re-run every scanner after every edit (done: §check_runs).**
