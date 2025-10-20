from fastapi import FastAPI

from .routers import salary
from .models import Base
from .database import engine

from .logging_config import configure_logging

configure_logging()
app = FastAPI()
app.include_router(salary.router, prefix="/api")
