"""
Evaluate annotation agreement and compute confusion/per-class metrics.
Produces a small markdown report `data/validation_report.md`.
"""
import csv
from pathlib import Path
from collections import Counter

import sklearn.metrics as skm

BASE = Path(__file__).resolve().parent.parent
ANN = BASE / 'data' / 'validation_sample_annotations.csv'
REPORT = BASE / 'data' / 'validation_report.md'

if not ANN.exists():
    print(f'Missing annotation file: {ANN} (run prepare_validation.py and annotate first)')
    raise SystemExit(1)

true = []
pred = []
ids = []
with ANN.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        gold = r.get('gold_label','').strip()
        if not gold:
            continue
        weak = r.get('weak_label','').strip()
        true.append(gold)
        pred.append(weak)
        ids.append(r.get('comment_id',''))

labels = sorted(list(set(true) | set(pred)))
report_lines = []
report_lines.append('# Validation Report\n')
report_lines.append(f'Total annotated rows: {len(true)}\n')

if len(true) == 0:
    report_lines.append('No gold labels found in annotations. Please fill `gold_label`.')
else:
    cm = skm.confusion_matrix(true, pred, labels=labels)
    pr = skm.precision_recall_fscore_support(true, pred, labels=labels, zero_division=0)
    acc = skm.accuracy_score(true, pred)
    report_lines.append(f'Accuracy: {acc:.3f}\n')
    report_lines.append('## Per-label precision/recall/f1\n')
    report_lines.append('|label|precision|recall|f1|support|')
    report_lines.append('|---|---:|---:|---:|---:|')
    for i,l in enumerate(labels):
        report_lines.append(f'|{l}|{pr[0][i]:.3f}|{pr[1][i]:.3f}|{pr[2][i]:.3f}|{pr[3][i]}|')
    report_lines.append('\n## Confusion matrix\n')
    report_lines.append("```\n" + str(cm) + "\n```\n")

REPORT.write_text('\n'.join(report_lines), encoding='utf-8')
print(f'Wrote report to {REPORT}')
