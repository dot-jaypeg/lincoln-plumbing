# Email campaigns

Four customer email blasts for Lincoln Plumbing & Rooter, each with its own offer page on the site.

| # | Email file | Offer page | Campaign (utm_campaign) |
|---|---|---|---|
| 1 | `01-holiday-proof-your-plumbing.html` | `/holiday-plumbing-prep` | `holiday-prep` |
| 2 | `02-how-old-is-your-water-heater.html` | `/water-heater-checkup` | `water-heater-age` |
| 3 | `03-annual-plumbing-checkup.html` | `/plumbing-checkup` | `annual-checkup` |
| 4 | `04-refer-a-neighbor.html` | `/refer-a-neighbor` | `refer-a-neighbor` |

**Don't hand-edit the HTML.** It's generated: change `tools/build-emails.py`, then run `python3 tools/build-emails.py`. The offer pages come from `content/new-lps.json` and are built with `python3 tools/build-legacy-lps.py <slug>`.

## How they're built

- 600px table layout with inline styles, a VML button fallback for Outlook, and a single-column stack under 620px wide. Each file is about 28 KB, well under Gmail's 102 KB clipping limit.
- No merge tags and no personalization, so they work in any email platform.
- Images load from `https://www.lincolnplumbingandrooter.com/images/email/`. **They won't load until this branch is merged and deployed.**
- Every call link uses the main line, 909-780-0887 (`tel:+19097800887`). Every button goes to that email's offer page, tagged `utm_source=email`.
- The offer pages use the paid-LP template, but they show the main line and load the organic GTM container (`EMAIL_SLUGS` in `tools/build-legacy-lps.py`). They are `noindex` and use the same GHL Meta Form as the other LPs.

## Subject lines and preheaders

Each file's `<head>` comment lists the same options.

**1. Holiday-proof your plumbing**
- Before the guests arrive: is your plumbing ready?
- Holiday-proof your plumbing (before the rush)
- Full house this year? Your drains will feel it
- Preheader: Book a pre-holiday drain clean or water heater flush before our schedule fills up.

**2. How old is your water heater?**
- How old is your water heater?
- 8+ years old? Your water heater needs a look
- The 60-second check that could save you a cold shower
- Preheader: 8+ years old? It's time for a look. Book a free water heater inspection.

**3. Annual plumbing checkup**
- It's been a while since we've seen you
- A thank-you for coming back: loyalty savings inside
- When did someone last check your plumbing?
- Preheader: Returning customers get loyalty savings on a whole-home plumbing inspection.

**4. Refer a neighbor**
- Thank you. Here's $25 for you and a neighbor.
- Know someone who needs a plumber? You both get $25
- A thank-you from Lincoln Plumbing & Rooter
- Preheader: Thank you for being a customer. Send a neighbor our way and you both get $25 off.

## Before any send

- [ ] Replace `[UNSUBSCRIBE_LINK]` in each footer with the sending platform's unsubscribe tag. This is required by CAN-SPAM.
- [ ] Merge and deploy this branch so the images and offer pages are live.
- [ ] Send a test to Gmail, Outlook and an iPhone.

## Confirm with the client

The brief gave the concepts but not every number. The copy works around the missing ones, so nothing invented is shown as a fact:

- **Holiday:** No price or book-by date was given, so the copy says "book before the holidays." Get the price and a firm date, then add them to the offer box and the page hero.
- **Water heater:** The free inspection comes from the brief. No replacement discount amount was given, so none is advertised.
- **Checkup:** No loyalty discount amount was given, so the copy says "loyalty savings." Get the amount (e.g. 15%) and put it in the offer headline.
- **Referral:** $25 for them and $25 for you comes from the brief. Confirm how the client tracks referrals and applies the credit.
- **Google review link:** It's currently the site's `share.google` link. Swap it for the Google Business Profile "write a review" link if the client has one (`GOOGLE_REVIEW` in the generator).
