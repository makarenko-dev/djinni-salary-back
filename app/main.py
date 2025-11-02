from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import salary

from app.logging_config import configure_logging
from app.scrapers import session_pool
from app import settings

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    proxies = session_pool.read_proxy_from_file()
    session_pool.SessionPool.instance().pool_init(proxies)
    # await network_manager.SessionPool.instance().warm_up("https://djinni.co/jobs/")
    yield
    await session_pool.SessionPool.instance().close()


if settings.DEBUG:
    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)
app.include_router(salary.router, prefix="/api")
