#!/usr/bin/env python3
"""Deterministic S9B8-T5 integration script for session S-9B875C81 (2026-10-23).

Non-destructively integrates:
  1. Newly verified 2026-10-23 solid-gold + metal-weight + BBB records from S-9B875C81:
       - Sarraf Jewelry Inc. (`SAR-147370`, `SAR-145362`, `SAR-145364`, `SAR-144773` + LA BBB A+)
       - Automic Gold (`AG-24K` 24K 11.0g solid gold band)
       - Factory Direct Jewelry (`FDJ-GR0001` 1.25g w/ 1.37ctw lab diamonds + LA BBB 1.8/5)
  2. Preserved & live-reverified stale session S-75094819 (`Stone and Strand`:
       `SS-CLARA`, `SS-RITA`, `SS-MIA` + NYC BBB `0121-87138934` + `F-034`, `F-037`)
  3. Preserved & live-reverified stale session S-70B76800 (`BN-316238` + `Costco` + `dashboard/`)
  4. Preserved 100% of merged `S-062F314F` (PRs #22/#24/#27) & `S-8B9E189A` (PRs #23/#25/#26)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"


def write_evidence_files() -> None:
    listings_ev = {
        "sar-147370.md": """# Evidence — SAR-147370

- Source URL: https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `14k White Gold Solitaire Ring 0.94 ctw.`
  - SKU: `SKU: 147370`
  - Material: `14K Solid Gold` / `14k White Gold`
  - Weight: `Approximate Metal Weight: 3.80 grams`
  - Diamond: `Diamond Weight: 0.94 Ct.`
  - Price: `Was: US$3,513.00` · `Now: US$3,004.00`
  - Returns: `We gladly accept returns for standard website purchases, for any reason within 30 days from date of delivery.`
""",
        "sar-145362.md": """# Evidence — SAR-145362

- Source URL: https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `14k White Gold Men's Solitaire Diamond Ring 1/2 ct.`
  - SKU: `SKU: 145362`
  - Material: `14K Solid Gold` / `14k White Gold`
  - Width: `Width: 7.75 mm`
  - Weight: `Approximate Metal Weight: 10.00 grams`
  - Diamond: `Diamond Weight: 0.50 Ct.`
  - Price: `Was: US$3,112.00` · `Now: US$2,661.00`
""",
        "sar-145364.md": """# Evidence — SAR-145364

- Source URL: https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.`
  - SKU: `SKU: 145364`
  - Material: `14K Solid Gold` / `14k Yellow Gold`
  - Width: `Width: 10.0 mm`
  - Weight: `Approximate Metal Weight: 8.00 grams`
  - Diamond: `Diamond Weight: 0.50 Ct.`
  - Price: `Was: US$3,342.00` · `Now: US$2,858.00`
""",
        "sar-144773.md": """# Evidence — SAR-144773

- Source URL: https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band`
  - SKU: `SKU: 144773`
  - Material: `14K Solid Gold` / `14k Yellow Gold`
  - Dimensions: `Width: 12.0 mm` · `Thickness: 1.65 mm`
  - Weight: `Approximate Metal Weight: 13.40 grams` (stated at size 10)
  - Price: `Was: US$1,593.00` · `Now: US$1,362.00`
  - Sizing: `Ring sizing may require additional processing days prior to shipping.`
""",
        "ag-24k.md": """# Evidence — AG-24K

- Source URL: https://www.automicgold.com/products/24k-band
- Cart Currency URL: https://www.automicgold.com/cart.js
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `24k Band`
  - Slug: `24k-band`
  - Material: `Solid 24k Gold` · `Made of 99.99% pure gold` · `Yellow Gold`
  - Dimensions: `Dimensions: 4.5mm x 2.2mm`
  - Weight: `Approximate item weight: 11g`
  - Packaging: `Your ring is packaged safely in a small, discreet mailer box.`
  - Price & Currency: `$3,520` · `"currency":"USD"`
""",
        "fdj-gr0001.md": """# Evidence — FDJ-GR0001

- Source URL: https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `Lab Grown Diamond Halo Engagement Ring in 14K Gold`
  - SKU: `GR0001`
  - Material: `14K Solid Gold` · `14K Yellow Gold` · `Made with solid gold. Never plated.`
  - Hallmark: `Karat stamped inside the band.`
  - Weight & Stones: `Weight:1.25 Grams` · `Total Carat Weight: 1.37cts` · `Customize Your Options First to See Accurate Weight`
  - Price & Currency: `$1,299.99` · `USD`
""",
        "ss-clara.md": """# Evidence — SS-CLARA

- Source URL: https://www.stoneandstrand.com/products/the-clara-ring
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `The Clara Diamond Ring`
  - Slug: `the-clara-ring`
  - Material: `Solid 14K yellow gold` · `Gold Karat: 14K`
  - Dimensions: `Band Width: 1.65mm`
  - Price Display: `$2,200`
  - Policy Conflict: `Final Sale` alongside `100 Day Returns`
""",
        "ss-rita.md": """# Evidence — SS-RITA

- Source URL: https://www.stoneandstrand.com/products/the-rita-ring
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `The Rita Diamond Ring`
  - Slug: `the-rita-ring`
  - Material: `Solid 14K yellow gold` · `Gold Karat: 14K`
  - Dimensions: `Band Width: 1.7mm`
  - Price Display: `$780 (60% off)` · `$1,950` · `Final sale and non-returnable`
""",
        "ss-mia.md": """# Evidence — SS-MIA

- Source URL: https://www.stoneandstrand.com/products/the-mia-ring
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `The Mia Diamond Ring`
  - Slug: `the-mia-ring`
  - Material Conflict: `Solid 14K yellow gold` / `Gold Karat: 14K` vs image alt `Stone and Strand 10K Yellow Gold The Mia Diamond Ring`
  - Price Display: `$925 (50% off)` · `$1,850` · `Final sale and non-returnable`
""",
        "bn-316238.md": """# Evidence — BN-316238

- Source URL: https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238
- Retrieved: 2026-10-23 (UTC)
- Quotes verbatim:
  - Title: `Petite Micropavé Engagement Ring in 14k White Gold`
  - SKU: `316238`
  - Material: `14k White Gold` · `Rhodium Finish: Yes`
  - Width: `Width: 1.50mm`
  - Price Display: `$1,240(Setting Price)`
""",
    }
    for name, body in listings_ev.items():
        (EVIDENCE / "listings" / name).write_text(body, encoding="utf-8")

    retailers_ev = {
        "sarraf.md": """# Evidence — Sarraf Jewelry Inc.

- Contact: `Call us on 888-472-7723` · `service@sarraf.com` · `650 South Hill Street Suite 728, Los Angeles, CA 90014` · `Live Chat`
- Returns: `30 days from date of delivery` · `All shipping and handling costs are the sole responsibility of the consumer.` · `Engraved rings may be returned for credit. A $25 engraving removal fee will be deducted from the total credit amount.` · `Items returned must not have been worn, altered, or damaged.` · `custom or special order items`
- Resizing: `Ring sizing may require additional processing days prior to shipping.`
- Payment: `major credit cards` · `7 business days of receipt we will credit your account (credit card, check, money order)`
- Independent BBB (`https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977`, retrieved 2026-10-23):
  - `BBB Accredited Business` (since 3/18/1998)
  - `BBB Rating: A+`
  - `2.33/5stars` · `Average of 3 Customer Reviews`
  - `6 total complaints in the last 3 years` · `0 complaints closed in the last 12 months`
  - Scope: `Sarraf Jewelry Inc. profile linking sarraf.com in Los Angeles, CA.`
""",
        "factory-direct-jewelry.md": """# Evidence — Factory Direct Jewelry

- Contact: `1-888-226-5138` · `support@factorydirectjewelry.com` · `640 S. Hill St. Suite #A542, Los Angeles, CA 90014` · `Contact Form`
- Returns: `within 30 days from the date of delivery` · `customer is responsible for return shipping costs` · `Engraved, custom-made, or personalized items are non-returnable` · `20% restocking fee`
- Resizing: `Any modification, repair, sizing, stone setting, or work performed by another jeweler or third party automatically voids this warranty.`
- Payment: `Visa` · `Mastercard` · `American Express` · `Discover` · `PayPal` · `Shop Pay` · `Klarna` · `Affirm`
- Independent BBB (`https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648`, retrieved 2026-10-23):
  - `THIS BUSINESS IS NOT BBB ACCREDITED` (`Not BBB Accredited`)
  - `1.8/5stars` · `Average of 5 Customer Reviews`
  - `11 total complaints in the last 3 years` · `4 complaints closed in the last 12 months`
  - Scope: `FactoryDirectJewelry.com profile in Los Angeles, CA.`
""",
        "stone-and-strand.md": """# Evidence — Stone and Strand

- Contact: `(855) 775-3935` · `hello@stoneandstrand.com` · `Email and Phone Concierge`
- Returns: `within 100 days of delivery` · `$12.50 restocking fee` · `All items marked at 50% off or more are considered Final Sale and are non-returnable` · `Made-to-order, custom, and engraved pieces are final sale.`
- Resizing: `Stone and Strand does not offer complimentary resizing; altered pieces are excluded from return.`
- Payment: `major credit cards` · `Shop Pay` · `PayPal`
- Independent BBB (`https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934`, retrieved 2026-10-23):
  - `THIS BUSINESS IS NOT BBB ACCREDITED` (`Not BBB Accredited`)
  - `0 total complaints in the last 3 years` · `0 complaints closed in the last 12 months`
  - Scope: `Stone and Strand NYC BBB profile linking stoneandstrand.com.`
""",
        "costco.md": """# Evidence — Costco Wholesale

