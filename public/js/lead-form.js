// Lead forms: every <form data-lead-form> on the site posts straight from the
// visitor's browser to the GHL inbound webhook ("ENDPOINT - website-forms" in
// Lincoln's sub-account). There is no server hop. The webhook URL is not in
// this file: server.js serves it from the GHL_WEBHOOK_URL Railway variable as
// /js/lead-config.js, which sets window.LEAD_WEBHOOK_URL before this runs.
//
// On a 2xx from GHL the visitor goes to the form's data-thank-you page, which
// fires the Google Ads lead conversion. Any other outcome keeps them on the
// page with the phone number, so a lead is never silently dropped.
(function () {
  'use strict';

  var ATTR_KEY = 'lead_attr';
  var ATTR_MAX_AGE = 90 * 24 * 60 * 60 * 1000;   // Google's gclid window
  var AD_KEYS = ['gclid', 'gbraid', 'wbraid', 'fbclid'];
  var ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    .concat(AD_KEYS);

  // Attribution: the latest ad-tagged (or UTM-tagged) landing replaces the
  // stored set; untagged visits keep it. Never first-touch-forever.
  function attribution() {
    var stored = null;
    try { stored = JSON.parse(localStorage.getItem(ATTR_KEY) || 'null'); } catch (e) {}
    if (stored && Date.now() - (stored._t || 0) > ATTR_MAX_AGE) stored = null;
    var q = new URLSearchParams(location.search);
    var tagged = ATTR_KEYS.some(function (k) { return q.get(k); });
    if (tagged || !stored) {
      stored = { _t: Date.now(), landing_page: location.href.split('#')[0], referrer: document.referrer || '' };
      ATTR_KEYS.forEach(function (k) { stored[k] = q.get(k) || ''; });
      try { localStorage.setItem(ATTR_KEY, JSON.stringify(stored)); } catch (e) {}
    }
    return stored;
  }
  var attr = attribution();

  var forms = document.querySelectorAll('form[data-lead-form]');
  if (!forms.length) return;

  function digits(s) { return String(s || '').replace(/\D/g, ''); }

  function toE164(raw) {
    var d = digits(raw);
    if (d.length === 10) return '+1' + d;
    if (d.length === 11 && d[0] === '1') return '+' + d;
    return '';
  }

  // (909) 780-0887 as the visitor types.
  function formatPhone(raw) {
    var d = digits(raw);
    if (d.length === 11 && d[0] === '1') d = d.slice(1);
    d = d.slice(0, 10);
    if (d.length < 4) return d;
    if (d.length < 7) return '(' + d.slice(0, 3) + ') ' + d.slice(3);
    return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
  }

  function uuid() {
    return window.crypto && crypto.randomUUID ? crypto.randomUUID()
      : String(Date.now()) + Math.random().toString(16).slice(2);
  }

  function push(event, extra) {
    window.dataLayer = window.dataLayer || [];
    var o = { event: event };
    for (var k in extra) o[k] = extra[k];
    window.dataLayer.push(o);
  }

  function setError(field, msg) {
    var wrap = field.closest('.field');
    var err = wrap && wrap.querySelector('.field-error');
    if (msg) {
      field.setAttribute('aria-invalid', 'true');
      if (err) { err.textContent = msg; err.hidden = false; }
    } else {
      field.removeAttribute('aria-invalid');
      if (err) { err.textContent = ''; err.hidden = true; }
    }
  }

  function validate(form) {
    var first = null;
    form.querySelectorAll('input, select, textarea').forEach(function (f) {
      if (!f.closest('.field')) return;
      var v = (f.value || '').trim();
      var msg = '';
      if (f.required && !v) msg = 'Please fill in this field.';
      else if (f.name === 'phone' && v && !toE164(v)) msg = 'Please enter a 10-digit phone number.';
      else if (f.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = 'Please enter a valid email address.';
      else if (f.name === 'postal_code' && v && !/^\d{5}$/.test(v)) msg = 'Please enter a 5-digit ZIP code.';
      setError(f, msg);
      if (msg && !first) first = f;
    });
    if (first) first.focus();
    return !first;
  }

  function payload(form, eventId) {
    var fd = new FormData(form);
    var data = {};
    fd.forEach(function (v, k) {
      if (k === 'company_website') return;            // honeypot
      data[k] = typeof v === 'string' ? v.trim() : v;
    });
    data.phone = toE164(data.phone);
    data.full_name = [data.first_name, data.last_name].filter(Boolean).join(' ');
    data.sms_consent = form.querySelector('[name="sms_consent"]:checked') ? 'yes' : 'no';
    data.source = 'Website';
    data.form_name = location.pathname.replace(/^\/+|\/+$/g, '') || 'home';
    data.form_id = form.id || '';
    data.page_url = location.href.split('#')[0];
    data.submitted_at = new Date().toISOString();
    data.event_id = eventId;
    ATTR_KEYS.concat(['landing_page', 'referrer']).forEach(function (k) { data[k] = attr[k] || ''; });
    return data;
  }

  forms.forEach(function (form) {
    var status = form.querySelector('[data-form-status]');
    var btn = form.querySelector('[type="submit"]');
    var phoneText = form.getAttribute('data-phone') || '';
    var busy = false;
    var started = false;

    form.setAttribute('novalidate', '');

    form.addEventListener('input', function (e) {
      if (!started) { started = true; push('form_start', { form_id: form.id }); }
      if (e.target.name === 'phone') e.target.value = formatPhone(e.target.value);
      if (e.target.getAttribute('aria-invalid')) setError(e.target, '');
    });

    function say(msg) {
      status.textContent = msg;
      status.hidden = false;
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return;
      status.hidden = true;
      if (!validate(form)) return;

      var hp = form.querySelector('[name="company_website"]');
      if (hp && hp.value) { location.href = form.getAttribute('data-thank-you') || '/thank-you'; return; }

      var url = window.LEAD_WEBHOOK_URL;
      if (!url) {
        console.error('Lead form: GHL_WEBHOOK_URL is not set on the server.');
        say("We couldn't send your request. Please call us at " + phoneText + '.');
        return;
      }

      var eventId = uuid();
      var data = payload(form, eventId);
      busy = true;
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Sending…';

      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        if (!r.ok) throw new Error('GHL responded ' + r.status);
        push('generate_lead', { form_id: form.id, event_id: eventId });
        try { sessionStorage.setItem('lead_first_name', data.first_name || ''); } catch (err) {}
        location.href = form.getAttribute('data-thank-you') || '/thank-you';
      }).catch(function (err) {
        console.error('Lead form:', err);
        busy = false;
        btn.disabled = false;
        btn.textContent = label;
        say("We couldn't send your request. Please try again or call us at " + phoneText + '.');
      });
    });
  });
})();
