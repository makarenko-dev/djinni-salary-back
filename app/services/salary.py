from sqlalchemy.orm import Session
from app.crud.salary import CompanyCrud, VacancyCrud
from app.models import Vacancy
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Set
import time
import requests


def salary_probe(session: Session, vacancy_url: str, company_id: int) -> int:
    company = CompanyCrud.get_or_create(session, company_id)
    vacancy = VacancyCrud.get_or_create(session, vacancy_url, company)
    if vacancy.salary:
        return vacancy.salary
    salary = scrape_salary(session, vacancy)
    return salary


def middle_salary(low: int, high: int) -> int:
    step = 500
    mid = (low + high) // 2
    # snap to nearest multiple of step (down)
    mid = (mid // step) * step
    return mid


def scrape_salary(session: Session, vacancy: Vacancy):
    is_active = check_if_vacancy_active(vacancy.url)
    if not is_active:
        return -1
    all_links = vacancy_links_for_company(vacancy.company.djinni_id, 0)
    target_link = vacancy.url
    vacancies_mapping = {}
    for link in all_links:
        vacancies_mapping[link] = VacancyCrud.get_or_create(
            session, link, vacancy.company
        )
    time.sleep(2)
    salary_filter = middle_salary(vacancy.low_boundary, vacancy.high_boundary)
    print(f"Starting with filter {salary_filter}")
    i = 0
    while True:
        i = i + 1
        found_links = vacancy_links_for_company(
            vacancy.company.djinni_id, salary_filter
        )
        for link in found_links:
            vacancy = vacancies_mapping[link]
            if vacancy.low_boundary < salary_filter:
                vacancy.low_boundary = salary_filter
        gone_links = all_links - found_links
        for link in gone_links:
            vacancy = vacancies_mapping[link]
            if vacancy.high_boundary > salary_filter or vacancy.high_boundary == 0:
                vacancy.high_boundary = salary_filter
        print(
            f"Requested filter {salary_filter}. Found {found_links}. Gone {gone_links}"
        )
        # Check did salary was found
        for link in vacancies_mapping.keys():
            vacancy = vacancies_mapping[link]
            diff = vacancy.high_boundary - vacancy.low_boundary
            if diff == 500:
                vacancy.salary = vacancy.low_boundary
        session.commit()
        target = vacancies_mapping[target_link]
        if target.salary:
            print("Found salary")
            return target.salary
        salary_filter = middle_salary(target.low_boundary, target.high_boundary)
        print(f"Setting filter {salary_filter}")
        if i == 5:
            return 0


def check_if_vacancy_active(vacancy_url: str) -> bool:
    response = requests.get(vacancy_url)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    vacancy_title = soup.select_one("div.job-post-page > header > h1")
    spans = vacancy_title.find_all("span")
    return len(spans) == 1


def vacancy_links_for_company(djinni_id: int, starting_salary: int) -> Set[str]:
    url = "https://djinni.co/jobs/"
    params = {"company_id": djinni_id, "salary": starting_salary}
    response = requests.get(url, params=params)
    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    anchors = soup.select("a.job-item__title-link")
    links = {urljoin("https://djinni.co", anchor["href"]) for anchor in anchors}
    return links
