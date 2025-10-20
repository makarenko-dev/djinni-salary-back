import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Set, Tuple
import logging

logger = logging.getLogger("app")

DJINNI_HOST = "https://djinni.co"
NEXT_PAGE_SELECTOR = 'a:has(span.bi-chevron-right):not([aria-disabled="True"])'
VACANCY_TITLE_SELECTOR = "div.job-post-page > header > h1"
VACANCY_LINK_SELECTOR = "a.job-item__title-link"


def check_if_vacancy_active(vacancy_url: str) -> bool:
    response = requests.get(vacancy_url)
    page = response.text
    soup = BeautifulSoup(page, "lxml")
    vacancy_title = soup.select_one(VACANCY_TITLE_SELECTOR)
    spans = vacancy_title.find_all("span")
    return len(spans) == 1


def vacancy_links_for_company(
    djinni_id: int, starting_salary: int, target_vacancy: str
) -> Tuple[Set[str], bool]:
    url = f"{DJINNI_HOST}/jobs/"
    links = set()
    params = {"company_id": djinni_id, "salary": starting_salary, "page": "1"}
    has_next_page = True
    while has_next_page:
        logger.info(f"Requesting djinni jobs with params {params}")
        response = requests.get(url, params=params)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        anchors = soup.select(VACANCY_LINK_SELECTOR)
        page_links = {urljoin(DJINNI_HOST, anchor["href"]) for anchor in anchors}
        links.update(page_links)
        page_number = _next_page(soup)
        if not page_number:
            has_next_page = False
        else:
            if target_vacancy in page_links:
                break
            params["page"] = page_number
    return links, has_next_page


def _next_page(soup: BeautifulSoup) -> int | None:
    element = soup.select_one(NEXT_PAGE_SELECTOR)
    if not element:
        return None
    page_number = element["href"].split("=")[-1]
    return page_number
