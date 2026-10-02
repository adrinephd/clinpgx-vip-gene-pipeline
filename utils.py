"""Small shared helpers for the ClinPGx pipeline."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


def clean_text(value: object) -> str:
    """Return a stripped string, using an empty string for missing values."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_gene_variant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize merge keys without converting missing values to the literal 'nan'."""
    result = df.copy()
    for col in ("Gene", "Variant"):
        if col in result.columns:
            result[col] = result[col].astype("string").str.strip()
    return result


def extract_allele_number(variant: object) -> float:
    """Extract the first star-allele number for sorting; rsIDs return NaN."""
    if not isinstance(variant, str):
        return np.nan
    match = re.search(r"\*(\d+)", variant)
    return float(match.group(1)) if match else np.nan


def variant_sort_key(variant: object) -> tuple[int, float | str]:
    """Sort star alleles numerically, then rsIDs numerically, then other labels."""
    if pd.isna(variant):
        return (3, float("inf"))
    text = str(variant).strip()
    star = re.search(r"\*(\d+)", text)
    if star:
        return (0, int(star.group(1)))
    if text.startswith("rs"):
        suffix = text[2:]
        return (1, int(suffix) if suffix.isdigit() else text)
    return (2, text)


def require_columns(df: pd.DataFrame, required: Iterable[str], source: Path | str) -> None:
    """Raise a clear error if an input table is missing required columns."""
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")
