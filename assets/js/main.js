/* HEIDEHOF – kleine Helfer, ohne Abhängigkeiten */
(function () {
  "use strict";
  var doc = document.documentElement;
  var body = document.body;
  var reduziert = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Header: fest werden beim Scrollen, mobile Leiste einblenden */
  var header = document.querySelector(".site-header");
  var mobilCta = document.querySelector(".mobil-cta");
  function aufScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("ist-fest", y > 40);
    if (mobilCta) mobilCta.classList.toggle("sichtbar", y > 520);
  }
  window.addEventListener("scroll", aufScroll, { passive: true });
  aufScroll();

  /* Mobile Navigation */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var offen = body.classList.toggle("nav-offen");
      toggle.setAttribute("aria-expanded", offen ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("nav-offen")) {
        body.classList.remove("nav-offen");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
    document.querySelectorAll(".hauptnav a").forEach(function (a) {
      a.addEventListener("click", function () { body.classList.remove("nav-offen"); toggle.setAttribute("aria-expanded", "false"); });
    });
  }

  /* Scroll-Reveal */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reduziert) {
    var io = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("sichtbar"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("sichtbar"); });
  }

  /* Zähler */
  var zaehler = document.querySelectorAll("[data-zahl]");
  function zaehle(el) {
    var ziel = parseFloat(el.getAttribute("data-zahl"));
    var nach = el.getAttribute("data-nach") || "";
    if (reduziert) { el.textContent = ziel.toLocaleString("de-DE") + nach; return; }
    var start = null, dauer = 1800;
    function schritt(t) {
      if (!start) start = t;
      var p = Math.min((t - start) / dauer, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(ziel * e).toLocaleString("de-DE") + nach;
      if (p < 1) requestAnimationFrame(schritt);
    }
    requestAnimationFrame(schritt);
  }
  if ("IntersectionObserver" in window) {
    var zio = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) { if (e.isIntersecting) { zaehle(e.target); zio.unobserve(e.target); } });
    }, { threshold: 0.6 });
    zaehler.forEach(function (el) { zio.observe(el); });
  }

  /* Parallax für Bild-Bänder */
  var baender = document.querySelectorAll(".band-bild");
  if (baender.length && !reduziert) {
    var tick = false;
    function parallax() {
      var vh = window.innerHeight;
      baender.forEach(function (b) {
        var r = b.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var fortschritt = (r.top + r.height / 2 - vh / 2) / vh;
        b.style.transform = "translate3d(0," + (fortschritt * -90).toFixed(1) + "px,0)";
      });
      tick = false;
    }
    window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(parallax); } }, { passive: true });
    parallax();
  }

  /* Öffnungszeiten: „Jetzt geöffnet“ + heutigen Tag markieren (Zeitzone Berlin) */
  var zeiten = {
    0: [["09:30", "21:00"]],
    1: [],
    2: [["11:30", "14:30"], ["17:00", "22:00"]],
    3: [["11:30", "14:30"], ["17:00", "22:00"]],
    4: [["11:30", "14:30"], ["17:00", "22:00"]],
    5: [["11:30", "14:30"], ["17:00", "22:00"]],
    6: [["11:30", "22:30"]]
  };
  function jetztBerlin() {
    try {
      var teile = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Berlin", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
      var tage = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
      var o = {};
      teile.forEach(function (t) { o[t.type] = t.value; });
      return { tag: tage[o.weekday], min: (parseInt(o.hour, 10) % 24) * 60 + parseInt(o.minute, 10) };
    } catch (e) {
      var d = new Date();
      return { tag: d.getDay(), min: d.getHours() * 60 + d.getMinutes() };
    }
  }
  function inMin(s) { var p = s.split(":"); return +p[0] * 60 + +p[1]; }
  var jetzt = jetztBerlin();
  document.querySelectorAll("[data-offen-status]").forEach(function (el) {
    var heute = zeiten[jetzt.tag] || [];
    var offen = false, naechste = null;
    heute.forEach(function (z) {
      if (jetzt.min >= inMin(z[0]) && jetzt.min < inMin(z[1])) offen = z;
      else if (!naechste && jetzt.min < inMin(z[0])) naechste = z;
    });
    var text = el.querySelector("span");
    if (offen) { el.classList.add("offen"); text.textContent = "Jetzt geöffnet · bis " + offen[1] + " Uhr"; }
    else if (naechste) { text.textContent = "Heute ab " + naechste[0] + " Uhr geöffnet"; }
    else if (jetzt.tag === 1) { text.textContent = "Montag ist Ruhetag · ab Dienstag wieder da"; }
    else { text.textContent = "Gerade geschlossen · bis bald"; }
  });
  document.querySelectorAll(".zeiten tr[data-tage]").forEach(function (tr) {
    if (tr.getAttribute("data-tage").split(",").indexOf(String(jetzt.tag)) > -1) tr.classList.add("heute");
  });

  /* Speisekarte: aktiven Abschnitt markieren */
  var kartenLinks = document.querySelectorAll(".karten-nav a");
  if (kartenLinks.length && "IntersectionObserver" in window) {
    var kio = new IntersectionObserver(function (eintraege) {
      eintraege.forEach(function (e) {
        if (e.isIntersecting) {
          kartenLinks.forEach(function (a) { a.classList.toggle("aktiv", a.getAttribute("href") === "#" + e.target.id); });
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    document.querySelectorAll(".karten-abschnitt").forEach(function (s) { kio.observe(s); });
  }

  /* Formulare (Demo: es werden keine Daten übertragen) */
  document.querySelectorAll("form[data-demo-formular]").forEach(function (form) {
    var datum = form.querySelector('input[type="date"]');
    if (datum) {
      var h = new Date();
      datum.min = h.getFullYear() + "-" + String(h.getMonth() + 1).padStart(2, "0") + "-" + String(h.getDate()).padStart(2, "0");
      datum.addEventListener("change", function () {
        var d = new Date(datum.value + "T12:00:00");
        datum.setCustomValidity(d.getDay() === 1 ? "Montags ist Ruhetag – such dir gern einen anderen Tag aus." : "");
      });
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var ziel = document.getElementById(form.getAttribute("data-demo-formular"));
      var name = form.querySelector('[name="name"]');
      if (ziel) {
        var n = ziel.querySelector("[data-name]");
        if (n && name) n.textContent = name.value.split(" ")[0];
        form.hidden = true;
        ziel.classList.add("sichtbar");
        ziel.setAttribute("tabindex", "-1");
        ziel.focus();
      }
    });
  });

  /* Jahr im Footer */
  document.querySelectorAll("[data-jahr]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
