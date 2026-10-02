#!/usr/bin/env python3
"""Step 1: scrape ClinPGx named-allele tables for the configured VIP genes."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import CLINPGX_BASE_URL, CLINPGX_GENES  # noqa: E402


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1600,1200")
    return webdriver.Chrome(options=options)


def rendered_soup(driver: webdriver.Chrome, url: str, timeout: int) -> BeautifulSoup:
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_elements("tag name", "table") or "Named Alleles" in d.page_source
    )
    return BeautifulSoup(driver.page_source, "html.parser")


def normalize_header(header: str) -> str | None:
    text = re.sub(r"\s+", " ", header).strip()
    if text.startswith("CPIC Function"):
        return "CPIC Function"
    if text.startswith("ClinPGx Function"):
        return "ClinPGx Function"
    if text.startswith("AMP Tier"):
        return "AMP Tier"
    if text in {"All", "Filter Named Alleles", "Filter Named Variants", "Filter PharmVar Id"}:
        return None
    return text


def extract_named_allele_description(soup: BeautifulSoup) -> str:
    heading = soup.find(
        ["h2", "h3"], string=lambda x: bool(x and "Named Alleles" in x)
    )
    if not heading:
        return ""
    paragraph = heading.find_next("p")
    return paragraph.get_text(" ", strip=True) if paragraph else ""


def scrape_gene(soup: BeautifulSoup, gene: str) -> list[dict[str, str]]:
    table = soup.find("table")
    if not table:
        return [{"Gene": gene, "Named Alleles Description": extract_named_allele_description(soup)}]

    raw_headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]
    headers = [normalize_header(h) for h in raw_headers]
    rows: list[dict[str, str]] = []

    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if not cells:
            continue
        row: dict[str, str] = {"Gene": gene}
        for header, value in zip(headers, cells):
            if header:
                row[header] = value
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs/1_gene_table_clinpgx_extraction_april_2026.csv"))
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, str]] = []
    with build_driver() as driver:
        for gene, clinpgx_id in CLINPGX_GENES:
            url = f"{CLINPGX_BASE_URL}/gene/{clinpgx_id}/haplotype"
            print(f"Checking {gene}: {url}")
            try:
                soup = rendered_soup(driver, url, args.timeout)
                rows = scrape_gene(soup, gene)
                all_rows.extend(rows)
                if not rows or (len(rows) == 1 and not rows[0].get("Named Alleles Description")):
                    print(f"  Warning: no named-allele table or description found for {gene}")
            except Exception as exc:
                print(f"  ERROR for {gene}: {exc}")
                all_rows.append({"Gene": gene, "Scrape Error": str(exc)})

    preferred = ["Gene", "Named Alleles", "Named Variants", "CPIC Function", "ClinPGx Function", "AMP Tier", "Named Alleles Description"]
    extra = sorted({key for row in all_rows for key in row} - set(preferred))
    fieldnames = [c for c in preferred if any(c in row for row in all_rows)] + extra

    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved {len(all_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
