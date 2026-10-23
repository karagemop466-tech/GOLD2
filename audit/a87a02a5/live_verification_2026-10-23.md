# Live line-by-line re-verification — 2026-10-23 (session S-A87A02A5)

**Rule applied:** a value counts as re-verified only if the official page rendered it
again *today*, to this session, and the exact observed text is transcribed below.
Anything that could not be re-read is marked **not re-read this pass** — which means
neither verified nor invalidated. Nothing is inferred, averaged, carried forward
silently, or filled in from a neighbouring field, a search snippet, or memory.

- **Scanner/method:** `fetch_page` (rendered page text). No search snippets were used
  as product facts. `bash` has no route to retailer hosts in this sandbox (allowlist is
  `github.com`, `api.github.com`, `codeload.github.com`, `registry.npmjs.org`,
  `pypi.org`, `files.pythonhosted.org`), so no `curl`/`wget` cross-check was possible.
- **Retrieval window:** 2026-10-23, between ~10:05Z and ~10:25Z. Per-request
  timestamps were not separately recorded; the window is stated instead of inventing
  precise times.
- **Repository state at the start of this log:** `main` @ `22d9f85` (20 root rows).
  **State at the end:** `main` @ `161dbe1` (30 root rows, 36 flags, 41 combined
  products). Peers merged PRs #22–#32 *during* this pass, so every finding below was
  re-checked against the newer tree before being published. Two of this session's
  findings were fixed by peers mid-pass and are recorded as resolved, not open.

---

## 1. Official pages actually re-read today

### 1.1 Automic Gold — Sapphire Ring ✅ CONFIRMED (all five register values)

**URL:** https://www.automicgold.com/products/sapphire-ring (HTML, chunk 0 of 2)
**Register row:** `AG-SAPPHIRE-RING` (`data/solid-gold-verified.json`)

| Register field | Stored value | Text observed on the page today | Verdict |
|---|---|---|---|
| `name` | Sapphire Ring | `Sapphire Ring` | match |
| `price` / `currency` | 526.0 / USD | `$526` | match |
| `metal` / `karat` | Solid 14k Gold / 14 | `Solid 14k Gold and 950 Platinum` | match |
| `color` | Yellow | `14k Yellow Gold` (default selected metal) | match |
| `width_mm` | 1.1 | `Band is 1.1mm` | match |
| `depth_mm` | 1.1 | `Approximately 1.1mm` (Height) | match |
| `gross_ring_weight_g` | 1.2 | `Item Weight` → `Approximately 1.2g (gold) or 1.8g (platinum)` | match |
| `weight_g` | **null** | page states an *item* weight that includes the stone | correctly left blank |
| `center_stone_included` | true | `Natural sapphire. Natural stones may vary in color` | match |
| `solid_gold_explicit` | true | `Solid 14k Gold and 950 Platinum`; `950 platinum and/or Solid 14k gold` | match |

Also displayed, recorded as context and **not** promoted into register fields:
`Stone is 3mm in diameter` · `Only 3 units left in stock!` · `Rated 5.0 out of 5` /
`1 Review` · `Ships from New York City • Production time is 1 to 5 business days •
Free returns (US only)` · `100% Recycled gold` · `Manufacturing In house in New York` ·
metal options `14k Yellow Gold`, `14k White Gold`, `Nickel Free 14k White Gold`,
`14k Rose Gold`, `14k Champagne Gold`, `950 Platinum`.

No hallmark or maker's-mark wording appeared → `hallmark_stated` / `makers_mark_stated`
stay `null` (F-002). No physical inspection was performed (F-024).

### 1.2 Automic Gold — Coffin Ring ✅ price CONFIRMED, ⚠️ weight not re-read

**URL read:** https://www.automicgold.com/products/coffin-ring.js — the retailer's own
product-data endpoint on `automicgold.com` (chunk 0 of 3). Used because the HTML page
serves a six-chunk CookieYes consent wall before any product text.
**Register row:** `AG-COFFIN-RING`

| Observed today (verbatim JSON) | Meaning | Verdict vs register |
|---|---|---|
| `"title":"Coffin Ring"` | product name | match |
| `"price":191000` | 191000 minor units = **$1,910.00** | match (`price` 1910.0, USD) |
| `"price_min":191000`, `"price_max":223300`, `"price_varies":true` | price varies by option | **not recorded in the register** → FIND-A87A-03 |
| variant `"14k Yellow Gold"` → `"price":191000` | the row's recorded colour | match |
| variant `"Nickel Free 14k White Gold"` → `"price":203900` | a different option | not recorded (informational) |
| `"available":true`, `"vendor":"Automic Gold Studio"`, `"type":"Rings"` | seller/availability | consistent |
| tags `collections-rings-engagement`, `engagement` | sold as an engagement ring | consistent with `price_basis: complete_ring` |

