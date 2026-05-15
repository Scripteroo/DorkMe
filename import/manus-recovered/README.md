# Manus Recovery Files

Recovered source data from the original Manus.AI build of DorkMe.
Extracted 2026-05-14 after discovering the live /tools route was returning 500.

Files:
- dorkme_extracted_tools_records.json — 1,456 structured tool entries with category, name, URL, and metadata. Primary source for the v2 tools.json migration.
- dorkme_extracted_tools_records.csv — same data, human-readable
- dorkme_extracted_urls.csv — 2,432 raw URLs from the Manus scrape. Triage confirmed 99.96% are sub-pages of domains already in records.json (see TRIAGE_SUMMARY.md) — contributes no novel tools.
- SUMMARY.md — Manus extraction report
- TRIAGE_SUMMARY.md — bucket counts from the supplemental-URL triage

Reference only — not deployed.
