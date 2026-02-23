"""Scopus fetcher using the Elsevier Scopus Search API.

Returns records in the same format as ris_parser.parse_ris_file() so they
plug directly into the existing AI processing pipeline.
"""

import re

import httpx

from pipeline.ris_parser import normalize_doi


class ScopusFetcher:
    """Fetch papers from Scopus via Elsevier API."""

    BASE_URL = "https://api.elsevier.com/content/search/scopus"

    def __init__(self, api_key: str = "", insttoken: str = ""):
        self.api_key = api_key
        self.insttoken = insttoken

    def search(self, query: str, max_results: int = 100) -> list[dict]:
        """Search Scopus and return normalized paper records.

        Wraps the query in TITLE-ABS-KEY() for Scopus syntax.
        Paginates via start/count params (25 per page).
        """
        if not self.api_key:
            raise ValueError("Scopus API key is required")

        # Wrap in TITLE-ABS-KEY if not already formatted
        if not query.strip().startswith("TITLE-ABS-KEY"):
            scopus_query = f"TITLE-ABS-KEY({query})"
        else:
            scopus_query = query

        records = []
        count = 25  # Scopus default page size
        start = 0

        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
        }
        if self.insttoken:
            headers["X-ELS-Insttoken"] = self.insttoken

        with httpx.Client(timeout=30, headers=headers) as client:
            while len(records) < max_results:
                params = {
                    "query": scopus_query,
                    "start": start,
                    "count": min(count, max_results - len(records)),
                }

                resp = client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                search_results = data.get("search-results", {})
                entries = search_results.get("entry", [])

                if not entries:
                    break

                # Scopus returns an error entry when no results
                if len(entries) == 1 and "error" in entries[0]:
                    break

                for entry in entries:
                    record = self._parse_entry(entry)
                    if record:
                        records.append(record)

                # Check total results
                total = int(search_results.get("opensearch:totalResults", "0"))
                start += count
                if start >= total:
                    break

        return records[:max_results]

    def _parse_entry(self, entry: dict) -> dict | None:
        """Parse a single Scopus search result entry."""
        title = entry.get("dc:title", "").strip()
        if not title:
            return None

        # Abstract (Scopus search API returns dc:description)
        abstract = entry.get("dc:description")
        if abstract:
            abstract = abstract.strip()

        # Authors
        authors = []
        author_str = entry.get("dc:creator", "")
        if author_str:
            authors = [a.strip() for a in author_str.split(";") if a.strip()]
        # If only one author returned, also check author list
        if not authors:
            author_name = entry.get("dc:creator")
            if author_name:
                authors = [author_name]

        # DOI
        doi = normalize_doi(entry.get("prism:doi"))

        # Journal
        journal = entry.get("prism:publicationName")

        # Year
        year = None
        cover_date = entry.get("prism:coverDate", "")
        if cover_date:
            match = re.search(r"(19|20)\d{2}", cover_date)
            if match:
                year = int(match.group())

        # Keywords (authkeywords field)
        keywords = []
        authkeywords = entry.get("authkeywords")
        if authkeywords:
            keywords = [k.strip() for k in authkeywords.split("|") if k.strip()]

        # URL
        url = None
        for link in entry.get("link", []):
            if link.get("@ref") == "scopus":
                url = link.get("@href")
                break
        if not url and doi:
            url = f"https://doi.org/{doi}"

        return {
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "doi": doi,
            "url": url,
            "journal": journal,
            "year": year,
            "keywords": keywords,
            "source_database": "scopus",
            "ris_raw": None,
        }
