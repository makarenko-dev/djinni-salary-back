from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    MappedAsDataclass,
)
from typing import List
from datetime import datetime


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(150))
    djinni_id: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    vacancies: Mapped[List["Vacancy"]] = relationship(
        back_populates="company", cascade="all, delete-orphan", default_factory=list
    )


class Vacancy(Base):
    __tablename__ = "vacancies"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    url: Mapped[str] = mapped_column(String(150))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="vacancies", init=False)
    low_boundary: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default="0", default=0
    )
    high_boundary: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default="10000", default=10000
    )
    salary: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default="0", default=0
    )
    salary_dt: Mapped[datetime | None] = mapped_column(
        DateTime(), nullable=True, default=None
    )