Deliberately **not** used: the endpoint's variant `"weight"` fields (`0`, `227`). Those
are Shopify shipping weights, not jewellery mass — the same trap `research/evidence.json`
already warns about ("Do not use shipping-weight fields in Shopify JSON as jewelry weight").

**Not re-read this pass:** the spec text `Approximately 6.1g (gold) or 9.2g (platinum)`
that supports `weight_g: 6.1`. The HTML page's first three chunks contained only cookie
consent text and the later chunks could not be retrieved (see §3). The 6.10 g figure
therefore still rests on session `S-8C810C15`'s 2026-10-22 capture; this session neither
confirms nor challenges it.

### 1.3 Automic Gold — Cushion Diamond Signet Ring ⚠️ CONFIRMED BUT UNSCOPED

**URL read:** https://www.automicgold.com/products/cushion-diamond-signet-ring.js (chunk 0 of 4)
**Register row:** `AG-CUSHION-SIGNET` — publishes `price: 2758.0`, `currency: USD`,
`color: Yellow`, quote `"$2,758"`.

| Observed today | Amount |
|---|---|
| `"price"` / `"price_min"` | 240800 → **$2,408.00** |
| `"price_max"` | 325300 → **$3,253.00** |
| `"price_varies"` | **true** |
| variant `14k Yellow Gold / Salt and Pepper Diamond` | 275800 → **$2,758.00** |
| variant `14k Yellow Gold / Clear Lab Diamond` | 240800 → **$2,408.00** |
| variant `14k White Gold / Salt and Pepper Diamond` | 275800 → $2,758.00 |

So `$2,758` is a **real** price the seller charges today — it is not invented. But it is
the price of one specific configuration, and a second 14k *yellow* gold configuration of
the same ring is $2,408. The register records neither the stone option nor the range, and
`observed_native_display` is `null`. See **FIND-A87A-03**.

Description text also observed: `"the ultimate engagement ring for a masculine person"`;
tags include `engagement`, `promise ring`. Not re-read: the `5.5g` item weight (HTML spec
block not retrieved) — it retains its 2026-10-22 capture.

### 1.4 World Gold Council — gold spot reference ⚠️ VALUE HAS MOVED

**URL:** https://www.gold.org/goldhub/data/gold-prices (HTML, complete in 1 chunk)

Verbatim observations:

```
USD
/oz
-
4,023.19
Last Updated
```

```
22 October, 2026
```

```
Data as of 22 October, 2026
```

```
Prices are quoted in currency unit per troy ounce unless otherwise stated.
```

```
Updated weekly.
```

```
Market Data: Provided by ICE Data Services.
```

```
As of 18 March 2025, only limited LBMA Gold Price data is available on our website.
Historical LBMA Gold Price data has been removed at the request of the ICE Benchmark
Administration.
```

The page also carries a WGC **impersonation-scam alert** stating that the organisation
"does not provide investment advice, solicit or sell gold or any other financial
products, open customer trading accounts, or request money transfers under any
circumstances" — relevant to this project's seller-verification checklist, recorded as
context only.

**Three reads of this one URL on two consecutive days produced three different numbers:**

