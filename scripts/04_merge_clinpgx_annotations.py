#!/usr/bin/env python3
"""Step 4: outer-join named-allele/haplotype data with clinical annotations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import normalize_gene_variant_columns  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gene-table", type=Path, default=Path("outputs/2_gene_table_clinpgx_extraction_april_2026.csv"))
    parser.add_argument("--clinical-annotations", type=Path, default=Path("outputs/3_clinical_annotation_clinpgx_extraction_april_2026.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("outputs/4_combined_gene_clinical_annotations_april_2026.xlsx"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    gene_df = pd.read_csv(args.gene_table, dtype="string")
    clinical_df = pd.read_excel(args.clinical_annotations, dtype="string")

    gene_df.rename(columns=lambda x: str(x).strip(), inplace=True)
    clinical_df.rename(columns=lambda x: str(x).strip(), inplace=True)
    if "Named Alleles" not in gene_df.columns:
        raise ValueError(f"{args.gene_table} is missing 'Named Alleles'")

    gene_df = gene_df.rename(columns={"Named Alleles": "Variant"})
    gene_df = normalize_gene_variant_columns(gene_df)
    clinical_df = normalize_gene_variant_columns(clinical_df)

    merged = gene_df.merge(
        clinical_df,
        on=["Gene", "Variant"],
        how="outer",
        suffixes=("_gene", "_clinical"),
    )
    merged = merged[["Gene", "Variant"] + [c for c in merged.columns if c not in {"Gene", "Variant"}]]
    merged.to_excel(args.output, index=False)
    print(f"Saved {len(merged)} rows to {args.output}")


if __name__ == "__main__":
    main()
