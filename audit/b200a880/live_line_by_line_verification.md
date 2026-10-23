# S-B200A880 — independent live line-by-line verification (2026-10-23 UTC)

- **Session / branch:** `S-B200A880` on `arena/b200a880-gold2`
- **Scope:** every official URL cited by the root register — 20 product pages, 6 retailer policy sources, and the WGC gold reference — re-fetched live on 2026-10-23.
- **Machine-readable record:** `audit/b200a880/live_verification_2026-10-23.json`
- **No-hallucination rule applied:** a row is "matched" only when the exact stored quote appears in the page retrieved today. Changed pages are quoted verbatim and routed through dated evidence. Client-rendered shells are recorded as limitations; nothing is filled in from memory, position, arithmetic, snippets, or a currency symbol alone.

## 0. Integration outcome after rebasing onto `main` (2026-10-23)

This branch's data-refresh commit was prepared against the pre-merge tree, then rebased onto
`main` `39c81db` (PRs #22–#27, sessions `S-062F314F` and `S-8B9E189A`). The rebase showed that
**every data change this pass had independently reached had already been integrated on `main`
from the parallel sessions' own live fetches**, in several cases under a stricter evidence model.
Rather than overwrite their work, this branch keeps only its unique artifacts — this audit folder,
the scanner (`3,056` controls) and its unit tests — and accepts the integrated register:

| This session's independent finding (2026-10-23) | State on `main` after PRs #22–#27 |
|---|---|
| WGC header **4,024.45 USD/oz**, chart "Data as of 22 October, 2026", `quote_date` null; 4,028.53/4,024.36 only as superseded observations | Integrated identically in `data/gold-price.json` and on `verification.html` (`check-gold-quote`); F-026 wording matches |
| BE-121H6 renders **`$890(Setting Only)`** with a page-level USD selector; EUR €990 retained only as dated history; no FX conversion | Integrated identically; modeled as `partial_official_fields` with F-007 kept on the item and the duplicate currency finding merged back into F-007 (no F-032) |
| Z-20303279 / Z-20301172 now show **labeled** Discounted/Original texts with unchanged amounts | Same verbatim strings captured independently; stored in `observed_native_display` + field evidence, structured price stays `null` under F-025 |
| Z-20046552 unlabeled `$909.30  $1,299.00 30% Off` render | Same render captured independently; row stays `partial_price_unassigned` (F-018) |
| 16 further rows exact matches | Same matches recorded entry-by-entry on `verification.html` |
| Builder hardcoded "16 item files" count (B200-F4) | Independently fixed on `main`: `tools/build_site.py` now derives all counts (`len(items)`/`len(retailers)`); corroborated, no edit from this branch needed |

Modeling decision accepted from `main`: the **one-currency rule (F-033)** — an amount is assigned
to a currency only when the retailer itself states the ISO currency. The register therefore holds
**4 assigned prices** (three Automic Gold rows backed by the public cart endpoint, plus BE-121H6
backed by its rendered USD selector); 16 displayed amounts remain verbatim-but-unassigned,
including Blue Nile setting prices and the Mejuri "From $2,900" display that this pass re-read
verbatim. That is stricter than, and not in conflict with, the observations recorded below.

**Unique contribution of this pass:** `AG-CUSHION-SIGNET` is marked "not re-read this pass" on
`main`'s verification log (stored observation dated 2026-10-22). This session re-fetched
<https://www.automicgold.com/products/cushion-diamond-signet> on 2026-10-23 and re-read
`$2,758`, solid 14k gold, and the stone-inclusive ~5.5 g item weight exactly as stored — an
additional independent dated observation for that one row, recorded in the machine-readable JSON.

## 1. Gold reference — verified change

Re-fetch of <https://www.gold.org/goldhub/data/gold-prices> on 2026-10-23 returned:

```
USD /oz - 4,024.45
```

and chart metadata:

```
Data as of 22 October, 2026
Market Data: Provided by ICE Data Services.
```

The stored current quote was **4,028.53** with chart date 21 October 2026 (retrieved 2026-10-22). Action taken:

- `usd_per_troy_oz` moves to **4,024.45**; `retrieved_at` becomes 2026-10-23; `chart_as_of_date` becomes 2026-10-22.
- 4,028.53 is retained only inside `superseded_observations` with its reason. The earlier 4,024.36 intraday observation is also retained.
- `quote_date` stays `null`: the moving header still publishes no exact as-of timestamp (F-026 remains open with updated wording).

## 2. Product rows — 16 exact matches, 4 dated evidence updates

### Exact matches (16 rows, no data change)

| Row | Re-read on 2026-10-23 |
|---|---|
| BN-203348 | `$1,145(Setting Price)` · stock `502120y14` · 14K Yellow Gold · 2.40mm |
| BN-194158 | `$1,125(Setting Price)` · stock `500000y` · 18K Yellow Gold · 1.90mm |
| BN-195269 | `$1,155(Setting Price)` · stock `501130y` · 18K Yellow Gold · 1.80mm |
| BN-192506 | `$1,255(Setting Price)` · stock `502250y14` · 14K Yellow Gold · 1.60mm |
| BN-315661 | `$2,210(Setting Price)` · stock `505094w14` · 14K White Gold · 1.75mm · By James Allen |
| BN-195402 | `$1,300(Setting Price)` · stock `501480w14` · 14K White Gold · 1.70mm |
| BN-302868 | `$1,050(Setting Price)` · stock `501480w14l` · 14K White Gold · 1.70mm · lab-grown |
| BN-195639 | `$1,000(Setting Price)` · stock `501130y14` · 14K Yellow Gold · 1.80mm |
| BN-194548 | `$1,045(Setting Price)` · stock `501290w14` · 14K White Gold · 2.00mm |
| BN-193625 | `$1,950(Setting Price)` · stock `502350y14` · 14K Yellow Gold · 1.80mm |
| VRAI-CLASSIC-4P | no price rendered; `Metal weight:2.86g (Ring size 6)`; `Band depth:1.6mm`; Plain Band title vs `Pavé carat weight:0.18ctw` inconsistency still live |
| Z-19957449 | `Discounted Price $899.00` |
| AG-COFFIN-RING | `$1,910` · `Solid 14k Gold and 950 Platinum` · 3mm band · `Approximately 6.1g (gold) or 9.2g (platinum)` |
| AG-CUSHION-SIGNET | `$2,758` · Solid 14k Gold · item weight gold 5.5g (stone-inclusive, correctly excluded from `weight_g`) |
| AG-SAPPHIRE-RING | `$526` · Solid 14k Gold · 1.1mm band · item weight ~1.2g gold (stone-inclusive, correctly excluded) |
| MJ-BOLD-ETERNITY | `From$2,900` · `Solid White Gold (14k)` · 2.6mm band · no gram weight |

All four explicitly assigned solid-gold prices ($1,910 / $2,758 / $526 / From $2,900) re-read identically. No hallucinated price was found.

### Dated evidence updates (4 rows)

1. **BE-121H6 — currency and amount changed on the official page.** On 2026-10-22 the page rendered `€ 990.00(Setting Only)`. On 2026-10-23 it renders `$890(Setting Only)`, the site currency selector reads `USD`, and the configurator breadcrumb reads `classic six-prong solitaire-$890`. Style `BE121H6-14KY`, 14K Yellow Gold, 2.5mm, and 14K white-gold prongs are unchanged. The row carries **890.00 USD** backed by two field-scoped quotes (`$890(Setting Only)` and the page-level `USD` label); the EUR 990 observation is retained only as dated superseded history. On integrated `main`, F-007 remains applied to the item as a historical currency-change record (the parallel sessions' duplicate F-032 finding was merged into F-007); no exchange-rate conversion is performed anywhere.
2. **Z-20303279 — labels now present.** 2026-10-22 showed `$979.30  $1,399.00 30% Off` without labels; today the official page shows `Discounted Price $979.30  Original Price was $1,399.00 30% Off`. Amounts are unchanged. Structured price fields stay `null` under F-025 (a dollar sign does not establish ISO currency); only the verbatim unassigned text and evidence are refreshed.
3. **Z-20301172 — labels now present.** Same pattern: today `Discounted Price $769.30  Original Price was $1,099.00 30% Off`; amounts unchanged; structured fields stay `null`.
4. **Z-20046552 — label rendering varies.** Today's fetch shows `$909.30  $1,299.00 30% Off` without labels; the 2026-10-22 capture was labeled `Discounted Price $909.30` / `Original Price was $1,299.00`. Both exact texts are retained as dated observations; amounts are unchanged; structured fields stay `null`.

F-018 on integrated `main` states the same reality (label presence is unstable between renders; values remain deliberately unassigned under the F-025 ISO-currency rule). The item notes on `main` still contain an older "without labels" sentence for Z-20303279/Z-20301172 even though the captured evidence quote itself is labeled; this is wording drift inside an open flag, not a wrong value, and is noted for a future wording pass rather than edited from this audit-only scope.

## 3. Retailer policy re-checks

| Retailer | Official source re-read 2026-10-23 | Result |
|---|---|---|
| Blue Nile | `/policies/returns` | 30 days from shipment; resized/custom/engraved excluded; two complimentary returns/year; one free resize within 6 months — matches |
| VRAI | `/returns-exchanges` | 30 days; `$300` engagement-ring recycling fee; resized/custom non-eligible; free US returns; page revised 2025-03-21 — matches |
| Brilliant Earth | `/30-Day-Returns/` | 30-day returns; engraved/CYO rings require assisted returns; custom/modified/engraved resize fees — matches F-019 |
| Zales | `/return-and-exchange-policy` | URL resolves (200, titled "Returns and Exchanges") but static fetch returns a client-rendered shell; product shells still show "Free and easy 30-day returns". **Limitation, not a contradiction — no field changed.** |
| Automic Gold | `/pages/returns-exchange-policy` | 30-day free US returns; engraved/custom/modified items final sale; `care@automicgold.com` — matches |
| Mejuri | FAQ standard return policy | free 30-day returns; engraved/monogrammed and final-sale items non-returnable; US return shipping free — matches |

## 4. Irregularities flagged for review (non-blocking)

- **B200-F1 (medium, disposition updated post-rebase):** this session's static retrieval of the Zales policy page returned only a client-rendered shell, so the 2026-10-22 policy quotes could not be re-read through this tool path. The parallel `S-062F314F` pass retrieved the same URL successfully on 2026-10-23 and re-confirmed "Returns are allowed within 30 days from the purchase (shipment) date and exchanges within 60 days" plus the sized-to-order refund wording (see `verification.html`, `check-zales-returns`). The policy is therefore re-verified on `main`; the shell limitation remains true for this session's fetch path.
- **B200-F2 (low):** Zales price-label rendering differs between fetches for the same URLs (labeled vs unlabeled). Both variants are preserved with dates on `main` (`observed_native_display`, F-018); never assign by position.
- **B200-F3 (low):** VRAI's Plain Band title alongside a `Pavé carat weight:0.18ctw` spec remains an unresolved seller-side inconsistency (already covered by the register's notes/flags).
- **B200-F4 (process, resolved on `main`):** `tools/build_site.py` previously hardcoded an "item files / retailer files" sentence that could drift from the register. The parallel sessions independently replaced every typed count with data-derived counts (`len(items)` / `len(retailers)`), which is also the fix this session had implemented; the rebase confirmed it in the integrated builder — the exact class of stale-number risk this project exists to catch.

## 5. What this pass does not establish

It does not prove physical purity, hallmarks, maker's marks, actual gram weights, or return eligibility of a specific order. No XRF assay, scale weighing, or seller contact occurred. Automated and manual re-verification reduce hallucination risk; they cannot eliminate it. Re-open every official source after any future edit.
