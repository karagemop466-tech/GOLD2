/* GOLD2 Companion Dashboard — NIST Precious-Metals & Gemstone Mass Calculator
 * Exact constants from NIST OWM & FTC 16 CFR Part 23:
 *   1 troy ounce (ozt) = 31.1034768 grams (exact)
 *   1 pennyweight (dwt) = 1.55517384 grams (exact)
 *   1 metric carat (ct) = 0.200 grams (exact)
 * Strict security: zero innerHTML / outerHTML / eval sinks; textContent only.
 */
(function () {
  "use strict";

  var TROY_OZ_GRAMS = 31.1034768;
  var DWT_GRAMS = 1.55517384;
  var CARAT_GRAMS = 0.2;
  var ALLOWED_KARATS = { 9: true, 10: true, 14: true, 18: true, 20: true, 22: true, 24: true };

  function fmt(n, digits) {
    if (typeof n !== "number" || !Number.isFinite(n)) {
      return "—";
    }
    return n.toLocaleString("en-US", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    });
  }

  function parseStrictNumber(raw) {
    if (typeof raw === "number") {
      return Number.isFinite(raw) ? raw : NaN;
    }
    if (typeof raw !== "string") {
      return NaN;
    }
    var trimmed = raw.trim();
    if (!trimmed) {
      return NaN;
    }
    var val = Number(trimmed);
    return Number.isFinite(val) ? val : NaN;
  }

  /* Backward-compatible core arithmetic required by calc-test.js: compute(weight, karat, spot) */
  function compute(weight, karat, spot, options) {
    var w = parseStrictNumber(weight);
    var k = parseStrictNumber(karat);
    var s = parseStrictNumber(spot);
    var opts = options || {};
    var unit = opts.unit || "g";
    var stoneCarats = opts.stoneCarats === undefined || opts.stoneCarats === "" ? 0 : parseStrictNumber(opts.stoneCarats);
    var ask = opts.ask === undefined || opts.ask === "" || opts.ask === null ? null : parseStrictNumber(opts.ask);

    if (!Number.isFinite(w) || w <= 0 || w > 10000) {
      return { ok: false, error: "Enter a positive finite ring weight." };
    }
    if (!Number.isFinite(k) || !ALLOWED_KARATS[k]) {
      return { ok: false, error: "Select a supported gold karat (9K, 10K, 14K, 18K, 20K, 22K, or 24K)." };
    }
    if (!Number.isFinite(s) || s <= 0 || s > 1000000) {
      return { ok: false, error: "Enter a positive finite gold spot quote in USD / troy oz." };
    }
    if (!Number.isFinite(stoneCarats) || stoneCarats < 0 || stoneCarats > 500) {
      return { ok: false, error: "Set gemstone carat deduction must be 0 or a positive number." };
    }

    var grossG = w;
    if (unit === "dwt") {
      grossG = w * DWT_GRAMS;
    } else if (unit === "ozt") {
      grossG = w * TROY_OZ_GRAMS;
    } else if (unit !== "g") {
      return { ok: false, error: "Unsupported mass unit." };
    }

    var stoneG = stoneCarats * CARAT_GRAMS;
    var netMetalG = grossG - stoneG;
    if (netMetalG <= 0) {
      return { ok: false, error: "Gemstone mass (" + fmt(stoneG, 3) + " g) equals or exceeds total entered weight." };
    }

    var purity = k / 24;
    var pureG = netMetalG * purity;
    var perGramPure = s / TROY_OZ_GRAMS;
    var melt = pureG * perGramPure;

    var ratio = null;
    var goldSharePct = null;
    var markupUsd = null;
    if (ask !== null) {
      if (!Number.isFinite(ask) || ask <= 0) {
        return { ok: false, error: "Optional USD asking price must be positive." };
      }
      ratio = ask / melt;
      goldSharePct = (melt / ask) * 100;
      markupUsd = ask - melt;
    }

    return {
      ok: true,
      grossG: grossG,
      stoneG: stoneG,
      netMetalG: netMetalG,
      purity: purity,
      pureG: pureG,
      perGramPure: perGramPure,
      melt: melt,
      ratio: ratio,
      goldSharePct: goldSharePct,
      markupUsd: markupUsd
    };
  }

  function initBrowserCalculator() {
    if (typeof document === "undefined") {
      return;
    }
    var wEl = document.getElementById("calc-weight");
    var unitEl = document.getElementById("calc-unit");
    var karatEl = document.getElementById("calc-karat");
    var stoneEl = document.getElementById("calc-stone-ct");
    var spotEl = document.getElementById("calc-spot");
    var askEl = document.getElementById("calc-ask");
    if (!wEl || !unitEl || !karatEl || !spotEl) {
      return;
    }

    var outNet = document.getElementById("out-net-g");
    var outPure = document.getElementById("out-pure-g");
    var outMelt = document.getElementById("out-melt");
    var outRatio = document.getElementById("out-ratio");
    var outShare = document.getElementById("out-share");
    var outMsg = document.getElementById("calc-status");

    function render() {
      var res = compute(wEl.value, Number(karatEl.value), spotEl.value, {
        unit: unitEl.value,
        stoneCarats: stoneEl ? stoneEl.value : "0",
        ask: askEl ? askEl.value : ""
      });
      if (!res.ok) {
        if (outNet) outNet.textContent = "—";
        if (outPure) outPure.textContent = "—";
        if (outMelt) outMelt.textContent = "—";
        if (outRatio) outRatio.textContent = "—";
        if (outShare) outShare.textContent = "—";
        if (outMsg) outMsg.textContent = res.error;
        return;
      }
      if (outNet) outNet.textContent = fmt(res.netMetalG, 3) + " g";
      if (outPure) outPure.textContent = fmt(res.pureG, 3) + " g";
      if (outMelt) outMelt.textContent = "$" + fmt(res.melt, 2);
      if (outRatio) outRatio.textContent = res.ratio !== null ? fmt(res.ratio, 2) + "×" : "—";
      if (outShare) outShare.textContent = res.goldSharePct !== null ? fmt(res.goldSharePct, 1) + "%" : "—";
      if (outMsg) {
        var note = "Nominal arithmetic at $" + fmt(res.perGramPure, 2) + "/fine g (" + fmt(res.purity * 100, 2) + "% pure gold).";
        if (res.stoneG > 0) {
          note += " Deducted " + fmt(res.stoneG, 3) + " g gemstone mass from gross scale weight.";
        }
        if (res.ratio !== null && res.ratio < 1.0) {
          note += " RED FLAG: Asking price is BELOW raw gold melt value — high counterfeit/plating risk!";
        }
        outMsg.textContent = note;
      }
    }

    [wEl, unitEl, karatEl, stoneEl, spotEl, askEl].forEach(function (el) {
      if (el) {
        el.addEventListener("input", render);
        el.addEventListener("change", render);
      }
    });

    var buttons = document.querySelectorAll("[data-preset-weight]");
    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener("click", function (ev) {
        var btn = ev.currentTarget;
        wEl.value = btn.getAttribute("data-preset-weight") || "";
        unitEl.value = "g";
        karatEl.value = btn.getAttribute("data-preset-karat") || "14";
        if (stoneEl) stoneEl.value = btn.getAttribute("data-preset-stone") || "0";
        if (askEl) askEl.value = btn.getAttribute("data-preset-ask") || "";
        render();
      });
    }

    if (typeof window !== "undefined" && window.location && window.location.search) {
      var params = new URLSearchParams(window.location.search);
      if (params.get("w")) wEl.value = params.get("w");
      if (params.get("k")) karatEl.value = params.get("k");
      if (params.get("ct") && stoneEl) stoneEl.value = params.get("ct");
      if (params.get("ask") && askEl) askEl.value = params.get("ask");
    }

    render();
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      TROY_OZ_GRAMS: TROY_OZ_GRAMS,
      DWT_GRAMS: DWT_GRAMS,
      CARAT_GRAMS: CARAT_GRAMS,
      fmt: fmt,
      compute: compute
    };
  }
  initBrowserCalculator();
})();
