#!/usr/bin/env python3
"""Step 5: merge CPIC allele-functionality data and apply April 2026 curation."""

from __future__ import annotations

import argparse
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import (  # noqa: E402
    CPIC_ALLELE_FUNCTION_URLS,
    CPIC_FUNCTION_COLUMN_INDICES,
    CPIC_FUNCTION_COLUMN_NAMES,
    GRCH38_BOILERPLATE,
    GRCH38_SHORT_LABEL,
)
from utils import extract_allele_number, normalize_gene_variant_columns  # noqa: E402

OUTPUT_COLUMNS = [
    "Gene",
    "Variant",
    "Allele number",
    "Previously validated",
    "Included in custom veridose panel",
    "AMP Tier",
    "CPIC Function",
    "ClinPGx Function",
    "Allele",
    "Activity Score",
    "Allele Function",
    "CPIC Strength of Evidence",
    "References",
    "Summary",
    "Named Alleles Description",
    "Named Variants",
    "Haplotype ID",
    "HGVS Representation",
    "DPWG Function Assignment",
    "DPWG Activity Value",
    "Definition",
    "Pediatric ClinPGx Level of Evidence (1)",
    "Pediatric ClinPGx Level of Evidence (2)",
    "Pediatric ClinPGx Level of Evidence (3)",
    "Pediatric ClinPGx Level of Evidence (4)",
    "Pediatric ClinPGx Level of Evidence (Unknown)",
    "Non-Pediatric ClinPGx Level of Evidence (1)",
    "Non-Pediatric ClinPGx Level of Evidence (2)",
    "Non-Pediatric ClinPGx Level of Evidence (3)",
    "Non-Pediatric ClinPGx Level of Evidence (4)",
    "Non-Pediatric ClinPGx Level of Evidence (Unknown)",
]


def download_cpic_tables(timeout: int = 60) -> pd.DataFrame:
    tables: list[pd.DataFrame] = []
    headers = {"User-Agent": "clinpgx-vip-gene-pipeline/2026-04"}

    for gene, url in CPIC_ALLELE_FUNCTION_URLS.items():
        print(f"Downloading CPIC allele-functionality table for {gene}")
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            workbook = pd.ExcelFile(BytesIO(response.content))
            raw = workbook.parse(workbook.sheet_names[0], header=None)
            if raw.shape[1] <= max(CPIC_FUNCTION_COLUMN_INDICES):
                raise ValueError(
                    f"Unexpected CPIC workbook layout: found {raw.shape[1]} columns"
                )
            selected = raw.iloc[:, CPIC_FUNCTION_COLUMN_INDICES].copy()
            selected.columns = CPIC_FUNCTION_COLUMN_NAMES
            selected["Gene"] = gene
            tables.append(selected)
        except Exception as exc:
            print(f"  WARNING: CPIC table failed for {gene}: {exc}")

    if not tables:
        raise RuntimeError("No CPIC allele-functionality tables were downloaded")
    return pd.concat(tables, ignore_index=True)


def load_curation(path: Path | None) -> pd.DataFrame:
    if not path or not path.exists():
        return pd.DataFrame(
            columns=[
                "Gene",
                "Variant",
                "Previously validated",
                "Included in custom veridose panel",
                "HGVS Representation override",
            ]
        )
    cur = pd.read_csv(path, dtype="string")
    expected = {"Gene", "Variant"}
    if not expected.issubset(cur.columns):
        raise ValueError(f"{path} must contain Gene and Variant columns")
    return normalize_gene_variant_columns(cur)


