from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Set, Tuple
import logging
import json
import html

from dataclasses import dataclass, field

from .network import fetch_page_async

logger = logging.getLogger("app")

DJINNI_HOST = "https://djinni.co"
NEXT_PAGE_SELECTOR = 'a:has(span.bi-chevron-right):not([aria-disabled="True"])'
VACANCY_TITLE_SELECTOR = "div.job-post-page > header > h1"
VACANCY_LINK_SELECTOR = "a.job-item__title-link"
COMPANY_LINK_SELECTOR = 'a[data-analytics="company_page"].text-body'


@dataclass
class PageListing:
    next_page: str | None
    company_id: str
    links: Set[str] = field(default_factory=set)

    def has_next_page(self) -> bool:
        return self.next_page is not None


async def check_if_vacancy_active(vacancy_url: str) -> bool:
    html = await fetch_page_async(vacancy_url)
    return _parse_vacancy_active(html)


def _parse_vacancy_active(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    vacancy_title = soup.select_one(VACANCY_TITLE_SELECTOR)
    spans = vacancy_title.find_all("span")
    return len(spans) == 1


async def company_links_by_name(company_name: str, target_vacancy: str):
    url = f"{DJINNI_HOST}/jobs/{company_name}"
    params = {"page": "1"}
    return await _scrape_listing(url, params, target_vacancy)


async def vacancy_links_by_id(
    djinni_id: int, starting_salary: int, target_vacancy: str
) -> Tuple[Set[str], bool]:
    url = f"{DJINNI_HOST}/jobs/"
    params = {"company_id": djinni_id, "salary": starting_salary, "page": "1"}
    return await _scrape_listing(url, params, target_vacancy)


async def _scrape_listing(url: str, params, target_vacancy: str):
    links = set()
    has_next_page = True
    while has_next_page:
        logger.info(f"Requesting djinni jobs with params {params}")
        html = await fetch_page_async(url, params=params)
        page = _parse_listing_page(html)
        links.update(page.links)
        if target_vacancy in page.links:
            break
        if not page.has_next_page():
            break
        params["page"] = page.next_page
    return links, page.has_next_page(), page.company_id


def _parse_listing_page(html_text: str) -> PageListing:
    soup = BeautifulSoup(html_text, "lxml")
    anchors = soup.select(VACANCY_LINK_SELECTOR)
    page_links = {urljoin(DJINNI_HOST, anchor["href"]) for anchor in anchors}
    page_number = _next_page(soup)
    company_link = soup.select_one(COMPANY_LINK_SELECTOR)
    if company_link:
        company_json = json.loads(html.unescape(company_link["data-json-parameter"]))
        company_id = company_json["company_id"]
    else:
        company_id = None
    return PageListing(links=page_links, next_page=page_number, company_id=company_id)


def _next_page(soup: BeautifulSoup) -> int | None:
    element = soup.select_one(NEXT_PAGE_SELECTOR)
    if not element:
        return None
    page_number = element["href"].split("=")[-1]
    return page_number
