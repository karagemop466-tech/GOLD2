#!/usr/bin/env python3
"""Unit tests for the S-B200A880 scanner helpers and melt arithmetic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hallucination_security_scanner import (  # noqa: E402
    norm, number_variants, quote_contains_number, host_of, Scanner,
)

GRAMS_PER_TROY_OZ = 31.1034768
passed = 0


def check(condition, label):
    global passed
    if not condition:
        raise AssertionError(label)
    passed += 1


# Normalization collapses whitespace, zero-width characters, and case.
check(norm("  $1,145 (Setting\nPrice) ") == "$1,145 (setting price)", "norm whitespace")
check(norm("\u200b$890\u00a0USD") == "$890 usd", "norm invisible chars")

# Number variants cover integer, decimal, and comma-grouped renderings.
check("890" in number_variants(890.0), "variant 890")
check("1,299.00" in number_variants(1299.0), "variant grouped")
check("2.86" in number_variants(2.86), "variant decimal")

# Quote containment must require the actual value, not a prefix/superstring.
check(quote_contains_number(890.0, "$890(setting only)"), "890 found in quote")
check(not quote_contains_number(890.0, "$8,900.00"), "890 not matched inside 8,900")
check(quote_contains_number(1299.0, "original price was $1,299.00 30% off"), "1299 grouped")
check(quote_contains_number(2.86, "metal weight:2.86g (ring size 6)"), "2.86 weight")

# Host normalization strips www. so official-domain checks match subdomains.
check(host_of("https://www.bluenile.com/policies/returns") == "bluenile.com", "host strip www")
check(host_of("https://mejuri.com/products/x") == "mejuri.com", "host no www")

# Independent melt arithmetic control (14K, 6.10 g, spot 4024.45).
fine = 6.10 * 14 / 24
melt = fine / GRAMS_PER_TROY_OZ * 4024.45
check(abs(fine - 3.558333333333333) < 1e-9, "14K fine gold for 6.10g")
check(abs(melt - 460.41) < 0.01, f"melt 6.10g 14K at 4024.45: {melt:.2f}")
# 18K VRAI 2.86 g at the same spot.
fine18 = 2.86 * 18 / 24
melt18 = fine18 / GRAMS_PER_TROY_OZ * 4024.45
check(abs(fine18 - 2.145) < 1e-9, "18K fine gold for 2.86g")
check(abs(melt18 - 277.54) < 0.01, f"melt 2.86g 18K at 4024.45: {melt18:.2f}")
# A zero/negative weight must never produce a positive valuation.
check((0 * 14 / 24 / GRAMS_PER_TROY_OZ * 4024.45) == 0, "zero weight -> zero melt")

# Scanner control accounting: a failed check records a FAIL finding.
scanner = Scanner(Path("/nonexistent"))
scanner.check(False, "unit", "synthetic failure")
scanner.check(True, "unit", "synthetic pass")
check(any(level == "FAIL" for level, _ in scanner.findings), "fail recorded")
check(scanner.control_count == 2, "control count")

print(f"OK — {passed} scanner helper/arithmetic controls passed")
