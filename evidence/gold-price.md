# Evidence — dated gold quote and calculation constants

- **Retrieved:** 2026-10-23 (UTC), direct page fetches; the prior 2026-10-22 observation is kept below as superseded history.
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

4,024.45
Last Updated
```

### `chart_as_of_date` (page metadata, not the header timestamp)

```
Data as of 22 October, 2026
```

### `quote_date`

Left **null**: the page's own data blocks are dated 22 October, 2026, but the moving header that carries the amount shows no
quote-as-of timestamp. Page metadata is not silently bound to the header (F-026).

### `source_name`

```
Market Data: Provided by ICE Data Services.
```

The page also states: “Prices are quoted in currency unit per troy ounce unless otherwise stated.”

## Superseded intraday observation — not used

Header observations on this page move during the day. Recorded history: **4,024.36** and **4,028.53** (2026-10-22), **4,025.54** (2026-10-22 re-fetch), and **4,024.45** (2026-10-23 direct fetch, used now). Earlier numbers are retained only as superseded audit history; they are not used in `usd_per_troy_oz`, generated calculations, or dashboard outputs.

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

## Integration correction — 2026-10-22, re-verified 2026-10-23
Each stored amount is a moving-header observation. Its exact source quote timestamp is unconfirmed, so `quote_date` stays null.
The page's own data blocks are dated 22 October, 2026 and are stored separately as `chart_as_of_date`; they are not bound to the
header. On 2026-10-23 the header displayed 4,024.45 and that dated observation is now the current reference, with 4,028.53 kept as
superseded history in `superseded_observations`. No header amount is treated as a fixed daily close or an LBMA benchmark.