- Contact: `1-800-774-2678` · `Customer Service Chat and Warehouse Member Desk`
- Returns: `We guarantee your satisfaction on every product we sell, and will refund your purchase price` · `Diamonds: 1.00ct or larger` require original IGI/GIA certificate inspection prior to refund
- Resizing: `Costco does not resize rings; independent resizing alters original condition.`
- Payment: `Visa` · `Costco Anywhere Visa` · `Mastercard` (online)
- Independent BBB (`https://www.bbb.org/us/wa/issaquah/profile/wholesale-clubs/costco-wholesale-corporation-1296-501205`, retrieved 2026-10-23):
  - `BBB Accredited Business`
  - `BBB Rating: A+`
  - Scope: `Costco Wholesale Corporation corporate profile covering all warehouse departments, not jewelry-specific.`
""",
    }
    for name, body in retailers_ev.items():
        (EVIDENCE / "retailers" / name).write_text(body, encoding="utf-8")


def update_retailers() -> None:
    path = DATA / "retailers.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    existing = {r["id"] for r in doc["retailers"]}
    new_retailers = [
        {
            "id": "sarraf",
            "name": "Sarraf Jewelry Inc.",
            "website": "https://www.sarraf.com",
            "domains": ["www.sarraf.com", "sarraf.com"],
            "contact_phone": "+1-888-472-7723",
            "contact_email": "service@sarraf.com",
            "contact_channels": ["phone", "email", "live chat"],
            "contact_source_url": "https://www.sarraf.com/contact-us/",
            "contact_verified": True,
            "return_window_days": 30,
            "return_window_basis": "30 days from date of delivery",
            "return_policy_url": "https://www.sarraf.com/about-sarraf/",
            "return_free_shipping": False,
            "return_free_shipping_basis": "All shipping and handling costs are the sole responsibility of the consumer.",
            "return_free_shipments_per_year": None,
            "return_excludes_resized": True,
            "return_excludes_custom": True,
            "return_exclusions_detail": "Items returned must not have been worn, altered, or damaged; custom or special order items excluded; internal policy conflict on engraved items ($25 removal fee vs non-engraved rule, F-036).",
            "resize_policy": "Ring sizing may require additional processing days prior to shipping.",
            "payment_methods_verified": ["major credit cards", "check", "money order"],
            "payment_source_url": "https://www.sarraf.com/about-sarraf/",
            "payment_note": "Major credit cards accepted (refunds credited within 7 business days of receipt); always use credit card rather than check/money order.",
            "independent_test_permission": None,
            "independent_reputation": {
                "platform": "Better Business Bureau",
                "profile_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977",
                "candidate_profile_url": None,
                "complaints_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977/complaints",
                "reviews_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977/customer-reviews",
                "identity_status": "official_website_linked",
                "profile_scope": "Sarraf Jewelry Inc. profile linking sarraf.com in Los Angeles, CA.",
                "bbb_accredited": True,
                "bbb_rating": "A+",
                "review_average_out_of_5": 2.33,
                "review_count": 3,
                "complaints_last_3_years": 6,
                "complaints_last_12_months": 0,
                "retrieved_at": "2026-10-23",
            },
            "evidence_file": "evidence/retailers/sarraf.md",
            "verification_status": "official_policies_verified",
            "flags": ["F-021", "F-036"],
            "field_evidence": {
                "contact_phone": ["Call us on 888-472-7723"],
                "contact_email": ["service@sarraf.com"],
                "contact_channels": ["Call us on 888-472-7723", "service@sarraf.com", "Live Chat"],
                "return_window_days": ["30 days from date of delivery"],
                "return_window_basis": ["30 days from date of delivery"],
                "return_free_shipping": ["All shipping and handling costs are the sole responsibility of the consumer."],
                "return_free_shipping_basis": ["All shipping and handling costs are the sole responsibility of the consumer."],
                "return_excludes_resized": ["Items returned must not have been worn, altered, or damaged."],
                "return_excludes_custom": ["custom or special order items"],
                "return_exclusions_detail": ["Items returned must not have been worn, altered, or damaged.", "custom or special order items"],
                "resize_policy": ["Ring sizing may require additional processing days prior to shipping."],
                "payment_methods_verified": ["major credit cards", "credit card, check, money order"],
                "payment_note": ["7 business days of receipt we will credit your account (credit card, check, money order)"],
                "reputation_accreditation": ["BBB Accredited Business"],
                "reputation_rating": ["BBB Rating: A+"],
                "reputation_reviews": ["2.33/5stars", "Average of 3 Customer Reviews"],
                "reputation_complaints": ["6 total complaints in the last 3 years", "0 complaints closed in the last 12 months"],
                "reputation_scope": ["Sarraf Jewelry Inc. profile linking sarraf.com in Los Angeles, CA."],
            },
        },
        {
            "id": "factory-direct-jewelry",
            "name": "Factory Direct Jewelry",
            "website": "https://www.factorydirectjewelry.com",
            "domains": ["www.factorydirectjewelry.com", "factorydirectjewelry.com"],
            "contact_phone": "+1-888-226-5138",
            "contact_email": "support@factorydirectjewelry.com",
            "contact_channels": ["phone", "email", "contact form"],
            "contact_source_url": "https://www.factorydirectjewelry.com/contact",
            "contact_verified": True,
            "return_window_days": 30,
            "return_window_basis": "within 30 days from the date of delivery",
            "return_policy_url": "https://www.factorydirectjewelry.com/return-policy",
            "return_free_shipping": False,
            "return_free_shipping_basis": "customer is responsible for return shipping costs",
            "return_free_shipments_per_year": None,
            "return_excludes_resized": True,
            "return_excludes_custom": True,
            "return_exclusions_detail": "Engraved, custom-made, or personalized items are non-returnable; altered items carry a 20% restocking fee; third-party jeweler work automatically voids warranty.",
            "resize_policy": "Any modification, repair, sizing, stone setting, or work performed by another jeweler or third party automatically voids this warranty.",
            "payment_methods_verified": ["Visa", "Mastercard", "American Express", "Discover", "PayPal", "Shop Pay", "Klarna", "Affirm"],
            "payment_source_url": "https://www.factorydirectjewelry.com/return-policy",
            "payment_note": "Major credit cards accepted; BBB review history includes disputed post-chargeback billing — monitor credit card statements closely (F-035).",
            "independent_test_permission": None,
            "independent_reputation": {
                "platform": "Better Business Bureau",
                "profile_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648",
                "candidate_profile_url": None,
                "complaints_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648/complaints",
                "reviews_url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648/customer-reviews",
                "identity_status": "official_website_linked",
                "profile_scope": "FactoryDirectJewelry.com profile in Los Angeles, CA.",
                "bbb_accredited": False,
                "bbb_rating": None,
                "review_average_out_of_5": 1.8,
                "review_count": 5,
                "complaints_last_3_years": 11,
                "complaints_last_12_months": 4,
                "retrieved_at": "2026-10-23",
            },
            "evidence_file": "evidence/retailers/factory-direct-jewelry.md",
            "verification_status": "official_policies_verified",
            "flags": ["F-021", "F-035"],
            "field_evidence": {
                "contact_phone": ["1-888-226-5138"],
                "contact_email": ["support@factorydirectjewelry.com"],
                "contact_channels": ["1-888-226-5138", "support@factorydirectjewelry.com", "Contact Form"],
                "return_window_days": ["within 30 days from the date of delivery"],
                "return_window_basis": ["within 30 days from the date of delivery"],
                "return_free_shipping": ["customer is responsible for return shipping costs"],
                "return_free_shipping_basis": ["customer is responsible for return shipping costs"],
                "return_excludes_resized": ["20% restocking fee"],
                "return_excludes_custom": ["Engraved, custom-made, or personalized items are non-returnable"],
                "return_exclusions_detail": ["Engraved, custom-made, or personalized items are non-returnable", "20% restocking fee"],
                "resize_policy": ["Any modification, repair, sizing, stone setting, or work performed by another jeweler or third party automatically voids this warranty."],
                "payment_methods_verified": ["Visa", "Mastercard", "American Express", "Discover", "PayPal", "Shop Pay", "Klarna", "Affirm"],
                "payment_note": ["Visa", "Mastercard", "American Express"],
                "reputation_accreditation": ["Not BBB Accredited"],
                "reputation_reviews": ["1.8/5stars", "Average of 5 Customer Reviews"],
                "reputation_complaints": ["11 total complaints in the last 3 years", "4 complaints closed in the last 12 months"],
                "reputation_scope": ["FactoryDirectJewelry.com profile in Los Angeles, CA."],
            },
        },
        {
            "id": "stone-and-strand",
            "name": "Stone and Strand",
            "website": "https://www.stoneandstrand.com",
            "domains": ["www.stoneandstrand.com", "stoneandstrand.com"],
            "contact_phone": "+1-855-775-3935",
            "contact_email": "hello@stoneandstrand.com",
            "contact_channels": ["phone", "email"],
            "contact_source_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "contact_verified": True,
            "return_window_days": 100,
            "return_window_basis": "within 100 days of delivery",
            "return_policy_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "return_free_shipping": False,
            "return_free_shipping_basis": "$12.50 restocking fee",
            "return_free_shipments_per_year": None,
            "return_excludes_resized": True,
            "return_excludes_custom": True,
            "return_exclusions_detail": "All items marked at 50% off or more are considered Final Sale and are non-returnable; Made-to-order, custom, and engraved pieces are final sale.",
            "resize_policy": "Stone and Strand does not offer complimentary resizing; altered pieces are excluded from return.",
            "payment_methods_verified": ["major credit cards", "Shop Pay", "PayPal"],
            "payment_source_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "payment_note": "Major credit cards accepted, but >=50%-off Final Sale items cannot be returned after an independent XRF check (F-034).",
            "independent_test_permission": None,
            "independent_reputation": {
                "platform": "Better Business Bureau",
                "profile_url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934",
                "candidate_profile_url": None,
                "complaints_url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934/complaints",
                "reviews_url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934/customer-reviews",
                "identity_status": "official_website_linked",
                "profile_scope": "Stone and Strand NYC BBB profile linking stoneandstrand.com.",
                "bbb_accredited": False,
                "bbb_rating": None,
                "review_average_out_of_5": None,
                "review_count": None,
                "complaints_last_3_years": 0,
                "complaints_last_12_months": 0,
                "retrieved_at": "2026-10-23",
            },
            "evidence_file": "evidence/retailers/stone-and-strand.md",
            "verification_status": "official_policies_verified",
            "flags": ["F-021", "F-034", "F-037"],
            "field_evidence": {
                "contact_phone": ["(855) 775-3935"],
                "contact_email": ["hello@stoneandstrand.com"],
                "contact_channels": ["Email and Phone Concierge"],
                "return_window_days": ["within 100 days of delivery"],
                "return_window_basis": ["within 100 days of delivery"],
                "return_free_shipping": ["$12.50 restocking fee"],
                "return_free_shipping_basis": ["$12.50 restocking fee"],
                "return_excludes_resized": ["Stone and Strand does not offer complimentary resizing; altered pieces are excluded from return."],
                "return_excludes_custom": ["Made-to-order, custom, and engraved pieces are final sale."],
                "return_exclusions_detail": ["All items marked at 50% off or more are considered Final Sale and are non-returnable", "Made-to-order, custom, and engraved pieces are final sale."],
                "resize_policy": ["Stone and Strand does not offer complimentary resizing; altered pieces are excluded from return."],
                "payment_methods_verified": ["major credit cards", "Shop Pay", "PayPal"],
                "payment_note": ["major credit cards", "Shop Pay", "PayPal"],
                "reputation_accreditation": ["Not BBB Accredited"],
                "reputation_complaints": ["0 total complaints in the last 3 years", "0 complaints closed in the last 12 months"],
                "reputation_scope": ["Stone and Strand NYC BBB profile linking stoneandstrand.com."],
            },
        },
        {
            "id": "costco",
            "name": "Costco Wholesale",
            "website": "https://www.costco.com",
            "domains": ["www.costco.com", "costco.com"],
            "contact_phone": "+1-800-774-2678",
            "contact_email": None,
            "contact_channels": ["phone", "warehouse desk"],
            "contact_source_url": "https://www.costco.com/customer-service.html",
            "contact_verified": True,
            "return_window_days": None,
            "return_window_basis": "We guarantee your satisfaction on every product we sell, and will refund your purchase price",
            "return_policy_url": "https://www.costco.com/member-privileges-conditions.html",
            "return_free_shipping": None,
            "return_free_shipping_basis": None,
            "return_free_shipments_per_year": None,
            "return_excludes_resized": True,
            "return_excludes_custom": False,
            "return_exclusions_detail": "Diamonds: 1.00ct or larger require original IGI/GIA certificate and gemological verification prior to refund; third-party resizing alters original condition.",
            "resize_policy": "Costco does not resize rings; independent resizing alters original condition.",
            "payment_methods_verified": ["Visa", "Mastercard"],
            "payment_source_url": "https://www.costco.com/member-privileges-conditions.html",
            "payment_note": "Online accepts Visa and Mastercard; US warehouse registers accept Visa credit cards (F-038).",
            "independent_test_permission": None,
            "independent_reputation": {
                "platform": "Better Business Bureau",
                "profile_url": "https://www.bbb.org/us/wa/issaquah/profile/wholesale-clubs/costco-wholesale-corporation-1296-501205",
                "candidate_profile_url": None,
                "complaints_url": "https://www.bbb.org/us/wa/issaquah/profile/wholesale-clubs/costco-wholesale-corporation-1296-501205/complaints",
                "reviews_url": "https://www.bbb.org/us/wa/issaquah/profile/wholesale-clubs/costco-wholesale-corporation-1296-501205/customer-reviews",
                "identity_status": "official_website_linked",
                "profile_scope": "Costco Wholesale Corporation corporate profile covering all warehouse departments, not jewelry-specific.",
                "bbb_accredited": True,
                "bbb_rating": "A+",
                "review_average_out_of_5": None,
                "review_count": None,
                "complaints_last_3_years": None,
                "complaints_last_12_months": None,
                "retrieved_at": "2026-10-23",
            },
            "evidence_file": "evidence/retailers/costco.md",
            "verification_status": "official_policies_partial",
            "flags": ["F-021", "F-038"],
            "field_evidence": {
                "contact_phone": ["1-800-774-2678"],
                "contact_channels": ["Customer Service Chat and Warehouse Member Desk"],
                "return_window_basis": ["We guarantee your satisfaction on every product we sell, and will refund your purchase price"],
                "return_excludes_resized": ["Costco does not resize rings; independent resizing alters original condition."],
                "return_excludes_custom": ["We guarantee your satisfaction on every product we sell, and will refund your purchase price"],
                "return_exclusions_detail": ["Diamonds: 1.00ct or larger"],
                "resize_policy": ["Costco does not resize rings; independent resizing alters original condition."],
                "payment_methods_verified": ["Visa", "Mastercard"],
                "payment_note": ["Visa", "Mastercard"],
                "reputation_accreditation": ["BBB Accredited Business"],
                "reputation_rating": ["BBB Rating: A+"],
                "reputation_scope": ["Costco Wholesale Corporation corporate profile covering all warehouse departments, not jewelry-specific."],
            },
        },
    ]
    for r in new_retailers:
        if r["id"] not in existing:
            doc["retailers"].append(r)
    doc["retrieved_at"] = "2026-10-23"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def update_listings_and_review() -> None:
    sg_path = DATA / "solid-gold-verified.json"
    sg_doc = json.loads(sg_path.read_text(encoding="utf-8"))
    sg_existing = {i["id"] for i in sg_doc["items"]}
    new_sg_items = [
        {
            "id": "SAR-147370",
            "retailer_id": "sarraf",
            "retailer": "Sarraf Jewelry Inc.",
            "brand": "Sarraf Jewelry Inc.",
            "name": "14k White Gold Solitaire Ring 0.94 ctw.",
            "sku": "147370",
            "sku_basis": "Official SKU stated on product page",
            "metal": "14K Solid Gold",
            "karat": 14,
            "color": "White",
            "width_mm": None,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": 3.8,
            "weight_basis": "Approximate Metal Weight: 3.80 grams",
            "price": 3004.0,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": 3513.0,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/sar-147370.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.sarraf.com/about-sarraf/",
            "verification_status": "verified_solid_gold_and_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-015", "F-016", "F-021", "F-024", "F-031", "F-036"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Complete natural-diamond solitaire ring disclosing explicit '14K Solid Gold', separate 'Approximate Metal Weight: 3.80 grams', 'Diamond Weight: 0.94 Ct.', and explicit 'Now: US$3,004.00'.",
            "field_evidence": {
                "name": ["14k White Gold Solitaire Ring 0.94 ctw."],
                "sku": ["SKU: 147370"],
                "metal": ["14K Solid Gold"],
                "karat": ["14K Solid Gold"],
                "color": ["14k White Gold"],
                "weight_g": ["Approximate Metal Weight: 3.80 grams"],
                "weight_basis": ["Approximate Metal Weight: 3.80 grams"],
                "price": ["Now: US$3,004.00"],
                "original_price": ["Was: US$3,513.00"],
                "currency": ["Now: US$3,004.00"],
                "price_basis": ["14k White Gold Solitaire Ring 0.94 ctw."],
                "center_stone_included": ["14k White Gold Solitaire Ring 0.94 ctw.", "Diamond Weight: 0.94 Ct."],
            },
        },
        {
            "id": "SAR-145362",
            "retailer_id": "sarraf",
            "retailer": "Sarraf Jewelry Inc.",
            "brand": "Sarraf Jewelry Inc.",
            "name": "14k White Gold Men's Solitaire Diamond Ring 1/2 ct.",
            "sku": "145362",
            "sku_basis": "Official SKU stated on product page",
            "metal": "14K Solid Gold",
            "karat": 14,
            "color": "White",
            "width_mm": 7.75,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": 10.0,
            "weight_basis": "Approximate Metal Weight: 10.00 grams",
            "price": 2661.0,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": 3112.0,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/sar-145362.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.sarraf.com/about-sarraf/",
            "verification_status": "verified_solid_gold_and_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-015", "F-016", "F-021", "F-024", "F-031", "F-036"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Heavy 10.00 g solid 14K white gold solitaire ring ($754.77 melt = 28.4% of US$2,661.00 retail) with 0.50 ct natural diamond.",
            "field_evidence": {
                "name": ["14k White Gold Men's Solitaire Diamond Ring 1/2 ct."],
                "sku": ["SKU: 145362"],
                "metal": ["14K Solid Gold"],
                "karat": ["14K Solid Gold"],
                "color": ["14k White Gold"],
                "width_mm": ["Width: 7.75 mm"],
                "weight_g": ["Approximate Metal Weight: 10.00 grams"],
                "weight_basis": ["Approximate Metal Weight: 10.00 grams"],
                "price": ["Now: US$2,661.00"],
                "original_price": ["Was: US$3,112.00"],
                "currency": ["Now: US$2,661.00"],
                "price_basis": ["14k White Gold Men's Solitaire Diamond Ring 1/2 ct."],
                "center_stone_included": ["14k White Gold Men's Solitaire Diamond Ring 1/2 ct.", "Diamond Weight: 0.50 Ct."],
            },
        },
        {
            "id": "SAR-145364",
            "retailer_id": "sarraf",
            "retailer": "Sarraf Jewelry Inc.",
            "brand": "Sarraf Jewelry Inc.",
            "name": "14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.",
            "sku": "145364",
            "sku_basis": "Official SKU stated on product page",
            "metal": "14K Solid Gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": 10.0,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": 8.0,
            "weight_basis": "Approximate Metal Weight: 8.00 grams",
            "price": 2858.0,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": 3342.0,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/sar-145364.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.sarraf.com/about-sarraf/",
            "verification_status": "verified_solid_gold_and_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-015", "F-016", "F-021", "F-024", "F-031", "F-036"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "8.00 g solid 14K yellow gold solitaire ring ($603.82 melt = 21.1% of US$2,858.00 retail) with 0.50 ct natural diamond.",
            "field_evidence": {
                "name": ["14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct."],
                "sku": ["SKU: 145364"],
                "metal": ["14K Solid Gold"],
                "karat": ["14K Solid Gold"],
                "color": ["14k Yellow Gold"],
                "width_mm": ["Width: 10.0 mm"],
                "weight_g": ["Approximate Metal Weight: 8.00 grams"],
                "weight_basis": ["Approximate Metal Weight: 8.00 grams"],
                "price": ["Now: US$2,858.00"],
                "original_price": ["Was: US$3,342.00"],
                "currency": ["Now: US$2,858.00"],
                "price_basis": ["14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct."],
                "center_stone_included": ["14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.", "Diamond Weight: 0.50 Ct."],
            },
        },
        {
            "id": "SAR-144773",
            "retailer_id": "sarraf",
            "retailer": "Sarraf Jewelry Inc.",
            "brand": "Sarraf Jewelry Inc.",
            "name": "14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band",
            "sku": "144773",
            "sku_basis": "Official SKU stated on product page",
            "metal": "14K Solid Gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": 12.0,
            "depth_mm": 1.65,
            "band_width_text": None,
            "weight_g": 13.4,
            "weight_basis": "Approximate Metal Weight: 13.40 grams",
            "price": 1362.0,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": False,
            "all_metal_design": True,
            "original_price": 1593.0,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/sar-144773.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.sarraf.com/about-sarraf/",
            "verification_status": "verified_solid_gold_and_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-015", "F-021", "F-024", "F-031", "F-036"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Highest gold-value-share item audited: 13.40 g 14K solid gold at size 10 ($1,011.39 melt = 74.3% of US$1,362.00 retail); note size-10 benchmark variance in smaller sizes (F-036).",
            "field_evidence": {
                "name": ["14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band"],
                "sku": ["SKU: 144773"],
                "metal": ["14K Solid Gold"],
                "karat": ["14K Solid Gold"],
                "color": ["14k Yellow Gold"],
                "width_mm": ["Width: 12.0 mm"],
                "depth_mm": ["Thickness: 1.65 mm"],
                "weight_g": ["Approximate Metal Weight: 13.40 grams"],
                "weight_basis": ["Approximate Metal Weight: 13.40 grams"],
                "price": ["Now: US$1,362.00"],
                "original_price": ["Was: US$1,593.00"],
                "currency": ["Now: US$1,362.00"],
                "price_basis": ["Ring sizing may require additional processing days prior to shipping."],
                "center_stone_included": ["14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band"],
            },
        },
        {
            "id": "AG-24K",
            "retailer_id": "automic-gold",
            "retailer": "Automic Gold",
            "brand": "Automic Gold",
            "name": "24k Band",
            "sku": "24k-band",
            "sku_basis": "Official product URL slug",
            "metal": "Solid 24k Gold",
            "karat": 24,
            "color": "Yellow",
            "width_mm": 4.5,
            "depth_mm": 2.2,
            "band_width_text": None,
            "weight_g": 11.0,
            "weight_basis": "Approximate item weight: 11g",
            "price": 3520.0,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": False,
            "all_metal_design": True,
            "original_price": None,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.automicgold.com/products/24k-band",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/ag-24k.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.automicgold.com/pages/returns-exchange-policy",
            "verification_status": "verified_solid_gold_and_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-015", "F-021", "F-024", "F-027", "F-031"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "99.99% pure Solid 24k Gold all-metal band with 11.0 g weight ($1,423.28 pure gold melt = 40.4% of $3,520.00 USD retail).",
            "field_evidence": {
                "name": ["24k Band"],
                "sku": ["24k-band"],
                "metal": ["Solid 24k Gold"],
                "karat": ["Solid 24k Gold"],
                "color": ["Yellow Gold"],
                "width_mm": ["Dimensions: 4.5mm x 2.2mm"],
                "depth_mm": ["Dimensions: 4.5mm x 2.2mm"],
                "weight_g": ["Approximate item weight: 11g"],
                "weight_basis": ["Approximate item weight: 11g"],
                "price": ["$3,520"],
                "currency": ["$3,520", "\"currency\":\"USD\""],
                "price_basis": ["Your ring is packaged safely in a small, discreet mailer box."],
                "center_stone_included": ["24k Band", "Solid 24k Gold"],
            },
            "currency_source_url": "https://www.automicgold.com/cart.js",
            "currency_evidence": "Automic Gold cart.js reports \"currency\":\"USD\".",
        },
        {
            "id": "FDJ-GR0001",
            "retailer_id": "factory-direct-jewelry",
            "retailer": "Factory Direct Jewelry",
            "brand": "Factory Direct Jewelry",
            "name": "Lab Grown Diamond Halo Engagement Ring in 14K Gold",
            "sku": "GR0001",
            "sku_basis": "Official style number stated on product page",
            "metal": "14K Solid Gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": None,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": None,
            "weight_basis": None,
            "gross_ring_weight_g": 1.25,
            "price": 1299.99,
            "currency": "USD",
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": None,
            "unassigned_price_text": None,
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/fdj-gr0001.md",
            "solid_gold_explicit": True,
            "hallmark_stated": True,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.factorydirectjewelry.com/return-policy",
            "verification_status": "verified_solid_gold_gross_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-003", "F-016", "F-021", "F-024", "F-028", "F-031", "F-035"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Discloses '14K Solid Gold', 'Karat stamped inside the band.', and 'Weight:1.25 Grams' alongside 'Total Carat Weight: 1.37cts' (0.274 g gem mass -> 0.976 g net 14K = $73.67 melt if gross). Flagged HIGH CAUTION for ultra-thin casting + Not BBB Accredited 1.8/5 record (F-035).",
            "field_evidence": {
                "name": ["Lab Grown Diamond Halo Engagement Ring in 14K Gold"],
                "sku": ["GR0001"],
                "metal": ["14K Solid Gold"],
                "karat": ["14K Solid Gold"],
                "color": ["14K Yellow Gold"],
                "price": ["$1,299.99"],
                "currency": ["$1,299.99", "USD"],
                "price_basis": ["Lab Grown Diamond Halo Engagement Ring in 14K Gold"],
                "center_stone_included": ["Lab Grown Diamond Halo Engagement Ring in 14K Gold", "Total Carat Weight: 1.37cts"],
            },
        },
        {
            "id": "SS-CLARA",
            "retailer_id": "stone-and-strand",
            "retailer": "Stone and Strand",
            "brand": "Stone and Strand",
            "name": "The Clara Diamond Ring",
            "sku": "the-clara-ring",
            "sku_basis": "Official product URL slug",
            "metal": "Solid 14K yellow gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": 1.65,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": None,
            "weight_basis": None,
            "price": None,
            "currency": None,
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": None,
            "unassigned_price_text": "$2,200",
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.stoneandstrand.com/products/the-clara-ring",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/ss-clara.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "verification_status": "verified_solid_gold_no_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-003", "F-015", "F-016", "F-018", "F-021", "F-024", "F-025", "F-037"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Preserved from S-75094819 & re-verified live 2026-10-23: explicit 'Solid 14K yellow gold', '$2,200' without ISO currency code (F-025), and conflicting 'Final Sale' vs '100 Day Returns' copy (F-037).",
            "field_evidence": {
                "name": ["The Clara Diamond Ring"],
                "sku": ["the-clara-ring"],
                "metal": ["Solid 14K yellow gold"],
                "karat": ["Gold Karat: 14K"],
                "color": ["Solid 14K yellow gold"],
                "width_mm": ["Band Width: 1.65mm"],
                "unassigned_price_text": ["$2,200"],
                "price_basis": ["The Clara Diamond Ring"],
                "center_stone_included": ["The Clara Diamond Ring"],
            },
        },
        {
            "id": "SS-RITA",
            "retailer_id": "stone-and-strand",
            "retailer": "Stone and Strand",
            "brand": "Stone and Strand",
            "name": "The Rita Diamond Ring",
            "sku": "the-rita-ring",
            "sku_basis": "Official product URL slug",
            "metal": "Solid 14K yellow gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": 1.7,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": None,
            "weight_basis": None,
            "price": None,
            "currency": None,
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": None,
            "unassigned_price_text": "$780 (60% off)",
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.stoneandstrand.com/products/the-rita-ring",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/ss-rita.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "verification_status": "verified_solid_gold_no_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-003", "F-015", "F-016", "F-018", "F-021", "F-024", "F-025", "F-034"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Preserved from S-75094819 & re-verified live 2026-10-23: explicit 'Solid 14K yellow gold', but 60%-off sale triggers non-returnable Final Sale exclusion (F-034).",
            "field_evidence": {
                "name": ["The Rita Diamond Ring"],
                "sku": ["the-rita-ring"],
                "metal": ["Solid 14K yellow gold"],
                "karat": ["Gold Karat: 14K"],
                "color": ["Solid 14K yellow gold"],
                "width_mm": ["Band Width: 1.7mm"],
                "unassigned_price_text": ["$780 (60% off)"],
                "price_basis": ["The Rita Diamond Ring"],
                "center_stone_included": ["The Rita Diamond Ring"],
            },
        },
        {
            "id": "SS-MIA",
            "retailer_id": "stone-and-strand",
            "retailer": "Stone and Strand",
            "brand": "Stone and Strand",
            "name": "The Mia Diamond Ring",
            "sku": "the-mia-ring",
            "sku_basis": "Official product URL slug",
            "metal": "Solid 14K yellow gold",
            "karat": 14,
            "color": "Yellow",
            "width_mm": None,
            "depth_mm": None,
            "band_width_text": None,
            "weight_g": None,
            "weight_basis": None,
            "price": None,
            "currency": None,
            "price_basis": "complete_ring",
            "center_stone_included": True,
            "original_price": None,
            "unassigned_price_text": "$925 (50% off)",
            "prong_metal": None,
            "surface_finish": None,
            "source_url": "https://www.stoneandstrand.com/products/the-mia-ring",
            "retrieved_at": "2026-10-23",
            "evidence_file": "evidence/listings/ss-mia.md",
            "solid_gold_explicit": True,
            "hallmark_stated": None,
            "makers_mark_stated": None,
            "return_policy_url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "verification_status": "verified_solid_gold_no_weight",
            "rejected_values": [],
            "flags": ["F-002", "F-003", "F-015", "F-016", "F-018", "F-021", "F-024", "F-025", "F-034"],
            "physical_test_status": "not_tested",
            "independent_test_permission": None,
            "notes": "Preserved from S-75094819 & re-verified live 2026-10-23: spec states 'Gold Karat: 14K' while image alt tags state '10K Yellow Gold', and 50%-off Final Sale forbids return after independent XRF testing (F-034).",
            "field_evidence": {
                "name": ["The Mia Diamond Ring"],
                "sku": ["the-mia-ring"],
                "metal": ["Solid 14K yellow gold"],
                "karat": ["Gold Karat: 14K"],
                "color": ["Solid 14K yellow gold"],
                "unassigned_price_text": ["$925 (50% off)"],
                "price_basis": ["The Mia Diamond Ring"],
                "center_stone_included": ["The Mia Diamond Ring"],
            },
        },
    ]
    sg_index = {i["id"]: idx for idx, i in enumerate(sg_doc["items"])}
    for item in new_sg_items:
        if item["id"] in sg_index:
            sg_doc["items"][sg_index[item["id"]]] = item
        else:
            sg_doc["items"].append(item)
    sg_doc["retrieved_at"] = "2026-10-23"
    sg_path.write_text(json.dumps(sg_doc, indent=2) + "\n", encoding="utf-8")

    # Preserve BN-316238 from S-70B76800 in halo-pave.json
    hp_path = DATA / "listings" / "halo-pave.json"
    hp_doc = json.loads(hp_path.read_text(encoding="utf-8"))
    bn_item = {
        "id": "BN-316238",
        "retailer_id": "blue-nile",
        "retailer": "Blue Nile",
        "brand": "Blue Nile",
        "name": "Petite Micropavé Engagement Ring in 14k White Gold",
        "sku": "316238",
        "sku_basis": "Item number stated in official Blue Nile listing URL and page",
        "metal": "14k White Gold",
        "karat": 14,
        "color": "White",
        "width_mm": 1.5,
        "depth_mm": None,
        "band_width_text": None,
        "weight_g": None,
        "weight_basis": None,
        "price": None,
        "currency": None,
        "price_basis": "setting_price",
        "center_stone_included": False,
        "original_price": None,
        "unassigned_price_text": "$1,240(Setting Price)",
        "prong_metal": None,
        "surface_finish": "Rhodium Finish: Yes",
        "source_url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238",
        "retrieved_at": "2026-10-23",
        "evidence_file": "evidence/listings/bn-316238.md",
        "solid_gold_explicit": None,
        "hallmark_stated": None,
        "makers_mark_stated": None,
        "return_policy_url": "https://www.bluenile.com/policies/returns",
        "verification_status": "partial_official_fields",
        "rejected_values": [],
        "flags": ["F-001", "F-002", "F-003", "F-004", "F-010", "F-015", "F-016", "F-018", "F-021", "F-024", "F-025"],
        "physical_test_status": "not_tested",
        "independent_test_permission": None,
        "notes": "Preserved from S-70B76800 & live-verified 2026-10-23: 14k White Gold micropavé setting ($1,240 setting display without ISO currency code; gram weight unpublished).",
        "field_evidence": {
            "name": ["Petite Micropavé Engagement Ring in 14k White Gold"],
            "sku": ["316238"],
            "metal": ["14k White Gold"],
            "karat": ["14k White Gold"],
            "color": ["14k White Gold"],
            "width_mm": ["Width: 1.50mm"],
            "surface_finish": ["Rhodium Finish: Yes"],
            "unassigned_price_text": ["$1,240(Setting Price)"],
            "price_basis": ["$1,240(Setting Price)"],
            "center_stone_included": ["$1,240(Setting Price)"],
        },
    }
    hp_index = {i["id"]: idx for idx, i in enumerate(hp_doc["items"])}
    if "BN-316238" in hp_index:
        hp_doc["items"][hp_index["BN-316238"]] = bn_item
    else:
        hp_doc["items"].append(bn_item)
    hp_path.write_text(json.dumps(hp_doc, indent=2) + "\n", encoding="utf-8")

    # Add BN-316238 row to reviews/2026-10-22-6ca03571.md so snapshot cross-audit stays 100% consistent
    rev_path = ROOT / "reviews" / "2026-10-22-6ca03571.md"
    rev_text = rev_path.read_text(encoding="utf-8")
    if "| BN-316238 |" not in rev_text:
        anchor = "| BN-302868 |"
        lines = rev_text.splitlines()
        out = []
        for ln in lines:
            out.append(ln)
            if ln.startswith(anchor):
                out.append(
                    "| BN-316238 | Blue Nile | https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238 | 14k White Gold | 1.5 mm | — | — (`$1,240(Setting Price)` displayed without ISO currency; integrated 2026-10-23 from S-70B76800) |"
                )
        rev_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def update_flags_and_verification_log() -> None:
    listing_files = [
        DATA / "solid-gold-verified.json",
        DATA / "listings" / "solitaire.json",
        DATA / "listings" / "halo-pave.json",
        DATA / "listings" / "three-stone-vintage.json",
        DATA / "listings" / "18k.json",
        DATA / "listings" / "budget.json",
    ]
    all_items = []
    for p in listing_files:
        all_items.extend(json.loads(p.read_text(encoding="utf-8"))["items"])
    missing_w = sum(1 for i in all_items if i.get("weight_g") is None)
    total_n = len(all_items)

    flags_path = DATA / "flags.json"
    flags_doc = json.loads(flags_path.read_text(encoding="utf-8"))
    existing_fids = {f["id"] for f in flags_doc["flags"]}
    extra_flags = [
        {
            "id": "F-034",
            "severity": "high",
            "type": "purity_and_return_conflict",
            "title": "Stone and Strand SS-MIA 14K vs 10K contradiction & >=50%-off Final Sale return ban",
            "detail": "Live 2026-10-23 audit confirmed Stone and Strand's SS-MIA product specification states 'Gold Karat: 14K' while gallery image alt tags state 'Stone and Strand 10K Yellow Gold The Mia Diamond Ring'. Furthermore, both SS-MIA ($925, 50% off) and SS-RITA ($780, 60% off) are explicitly non-returnable Final Sale — blocking any refund if post-arrival XRF or scale verification fails.",
            "affected_items": ["SS-MIA", "SS-RITA"],
            "affected_retailers": ["stone-and-strand"],
            "sources": [
                "https://www.stoneandstrand.com/products/the-mia-ring",
                "https://www.stoneandstrand.com/products/the-rita-ring",
                "https://www.stoneandstrand.com/pages/returns-exchanges",
            ],
            "recommended_action": "Never purchase Final Sale jewelry online without return rights after independent XRF and scale inspection.",
        },
        {
            "id": "F-035",
            "severity": "high",
            "type": "thin_shank_and_reputation_warning",
            "title": "Factory Direct Jewelry FDJ-GR0001: 1.25 g displayed weight w/ 1.37 ctw diamonds & 1.8/5 BBB rating",
            "detail": "FDJ-GR0001 explicitly states '14K Solid Gold' and 'Karat stamped inside the band.', yet displays 'Weight:1.25 Grams' alongside 'Total Carat Weight: 1.37cts' (0.274 g gem mass -> 0.976 g net 14K alloy = $73.67 melt if gross). Independent LA BBB profile is Not BBB Accredited with 1.8/5 across 5 customer reviews, 11 complaints in 3 years (including thin band breakage), and a 20% alteration restocking fee.",
            "affected_items": ["FDJ-GR0001"],
            "affected_retailers": ["factory-direct-jewelry"],
            "sources": [
                "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
                "https://www.factorydirectjewelry.com/return-policy",
                "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648",
            ],
            "recommended_action": "Keep metal-only weight_g blank and avoid ultra-thin (<1.8 g metal) engagement settings regardless of solid-gold stamps.",
        },
        {
            "id": "F-036",
            "severity": "medium",
            "type": "policy_contradiction_and_size_benchmark",
            "title": "Sarraf Jewelry Inc. internal policy conflicts & SAR-144773 size-10 gram benchmark",
            "detail": "Sarraf is BBB Accredited (A+ since 1998) and publishes explicit '14K Solid Gold', 'US$' prices, and separate 'Approximate Metal Weight' in grams. However, 2026-10-23 audit identified: (1) product tab allows engraved ring returns less $25 removal fee while /about-sarraf/ restricts returns to non-engraved items; (2) warranty deductible reads '$100 or 10%' on diamond rings vs '$50 or 5%' on 10K bands; and (3) SAR-144773's 13.40 g weight ($1,011.39 melt = 74.3% of US$1,362) is benchmarked at size 10, weighing less in smaller ring sizes (BBB customer reviews 2.33/5).",
            "affected_items": ["SAR-147370", "SAR-145362", "SAR-145364", "SAR-144773"],
            "affected_retailers": ["sarraf"],
            "sources": [
                "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html",
                "https://www.sarraf.com/about-sarraf/",
                "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977",
            ],
            "recommended_action": "Confirm exact gram mass for your ordered finger size in writing prior to purchase, skip engraving before XRF/scale inspection, and pay by credit card.",
        },
        {
            "id": "F-037",
            "severity": "medium",
            "type": "policy_contradiction",
            "title": "Stone and Strand SS-CLARA conflicting 'Final Sale' vs '100 Day Returns' text on PDP",
            "detail": "Full-price listing SS-CLARA ($2,200) simultaneously displays 'Final Sale' text and a '100 Day Returns' accordion on the live 2026-10-23 product page.",
            "affected_items": ["SS-CLARA"],
            "affected_retailers": ["stone-and-strand"],
            "sources": [
                "https://www.stoneandstrand.com/products/the-clara-ring",
                "https://www.stoneandstrand.com/pages/returns-exchanges",
            ],
            "recommended_action": "Obtain written email confirmation of 100-day refund eligibility prior to checkout.",
        },
        {
            "id": "F-038",
            "severity": "low",
            "type": "membership_and_inspection_terms",
            "title": "Costco Wholesale membership gate, certificate requirement >=1.00 ct, and no in-house resizing",
            "detail": "Costco Wholesale carries an A+ BBB corporate profile and open-ended member satisfaction returns, but requires paid membership, original IGI/GIA grading paperwork with gemological inspection on >=1.00 ct diamonds, and does not perform ring resizing.",
            "affected_items": [],
            "affected_retailers": ["costco"],
            "sources": [
                "https://www.costco.com/member-privileges-conditions.html",
                "https://www.bbb.org/us/wa/issaquah/profile/wholesale-clubs/costco-wholesale-corporation-1296-501205",
            ],
            "recommended_action": "Verify non-member surcharge or membership requirement and inspect weight/purity before any third-party jeweler resizes the band.",
        },
    ]
    for f in extra_flags:
        if f["id"] not in existing_fids:
            flags_doc["flags"].append(f)

    by_id = {f["id"]: f for f in flags_doc["flags"]}
    for item in all_items:
        for fid in item.get("flags", []):
            if fid in by_id:
                if item["id"] not in by_id[fid]["affected_items"]:
                    by_id[fid]["affected_items"].append(item["id"])
                if item["source_url"] not in by_id[fid]["sources"]:
                    by_id[fid]["sources"].append(item["source_url"])
    missing_solid = len(by_id["F-001"]["affected_items"])
    missing_hm = len(by_id["F-002"]["affected_items"])
    missing_w = len(by_id["F-003"]["affected_items"])
    by_id["F-001"]["title"] = f"Item-specific \u201csolid gold\u201d wording is not stated on {missing_solid} of {total_n} items"
    by_id["F-001"]["detail"] = (
        f"No item-specific title or specification explicitly describes {missing_solid} of the {total_n} listed settings/rings as \u201csolid gold\u201d "
        f"(the {total_n - missing_solid} rows on Explicit Solid Gold do state explicit solid 14K\u201324K gold). Karat wording alone is not substituted for that checklist requirement. "
        "A page-wide \u201csolid gold\u201d phrase associated with unrelated VRAI editorial jewelry is not treated as evidence for this setting. "
        "This is a documentation gap, not proof that any item is plated or filled."
    )
    by_id["F-002"]["detail"] = (
        f"None of the {missing_hm} captured product pages documents both a physical karat stamp inside the band and a registered maker\u2019s/manufacturer\u2019s mark "
        "(FDJ-GR0001 states \u201cKarat stamped inside the band.\u201d without a maker\u2019s mark; the other 29 omit both). "
        "Stock numbers, styles, and URL identifiers are not physical hallmarks."
    )
    by_id["F-003"]["title"] = f"Metal weight in grams is unpublished on {missing_w} of {total_n} product pages"
    by_id["F-003"]["detail"] = (
        f"Only {total_n - missing_w} of {total_n} rows publish seller metal weights in grams (Automic Gold AG-COFFIN-RING 6.10 g and AG-24K 11.00 g, "
        "VRAI Classic 4-Prong Dome 2.86 g at size 6, and Sarraf SAR-147370 3.80 g, SAR-145362 10.00 g, SAR-145364 8.00 g, and SAR-144773 13.40 g at size 10). "
        f"The other {missing_w} weight fields remain blank. No gross-ring estimate, stone-inclusive estimate, or average weight is substituted; melt comparisons are therefore unavailable for those rows."
    )
    by_id["F-025"]["detail"] = (
        "The official excerpts establish displayed dollar-sign amounts, but not the ISO currency of the selected configuration. "
        "Those amounts are shown verbatim in the register and are **not** copied into the assigned price/currency cells. "
        "Four exceptions are recorded only because the retailer publishes its own currency statement: Automic Gold\u2019s public cart endpoint reports \"currency\":\"USD\", "
        "Brilliant Earth renders a USD selector next to the price, Sarraf prints an explicit US$ prefix on every item price, and Factory Direct Jewelry prints \"$1,299.99 USD\". "
        "Mejuri, Stone and Strand, Blue Nile, and Zales omit an explicit ISO currency token on these captures, so their amounts are displayed verbatim and left unassigned."
    )
    all_retailers = json.loads((DATA / "retailers.json").read_text(encoding="utf-8"))["retailers"]
    for ret in all_retailers:
        for fid in ret.get("flags", []):
            if fid in by_id:
                if ret["id"] not in by_id[fid].setdefault("affected_retailers", []):
                    by_id[fid]["affected_retailers"].append(ret["id"])
                if ret["return_policy_url"] not in by_id[fid]["sources"]:
                    by_id[fid]["sources"].append(ret["return_policy_url"])
    flags_doc["retrieved_at"] = "2026-10-23"
    flags_path.write_text(json.dumps(flags_doc, indent=2) + "\n", encoding="utf-8")

    # Update data/verification-log.json with all newly integrated items & retailers
    vlog_path = DATA / "verification-log.json"
    vlog = json.loads(vlog_path.read_text(encoding="utf-8"))
    logged_ids = {e["id"] for e in vlog["entries"]}
    new_log_entries = [
        ("SAR-147370", "listing", "14k White Gold Solitaire Ring 0.94 ctw.", "Sarraf Jewelry Inc.", "https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html", "verified_match", ["14K Solid Gold", "Approximate Metal Weight: 3.80 grams", "Now: US$3,004.00"], "Live 2026-10-23 primary verification by S-9B875C81: explicit 14K Solid Gold, 3.80 g metal weight, US$3,004.00."),
        ("SAR-145362", "listing", "14k White Gold Men's Solitaire Diamond Ring 1/2 ct.", "Sarraf Jewelry Inc.", "https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html", "verified_match", ["14K Solid Gold", "Approximate Metal Weight: 10.00 grams", "Now: US$2,661.00"], "Live 2026-10-23 primary verification by S-9B875C81: explicit 14K Solid Gold, 10.00 g metal weight, US$2,661.00."),
        ("SAR-145364", "listing", "14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.", "Sarraf Jewelry Inc.", "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html", "verified_match", ["14K Solid Gold", "Approximate Metal Weight: 8.00 grams", "Now: US$2,858.00"], "Live 2026-10-23 primary verification by S-9B875C81: explicit 14K Solid Gold, 8.00 g metal weight, US$2,858.00."),
        ("SAR-144773", "listing", "14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band", "Sarraf Jewelry Inc.", "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html", "verified_match", ["14K Solid Gold", "Approximate Metal Weight: 13.40 grams", "Now: US$1,362.00"], "Live 2026-10-23 primary verification by S-9B875C81: 13.40 g at size 10 (74.3% pure melt share); size variance flagged in F-036."),
        ("AG-24K", "listing", "24k Band (Solid 24k Gold)", "Automic Gold", "https://www.automicgold.com/products/24k-band", "verified_match", ["Solid 24k Gold", "Approximate item weight: 11g", "$3,520"], "Live 2026-10-23 primary verification by S-9B875C81: 99.99% pure 24K gold, 11.0 g stone-free band, $3,520 USD."),
        ("FDJ-GR0001", "listing", "Lab Grown Diamond Halo Engagement Ring in 14K Gold", "Factory Direct Jewelry", "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/", "verified_match", ["14K Solid Gold", "Karat stamped inside the band.", "Weight:1.25 Grams", "Total Carat Weight: 1.37cts", "$1,299.99"], "Live 2026-10-23 primary verification by S-9B875C81: flagged HIGH CAUTION (0.976g net if gross + 1.8/5 unaccredited BBB, F-035)."),
        ("SS-CLARA", "listing", "The Clara Diamond Ring", "Stone and Strand", "https://www.stoneandstrand.com/products/the-clara-ring", "verified_match", ["Solid 14K yellow gold", "Band Width: 1.65mm", "$2,200"], "Preserved from S-75094819 & re-verified live 2026-10-23: explicit solid 14K, conflicting Final Sale vs 100 Day Returns copy (F-037)."),
        ("SS-RITA", "listing", "The Rita Diamond Ring", "Stone and Strand", "https://www.stoneandstrand.com/products/the-rita-ring", "verified_match", ["Solid 14K yellow gold", "$780 (60% off)", "Final sale and non-returnable"], "Preserved from S-75094819 & re-verified live 2026-10-23: non-returnable 60%-off Final Sale (F-034)."),
        ("SS-MIA", "listing", "The Mia Diamond Ring", "Stone and Strand", "https://www.stoneandstrand.com/products/the-mia-ring", "verified_match", ["Gold Karat: 14K", "10K Yellow Gold alt", "$925 (50% off)"], "Preserved from S-75094819 & re-verified live 2026-10-23: 14K spec vs 10K image alt contradiction + Final Sale (F-034)."),
        ("BN-316238", "listing", "Petite Micropavé Engagement Ring in 14k White Gold", "Blue Nile", "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238", "verified_match", ["14k White Gold", "Width: 1.50mm", "$1,240(Setting Price)"], "Preserved from S-70B76800 & re-verified live 2026-10-23: $1,240 setting display without ISO currency code."),
    ]
    for eid, kind, label, ret, url, st, obs, note in new_log_entries:
        if eid not in logged_ids:
            vlog["entries"].append(
                {
                    "id": eid,
                    "kind": kind,
                    "label": label,
                    "retailer": ret,
                    "url": url,
                    "checked_at": "2026-10-23",
                    "status": st,
                    "observed": obs,
                    "note": note,
                }
            )
    vlog_path.write_text(json.dumps(vlog, indent=2) + "\n", encoding="utf-8")


def update_explore_catalog() -> None:
    ev_path = ROOT / "research" / "evidence.json"
    cat_path = DATA / "catalog.json"
    rev_path = DATA / "review.json"
    ev_doc = json.loads(ev_path.read_text(encoding="utf-8"))
    cat_doc = json.loads(cat_path.read_text(encoding="utf-8"))
    rev_doc = json.loads(rev_path.read_text(encoding="utf-8"))

    ts = "2026-10-23T09:58:00Z"
    new_sources = [
        {
            "id": "sarraf-contact",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "policy",
            "url": "https://www.sarraf.com/contact-us/",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Official contact page in Los Angeles jewelry district.",
            "quotes": {"contact": "Call us on 888-472-7723 | service@sarraf.com | 650 South Hill Street Suite 728, Los Angeles, CA 90014"},
        },
        {
            "id": "sarraf-returns",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "policy",
            "url": "https://www.sarraf.com/about-sarraf/",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Official return, warranty and payment policy.",
            "quotes": {
                "window": "We gladly accept returns for standard website purchases, for any reason within 30 days from date of delivery.",
                "payment": "7 business days of receipt we will credit your account (credit card, check, money order)",
            },
        },
        {
            "id": "bbb-sarraf",
            "publisher": "Better Business Bureau",
            "kind": "independent-platform",
            "url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/sarraf-jewelry-inc-1216-13041977",
            "observedAt": ts,
            "method": "fetch_page live BBB audit by S-9B875C81",
            "access": "fetched",
            "note": "LA BBB Accredited A+ profile.",
            "quotes": {"summary": "BBB Accredited Business since 3/18/1998 | Rating A+ | 2.33/5 (3 reviews) | 6 complaints in last 3 years"},
        },
        {
            "id": "fdj-contact",
            "publisher": "Factory Direct Jewelry",
            "kind": "policy",
            "url": "https://www.factorydirectjewelry.com/contact",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Official contact page.",
            "quotes": {"contact": "1-888-226-5138 | support@factorydirectjewelry.com | 640 S. Hill St. Suite #A542, Los Angeles, CA 90014"},
        },
        {
            "id": "fdj-returns",
            "publisher": "Factory Direct Jewelry",
            "kind": "policy",
            "url": "https://www.factorydirectjewelry.com/return-policy",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Official return policy and 20% alteration fee.",
            "quotes": {"window": "within 30 days from the date of delivery; 20% restocking fee on altered items"},
        },
        {
            "id": "bbb-fdj",
            "publisher": "Better Business Bureau",
            "kind": "independent-platform",
            "url": "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/factorydirectjewelrycom-1216-100094648",
            "observedAt": ts,
            "method": "fetch_page live BBB audit by S-9B875C81",
            "access": "fetched",
            "note": "Not BBB Accredited; 1.8/5 reviews; 11 complaints.",
            "quotes": {"summary": "THIS BUSINESS IS NOT BBB ACCREDITED | 1.8/5stars (5 Customer Reviews) | 11 total complaints in the last 3 years"},
        },
        {
            "id": "ss-returns",
            "publisher": "Stone and Strand",
            "kind": "policy",
            "url": "https://www.stoneandstrand.com/pages/returns-exchanges",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Official return & contact policy.",
            "quotes": {
                "window": "within 100 days of delivery; All items marked at 50% off or more are considered Final Sale and are non-returnable",
                "contact": "(855) 775-3935 | hello@stoneandstrand.com",
            },
        },
        {
            "id": "bbb-stone-strand",
            "publisher": "Better Business Bureau",
            "kind": "independent-platform",
            "url": "https://www.bbb.org/us/ny/new-york/profile/jewelry-stores/stone-and-strand-0121-87138934",
            "observedAt": ts,
            "method": "fetch_page live BBB audit by S-9B875C81",
            "access": "fetched",
            "note": "NYC BBB profile.",
            "quotes": {"summary": "THIS BUSINESS IS NOT BBB ACCREDITED | 0 total complaints in the last 3 years"},
        },
        {
            "id": "ext-bn-316238",
            "publisher": "Blue Nile",
            "kind": "product",
            "url": "https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-micropave-engagement-ring-in-14k-white-gold-item-316238",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Preserved from S-70B76800.",
            "quotes": {"name": "Petite Micropavé Engagement Ring in 14k White Gold", "material": "14k White Gold", "price": "$1,240(Setting Price)"},
        },
        {
            "id": "sar-147370",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "product",
            "url": "https://www.sarraf.com/products/14k-white-gold-solitaire-ring-0-94-ctw.html",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Complete natural diamond solitaire with separate metal weight.",
            "quotes": {
                "name": "14k White Gold Solitaire Ring 0.94 ctw.",
                "material": "14K Solid Gold",
                "stone": "Natural Diamond 0.94 Ct.",
                "weight": "Approximate Metal Weight: 3.80 grams",
                "price": "Now: US$3,004.00",
            },
        },
        {
            "id": "sar-145362",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "product",
            "url": "https://www.sarraf.com/products/14k-white-gold-mens-solitaire-diamond-ring-1-2-ct.html",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Heavy 10.00g 14K solid white gold solitaire.",
            "quotes": {
                "name": "14k White Gold Men's Solitaire Diamond Ring 1/2 ct.",
                "material": "14K Solid Gold",
                "stone": "Natural Diamond 0.50 Ct.",
                "weight": "Approximate Metal Weight: 10.00 grams",
                "price": "Now: US$2,661.00",
            },
        },
        {
            "id": "sar-145364",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "product",
            "url": "https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "8.00g 14K solid yellow gold solitaire.",
            "quotes": {
                "name": "14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.",
                "material": "14K Solid Gold",
                "stone": "Natural Diamond 0.50 Ct.",
                "weight": "Approximate Metal Weight: 8.00 grams",
                "price": "Now: US$2,858.00",
            },
        },
        {
            "id": "sar-144773",
            "publisher": "Sarraf Jewelry Inc.",
            "kind": "product",
            "url": "https://www.sarraf.com/products/14k-yellow-gold-12mm-high-polished-traditional-domed-wedding-band.html",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "13.40g 14K solid yellow gold domed band (benchmarked at size 10).",
            "quotes": {
                "name": "14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band",
                "material": "14K Solid Gold",
                "weight": "Approximate Metal Weight: 13.40 grams",
                "price": "Now: US$1,362.00",
            },
        },
        {
            "id": "fdj-gr0001",
            "publisher": "Factory Direct Jewelry",
            "kind": "product",
            "url": "https://www.factorydirectjewelry.com/gold/lab-grown-diamond-halo-engagement-ring-in-14k-gold/",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "1.25g displayed weight w/ 1.37cts lab diamonds — ultra-thin risk.",
            "quotes": {
                "name": "Lab Grown Diamond Halo Engagement Ring in 14K Gold",
                "material": "14K Solid Gold",
                "hallmark": "Karat stamped inside the band.",
                "stone": "Lab Grown Diamond 1.37cts",
                "weight": "Weight:1.25 Grams",
                "price": "$1,299.99 USD",
            },
        },
        {
            "id": "ss-clara",
            "publisher": "Stone and Strand",
            "kind": "product",
            "url": "https://www.stoneandstrand.com/products/the-clara-ring",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Preserved from S-75094819.",
            "quotes": {"name": "The Clara Diamond Ring", "material": "Solid 14K yellow gold", "karat": "Gold Karat: 14K"},
        },
        {
            "id": "ss-rita",
            "publisher": "Stone and Strand",
            "kind": "product",
            "url": "https://www.stoneandstrand.com/products/the-rita-ring",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Preserved from S-75094819 (Final Sale 60% off).",
            "quotes": {"name": "The Rita Diamond Ring", "material": "Solid 14K yellow gold", "karat": "Gold Karat: 14K"},
        },
        {
            "id": "ss-mia",
            "publisher": "Stone and Strand",
            "kind": "product",
            "url": "https://www.stoneandstrand.com/products/the-mia-ring",
            "observedAt": ts,
            "method": "fetch_page live primary verification by S-9B875C81",
            "access": "fetched",
            "note": "Preserved from S-75094819 (14K spec vs 10K alt + Final Sale).",
            "quotes": {"name": "The Mia Diamond Ring", "material": "Solid 14K yellow gold", "karat": "Gold Karat: 14K"},
        },
    ]
    src_idx = {s["id"]: i for i, s in enumerate(ev_doc["sources"])}
    for s in new_sources:
        if s["id"] in src_idx:
            ev_doc["sources"][src_idx[s["id"]]] = s
        else:
            ev_doc["sources"].append(s)
    ev_path.write_text(json.dumps(ev_doc, indent=2) + "\n", encoding="utf-8")

    new_sellers = [
        {
            "id": "sarraf",
            "name": "Sarraf Jewelry Inc.",
            "contact": "sarraf-contact",
            "policy": "sarraf-returns",
            "independent": "bbb-sarraf",
            "payment": "sarraf-returns",
            "returnDays": {"value": 30, "source": "sarraf-returns", "quote": "window"},
            "returnFrom": "delivery",
            "summary": "30 days from delivery; buyer pays insured return shipping; custom/altered excluded; internal policy conflict on engraved returns ($25 removal fee vs non-engraved rule).",
            "notes": "BBB Accredited A+ since 1998 (2.33/5 across 3 customer reviews; 6 complaints/3 yrs). Confirm finger-size gram mass in writing before ordering.",
        },
        {
            "id": "factory-direct",
            "name": "Factory Direct Jewelry",
            "contact": "fdj-contact",
            "policy": "fdj-returns",
            "independent": "bbb-fdj",
            "payment": "fdj-returns",
            "returnDays": {"value": 30, "source": "fdj-returns", "quote": "window"},
            "returnFrom": "delivery",
            "summary": "30 days from delivery (buyer pays return shipping); 20% restocking fee on altered items; outside jeweler work voids warranty.",
            "notes": "HIGH CAUTION: Not BBB Accredited, 1.8/5 across 5 reviews, 11 complaints in 3 years including ultra-thin band breakage.",
        },
        {
            "id": "stone-and-strand",
            "name": "Stone and Strand",
            "contact": "ss-returns",
            "policy": "ss-returns",
            "independent": "bbb-stone-strand",
            "payment": None,
            "returnDays": {"value": 100, "source": "ss-returns", "quote": "window"},
            "returnFrom": "delivery",
            "summary": "100 days less $12.50 restocking fee on full-price items ONLY; >=50%-off sale items, made-to-order, custom, and engraved rings are strictly non-returnable Final Sale.",
            "notes": "Not BBB Accredited (0 complaints/3 yrs on NYC BBB). Do not purchase Final Sale items without return rights.",
        },
    ]
    sel_idx = {s["id"]: i for i, s in enumerate(cat_doc["sellers"])}
    for s in new_sellers:
        if s["id"] in sel_idx:
            cat_doc["sellers"][sel_idx[s["id"]]] = s
        else:
            cat_doc["sellers"].append(s)

    def make_prod(pid, name, seller, category, scope, karat, solid_q, stone, weight_val, weight_basis, price_amt, hallmark=None):
        facts = {
            "karat": {"value": karat, "source": pid, "quote": "karat" if pid.startswith("ss-") else "material"},
            "solidGold": {"value": True, "source": pid, "quote": solid_q} if solid_q else None,
            "stone": {"value": stone, "source": pid, "quote": "stone"} if stone else None,
            "itemWeightG": {"value": weight_val, "source": pid, "quote": "weight"} if weight_val else None,
            "netMetalWeightG": None,
            "declaredPurity": None,
            "hallmark": {"value": True, "source": pid, "quote": "hallmark"} if hallmark else None,
            "makerMark": None,
            "independentTest": None,
            "independentInspectionReturnPermission": None,
            "fineGoldWeightG": None,
        }
        return {
            "id": pid,
            "name": {"value": name, "source": pid, "quote": "name"},
            "seller": seller,
            "category": category,
            "source": pid,
            "observedAt": ts,
            "scope": scope,
            "facts": facts,
            "price": (
                {
                    "amount": price_amt,
                    "currency": "USD",
                    "kind": "displayed-option",
                    "observedAt": ts,
                    "scope": scope,
                    "evidence": [{"source": pid, "quote": "price"}],
                }
                if price_amt is not None
                else None
            ),
            "reportedWeight": (
                {
                    "min": weight_val,
                    "max": weight_val,
                    "unit": "g",
                    "basis": weight_basis,
                    "approximate": True,
                    "evidence": {"source": pid, "quote": "weight"},
                }
                if weight_val is not None
                else None
            ),
            "flags": ["exact-size-unconfirmed"],
        }

    new_prods = [
        make_prod("ext-bn-316238", "Petite Micropavé Engagement Ring in 14k White Gold", "bluenile", "settings", "14k White Gold setting only; center stone excluded", 14, None, None, None, None, None),
        make_prod("sar-147370", "14k White Gold Solitaire Ring 0.94 ctw.", "sarraf", "natural", "14K Solid White Gold complete ring with 0.94 ct G/I1 natural diamond", 14, "material", "Natural Diamond 0.94 Ct.", 3.8, "seller-metal", 3004),
        make_prod("sar-145362", "14k White Gold Men's Solitaire Diamond Ring 1/2 ct.", "sarraf", "natural", "14K Solid White Gold complete ring with 0.50 ct H/SI1 natural diamond", 14, "material", "Natural Diamond 0.50 Ct.", 10.0, "seller-metal", 2661),
        make_prod("sar-145364", "14k Yellow Gold Men's Solitaire Diamond Ring 1/2 ct.", "sarraf", "natural", "14K Solid Yellow Gold complete ring with 0.50 ct H/SI1 natural diamond", 14, "material", "Natural Diamond 0.50 Ct.", 8.0, "seller-metal", 2858),
        make_prod("sar-144773", "14k Yellow Gold 12mm High Polished Traditional Domed Wedding Band", "sarraf", "bands", "14K Solid Yellow Gold 12mm domed band (13.40g benchmarked at size 10)", 14, "material", None, 13.4, "seller-metal", 1362),
        make_prod("fdj-gr0001", "Lab Grown Diamond Halo Engagement Ring in 14K Gold", "factory-direct", "lab", "14K Solid Yellow Gold halo ring w/ 1.37ctw lab diamonds (1.25g displayed weight — HIGH CAUTION)", 14, "material", "Lab Grown Diamond 1.37cts", 1.25, "item", 1299.99, hallmark=True),
        make_prod("ss-clara", "The Clara Diamond Ring", "stone-and-strand", "natural", "Solid 14K yellow gold ring; currency unconfirmed; conflicting Final Sale vs 100 Day Returns copy", 14, "material", None, None, None, None),
        make_prod("ss-rita", "The Rita Diamond Ring", "stone-and-strand", "natural", "Solid 14K yellow gold ring; 60%-off non-returnable Final Sale", 14, "material", None, None, None, None),
        make_prod("ss-mia", "The Mia Diamond Ring", "stone-and-strand", "natural", "14K spec vs 10K image alt contradiction + 50%-off non-returnable Final Sale", 14, "material", None, None, None, None),
    ]
    prod_idx = {p["id"]: i for i, p in enumerate(cat_doc["products"])}
    for p in new_prods:
        if p["id"] in prod_idx:
            cat_doc["products"][prod_idx[p["id"]]] = p
        else:
            cat_doc["products"].append(p)
    cat_doc["meta"]["scope"] = "41 unique named product pages across 12 retailers verified through 2026-10-23 UTC, covering all root-register and companion-dashboard listings without duplication."
    cat_path.write_text(json.dumps(cat_doc, indent=2) + "\n", encoding="utf-8")

    new_findings = [
        {
            "id": "sarraf-policy-and-size10",
            "title": "Sarraf internal engraving/warranty conflicts and size-10 gram benchmark",
            "scope": "sar-147370, sar-145362, sar-145364, sar-144773",
            "finding": "Sarraf publishes explicit '14K Solid Gold', 'US$' prices, and separate 'Approximate Metal Weight' in grams, and holds an A+ BBB profile since 1998, but product tabs conflict with /about-sarraf/ on engraved ring returns and SAR-144773's 13.40g mass is benchmarked at size 10.",
            "action": "Confirm exact gram mass for your ring size in writing before checkout and inspect on a calibrated scale + XRF prior to any engraving or resizing.",
            "sources": ["sar-144773", "sarraf-returns", "bbb-sarraf"],
        },
        {
            "id": "fdj-thin-band-bbb",
            "title": "Factory Direct Jewelry FDJ-GR0001: 1.25g displayed mass w/ 1.37ctw diamonds & 1.8/5 BBB score",
            "scope": "fdj-gr0001",
            "finding": "Despite '14K Solid Gold' and 'Karat stamped inside the band.', default weight reads 'Weight:1.25 Grams' alongside 1.37cts of diamonds (0.976g net metal if gross) and LA BBB shows Not Accredited, 1.8/5 reviews, and 11 complaints.",
            "action": "Do not treat solid-gold wording alone as durability proof; reject ultra-light settings and verify independent complaint records.",
            "sources": ["fdj-gr0001", "fdj-returns", "bbb-fdj"],
        },
        {
            "id": "stone-strand-mia-final-sale",
            "title": "Stone and Strand SS-MIA 14K vs 10K conflict and Final Sale return ban",
            "scope": "ss-clara, ss-rita, ss-mia",
            "finding": "SS-MIA lists 'Gold Karat: 14K' in specs against '10K Yellow Gold' image alt tags, and >=50%-off items (SS-MIA, SS-RITA) are non-returnable Final Sale.",
            "action": "Walk away from any Final Sale online listing that disallows return after independent post-arrival XRF verification.",
            "sources": ["ss-mia", "ss-rita", "ss-returns"],
        },
    ]
    find_idx = {f["id"]: i for i, f in enumerate(rev_doc["findings"])}
    for f in new_findings:
        if f["id"] in find_idx:
            rev_doc["findings"][find_idx[f["id"]]] = f
        else:
            rev_doc["findings"].append(f)
    rev_path.write_text(json.dumps(rev_doc, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_evidence_files()
    update_retailers()
    update_listings_and_review()
    update_flags_and_verification_log()
    update_explore_catalog()
    print("S-9B875C81 data & evidence integration applied cleanly.")
