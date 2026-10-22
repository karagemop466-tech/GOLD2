// Gold weight / melt-value calculator. No stored prices: the user enters a
// current USD-per-troy-ounce quote and its date/time. Pure client-side math.
//
// Validation (see R6-07 disposition in COORDINATION.md): only finite positive
// numbers are accepted; anything else yields an explicit error and BLANK
// outputs — never Infinity/NaN rendered as a value.
(function (root) {
  "use strict";
  var TROY_OZ_GRAMS = 31.1034768; // exact, per LBMA/NIST (see reference page)
  var VALID_KARATS = [10, 14, 18, 24];

  function num(x) {
    if (typeof x === "string" && x.trim() === "") return NaN;
    return Number(x);
  }

  // Pure computation. Returns {ok:true, ...} or {ok:false, error:"..."}.
  // weightG must be METAL-ONLY grams (stones/excluded components overstate it).
  function compute(weightG, karat, spotUsd) {
    var w = num(weightG);
    var k = num(karat);
    var s = num(spotUsd);
    if (!isFinite(w) || !(w > 0)) return { ok: false, error: "Metal weight must be a finite number greater than 0." };
    if (VALID_KARATS.indexOf(k) === -1) return { ok: false, error: "Karat must be one of 10, 14, 18, 24." };
    if (!isFinite(s) || !(s > 0)) return { ok: false, error: "Spot price must be a finite number greater than 0 (USD per troy ounce)." };
    var fraction = k / 24;
    var pureG = w * fraction;
    var perGramPure = s / TROY_OZ_GRAMS;
    var melt = pureG * perGramPure;
    if (!isFinite(pureG) || !isFinite(perGramPure) || !isFinite(melt)) {
      return { ok: false, error: "Inputs overflow finite arithmetic. Check the magnitudes." };
    }
    return { ok: true, weightG: w, karat: k, spotUsd: s, fraction: fraction,
             pureG: pureG, perGramPure: perGramPure, melt: melt };
  }

  function fmt(n, d) {
    if (!isFinite(n)) return "—";
    return n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }

  // Export for node tests: `node dashboard/scripts/calc-test.js`
  var api = { compute: compute, fmt: fmt, TROY_OZ_GRAMS: TROY_OZ_GRAMS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.GoldCalc = api;

  // Browser wiring (skipped under node).
  if (typeof document === "undefined") return;
  function val(id) { return document.getElementById(id).value; }
  function esc(s) { return String(s).replace(/[<>&"]/g, function (c) {
    return { "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]; }); }
  function calc() {
    var out = document.getElementById("calc-result");
    var r = compute(val("weight"), val("karat"), val("spot"));
    if (!r.ok) {
      out.innerHTML = "<p><strong>Enter valid inputs to see the melt value.</strong></p>" +
        "<p class='muted small'>" + esc(r.error) + " Outputs stay blank until all three inputs are finite and positive.</p>";
      return;
    }
    var spotDate = val("spot-date") || "(no date entered — record it!)";
    out.innerHTML =
      "<p class='muted small'>Pure-gold content: <strong>" + fmt(r.pureG, 3) + " g</strong> " +
      "(" + fmt(r.weightG, 2) + " g metal × " + r.karat + "K ÷ 24). Pure-gold price per gram: <strong>$" + fmt(r.perGramPure, 2) +
      "</strong> ($" + fmt(r.spotUsd, 2) + " USD ÷ " + TROY_OZ_GRAMS + " g). Spot quote dated: <strong>" +
      esc(spotDate) + "</strong>.</p>" +
      "<p>Estimated melt (raw-gold) value:</p>" +
      "<p class='val'>$" + fmt(r.melt, 2) + " USD</p>" +
      "<p class='muted small'>Melt value ≠ retail value. Craftsmanship, stones, brand, and retail margin are not included. " +
      "Per the project checklist, an unusually cheap asking price is a red flag — but this arithmetic alone cannot price a finished ring.</p>";
  }
  ["weight", "karat", "spot", "spot-date"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("input", calc);
  });
  calc();
})(typeof self !== "undefined" ? self : this);
