# Evidence — AG-COFFIN-RING

- **Official product URL:** https://www.automicgold.com/products/coffin-ring
- **Retrieved:** 2026-10-22 (UTC), direct official-page fetch.
- **Scope:** Field-scoped excerpts transcribed from the retrieved page. This is not a full HTML archive or a physical inspection.

## Field-scoped excerpts

### Product name / title — `name`

```
Coffin Ring
```

### SKU or source identifier — `sku`

```
coffin-ring
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

### Band width — `width_mm`

```
Band is 3mm
```

### Metal weight & basis — `weight_g`, `weight_basis`

```
Approximately 6.1g (gold) or 9.2g (platinum)
```

### Price & currency — `price`, `currency`

```
$1,910
```

### Price basis & stone scope — `price_basis`, `center_stone_included`

```
Coffin Ring
```

```
giving it to the one you love as a unique engagement or promise ring
```

```
Solid 14k Gold
```

## Capture limitations

- Band height is stated only as a range (`Approximately 1.8mm - 2.3mm`), so single-number `depth_mm` is left `null` rather than averaged (flagged F-016).
- All-metal ring design contains zero gemstones, so `6.1g (gold)` is stone-free gold alloy mass; however, the exact reference ring size across sizes 2–16 is not stated (flagged F-027).
- No physical interior karat stamp or maker’s mark was documented in the retrieved product text (flagged F-002).
- No physical inspection, XRF assay, or jeweller’s-scale verification was performed (flagged F-024).

## Re-verification — 2026-10-23 (UTC)

- **Currency source:** https://www.automicgold.com/cart.js
- **Result:** the public cart endpoint reports the store currency, which is the only formal
  currency statement found for this retailer. It is quoted verbatim, not inferred.

```
"currency":"USD"
```

- **Product page re-read 2026-10-23:** https://www.automicgold.com/products/coffin-ring

```
$1,910
```

## Re-verification — 2026-10-23 20:xxZ (UTC)

- **Product page re-read:** https://www.automicgold.com/products/coffin-ring

```
Coffin Ring
$1,910
Solid 14k Gold and 950 Platinum
Approximately 6.1g (gold) or 9.2g (platinum)
Band is 3mm
Approximately 1.8mm - 2.3mm
950 platinum and/or Solid 14k gold
```

- **Seller product JSON:** https://www.automicgold.com/products/coffin-ring.js

```
"price":191000,"price_min":191000,"price_max":223300,"price_varies":true
"title":"14k Yellow Gold","price":191000
"title":"14k White Gold","price":191000
"title":"Nickel Free 14k White Gold","price":203900
"title":"14k Rose Gold","price":191000
```

- **Interpretation boundary:** the page displays `$1,910` at the default 14k selection; the JSON confirms a `$1,910–$2,233` variant range. The specific variant carrying the `223300` maximum was not captured in the retrieved chunk, so it is not named here (F-039). Currency remains supported only by the store cart endpoint.
