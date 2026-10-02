"""Shared configuration for the April 2026 ClinPGx/CPIC extraction pipeline."""

from __future__ import annotations

CLINPGX_GENES: list[tuple[str, str]] = [
    ("ABCB1", "PA267"),
    ("ABCG2", "PA390"),
    ("ACE", "PA139"),
    ("ADRB1", "PA38"),
    ("ADRB2", "PA39"),
    ("CACNA1S", "PA85"),
    ("CFTR", "PA109"),
    ("COMT", "PA117"),
    ("CYP2A6", "PA121"),
    ("CYP2B6", "PA123"),
    ("CYP2C19", "PA124"),
    ("CYP2C8", "PA125"),
    ("CYP2C9", "PA126"),
    ("CYP2D6", "PA128"),
    ("CYP3A4", "PA130"),
    ("CYP3A5", "PA131"),
    ("CYP4F2", "PA27121"),
    ("DPYD", "PA145"),
    ("DRD2", "PA27478"),
    ("G6PD", "PA28469"),
    ("GSTP1", "PA29028"),
    ("HLA-B", "PA35056"),
    ("IFNL3", "PA134952671"),
    ("MTHFR", "PA245"),
    ("MT-RNR1", "PA31274"),
    ("NAT2", "PA18"),
    ("NUDT15", "PA134963132"),
    ("RYR1", "PA34896"),
    ("SLC19A1", "PA327"),
    ("SLCO1B1", "PA134865839"),
    ("TPMT", "PA356"),
    ("TYMS", "PA359"),
    ("UGT1A1", "PA420"),
    ("VKORC1", "PA133787052"),
]

CPIC_ALLELE_FUNCTION_URLS: dict[str, str] = {
    gene: (
        "https://files.cpicpgx.org/data/report/current/allele_function_reference/"
        f"{gene}_allele_functionality_reference.xlsx"
    )
    for gene in [
        "ABCG2",
        "CACNA1S",
        "CYP2B6",
        "CYP2C9",
        "CYP2C19",
        "CYP2D6",
        "CYP3A5",
        "DPYD",
        "G6PD",
        "MT-RNR1",
        "NAT2",
        "NUDT15",
        "RYR1",
        "SLCO1B1",
        "TPMT",
        "UGT1A1",
        "VKORC1",
    ]
}

CLINPGX_BASE_URL = "https://www.clinpgx.org"

CPIC_FUNCTION_COLUMN_INDICES = [0, 1, 3, 6, 5, 7]
CPIC_FUNCTION_COLUMN_NAMES = [
    "Allele",
    "Activity Score",
    "Allele Function",
    "CPIC Strength of Evidence",
    "References",
    "Summary",
]

GRCH38_BOILERPLATE = (
    "Any chromosomal positions listed below are assumed to be on the GRCh38 assembly. "
    "Be aware, the assembly may differ for variants elsewhere on the ClinPGx site."
)
GRCH38_SHORT_LABEL = "Assume to be on GRCh38 assembly"
