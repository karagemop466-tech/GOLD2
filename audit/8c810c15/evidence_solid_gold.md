# Evidence — Explicit "Solid Gold" Engagement & Commitment Rings (`S8C8-T2`)

Retrieved live via `fetch_page` on **2026-10-22 (UTC)**. Every single quote below is copied verbatim from the fetched primary retailer page; every omitted or ambiguous specification (manufacturer SKU, physical hallmark stamp, net metal-only mass where a gemstone is included, or reference ring size for approximate gram weight) is left `null` and flagged on `flags.html`.

---

## AG-COFFIN-RING — Automic Gold Coffin Ring (Solid 14k Yellow Gold)

- **Source URL:** https://www.automicgold.com/products/coffin-ring
- **Retrieved:** 2026-10-22 (UTC), `fetch_page` chunk 4
- **Return Policy URL:** https://www.automicgold.com/pages/returns-exchange-policy

### Verbatim Excerpts

- `# Coffin Ring`
- `$1,910`
- `Solid 14k Gold and 950 Platinum`
- `metal` / `14k Yellow Gold`
- `so whether you’re buying this genderless statement ring for yourself or giving it to the one you love as a unique engagement or promise ring`
- `Width` / `Band is 3mm`
- `Height` / `Approximately 1.8mm - 2.3mm`
- `Item Weight` / `Approximately 6.1g (gold) or 9.2g (platinum)`
- `Material` / `950 platinum and/or Solid 14k gold`
- `Gold source` / `100% Recycled gold`
- `Manufacturing` / `In house in New York`
- `Returns can be made within 30 days of the delivery date. Free return shipping on US orders. Engraved items are final sale and cannot be returned.`

### Field Audit Notes

- **Explicit `"solid ... gold"` wording:** **YES** (`Solid 14k Gold and 950 Platinum` and `950 platinum and/or Solid 14k gold`).
- **Metal-only weight (`6.1 g`):** **YES (all-metal design with zero gemstones)** — marked `"Approximately 6.1g (gold)"` without specifying which ring size (`2`–`16`) weighs `6.1 g`. Flagged (`F-018`) so buyers request exact gram weight for their ordered size and weigh on receipt.
- **Hallmark / Maker's mark / SKU:** Not stated in page text (`sku: null`, `hallmark_stated: false`, `makers_mark_stated: false`, `F-002`).

---

## AG-CUSHION-SIGNET — Automic Gold Cushion Diamond Signet Ring (Solid 14k Yellow Gold)

- **Source URL:** https://www.automicgold.com/products/cushion-diamond-signet-ring
- **Retrieved:** 2026-10-22 (UTC), `fetch_page` chunks 4–5
- **Return Policy URL:** https://www.automicgold.com/pages/returns-exchange-policy

### Verbatim Excerpts

- `# Cushion Diamond Signet Ring`
- `$2,758`
- `Solid 14k Gold and 950 Platinum`
- `metal` / `14k Yellow Gold`
- `gemstone` / `Salt and Pepper Diamond` / `Clear Lab Diamond`
- `Rock this piece as a wedding band, engagement ring, or outfit staple.`
- `Width` / `Band width is tapered from 8.5mm - 2.5mm`
- `Height` / `Approximately 2mm - 4mm`
- `Item Weight` / `Approximate item weight: gold 5.5g, platinum 8.3g`
- `Diamond weight` / `Approximately 0.65ct`
- `Material` / `950 platinum and/or Solid 14k gold`
- `Gold source` / `100% Recycled gold`
- `Returns can be made within 30 days of the delivery date. Free return shipping on US orders. Engraved items are final sale and cannot be returned.`

### Field Audit Notes

- **Gross vs. metal-only weight discipline (`R39-02`, `R6-07`):** `ring_weight_total_g` is recorded as `5.5` g verbatim (`Approximate item weight: gold 5.5g`), while `weight_g` (metal-only gram weight used for fine-gold arithmetic) is strictly kept `null` (`F-019`) rather than subtracting an estimated `0.65 ct × 0.2 g/ct = 0.13 g`.
- **Tapered width discipline:** `Band width is tapered from 8.5mm - 2.5mm` is NOT averaged into a synthetic single number; `width_mm` is kept `null` with `width_note: "Tapered 8.5mm - 2.5mm"` and flagged (`F-016`).

---

