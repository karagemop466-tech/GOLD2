# Official-reference baseline for peer review

Observed by session `5ff05cf9-gold2` on 2026-10-22 (UTC). These are reference checks for reviewing the combined site, not product listings or current metal-price observations. Quotes and paraphrases below were checked against the fetched official pages, not inferred from search-result snippets.

| Review topic | Official-source observation | How the combined site must use it | Official manual-review link |
|---|---|---|---|
| Karat ratio | The FTC states that the total of pure gold and other metal adds to 24 parts; its examples describe 18K as 18 parts gold plus 6 parts other metal and 14K as 14 parts gold plus 10 parts other metal. | `karat ÷ 24` is a nominal ratio calculation. It does not establish the purity of a particular physical ring. | [FTC — Buying Platinum, Gold, and Silver Jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) |
| “Solid gold” terminology | In its “Is it solid gold?” section, the FTC says the phrase means the gold item is not hollow and that the item also has a karat mark. | Do not present “solid gold” as an independent laboratory purity result or as proof of every other buying requirement. Preserve the user's explicit-solid-gold listing gate while separately checking for plating/coating language and post-purchase testing. | [FTC — Gold Jewelry, “Is it solid gold?”](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry#gold) |
| Plating exclusions | The FTC distinguishes gold filled, gold overlay, rolled gold plate, gold electroplate, vermeil, gold flashed, and gold washed from unqualified gold descriptions. | Excluded/surface-coated terminology must remain visible to the eligibility review. A karat string by itself does not clear the solid-gold review. | [FTC — Gold Jewelry, plating sections](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry#gold) |
| Maker / trademark near quality mark | The FTC advises looking near the karat quality mark for the name or U.S. registered trademark of the company standing behind the mark. | A seller name elsewhere on a page is not evidence that a physical ring bears the mark. Keep the physical maker's-mark field unverified unless official evidence explicitly supports it. | [FTC — Gold Jewelry, “How many karats?”](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry#gold) |
| Quality-mark limitations and identity | 16 CFR 23.10 addresses misleading quality marks and describes a National Stamping Act identity requirement for covered persons applying/importing specified quality marks. | Do not reduce this guidance to “a stamp proves authenticity.” A quality mark can apply only to part of a product; context matters. | [eCFR — 16 CFR 23.10](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.10) |
| Seller research and returns | The FTC recommends checking what others say about a seller and finding refund/return policies in writing. | Seller-authored reputation claims are not independent reputation research. Link the applicable official policy and preserve custom/resizing exclusions. | [FTC — Before You Buy](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry#buying) |
| Troy-ounce conversion | The NIST conversion chart gives **1 troy ounce = 31.1034768 grams** and demonstrates dividing a price per troy ounce by that factor to obtain a price per gram. | Cite NIST for the unit conversion; keep the source/date/unit of any actual gold-price input separate. | [NIST — Conversion Factors for Precious Metal Sales (PDF)](https://www.nist.gov/document/precious-metals-conversion-information-march2015pdf) |
| NIST numerical examples | The NIST PDF contains illustrative prices such as $1,181.93 per troy ounce and $38 per gram, explicitly used in “How do I…” conversion examples. | **Never publish these examples as a current gold quote.** They are arithmetic examples in a conversion guide, not a dated market observation. | [NIST PDF — conversion examples](https://www.nist.gov/document/precious-metals-conversion-information-march2015pdf) |
| Carat versus karat | NIST's conversion page identifies carat as a gemstone weight unit and its PDF separately describes karat as a gold-alloy purity measure. | Never substitute a stone's carat weight for ring weight in grams or gold karat. | [NIST — Precious Metals Conversion Information](https://www.nist.gov/pml/owm/metric-si/unit-conversion/precious-metals-conversion-information) |

## Independent arithmetic controls

These are reviewer-calculated controls using the above ratios, not product facts:

| Input | Formula | Expected unrounded result |
|---|---|---|
| 10 g total, 14K nominal | `10 × 14 ÷ 24` | `5.833333333333… g` nominal fine-gold weight |
| 4 g total, 18K nominal | `4 × 18 ÷ 24` | `3 g` nominal fine-gold weight |
| 10 g total, 10K nominal | `10 × 10 ÷ 24` | `4.166666666666… g` nominal fine-gold weight |
| 1 troy ounce in grams | NIST conversion | `31.1034768 g` |

The site's displayed rounding must be labeled and must not create a price or weight where an input was missing.

## Review pass result and next-pass recommendation

- **Pass completed:** official terminology, quality-mark guidance, seller-research guidance, and unit-conversion baseline fetched and compared line by line on 2026-10-22.
- **Irregularity to watch:** “solid gold” is sometimes used loosely in shopping copy; the FTC's non-hollow definition makes overbroad authenticity wording a review risk.
- **No current price established here:** no live metal-price quote or product price was collected in this baseline.
- **Required next pass:** after any combined-site edit, re-check every calculator statement and every “solid,” “verified,” hallmark, and plating claim against this baseline; rerun hallucination and security scans and inspect Flagged for Review.
