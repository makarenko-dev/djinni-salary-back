from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Company, Vacancy


class CompanyCrud:
    @staticmethod
    def get_by_url(session: Session, company_id: int) -> Company | None:
        stmt = select(Company).where(Company.djinni_id == company_id)
        return session.scalar(stmt)

    @staticmethod
    def get_or_create(session: Session, company_id: int) -> Company:
        company = CompanyCrud.get_by_url(session, company_id)
        if company:
            return company
        company = Company(djinni_id=company_id)
        session.add(company)
        session.commit()
        session.refresh(company)
        return company


class VacancyCrud:
    @staticmethod
    def get_by_url(session: Session, url: str) -> Vacancy | None:
        stmt = select(Vacancy).where(Vacancy.url == url)
        return session.scalar(stmt)

    @staticmethod
    def get_or_create(session: Session, url: str, company: Company) -> Vacancy:
        vacancy = VacancyCrud.get_by_url(session, url)
        if vacancy:
            return vacancy
        vacancy = Vacancy(url=url, company_id=company.id)
        session.add(vacancy)
        session.commit()
        session.refresh(vacancy)
        return vacancy
