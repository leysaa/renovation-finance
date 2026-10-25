(function () {
  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function cssVar(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name);
    v = v ? v.trim() : "";
    return v || fallback;
  }

  function theme() {
    var dark = isDark();
    var labelFallback = dark ? "#ffffff" : "#000000";
    return {
      tick: cssVar("--ios-label", labelFallback),
      grid: cssVar("--ios-separator", "rgba(60, 60, 67, 0.12)"),
      legend: cssVar("--ios-label", labelFallback),
      pieBorder: cssVar("--ios-card", dark ? "#1c1c1e" : "#ffffff"),
    };
  }

  function applyLegendColors(chart) {
    var t = theme();
    var legend = chart.options.plugins && chart.options.plugins.legend;
    if (!legend || !legend.labels) return;

    legend.labels.color = t.legend;
    if (typeof legend.labels.generateLabels === "function") {
      chart.update();
      return;
    }
  }

  function applyToChart(chart) {
    if (!chart || !chart.options) return;
    var t = theme();

    var scales = chart.options.scales;
    if (scales) {
      Object.keys(scales).forEach(function (axis) {
        var scale = scales[axis];
        if (!scale) return;
        if (scale.ticks) scale.ticks.color = t.tick;
        if (scale.grid && scale.grid.display !== false) scale.grid.color = t.grid;
      });
    }

    var legend = chart.options.plugins && chart.options.plugins.legend;
    if (legend && legend.labels) {
      legend.labels.color = t.legend;
    }

    if (chart.config.type === "pie" || chart.config.type === "doughnut") {
      chart.data.datasets.forEach(function (ds) {
        ds.borderColor = t.pieBorder;
      });
    }

    chart.update();
  }

  function watch(chart) {
    applyToChart(chart);
    document.addEventListener("rf-theme-change", function () {
      applyToChart(chart);
    });
  }

  window.rfChartTheme = { theme: theme, applyToChart: applyToChart, watch: watch };
})();
