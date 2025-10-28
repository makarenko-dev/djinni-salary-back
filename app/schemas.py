from pydantic import BaseModel


class SalaryRequest(BaseModel):
    vacancy_url: str
    company_name: str


class SalaryResponse(BaseModel):
    vacancy_url: str
    salary: int
