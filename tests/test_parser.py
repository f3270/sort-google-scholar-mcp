from bs4 import BeautifulSoup

from sortgs_mcp.core.parser import (
    get_author,
    get_citations,
    get_pdf_link,
    get_year,
    parse_google_scholar_page,
)


def test_get_citations_match():
    assert get_citations("Cited by 123") == 123


def test_get_citations_no_match():
    assert get_citations("No citations here") == 0


def test_get_citations_zero():
    assert get_citations("Cited by 0") == 0


def test_get_year_match():
    assert get_year("Published in 2019") == 2019


def test_get_year_no_match():
    assert get_year("No year here") == 0


def test_get_year_multiple_matches():
    assert get_year("2018 2020") == 2018


def test_get_author_clean_unicode():
    assert get_author("A Author\xa0B Author - Journal") == "A Author B Author"


def test_get_author_split_on_dash():
    assert get_author("A Author - Journal") == "A Author"


def test_get_author_empty():
    assert get_author("") == ""


def test_get_pdf_link_found():
    html = """
    <div class="gs_or">
      <div class="gs_ggs gs_fl">
        <a href="https://example.com/paper.pdf">[PDF]</a>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", {"class": "gs_or"})
    assert get_pdf_link(div) == "https://example.com/paper.pdf"


def test_get_pdf_link_not_found():
    html = '<div class="gs_or"></div>'
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", {"class": "gs_or"})
    assert get_pdf_link(div) is None


def test_parse_google_scholar_page_full(scholar_html_fixture):
    papers = parse_google_scholar_page(scholar_html_fixture)
    assert len(papers) == 2
    assert papers[0]["title"] == "Attention Is All You Need"
    assert papers[0]["citations"] == 123
    assert papers[0]["year"] == 2017
    assert papers[0]["pdf_url"] == "https://example.com/paper1.pdf"
    assert papers[1]["pdf_url"] is None


def test_parse_google_scholar_page_empty():
    papers = parse_google_scholar_page(b"")
    assert papers == []
