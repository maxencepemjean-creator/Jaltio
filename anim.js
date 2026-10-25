/* Animations du site vitrine Jaltio : apparitions au défilement, en-tête qui se pose, FAQ fluide.
   Sans effet si l'appareil demande moins de mouvement (le contenu reste visible). */
(function () {
  var d = document.documentElement;
  var calme = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!calme && "IntersectionObserver" in window) d.classList.add("js");

  function pret(fn) { if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn); }
  pret(function () {
    /* En-tête collant : ombre légère dès qu'on a défilé */
    var top = document.querySelector("header.top");
    if (top && !top.parentNode.classList.contains("top-wrap")) {
      var w = document.createElement("div"); w.className = "top-wrap";
      top.parentNode.insertBefore(w, top); w.appendChild(top);
      var maj = function () { w.classList.toggle("scrolled", window.scrollY > 8); };
      window.addEventListener("scroll", maj, { passive: true }); maj();
    }

    /* Apparitions au défilement (groupes : léger décalage entre éléments voisins) */
    if (d.classList.contains("js")) {
      var groupes = ["main h1", "main .lead", ".kicker", "main h2", ".hero .cta-row", ".hero .reassure", ".duo-wrap",
        ".steps3 > li", ".feats > .feat-c", ".honest > *", ".price-card", ".demo-win", ".plans > .plan", ".legal-line", ".already",
        ".faq details", ".contact-grid > *", ".topics > li", ".tag", "main > .wrap > .card", ".doc > p", ".doc > ul", ".doc > .table-wrap"];
      var vus = new Set();
      groupes.forEach(function (sel) {
        document.querySelectorAll(sel).forEach(function (el) {
          if (vus.has(el) || el.closest(".lecture")) return; vus.add(el);
          var i = 0, p = el.previousElementSibling;
          while (p && i < 6) { if (vus.has(p)) i++; p = p.previousElementSibling; }
          el.style.setProperty("--d", (i * 70) + "ms");
          el.classList.add("rv");
        });
      });
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("vu"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
      vus.forEach(function (el) { io.observe(el); });
      /* Filet de sécurité : rien ne reste caché (impression, onglet en arrière-plan…) */
      window.addEventListener("beforeprint", function () { vus.forEach(function (el) { el.classList.add("vu"); }); });
    }

    /* FAQ : ouverture et fermeture en douceur */
    if (!calme && Element.prototype.animate) {
      document.querySelectorAll(".faq details").forEach(function (det) {
        var s = det.querySelector("summary"), c = det.querySelector("summary + *");
        if (!s || !c) return;
        s.addEventListener("click", function (ev) {
          ev.preventDefault();
          if (det.dataset.anim) return; det.dataset.anim = "1";
          if (!det.open) {
            det.open = true;
            var h = c.scrollHeight;
            c.animate([{ height: "0px", opacity: 0 }, { height: h + "px", opacity: 1 }], { duration: 260, easing: "cubic-bezier(.2,.7,.2,1)" })
              .onfinish = function () { delete det.dataset.anim; };
          } else {
            var h2 = c.scrollHeight;
            c.animate([{ height: h2 + "px", opacity: 1 }, { height: "0px", opacity: 0 }], { duration: 200, easing: "ease-in" })
              .onfinish = function () { det.open = false; delete det.dataset.anim; };
          }
        });
      });
    }
  });
})();
