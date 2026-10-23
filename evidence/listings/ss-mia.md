# Evidence — SS-MIA

**Stone and Strand, The Mia Ring in Yellow Gold**

- **Official URL:** https://www.stoneandstrand.com/products/the-mia-ring
- **Retrieved:** 2026-10-22 (UTC), session S-75094819, direct page fetch.
- **Scope:** Verbatim excerpts from the retrieved product-page text; fetcher markup (bold `**`, heading `##`) is removed, wording otherwise unchanged. Spec-table label/value pairs are shown as `Label: value` (the page renders them as a two-column spec list). The full session capture log for this category is `evidence/listings/solid-gold.md`; this per-item file is the authoritative field-scoped input.

## Field-scoped excerpts

### `name`

```
The Mia Ring in Yellow Gold
```

### `sku`

```
https://www.stoneandstrand.com/products/the-mia-ring
```

No SKU is stated in the retrieved page text; the dataset `sku` value is the product handle from the official source URL (see `sku_basis`).

### `metal` / `color`

```
Metal Color: Yellow Gold
```

### `karat`

```
Gold Karat: 14K
```

**Contested (F-033):** the product-image alt text on the same page repeatedly says 10K:

```
Stone and Strand 10K Yellow Gold The Mia Diamond Ring Front Image
Image of 10K Yellow Gold The Mia Diamond Ring on Models Hand
```

The published karat (14) is taken from the structured Metals spec table; the conflicting alt text is recorded here, not silently dropped. One of the two numbers on the retailer's own page is wrong; this dataset cannot determine which.

### `surface_finish`

```
Metal Finish: High Polish
```

### `width_mm`

```
Band Width: 1.5mm
```

### `price` / `currency`

```
$925 (50% off)
```

Currency note (F-025): the retrieved text shows dollar-sign amounts only; the ISO currency is not confirmed, so the dataset keeps the normalized price blank and retains the observed amounts under `superseded_normalization`.

### `original_price`

```
$1,850
```

### `price_basis` / `center_stone_included`

```
Each ring is crafted with conflict-free diamonds and set in 14K solid gold or platinum.
```

```
Total Weight (CTW): 0.5CTW
Center Stone: 0.200CTW
```

### `solid_gold_explicit`

```
Each ring is crafted with conflict-free diamonds and set in 14K solid gold or platinum.
```

The buy-box badge list also includes "Solid Gold".

## Absences and limitations

- **Final sale (F-032):** the buy-box shows "Final Sale — This product is non-returnable" and the Product Description bullets state "Final sale and non-returnable". At 50% off, the ring is also non-returnable under the retailer's own "purchased at a discount of 50% or greater" rule (`evidence/retailers/stone-and-strand.md`), on the same page that advertises "100 Day Returns".
- **Rhodium finish stated:** the spec table also states "Rhodium Plating: Yes: Diamond area" — recorded verbatim in the item notes; it describes a finish over the diamond area and is separate from the solid-gold metal claim.
- **Not on the page:** gram weight (F-003), hallmark / maker's mark (F-002), band depth (F-016), SKU.