## AG-SAPPHIRE-RING — Automic Gold Sapphire Ring (Solid 14k Yellow Gold)

- **Source URL:** https://www.automicgold.com/products/sapphire-ring
- **Retrieved:** 2026-10-22 (UTC), `fetch_page` chunk 4
- **Return Policy URL:** https://www.automicgold.com/pages/returns-exchange-policy

### Verbatim Excerpts

- `# Sapphire Ring`
- `$526`
- `Solid 14k Gold and 950 Platinum`
- `metal` / `14k Yellow Gold`
- `Dimensions` / `Stone is 3mm in diameter`
- `Width` / `Band is 1.1mm`
- `Height` / `Approximately 1.1mm`
- `Item Weight` / `Approximately 1.2g (gold) or 1.8g (platinum)`
- `Stone` / `Natural sapphire. Natural stones may vary in color`
- `Material` / `950 platinum and/or Solid 14k gold`

### Field Audit Notes

- Complete ring under `$1,500` (`$526`) explicitly disclosed as `Solid 14k Gold`.
- `ring_weight_total_g: 1.2` g includes the `3mm` natural sapphire (`weight_g: null`, `F-019`).
- `width_mm: 1.1` mm is explicitly flagged (`F-021`) because bands below `1.8 mm` face higher bending risk in daily engagement wear.

---

## MJ-BOLD-ETERNITY — Mejuri Bold Diamond Eternity Ring (Solid 14k White Gold)

- **Source URL:** https://mejuri.com/products/bold-diamond-eternity-ring?Material=Solid+White+Gold+%2814k%29&Stone=Natural+Diamond
- **Retrieved:** 2026-10-22 (UTC), `fetch_page` chunk 0
- **Return Policy URL:** https://mejuri.com/faq/return-exchanges/what-is-the-standard-return-policy

### Verbatim Excerpts

- `# Bold Diamond Eternity Ring`
- `From$2,900`
- `Solid White Gold (14k), Natural Diamond`
- `Finding a ring you’ll love for a lifetime is something to celebrate. Here it is: a bold ring handcrafted in 14k solid gold featuring as many as 23 round brilliant cut diamonds.`
- `14k solid white gold pieces are finished with rhodium plating, giving them their signature color along with added shine and durability.`
- `- Minimum Carat Weight: 1.15 ct - 1.57 ct`
- `- Diamond Clarity: SI - I`
- `- Diamond Color: GHI`
- `- Stone Size: 2.5 mm`
- `- Band Width: 2.6 mm`
- `We offer free 30-day returns & exchanges starting from the day the shipment is delivered or picked up in-store.`

### Field Audit Notes

- Explicitly confirms both `Solid White Gold (14k)` and `handcrafted in 14k solid gold` on the live product page, plus `Band Width: 2.6 mm`.
- Omitted gram weight is left `null` (`F-003`), and size-dependent pricing (`From$2,900`) is flagged transparently (`F-022`).

---

## Additional Benchmark Checked & Documented — Catbird (`catbirdnyc.com`)

- Live-fetched pages on `2026-10-22` UTC:
  - `https://www.catbirdnyc.com/column-solitaire-two-tone-diamond-ring.html` (`Column Solitaire Two-Tone Diamond Ring`, `from$2,000.00`)
  - `https://www.catbirdnyc.com/pas-de-deux-ring.html` (`Pas de Deux Ring`, `from$720.00`)
  - `https://www.catbirdnyc.com/a-guide-to-metals` (`Our 14k yellow gold is comprised of 58.50% yellow gold, 31.25% copper, 5.25% zinc, and 5% silver.`)
  - `https://www.catbirdnyc.com/returns` (`within 20 days of the date your package was delivered`, `An $9 charge for return shipping will be deducted from your refund`, `All international sales are final`)
  - `https://www.catbirdnyc.com/contact-us` (`customerservice@catbirdnyc.com`)
- **Why excluded from primary catalog rows:** Catbird's Magento accordion specification bullets did not expand in non-interactive chunk rendering on the product pages (leaving item-level `"solid 14k gold"` bullet text outside the static HTML body chunk even though visible in metadata/search index), AND Catbird provides only a **20-day** domestic return window (shorter than the 30-day buyer protection benchmark) with no published gram weights. Recorded transparently as an audited benchmark rather than guessed from snippets.
