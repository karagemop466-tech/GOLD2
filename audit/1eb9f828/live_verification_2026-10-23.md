# Live re-verification — S-1EB9F828 (2026-10-23 20:18–20:35 UTC)

Scope of this pass: the gold reference, the three root rows that were missing from the
combined register, the Automic Gold currency statement, and the Mejuri seller-level
policies needed to register that seller. Everything below was retrieved with the
`fetch_page` tool on 2026-10-23. No value in this file was inferred, averaged,
converted, or copied from a search snippet or a neighbouring row.

Limits: a successful retrieval is not an assay, a hallmark check, proof of stock, or a
future price. `bash` has no outbound route to retailer hosts in this sandbox
(`curl` exits 35, `OpenSSL SSL_connect: SSL_ERROR_SYSCALL`), so `fetch_page` was the only
retrieval path; it returns extracted text, not a byte-level archive.

## 1. Sources directly re-read this pass

| Source | URL | What was read | Result |
|---|---|---|---|
| World Gold Council — Goldhub | https://www.gold.org/goldhub/data/gold-prices | header, chart date, ICE attribution | `USD /oz - 3,996.31`; `Data as of 22 October, 2026`; no rendered quote timestamp (F-026) |
| Automic Gold — Coffin Ring (page) | https://www.automicgold.com/products/coffin-ring | title, price, metal selector, details block | `Coffin Ring`, `$1,910`, `Solid 14k Gold and 950 Platinum`, `Approximately 6.1g (gold) or 9.2g (platinum)`, `Band is 3mm`, height `Approximately 1.8mm - 2.3mm` |
| Automic Gold — Coffin Ring (JSON) | https://www.automicgold.com/products/coffin-ring.js | product/variant prices | `price 191000`, `price_min 191000`, `price_max 223300`, `price_varies true`; 14k Yellow/White/Rose `191000`; Nickel Free 14k White `203900` |
| Automic Gold — Cushion Diamond Signet Ring (page) | https://www.automicgold.com/products/cushion-diamond-signet-ring | title, price, options, details | `$2,758`, metal options 14k Yellow/White/Nickel Free White/Rose/Champagne/950 Platinum, gemstone options `Salt and Pepper Diamond` / `Clear Lab Diamond`, `Approximate item weight: gold 5.5g, platinum 8.3g`, `Approximately 0.65ct`, tapered `8.5mm - 2.5mm` |
| Automic Gold — Cushion Diamond Signet Ring (JSON) | https://www.automicgold.com/products/cushion-diamond-signet-ring.js | product/variant prices | `price 240800`, `price_min 240800`, `price_max 325300`, `price_varies true`; 14k YG/Salt-and-Pepper `275800`; 14k YG/Clear Lab `240800` |
| Automic Gold — cart endpoint | https://www.automicgold.com/cart.js | currency field on an empty cart | `"currency":"USD"`; cart identifier deliberately not retained |
| Mejuri — Bold Diamond Eternity Ring | https://mejuri.com/products/bold-diamond-eternity-ring?Material=Solid+White+Gold+%2814k%29&Stone=Natural+Diamond | title, price, materials, specifications, shipping/returns | `From$2,900`; `Solid White Gold (14k), Natural Diamond`; `handcrafted in 14k solid gold`; `Band Width: 2.6 mm`; `Minimum Carat Weight: 1.15 ct - 1.57 ct`; `Diamond Clarity: SI - I`; `Diamond Color: GHI`; `Stone Size: 2.5 mm`; free 30-day returns; engraving not returnable; no ISO currency statement |
| Mejuri — standard return policy | https://mejuri.com/faq/return-exchanges/what-is-the-standard-return-policy | window, exclusions, fees | free 30-day returns from delivery (US/Canada/UK/Australia/Germany); engraved and monogrammed products non-returnable; `US | Free` |
| BBB — Mejuri (Toronto) | https://www.bbb.org/ca/on/toronto/profile/jewelry-manufacturers/mejuri-0107-1370644 | accreditation, phone | `NOT BBB Accredited`; `(310) 597-4745`; no static letter rating rendered (F-031) |

