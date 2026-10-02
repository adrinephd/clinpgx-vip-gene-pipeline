# ClinPGx clinical-annotation inputs

Place the downloaded ClinPGx TSV exports for this analysis in this directory.

Expected naming:

```text
GENE_pediatric-clinicalAnnotations-all-data.tsv
GENE_nonPediatric-clinicalAnnotations-all-data.tsv
```

Required columns: `Level`, `Variant`, `Gene`, `Drugs`, `Phenotype Categories`, and `Phenotype`.

The TSV files themselves are gitignored because they are source-data snapshots rather than code.
