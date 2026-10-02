# Local curation files

The cleaned pipeline makes supported edits explicit via optional local CSV files:

- `allele_curation_april_2026.csv` — validation/custom-panel flags and narrowly scoped manual field overrides.
- `filtered_alleles_selection_april_2026.csv` — the exact Gene/Variant selection used for the curated `Filtered alleles` sheet, plus the filtered-sheet orthogonal-panel flag.

Both are gitignored by default because they may contain project-specific validation/panel information. Template files are tracked so the required schema is clear.
