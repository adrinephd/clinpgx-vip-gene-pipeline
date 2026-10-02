# ClinPGx clinical-annotation inputs


This code extract and extratified clinical annotations from ClinPGx and saparates by pediatric and non-pediatric evidence levels. Level 1 is the higher level of evidence, usually associated with dosing guidelines.

Visit ClinPGx and download the summary annotation files of that date and log the version.
https://www.clinpgx.org/downloads

Place the downloaded ClinPGx TSV exports for this analysis in this directory
Expected naming:

```text
GENE_pediatric-clinicalAnnotations-all-data.tsv
GENE_nonPediatric-clinicalAnnotations-all-data.tsv
```

Required columns: `Level`, `Variant`, `Gene`, `Drugs`, `Phenotype Categories`, and `Phenotype`.
