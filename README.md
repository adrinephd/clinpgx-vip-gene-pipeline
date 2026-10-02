# ClinPGx VIP Gene / Allele Review Pipeline — Template Version 1

This repository contains **Template Version 1** of the Python workflow used to build the ClinPGx/CPIC pharmacogenomics allele review workbook used in this project.

The workflow brings together three types of information:

- **ClinPGx named-allele and haplotype information**
- **ClinPGx clinical annotations**, separated into pediatric and non-pediatric evidence
- **CPIC allele-functionality reference information**

The resulting Excel workbook is designed to support review and selection of pharmacogenomic alleles for a VIP-gene panel.

## Template Version 1 workflow

The workflow is organized into five sequential scripts:

1. **Gene-level ClinPGx extraction**  
   Extracts named alleles, named variants, ClinPGx/CPIC function fields, AMP tier information, and gene-level named-allele descriptions from configured ClinPGx gene pages.

2. **Haplotype-level ClinPGx extraction**  
   Adds haplotype identifiers and detailed haplotype information, including HGVS representation, CPIC and DPWG function/activity fields, and ClinPGx definitions.

3. **ClinPGx clinical annotation compilation**  
   Combines downloaded ClinPGx pediatric and non-pediatric clinical-annotation TSV files. Clinical annotations are organized by ClinPGx evidence level (1, 2, 3, 4, or unknown).

4. **ClinPGx table integration**  
   Combines the named-allele/haplotype information with the clinical-annotation table using `Gene + Variant` as the shared key.

5. **CPIC integration and workbook generation**  
   Adds CPIC allele-functionality information and writes the final Excel workbook used for allele review.

## Final workbook

Template Version 1 produces an Excel workbook with three worksheets.

### 1. All VIP genes

This is the comprehensive allele/variant review table.

The worksheet includes:

**Allele identification and project review**
- Gene
- Variant
- Allele number
- Previously validated
- Included in custom Veridose panel
- AMP Tier

**ClinPGx and CPIC function information**
- CPIC Function
- ClinPGx Function
- Allele
- Activity Score
- Allele Function
- CPIC Strength of Evidence
- References
- Summary

**ClinPGx named-allele / haplotype information**
- Named Alleles Description
- Named Variants
- Haplotype ID
- HGVS Representation
- DPWG Function Assignment
- DPWG Activity Value
- Definition

**ClinPGx clinical annotations**
- Pediatric ClinPGx Level of Evidence (1)
- Pediatric ClinPGx Level of Evidence (2)
- Pediatric ClinPGx Level of Evidence (3)
- Pediatric ClinPGx Level of Evidence (4)
- Pediatric ClinPGx Level of Evidence (Unknown)
- Non-Pediatric ClinPGx Level of Evidence (1)
- Non-Pediatric ClinPGx Level of Evidence (2)
- Non-Pediatric ClinPGx Level of Evidence (3)
- Non-Pediatric ClinPGx Level of Evidence (4)
- Non-Pediatric ClinPGx Level of Evidence (Unknown)

### 2. Filtered alleles

This worksheet contains the selected allele subset used for focused panel review.

It retains the same ClinPGx/CPIC evidence structure as the full worksheet and includes project-review fields such as:

- Previously validated
- DNALabs Orthogonal Panel
- CPIC / ClinPGx functional information
- Haplotype and HGVS information
- Pediatric and non-pediatric ClinPGx evidence

### 3. Legend

The Legend sheet documents the worksheet highlighting categories used during allele review:

- Data extracted directly from the ClinPGx named-alleles table
- Data extracted from the CPIC Allele Functionality Table
- Already included in validation
- Candidate allele
- Must-include allele: strong or definitive evidence allele not previously included for validation

## Repository structure

```text
.
├── config.py
├── utils.py
├── run_pipeline.py
├── requirements.txt
├── scripts/
│   ├── 01_scrape_clinpgx_gene_table.py
│   ├── 02_enrich_haplotype_details.py
│   ├── 03_compile_clinical_annotations.py
│   ├── 04_merge_clinpgx_annotations.py
│   └── 05_build_allele_overview.py
├── data/
│   ├── clinical_annotations/
│   └── curation/
├── outputs/
└── docs/
    └── TEMPLATE_VERSION_1.md
```

## Setup

Python 3.10+ is recommended. Google Chrome/Chromium is required for the Selenium-based ClinPGx extraction steps.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## ClinPGx clinical-annotation inputs

Place the downloaded ClinPGx clinical-annotation TSV files in:

```text
data/clinical_annotations/
```

using the naming convention:

```text
GENE_pediatric-clinicalAnnotations-all-data.tsv
GENE_nonPediatric-clinicalAnnotations-all-data.tsv
```

The clinical-annotation files are expected to contain:

`Level`, `Variant`, `Gene`, `Drugs`, `Phenotype Categories`, and `Phenotype`.

## Run the full workflow

From the repository root:

```bash
python run_pipeline.py
```

To start from a later step:

```bash
python run_pipeline.py --from-step 3
```

Each numbered script can also be run independently.

## Main outputs

```text
outputs/1_gene_table_clinpgx_extraction_april_2026.csv
outputs/2_gene_table_clinpgx_extraction_april_2026.csv
outputs/3_clinical_annotation_clinpgx_extraction_april_2026.xlsx
outputs/4_combined_gene_clinical_annotations_april_2026.xlsx
outputs/5_combined_with_allele_functionality_columns_april_2026.xlsx
```

## Project-specific review fields

Template Version 1 supports optional local curation files for fields such as prior validation, orthogonal/custom-panel inclusion, and the allele subset included in the `Filtered alleles` worksheet.

Only template CSVs are included in the public repository. Project-specific curation values are kept outside the public code repository.

## Data sources

- ClinPGx: https://www.clinpgx.org/
- CPIC: https://cpicpgx.org/

ClinPGx and CPIC are maintained resources. A re-run at a later date may therefore retrieve updated source information.

## Repository version

**Template Version 1 — April 2026**

## Manuscript link

https://github.com/adrinephd/clinpgx-vip-gene-pipeline
