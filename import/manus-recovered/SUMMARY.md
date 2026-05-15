# DorkMe Static Bundle Data Extraction Summary
This report summarizes what could be recovered from the compiled DorkMe static JavaScript bundle currently present in `/home/ubuntu/dorkme/assets/index-D23FajOp.js`.
## Source Code Status
The repository inventory found only static deployment artifacts: `index.html`, `assets/`, `media/`, `external-assets/`, Apache fallback files, and deployment documentation. It did not find editable application source directories such as `src/`, `client/`, `components/`, `pages/`, or TypeScript/React source files.
## Extracted Data Counts
| Metric | Count |
|---|---:|
| Candidate structured records extracted from bundle | 2428 |
| Unique non-framework URLs extracted from bundle | 2432 |
| Structured records with names | 2428 |
| Unique named tools | 2338 |
| Unique URLs in structured records | 2428 |
| Duplicate URLs across structured records | 0 |

## Category Counts
| Category | Records | Example Name | Example URL |
|---|---:|---|---|
| General OSINT | 788 | 10 Minute OSINT Tips | https://osintcurio.us/10-minute-tips |
| Public Records | 598 | Alabama | http://sos.alabama.gov/government-records/ucc-records?area=UCC |
| Maps & Geolocation | 130 | AIS Ships Map | https://www.shipfinder.com/Monitor/Index |
| Social Media | 114 | Advanced LinkedIn Search Guide | https://nubela.co/blog/how-to-find-anyone-with-an-advanced-linkedin-people-search |
| Dark Web | 88 | Ahmia — Search Tor Hidden Services | https://ahmia.fi |
| Phone & Email | 69 | 10 Minute Mail | https://10minutemail.com |
| Business & Corporate | 55 | Advanced Registry Search | https://lobbycanada.gc.ca/app/secure/ocl/lrs/do/advSrch?lang=eng |
| Image & Video | 52 | Airbus – Satellite Imagery Services | https://www.airbus-ds.com |
| Telegram OSINT | 51 | Awesome Telegram OSINT | https://github.com/ItIsMeCall911/Awesome-Telegram-OSINT |
| Domain & IP | 47 | BeVigil | https://bevigil.com/search |
| Threat Intel | 45 | Abuse.ch – Malware Bazaar | https://bazaar.abuse.ch |
| People Search | 43 | ABA Generator | https://www.fakenamegenerator.com/aba-validator.php |
| Resources & Training | 39 | Al Jazeera OSINT Handbook | https://institute.aljazeera.net/ |
| AI Tools | 38 | 10Web | https://10web.io/ |
| Transportation | 35 | Car/Vehicle Model Recognition Online | https://carmodel.toolpie.com |
| Search Engines | 32 | 2lingual | http://2lingual.com/ |
| Breach & Credential | 31 | 8chan Leak | https://bloopbase.keybase.pub/LEFTHOOK/8chan/index.html |
| Archives & Caches | 22 | Archive-it.org | https://archive-it.org |
| Government & Legal | 22 | ChromeCacheView | https://www.nirsoft.net/utils/chrome_cache_view.html |
| Browser & OPSEC | 17 | 0bin | https://0bin.net/ |
| Username & Account | 16 | AnalyzeID | https://analyzeid.com/ |
| Code & Repositories | 14 | Amass | https://github.com/owasp-amass/amass |
| Documents & Data | 14 | AidData | http://aiddata.org/ |
| Email | 13 | Apollo | https://www.apollo.io/ |
| Visualization & DataViz | 12 | Canva | https://www.canva.com/ |
| Financial | 9 | Bitcoin Explorer | https://blockchair.com/bitcoin |
| Phone & Telecom | 9 | Bellingcat Phone Number Checker | https://github.com/bellingcat/telegram-phone-number-checker |
| Fact-Check & Verification | 7 | AllTop | http://alltop.com/ |
| Web & SEO | 7 | Ahrefs | https://ahrefs.com/ |
| Communications | 6 | Free Fax | https://faxzero.com |
| Metadata & EXIF | 5 | Exif.regex.info | http://exif.regex.info/ |

## Output Files
| File | Purpose |
|---|---|
| `extracted_tools_records.csv` | Structured CSV with `name`, `url`, `category`, and `description` fields recovered from bundled objects. |
| `extracted_tools_records.json` | Same structured data in JSON, including raw object chunks useful for further forensic cleanup. |
| `extracted_urls.csv` | Plain URL inventory from the bundle after filtering React/framework documentation URLs. |
| `extracted_urls.json` | Same plain URL inventory in JSON. |

## Important Caveat
This is a reverse extraction from minified compiled output, not original source data. It is suitable as a recovery/export list, but it is not a substitute for the original editable React/TypeScript source or a clean source-of-truth data file such as `osintTools.ts`.
