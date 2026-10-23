# S-66F158E6 — final integration source and baseline record

**Session/branch:** `S-66F158E6` / `arena/66f158e6-gold2`  
**Live observation window:** 2026-10-23T20:18:44Z–2026-10-23T20:27:21Z  
**Method:** direct `fetch_page` retrieval of official product, variant, policy, and market-reference URLs; comparison with every root/combined/companion record. No search snippet, schema.org block, recommendation card, currency conversion, or cross-variant substitution was used as a replacement observation. Seller statements are not assays.

## Pre-edit baseline (not final acceptance)

The unmodified inherited snapshot passed its own checks, but those checks did not detect the cross-register contradictions below.

- Root QA: PASS, 11 checks, 0 failures, 3 non-blocking coverage warnings.
- Root calculator and independent snapshot audit: PASS; 12 arithmetic controls, 0 independent findings.
- Independent scanners: PASS at 202, 4,220, 1,979, and 986 controls respectively; the last reported 13 warnings and 0 failures.
- Dashboard build verifier: PASS despite the identity/URL/currency drift documented below; this gap is being closed with a cross-register gate.
- Combined verifier: PASS for 41 products / 12 sellers / 77 sources / 25 findings / 0 purchase approvals, with 69 non-blocking review warnings.
- Node tests: 23/23 PASS. Deterministic combined build: 13 pages. Link check: PASS across 46 pages, 102 local targets, and 177 external publisher URLs.
- `npm ci --ignore-scripts`: 23 packages, 0 reported vulnerabilities.
- Post-baseline Git difference: only the timestamp/generated content in `reports/qa-report.md` before source-backed edits began.

An automated PASS is a guardrail, not a guarantee of source truth, physical purity, or future availability. Repeat hallucination review after every edit and before publication.

## Full 44-product live re-read

“Raw display” deliberately does not imply an assigned ISO currency. “Matched” means the retrieved value agrees with the stored source-backed field; it does not mean the product is purchase-approved.