## 2. Dated observations and what changed

1. **Gold reference.** The moving WGC header read **3,996.31 USD/oz** at 20:18Z on
   2026-10-23, while the chart still said **22 October 2026**. The register had stored
   **4,024.45** with `retrieved_at` 2026-10-23. This is a **freshness update of a moving
   header**, not a correction of a fixed benchmark: 4,024.45 is retained in
   `data/gold-price.json → superseded_observations` and is no longer rendered on any page.
   `quote_date` stays `null` (F-026). All generated melt figures were rebuilt from the new
   constant; no derived dollar figure is hardcoded in prose (QA check 12).
2. **Coffin Ring.** The page still shows `$1,910`; the product JSON proves the amount is
   the 14k default and that variants run to `$2,233`. The specific variant carrying
   `223300` was truncated out of the retrieved chunk, so it is **not named** anywhere.
   Published as F-039, with the range recorded and never averaged.
3. **Cushion Diamond Signet Ring.** The page still shows `$2,758`, but that is the
   14k Yellow Gold / Salt and Pepper Diamond configuration; the JSON shows
   `$2,408–$3,253`. The earlier `not_re_read` status was replaced with today's
   observation; `weight_g` remains `null` because `5.5 g` is a gross item weight that
   includes the ~0.65 ct stone (F-028).
4. **Mejuri Bold Diamond Eternity Ring.** Displayed price and specification are unchanged.
   No ISO currency statement exists on the page, the cart endpoint (404) or the payment FAQ,
   so the amount stays **unassigned** (`price: null`), consistent with F-025/F-030. This row
   was previously **absent from the combined register**; it is now included with a `mejuri`
   seller record and its own dated sources, closing REQ-A87A-01.
5. **Automic Gold currency.** The empty-cart endpoint again returned
   `"currency":"USD"`. It remains the only formal currency statement for this retailer.

## 3. Irregularities found (published, not hidden)

- **Automic production-time copy contradicts itself on the same page.** The shipping
  banner says `Production time is 1 to 5 business days` (Coffin) and `4-8 business days`
  (Cushion), while the Shipping & Returns block says `made to order. Production time is 1-2
  weeks` (`2-3 weeks` with engraving). Both texts are recorded; neither was chosen as "the"
  lead time. This is a new observation and is **not** yet a numbered flag; it is logged here
  for review.
- **Automic pages both render `Only 3 units left in stock!`** on different products. This
  looks like template or inventory-sync copy; it is not treated as a stock fact.
- **Mejuri Materials accordion reads `Solid Yellow Gold (14k)`** while the selected variant
  is Solid White Gold (14k). The selected option text governs the row; the accordion heading
  was not used to assign metal colour.
- **The WGC header moved within one day** (three observations across 2026-10-23 now in
  history). Any fixed dollar figure derived from it becomes stale immediately; this is why
  derived melt values now live only in generated tables.
- **The SVG/JSON variant maximum `$2,233` is unattributed.** `price_max` is a real seller
  figure, but the retrieved chunk did not include the variant title that carries it, so the
  site says "range to $2,233" without naming a metal.

## 4. Rows deliberately NOT re-read this pass

The other 41 combined-register rows and the 26 non-Automic/Mejuri root rows were **not
re-read** during this pass. Their stored values and dates are unchanged; the verification
log marks them with their earlier `checked_at` (2026-10-22 or 2026-10-23) and this file does
not present them as freshly verified. The automated passes prove quote/provenance
consistency, not present-day availability. Priority for the next pass: the four Zales
pages (F-018 label instability), Brilliant Earth `BE-121H6` (locale-dependent currency),
VRAI (no rendered price), and every Sarraf gram weight.

## 5. What this pass did not do

No ring was handled, no stamp or maker's mark was inspected, no scale or XRF measurement
was taken, and no seller was contacted. **Zero rows are approved purchases.** After every
future review, look for hallucinations again.
