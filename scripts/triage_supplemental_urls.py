import json, re, csv
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

base = Path('import/manus-recovered')

# 1. Build set of known domains from records.json
with open(base / 'dorkme_extracted_tools_records.json') as f:
    data = json.load(f)

def find_urls(obj):
    if isinstance(obj, dict):
        for v in obj.values(): yield from find_urls(v)
    elif isinstance(obj, list):
        for item in obj: yield from find_urls(item)
    elif isinstance(obj, str) and re.match(r'^https?://', obj):
        yield obj

def domain_of(url):
    try:
        d = urlparse(url).netloc.lower()
        return re.sub(r'^www\.', '', d)
    except Exception:
        return None

known_domains = {d for d in (domain_of(u) for u in find_urls(data)) if d}

# 2. Junk patterns
junk_domain_patterns = [
    r'cloudfront\.net$', r'amazonaws\.com$', r'cdn\.jsdelivr\.net$',
    r'^(i\.)?imgur\.com$', r'prnt\.sc$', r'bit\.ly$', r'tinyurl\.com$',
    r'^t\.co$', r'goo\.gl$', r'ow\.ly$', r'^\d+\.\d+\.\d+\.\d+$',
    r'akamaihd\.net$', r'fastly\.net$', r'imgix\.net$',
]
junk_re = re.compile('|'.join(junk_domain_patterns))

resource_ext = re.compile(r'\.(pdf|jpg|jpeg|png|gif|webp|svg|mp4|mp3|wav|zip|doc|docx|xls|xlsx|ppt|pptx|tar|gz)(\?|$)', re.I)

# 3. Read urls.csv and bucket
candidates, subpages, junk = [], [], []
with open(base / 'dorkme_extracted_urls.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        for cell in row:
            cell = cell.strip()
            if not re.match(r'^https?://', cell):
                continue
            d = domain_of(cell)
            if not d:
                junk.append(cell); continue
            if d in known_domains:
                subpages.append(cell)
            elif junk_re.search(d) or resource_ext.search(cell):
                junk.append(cell)
            else:
                candidates.append(cell)

# 4. Write bucket files
def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow([r])

write_csv(base / 'urls_supplemental_candidates.csv', candidates)
write_csv(base / 'urls_supplemental_subpages.csv', subpages)
write_csv(base / 'urls_supplemental_junk.csv', junk)

# 5. Summary report
candidate_domains = Counter(domain_of(u) for u in candidates).most_common(20)
total = len(candidates) + len(subpages) + len(junk)

summary = f"""# Supplemental URL Triage Summary

Source: import/manus-recovered/dorkme_extracted_urls.csv ({total} URLs total)

## Buckets
- **Candidates** (novel tool URLs, need enrichment): {len(candidates)}
- **Subpages** (domain already in records.json): {len(subpages)}
- **Junk** (CDN, image hosts, file URLs, IP literals, etc.): {len(junk)}

## Top 20 candidate domains by frequency
"""
for d, c in candidate_domains:
    summary += f"- {d}: {c}\n"

(base / 'TRIAGE_SUMMARY.md').write_text(summary)
print(summary)
