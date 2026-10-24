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

**Retrieved:** 2026-10-23 (UTC). The fetch tool does not expose request-second timestamps. A later direct
capture in this session independently confirmed the same displayed value already integrated by PR #45.

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
| 3,996.31 | 2026-10-23 | 2026-10-22 | `superseded_moving_header` | Earlier same-day fetch of the same moving header; a later read displayed 3,995.47 with the same chart date. |
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

### `karat_basis` — NIST conversion chart

```
an item marked 18 k is made of 75 % gold
```

### `karat_basis` — eCFR labeling context

**URL:** https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3

```
fine (24 karat) gold
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

## Revision note — 2026-10-23 (S-E0D6DD62)

At the time S-E0D6DD62 re-ordered this file, 3,996.31 was the latest same-day WGC header observation. That
value was subsequently superseded by the direct S-1B04074F re-read at 3,995.47 and is retained only in the dated
history table above. `data/gold-price.json` is the machine-readable source of the current dated observation.

**One claim was removed rather than restated.** The previous integration note said that a header reading of
4,025.54 was "recorded separately in `research/evidence.json`". No such figure exists anywhere in
`research/evidence.json`, `data/gold-price.json` or any other data file in this repository, so it is not
presented here as an observation. A pointer to a record that does not exist is the same class of defect as an
invented number, and it is flagged for review rather than silently carried forward.

## Recheck note — 2026-10-23 (S-A182C7CC)

A direct fetch by S-A182C7CC again displayed 3,995.47 USD/oz with the page chart still dated 22 October, 2026.
This independently corroborates the value already stored after PR #45; it is not a second market benchmark or a
claim that the value is still live. The fetch tool exposed the content but not the request timestamp, so this
record keeps date-level retrieval precision only. The exact header quote-as-of time remains unconfirmed (F-026).
