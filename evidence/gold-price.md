# Evidence — dated gold quote and calculation constants

- **Retrieved:** 2026-10-22 (UTC), direct page fetches.
- **Current quote source:** World Gold Council, Gold spot prices.
- **Conversion source:** US National Institute of Standards and Technology (NIST).
- **Karat-labeling context:** government-hosted eCFR; useful regulatory guidance, not a physical assay.

## World Gold Council — current observation

**URL:** https://www.gold.org/goldhub/data/gold-prices

### `usd_per_troy_oz`

```
USD

/oz

-

4,028.53
Last Updated
```

### `quote_date`

```
Data as of 21 October, 2026
```

### `source_name`

```
Market Data: Provided by ICE Data Services.
```

The page also states: “Prices are quoted in currency unit per troy ounce unless otherwise stated.”

## Superseded intraday observation — not used

An earlier direct capture on the same retrieval date displayed **4,024.36** with the same data date, 21 October 2026. A later direct fetch displayed **4,028.53**. The earlier number is retained only as superseded audit history; it is not used in `usd_per_troy_oz`, generated calculations, or dashboard outputs.

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

The same section distinguishes gold alloys from products that are only surface-plated or coated. The calculator therefore labels its result **nominal** fine-gold content and never treats a listing’s karat as laboratory confirmation.

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

## Integration correction — 2026-10-22
The stored 4,028.53 was a prior moving-header observation. Its exact source quote timestamp is unconfirmed; quote_date is now null. Chart text “Data as of 21 October, 2026” must not be silently bound to the header. A later re-fetch displayed 4,025.54 in the header; this is recorded separately in research/evidence.json, not used to make the old observation live.

## Re-verification — 2026-10-23 (UTC)

Direct page fetch of https://www.gold.org/goldhub/data/gold-prices.

### Current observation (`usd_per_troy_oz`) — retrieved 2026-10-23

```
USD

/oz

-

4,024.45
```

### Chart date shown on the same page

```
Data as of 22 October, 2026
```

The moving header carries no rendered quote timestamp, so `quote_date` stays `null` (F-026).
The prior observation, 4,028.53 with chart date 21 October 2026, is retained only inside
`superseded_observations`; it is not used in any calculation and no page renders it.

## Re-verification — 2026-10-23 20:xxZ (UTC)

Direct page fetch of https://www.gold.org/goldhub/data/gold-prices.

### Current observation (`usd_per_troy_oz`) — retrieved 2026-10-23

```
USD

/oz

-

3,996.31
```

### Chart date shown on the same page

```
Data as of 22 October, 2026
```

### `source_name`

```
Market Data: Provided by ICE Data Services.
```

The moving header still carries no rendered quote timestamp, so `quote_date` stays `null`
(F-026). The 4,024.45 header value observed earlier on 2026-10-23 is now retained only in
`superseded_observations`; it is not used in any calculation and no page renders it. The
two readings are honest observations of a moving header, not a correction of a fixed
benchmark.
