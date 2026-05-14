# DorkMe.com Site Findings

The homepage at `https://dorkme.com/` loads as **DorkMe — Public Web Discovery Console**. It presents a static-first, privacy-oriented public-web discovery console with a search-card generator, dork block builder, and ethics guardrails. The visible copy states that searches stay local in the browser and only open external search engines when the user clicks.

Key homepage claims and content observed:

| Item | Observed detail |
|---|---|
| Title | DorkMe — Public Web Discovery Console |
| Hero | Find your digital footprint. |
| Privacy claims | No stored searches; transparent queries; ethical workflows |
| Main builder | Search-card generator with username, real name, domain, and custom modes |
| Workbench | Query blocks for `site`, `filetype`, `inurl`, exact phrase, and exclusion |
| Directory claim | Dedicated `/tools` route with 1,456 exact OSINT links across 78 categories |
| Ethics section | Self-check first, no scraping in v0, explicit actions, attribution |
| Assets observed | `/media/dorkme-logo.png` and three CloudFront `.webp` images |

The `/tools` route at `https://dorkme.com/tools` returned **500 Internal Server Error** during testing. The error page listed contact `webmaster@dorkme.reignsnap.io`, suggesting the deployed route was misconfigured or missing server-side support at capture time. The uploaded repository now includes `tools/index.html`, copied from the SPA entry point, so static hosts that serve directory indexes can load the client-side tools route at `/tools/`.

The homepage HTML was saved by the browser to `/home/ubuntu/browser_html/dorkme_com_page_1778793563610.html` for analysis.
