(function () {
  const canvas = document.getElementById("overviewBalanceChart");
  if (!canvas) return;

  const fmt = new Intl.NumberFormat(undefined, { style: "currency", currency: "EUR" });
  const theme = window.rfChartTheme ? window.rfChartTheme.theme() : { tick: "#000", grid: "rgba(0,0,0,0.1)" };

  fetch("/overview/balance-by-project.json", { credentials: "same-origin" })
    .then(function (r) {
      if (!r.ok) throw new Error("Failed to load chart data");
      return r.json();
    })
    .then(function (data) {
      if (!data.labels.length) {
        canvas.parentElement.innerHTML =
          '<p class="ios-chart-empty"><i class="bi bi-bar-chart"></i> No projects yet</p>';
        return;
      }

      const chart = new Chart(canvas, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              data: data.values,
              backgroundColor: data.colors,
              borderRadius: 6,
              maxBarThickness: 48,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  return fmt.format(ctx.parsed.y);
                },
              },
            },
          },
          scales: {
            x: {
              ticks: {
                maxRotation: 45,
                minRotation: 0,
                font: { size: 11 },
                color: theme.tick,
              },
              grid: { display: false },
            },
            y: {
              ticks: {
                callback: function (v) {
                  return fmt.format(v);
                },
                font: { size: 11 },
                color: theme.tick,
              },
              grid: { color: theme.grid },
            },
          },
          onClick: function (_evt, elements) {
            if (!elements.length) return;
            const idx = elements[0].index;
            const id = data.project_ids[idx];
            if (id) window.location.href = "/projects/" + id + "/charts";
          },
        },
      });

      if (window.rfChartTheme) window.rfChartTheme.watch(chart);

      window.addEventListener("resize", function () {
        chart.resize();
      });
    })
    .catch(function () {
      canvas.parentElement.innerHTML =
        '<p class="ios-chart-empty text-danger">Could not load chart</p>';
    });
})();
