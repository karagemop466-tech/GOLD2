"use strict";

const assert = require("node:assert/strict");
const calculator = require("../assets/calculator.js");

function close(actual, expected, tolerance = 1e-9) {
  assert.equal(typeof actual, "number");
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);
}

assert.equal(calculator.GRAMS_PER_TROY_OUNCE, 31.1034768);

const vrai = calculator.calculate(2.86, 18, 4028.53);
close(vrai.fineGoldGrams, 2.145);
close(vrai.meltUsd, 2.145 / 31.1034768 * 4028.53);
assert.equal(vrai.askingToMeltRatio, null);
assert.equal(vrai.askingMinusMeltUsd, null);

const reference = calculator.calculate(6, 14, 4028.53, 1000);
close(reference.fineGoldGrams, 3.5);
close(reference.meltUsd, 3.5 / 31.1034768 * 4028.53);
close(reference.askingToMeltRatio, 1000 / reference.meltUsd);
close(reference.askingMinusMeltUsd, 1000 - reference.meltUsd);
assert.ok(reference.askingMinusMeltUsd > 0);

const below = calculator.calculate(10, 10, 4000, 1);
assert.ok(below.askingMinusMeltUsd < 0);
close(below.askingToMeltRatio, 1 / below.meltUsd);
assert.equal(calculator.money(below.askingMinusMeltUsd).startsWith("−$"), true);

const invalidBaseInputs = [
  [null, 14, 4000], ["", 14, 4000], [0, 14, 4000], [-1, 14, 4000],
  ["abc", 14, 4000], [Infinity, 14, 4000], [NaN, 14, 4000], [true, 14, 4000],
  [3, 0, 4000], [3, -14, 4000], [3, 25, 4000], [3, "abc", 4000],
  [3, 14, 0], [3, 14, -4000], [3, 14, "abc"], [3, 14, Infinity], [1e308, 24, 4000]
];
for (const [weight, karat, spot] of invalidBaseInputs) {
  const result = calculator.calculate(weight, karat, spot, 1000);
  assert.deepEqual(result, {
    fineGoldGrams: null,
    meltUsd: null,
    askingToMeltRatio: null,
    askingMinusMeltUsd: null
  });
}

for (const asking of [null, "", 0, -1, "abc", Infinity, NaN]) {
  const result = calculator.calculate(3, 14, 4000, asking);
  close(result.fineGoldGrams, 1.75);
  assert.ok(result.meltUsd > 0);
  assert.equal(result.askingToMeltRatio, null);
  assert.equal(result.askingMinusMeltUsd, null);
}

assert.equal(calculator.money(null), "—");
assert.equal(calculator.money(NaN), "—");
assert.equal(calculator.money(0), "$0.00");
assert.equal(calculator.money(-12.5), "−$12.50");
assert.equal(calculator.bindCalculator({ getElementById: () => null }), false);

console.log("PASS calculator: formula, dated VRAI case, asking comparisons, blanks, invalid inputs, negative difference, and formatting");