| Combined / root identity | Official URL result and current raw display | Weight/configuration result | Integration disposition |
|---|---|---|---|
| `ag-natural` | Natural Diamond Ring — `$726`; official Automic page | ≈1.2 g gold item weight; default 14k Yellow Gold | Matched; USD separately supported by official cart `currency:USD` |
| `ag-cluster` | Diamond Cluster Ring — `$2,862` | ≈3.1 g gold item weight; default 14k Yellow / Natural Diamond | Matched |
| `ag-petal` | 0.6ct Round Diamond Petal Ring — `$1,774` | ≈2.7 g gold item weight; default 14k Yellow / Lab Created Diamond | Matched |
| `ag-ruby` | Ruby Ring — `$526` | ≈1.2 g gold item weight; default 14k Yellow Gold | Matched |
| `ag-sapphire` / `AG-SAPPHIRE-RING` | Sapphire Ring — `$526` | ≈1.2 g gold item weight; 3 mm natural sapphire | Matched; add explicit gross-weight field evidence |
| `ag-moissanite` | Moissanite Ring — `$420` | ≈1.2 g gold item weight; default 14k Yellow Gold | Matched |
| `ag-24k` / `AG-24K` | 24k Band — `$3,520` | Approximate item weight 11 g; seller declares 99.99% pure 24k | Matched; declared fineness is not an assay |
| `AG-COFFIN-RING` | Coffin Ring default `$1,910`; official JSON `price_min:191000`, `price_max:223300`, `price_varies:true` | Default 14k Yellow Gold; ≈6.1 g gold / 9.2 g platinum; stone-free | Restore to combined register; publish scoped `$1,910–$2,233` variant range |
| `AG-CUSHION-SIGNET` | Cushion Diamond Signet Ring default `$2,758`; official JSON `price_min:240800`, `price_max:325300`, `price_varies:true` | Default 14k Yellow / Salt and Pepper; ≈5.5 g gross item weight and ≈0.65 ct diamond | Restore; publish scoped `$2,408–$3,253`; never call gross weight net metal |
| `cb-odile` | Odile the Swan Black Diamond Ring — `from$1,600.00` | Configuration/currency not established | Raw display retained; structured price remains blank |
| `cb-sonnet` | Sonnet Lab-Grown Diamond Ring — `$2,800.00` | Configuration/currency not established | Raw display retained; structured price remains blank |
| `cb-ballet` | Night at the Ballet Diamond Ring, Emerald Cut — `from$5,300.00` | Configuration/currency not established | Raw display retained; structured price remains blank |
| `cb-pointelle` | Pointelle Diamond Ring — `$578.00` | Currency not established | Raw display retained; structured price remains blank |
| `av-bridge` | Diamond Bridge Ring Tall; no main-product price exposed in relevant retrieved chunks | “Approximate Fine Weight” 5–6.1 g depending on size; term undefined | Weight range is not imported as net/fine gold; price remains blank |
| `av-clean` | Clean Cut Stack Ring Polished; no main-product price exposed in relevant retrieved chunks | “Approximate Fine Weight” 2.8–3.7 g depending on size; term undefined | Same unresolved basis; no calculation |
| `quince-oval` | Lab Grown Diamond Oval Petite Classic Engagement Ring - 1ct — `$900.00`, yellow-gold color, size unselected | 14k gold band with platinum head or all platinum | Raw display only; no currency, selected size, or component-weight inference |
| `mene-rose` | Rose Ring — `$1,325` with explicit `USD` | 24k Gold, Crafted-on-Demand; no bound size/weight | **Correction:** `$1,336 → $1,325` |
| `mene-knot` | Knot Ring — `$1,442` with explicit `USD` | 24k Gold, Crafted-on-Demand; no bound size/weight | **Correction:** `$1,454 → $1,442` |
| `MJ-BOLD-ETERNITY` | Bold Diamond Eternity Ring — `From$2,900` | Selected “Solid White Gold (14k), Natural Diamond”; 2.6 mm band; 1.15–1.57 ct | Restore; no ISO currency assignment. Same page’s specification panel also says “Solid Yellow Gold (14k)” — publish conflict |
| `bn-501480w14` | Petite Micropavé Diamond Engagement Ring in 14k White Gold (1/10 ct. tw.) — `$1,300(Setting Price)` | SKU 501480w14; width 1.70 mm; rhodium finish | Matched; currency remains unconfirmed |
| `bn-501480w14l` | Petite Micropavé Lab-Grown Diamond Engagement Ring in 14k White Gold (1/10 ct. tw.) — `$1,050(Setting Price)` | SKU 501480w14l; width 1.70 mm; rhodium finish | Matched; currency remains unconfirmed |
| `BN-194158` | Classic Four Prong Solitaire Engagement Ring in 18k Yellow Gold — `$1,125(Setting Price)` | SKU 500000y; width 1.90 mm; platinum prongs | Canonical item confirmed; replace companion’s wrong Petite title/URL; no USD assignment |
| `BN-195269` | Petite Solitaire Engagement Ring in 18k Yellow Gold — `$1,155(Setting Price)` | SKU 501130y; width 1.80 mm | Canonical item confirmed; replace companion’s wrong Classic Four-Prong Rose title/URL; no USD assignment |
| `BN-192506` | Petite Hidden Halo Solitaire Plus Diamond Engagement Ring in 14k Yellow Gold — `$1,255(Setting Price)` | SKU 502250y14; width 1.60 mm | Matched; currency remains unconfirmed |
| `BN-315661` | Pavé Contour Diamond Engagement Ring In 14K White Gold By James Allen — `$2,210(Setting Price)` | SKU 505094w14; width 1.75 mm; rhodium finish | Canonical item confirmed; replace companion’s wrong French Pavé Halo title/URL; no USD assignment |
| `BN-203348` | Classic Simple Solitaire Engagement Ring in 14K Yellow Gold — `$1,145(Setting Price)` | SKU 502120y14; width 2.40 mm | Canonical item confirmed; replace companion’s wrong Three-Stone Trellis title/URL; no USD assignment |
| `BN-195639` | Petite Solitaire Engagement Ring in 14k Yellow Gold — `$1,000(Setting Price)` | SKU 501130y14; width 1.80 mm | Matched; currency remains unconfirmed |
| `BN-194548` | Solitaire Compass Set Engagement Ring in 14k White Gold — `$1,045(Setting Price)` | SKU 501290w14; width 2.00 mm; rhodium finish | Matched; currency remains unconfirmed |
| `BN-193625` | Petite Three-Stone Diamond Engagement Ring in 14k Yellow Gold — `$1,950(Setting Price)` | SKU 502350y14; width 1.80 mm | Matched; currency remains unconfirmed |
| `BN-316238` | **Comfort Fit Solitaire Engagement Ring In 14K White Gold By James Allen** — `$1,240(Setting Price)` | SKU 505097w14; width 1.50 mm; rhodium finish | **Live title correction** from inherited “Petite Micropavé”; source slug/item ID remains official; no USD assignment |
| `Z-19957449` | 1/5 CT. Diamond Solitaire Engagement Ring in 10K Gold — `Discounted Price $899.00` | Complete ring as listed | Matched; no ISO currency assignment |
| `Z-20046552` | 1/2 CT. T.W. Multi-Diamond Cushion Frame Engagement Ring in 10K Gold — `Discounted Price $909.30  Original Price was $1,299.00 30% Off` | Complete ring as listed | Canonical item confirmed; replace companion’s wrong 1 CT Frame Twist title/URL; label instability remains flagged |
| `Z-20303279` | 1/2 CT. T.W. Diamond Frame Vintage-Style Twist Shank Engagement Ring in 10K Gold — `$979.30  $1,399.00 30% Off` (this render unlabeled) | Complete ring as listed | Canonical item confirmed; replace companion’s wrong Vera Wang title/URL; do not assign amounts by position |
| `Z-20301172` | 1/3 CT. T.W. Diamond Three Stone Engagement Ring in 10K Gold — `Discounted Price $769.30  Original Price was $1,099.00 30% Off` | Complete ring as listed | Matched; no ISO currency assignment |
| `VRAI-CLASSIC-4P` | Classic Round Brilliant Engagement Ring | Plain Band | 18k Yellow Gold; no price string in retrieved text | Metal weight 2.86 g at ring size 6; depth 1.6 mm; Plain selection also displays pavé 0.18 ctw | Canonical URL works; replace companion’s dead alternate URL; weight remains size-scoped |
| `BE-121H6` | Classic Six-Prong Solitaire Ring in 14K Yellow Gold — `$890(Setting Only)` with `USD` selector | 2.5 mm band; 14K Yellow setting / 14K White prongs | Matched; setting-only scope retained |
| `sar-147370` / `SAR-147370` | 14k White Gold Solitaire Ring 0.94 ctw. — `Now: US$3,004.00` | 14K Solid Gold; Approximate Metal Weight 3.80 g | Matched |
| `sar-145362` / `SAR-145362` | 14k White Gold Men’s Solitaire Diamond Ring 1/2 ct. — `Now: US$2,661.00` | 14K Solid Gold; Approximate Metal Weight 10.00 g | Matched |
| `sar-145364` / `SAR-145364` | 14k Yellow Gold Men’s Solitaire Diamond Ring 1/2 ct. — `Now: US$2,858.00` | 14K Solid Gold; Approximate Metal Weight 8.00 g | Matched |
| `sar-144773` / `SAR-144773` | 14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band — `Now: US$1,362.00` | 14K Solid Gold; Approximate Metal Weight 13.40 g at size 10 | Matched; size scope retained |
| `fdj-gr0001` / `FDJ-GR0001` | Lab Grown Diamond Halo Engagement Ring in 14K Gold — `$1,299.99`; separate `USD` currency selector | Option-dependent `Weight:1.25 Grams`; 1.37 ctw; “Customize Your Options First to See Accurate Weight” | Add explicit gross-weight evidence; remove unconditional derived-net/melt prose; no product gold valuation |
| `ss-clara` / `SS-CLARA` | Current H2 **The Clara Ring** — `$2,200` | Solid Gold bullet, Gold Karat 14K, Yellow Gold; 1.65 mm band; Final Sale and 100 Day Returns both render | Correct inherited heading/provenance; raw amount only, no ISO currency assignment |
| `ss-rita` / `SS-RITA` | Current H2 **The Rita Ring** — `$1,950` and `$780 (60% off)` | Solid Gold bullet, Gold Karat 14K, Yellow Gold; 1.70 mm band; Final Sale | Correct inherited heading/provenance; raw current display retained without assigning original price by position |
| `ss-mia` / `SS-MIA` | Current H2 **The Mia Ring in Yellow Gold** — `$1,850` and `$925 (50% off)` | Specification says Gold Karat 14K while image alt says 10K Yellow Gold; 1.50 mm band; Final Sale | Correct inherited heading/provenance; publish existing 14K/10K conflict; no USD assignment |

