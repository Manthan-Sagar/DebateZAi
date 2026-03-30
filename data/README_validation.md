Validation sample and annotation workflow

Files created:
- `validation_sample_stratified.csv`: stratified 500-row sample (all minority labels + random majority rows)
- `validation_sample_annotations_template.csv`: empty template for manual annotation
- `validation_sample_instructions.txt`: short labeling instructions
- `validation_sample_annotations.csv`: will be created by `scripts/prepare_validation.py` and filled by annotators

Workflow:
1. Run `python scripts/prepare_validation.py` to create `validation_sample_annotations.csv` pre-filled with ids and weak labels.
2. Annotators fill `gold_label` and `agrees_with_weak_label` and save the file.
3. Run `python scripts/evaluate_annotations.py` to generate `data/validation_report.md` with agreement/metrics.

Notes:
- The repo's `requirements.txt` lists `scikit-learn` and `pandas` if you need to run the scripts.
- If you want, I can run the evaluation after you produce `validation_sample_annotations.csv` (or I can run it now if you prefer to annotate inline here).
