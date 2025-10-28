from fastapi import FastAPI
from contextlib import asynccontextmanager

from .routers import salary

from app.logging_config import configure_logging
from app.scrapers import session_pool

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    proxies = session_pool.read_proxy_from_file()
    session_pool.SessionPool.instance().pool_init(proxies)
    # await network_manager.SessionPool.instance().warm_up("https://djinni.co/jobs/")
    yield
    await session_pool.SessionPool.instance().close()


app = FastAPI(lifespan=lifespan)
app.include_router(salary.router, prefix="/api")