The three restored records produce **44 unique product URLs**. The combined seller set becomes **13** with Mejuri restored. Structured prices become **17** only if the two Automic defaults are included; Mejuri remains blank.

## Official variant endpoints used for range scope

- Coffin default: `https://www.automicgold.com/products/coffin-ring` — 14k Yellow Gold `$1,910`.
- Coffin maximum: `https://www.automicgold.com/products/coffin-ring?variant=41654426763358` — 950 Platinum `$2,233`.
- Coffin intermediate check: `https://www.automicgold.com/products/coffin-ring?variant=42436492296286` — Nickel Free 14k White Gold `$2,039`.
- Cushion minimum: `https://www.automicgold.com/products/cushion-diamond-signet-ring?variant=42510662729822` — 14k Yellow Gold / Clear Lab Diamond `$2,408`.
- Cushion default: `https://www.automicgold.com/products/cushion-diamond-signet-ring` — 14k Yellow Gold / Salt and Pepper `$2,758`.
- Cushion maximum: `https://www.automicgold.com/products/cushion-diamond-signet-ring?variant=40139466080350` — 950 Platinum / Salt and Pepper `$3,253`.
- Store currency: `https://www.automicgold.com/cart.js` — `"currency":"USD"`.

Ranges are observations across the official variants examined, not guaranteed minima for every future size/configuration and not checkout totals.

