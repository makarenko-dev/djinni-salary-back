from sqlalchemy.orm import Session
from app.crud.salary import CompanyCrud, VacancyCrud
from app.models import Vacancy, Company
from typing import Set, Dict, List

import time
from datetime import datetime, timezone
from app.scrapers import djinni

import logging

logger = logging.getLogger("app")

MAX_ITERATONS = 10
SALARY_STEP = 500


def salary_probe(session: Session, vacancy_url: str, company_id: int) -> int:
    company = CompanyCrud.get_or_create(session, company_id)
    vacancy = VacancyCrud.get_or_create(session, vacancy_url, company)
    if vacancy.salary:
        return vacancy.salary
    salary = _scrape_salary(session, vacancy)
    return salary


def _middle_salary(low: int, high: int) -> int:
    mid = (low + high) // 2
    mid = (mid // SALARY_STEP) * SALARY_STEP
    return mid


def _update_upper_boundary(
    vacancies: Dict[str, Vacancy], vacancies_urls: List[str], salary_filter: int
):
    for link in vacancies_urls:
        vacancy = vacancies[link]
        if vacancy.high_boundary > salary_filter or vacancy.high_boundary == 0:
            vacancy.high_boundary = salary_filter


def _update_low_boundary(
    vacancies: Dict[str, Vacancy],
    vacancies_urls: List[str],
    salary_filter: int,
    session: Session,
    company: Company,
):
    for link in vacancies_urls:
        v = _ensure_vacancy(vacancies, session, link, company)
        if v.low_boundary < salary_filter:
            v.low_boundary = salary_filter


def _ensure_vacancy(
    mapping: Dict[str, Vacancy], session: Session, link: str, company: Company
) -> Vacancy:
    if link not in mapping:
        mapping[link] = VacancyCrud.get_or_create(session, link, company)
    return mapping[link]


def _finalize_salaries(vacancies: Dict[str, Vacancy]):
    for v in vacancies.values():
        if v.salary:
            continue
        if (v.high_boundary - v.low_boundary) == SALARY_STEP:
            v.salary = v.low_boundary
            v.salary_dt = datetime.now(timezone.utc)


def _scrape_salary(session: Session, vacancy: Vacancy):
    is_active = djinni.check_if_vacancy_active(vacancy.url)
    if not is_active:
        return -1
    all_links, _ = djinni.vacancy_links_for_company(
        vacancy.company.djinni_id, 0, vacancy.url
    )
    target_link = vacancy.url
    vacancies: Dict[str, Vacancy] = {
        link: VacancyCrud.get_or_create(session, link, vacancy.company)
        for link in all_links
    }
    time.sleep(2)
    salary_filter = _middle_salary(vacancy.low_boundary, vacancy.high_boundary)
    logger.info(f"Starting salary filter {salary_filter}")
    for iteration in range(1, MAX_ITERATONS + 1):
        found_links, has_more = djinni.vacancy_links_for_company(
            vacancy.company.djinni_id, salary_filter, vacancy.url
        )
        _update_low_boundary(
            vacancies, found_links, salary_filter, session, vacancy.company
        )
        target_found = target_link in found_links
        if not target_found:
            _update_upper_boundary(vacancies, [target_link], salary_filter)
        if not has_more:
            gone_links = all_links - found_links
            _update_upper_boundary(vacancies, gone_links, salary_filter)
        logger.info(
            f"Iteration {iteration} gave {len(found_links)} links. Target present: {target_found}, has more pages: {has_more}"
        )
        _finalize_salaries(vacancies)
        session.commit()
        target = vacancies[target_link]
        if target.salary:
            logger.info("Salary found")
            return target.salary
        salary_filter = _middle_salary(target.low_boundary, target.high_boundary)
        logger.info(f"Setting salary filter to {salary_filter}")
    return 0
