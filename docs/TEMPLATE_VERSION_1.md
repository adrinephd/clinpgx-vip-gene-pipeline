# Template Version 1

**Version:** Template Version 1  
**Date:** April 2026

Template Version 1 is the first structured version of the ClinPGx/CPIC VIP-gene allele review workflow used in this project.

## Purpose

The template was designed to assemble pharmacogenomic allele information into a single review workbook that supports:

- review of named alleles and variants across VIP genes;
- comparison of ClinPGx and CPIC functional information;
- review of CPIC allele-functionality evidence;
- review of pediatric and non-pediatric ClinPGx clinical annotations;
- documentation of alleles previously included in validation;
- identification of candidate or must-include alleles for further review; and
- creation of a focused filtered allele list.

## Data flow

```text
ClinPGx gene / named-allele pages
            │
            ▼
      Gene-level table
            │
            ▼
 ClinPGx haplotype details
            │
            ├───────────────┐
            ▼               │
 Enriched allele table      │
            │               │
            │       ClinPGx clinical-
            │       annotation TSVs
            │               │
            └───────┬───────┘
                    ▼
          Combined ClinPGx table
                    │
                    │
          CPIC allele-functionality
             reference tables
                    │
                    ▼
           Template Version 1
             review workbook
```

## Workbook worksheets

### All VIP genes

Comprehensive combined table containing allele identity, functional assignments, ClinPGx haplotype information, CPIC allele-functionality information, and clinical annotation evidence.

### Filtered alleles

Focused subset of alleles selected from the full table for panel-oriented review. It also includes project review fields such as prior validation and orthogonal-panel status.

### Legend

Defines the worksheet highlighting categories used to distinguish data sources and allele-review status.

## Clinical annotation structure

ClinPGx clinical annotations are retained separately for:

- Pediatric evidence
- Non-Pediatric evidence

and are organized into the following ClinPGx evidence categories:

- Level 1
- Level 2
- Level 3
- Level 4
- Unknown

Within each evidence-level cell, annotation text records the ClinPGx evidence level together with drug, phenotype category, and phenotype.

## Public repository contents

The public repository contains:

- the five processing scripts;
- shared gene and URL configuration;
- pipeline utilities;
- dependency specifications;
- input-folder documentation;
- blank curation templates; and
- workflow documentation.

Project-specific curation values and generated source/output datasets are not required to be committed to the public repository.
