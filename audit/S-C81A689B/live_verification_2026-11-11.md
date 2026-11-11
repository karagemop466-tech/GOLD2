# Live Line-by-Line Verification Log — Session `S-C81A689B` (2026-11-11 UTC)

> **No Hallucinations Policy:** Every published claim must be supported by a dated, field-scoped verbatim excerpt from an official primary-source page actually retrieved. Unconfirmed values are left blank (`null`) and flagged on the **Flagged for Review** page. Never infer, estimate, convert currencies, or extrapolate across sizes or variants. Stored values are dated snapshots; a live re-read that differs is recorded here as a dated observation and is **never written back** into stored product data. **Always look for hallucinations again after every review.**

- **Session:** `S-C81A689B`
- **Branch:** `arena/c81a689b-gold2` (HEAD `9819787`, equal to `origin/main`)
- **Date:** `2026-11-11` (UTC)
- **Live Retrievals Performed (`fetch_page`):** 6 official primary-source fetches (all chunk 0 unless noted) plus re-read of WGC header panel.

---

## 1. World Gold Council Spot Price & NIST Bullion Arithmetic (re-live read)

| Field | Live Observation (2026-11-11 UTC) | Source |
|---|---|---|
| Official Source URL | `https://www.gold.org/goldhub/data/gold-prices` | World Gold Council |
| Moving Header Quote | `USD /oz - 4,059.49 Last Updated` | WGC header panel |
| Page Date / Data Date | `10 November, 2026` / `Data as of 10 November, 2026` | WGC page |
| Market Data Attribution | `Market Data: Provided by ICE Data Services.` | WGC body |
| Units Statement | `Prices are quoted in currency unit per troy ounce unless otherwise stated.` | WGC body |
| Update Schedule | `Updated weekly.` | WGC body |
| Header Timestamp | **Unpublished (`null`)** — WGC header carries no independent timestamp (`F-026`) | WGC header panel |
| Stored root reference (dated) | `$3,995.47 / troy oz`, retrieved `2026-10-23`, quote date unconfirmed (`F-026`) | `index.html`, `data/gold-price.json` |
| NIST Conversion Factor | `1 troy ounce = 31.103 476 8 g` | NIST Precious Metals Conversion Information |
| Derived illustrative rate (live) | `$4,059.47 ...` not computed — conditional arithmetic only; no value written back | NIST × WGC |
| Derived illustrative rate (stored) | `$3,995.47 / 31.1034768 = $128.4573432 / fine g` (conditional arithmetic only) | `audit/86379ca7/live_verification_2026-10-23.md` |

**Assessment:** The WGC moving header moved from the stored `$3,995.47/oz` (23 Oct 2026 snapshot) to `$4,059.49/oz` (page dated 10 Nov 2026). Expected for a moving market reference; neither value is a "current quote" and neither is written into product data. Root `index.html` keeps `$3,995.47` labeled as a dated snapshot with `quote_date: null` (F-026). No inconsistency in stored data; new observation recorded here only.

---

## 2. FTC — Buying Platinum, Gold, and Silver Jewelry (official U.S. consumer guidance)

| Field | Live Observation (2026-11-11 UTC) | Source |
|---|---|---|
| Official Source URL | `https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry` | FTC (consumer.ftc.gov), article dated November 2024 |
| Karat definition | "Pure gold, or 24 karat (24K) gold... The total of pure gold and other metal adds up to 24 parts. A piece of jewelry marked 18K gold is 18 parts gold mixed with six parts of another metal. A piece marked 14K gold is 14 parts gold mixed with 10 parts of another metal." | FTC, Gold Jewelry |
| Trademark/maker's mark | "Near the karat quality mark, look for the name or the U.S. registered trademark of the company that will stand behind the mark. ... If you're thinking about buying a piece of gold jewelry but don't see a trademark along with the karat mark, don't buy it." | FTC, Gold Jewelry |
| "Solid gold" meaning | "The phrase 'solid gold' means the gold item isn't hollow. The item will also have a karat mark like 14K or 18K..." | FTC, Gold Jewelry |
| Plated / filled / overlay | "Gold filled," "gold overlay," "rolled gold plate (RGP)" describe a layer of at least 10K gold mechanically applied to a base metal; "gold electroplate" ≥10K and ≥0.175 microns; vermeil = sterling silver base coated/plated with gold; "gold flashed/washed" = very thin electroplating. | FTC, Gold Jewelry |
| Seller research | "Find out what others say about a seller... Find the store's refund and return policies — and get them in writing." | FTC, Before You Buy |
| Problem reporting | ReportFraud.ftc.gov; state attorney general; JVC mediation program | FTC, Report Problems |

