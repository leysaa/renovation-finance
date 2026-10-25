/** Shared category colors (pie chart + transaction list icons). */
window.CATEGORY_COLORS = {
  I: "#00ff88",
  M: "#ffaa00",
  S: "#ff2bd6",
  T: "#b45cff",
  O: "#00e5ff",
};

window.categoryColor = function (code) {
  return window.CATEGORY_COLORS[code] || "#00e5ff";
};
