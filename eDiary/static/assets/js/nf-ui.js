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

  function initLoadingForms() {
    document.querySelectorAll("form.nf-loading-form").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        if (e.defaultPrevented) return;
        if (form.dataset.nfLoading === "1") {
          e.preventDefault();
          return;
        }
        var btn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (!btn) return;
        form.dataset.nfLoading = "1";
        btn.classList.add("is-loading");
        btn.setAttribute("disabled", "disabled");
        if (!btn.querySelector(".nf-spinner")) {
          var spin = document.createElement("span");
          spin.className = "nf-spinner";
          spin.setAttribute("aria-hidden", "true");
          btn.appendChild(spin);
        }
      });
    });
  }

  function initLandingNav() {
    var nav = document.getElementById("landingNav");
    if (!nav) return;
    var toggle = document.getElementById("landingNavToggle");
    var links = document.getElementById("landingNavLinks");
    var anchors = nav.querySelectorAll('a[href^="#"]');

    function onScroll() {
      if (window.scrollY > 24) nav.classList.add("is-scrolled");
      else nav.classList.remove("is-scrolled");
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    if (toggle && links) {
      toggle.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.innerHTML = open ? '<i class="bx bx-x"></i>' : '<i class="bx bx-menu"></i>';
      });
      links.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () {
          nav.classList.remove("is-open");
          toggle.setAttribute("aria-expanded", "false");
          toggle.innerHTML = '<i class="bx bx-menu"></i>';
        });
      });
    }

    var sections = [];
    anchors.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) sections.push({ id: id, el: el, link: a });
    });
    if (sections.length && "IntersectionObserver" in window) {
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          anchors.forEach(function (a) { a.classList.remove("is-active"); });
          var hit = sections.find(function (s) { return s.el === entry.target; });
          if (hit) hit.link.classList.add("is-active");
        });
      }, { rootMargin: "-35% 0px -55% 0px", threshold: 0 });
      sections.forEach(function (s) { spy.observe(s.el); });
    }
  }

  function initCounters() {
    var nodes = document.querySelectorAll(".nf-count[data-count]");
    if (!nodes.length) return;

    function animate(el) {
      var raw = el.getAttribute("data-count");
      if (raw === "∞") {
        el.textContent = "∞";
        return;
      }
      var target = parseInt(raw, 10) || 0;
      var suffix = el.getAttribute("data-suffix") || "";
      var start = performance.now();
      var dur = 1100;
      function frame(now) {
        var t = Math.min(1, (now - start) / dur);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (t < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    if (!("IntersectionObserver" in window)) {
      nodes.forEach(animate);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        animate(entry.target);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.4 });
    nodes.forEach(function (el) { io.observe(el); });
  }

  function boot() {
    reveal();
    initTheme();
    initLoadingForms();
    initLandingNav();
    initCounters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
