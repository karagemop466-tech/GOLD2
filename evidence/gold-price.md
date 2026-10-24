# Evidence — dated gold quote and calculation constants

- **Current observation retrieved:** 2026-10-23 (UTC), direct page fetch.
- **Current quote source:** World Gold Council, Gold spot prices.
- **Conversion source:** US National Institute of Standards and Technology (NIST).
- **Karat-labeling context:** government-hosted eCFR; useful regulatory guidance, not a physical assay.

> **Read the current observation first.** This file previously stacked three "current observation"
> blocks on top of each other, newest last, so the value at the top of the page was two observations
> out of date. It is now ordered newest-first with one current block and one dated history table.
> Nothing was deleted: every earlier number is in the history table with its retrieval date.

## World Gold Council — current observation

**URL:** https://www.gold.org/goldhub/data/gold-prices

**Retrieved:** 2026-10-23T23:41Z (UTC). This is the latest direct fetch of the same page on that day; every earlier reading of the moving header is kept only in the dated history table below.

### `usd_per_troy_oz`

```
USD

/oz

-

3,995.47
Last Updated
```

### Chart date on the same page

```
Data as of 22 October, 2026
```

### `source_name`

```
Market Data: Provided by ICE Data Services.
```

The page also states:

```
Prices are quoted in currency unit per troy ounce unless otherwise stated.
```

### Why `quote_date` is `null`

The moving header renders no quote-as-of timestamp. The chart's date is stored separately as
`chart_as_of_date` and is **not** assigned to the header. Only the retrieval date and the value observed at
that retrieval are recorded. This is F-026.

## Superseded observations — never used in calculations

| Value (USD/oz) | Retrieved | Chart date on that page | Status | Why it is not current |
| --- | --- | --- | --- | --- |
| 3,996.31 | 2026-10-23T20:00Z | 2026-10-22 | `superseded_moving_header` | Earlier same-day fetch of the same moving header. A later fetch at 23:41Z rendered 3,995.47 with the same chart date. |
| 4,024.45 | 2026-10-23 | 2026-10-22 | `superseded_intraday` | Earlier same-day fetch of the same moving header. A later fetch displayed a different value with the same chart date. |
| 4,028.53 | 2026-10-22 | 2026-10-21 | `superseded_moving_header` | Prior-day moving-header observation. |
| 4,024.36 | 2026-10-22 | 2026-10-21 | `superseded_intraday` | Earlier same-day capture on 2026-10-22. |

A moving spot header is not a fixed benchmark. Historical LBMA Gold Price data was removed from the public
WGC site at the request of ICE Benchmark Administration, so no unlicensed LBMA fix is claimed (F-013).

## NIST — troy-ounce conversion

**URL:** https://www.nist.gov/system/files/documents/2017/05/09/Precious-Metals-Conversion-Information-march2015.pdf

### `grams_per_troy_ounce`

```
| 1 troy ounce | 1 | 20 | 480 | 31.103 476 8 | 31 103.476 8 |
```

NIST also explains:

```
Divide the price per troy ounce by 31.103 476 8
```

The JSON stores the same chart value without grouping spaces: `31.1034768`.

## Karat basis — NIST and eCFR

### `karat_basis` — FTC consumer guidance (verbatim)

**URL:** https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry

```
A piece of jewelry marked 18K gold is 18 parts gold mixed with six parts of another metal.
```

The `75 %` the calculator uses for 18K is `18 / 24` arithmetic on that sentence. It is not a quoted
percentage and it appears on neither the FTC page nor 16 CFR 23.3 as written. A previous revision of
this file presented `an item marked 18 k is made of 75 % gold` as a verbatim NIST/eCFR excerpt; both
pages were re-read on 2026-10-23 and neither contains that sentence, so it was removed rather than
restated. Published as F-044.

### `karat_basis` — eCFR labeling context

**URL:** https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3

```
fine (24 karat) gold
```

```
composed throughout of an alloy of gold (i.e., gold that is less than 24 karats)
```

The same section distinguishes gold alloys from products that are only surface-plated or coated. The calculator
therefore labels its result **nominal** fine-gold content and never treats a listing's karat as laboratory
confirmation.

## LBMA access limitation

**URL:** https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices

```
The historical tabulated data for the LBMA Precious Metals Prices has been moved to our MyLBMA Portal. In order to view this data on our Portal, you will need to have the relevant licence from IBA.
```

No free LBMA fix is claimed. This limitation is recorded as F-013.

## Calculation boundaries

- `nominal fine-gold grams = documented metal-only grams × listed karat ÷ 24`
- `theoretical melt USD = nominal fine-gold grams ÷ 31.1034768 × dated USD per troy ounce`
- Do not use gross ring weight when it includes stones or non-gold components.
- The result is not an appraisal, resale quote, refiner payout, or fair-retail estimate.
- The reference moves intraday. Any figure computed from it is a conditional illustration stamped with the
  observation date, never a current retail or scrap price.

## Revision note — 2026-10-23 (S-1B04074F)

Session S-1B04074F re-read the official page and the moving header displayed **3,995.47 USD/oz** with the same
chart date, *Data as of 22 October, 2026*. The stored current observation was updated to 3,995.47 and the previous
3,996.31 moved into the history table above. Derived figures on the site are recomputed from the stored spot and
the NIST constant; nothing is typed by hand. `quote_date` stays `null` (F-026) because the header still renders no
quote-as-of timestamp.

## Revision note — 2026-10-23

Session S-E0D6DD62 re-ordered this file without changing any quoted text, any URL, or any stored value:
the single current observation is now 3,995.47 from the 2026-10-23T23:41Z fetch, and the earlier readings appear
only in the dated history table. `data/gold-price.json` is the machine-readable source of the same facts.

**One claim was removed rather than restated.** The previous integration note said that a header reading of
4,025.54 was "recorded separately in `research/evidence.json`". No such figure exists anywhere in
`research/evidence.json`, `data/gold-price.json` or any other data file in this repository, so it is not
presented here as an observation. A pointer to a record that does not exist is the same class of defect as an
invented number, and it is flagged for review rather than silently carried forward.

## Revision note — 2026-10-23T23:4xZ (S-88AA65FD)

A later direct fetch of the same World Gold Council page rendered **3,995.47** with the chart still
dated 22 October 2026, so the current observation moved forward and 3,996.31 was added to the dated
history table. The `karat_basis` section was corrected: a sentence that had been presented as a
verbatim NIST/eCFR quote appears on neither page and was replaced by the FTC sentence it paraphrased,
with the 75 % figure labelled as arithmetic. Both changes are published as F-044.

## Revision note — 2026-10-23T23:4xZ (S-88AA65FD)

A later direct fetch of the same World Gold Council page rendered **3,995.47** with the chart still
dated 22 October 2026, so the current observation moved forward and 3,996.31 was added to the dated
history table. The `karat_basis` section was corrected: a sentence that had been presented as a
verbatim NIST/eCFR quote appears on neither page and was replaced by the FTC sentence it paraphrased,
with the 75 % figure labelled as arithmetic. Both changes are published as F-044.

## Revision note — 2026-10-23 (S-A182C7CC)

Session S-A182C7CC independently re-read the official World Gold Council page on 2026-10-23 UTC. The moving header displayed **3,995.47 USD/ozt** while the chart separately stated *Data as of 22 October, 2026*. The fetch tool exposes date-level retrieval precision only for this pass; the moving header's quote-as-of time remains unknown, so `quote_date` stays `null` (F-026). This corroborates the dated observation and does not call it a current quote.

