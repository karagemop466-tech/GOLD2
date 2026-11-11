#!/usr/bin/env python3
"""Guard against assigning the market retrieval date to stale product evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def read(path):
    return json.loads((ROOT / path).read_text())

for path, key in [('dashboard/data/rings.json', 'rings'), ('dashboard/data/retailers.json', 'retailers')]:
    obj = read(path)
    dates = [row['capture_date'] for row in obj[key] if row.get('capture_date')]
    assert dates and obj['retrieved_at'] == max(dates), (path, obj['retrieved_at'], max(dates))
gold = read('data/gold-price.json')
assert read('dashboard/data/gold-reference.json')['retrieved_at'] == gold['retrieved_at']
assert gold['quote_date'] is None
print('PASS product and seller dates remain independent from WGC observation; unknown quote date stays blank')
