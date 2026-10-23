# Evidence — AG-CUSHION-SIGNET

- **Official product URL:** https://www.automicgold.com/products/cushion-diamond-signet-ring
- **Retrieved:** 2026-10-22 (UTC), direct official-page fetch.
- **Scope:** Field-scoped excerpts transcribed from the retrieved page. This is not a full HTML archive or a physical inspection.

## Field-scoped excerpts

### Product name / title — `name`

```
Cushion Diamond Signet Ring
```

### SKU or source identifier — `sku`

```
cushion-diamond-signet-ring
```

### Metal description — `metal`

```
Solid 14k Gold and 950 Platinum
```

```
950 platinum and/or Solid 14k gold
```

### Karat — `karat`

```
Solid 14k Gold
```

### Metal colour — `color`

```
14k Yellow Gold
```

### Published band-width wording — `band_width_text`

```
Band width is tapered from 8.5mm - 2.5mm
```

### Gross item weight & diamond note (excluded from `weight_g`)

```
Approximate item weight: gold 5.5g, platinum 8.3g
```

```
Approximately 0.65ct
```

### Price & currency — `price`, `currency`

```
$2,758
```

### Price basis & stone scope — `price_basis`, `center_stone_included`

```
Cushion Diamond Signet Ring
```

## Capture limitations

- Band width is tapered (`8.5mm - 2.5mm`) and height is a range (`Approximately 2mm - 4mm`), so `width_mm` and `depth_mm` remain `null` rather than averaged (flagged F-016).
- Published `5.5g` item weight includes the set `~0.65ct` diamond, so stone-excluded `weight_g` is left strictly `null` (flagged F-003, F-028).
- No physical hallmark or maker’s mark text appeared on the product page (flagged F-002).

## Re-verification — 2026-10-23 (UTC)

- **Currency source:** https://www.automicgold.com/cart.js
- **Result:** the public cart endpoint reports the store currency, which is the only formal
  currency statement found for this retailer. It is quoted verbatim, not inferred.

```
"currency":"USD"
```

- **Product page re-read 2026-10-23:** https://www.automicgold.com/products/cushion-diamond-signet-ring (not re-read this pass; observation date unchanged)

```
$2,758
```

## Re-verification — 2026-10-23 20:xxZ (UTC)

- **Product page re-read:** https://www.automicgold.com/products/cushion-diamond-signet-ring

```
Cushion Diamond Signet Ring
$2,758
Solid 14k Gold and 950 Platinum
Salt and Pepper Diamond
Clear Lab Diamond
Approximate item weight: gold 5.5g, platinum 8.3g
Approximately 0.65ct
Band width is tapered from 8.5mm - 2.5mm
Approximately 2mm - 4mm
950 platinum and/or Solid 14k gold
```

- **Seller product JSON:** https://www.automicgold.com/products/cushion-diamond-signet-ring.js

```
"price":240800,"price_min":240800,"price_max":325300,"price_varies":true
"title":"14k Yellow Gold \/ Salt and Pepper Diamond","price":275800
"title":"14k Yellow Gold \/ Clear Lab Diamond","price":240800
```

- **Interpretation boundary:** the stored `$2,758` is the 14k Yellow Gold / Salt and Pepper Diamond variant, not a single product-wide price. The range is `$2,408–$3,253` and is not averaged (F-039). `5.5 g` remains a gross item weight that includes the ~0.65 ct stone, so `weight_g` stays `null` (F-028).
