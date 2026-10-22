// Shared UI helpers: active nav highlighting + rings table filter.
(function () {
  "use strict";
  // Active nav
  var path = (location.pathname.split("/").pop() || "index.html").split("?")[0];
  document.querySelectorAll("nav.main a").forEach(function (a) {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });
  // Rings table filter (rings.html only)
  var q = document.getElementById("ring-filter");
  var karat = document.getElementById("karat-filter");
  var table = document.getElementById("rings-table");
  if ((q || karat) && table) {
    var apply = function () {
      var text = q ? q.value.trim().toLowerCase() : "";
      var k = karat ? karat.value : "";
      table.querySelectorAll("tbody tr").forEach(function (tr) {
        var hay = tr.textContent.toLowerCase();
        var kk = tr.getAttribute("data-karat") || "";
        var show = (!text || hay.indexOf(text) !== -1) && (!k || kk === k);
        tr.style.display = show ? "" : "none";
      });
    };
    if (q) q.addEventListener("input", apply);
    if (karat) karat.addEventListener("change", apply);
  }
})();
