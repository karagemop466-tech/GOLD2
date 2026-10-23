# S-B200A880 — independent live line-by-line verification (2026-10-23 UTC)

- **Session / branch:** `S-B200A880` on `arena/b200a880-gold2`
- **Scope:** every official URL cited by the root register — 20 product pages, 6 retailer policy sources, and the WGC gold reference — re-fetched live on 2026-10-23.
- **Machine-readable record:** `audit/b200a880/live_verification_2026-10-23.json`
- **No-hallucination rule applied:** a row is "matched" only when the exact stored quote appears in the page retrieved today. Changed pages are quoted verbatim and routed through dated evidence. Client-rendered shells are recorded as limitations; nothing is filled in from memory, position, arithmetic, snippets, or a currency symbol alone.

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

1. **BE-121H6 — currency and amount changed on the official page.** On 2026-10-22 the page rendered `€ 990.00(Setting Only)`. On 2026-10-23 it renders `$890(Setting Only)`, the site currency selector reads `USD`, and the configurator breadcrumb reads `classic six-prong solitaire-$890`. Style `BE121H6-14KY`, 14K Yellow Gold, 2.5mm, and 14K white-gold prongs are unchanged. The row is updated to **890.00 USD** backed by two field-scoped quotes (`$890(Setting Only)` and the page-level `USD` label); the EUR 990 observation becomes a dated superseded record. F-007 is rewritten as a historical currency-change record with no affected rows; no exchange-rate conversion is performed anywhere.
2. **Z-20303279 — labels now present.** 2026-10-22 showed `$979.30  $1,399.00 30% Off` without labels; today the official page shows `Discounted Price $979.30  Original Price was $1,399.00 30% Off`. Amounts are unchanged. Structured price fields stay `null` under F-025 (a dollar sign does not establish ISO currency); only the verbatim unassigned text and evidence are refreshed.
3. **Z-20301172 — labels now present.** Same pattern: today `Discounted Price $769.30  Original Price was $1,099.00 30% Off`; amounts unchanged; structured fields stay `null`.
4. **Z-20046552 — label rendering varies.** Today's fetch shows `$909.30  $1,299.00 30% Off` without labels; the 2026-10-22 capture was labeled `Discounted Price $909.30` / `Original Price was $1,299.00`. Both exact texts are retained as dated observations; amounts are unchanged; structured fields stay `null`.

F-018 is reworded to state the current reality (labels present on both pages as of 2026-10-23; values remain deliberately unassigned under the F-025 ISO-currency rule) rather than leaving the stale "unlabeled" claim.

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

- **B200-F1 (medium):** Zales policy body is not present in static retrievals; the 2026-10-22 policy quotes remain dated evidence and could not be independently re-read today.
- **B200-F2 (low):** Zales price-label rendering differs between fetches for the same URLs (labeled vs unlabeled). Both variants are now preserved with dates; never assign by position.
- **B200-F3 (low):** VRAI's Plain Band title alongside a `Pavé carat weight:0.18ctw` spec remains an unresolved seller-side inconsistency (already covered by the register's notes/flags).
- **B200-F4 (process):** `tools/build_site.py` contained a hardcoded "16 item files, four retailer files" sentence on the Method page although the register holds 20 items and 6 retailers. Corrected to derived counts in this pass — the exact class of stale-number risk this project exists to catch.

## 5. What this pass does not establish

It does not prove physical purity, hallmarks, maker's marks, actual gram weights, or return eligibility of a specific order. No XRF assay, scale weighing, or seller contact occurred. Automated and manual re-verification reduce hallucination risk; they cannot eliminate it. Re-open every official source after any future edit.
