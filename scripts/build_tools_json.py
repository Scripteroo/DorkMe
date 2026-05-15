#!/usr/bin/env python3
"""
Build v1 of data/tools.json from import/manus-recovered/dorkme_extracted_tools_records.json.

Pipeline:
1. Load 2,428 source records
2. Map 31 Manus categories → 14 new buckets
3. Run rule-based reclassifier on "General OSINT" (788 records)
4. Apply per-record split heuristics for "Phone & Email" and "Domain & IP"
5. Generate slug IDs, dedup by normalized URL, emit tools.json
6. Print stats
"""

import json
import re
from collections import Counter
from pathlib import Path

SRC = Path('import/manus-recovered/dorkme_extracted_tools_records.json')
DST = Path('data/tools.json')

# ============================================================================
# Category mapping: 31 Manus categories → 14 new buckets
# ============================================================================
# Special values trigger per-record logic:
#   'SPLIT_PHONE_EMAIL', 'SPLIT_DOMAIN_IP', 'RECLASSIFY'
# Everything else is a direct mapping.

CATEGORY_MAP = {
    'Public Records': 'records',
    'Maps & Geolocation': 'geo',
    'Social Media': 'username',
    'Dark Web': 'leaks',
    'Phone & Email': 'SPLIT_PHONE_EMAIL',
    'Business & Corporate': 'records',
    'Image & Video': 'image',
    'Telegram OSINT': 'username',
    'Domain & IP': 'SPLIT_DOMAIN_IP',
    'Threat Intel': 'general',
    'People Search': 'person',
    'Transportation': 'vehicle',
    'Search Engines': 'dorks',
    'Breach & Credential': 'leaks',
    'Archives & Caches': 'archives',
    'Government & Legal': 'records',
    'Username & Account': 'username',
    'Documents & Data': 'leaks',
    'Email': 'email',
    'Financial': 'records',
    'Phone & Telecom': 'phone',
    'Fact-Check & Verification': 'archives',
    'Web & SEO': 'domain',
    'Metadata & EXIF': 'image',
    # Folded into general (Dan elected "keep everything"):
    'Resources & Training': 'general',
    'AI Tools': 'general',
    'Browser & OPSEC': 'general',
    'Code & Repositories': 'general',
    'Visualization & DataViz': 'general',
    'Communications': 'general',
    # Needs reclassification:
    'General OSINT': 'RECLASSIFY',
}

# ============================================================================
# Input types per bucket — drives the smart-input router
# ============================================================================
INPUT_TYPES = {
    'username': ['username'],
    'person':   ['person', 'phone', 'address'],
    'email':    ['email'],
    'phone':    ['phone'],
    'domain':   ['domain', 'url'],
    'ip':       ['ip', 'domain'],
    'image':    ['image'],
    'geo':      ['address', 'coordinates'],
    'records':  ['person', 'address', 'business'],
    'leaks':    ['email', 'username'],
    'dorks':    [],
    'archives': ['url', 'search'],
    'vehicle':  ['license_plate', 'vin'],
    'general':  [],
}

# ============================================================================
# Rule-based reclassifier (for General OSINT, 788 records)
# ============================================================================
# Patterns checked in order; first match wins. Operates on lowercased name+url.
# More specific patterns first; broader categories last.

RECLASSIFY_RULES = [
    ('vehicle',  re.compile(r'\b(license[\s\-]?plate|\bvin\b|vehicle|carfax|flightaware|flightradar|adsb|marinetraffic|vesselfinder|aircraft|airplane|maritime)\b')),
    ('username', re.compile(r'\b(reddit|teddit|twitter|tweet|twitch|youtube|youtu\.be|instagram|tiktok|telegram|discord|mastodon|snapchat|linkedin|facebook|profile[\s\-]?lookup)\b')),
    ('image',    re.compile(r'\b(image|photo|exif|tineye|reverse[\s\-]?image|fotoforensic|invid|deepfake|sensity|metadata)\b')),
    ('geo',      re.compile(r'\b(geocod|geolocat|\bmap\b|gis|arcgis|satellite|terrain|coordinates|openstreetmap|\bosm\b|geofence|geospatial|sun[\s\-]?calc|shadow)\b')),
    ('leaks',    re.compile(r'\b(breach|leak|pwned|dehash|paste|h8mail|credential|dark[\s\-]?web|\bonion\b|tor[\s\-])\b')),
    ('phone',    re.compile(r'\b(phone|number[\s\-]?lookup|sms|carrier[\s\-]?lookup|truecaller|numlookup|phoneinfoga|caller[\s\-]?id|twilio)\b')),
    ('email',    re.compile(r'\b(email|e-mail|smtp|mail[\s\-]?check|mailtester|verify[\s\-]?email|hunter\.io|epieos|holehe)\b')),
    ('ip',       re.compile(r'\b(shodan|censys|\bip[\s\-]?(lookup|address|range)|geoip|\basn\b|cidr|fofa|zoomeye|binaryedge|abuseipdb|ipinfo|greynoise)\b')),
    ('domain',   re.compile(r'\b(whois|domain|\bdns\b|subdomain|\bseo\b|securitytrails|dnsdumpster|mxtoolbox|builtwith|wappalyzer|certificate[\s\-]?transparency|crt\.sh)\b')),
    ('records',  re.compile(r'\b(court|legal|judicial|government|public[\s\-]?record|voter|deed|\bproperty\b|parcel|business[\s\-]?registry|company[\s\-]?registry|opencorporates|sec\.gov|\bedgar\b|\bpacer\b|civil|criminal|incorporation|jurisdiction|gazette|registrant|licensure|tax)\b')),
    ('dorks',    re.compile(r'\b(dork|google[\s\-]?search|advanced[\s\-]?search|search[\s\-]?operator|google[\s\-]?cse|custom[\s\-]?search)\b')),
    ('archives', re.compile(r'\b(wayback|web[\s\-]?archive|\bcached?\b|archive\.(today|ph|is|org)|\brss\b|fact[\s\-]?check|news[\s\-]?verif)\b')),
    ('person',   re.compile(r'\b(people[\s\-]?search|find[\s\-]?a[\s\-]?person|background[\s\-]?check|spokeo|whitepages|truepeoplesearch|fastpeoplesearch|webmii|\bpipl\b|zabasearch|familytreenow|radaris)\b')),
]

