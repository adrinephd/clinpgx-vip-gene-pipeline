#!/usr/bin/env python3
"""Step 3: compile pediatric and non-pediatric ClinPGx annotation downloads."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import variant_sort_key  # noqa: E402

REQUIRED_COLUMNS = {
    "Level",
    "Variant",
    "Gene",
    "Drugs",
    "Phenotype Categories",
    "Phenotype",
}

COLUMN_ORDER = [
    "Gene",
    "Variant",
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

FILENAME_RE = re.compile(
    r"^(?P<gene>[^_]+)_(?P<cohort>pediatric|nonPediatric)-clinicalAnnotations-all-data\.tsv$"
)


def discover_files(input_dir: Path) -> dict[str, dict[str, Path]]:
    discovered: dict[str, dict[str, Path]] = {}
    for path in sorted(input_dir.glob("*-clinicalAnnotations-all-data.tsv")):
        match = FILENAME_RE.match(path.name)
        if not match:
            print(f"Skipping unrecognized filename: {path.name}")
            continue
        gene = match.group("gene")
        cohort = match.group("cohort")
        discovered.setdefault(gene, {})[cohort] = path
    return discovered


def annotation_text(row: pd.Series) -> str:
    # Preserve the April 2026 output convention, including 'nan' when a source
    # field is missing, so regenerated annotations remain comparable.
    return f"({row['Level']}, {row['Drugs']}, {row['Phenotype Categories']}, {row['Phenotype']})"


def process_data(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    df = df.copy()
    df.rename(columns=lambda x: str(x).strip(), inplace=True)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    keep = df["Variant"].astype("string").str.startswith("rs", na=False) | df[
        "Variant"
    ].astype("string").str.contains(r"\*", na=False)
    df = df.loc[keep].copy()

    df["Gene"] = df["Gene"].astype("string").str.split("; ")
    df = df.explode("Gene")
    df["Variant"] = df["Variant"].astype("string").str.split("; ")
    df = df.explode("Variant")

    df["Gene"] = df["Gene"].astype("string").str.strip()
    df["Variant"] = df["Variant"].astype("string").str.strip()
    # Remove only a gene prefix at the start of a star-allele label.
    df["Variant"] = df.apply(
        lambda r: r["Variant"][len(r["Gene"]) :]
        if isinstance(r["Variant"], str)
        and isinstance(r["Gene"], str)
        and r["Variant"].startswith(r["Gene"])
        else r["Variant"],
        axis=1,
    )

    df["Annotation"] = df.apply(annotation_text, axis=1)
    df["Evidence Level"] = pd.to_numeric(
        df["Level"].astype(str).str.extract(r"(\d)", expand=False), errors="coerce"
    )
    df["Annotation Group"] = df["Evidence Level"].apply(
        lambda level: (
            f"{source_type} Level {int(level)}"
            if pd.notna(level)
            else f"{source_type} Level Unknown"
        )
    )

    grouped = (
        df.groupby(["Gene", "Variant", "Annotation Group"], dropna=False)["Annotation"]
        .apply(lambda values: "; ".join(sorted(values.astype(str))))
        .reset_index()
        .pivot(index=["Gene", "Variant"], columns="Annotation Group", values="Annotation")
        .reset_index()
    )

    grouped.rename(
        columns={
            f"{source_type} Level {level}": f"{source_type} ClinPGx Level of Evidence ({level})"
            for level in [1, 2, 3, 4]
        }
        | {
            f"{source_type} Level Unknown": f"{source_type} ClinPGx Level of Evidence (Unknown)"
        },
        inplace=True,
    )
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/clinical_annotations"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/3_clinical_annotation_clinpgx_extraction_april_2026.xlsx"),
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    files = discover_files(args.input_dir)
    if not files:
        raise FileNotFoundError(
            f"No '*-clinicalAnnotations-all-data.tsv' files were found in {args.input_dir}"
        )

    combined: list[pd.DataFrame] = []
    for gene, cohorts in sorted(files.items()):
        pieces: list[pd.DataFrame] = []
        for cohort_key, source_label in [
            ("pediatric", "Pediatric"),
            ("nonPediatric", "Non-Pediatric"),
        ]:
            path = cohorts.get(cohort_key)
            if not path:
                continue
            try:
                df = pd.read_csv(path, sep="\t")
                pieces.append(process_data(df, source_label))
            except ValueError as exc:
                print(f"Skipping {path.name}: {exc}")

        if not pieces:
            continue
        master = pieces[0]
        for piece in pieces[1:]:
            master = master.merge(piece, on=["Gene", "Variant"], how="outer")
        # The source file is gene-specific; use its filename-derived gene as the
        # canonical gene label, matching the original April 2026 workflow.
        master["Gene"] = gene
        combined.append(master)

    if not combined:
        raise RuntimeError("No valid clinical-annotation files could be processed")

    out = pd.concat(combined, ignore_index=True)
    for col in COLUMN_ORDER:
        if col not in out.columns:
            out[col] = ""
    out = out[COLUMN_ORDER]

    # Stable gene + variant sort while preserving the custom star-allele ordering.
    out["_variant_sort"] = out["Variant"].map(variant_sort_key)
    out = out.sort_values(["Gene", "_variant_sort", "Variant"]).drop(columns="_variant_sort")
    out.to_excel(args.output, index=False)
    print(f"Saved {len(out)} rows to {args.output}")


if __name__ == "__main__":
    main()
