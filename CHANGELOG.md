# Cleanup summary

## From the original April 2026 scripts to this repository

- Preserved the five-step workflow and April 2026 output filenames.
- Centralized the 34-gene ClinPGx ID list and CPIC allele-functionality URLs in `config.py`.
- Normalized ClinPGx headers by prefix so the real `CPIC FunctionLearn more about allele functions` header is captured correctly.
- Removed the empty duplicate `CPIC FUNCTION from ClinPGx` column in newly generated files while retaining backward compatibility.
- Replaced fixed Selenium sleeps with explicit readiness/content waits where practical.
- Deduplicated rendered haplotype links before visiting haplotype pages.
- Made input/output paths configurable.
- Added explicit input validation for clinical-annotation TSVs.
- Preserved missing merge keys with pandas nullable strings.
- Added HTTP timeouts and basic workbook-layout validation for CPIC downloads.
- Added explicit local CSV support for project-specific validation/panel flags and narrowly scoped field overrides.
- Added support for the curated `Filtered alleles` and `Legend` sheets.
- Reproduced the shortened GRCh38 boilerplate and supports the VKORC1 HGVS correction through local curation data.
- Documented genes absent from supplied outputs and 24 MT-RNR1 rows present only in the manually curated final workbook.
- Added gitignore rules for generated outputs, source TSVs, and project-specific curation.
