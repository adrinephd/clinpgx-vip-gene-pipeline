#!/usr/bin/env python3
"""Run the five extraction steps in order from the repository root."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

STEPS = [
    "scripts/01_scrape_clinpgx_gene_table.py",
    "scripts/02_enrich_haplotype_details.py",
    "scripts/03_compile_clinical_annotations.py",
    "scripts/04_merge_clinpgx_annotations.py",
    "scripts/05_build_allele_overview.py",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-step",
        type=int,
        choices=range(1, 6),
        default=1,
        help="Start at this step (1-5). Useful when web-scraped intermediate files already exist.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent
    for index, relative in enumerate(STEPS, start=1):
        if index < args.from_step:
            continue
        script = repo / relative
        print(f"\n=== Step {index}: {script.name} ===", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=repo, check=True)


if __name__ == "__main__":
    main()
