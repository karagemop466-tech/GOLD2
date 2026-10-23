# Live line-by-line re-verification — Session S-305FDD02 (2026-10-23 UTC)

Every value below was read from the seller's own live page in this session. "Matches" means the
rendered text is byte-for-byte the text already stored in that row's `field_evidence`.
No value was inferred, converted, averaged or filled in. Where the live page differed from the
stored record, the difference is recorded and routed to Flagged for Review — not silently
"corrected" into a new number.

## 1. Gold reference (official WGC page)

| Item | Stored before this pass | Live read 2026-10-23 | Action |
|---|---|---|---|
| `usd_per_troy_oz` | 4,024.45 (retrieved 2026-10-23 by a peer session) | **3,996.31** (`USD` / `/oz` / `-` / `3,996.31`), read twice, same value | Refreshed; prior value moved to `superseded_observations` |
| `chart_as_of_date` | 2026-10-22 | `Data as of 22 October, 2026` | Unchanged; still not bound to the header (F-026) |
| `quote_date` | null | header carries no timestamp | Stays null (F-026) |

Source: https://www.gold.org/goldhub/data/gold-prices

## 2. Root register rows — live re-read

| Row | Official page re-read | Displayed price | Stored price quote | Weight | Result |
|---|---|---|---|---|---|
| AG-COFFIN-RING | automicgold.com/products/coffin-ring (+ `.js`) | `$1,910` (product `.js`: 191000 minor units, min 191000, max 223300) | `$1,910` | `Approximately 6.1g (gold) or 9.2g (platinum)` | Price matches. Range 1,910–2,233 is real (`price_varies:true`); stored single figure remains the yellow-gold display value |
| AG-24K | automicgold.com/products/24k-band (+ `.js`) | `$3,520` (352000, `price_varies:false`) | `$3,520` | `Approximate item weight: 11g` | Matches |
| AG-CUSHION-SIGNET | automicgold.com/products/cushion-diamond-signet-ring (+ `.js`) | `$2,758` (275800 = 14k Yellow Gold / Salt and Pepper) | `$2,758` | not published | Matches. `.js` range 2,408 (14k Yellow / Clear Lab) – 3,253 |
| AG-SAPPHIRE-RING | automicgold.com/products/sapphire-ring (+ `.js`) | `$526` (52600 = 14k Yellow Gold) | `$526` | not published | Matches. Range 526–625 |
| SAR-147370 | sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html | `Now: US$3,004.00` (`Was: US$3,513.00`, `-14% OFF`) | `Now: US$3,004.00` | `3.80 grams` (`14K Solid Gold`) | Matches |
| SAR-145362 | …/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html | `Now: US$2,661.00` (`Was: US$3,112.00`) | `Now: US$2,661.00` | `10.00 grams` | Matches |
| SAR-145364 | …/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html | `Now: US$2,858.00` (`Was: US$3,342.00`) | `Now: US$2,858.00` | `8.00 grams` | Matches |
| SAR-144773 | …/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html | `Now: US$1,362.00` (`Was: US$1,593.00`) | `Now: US$1,362.00` | `13.40 grams` (page adds "approximate weight of ring in size 10") | Matches |
| BN-194158 | bluenile.com … item-194158 | `$1,125(Setting Price)`; stock `500000y`; `1.90mm` | `$1,125(Setting Price)` | none stated | Matches. Amount still not assigned because Blue Nile states no ISO currency (F-025) |
| BN-195269 | … item-195269 | `$1,155(Setting Price)`; stock `501130y`; `1.80mm` | `$1,155(Setting Price)` | none stated | Matches |
| BN-192506 | … item-192506 | `$1,255(Setting Price)`; stock `502250y14`; `1.60mm` | `$1,255(Setting Price)` | none stated | Matches |
| BN-315661 | … item-315661 | `$2,210(Setting Price)`; stock `505094w14`; `1.75mm` | `$2,210(Setting Price)` | none stated | Matches |
| BN-195402 | … item-195402 | `$1,300(Setting Price)`; stock `501480w14`; `1.70mm` | `$1,300(Setting Price)` | none stated | Matches |
| BN-302868 | … item-302868 | `$1,050(Setting Price)`; stock `501480w14l`; `1.70mm` | `$1,050(Setting Price)` | none stated | Matches |
| BN-203348 | … item-203348 | `$1,145(Setting Price)`; stock `502120y14`; `2.40mm` | `$1,145(Setting Price)` | none stated | Matches |
| BN-195639 | … item-195639 | `$1,000(Setting Price)`; stock `501130y14`; `1.80mm` | `$1,000(Setting Price)` | none stated | Matches |
| BN-194548 | … item-194548 | `$1,045(Setting Price)`; stock `501290w14`; `2.00mm` | `$1,045(Setting Price)` | none stated | Matches |
| BN-193625 | … item-193625 | `$1,950(Setting Price)`; stock `502350y14`; `1.80mm` | `$1,950(Setting Price)` | none stated | Matches |
| BN-316238 | … item-316238 | **`$1,240(Setting Price)`** — page title **"Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen"**, stock `505097w14`, `1.50mm` | no price stored; stored name is "Petite Micropavé Engagement Ring in 14k White Gold" | none stated | **Irregularity F-037**: the URL now serves a different product. Stored name/price deliberately left unassigned; no value copied from the new page |

