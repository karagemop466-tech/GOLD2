# S-FE7BA040 — live line-by-line re-verification (2026-10-23, ~23:41–23:47Z UTC)

Session `S-FE7BA040` (`arena/fe7ba040-gold2`). Read-only inspection of the published
register plus targeted direct `fetch_page` retrieval of the official pages named below.
Every observation below is a short factual transcription of text the page actually
rendered during this pass; no value was inferred, converted, averaged or copied from a
search snippet.

**Rule applied:** a stored value is reused only when the official page rendered it again
during this pass. A page that could not be re-read keeps its older date and is labelled.
A successful retrieval is not an assay, not a hallmark check, and not proof of stock or
future price.

## 1. Re-read official sources

| # | Source | URL | Stored value | Observed this pass | Outcome |
|---|--------|-----|--------------|--------------------|---------|
| 1 | World Gold Council — gold spot | https://www.gold.org/goldhub/data/gold-prices | `3,996.31` USD/oz (retrieved 2026-10-23) | `USD /oz - 3,995.47` `Last Updated`; chart `Data as of 22 October, 2026`; `Market Data: Provided by ICE Data Services.` | **DRIFT** — header moved again; refreshed to `3,995.47`, `3,996.31` moved to superseded history |
| 2 | Automic Gold — Coffin Ring (product endpoint) | https://www.automicgold.com/products/coffin-ring.js | price `1910.0`, `observed_price_range` | `price:191000` ($1,910), `price_min:191000`, `price_max:223300` ($2,233), variant `Nickel Free 14k White Gold` `$203900` ($2,039) | MATCH — price and range unchanged |
| 3 | Sarraf — SAR-144773 wedding band | https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html | price `1362.0`, weight `13.4` g | `Now: US$1,362.00` (Was `US$1,593.00`, MSRP `US$5,296.00`); `14K Solid Gold`; `Approximate Metal Weight 13.40 grams`; SKU `ST-LPBWB120-14KY`; Stock `144773` | MATCH |
| 4 | VRAI — Classic 4-Prong Dome | https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-32797281484893 | weight `2.86` g @ size 6, price null | `Metal: 18k Yellow Gold`; `Band width: Standard`; `Band depth: 1.6mm`; `Metal weight: 2.86g (Ring size 6)`; `Pavé carat weight: 0.18ctw`; `Returns accepted within 30 days`; `FedEx 2Day $10` / `FedEx Overnight $50` | MATCH — no price in served HTML, so `price: null` is correct |
| 5 | Blue Nile — BN-316238 | https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238 | description as stored, price null | URL now renders `Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen`; `Stock Number 505097w14`; `Width 1.50mm`; `$1,240(Setting Price)` | MATCH with flagged discrepancy — confirms **F-041/F-042**; the row keeps its stored description and blank price |
| 6 | Mejuri — Bold Diamond Eternity Ring | https://mejuri.com/products/bold-diamond-eternity-ring | price null (`From $2,900`) | `From$2,900`; `14k solid gold`; up to `23 round brilliant cut diamonds`; `Band Width: 2.6 mm`; `free 30-day returns & exchanges` | MATCH |
| 7 | Brilliant Earth — BE-121H6 | https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/ | price `890.0` (Setting Only, USD selector) | Page loaded; the setting price is client-rendered and did not appear in the retrieved text | **NOT RE-CONFIRMED** this pass — no value changed; the stored dated observation stands |

## 2. Not re-read this pass

The remaining register rows were **not** re-fetched in this pass. Their stored
observations keep their own earlier retrieval dates and are not silently refreshed.
Not re-read ≠ unverified ≠ invalidated. The rows are visible on `verification.html`
with their own dates.

## 3. Change applied

- `data/gold-price.json`: `usd_per_troy_oz` `3,996.31` → `3,995.47`; `3,996.31` added to
  `superseded_observations`; `evidence_quotes` and `field_evidence` updated; `quote_scope`
  updated. `quote_date` stays `null` (F-026).
- `evidence/gold-price.md`: current observation block updated; `3,996.31` added to the
  dated history table; revision note added.
- `research/evidence.json` (+ generated `explore/research/evidence.json`): the
  `wgc-panel-review` source record's `quotes`, `note`, `observedAt` and `lastRecheckedAt`
  updated.
- `data/verification-log.json`: the `GOLD-QUOTE` entry's observed values and note updated;
  `pass.session` updated to `S-FE7BA040`.
- `dashboard/scripts/build.py`: `SPOT_USD`, `GOLD_REFERENCE`, the karat reference table
  heading, the calculator input default and the shell spot line updated to `3,995.47`
  (and `$128.46 / fine g`).
- `dashboard/scripts/calc-test.js`: the dated-spot fixtures recomputed at `3,995.47`.
- Every generated artifact regenerated (root `*.html`, `explore/**`, `dashboard/**`,
  `site/**`, `reports/**`).

## 4. Independent scanner

`audit/fe7ba040/hallucination_provenance_scan.py` — 7 check families, written without
importing `tools/qa.py` or any other session's scanner:

- **C1** current gold quote on every rendered page that shows one; no superseded value.
- **C2** gold evidence chain (markdown, source record, JSON quotes) agree.
- **C3** every root URL present in the combined catalog; catalog hosts official.
- **C4** every root category page links each of its items' official URL.
- **C5** flag "N of M" titles match their `affected_items` and the register size.
- **C6** prices carry currency+evidence; null semantics preserved (no silent zero).
- **C7** every published root page displays the No-Hallucinations policy.

Result on the published tree: **PASS — 7 families, 0 failures.**
`audit/fe7ba040/test_scan.py` injects 9 defects plus the unmutated baseline and confirms
the scanner catches each one: **10/10**.

## 5. Boundaries

- No physical ring, stamp, purity, scale weight or XRF assay was examined.
- Zero rows are purchase-approved. No seller was contacted.
- This is one review, not a certificate. **Look for hallucinations again after every
  review.**
