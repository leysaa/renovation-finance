(function () {
  var DEFAULT_WIDTH = 88;
  var openRow = null;

  function actionWidth(row) {
    var w = parseInt(row.getAttribute("data-swipe-width"), 10);
    return w > 0 ? w : DEFAULT_WIDTH;
  }

  function openThreshold(row) {
    return Math.round(actionWidth(row) / 2);
  }

  function setOffset(row, px, animate) {
    var panel = row.querySelector(".ios-swipe-row-panel");
    if (!panel) return;
    panel.style.transition = animate ? "transform 0.22s ease" : "none";
    panel.style.transform = px ? "translateX(" + px + "px)" : "";
    row.classList.toggle("is-open", px >= openThreshold(row));
    if (px >= openThreshold(row)) {
      if (openRow && openRow !== row) closeRow(openRow, true);
      openRow = row;
      row.querySelector(".ios-swipe-row-actions")?.setAttribute("aria-hidden", "false");
    } else if (openRow === row) {
      openRow = null;
      row.querySelector(".ios-swipe-row-actions")?.setAttribute("aria-hidden", "true");
    }
  }

  function closeRow(row, animate) {
    setOffset(row, 0, animate);
  }

  function openRowFully(row) {
    setOffset(row, actionWidth(row), true);
  }

  document.querySelectorAll("[data-swipe-row]").forEach(function (row) {
    var panel = row.querySelector(".ios-swipe-row-panel");
    if (!panel) return;

    var startX = 0;
    var startY = 0;
    var startOffset = 0;
    var tracking = false;
    var horizontal = false;
    var dragged = false;

    function currentOffset() {
      return row.classList.contains("is-open") ? actionWidth(row) : 0;
    }

    function onPointerDown(e) {
      if (e.target.closest(".ios-swipe-row-actions")) return;
      if (e.pointerType === "mouse" && e.button !== 0) return;
      tracking = true;
      horizontal = false;
      dragged = false;
      startX = e.clientX;
      startY = e.clientY;
      startOffset = currentOffset();
      panel.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
      if (!tracking) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      if (!horizontal && Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) {
        horizontal = true;
        row.classList.add("is-dragging");
      }
      if (!horizontal) return;
      dragged = true;
      e.preventDefault();
      var max = actionWidth(row);
      var next = Math.max(0, Math.min(max, startOffset + dx));
      setOffset(row, next, false);
    }

    function onPointerUp(e) {
      if (!tracking) return;
      tracking = false;
      row.classList.remove("is-dragging");
      try {
        panel.releasePointerCapture(e.pointerId);
      } catch (_err) {
        /* ignore */
      }
      if (!horizontal) return;
      var dx = e.clientX - startX;
      var max = actionWidth(row);
      var projected = Math.max(0, Math.min(max, startOffset + dx));
      if (projected >= openThreshold(row)) openRowFully(row);
      else closeRow(row, true);
    }

    panel.addEventListener("pointerdown", onPointerDown);
    panel.addEventListener("pointermove", onPointerMove);
    panel.addEventListener("pointerup", onPointerUp);
    panel.addEventListener("pointercancel", onPointerUp);

    panel.addEventListener(
      "click",
      function (e) {
        if (!dragged) return;
        var link = e.target.closest("a");
        if (link) {
          e.preventDefault();
          dragged = false;
        }
      },
      true
    );
  });

  document.addEventListener("click", function (e) {
    if (!openRow) return;
    if (e.target.closest("[data-swipe-row]") === openRow) return;
    closeRow(openRow, true);
  });

  document.querySelectorAll(".ios-swipe-delete-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      var msg = form.getAttribute("data-confirm");
      if (msg && !window.confirm(msg)) e.preventDefault();
    });
  });
})();