def apply_curation(df: pd.DataFrame, curation: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if curation.empty:
        for col in ["Previously validated", "Included in custom veridose panel"]:
            if col not in out.columns:
                out[col] = pd.NA
        return out

    cur_cols = [
        c
        for c in [
            "Gene",
            "Variant",
            "Previously validated",
            "Included in custom veridose panel",
            "HGVS Representation override",
        ]
        if c in curation.columns
    ]
    cur = curation[cur_cols].drop_duplicates(["Gene", "Variant"], keep="last")
    out = out.merge(cur, on=["Gene", "Variant"], how="left", suffixes=("", "_curation"))

    for col in ["Previously validated", "Included in custom veridose panel"]:
        cur_col = f"{col}_curation"
        if cur_col in out.columns:
            out[col] = out[cur_col].combine_first(out[col] if col in out.columns else pd.Series(pd.NA, index=out.index))
            out.drop(columns=cur_col, inplace=True)
        elif col not in out.columns:
            out[col] = pd.NA

    override = "HGVS Representation override"
    if override in out.columns:
        mask = out[override].notna() & out[override].astype("string").str.strip().ne("")
        out.loc[mask, "HGVS Representation"] = out.loc[mask, override]
        out.drop(columns=override, inplace=True)
    return out


def build_filtered_sheet(all_df: pd.DataFrame, selection_path: Path | None) -> pd.DataFrame:
    if not selection_path or not selection_path.exists():
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    selection = pd.read_csv(selection_path, dtype="string")
    selection = normalize_gene_variant_columns(selection)
    required = {"Gene", "Variant"}
    if not required.issubset(selection.columns):
        raise ValueError(f"{selection_path} must contain Gene and Variant columns")

    # The curated filtered workbook contains one row per Gene + Variant even when
    # the all-genes sheet has duplicate matches after the CPIC merge.
    base = all_df.drop_duplicates(["Gene", "Variant"], keep="first")
    filtered = selection.merge(base, on=["Gene", "Variant"], how="left", suffixes=("_selection", ""))

    if "DNALabs Orthogonal Panel" not in filtered.columns:
        filtered["DNALabs Orthogonal Panel"] = pd.NA
    if "Previously validated_selection" in filtered.columns:
        filtered["Previously validated"] = filtered["Previously validated_selection"].combine_first(
            filtered.get("Previously validated")
        )
        filtered.drop(columns="Previously validated_selection", inplace=True)

    # Match the user's curated filtered-sheet naming.
    filtered = filtered.rename(
        columns={"Included in custom veridose panel": "Included in custom veridose panel (all-sheet value)"}
    )
    filtered_columns = [
        "Gene",
        "Variant",
        "Allele number",
        "Previously validated",
        "DNALabs Orthogonal Panel",
        "CPIC Function",
        "ClinPGx Function",
        "Allele",
        "Activity Score",
        "Allele Function",
        "CPIC Strength of Evidence",
        "References",
        "Summary",
        "Named Alleles Description",
        "Named Variants",
        "Haplotype ID",
        "HGVS Representation",
        "DPWG Function Assignment",
        "DPWG Activity Value",
        "Definition",
        "Pediatric ClinPGx Level of Evidence (1)",
        "Pediatric ClinPGx Level of Evidence (2)",
        "Pediatric ClinPGx Level of Evidence (3)",
        "Pediatric ClinPGx Level of Evidence (4)",
        "Pediatric ClinPGx Level of Evidence (Unknown)",
        "Non-Pediatric ClinPGx Level of Evidence (1)",
        "Non-Pediatric ClinPGx Level of Evidence (2)",
        "Non-Pediatric ClinPGx Level of Evidence (3)",
        "Non-Pediatric ClinPGx Level of Evidence (4)",
        "Non-Pediatric ClinPGx Level of Evidence (Unknown)",
    ]
    for col in filtered_columns:
        if col not in filtered.columns:
            filtered[col] = pd.NA
    return filtered[filtered_columns]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("outputs/4_combined_gene_clinical_annotations_april_2026.xlsx"),
    )
    parser.add_argument(
        "--curation",
        type=Path,
        default=Path("data/curation/allele_curation_april_2026.csv"),
    )
    parser.add_argument(
        "--filtered-selection",
        type=Path,
        default=Path("data/curation/filtered_alleles_selection_april_2026.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/5_combined_with_allele_functionality_columns_april_2026.xlsx"),
    )
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    merged = pd.read_excel(args.input, dtype="string")
    merged.rename(columns=lambda x: str(x).strip(), inplace=True)
    merged = normalize_gene_variant_columns(merged)

    # Normalize the Step-1 headers to the names used in the user's final workbook.
    merged.rename(
        columns={
            "CPIC FunctionLearn more about allele functions": "CPIC Function",
            "ClinPGx FunctionLearn more about allele functions": "ClinPGx Function",
            "CPIC FUNCTION from ClinPGx": "CPIC Function legacy",
        },
        inplace=True,
    )
    if "CPIC Function legacy" in merged.columns:
        if "CPIC Function" not in merged.columns:
            merged["CPIC Function"] = merged["CPIC Function legacy"]
        else:
            merged["CPIC Function"] = merged["CPIC Function"].combine_first(
                merged["CPIC Function legacy"]
            )
        merged.drop(columns="CPIC Function legacy", inplace=True)

    cpic = download_cpic_tables(timeout=args.timeout)
    cpic["Gene"] = cpic["Gene"].astype("string").str.strip()
    cpic["Allele"] = cpic["Allele"].astype("string").str.strip()

    final = merged.merge(
        cpic,
        how="left",
        left_on=["Gene", "Variant"],
        right_on=["Gene", "Allele"],
    )
    final["Allele number"] = final["Variant"].apply(extract_allele_number).astype("Int64")

    # Reproduce the concise definition used in the manually edited April 2026 workbook.
    if "Definition" in final.columns:
        final["Definition"] = final["Definition"].replace(
            {GRCH38_BOILERPLATE: GRCH38_SHORT_LABEL}
        )

    final = apply_curation(final, load_curation(args.curation))

    for col in OUTPUT_COLUMNS:
        if col not in final.columns:
            final[col] = pd.NA
    final = final[OUTPUT_COLUMNS]

    filtered = build_filtered_sheet(final, args.filtered_selection)

    legend = pd.DataFrame(
        {
            "Colour": ["", "", "", "", ""],
            "Meaning": [
                'Data extracted directly from the ClinPGx "named alleles" table',
                "Data extracted from the CPIC Allele Functionality Table",
                "Already included in validation",
                "Candidate allele",
                "Must include allele (strong or definitive evidence allele not previously included for validation)",
            ],
        }
    )

    with pd.ExcelWriter(args.output, engine="openpyxl") as writer:
        final.to_excel(writer, sheet_name="All VIP genes", index=False)
        filtered.to_excel(writer, sheet_name="Filtered alleles", index=False)
        legend.to_excel(writer, sheet_name="Legend", index=False)

    print(f"Saved {len(final)} all-gene rows and {len(filtered)} filtered rows to {args.output}")


if __name__ == "__main__":
    main()