## Rejected companion identities / dead ends

The following old companion values are not silently redirected into “evidence” for a different product:

- `https://www.automicgold.com/products/lab-grown-cushion-diamond-signet-ring` — official 404/Page Not Found. Use the canonical Cushion Diamond Signet URL above.
- `https://mejuri.com/products/bold-lab-grown-diamond-eternity-ring` — official 404/Page Not Found. Use canonical Bold Diamond Eternity; do not relabel it lab-grown.
- Companion VRAI alternate `/classic-4-prong-solitaire/...41383090421853` redirected to a page stating that the requested page does not exist. Use canonical `/classic-4-prong-dome/...32797281484893`.
- Blue Nile wrong slugs for items 194158, 195269, 315661, and 203348 resolved by item ID to the canonical products listed above. The resolved title—not the wrong slug—is authoritative.
- Zales V-20303279 and V-20046552 likewise resolve to the canonical products listed above, not the Vera Wang/1 CT titles previously shown in the companion.
- Six companion structured USD values lacked official ISO-USD support: Mejuri and Blue Nile items 194158, 195269, 316238, 315661, and 203348. Structured values are blank; dated raw displays remain.

## Policy and market references

- Mejuri standard returns: free 30-day returns in US/Canada/UK/Australia/Germany from delivery or in-store pickup; original condition/packaging; engraved and monogrammed products non-returnable; US return shipping free. Product page separately says optional complimentary engraving is not eligible for returns.
- World Gold Council: moving header `3,996.31` USD/oz; chart `Data as of 22 October, 2026`; exact header quote timestamp remains unconfirmed.
- JM Bullion: page timestamp `Oct 23, 2026 16:18 EDT`; body/table ask `$4,010.70 USD`; bid `$3,996.20`; separate header `$4,010.77`. Keep the body/table and header observations distinct.
- Automic USD cart context was re-read successfully. No transaction or cart mutation was performed.

These market values must be re-read immediately before the final build; dependent arithmetic will be regenerated from that final dated observation.