**Assessment:** Fully consistent with the repo's buying checklist (`data/requirements.json`) and the root `index.html` checklist: karat is a seller claim, "solid gold" must be explicit, karat mark must be paired with a maker's/trademark mark, plated/vermeil/filled/overlay/gold-tone are excluded categories, and returns/payment/verification steps match FTC guidance. No stored-data change required.

---

## 3. GIA — "Gold-Plated Gold" (Gems & Gemology, Summer 2025, Vol. 61, No. 2)

| Field | Live Observation (2026-11-11 UTC) | Source |
|---|---|---|
| Official Source URL | `https://www.gia.edu/gems-gemology/summer-2025-lab-notes-gold-plated-gold` | GIA |
| XRF caveat | "Adding a layer of gold plating to a gold alloy affects the X-ray fluorescence (XRF) results... coating 10K gold with a precise amount of gold plating can alter the XRF results, identifying the alloy as 14K or 18K gold without detecting any of the plating." | GIA Lab Notes |
| Recommendation | XRF is "one of the most reliable ways" but "unreliable... when a piece of metal is coated with the same element"; visual observation under a microscope is essential to check for discoloration, plating damage, or prior destructive testing. | GIA Lab Notes |

**Assessment:** Supports the repo's "Upon arrival" and "Best verification" checklist items and the caution that XRF alone can mislead in gold-over-gold cases. Stored guidance pages already reflect this; no stored-data change required.

---

## 4. Official product re-reads (sample)

| Entry ID | Retailer | Official URL Retrieved | Verbatim Excerpts Observed Live | Verification Result |
|---|---|---|---|---|
| `SAR-151362` | Sarraf Jewelry Inc. | `https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-belcher-diamond-ring-1ctw.html` (0) | Title `14k Yellow gold Mens Solitaire Belcher Diamond Ring 1ctw`; `MSRP: US$31,899.00 \| Was: US$9,594.00 \| Now: US$8,203.00`; `Material: 14K Solid Gold`; `Approximate Metal Weight: 9.20 grams`; `Diamond Weight: 1.00 Ct.`; `Diamond Color: H`; `Diamond Clarity: SI 1`; `Diamond (Natural / Lab Created): Natural`; SKU:3552G, Stock Number 151362 | **MATCHED EXACT** against stored evidence (`evidence/listings/sar-151362.md`, retrieved 2026-10-23 by S-C74095E5): title, "14K Solid Gold", 9.20 g, US$8,203.00, 1.00 ct H/SI1 natural. No change. |
| `BE-121H6` | Brilliant Earth | `https://www.brilliantearth.com/Classic-Six-Prong-Solitaire-Ring-Gold-BE121H6-1151507/` (0, 4) | Page title `Classic Six-Prong Solitaire Ring in 18K Yellow Gold`; `$1,090(Setting Only)`; `Metal: 18K Yellow Gold`; `Prong metal: 14K White Gold`; `Width: 2.5 mm`; style `BE121H6-18KY`; page lists variant links including `.../Classic-Six-Prong-Solitaire-Ring-14K-Gold-BE121H6-76788910/` | **IRREGULARITY FLAGGED (see Findings):** The stored row cites `...-76788910/` (14K Yellow Gold, `BE121H6-14KY`, `$890(Setting Only)`, retrieved 2026-10-23, USD selector confirmed in chunks 4–5 by S-86379CA7). That official URL now canonicalizes to/serves the **18K Yellow Gold** variant at **$1,090(Setting Only)**. Stored row left unchanged as a dated snapshot; no value inferred, averaged, or written back. Flagged for manual review. |

---

## 5. Verdict per entry re-read

| Entry | Result | Action |
|---|---|---|
| SAR-151362 | Matched exact | None; evidence current |
| BE-121H6 | Variant drift on official URL | New flag `F-C81-01` (advisory); stored data untouched |
| WGC reference | Moving header moved ($3,995.47 → $4,059.49) | Dated-snapshot rule confirmed; no write-back |

No prices, weights, karats, or policies were inferred, converted, or filled in. Zero physical testing; zero purchase approvals.
