#!/usr/bin/env python3
"""
LLM-based reclassification pass for tools.json.

Sends every record currently in the 'general' bucket to Claude Haiku 4.5,
asks it to pick a category from the fixed 14-bucket taxonomy, updates
the category and inputTypes in place.

Requires: ANTHROPIC_API_KEY env var, anthropic package installed.
"""

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from anthropic import Anthropic

TOOLS_JSON = Path('data/tools.json')
BATCH_SIZE = 25
MODEL = 'claude-haiku-4-5-20251001'

BUCKETS = ['username', 'person', 'email', 'phone', 'domain', 'ip', 'image',
           'geo', 'records', 'leaks', 'dorks', 'archives', 'vehicle', 'general']

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

SYSTEM_PROMPT = """You are categorizing OSINT (Open Source Intelligence) tools into a fixed 14-bucket taxonomy. For each tool you're given, you respond with EXACTLY ONE bucket from this list:

- username: tools that look up usernames or social-media profiles across platforms
- person: people search, background checks, finding individuals by name
- email: email lookup, verification, reverse email search
- phone: phone number lookup, carrier info, SMS or calling utilities
- domain: WHOIS, DNS, subdomain enumeration, SEO and website intelligence
- ip: IP geolocation, IP reputation, network infrastructure scanning (Shodan, Censys, etc.)
- image: reverse image search, photo forensics, EXIF analysis, video verification
- geo: maps, geolocation, satellite imagery, address-to-coordinates conversion
- records: public records, court records, business registries, government records, financial filings, voter records
- leaks: data breach lookups, dark web monitoring, paste sites, credential dumps, threat intelligence
- dorks: search engine operators, Google dorking, advanced search builders
- archives: web archives (Wayback Machine), cached pages, news verification, fact-checking
- vehicle: license plates, VIN lookups, flight tracking, maritime tracking
- general: tools that genuinely don't fit any other bucket above. Use sparingly — most tools fit somewhere.

You will receive a numbered list of tools (name + URL). Respond ONLY with a JSON array of objects, one per input tool, in the same order. Each object has exactly one field, "category", whose value is one of the bucket strings above (lowercase, exactly as written).

Do not include any other text, explanation, prose, or markdown code fences. Just the JSON array."""

def classify_batch(client, tools):
    tool_list = '\n'.join(
        f'{i+1}. {t["name"]} — {t["url"]}'
        for i, t in enumerate(tools)
    )
    msg = f"Classify these tools:\n\n{tool_list}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": msg}],
    )

    text = response.content[0].text.strip()
    text = text.replace('```json', '').replace('```', '').strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        print(f'  WARN: parse failed ({e}); defaulting batch to general')
        return ['general'] * len(tools)

    if not isinstance(result, list) or len(result) != len(tools):
        print(f'  WARN: length mismatch ({len(result)} vs {len(tools)}); defaulting batch')
        return ['general'] * len(tools)

    cats = []
    for item in result:
        cat = item.get('category', 'general') if isinstance(item, dict) else 'general'
        if cat not in BUCKETS:
            cat = 'general'
        cats.append(cat)
    return cats

def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY not set.')
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    tools = json.loads(TOOLS_JSON.read_text())
    print(f'Loaded {len(tools)} tools.\n')

    indices = [i for i, t in enumerate(tools) if t.get('category') == 'general']
    print(f'Found {len(indices)} records in `general` to reclassify.\n')
    if not indices:
        print('Nothing to do.')
        return

    n_batches = (len(indices) + BATCH_SIZE - 1) // BATCH_SIZE
    reclass = Counter()

    for batch_i in range(n_batches):
        s = batch_i * BATCH_SIZE
        e = min(s + BATCH_SIZE, len(indices))
        batch_idx = indices[s:e]
        batch_tools = [tools[i] for i in batch_idx]

        print(f'Batch {batch_i+1}/{n_batches} ({len(batch_tools)} tools)...', end=' ', flush=True)
        try:
            cats = classify_batch(client, batch_tools)
        except Exception as ex:
            print(f'ERROR: {ex}')
            cats = ['general'] * len(batch_tools)

        for idx, new_cat in zip(batch_idx, cats):
            tools[idx]['category'] = new_cat
            tools[idx]['inputTypes'] = INPUT_TYPES.get(new_cat, [])
            reclass[new_cat] += 1

        per_batch = Counter(cats)
        summary = ' '.join(f'{c}:{n}' for c, n in per_batch.most_common())
        print(f'→ {summary}')

        time.sleep(0.2)

    TOOLS_JSON.write_text(json.dumps(tools, indent=2, ensure_ascii=False))

    print(f'\n=== Reclassification results ({len(indices)} input) ===')
    resolved = sum(n for c, n in reclass.items() if c != 'general')
    pct = 100 * resolved / len(indices) if indices else 0
    print(f'Resolved into specific buckets: {resolved} ({pct:.1f}%)')
    print(f'Left in general:                {reclass.get("general", 0)}\n')
    for c, n in reclass.most_common():
        print(f'  {n:>4}  {c}')

    final = Counter(t['category'] for t in tools)
    print(f'\n=== Final bucket distribution (all {len(tools)} tools) ===')
    for c, n in final.most_common():
        print(f'{n:>5}  {c}')

if __name__ == '__main__':
    main()
