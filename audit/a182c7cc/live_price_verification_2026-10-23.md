# Official-price recheck — 2026-10-23 UTC

Session: **S-A182C7CC**. Scope: all 17 rows with an assigned price in the 44-product Explore catalog, plus the World Gold Council moving-header observation. This is a dated snapshot, not a live feed, a price guarantee, or a complete catalog recertification.

## Method and time precision

Each listed product was opened at its official seller page; the WGC page was fetched directly. The page extractor returns text but does not expose the exact request-start or response time. Therefore the catalog and verification log record **2026-10-23** at date precision rather than inventing second-level timestamps. The later confirmation of the WGC header and selected Automic pages independently matched the earlier same-day readings. The published amount is the displayed item/configuration amount, not a final checkout total. Currency is claimed only where the retailer itself states it or its official site context supports it.

## Product-price observations

| Catalog ID | Officially displayed amount on 2026-10-23 | Selection / scope and caveat | Official evidence |
|---|---:|---|---|
| `ag-natural` | **$726 USD** | Natural Diamond Ring; displayed 14k Yellow Gold option. No size-specific checkout or engraving total was checked. | [Automic Gold product page](https://www.automicgold.com/products/diamond-ring); the seller’s [cart endpoint](https://www.automicgold.com/cart.js) reports `"currency":"USD"`. |
| `ag-cluster` | **$2,862 USD** | Diamond Cluster Ring; 14k Yellow Gold / Natural Diamond selection. Lab-created option is distinct. | [Automic Gold product page](https://www.automicgold.com/products/diamond-cluster-ring); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-petal` | **$1,774 USD** | 0.6ct Round Diamond Petal Ring; 14k Yellow Gold / Lab Created Diamond selection. Natural-diamond option is not substituted. | [Automic Gold product page](https://www.automicgold.com/products/diamond-petal-ring); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-ruby` | **$526 USD** | Ruby Ring; displayed 14k Yellow Gold option. | [Automic Gold product page](https://www.automicgold.com/products/ruby-ring); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-sapphire` | **$526 USD** | Sapphire Ring; displayed 14k Yellow Gold option. | [Automic Gold product page](https://www.automicgold.com/products/sapphire-ring); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-moissanite` | **$420 USD** | Moissanite Ring; displayed 14k Yellow Gold option. | [Automic Gold product page](https://www.automicgold.com/collections/engagement/products/moissanite-ring); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-24k` | **$3,520 USD** | 24k Band; page says Solid 24k Gold and shows Hammered as the default finish. No exact size/weight or size-specific checkout total was confirmed. | [Automic Gold product page](https://www.automicgold.com/products/24k-band); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-coffin-ring` | **$1,910 USD** | Coffin Ring; default 14k Yellow Gold selection. The official product JSON reports variant-dependent pricing; F-039 remains applicable, and this amount is not a product-wide price. | [Automic Gold product page](https://www.automicgold.com/products/coffin-ring); [official variant JSON](https://www.automicgold.com/products/coffin-ring.js); [official USD cart context](https://www.automicgold.com/cart.js). |
| `ag-cushion-signet` | **$2,758 USD** | Cushion Diamond Signet Ring; 14k Yellow Gold / Salt and Pepper Diamond. The official page itself displayed `$2,758`. Its product JSON separately lists raw variant price `275800` and product-level range fields; **the raw integer was not converted into the displayed price**. F-039 remains applicable. | [Automic Gold product page](https://www.automicgold.com/products/cushion-diamond-signet-ring); [official variant JSON](https://www.automicgold.com/products/cushion-diamond-signet-ring.js); [official USD cart context](https://www.automicgold.com/cart.js). |
| `mene-rose` | **$1,325 USD** | Rose Ring; page states 24k Gold and Crafted-on-Demand. Earlier same-day stored observation `$1,336` at 10:00Z is superseded and retained in the evidence record. Exact buyer size, weight and final price are not bound. | [Menē Rose Ring official page](https://mene.com/products/rose-ring-gold). |
| `mene-knot` | **$1,442 USD** | Knot Ring; page states 24k Gold and Crafted-on-Demand. Earlier same-day stored observation `$1,454` at 10:00Z is superseded and retained in the evidence record. Exact buyer size, weight and final price are not bound. | [Menē Knot Ring official page](https://mene.com/products/knot-ring-gold). |
| `ext-be-121h6` | **$890 USD — Setting Only** | Classic Six-Prong Solitaire Ring in 14K Yellow Gold, with 14K White Gold prongs. The USD selector is visible; center diamond and ring size are not selected. This is not a complete-ring price. | [Brilliant Earth official product page](https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/). |
| `sar-147370` | **US$3,004.00** | 14k White Gold Solitaire Ring, 0.94 ctw. The page uses the explicit `US$` prefix. | [Sarraf official product page](https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html). |
| `sar-145362` | **US$2,661.00** | 14k White Gold Men's Solitaire Diamond Ring, 1/2 ct. The page uses the explicit `US$` prefix. | [Sarraf official product page](https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html). |
| `sar-145364` | **US$2,858.00** | 14k Yellow Gold Men's Solitaire Diamond Ring, 1/2 ct. The page uses the explicit `US$` prefix. | [Sarraf official product page](https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html). |
| `sar-144773` | **US$1,362.00** | 14k Yellow Gold 12mm Traditional Domed Wedding Band. The page uses `US$`; its published 13.40g metal-weight benchmark is for size 10, not a size-specific quote. | [Sarraf official product page](https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html). |
| `fdj-gr0001` | **$1,299.99 USD** | Lab Grown Diamond Halo Engagement Ring in 14K Gold. The displayed price does not resolve the separately flagged weight-basis caution or authenticate the item. | [Factory Direct Jewelry official product page](https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/). |

**Outcome:** 15 of the 17 product amounts matched the saved amount; two changed and were corrected: Menē Rose `$1,336 → $1,325 USD`, and Menē Knot `$1,454 → $1,442 USD`. The prior amounts remain in source history. Brilliant Earth's `$890` setting-only amount was directly re-read and confirmed; it was not an unverified dead end.

The other 15 amounts remain dated display observations. Their appearance on an official page does not prove that the seller will honor the price later, that a selected size/configuration is available, or that the amount is the final cart total.

## WGC gold reference (not a product price)

The [World Gold Council Gold spot prices page](https://www.gold.org/goldhub/data/gold-prices) displayed **USD /oz — 3,995.47**. The same page separately stated **“Data as of 22 October, 2026.”** The moving header has no quote-as-of timestamp, so `quote_date` remains `null` and the chart date is not assigned to the header (F-026). This session independently confirmed the value already integrated by PR #45; it did not treat the WGC read as a live quote.

## Explicit exclusions

- The 27 catalog rows whose price/currency was unconfirmed remain blank; no price was inferred from a dollar sign, variant, neighboring product, search result, discount arithmetic, or currency conversion.
- No unselected center diamond, final checkout total, tax, shipping charge, or size-specific price is inferred.
- This price pass did not re-certify seller terms, payment protections, seller identity, karat claims, hallmark/maker marks, weights, diamond origin, authenticity, or physical purity. No ring was weighed or physically/XRF tested; no purchase was approved.
- The assigned-price snapshot becomes stale as seller pages change. Re-open the linked official source before acting.
