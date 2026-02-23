"""OpenAlex fetcher using the OpenAlex REST API.

Returns records in the same format as ris_parser.parse_ris_file() so they
plug directly into the existing AI processing pipeline.
"""

import httpx

from pipeline.ris_parser import normalize_doi


class OpenAlexFetcher:
    """Fetch papers from OpenAlex."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, api_key: str = "", mailto: str = ""):
        self.api_key = api_key
        self.mailto = mailto

    def search(self, query: str, max_results: int = 100) -> list[dict]:
        """Search OpenAlex and return normalized paper records.

        Uses the /works endpoint with title_and_abstract.search filter.
        Paginates via page/per_page (max 200 per page).
        """
        records = []
        per_page = min(max_results, 200)
        page = 1

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        with httpx.Client(timeout=30, headers=headers) as client:
            while len(records) < max_results:
                params: dict = {
                    "filter": f"title_and_abstract.search:{query},is_oa:true",
                    "per_page": min(per_page, max_results - len(records)),
                    "page": page,
                }
                if self.mailto and not self.api_key:
                    params["mailto"] = self.mailto

                resp = client.get(f"{self.BASE_URL}/works", params=params)
                resp.raise_for_status()
                data = resp.json()

                results = data.get("results", [])
                if not results:
                    break

                for work in results:
                    record = self._parse_work(work)
                    if record:
                        records.append(record)

                # Stop if we've exhausted results
                meta = data.get("meta", {})
                total = meta.get("count", 0)
                if page * per_page >= total:
                    break

                page += 1

        return records[:max_results]

    def _parse_work(self, work: dict) -> dict | None:
        """Parse a single OpenAlex work object into a normalized record."""
        title = work.get("title", "")
        if not title:
            return None

        # Abstract: reconstruct from inverted index
        abstract = self._reconstruct_abstract(
            work.get("abstract_inverted_index")
        )

        # Authors
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                authors.append(name)

        # DOI
        doi = normalize_doi(work.get("doi"))

        # Journal
        journal = None
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        journal = source.get("display_name")

        # Year
        year = work.get("publication_year")

        # Keywords
        keywords = []
        for keyword in work.get("keywords", []):
            kw = keyword.get("display_name", "")
            if kw:
                keywords.append(kw)
        # Also grab concepts
        for concept in work.get("concepts", []):
            name = concept.get("display_name", "")
            score = concept.get("score", 0)
            if name and score > 0.5:
                keywords.append(name)

        # URL — prefer open-access URL for direct full-text access
        oa = work.get("open_access") or {}
        oa_url = oa.get("oa_url")
        url = oa_url or primary_location.get("landing_page_url") or work.get("doi")

        return {
            "title": title.strip(),
            "abstract": abstract,
            "authors": authors,
            "doi": doi,
            "url": url,
            "journal": journal,
            "year": year,
            "keywords": keywords,
            "source_database": "openalex",
            "ris_raw": None,
        }

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
        """Reconstruct abstract text from OpenAlex inverted index format.

        OpenAlex stores abstracts as {word: [position1, position2, ...]}
        which we need to convert back to plaintext.
        """
        if not inverted_index:
            return None

        # Build list of (position, word) tuples
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))

        if not word_positions:
            return None

        # Sort by position and join
        word_positions.sort(key=lambda x: x[0])
        return " ".join(word for _, word in word_positions)
