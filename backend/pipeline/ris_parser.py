"""RIS file parser wrapping the rispy library.

Handles export variations from EBSCO, Scopus, Web of Science, and PubMed.
"""

import re
from pathlib import Path

import rispy


def normalize_doi(doi: str | None) -> str | None:
    """Normalize a DOI to a canonical form (lowercase, no URL prefix)."""
    if not doi:
        return None
    doi = doi.strip()
    # Strip common URL prefixes
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"]:
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi.strip().lower()


def _detect_source(entry: dict) -> str | None:
    """Try to detect which database the RIS entry came from."""
    raw = str(entry)
    if "EBSCO" in raw or "EBSCOhost" in raw:
        return "ebsco"
    if "Scopus" in raw:
        return "scopus"
    if "Web of Science" in raw or "WoS" in raw:
        return "wos"
    if "PubMed" in raw or "NLM" in raw:
        return "pubmed"
    return None


def _extract_authors(entry: dict) -> list[str]:
    """Extract author list from various RIS fields."""
    authors = entry.get("authors") or entry.get("first_authors") or []
    if isinstance(authors, str):
        authors = [authors]
    return [a.strip() for a in authors if a and a.strip()]


def _extract_year(entry: dict) -> int | None:
    """Extract publication year from various RIS date fields."""
    for field in ["year", "publication_year", "date"]:
        val = entry.get(field)
        if val:
            val_str = str(val)
            match = re.search(r"(19|20)\d{2}", val_str)
            if match:
                return int(match.group())
    return None


def _extract_abstract(entry: dict) -> str | None:
    """Extract abstract from various RIS fields."""
    for field in ["abstract", "notes_abstract"]:
        val = entry.get(field)
        if val:
            return val.strip() if isinstance(val, str) else str(val).strip()
    return None


def parse_ris_file(filepath: str | Path) -> list[dict]:
    """Parse a RIS file and return normalized paper records.

    Each record is a dict with: title, abstract, authors, doi, journal,
    year, keywords, source_database, ris_raw.
    """
    filepath = Path(filepath)
    # Try multiple encodings
    content = None
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            content = filepath.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise ValueError(f"Could not decode file: {filepath}")

    entries = rispy.loads(content)
    records = []

    for entry in entries:
        title = entry.get("title") or entry.get("primary_title")
        if not title:
            continue  # Skip records missing titles

        doi = normalize_doi(
            entry.get("doi")
            or entry.get("url")  # Some exports put DOI in URL field
        )
        # Don't use URL as DOI if it's not actually a DOI
        if doi and not re.match(r"10\.\d{4,}", doi):
            doi = None

        # Extract URL from RIS entry; fall back to DOI link
        url = entry.get("url") or entry.get("file_attachments1") or entry.get("link") or None
        if isinstance(url, list):
            url = url[0] if url else None
        if not url and doi:
            url = f"https://doi.org/{doi}"

        record = {
            "title": title.strip(),
            "abstract": _extract_abstract(entry),
            "authors": _extract_authors(entry),
            "doi": doi,
            "url": url,
            "journal": (entry.get("journal_name") or entry.get("secondary_title") or entry.get("alternate_title3") or "").strip() or None,
            "year": _extract_year(entry),
            "keywords": entry.get("keywords") or [],
            "source_database": _detect_source(entry),
            "ris_raw": entry,
        }
        records.append(record)

    return records
