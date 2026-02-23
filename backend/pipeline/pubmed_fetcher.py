"""PubMed fetcher using NCBI E-utilities API.

Returns records in the same format as ris_parser.parse_ris_file() so they
plug directly into the existing AI processing pipeline.
"""

import re
import time
import xml.etree.ElementTree as ET

import httpx

from pipeline.ris_parser import normalize_doi


class PubMedFetcher:
    """Fetch papers from PubMed via NCBI E-utilities."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(
        self,
        api_key: str = "",
        email: str = "",
        tool: str = "DontEatCancer",
    ):
        self.api_key = api_key
        self.email = email
        self.tool = tool
        # With API key: 10 req/s (0.1s delay); without: 3 req/s (0.34s delay)
        self._delay = 0.1 if api_key else 0.34

    def _base_params(self) -> dict:
        params: dict = {"tool": self.tool}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def search(self, query: str, max_results: int = 100) -> list[dict]:
        """Search PubMed and return normalized paper records.

        Uses ESearch with usehistory=y, then EFetch in batches of 100.
        """
        # Step 1: ESearch to get WebEnv + QueryKey
        # Filter for free full text to avoid paywalled papers
        oa_query = f"({query}) AND free full text[filter]"
        search_params = {
            **self._base_params(),
            "db": "pubmed",
            "term": oa_query,
            "retmax": 0,  # We just want the count + WebEnv
            "usehistory": "y",
        }

        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{self.BASE_URL}/esearch.fcgi", params=search_params)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        count = int(root.findtext("Count", "0"))
        web_env = root.findtext("WebEnv", "")
        query_key = root.findtext("QueryKey", "")

        if count == 0 or not web_env:
            return []

        # Step 2: EFetch in batches using WebEnv
        fetch_total = min(count, max_results)
        records = []
        batch_size = 100

        with httpx.Client(timeout=60) as client:
            for start in range(0, fetch_total, batch_size):
                time.sleep(self._delay)
                fetch_params = {
                    **self._base_params(),
                    "db": "pubmed",
                    "query_key": query_key,
                    "WebEnv": web_env,
                    "retstart": start,
                    "retmax": min(batch_size, fetch_total - start),
                    "rettype": "xml",
                    "retmode": "xml",
                }
                resp = client.get(
                    f"{self.BASE_URL}/efetch.fcgi", params=fetch_params
                )
                resp.raise_for_status()
                records.extend(self._parse_xml(resp.text))

        return records[:max_results]

    def _parse_xml(self, xml_text: str) -> list[dict]:
        """Parse PubMed XML response into normalized records."""
        records = []
        root = ET.fromstring(xml_text)

        for article in root.iter("PubmedArticle"):
            try:
                record = self._parse_article(article)
                if record:
                    records.append(record)
            except Exception:
                continue  # Skip malformed articles

        return records

    def _parse_article(self, article: ET.Element) -> dict | None:
        """Parse a single PubmedArticle element."""
        medline = article.find("MedlineCitation")
        if medline is None:
            return None

        art = medline.find("Article")
        if art is None:
            return None

        # Title
        title = art.findtext("ArticleTitle", "").strip()
        if not title:
            return None

        # Abstract
        abstract_el = art.find("Abstract")
        abstract = None
        if abstract_el is not None:
            parts = []
            for text_el in abstract_el.iter("AbstractText"):
                label = text_el.get("Label", "")
                text = "".join(text_el.itertext()).strip()
                if label and text:
                    parts.append(f"{label}: {text}")
                elif text:
                    parts.append(text)
            if parts:
                abstract = " ".join(parts)

        # Authors
        authors = []
        author_list = art.find("AuthorList")
        if author_list is not None:
            for author in author_list.iter("Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    name = f"{last}, {fore}" if fore else last
                    authors.append(name)

        # DOI
        doi = None
        article_data = article.find("PubmedData")
        if article_data is not None:
            for aid in article_data.iter("ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = normalize_doi(aid.text)
                    break
        # Also check ELocationID
        if not doi:
            for eloc in art.iter("ELocationID"):
                if eloc.get("EIdType") == "doi":
                    doi = normalize_doi(eloc.text)
                    break

        # PMID and PMC ID
        pmid = medline.findtext("PMID", "")
        pmc_id = None
        if article_data is not None:
            for aid in article_data.iter("ArticleId"):
                if aid.get("IdType") == "pmc":
                    pmc_id = aid.text
                    break

        # Journal
        journal_el = art.find("Journal")
        journal = None
        if journal_el is not None:
            journal = journal_el.findtext("Title", "") or journal_el.findtext(
                "ISOAbbreviation", ""
            )

        # Year
        year = None
        pub_date = art.find(".//PubDate")
        if pub_date is not None:
            year_text = pub_date.findtext("Year", "")
            if year_text:
                match = re.search(r"(19|20)\d{2}", year_text)
                if match:
                    year = int(match.group())
        # Fallback: MedlineDate
        if year is None and pub_date is not None:
            medline_date = pub_date.findtext("MedlineDate", "")
            if medline_date:
                match = re.search(r"(19|20)\d{2}", medline_date)
                if match:
                    year = int(match.group())

        # Keywords
        keywords = []
        for kw_list in medline.iter("KeywordList"):
            for kw in kw_list.iter("Keyword"):
                text = "".join(kw.itertext()).strip()
                if text:
                    keywords.append(text)
        # Also grab MeSH terms
        for mesh in medline.iter("MeshHeading"):
            desc = mesh.findtext("DescriptorName", "").strip()
            if desc:
                keywords.append(desc)

        # URL — prefer PMC full-text link over abstract-only PubMed page
        if pmc_id:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
        elif pmid:
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        elif doi:
            url = f"https://doi.org/{doi}"
        else:
            url = None

        return {
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "doi": doi,
            "url": url,
            "journal": journal.strip() if journal else None,
            "year": year,
            "keywords": keywords,
            "source_database": "pubmed",
            "ris_raw": None,
        }
