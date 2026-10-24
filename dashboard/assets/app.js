/* GOLD2 Companion Dashboard — Client-Side Table Filter Enhancer
 * Progressive enhancement only; all rows are rendered statically in HTML.
 * Zero innerHTML / outerHTML / eval sinks.
 */
(function () {
  "use strict";
  if (typeof document === "undefined") {
    return;
  }

  var qInput = document.getElementById("filter-query");
  var karatSelect = document.getElementById("filter-karat");
  var solidSelect = document.getElementById("filter-solid");
  var weightSelect = document.getElementById("filter-weight");
  var countEl = document.getElementById("filter-count");
  var rows = document.querySelectorAll("tr[data-ring-row]");

  if (!rows.length || (!qInput && !karatSelect && !solidSelect && !weightSelect)) {
    return;
  }

  function applyFilters() {
    var q = qInput ? qInput.value.trim().toLowerCase() : "";
    var karat = karatSelect ? karatSelect.value : "all";
    var solid = solidSelect ? solidSelect.value : "all";
    var weight = weightSelect ? weightSelect.value : "all";
    var shown = 0;

    for (var i = 0; i < rows.length; i += 1) {
      var tr = rows[i];
      var matchQ = !q || (tr.textContent || "").toLowerCase().indexOf(q) !== -1;
      var matchK = karat === "all" || tr.getAttribute("data-karat") === karat;
      var matchS = solid === "all" || tr.getAttribute("data-solid") === solid;
      var matchW = weight === "all" || tr.getAttribute("data-has-weight") === weight;
      var visible = matchQ && matchK && matchS && matchW;
      tr.hidden = !visible;
      if (visible) {
        shown += 1;
      }
    }
    if (countEl) {
      countEl.textContent = "Showing " + String(shown) + " of " + String(rows.length) + " source-linked listings";
    }
  }

  [qInput, karatSelect, solidSelect, weightSelect].forEach(function (el) {
    if (el) {
      el.addEventListener("input", applyFilters);
      el.addEventListener("change", applyFilters);
    }
  });
  applyFilters();
})();