| Read (UTC) | Header value | Chart "Data as of" | Where it lives |
|---|---|---|---|
| 2026-10-22 (S-da963b79) | 4,028.53 | 21 October 2026 | superseded observation in `data/gold-price.json` |
| 2026-10-23 (peer PR #29/#30) | 4,024.45 | 22 October 2026 | **currently published** reference |
| 2026-10-23 ~10:10Z (this session) | **4,023.19** | 22 October 2026 | recorded here only |

The header is a moving intraday figure and the page publishes no quote-as-of timestamp
for it — only `Last Updated` with no value, and a separate chart date. This independently
corroborates the repository's own **F-026**. The published reference was already refreshed
by peers during this pass, so this session's earlier "stale reference" finding is recorded
as **resolved by peer**, and the residual issue is the volatility itself, not a wrong number.

**No melt figure in this document is a valuation.** Where arithmetic is shown it is
conditional arithmetic on a dated display value, per the project's standing rule.

### 1.5 VRAI — Classic 4-Prong Dome ⚠️ identity CONFIRMED, weight not re-read

**URL:** https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-32797281484893
(HTML, chunk 0 of 3)
**Register row:** `VRAI-CLASSIC-4P`

| Observed today | Verdict |
|---|---|
| page title `Classic Round Brilliant Engagement Ring \| Plain Band \| 18k Yellow Gold` | match: 18K, plain band |
| `Metal:18k Yellow Gold`, `Round Brilliant · 18k Yellow Gold` | match (`metal`, `karat`) |
| carat options `1.0` `1.5` `2.0`, `Shown with 1.5ct`, `View Full Inventory` | configurator; no centre stone selected |
| metal swatches: `Platinum` (pt), `18k Yellow Gold`, `18k White Gold`, `14k Rose Gold`, `Rose Gold And Platinum` | mixed-metal configurator, consistent with existing flags |
| **no price anywhere in the retrieved HTML** | ✅ `price: null` is correct (F-008: price is client-side only) |

**Not re-read this pass:** the specification block carrying `2.86 g at ring size 6`
(chunk 1 retrieval failed). That weight therefore still rests on the earlier dated
capture. Note the title/`Plain Band` vs `Pavé` wording question raised as REQ-8C8-03 by a
previous session is **not** resolvable from chunk 0 and is left open rather than guessed.

---

## 2. Rows NOT independently re-read by this session

These rows keep their own sessions' dated observations (2026-10-22 / 2026-10-23). They are
listed explicitly so no reader mistakes silence for verification.

| Row(s) | Published value at risk | Why not re-read |
|---|---|---|
| `MJ-BOLD-ETERNITY` | $2,900 ("From$2,900") | 3 retrieval attempts failed (§3) |
| `BE-121H6` | €990.00 EUR setting-only | not attempted after failures began |
| `VRAI-CLASSIC-4P` weight | 2.86 g @ size 6 | spec chunk unretrievable |
| `AG-COFFIN-RING` weight | 6.10 g | spec text behind consent wall, later chunks failed |
| `AG-CUSHION-SIGNET` weight | 5.5 g gross | spec chunk not retrieved |
| 11 Blue Nile rows (`BN-*`) | all `price: null` | not re-read; blank is the conservative state |
| 4 Zales rows (`Z-*`) | displayed amounts, all `price: null` | not re-read |
| `AG-24K`, `SAR-147370`, `SAR-145362`, `SAR-145364`, `SAR-144773`, `SS-CLARA`, `SS-RITA`, `SS-MIA`, `BN-316238`, `FDJ-GR0001` | prices/weights added by peers on 2026-10-23 | added to `main` after this session's fetch capability failed; not re-read |

**Cross-session corroboration, clearly labelled:** `verification.html` states that
`S-9B875C81` re-read `FDJ-GR0001` live on 2026-10-23 and matched `"14K Solid Gold"`,
`"Karat stamped inside the band."`, `"Weight:1.25 Grams"`, `"Total Carat Weight: 1.37cts"`,
`"$1,299.99"`. That is another session's observation, recorded in the repository. This
session did **not** retrieve that page and does not present it as its own verification.

---

## 3. Retrieval-infrastructure failure (recorded, not papered over)

Between ~10:08Z and ~10:25Z, `fetch_page` returned an Alibaba OSS proxy error instead of
page content on five attempts:

```
SignatureDoesNotMatch — The request signature we calculated does not match the
signature you provided.  <EC>0002-00000040</EC>
```

Affected attempts: `automicgold.com/products/coffin-ring` (later chunks),
`mejuri.com/products/bold-diamond-eternity-ring` (JSON endpoint and HTML, twice),
`vrai.com` spec chunk. This is a fault in the retrieval path, **not** a retailer refusal,
bot block, paywall or 404 — and it is explicitly *not* evidence that any page changed.
Where a retry succeeded (coffin-ring chunk 2) the content was cookie-consent text and is
reported as such rather than being treated as a product capture.

---

## 4. What this log does not establish

- No physical ring, stamp, purity, scale weight or XRF assay was examined. Nothing here is
  a physical authentication.
- Seller wording ("Solid 14k Gold", "Karat stamped inside the band.") is a **seller
  statement**. It is not independent proof of purity.
- A successful retrieval does not certify that a price is current at checkout for a chosen
  size/configuration, nor that a product will be returnable.
- The observations above are dated. Spot prices and displayed prices move; re-open the
  official page before acting on any figure.
- **Look for hallucinations again after every review.** This log is one pass, not a
  certificate.
