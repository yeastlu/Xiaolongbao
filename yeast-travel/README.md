# Yeast Travel

English-first, fixed-route China itinerary planner for Shanghai, Hangzhou, Suzhou and Jingdezhen.

## Current state

This repository is a **research-preview build**, not the public commercial release.

- 4 city pages
- 12 day modules
- 37 researched stops
- 12 fixed 1–3 day plan pages
- 4 practical China guides
- optional Amap overview with complete text fallback
- Netlify waitlist and internal route-interest forms
- Shanghai Side Quest shown as `Coming soon`, with no purchase action

All route and city pages currently use `RESEARCHED / DESK_CHECKED_BETA`. They are marked `noindex` until the required field tests are complete.

## Run locally

```sh
npm install
npm run dev
```

Build verification:

```sh
npm run build
```

The build validates exactly four cities, three modules per city, at least 36 stops, unique identifiers, required fallbacks and valid source/map URLs.

## Environment

Copy `.env.example` to `.env`. The site works without Amap or analytics values. Never commit secret values; configure production variables in Netlify.

## Netlify

Create a Netlify site with `yeast-travel/` as its base directory. The included `netlify.toml` builds `dist/`, applies security headers and lets Netlify detect both static forms.

Before launch, enable Forms in Netlify and submit one real test for:

- `side-quest-waitlist`
- `route-interest`

Then configure form notifications and verify that no contact details appear in analytics.

## Publication rule

Do not change a route to `PUBLISHED` until its weekday, weekend, rain fallback, English navigation and mobile Amap checks are recorded. Do not publish a paid offer until the fulfiller, qualification, cancellation rule, data transfer and tracking method are confirmed.
