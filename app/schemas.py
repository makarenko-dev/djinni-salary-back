from pydantic import BaseModel


class SalaryRequest(BaseModel):
    vacancy_url: str
    company_id: int


class SalaryResponse(BaseModel):
    vacancy_url: str
    salary: int
