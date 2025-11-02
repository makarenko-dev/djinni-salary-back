import pytest
from app.scrapers.djinni import _parse_listing_page, PageListing

FILES_PATH = "tests/html_pages"


@pytest.fixture
def read_fixture():
    def _read(name: str) -> str:
        with open(f"{FILES_PATH}/{name}", encoding="utf-8") as f:
            return f.read()

    return _read


def test_parse_listing_single_page(read_fixture):
    text = read_fixture("case_1.html")
    listing: PageListing = _parse_listing_page(text)
    assert listing.has_next_page() is False
    assert listing.company_id == 31192
    assert len(listing.links) == 12


def test_parse_listing_multipage_page_first(read_fixture):
    text = read_fixture("case_2_1.html")
    listing: PageListing = _parse_listing_page(text)
    assert listing.has_next_page() is True
    assert listing.company_id == 5055
    assert len(listing.links) == 15


def test_parse_listing_multipage_page_last(read_fixture):
    text = read_fixture("case_2_5.html")
    listing: PageListing = _parse_listing_page(text)
    assert listing.has_next_page() is False
    assert listing.company_id == 5055
    assert len(listing.links) == 5


def test_parse_listing_multipage_page_middle(read_fixture):
    text = read_fixture("case_2_3.html")
    listing: PageListing = _parse_listing_page(text)
    assert listing.has_next_page() is True
    assert listing.company_id == 5055
    assert len(listing.links) == 15
