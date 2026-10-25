(function () {
  var STORAGE_KEY = "rf-night-mode";

  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function setDark(on) {
    if (on) document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
    try {
      localStorage.setItem(STORAGE_KEY, on ? "1" : "0");
    } catch (_err) {
      /* ignore */
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", on ? "#1c1c1e" : "#007aff");
    document.dispatchEvent(new CustomEvent("rf-theme-change", { detail: { dark: on } }));
  }

  function syncToggle(toggle) {
    if (!toggle) return;
    toggle.checked = isDark();
    toggle.setAttribute("aria-checked", toggle.checked ? "true" : "false");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("night-mode-toggle");
    syncToggle(toggle);
    if (toggle) {
      toggle.addEventListener("change", function () {
        setDark(toggle.checked);
        toggle.setAttribute("aria-checked", toggle.checked ? "true" : "false");
      });
    }
  });

  window.rfAppearance = { isDark: isDark, setDark: setDark };
})();
