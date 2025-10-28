from typing import Set, Tuple, Dict
import requests
import time
import logging
from app.scrapers.session_pool import SessionPool
from app.utils import measure_time

logger = logging.getLogger("app")
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


@measure_time
async def fetch_page_async(url: str, params: Dict[str, str] | None = None):
    session, proxy = SessionPool.instance().get_session()
    logger.debug(f"Making request with {proxy} for {url}")
    async with session.get(
        url, params=params, proxy=proxy, headers=headers
    ) as response:
        text = await response.text()
    return text
