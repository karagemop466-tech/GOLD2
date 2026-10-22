// Negative + arithmetic tests for dashboard/assets/calculator.js (R6-07).
// Run: node dashboard/scripts/calc-test.js   (exit 0 = all pass)
const calc = require("../assets/calculator.js");
let failures = 0;
function check(name, cond, detail) {
  if (cond) { console.log("  PASS " + name); }
  else { failures++; console.log("  FAIL " + name + (detail ? " — " + detail : "")); }
}

// Arithmetic: 4.50 g metal, 14K, $4,000.00 USD/troy oz (independently computed).
const r = calc.compute(4.5, 14, 4000);
check("valid inputs accepted", r.ok === true);
check("pure grams exact", r.ok && r.pureG === 2.625, "got " + (r.ok && r.pureG));
check("per-gram value", r.ok && Math.abs(r.perGramPure - 128.60298627451192) < 1e-9);
check("melt value", r.ok && Math.abs(r.melt - 337.5828389705938) < 1e-9);
check("troy constant exact", calc.TROY_OZ_GRAMS === 31.1034768);

// Karat fractions.
check("18K fraction", calc.compute(24, 18, 100).pureG === 18);
check("10K fraction", calc.compute(24, 10, 100).pureG === 10);
check("24K fraction", calc.compute(2, 24, 100).pureG === 2);

// Negative cases: all must fail closed with an error (never Infinity/NaN out).
for (const [name, args] of [
  ["Infinity weight", [Infinity, 14, 4000]],
  ["Infinity spot", [4.5, 14, Infinity]],
  ["zero weight", [0, 14, 4000]],
  ["negative weight", [-1, 14, 4000]],
  ["NaN weight", [NaN, 14, 4000]],
  ["empty weight", ["", 14, 4000]],
  ["text weight", ["abc", 14, 4000]],
  ["zero spot", [4.5, 14, 0]],
  ["negative spot", [4.5, 14, -50]],
  ["bad karat 12", [4.5, 12, 4000]],
  ["bad karat 0", [4.5, 0, 4000]],
]) {
  const t = calc.compute(...args);
  check("rejects " + name, t.ok === false && typeof t.error === "string");
}
check("fmt guards non-finite", calc.fmt(Infinity, 2) === "—" && calc.fmt(NaN, 2) === "—");

console.log(failures === 0 ? "calc-test: PASS" : "calc-test: FAIL (" + failures + ")");
process.exit(failures === 0 ? 0 : 1);
