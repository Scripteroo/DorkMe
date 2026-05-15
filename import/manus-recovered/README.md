# Manus Recovery Files

Recovered source data from the original Manus.AI build of DorkMe.
Extracted 2026-05-14 after discovering the live /tools route was returning 500.

Files:
- dorkme_extracted_tools_records.json — 2,428 structured tool entries with category, name, URL, and metadata. All `description` fields are empty (Manus didn't capture them). The `raw_chunk` field preserves the original source-string with provenance tags ("Ghostint Tools", "OSINT Cabal", "einitial24"). Primary source for the v2 tools.json migration.
- dorkme_extracted_tools_records.csv — same data, human-readable
- dorkme_extracted_urls.csv — 2,432 raw URLs. Triage confirmed 99.96% redundant with records.json domains (see TRIAGE_SUMMARY.md). Not used.
- SUMMARY.md — Manus extraction report
- TRIAGE_SUMMARY.md — bucket counts from the supplemental-URL triage

Reference only — not deployed.
