(function () {
  function iconHtml(code) {
    if (window.categoryIconHtml) return window.categoryIconHtml(code);
    return (
      '<span class="ios-list-icon ios-cat-icon" data-code="' +
      code +
      '"><i class="bi bi-receipt"></i></span>'
    );
  }

  document.querySelectorAll("[data-picker]").forEach(function (root) {
    var select = root.querySelector(".ios-category-picker-native");
    var trigger = root.querySelector(".ios-category-picker-trigger");
    var menu = root.querySelector(".ios-category-picker-menu");
    var valueEl = root.querySelector('[data-role="value"]');
    if (!select || !trigger || !menu || !valueEl) return;

    function optionLabel(opt) {
      return opt.querySelector(".ios-category-picker-option-text").innerHTML;
    }

    function setOpen(open) {
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
      menu.hidden = !open;
      root.classList.toggle("is-open", open);
    }

    function syncFromSelect() {
      var code = select.value;
      var opt = menu.querySelector('[data-value="' + code + '"]');
      if (!opt) return;

      menu.querySelectorAll('[role="option"]').forEach(function (li) {
        var on = li.getAttribute("data-value") === code;
        li.classList.toggle("is-selected", on);
        li.setAttribute("aria-selected", on ? "true" : "false");
      });

      valueEl.innerHTML =
        iconHtml(code) +
        '<span class="ios-category-picker-text">' +
        optionLabel(opt) +
        "</span>";
    }

    trigger.addEventListener("click", function () {
      setOpen(menu.hidden);
    });

    menu.querySelectorAll('[role="option"]').forEach(function (li) {
      li.addEventListener("click", function () {
        select.value = li.getAttribute("data-value");
        syncFromSelect();
        setOpen(false);
      });
    });

    document.addEventListener("click", function (e) {
      if (!root.contains(e.target)) setOpen(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });

    syncFromSelect();
  });
})();
