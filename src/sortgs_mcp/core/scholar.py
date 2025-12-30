"""Async Google Scholar searcher with Selenium fallback."""

import asyncio
import datetime
import logging
import random
from typing import List
from urllib.parse import quote_plus

import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sortgs_mcp.core.debug_samples import DEBUG_SAMPLE_HTML
from sortgs_mcp.core.parser import get_author, parse_google_scholar_page
from sortgs_mcp.models import Paper, SearchParams

ROBOT_KW = ["unusual traffic from your computer network", "not a robot"]

logger = logging.getLogger(__name__)

_driver = None


def _format_languages(languages: List[str]) -> str:
    """Format language filters for Google Scholar."""
    if len(languages) == 1:
        return f"lang_{languages[0]}"
    return "%7C".join(f"lang_{lang}" for lang in languages)


def _get_driver():
    """Lazily initialize a shared Chrome WebDriver."""
    global _driver
    if _driver is None:
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        _driver = webdriver.Chrome(options=chrome_options)
    return _driver


class ScholarSearcher:
    """Async Google Scholar searcher using httpx with Selenium fallback."""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self._client: httpx.AsyncClient | None = None
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    async def __aenter__(self) -> "ScholarSearcher":
        self._client = self._make_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _make_client(self) -> httpx.AsyncClient:
        """Create a configured AsyncClient."""
        return httpx.AsyncClient(
            timeout=30.0,
            headers=self._headers,
            follow_redirects=True,
        )

    def build_url(self, params: SearchParams, offset: int = 0) -> str:
        """Construct Google Scholar URL based on params and offset."""
        debug_mode = params.debug or self.debug
        base_url = (
            "https://scholar.google.com/scholar?"
            f"start={offset}&q={quote_plus(params.keywords)}&hl=en&as_sdt=0,5"
        )

        if params.start_year:
            base_url += f"&as_ylo={params.start_year}"
        if params.end_year:
            base_url += f"&as_yhi={params.end_year}"
        if params.languages:
            base_url += f"&lr={_format_languages(params.languages)}"

        if debug_mode:
            return f"https://web.archive.org/web/20210314203256/{base_url}"
        return base_url

    async def fetch_page(self, url: str, *, debug_mode: bool = False) -> bytes:
        """Fetch page with httpx and fallback to Selenium on robot check."""
        if self._client is None:
            async with self._make_client() as client:
                return await self._fetch_with_client(client, url, debug_mode=debug_mode)

        return await self._fetch_with_client(self._client, url, debug_mode=debug_mode)

    async def _fetch_with_client(
        self, client: httpx.AsyncClient, url: str, *, debug_mode: bool
    ) -> bytes:
        """Perform the HTTP fetch and handle robot detection."""
        await asyncio.sleep(random.uniform(0.5, 3.0))
        try:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.content
        except httpx.HTTPError as exc:
            if debug_mode or self.debug:
                logger.warning(
                    "HTTP fetch failed in debug mode (%s); using bundled sample HTML.",
                    exc,
                )
                return DEBUG_SAMPLE_HTML
            raise

        is_archive = "web.archive.org" in url
        if not is_archive and self._is_robot_check(html_content):
            logger.warning("Robot check detected; using Selenium fallback.")
            html_content = await asyncio.to_thread(self.fetch_with_selenium, url)

        return html_content

    def fetch_with_selenium(self, url: str) -> bytes:
        """Fetch page content using Selenium (blocking)."""
        driver = _get_driver()
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        body = driver.find_element(By.TAG_NAME, "body")
        if any(kw in body.text for kw in ROBOT_KW):
            input(
                "Solve CAPTCHA manually in the browser, then press Enter to continue..."
            )

        return body.get_attribute("innerHTML").encode("utf-8")

    async def search(self, params: SearchParams) -> list[Paper]:
        """Search Google Scholar and return a list of Papers."""
        papers: list[Paper] = []
        current_year = params.end_year or datetime.datetime.now().year
        close_client = False

        if self._client is None:
            self._client = self._make_client()
            close_client = True

        try:
            for offset in range(0, params.num_results, 10):
                url = self.build_url(params, offset)
                debug_mode = params.debug or self.debug
                try:
                    html = await self.fetch_page(url, debug_mode=debug_mode)
                except httpx.HTTPError:
                    if debug_mode:
                        logger.warning(
                            "HTTP fetch raised in debug mode; using bundled sample HTML."
                        )
                        html = DEBUG_SAMPLE_HTML
                    else:
                        raise

                results = parse_google_scholar_page(html)
                if debug_mode and not results:
                    logger.warning(
                        "No results parsed in debug mode; using bundled sample HTML."
                    )
                    results = parse_google_scholar_page(DEBUG_SAMPLE_HTML)

                for result in results:
                    citations = result.get("citations", 0) or 0
                    year = result.get("year", 0) or 0
                    years_delta = max(1, current_year - year + 1) if year > 0 else 1
                    cit_per_year = int(citations / years_delta)

                    paper = Paper(
                        rank=len(papers) + 1,
                        title=result.get("title", "Could not catch title"),
                        authors=result.get("authors", get_author("")),
                        citations=citations,
                        year=year,
                        publisher=result.get("publisher", "Publisher not found"),
                        venue=result.get("venue", "Venue not found"),
                        content_snippet=result.get(
                            "content_snippet", "Content not found"
                        ),
                        source_url=result.get("source_url", ""),
                        pdf_url=result.get("pdf_url"),
                        cit_per_year=cit_per_year,
                    )
                    papers.append(paper)

                if len(papers) >= params.num_results:
                    break
        finally:
            if close_client and self._client:
                await self._client.aclose()
                self._client = None

        key = (
            (lambda p: p.cit_per_year)
            if params.sort_by == "cit/year"
            else (lambda p: p.citations)
        )
        papers_sorted = sorted(papers, key=key, reverse=True)

        for idx, paper in enumerate(papers_sorted, start=1):
            paper.rank = idx

        return papers_sorted[: params.num_results]

    @staticmethod
    def _is_robot_check(html_content: bytes) -> bool:
        """Detect robot checks by searching for known keywords."""
        try:
            text = html_content.decode("ISO-8859-1")
            return any(kw in text for kw in ROBOT_KW)
        except Exception:
            return False
