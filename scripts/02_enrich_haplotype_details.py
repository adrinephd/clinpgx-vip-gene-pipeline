#!/usr/bin/env python3
"""Step 2: enrich named alleles with ClinPGx haplotype-page details."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import CLINPGX_BASE_URL, CLINPGX_GENES  # noqa: E402

DETAIL_COLUMNS = [
    "Haplotype ID",
    "CPIC Function Assignment",
    "CPIC Activity Value",
    "HGVS Representation",
    "DPWG Function Assignment",
    "DPWG Activity Value",
    "Definition",
]


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1600,1200")
    return webdriver.Chrome(options=options)


def get_soup(driver: webdriver.Chrome, url: str, timeout: int) -> BeautifulSoup:
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    return BeautifulSoup(driver.page_source, "html.parser")


def text_after_label(soup: BeautifulSoup, label_text: str) -> str:
    """Extract a fact value using both legacy classes and a label-text fallback."""
    for fact in soup.select("div.fact"):
        label = fact.select_one(".factLabel__content")
        if label and label.get_text(" ", strip=True) == label_text:
            content = fact.select_one(".fact-content")
            if content:
                return content.get_text(" ", strip=True)

    label_node = soup.find(string=lambda s: bool(s and s.strip() == label_text))
    if not label_node:
        return ""
    container = label_node.parent
    for _ in range(4):
        if container is None:
            break
        candidates = container.find_all(["div", "span", "p"], recursive=False)
        for candidate in candidates:
            value = candidate.get_text(" ", strip=True)
            if value and value != label_text:
                return value
        sibling = container.find_next_sibling()
        if sibling:
            value = sibling.get_text(" ", strip=True)
            if value and value != label_text:
                return value
        container = container.parent
    return ""


def extract_definition(soup: BeautifulSoup) -> str:
    for section in soup.select("div.fact-section"):
        header = section.select_one(".fact-section-header")
        if header and header.get_text(" ", strip=True) == "Definition":
            content = section.select_one(".fact-section-content")
            if content:
                paragraph = content.find("p")
                if paragraph:
                    return paragraph.get_text(" ", strip=True)

    heading = soup.find(
        ["h2", "h3", "h4", "div"],
        string=lambda s: bool(s and s.strip() == "Definition"),
    )
    if heading:
        paragraph = heading.find_next("p")
        if paragraph:
            return paragraph.get_text(" ", strip=True)
    return ""


def parse_haplotype_page(
    soup: BeautifulSoup, gene: str, allele: str, hap_id: str
) -> dict[str, str]:
    row = {
        "Gene": gene,
        "Named Alleles": allele,
        "Haplotype ID": hap_id,
        "CPIC Function Assignment": text_after_label(soup, "CPIC Function Assignment"),
        "CPIC Activity Value": text_after_label(soup, "CPIC Activity Value"),
        "HGVS Representation": text_after_label(soup, "HGVS Representation"),
        "DPWG Function Assignment": text_after_label(soup, "DPWG Function Assignment"),
        "DPWG Activity Value": text_after_label(soup, "DPWG Activity Value"),
        "Definition": extract_definition(soup),
    }

    for field in soup.select("div.variantDetailItem___2nNqM"):
        label = field.select_one(".detailFieldLabel___36zHn")
        value = field.select_one(".detailFieldValue___yP1fO")
        if label and value:
            row[label.get_text(" ", strip=True)] = value.get_text(" ", strip=True)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("outputs/1_gene_table_clinpgx_extraction_april_2026.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/2_gene_table_clinpgx_extraction_april_2026.csv"),
    )
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    base = pd.read_csv(args.input, dtype="string")
    if "Named Alleles" not in base.columns:
        raise ValueError(f"{args.input} does not contain a 'Named Alleles' column")

    detail_rows: list[dict[str, str]] = []
    with build_driver() as driver:
        for gene, clinpgx_id in CLINPGX_GENES:
            gene_url = f"{CLINPGX_BASE_URL}/gene/{clinpgx_id}/haplotype"
            print(f"Finding haplotypes for {gene}")
            try:
                soup = get_soup(driver, gene_url, args.timeout)
                links = soup.select("a[href^='/haplotype/PA']")
                seen: set[tuple[str, str]] = set()
                for link in links:
                    allele = link.get_text(" ", strip=True)
                    href = link.get("href", "")
                    if not allele or not href:
                        continue
                    key = (allele, href)
                    if key in seen:
                        continue
                    seen.add(key)
                    hap_id = href.rstrip("/").split("/")[-1]
                    hap_soup = get_soup(
                        driver, f"{CLINPGX_BASE_URL}{href}", args.timeout
                    )
                    detail_rows.append(
                        parse_haplotype_page(hap_soup, gene, allele, hap_id)
                    )
            except Exception as exc:
                print(f"  ERROR for {gene}: {exc}")

    details = pd.DataFrame(detail_rows)
    if details.empty:
        details = pd.DataFrame(columns=["Gene", "Named Alleles", *DETAIL_COLUMNS])

    details = details.drop_duplicates(
        subset=["Gene", "Named Alleles"], keep="first"
    )

    base = base.drop(
        columns=[c for c in DETAIL_COLUMNS if c in base.columns],
        errors="ignore",
    )
    enriched = base.merge(details, on=["Gene", "Named Alleles"], how="left")
    for col in DETAIL_COLUMNS:
        if col not in enriched.columns:
            enriched[col] = ""

    enriched.to_csv(args.output, index=False)
    print(f"Saved {len(enriched)} rows to {args.output}")


if __name__ == "__main__":
    main()
