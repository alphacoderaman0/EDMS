/* eDiary UI: reveal, theme toggle, toast messages */
(function () {
  function reveal() {
    var nodes = document.querySelectorAll(".nf-reveal");
    if (!nodes.length) return;
    if (!("IntersectionObserver" in window)) {
      nodes.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    nodes.forEach(function (el) { io.observe(el); });
  }

  function applyTheme(theme) {
    var t = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("ediary-theme", t); } catch (e) {}
  }

  function initTheme() {
    var btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") || "dark";
      applyTheme(cur === "dark" ? "light" : "dark");
    });
  }

  function ensureHost() {
    var host = document.getElementById("nfToastHost");
    if (host) return host;
    host = document.createElement("div");
    host.id = "nfToastHost";
    host.className = "nf-toast-host";
    host.setAttribute("aria-live", "polite");
    document.body.appendChild(host);
    return host;
  }

  /**
   * nfToast(message, type, options)
   * type: 'success' | 'error' | 'info'
   * options: { title, redirect, delay }
   */
  window.nfToast = function (message, type, options) {
    options = options || {};
    type = type || "info";
    var delay = typeof options.delay === "number" ? options.delay : 2800;
    var titles = { success: "Success", error: "Error", info: "Notice" };
    var icons = { success: "bx-check-circle", error: "bx-error-circle", info: "bx-info-circle" };
    var host = ensureHost();
    var el = document.createElement("div");
    el.className = "nf-toast nf-toast-" + type;
    el.innerHTML =
      '<div class="nf-toast-icon"><i class="bx ' + (icons[type] || icons.info) + '"></i></div>' +
      '<div class="nf-toast-body">' +
        '<p class="nf-toast-title">' + (options.title || titles[type] || "Notice") + "</p>" +
        '<p class="nf-toast-msg"></p>' +
      "</div>" +
      '<button type="button" class="nf-toast-close" aria-label="Close">&times;</button>';
    el.querySelector(".nf-toast-msg").textContent = message || "";
    host.appendChild(el);

    function dismiss(thenRedirect) {
      if (el.classList.contains("is-out")) return;
      el.classList.add("is-out");
      setTimeout(function () {
        if (el.parentNode) el.parentNode.removeChild(el);
        if (thenRedirect && options.redirect) window.location = options.redirect;
      }, 240);
    }

    el.querySelector(".nf-toast-close").addEventListener("click", function () {
      dismiss(true);
    });

    setTimeout(function () { dismiss(true); }, Math.max(delay, options.redirect ? 1100 : 800));
    return el;
  };

  function boot() {
    reveal();
    initTheme();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
