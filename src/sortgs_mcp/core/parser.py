"""HTML parsing utilities for Google Scholar results."""

import re
from bs4 import BeautifulSoup, Tag


def get_citations(content: str) -> int:
    """Extract number of citations from HTML content using regex.

    Args:
        content: HTML content string containing citation info

    Returns:
        Number of citations (0 if not found)
    """
    match = re.search(r"Cited by (\d+)", content)
    return int(match.group(1)) if match else 0


def get_year(content: str) -> int:
    """Extract publication year from content using regex.

    Args:
        content: HTML content string containing year info

    Returns:
        Publication year (0 if not found)
    """
    match = re.search(r"\b(19|20)\d{2}\b", content)
    return int(match.group(0)) if match else 0


def get_author(content: str) -> str:
    """Extract the author string from metadata content.

    Args:
        content: HTML metadata content with author info

    Returns:
        Author string (cleaned of unicode artifacts)
    """
    clean_content = content.replace("\xa0", " ")
    return clean_content.split(" - ")[0] if clean_content else ""


def get_pdf_link(div: Tag) -> str | None:
    """Extract PDF link from Google Scholar result div if available.

    Args:
        div: BeautifulSoup Tag element containing the result

    Returns:
        PDF URL if found, None otherwise
    """
    try:
        pdf_div = div.find("div", {"class": "gs_ggs gs_fl"})
        if pdf_div:
            a_tag = pdf_div.find("a")
            if a_tag:
                return a_tag.get("href")
    except Exception:
        pass
    return None


def parse_google_scholar_page(html_content: bytes) -> list[dict]:
    """Parse a Google Scholar results page and extract paper metadata.

    Args:
        html_content: Raw HTML bytes from Google Scholar

    Returns:
        List of paper dictionaries with extracted metadata
    """
    soup = BeautifulSoup(html_content, "html.parser", from_encoding="utf-8")
    papers = []

    # Find all result divs
    result_divs = soup.findAll("div", {"class": "gs_or"})

    for div in result_divs:
        paper = {}

        # Extract title and source URL
        try:
            h3_tag = div.find("h3")
            a_tag = h3_tag.find("a") if h3_tag else None
            paper["title"] = a_tag.text if a_tag else "Could not catch title"
            paper["source_url"] = a_tag.get("href") if a_tag else ""
        except Exception:
            paper["title"] = "Could not catch title"
            paper["source_url"] = ""

        # Extract citations
        try:
            paper["citations"] = get_citations(str(div.format_string))
        except Exception:
            paper["citations"] = 0

        # Extract year
        try:
            gs_a_div = div.find("div", {"class": "gs_a"})
            year_text = gs_a_div.text if gs_a_div else ""
            paper["year"] = get_year(year_text)
        except Exception:
            paper["year"] = 0

        # Extract author
        try:
            gs_a_div = div.find("div", {"class": "gs_a"})
            author_text = gs_a_div.text if gs_a_div else ""
            paper["authors"] = get_author(author_text)
        except Exception:
            paper["authors"] = "Author not found"

        # Extract publisher
        try:
            gs_a_div = div.find("div", {"class": "gs_a"})
            pub_text = gs_a_div.text if gs_a_div else ""
            paper["publisher"] = pub_text.split("-")[-1]
        except Exception:
            paper["publisher"] = "Publisher not found"

        # Extract venue
        try:
            gs_a_div = div.find("div", {"class": "gs_a"})
            venue_text = gs_a_div.text if gs_a_div else ""
            paper["venue"] = " ".join(venue_text.split("-")[-2].split(",")[:-1])
        except Exception:
            paper["venue"] = "Venue not found"

        # Extract content snippet
        try:
            content_div = div.find("div", {"class": "gs_rs"})
            paper["content_snippet"] = content_div.text if content_div else "Content not found"
        except Exception:
            paper["content_snippet"] = "Content not found"

        # Extract PDF link
        paper["pdf_url"] = get_pdf_link(div)

        papers.append(paper)

    return papers
