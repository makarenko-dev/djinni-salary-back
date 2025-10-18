from fastapi import FastAPI

from .routers import salary
from .models import Base
from .database import engine


app = FastAPI()
app.include_router(salary.router, prefix="/api")
