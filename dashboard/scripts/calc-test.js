// Negative + NIST arithmetic + gemstone mass deduction tests for dashboard/assets/calculator.js
// Run: node dashboard/scripts/calc-test.js   (exit 0 = all pass)
const calc = require("../assets/calculator.js");
let failures = 0;
function check(name, cond, detail) {
  if (cond) {
    console.log("  PASS " + name);
  } else {
    failures += 1;
    console.log("  FAIL " + name + (detail ? " — " + detail : ""));
  }
}

// 1. Core NIST constants & standard karat arithmetic
const r = calc.compute(4.5, 14, 4000);
check("valid inputs accepted", r.ok === true);
check("pure grams exact", r.ok && r.pureG === 2.625, "got " + (r.ok && r.pureG));
check("per-gram value", r.ok && Math.abs(r.perGramPure - 128.60298627451192) < 1e-9);
check("melt value", r.ok && Math.abs(r.melt - 337.5828389705938) < 1e-9);
check("troy constant exact", calc.TROY_OZ_GRAMS === 31.1034768);
check("pennyweight constant exact", calc.DWT_GRAMS === 1.55517384);
check("carat constant exact", calc.CARAT_GRAMS === 0.2);

// 2. Live 2026-10-23 spot ($3,995.47/oz) across units & asking-price multiples
const ozt24 = calc.compute(1, 24, 3995.47, { unit: "ozt" });
const dwt24 = calc.compute(20, 24, 3995.47, { unit: "dwt" });
check("1 ozt == 20 dwt == $3,995.47 exact", Math.abs(ozt24.melt - 3995.47) < 1e-9 && Math.abs(dwt24.melt - 3995.47) < 1e-9);

const sarBand = calc.compute(13.4, 14, 3995.47, { ask: 1362 });
check("SAR-144773 13.40g 14K melt $1,004.11 & 73.72% gold share", Math.abs(sarBand.melt - 1004.108234) < 1e-3 && Math.abs(sarBand.goldSharePct - 73.7231) < 1e-2);

const gemDeduct = calc.compute(1.25, 14, 3995.47, { stoneCarats: 1.37, ask: 1299.99 });
check("FDJ-GR0001 gross 1.25g minus 1.37ct (0.274g) = 0.976g net 14K ($73.14)", Math.abs(gemDeduct.netMetalG - 0.976) < 1e-9 && Math.abs(gemDeduct.melt - 73.1350) < 1e-2);

// 3. Negative cases: fail closed with error string (never NaN/Infinity)
for (const [name, args] of [
  ["Infinity weight", [Infinity, 14, 3995.47]],
  ["Infinity spot", [4.5, 14, Infinity]],
  ["zero weight", [0, 14, 3995.47]],
  ["negative weight", [-1, 14, 3995.47]],
  ["NaN weight", [NaN, 14, 3995.47]],
  ["empty weight", ["", 14, 3995.47]],
  ["text weight", ["abc", 14, 3995.47]],
  ["zero spot", [4.5, 14, 0]],
  ["negative spot", [4.5, 14, -50]],
  ["bad karat 12", [4.5, 12, 3995.47]],
  ["bad karat 0", [4.5, 0, 3995.47]],
  ["gem mass exceeds gross ring weight", [0.5, 14, 3995.47, { stoneCarats: 5.0 }]]
]) {
  const t = calc.compute(...args);
  check("rejects " + name, t.ok === false && typeof t.error === "string");
}
check("fmt guards non-finite", calc.fmt(Infinity, 2) === "—" && calc.fmt(NaN, 2) === "—");

console.log(failures === 0 ? "calc-test: PASS" : "calc-test: FAIL (" + failures + ")");
process.exit(failures === 0 ? 0 : 1);
