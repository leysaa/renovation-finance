(function () {
  try {
    if (localStorage.getItem("rf-night-mode") === "1") {
      document.documentElement.setAttribute("data-theme", "dark");
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", "#1c1c1e");
    }
  } catch (_err) {
    /* ignore */
  }
})();
