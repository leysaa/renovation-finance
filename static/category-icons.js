/** Category icons (Labour SVG — sync with ios/_labour_icon.svg.html). */
(function () {
  var BOOTSTRAP = {
    I: "bi-arrow-down-circle",
    M: "bi-box-seam",
    T: "bi-tools",
    O: "bi-three-dots",
  };

  var LABOUR_SVG =
    '<svg class="ios-cat-svg ios-cat-svg-labour" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M11.25 5.25V3h1.5v2.25"/>' +
    '<path d="M6.5 11.25c0-3.75 2.45-6.25 5.5-6.25s5.5 2.5 5.5 6.25"/>' +
    '<path d="M4.75 11.25h14.5"/>' +
    '<path d="M10.25 12.25v2.5a1.75 1.75 0 0 0 3.5 0v-2.5"/>' +
    '<path d="M5.75 18.5c2.1-1.4 4.35-1.4 6.25 0 1.9 1.4 4.15 1.4 6.25 0"/>' +
    '<path d="M9.35 18.5V14l-1.35-1.1"/>' +
    '<path d="M14.65 18.5V14l1.35-1.1"/>' +
    '<rect x="9.85" y="14.35" width="4.3" height="3.85" rx="0.65"/>' +
    "</svg>";

  function inner(code) {
    if (code === "S") return LABOUR_SVG;
    var bi = BOOTSTRAP[code] || "bi-receipt";
    return '<i class="bi ' + bi + '"></i>';
  }

  window.categoryIconInner = inner;
  window.categoryIconHtml = function (code) {
    return (
      '<span class="ios-list-icon ios-cat-icon" data-code="' +
      code +
      '">' +
      inner(code) +
      "</span>"
    );
  };
})();
