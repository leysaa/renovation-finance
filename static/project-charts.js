(function () {
  const root = document.getElementById("project-charts");
  if (!root) return;

  const projectId = root.dataset.projectId;
  const canvas = document.getElementById("chartExpenses");
  const totalsList = document.getElementById("chartExpenseTotals");
  if (!canvas) return;

  const fmt = new Intl.NumberFormat(undefined, { style: "currency", currency: "EUR" });
  const colorFor = window.categoryColor || function () {
    return "#8e8e93";
  };
  const chartTheme = window.rfChartTheme ? window.rfChartTheme.theme() : { legend: "#000", pieBorder: "#fff" };

  fetch("/projects/" + projectId + "/charts/expenses-by-category.json", {
    credentials: "same-origin",
  })
    .then(function (r) {
      if (!r.ok) throw new Error("fetch failed");
      return r.json();
    })
    .then(function (data) {
      if (!data.labels.length) {
        canvas.parentElement.innerHTML =
          '<p class="ios-chart-empty"><i class="bi bi-pie-chart"></i> No expenses yet</p>';
        return;
      }

      const rawLabels = data.labels.slice();
      const codes = data.codes || [];
      const values = data.values;
      const sliceColors = codes.map(function (code) {
        return colorFor(code);
      });
      const grandTotal = values.reduce(function (a, b) {
        return a + b;
      }, 0);

      if (totalsList) {
        totalsList.hidden = false;
        totalsList.innerHTML = values
          .map(function (amount, i) {
            const pct = grandTotal ? Math.round((amount / grandTotal) * 100) : 0;
            const swatch = sliceColors[i] || colorFor(codes[i]);
            return (
              '<li class="ios-list-item">' +
              '<div class="ios-list-link pe-3">' +
              '<span class="ios-chart-swatch" style="background:' +
              swatch +
              '"></span>' +
              '<div class="ios-list-body">' +
              '<div class="ios-list-title">' +
              rawLabels[i] +
              "</div>" +
              '<div class="ios-list-meta">' +
              pct +
              "%</div>" +
              "</div>" +
              '<div class="ios-list-trailing">' +
              '<span class="ios-list-amount ios-cat-amount" data-code="' +
              (codes[i] || "") +
              '">' +
              fmt.format(amount) +
              "</span>" +
              "</div>" +
              "</div></li>"
            );
          })
          .join("");
        if (grandTotal > 0) {
          totalsList.innerHTML +=
            '<li class="ios-list-item ios-chart-grand-total">' +
            '<div class="ios-list-link pe-3">' +
            '<div class="ios-list-body">' +
            '<div class="ios-list-title fw-semibold">Total expenses</div>' +
            "</div>" +
            '<div class="ios-list-trailing">' +
            '<span class="ios-list-amount negative fw-semibold">' +
            fmt.format(grandTotal) +
            "</span>" +
            "</div></div></li>";
        }
      }

      const chart = new Chart(canvas, {
        type: "pie",
        data: {
          labels: rawLabels,
          datasets: [
            {
              data: values,
              backgroundColor: sliceColors,
              borderWidth: 2,
              borderColor: chartTheme.pieBorder,
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
                  const pct = grandTotal ? Math.round((ctx.parsed / grandTotal) * 100) : 0;
                  return fmt.format(ctx.parsed) + " (" + pct + "%)";
                },
              },
            },
          },
        },
      });

      if (window.rfChartTheme) window.rfChartTheme.watch(chart);
    })
    .catch(function () {
      canvas.parentElement.innerHTML =
        '<p class="ios-chart-empty text-danger">Could not load chart</p>';
    });
})();
