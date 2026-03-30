"""
Prepare stratified validation annotations: read validation_sample_stratified.csv and produce
validation_sample_annotations.csv pre-filled with ids, comment_id, text, weak_label columns.
"""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IN = BASE / 'data' / 'validation_sample_stratified.csv'
OUT = BASE / 'data' / 'validation_sample_annotations.csv'

if not IN.exists():
    print(f'Missing input: {IN}')
    raise SystemExit(1)

rows = []
with IN.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, r in enumerate(reader, start=1):
        rows.append({'id': i, 'comment_id': r.get('comment_id',''), 'text': r.get('text',''), 'weak_label': r.get('label','')})

fieldnames = ['id','comment_id','text','weak_label','gold_label','agrees_with_weak_label','annotator_notes']
with OUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow({**r, 'gold_label':'', 'agrees_with_weak_label':'', 'annotator_notes':''})

print(f'Wrote {OUT} ({len(rows)} rows)')