## 3. Remaining rows — live re-read

| Row | Official page re-read | Displayed price | Stored price quote | Result |
|---|---|---|---|---|
| Z-19957449 | zales.com/15-ct-diamond-solitaire-engagement-ring-10k-gold/p/V-19957449 | `Discounted Price $899.00` | `Discounted Price $899.00` | Matches. No ISO currency stated, so the amount stays unassigned (F-025) |
| Z-20303279 | …/p/V-20303279 | `Discounted Price $979.30  Original Price was $1,399.00 30% Off` | same | Matches (labelled render) |
| Z-20301172 | …/p/V-20301172 | `Discounted Price $769.30  Original Price was $1,099.00 30% Off` | same | Matches (labelled render) |
| Z-20046552 | …/p/V-20046552 | `Discounted Price $909.30  Original Price was $1,299.00 30% Off` | `$909.30  $1,299.00 30% Off` | Labelled render today vs unlabeled stored render → F-018 confirmed a fourth time. Both renders kept; nothing assigned |
| BE-121H6 | brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/ | `$890(Setting Only)` with a rendered `USD` selector; width `2.5 mm`; prong metal `14K White Gold` | `$890(Setting Only)` | Matches |
| VRAI-CLASSIC-4P | vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-32797281484893 | `Metal weight:2.86g (Ring size 6)`, `Band depth:1.6mm`, `Band width:Standard`, **no price string** | `Metal weight:2.86g (Ring size 6)` | Matches. Price stays blank (F-008) |
| MJ-BOLD-ETERNITY | mejuri.com/products/bold-diamond-eternity-ring | `From$2,900`; `Band Width: 2.6 mm`; `Minimum Carat Weight: 1.15 ct - 1.57 ct`; `Diamond Color: GHI`; `Diamond Clarity: SI - I` | `From$2,900` | Matches. No ISO currency on the page → verbatim only (F-025) |
| SS-CLARA | stoneandstrand.com/products/the-clara-ring | `$2,200`; `Gold Karat 14K`; `Final Sale — This product is non-returnable`; band `1.65mm` | `$2,200` (unassigned) | Matches |
| SS-RITA | …/the-rita-ring | `$1,950` / `$780 (60% off)`; `14K`; Final Sale; band `1.70mm` | `$780 (60% off)` | Matches |
| SS-MIA | …/the-mia-ring | `$1,850` / `$925 (50% off)`; spec `Gold Karat 14K` while image alt text reads `10K Yellow Gold`; Final Sale | `$925 (50% off)` | Matches, and the 14K-vs-10K conflict is reproduced live (F-034) |
| FDJ-GR0001 | factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/ | `$1,299.99` with a rendered `USD` currency menu; `Stamped with the appropriate hallmark`; `Solid Gold` | `$1,299.99` | Matches |

