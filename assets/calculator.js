(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  if (typeof document !== "undefined") {
    root.GoldCalculator = api;
    document.addEventListener("DOMContentLoaded", function () {
      api.bindCalculator(document);
    });
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const GRAMS_PER_TROY_OUNCE = 31.1034768;
  const GRAMS_PER_PENNYWEIGHT = 1.55517384;
  const EMPTY = "—";

  function positiveNumber(value) {
    if (value === null || value === "" || typeof value === "boolean") return null;
    const number = Number(value);
    return Number.isFinite(number) && number > 0 ? number : null;
  }

  function calculate(weight, karat, spot, askingPrice, unit) {
    const rawWeight = positiveNumber(weight);
    const listedKarat = positiveNumber(karat);
    const goldSpot = positiveNumber(spot);
    const empty = {
      fineGoldGrams: null,
      meltUsd: null,
      askingToMeltRatio: null,
      askingMinusMeltUsd: null
    };
    if (rawWeight === null || listedKarat === null || goldSpot === null || listedKarat > 24) {
      return empty;
    }
    const u = unit || "g";
    const metalWeight = u === "dwt" ? rawWeight * GRAMS_PER_PENNYWEIGHT : (u === "ozt" ? rawWeight * GRAMS_PER_TROY_OUNCE : rawWeight);

    const fineGoldGrams = metalWeight * listedKarat / 24;
    const meltUsd = fineGoldGrams / GRAMS_PER_TROY_OUNCE * goldSpot;
    if (!Number.isFinite(fineGoldGrams) || !Number.isFinite(meltUsd) || meltUsd <= 0) return empty;
    const result = {
      fineGoldGrams: fineGoldGrams,
      meltUsd: meltUsd,
      askingToMeltRatio: null,
      askingMinusMeltUsd: null
    };

    if (askingPrice !== null && askingPrice !== "") {
      const asking = positiveNumber(askingPrice);
      if (asking !== null) {
        result.askingToMeltRatio = Number.isFinite(asking / meltUsd) ? asking / meltUsd : null;
        result.askingMinusMeltUsd = asking - meltUsd;
      }
    }
    return result;
  }

  function money(value) {
    if (!Number.isFinite(value)) return EMPTY;
    const sign = value < 0 ? "−" : "";
    return sign + "$" + Math.abs(value).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function bindCalculator(doc) {
    const weight = doc.getElementById("w");
    const unit = doc.getElementById("unit");
    const karat = doc.getElementById("k");
    const spot = doc.getElementById("spot");
    const asking = doc.getElementById("ask");
    const fine = doc.getElementById("fine");
    const melt = doc.getElementById("melt");
    const ratio = doc.getElementById("ratio");
    const over = doc.getElementById("over");
    if (!weight || !karat || !spot || !asking || !fine || !melt || !ratio || !over) {
      return false;
    }

    const acknowledgement = doc.getElementById("root-scenario-ack");
    function run() {
      const result = (!acknowledgement || acknowledgement.checked) ? calculate(weight.value, karat.value, spot.value, asking.value, unit ? unit.value : "g") : calculate(null, null, null, null);
      fine.textContent = result.fineGoldGrams === null ? EMPTY : result.fineGoldGrams.toFixed(3) + " g";
      melt.textContent = money(result.meltUsd);
      ratio.textContent = result.askingToMeltRatio === null ? EMPTY : result.askingToMeltRatio.toFixed(2) + "×";
      over.textContent = money(result.askingMinusMeltUsd);
    }

    [weight, unit, karat, spot, asking].filter(Boolean).forEach(function (element) {
      element.addEventListener("input", run);
      element.addEventListener("change", run);
    });
    if (acknowledgement) acknowledgement.addEventListener("change", run);
    run();
    return true;
  }

  return {
    GRAMS_PER_TROY_OUNCE: GRAMS_PER_TROY_OUNCE,
    calculate: calculate,
    bindCalculator: bindCalculator,
    money: money
  };
});
