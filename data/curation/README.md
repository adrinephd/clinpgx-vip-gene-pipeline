# Optional Template Version 1 curation files

Template Version 1 can incorporate project-review information that is not derived directly from ClinPGx or CPIC.

Two optional CSV inputs are supported.

## allele_curation_april_2026.csv

One row per `Gene + Variant`.

Supported fields include:

- `Gene`
- `Variant`
- `Previously validated`
- `Included in custom veridose panel`
- `HGVS Representation override`

The HGVS override field is optional and can be used when a project-specific representation should be retained in the final workbook.

## filtered_alleles_selection_april_2026.csv

Defines the allele subset included in the `Filtered alleles` worksheet.

Supported fields include:

- `Gene`
- `Variant`
- `Previously validated`
- `DNALabs Orthogonal Panel`

## Public repository behavior

Blank template files are tracked in GitHub so the expected schema is visible. Filled project-specific curation files are ignored by Git.
