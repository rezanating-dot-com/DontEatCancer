"""Full-text fetcher for academic papers.

Tries multiple strategies to retrieve full article text:
1. PMC XML API (if pmc_id is known)
2. NCBI ID converter (doi → pmc_id → PMC XML)
3. Direct URL scraping (fallback)
"""

import logging
import re
import xml.etree.ElementTree as ET

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DontEatCancer/1.0; academic research bot)"
}


def fetch_fulltext(record: dict) -> str | None:
    """Orchestrate full-text retrieval for a paper record.

    Tries PMC (by pmc_id or doi), then falls back to URL scraping.
    Returns cleaned full text or None.
    """
    pmc_id = record.get("pmc_id")

    # Strategy 1: Direct PMC fetch if we have a PMC ID
    if pmc_id:
        text = fetch_from_pmc(pmc_id)
        if text:
            return text

    # Strategy 2: Convert DOI to PMC ID, then fetch
    doi = record.get("doi")
    if doi and not pmc_id:
        pmc_id = fetch_pmc_id_from_doi(doi)
        if pmc_id:
            text = fetch_from_pmc(pmc_id)
            if text:
                return text

    # Strategy 3: Scrape the URL directly
    url = record.get("url")
    if url:
        text = fetch_from_url(url)
        if text:
            return text

    return None


def fetch_from_pmc(pmc_id: str) -> str | None:
    """Fetch full text from PMC via the E-utilities XML API.

    Extracts body sections (methods, results, discussion), stripping
    references and figure captions.
    """
    # Normalize: accept both "PMC1234" and "1234"
    numeric_id = pmc_id.replace("PMC", "")
    url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pmc&id={numeric_id}&rettype=xml"
    )

    try:
        with httpx.Client(timeout=30, headers=_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("PMC fetch failed for %s: %s", pmc_id, e)
        return None

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        logger.warning("PMC XML parse failed for %s", pmc_id)
        return None

    # Extract <body> text from JATS XML
    body = root.find(".//body")
    if body is None:
        logger.debug("No <body> element in PMC XML for %s", pmc_id)
        return None

    # Remove elements we don't want
    for tag in ("ref-list", "fig", "table-wrap", "supplementary-material"):
        for el in body.iter(tag):
            parent = _find_parent(body, el)
            if parent is not None:
                parent.remove(el)

    # Extract text from remaining elements
    sections = []
    for sec in body.iter("sec"):
        title_el = sec.find("title")
        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        paragraphs = []
        for p in sec.iter("p"):
            text = "".join(p.itertext()).strip()
            if text:
                paragraphs.append(text)
        if paragraphs:
            section_text = f"\n\n## {title}\n\n" if title else "\n\n"
            section_text += "\n\n".join(paragraphs)
            sections.append(section_text)

    if not sections:
        # Fallback: just grab all paragraph text from body
        paragraphs = []
        for p in body.iter("p"):
            text = "".join(p.itertext()).strip()
            if text:
                paragraphs.append(text)
        if paragraphs:
            return "\n\n".join(paragraphs)
        return None

    full_text = "\n".join(sections).strip()
    return full_text if len(full_text) > 200 else None


def fetch_pmc_id_from_doi(doi: str) -> str | None:
    """Look up a PMC ID from a DOI using the NCBI ID Converter API."""
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi}&format=json"

    try:
        with httpx.Client(timeout=15, headers=_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.debug("NCBI ID converter failed for DOI %s: %s", doi, e)
        return None

    records = data.get("records", [])
    if records and records[0].get("pmcid"):
        return records[0]["pmcid"]
    return None


def fetch_from_url(url: str) -> str | None:
    """Scrape article text from a URL as a last resort.

    Uses BeautifulSoup to extract article body content. Returns None
    if the page looks like a paywall or login page.
    """
    try:
        with httpx.Client(timeout=20, headers=_HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.debug("URL fetch failed for %s: %s", url, e)
        return None

    content_type = resp.headers.get("content-type", "")
    if "html" not in content_type:
        return None

    soup = BeautifulSoup(resp.text, "lxml")

    # Detect paywall / login pages
    page_text_lower = soup.get_text().lower()
    paywall_signals = [
        "sign in to access",
        "subscribe to read",
        "purchase this article",
        "institutional login",
        "access denied",
        "buy this article",
    ]
    if any(signal in page_text_lower for signal in paywall_signals):
        logger.debug("Paywall detected at %s", url)
        return None

    # Try common academic article selectors
    article_el = (
        soup.find("article")
        or soup.find("div", class_=re.compile(r"article[-_]?(body|content|text)", re.I))
        or soup.find("main")
        or soup.find("div", id=re.compile(r"article[-_]?(body|content|text)", re.I))
    )

    if article_el is None:
        return None

    # Remove nav, header, footer, sidebar, reference sections
    for unwanted in article_el.find_all(["nav", "header", "footer", "aside"]):
        unwanted.decompose()
    for unwanted in article_el.find_all(class_=re.compile(r"(reference|citation|sidebar|nav)", re.I)):
        unwanted.decompose()

    paragraphs = [p.get_text(strip=True) for p in article_el.find_all("p") if p.get_text(strip=True)]

    if not paragraphs or len(paragraphs) < 3:
        return None

    text = "\n\n".join(paragraphs)
    return text if len(text) > 200 else None


def _find_parent(root: ET.Element, target: ET.Element) -> ET.Element | None:
    """Find the parent of an element in an ElementTree (ET lacks parent map)."""
    for parent in root.iter():
        for child in parent:
            if child is target:
                return parent
    return None
