# Legacy site scrape — lincolnplumbingandrooter.com

Scraped 2026-08-28 ahead of the platform swap. Source platform: WordPress + Divi
(plugins: divi-overlays, wp-fuse, wp-rocket). Everything here exists so the copy,
slugs, and lead capture survive the move.

- One `.md` per page: slug, title tag, meta description, canonical, GHL form ids,
  image originals, then the full linearized page copy (headings preserved as `#`/`##`).
- `raw-html/` — the untouched fetched HTML, in case a Divi module needs re-reading.
- `_index.json` — machine-readable summary of all 11 pages.

## Slugs to retain (trailing slash, exactly as-is)

| slug | title tag | GHL form slots |
|---|---|---|
| /ga-plumbing-services/ | Plumbing Services | hero, final |
| /sewer-lines/ | Sewer Lines | hero, final |
| /ga-tankless-water-heaters/ | tankless-water-heaters | hero, final |
| /ga-testimonials/ | testimonials | — none |
| /ga-water-heater/ | Water Heater | hero, final |
| /ga-about-us/ | about-us | — none |
| /ga-contact/ | contact | contact |
| /drain-cleaning/ | Drain Cleaning | hero, final |
| /ga-garbage-disposal-services/ | garbage-disposal-services | hero, final |
| /hydrojetting/ | Hydrojetting | hero, final |
| /ga-leak-detection/ | leak-detection | hero, final |

## The GHL form (one form, reused everywhere)

- Form name: **Meta Form**
- Form id: **dxqfiiA9bB1OLTNaNnRx**
- Embed URL: `https://link.advancedmarketers.co/widget/form/dxqfiiA9bB1OLTNaNnRx`
- Loader script: `https://link.advancedmarketers.co/js/form_embed.js`

Only the `id` / `data-layout-iframe-id` suffix changes per placement
(`-hero`, `-final`, `-contact`) so two embeds on one page don't collide.
Drop-in snippet:

```html
<iframe
  src="https://link.advancedmarketers.co/widget/form/dxqfiiA9bB1OLTNaNnRx"
  style="width:100%;height:600px;border:none"
  id="inline-dxqfiiA9bB1OLTNaNnRx-hero"
  data-layout="{'id':'INLINE'}"
  data-trigger-type="alwaysShow"
  data-activation-type="alwaysActivated"
  data-deactivation-type="neverDeactivate"
  data-form-name="Meta Form"
  data-height="600"
  data-layout-iframe-id="inline-dxqfiiA9bB1OLTNaNnRx-hero"
  data-form-id="dxqfiiA9bB1OLTNaNnRx"
  title="Get A Free Quote">
</iframe>
<script src="https://link.advancedmarketers.co/js/form_embed.js"></script>
```

## Tracking on the legacy pages (carry over or consciously drop)

- GTM `GTM-NB7XCVVG`
- GA4 `G-XL9X7ZMQ2J`
- Google Ads `AW-16721660937`

## Brand facts confirmed on every page

- Phone: (909) 765-0236 — "Open 24 Hours, 7 Days a Week"
- Email: lincolnplumbingrooter@gmail.com
- Address: 738 S Waterman Ave. #C45, San Bernardino, CA 92408
- Tagline: "Your Pipes, Our Priority"
- Cities: San Bernardino, Riverside, Rancho Cucamonga, Fontana, Redlands, Highland
- Financing partner: GoodLeap (soft credit check) — has its own section on every page
- Exit-intent popup: "Don't Leave Without Your Discount!" / "Get up to $200 off"

## Notes

- Legacy nav is much deeper than our repo's (Plumbing Services / Water Heaters /
  Drains and Sewers / Commercial Plumbing sub-menus, plus Specials & Service
  Locations). Those child URLs weren't in scope for this scrape.
- Page imagery is chrome only (logo, GoodLeap, popup) — the LP bodies are
  emoji/type-driven, so our own photo set in `public/images/` covers it.
- `/ga-about-us/` and `/ga-testimonials/` had no form embed on the legacy page.
