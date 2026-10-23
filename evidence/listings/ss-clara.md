# Evidence — SS-CLARA

**Stone and Strand, The Clara Ring**

- **Official URL:** https://www.stoneandstrand.com/products/the-clara-ring
- **Retrieved:** 2026-10-22 (UTC), session S-75094819, direct page fetch.
- **Scope:** Verbatim excerpts from the retrieved product-page text; fetcher markup (bold `**`, heading `##`) is removed, wording otherwise unchanged. Spec-table label/value pairs are shown as `Label: value` (the page renders them as a two-column spec list). The full session capture log for this category is `evidence/listings/solid-gold.md`; this per-item file is the authoritative field-scoped input.

## Field-scoped excerpts

### `name`

```
The Clara Ring
```

### `sku`

```
https://www.stoneandstrand.com/products/the-clara-ring
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

### `surface_finish`

```
Metal Finish: High Polish
```

### `width_mm`

```
Band Width: 1.65mm
```

### `price` / `currency`

```
$2,200
```

### `price_basis` / `center_stone_included`

```
Each ring is crafted with conflict-free diamonds and set in 14K solid gold or platinum.
```

```
Total Weight (CTW): 0.620CTW
Center Stone: 0.50CTW
```

### `solid_gold_explicit`

```
Each ring is crafted with conflict-free diamonds and set in 14K solid gold or platinum.
```

The buy-box badge list also includes "Solid Gold".

## Absences and limitations

- **Final sale (F-025):** the retrieved buy-box text shows "Final Sale — This product is non-returnable" on the same page that advertises "100 Day Returns". The retailer returns policy confirms final-sale items cannot be returned or exchanged (`evidence/retailers/stone-and-strand.md`).
- **Rhodium finish stated:** the spec table also states "Rhodium Plating: Yes: Diamond area" — recorded verbatim in the item notes; it describes a finish over the diamond area and is separate from the solid-gold metal claim.
- **Contradictory page states (not resolved):** the retrieved text contains both "In stock. Ships out in 3-5 days." and a "Sold out" button state. Availability is not recorded in the dataset.
- **Rejected cached value:** a search-engine snippet for this product showed `$2,000`. The live page on 2026-10-22 showed `$2,200` with no discount. The snippet value is stored in `rejected_values` and never published as the price.
- **Not on the page:** gram weight (F-003), hallmark / maker's mark (F-002), band depth (F-016), SKU.
