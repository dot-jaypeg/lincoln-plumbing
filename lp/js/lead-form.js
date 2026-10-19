// Lead forms post straight from the browser to the GoHighLevel inbound webhook.
// No server hop: this site is static, GHL is the only backend.
(function () {
  "use strict";

  // TODO: paste the GHL "ENDPOINT - website-forms" inbound webhook URL here before launch.
  var GHL_WEBHOOK_URL = "";
  var PHONE = "909-765-0236";
  var THANK_YOU_URL = "/thank-you/";
  var ATTR_KEY = "lincoln_lp_attr";
  var UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"];

  // First-touch attribution: captured once per browser, never overwritten.
  function captureFirstTouch() {
    var s = {};
    try { s = JSON.parse(localStorage.getItem(ATTR_KEY) || "{}"); } catch (e) {}
    if (s._captured) return s;
    var q = new URLSearchParams(location.search);
    var a = { _captured: new Date().toISOString(), landing_page: location.pathname + location.search, referrer: document.referrer || "" };
    UTM_KEYS.forEach(function (k) { a[k] = q.get(k) || ""; });
    try { localStorage.setItem(ATTR_KEY, JSON.stringify(a)); } catch (e) {}
    return a;
  }
  var attribution = captureFirstTouch();
  // a gclid on this visit always wins, so a returning ad click is still credited
  var current = new URLSearchParams(location.search);

  function toKey(n) { return String(n).trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, ""); }
  function toE164(raw) {
    var d = String(raw || "").replace(/\D/g, "");
    if (d.length === 10) return "+1" + d;
    if (d.length === 11 && d[0] === "1") return "+" + d;
    return String(raw || "").trim();
  }
  function newEventId() { return window.crypto && crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2); }

  function buildLeadPayload(form) {
    var data = {};
    new FormData(form).forEach(function (v, k) {
      if (k === "website") return; // honeypot
      data[k === "Source" ? "form_source" : toKey(k)] = typeof v === "string" ? v.trim() : v;
    });
    var parts = (data.name || "").split(/\s+/).filter(Boolean);
    data.full_name = data.name || "";
    data.first_name = parts.shift() || "";
    data.last_name = parts.join(" ");
    delete data.name;
    data.phone = toE164(data.phone);
    data.source = "Website";
    data.form_name = location.pathname.replace(/\/+$/, "").replace(/^\/+/, "") || "home";
    data.form_id = form.id || "";
    data.page_url = location.href.split("#")[0];
    data.submitted_at = new Date().toISOString();
    return data;
  }

  function fillHidden(form) {
    UTM_KEYS.concat(["referrer", "landing_page"]).forEach(function (k) {
      var el = form.querySelector('input[name="' + k + '"]');
      if (el) el.value = current.get(k) || attribution[k] || "";
    });
    var eid = form.querySelector('input[name="event_id"]');
    if (eid) eid.value = newEventId();
  }

  function setError(field, msg) {
    var wrap = field.closest(".field");
    if (!wrap) return;
    wrap.classList.toggle("has-error", !!msg);
    var err = wrap.querySelector(".field-error");
    if (!err) { err = document.createElement("span"); err.className = "field-error"; wrap.appendChild(err); }
    err.textContent = msg || "";
    field.setAttribute("aria-invalid", msg ? "true" : "false");
  }

  function validate(form) {
    var first = null;
    form.querySelectorAll("input[required], select[required], textarea[required]").forEach(function (f) {
      var v = (f.value || "").trim(), msg = "";
      if (!v) msg = "Required";
      else if (f.type === "tel" && v.replace(/\D/g, "").length < 10) msg = "Enter a 10-digit phone number";
      else if (f.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = "Enter a valid email";
      setError(f, msg);
      if (msg && !first) first = f;
    });
    form.querySelectorAll('input[type="email"]:not([required])').forEach(function (f) {
      var v = f.value.trim(), msg = v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? "Enter a valid email" : "";
      setError(f, msg);
      if (msg && !first) first = f;
    });
    if (first) first.focus();
    return !first;
  }

  document.querySelectorAll("form[data-contact-form]").forEach(function (form) {
    fillHidden(form);
    form.setAttribute("novalidate", "");
    var status = form.querySelector("[data-form-status]");
    var btn = form.querySelector('[type="submit"]');
    var btnLabel = btn ? btn.textContent : "";
    var busy = false;

    function show(msg, ok) {
      status.hidden = false;
      status.className = "form-status " + (ok ? "is-ok" : "is-err");
      status.textContent = msg;
    }

    form.addEventListener("input", function (e) {
      if (e.target.closest(".field.has-error")) setError(e.target, "");
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (busy) return;
      var hp = form.querySelector('input[name="website"]');
      if (hp && hp.value.trim()) { show("Thank you! Your request has been received.", true); form.reset(); return; }
      if (!validate(form)) return;
      if (!GHL_WEBHOOK_URL) { show("Form isn't connected yet. Please call us at " + PHONE + ".", false); return; }

      busy = true;
      if (btn) { btn.disabled = true; btn.textContent = "Sending..."; }
      var payload = buildLeadPayload(form);
      fetch(GHL_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          // conversion events fire on /thank-you/ from this flag, so the redirect can't cut them off
          try { sessionStorage.setItem("lincoln_lp_lead", JSON.stringify({ event_id: payload.event_id, form_name: payload.form_name })); } catch (e) {}
          location.href = THANK_YOU_URL;
        })
        .catch(function () {
          show("We couldn't send your request. Please call us at " + PHONE + ", we're open 24/7.", false);
          busy = false;
          if (btn) { btn.disabled = false; btn.textContent = btnLabel; }
        });
    });
  });
})();