def reclassify(name, url):
    text = f'{name} {url}'.lower()
    for bucket, pattern in RECLASSIFY_RULES:
        if pattern.search(text):
            return bucket
    return 'general'

def split_phone_email(name, url):
    text = f'{name} {url}'.lower()
    if re.search(r'\b(phone|number|sms|call|carrier|dialer)\b', text):
        return 'phone'
    return 'email'

def split_domain_ip(name, url):
    text = f'{name} {url}'.lower()
    if re.search(r'\b(shodan|censys|\bip[\s\-]?(lookup|address)|\basn\b|cidr|fofa|zoomeye|greynoise|abuseipdb|ipinfo)\b', text):
        return 'ip'
    return 'domain'

# ============================================================================
# Slug generator (unique IDs)
# ============================================================================
_slug_used = set()

def make_slug(name):
    base = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not base:
        base = 'tool'
    slug = base
    n = 2
    while slug in _slug_used:
        slug = f'{base}-{n}'
        n += 1
    _slug_used.add(slug)
    return slug

# ============================================================================
# URL normalization (for dedup)
# ============================================================================
def norm_url(u):
    u = u.lower().strip()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^www\.', '', u)
    return u.rstrip('/')

# ============================================================================
# Main pipeline
# ============================================================================
def main():
    records = json.loads(SRC.read_text())
    print(f'Loaded {len(records)} source records.\n')

    reclassify_stats = Counter()
    split_pe_stats = Counter()
    split_di_stats = Counter()

    out = []
    seen_urls = set()
    duplicate_count = 0
    skipped_empty = 0

    for rec in records:
        name = (rec.get('name') or '').strip()
        url = (rec.get('url') or '').strip()
        manus_cat = (rec.get('category') or '').strip()
        raw_chunk = rec.get('raw_chunk') or ''

        if not name or not url:
            skipped_empty += 1
            continue

        n_url = norm_url(url)
        if n_url in seen_urls:
            duplicate_count += 1
            continue
        seen_urls.add(n_url)

        mapped = CATEGORY_MAP.get(manus_cat, 'general')

        if mapped == 'RECLASSIFY':
            bucket = reclassify(name, url)
            reclassify_stats[bucket] += 1
        elif mapped == 'SPLIT_PHONE_EMAIL':
            bucket = split_phone_email(name, url)
            split_pe_stats[bucket] += 1
        elif mapped == 'SPLIT_DOMAIN_IP':
            bucket = split_domain_ip(name, url)
            split_di_stats[bucket] += 1
        else:
            bucket = mapped

        entry = {
            'id': make_slug(name),
            'name': name,
            'category': bucket,
            'inputTypes': INPUT_TYPES.get(bucket, []),
            'url': url,
            'urlTemplate': '',
            'description': '',
            'featured': False,
            'trustLevel': 'medium',
            '_originalCategory': manus_cat,
        }
        m = re.search(r'source:\s*([^\n|;]+)', raw_chunk, re.I)
        if m:
            entry['_source'] = m.group(1).strip()

        out.append(entry)

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f'Output: {len(out)} tools written to {DST}')
    print(f'Duplicates skipped: {duplicate_count}')
    print(f'Empty records skipped: {skipped_empty}\n')

    bucket_counts = Counter(e['category'] for e in out)
    print('=== Final bucket distribution ===')
    for bucket, n in bucket_counts.most_common():
        print(f'{n:>5}  {bucket}')

    print('\n=== Reclassifier results (General OSINT, 788 input) ===')
    total_reclass = sum(reclassify_stats.values())
    classified = total_reclass - reclassify_stats.get('general', 0)
    pct = 100 * classified / total_reclass if total_reclass else 0
    print(f'Resolved into buckets: {classified} ({pct:.1f}%)')
    print(f'Left in general:       {reclassify_stats.get("general", 0)}')
    for bucket, n in reclassify_stats.most_common():
        print(f'  {n:>4}  {bucket}')

    print('\n=== Split heuristics ===')
    print(f'Phone & Email (69 → split):  {dict(split_pe_stats)}')
    print(f'Domain & IP (47 → split):    {dict(split_di_stats)}')

if __name__ == '__main__':
    main()
