from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.schemas import SalaryRequest, SalaryResponse
from app.services import salary as salary_service

router = APIRouter(prefix="/salary")


@router.post("/", response_model=SalaryResponse)
async def salary_probe(payload: SalaryRequest, session: Session = Depends(get_db)):
    salary = await salary_service.salary_probe(
        session, payload.vacancy_url, payload.company_name
    )
    return SalaryResponse(vacancy_url=payload.vacancy_url, salary=salary)