## 4. What changed in the repository as a result of this pass

| Change | File(s) | Reason |
|---|---|---|
| Gold reference 4,024.45 → **3,996.31**, prior value moved to `superseded_observations` | `data/gold-price.json`, `evidence/gold-price.md`, `dashboard/data/gold-reference.json`, `research/evidence.json` | Live WGC read, twice, same value |
| Legacy dashboard constants, karat table, calculator default, FDJ and Sarraf melt prose, calculator tests recomputed at the new spot | `dashboard/scripts/build.py`, `dashboard/scripts/calc-test.js` | The old numbers were derived from the superseded quote; leaving them would publish stale arithmetic |
| `F-026` detail rewritten without binding the chart date to the header and without quoting a single stale figure | `data/flags.json` | The header moved twice in one day |
| Zales rows: today's labelled render appended to `render_history`; `unassigned_price_text` set to the verbatim render actually seen, with a matching `unassigned_price_text` field quote | `data/listings/budget.json`, `data/listings/three-stone-vintage.json` | The register showed a blank price line for rows whose page displayed an amount. The amount is still **not** assigned because no ISO currency is stated |
| New flags `F-039` (identity drift) and `F-040` (log/register disagreement) | `data/flags.json`, `data/retailers.json`, `data/verification-log.json`, item flags | See below |
| `BN-316238` status → `identity mismatch · review` | `data/listings/halo-pave.json` | Stored name no longer matches the served page |
| "Two registers, not one" note derived from the data files (30 root rows / 41 companion entries / 27 shared URLs / 3 root-only rows / 45 URLs across both) | `tools/build_site.py` → `index.html` | The scanner repeatedly flagged an "all entries" claim that compared two different registers |
| README counts corrected to 30 rows, 9 retailers, 38 flags, 41 companion entries, 46 HTML pages | `README.md` | Five stale counts (REQ-A87A-04) |

## 5. Irregularities published for review (nothing was silently repaired)

1. **F-039 — Blue Nile `BN-316238` served a different product.** The URL slug says
   *petite-micropave-engagement-ring-in-14k-white-gold-item-316238*; the live page returned
   **"Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen"**, stock
   `505097w14`, `1.50mm`, `$1,240(Setting Price)`. The row keeps its stored description, its
   price stays blank, and the discrepancy is on the Flagged for Review page with the URL.
2. **F-040 — the verification log recorded that `$1,240` as a "verified match"** while the row
   itself carried no price and a different name. Log entry corrected; the row stays blank.
   This is exactly the class of error the project says not to make: a value that the register
   never accepted had already been written into a "verified" log.
3. **F-018 re-confirmed.** The four Zales pages render the same amounts with and without
   `Discounted Price` / `Original Price was` labels. Today's render was labelled; a peer's
   same-day render was not. Both are preserved; no amount is ordered by position.
4. **`F-008` / `F-025` hold.** Blue Nile, Mejuri and Zales still publish no ISO currency code,
   and VRAI's configurator still serves no price. Those amounts stay verbatim-but-unassigned.

## 6. Explicit limits of this pass

- No physical ring, stamp, scale weight or XRF assay was examined. Every statement above is a
  reading of a web page.
- `github.io` is outside this sandbox's outbound allowlist, so the deployed site could not be
  read back through this session's browser-equivalent tool. Deployment is evidenced by the
  GitHub Pages API build record for the merge commit (see `COORDINATION.md`).
- The companion `explore/` register's 41 entries were **not** individually re-fetched in this
  pass. Their stored quotes keep their own observation dates; nothing was upgraded to
  "verified today" by association with the root pass.
- Search snippets, cached copies and third-party mirrors were never used as price evidence.

