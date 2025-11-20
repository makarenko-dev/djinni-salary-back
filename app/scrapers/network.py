from typing import Set, Tuple, Dict
import time
import sentry_sdk
import logging
import re
from app.scrapers.session_pool import SessionPool, NoSessionsError
from app.utils import measure_time
from app.scrapers.exceptions import ScrapperUnavailableError

logger = logging.getLogger("app")
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}
retry_attempts = 3


@measure_time
async def fetch_page_async(url: str, params: Dict[str, str] | None = None):
    for attempt in range(1, retry_attempts):
        try:
            session, proxy = SessionPool.instance().get_session()
            logger.debug(f"Making request with {proxy} for {url}")
            async with session.get(
                url, params=params, proxy=proxy, headers=headers
            ) as response:
                text = await response.text()
            check_ban(text)
            return text
        except BanDetectedError as e:
            logger.warning(f"ip address banned {proxy}")
            await SessionPool.instance().mark_banned(proxy)
            sentry_sdk.capture_message(f"Ip address has been banned {proxy}")
        except NoSessionsError as e:
            logger.warning(f"No more sessions left")
            sentry_sdk.capture_message(f"No sessions left")
            break
    raise ScrapperUnavailableError()


class BanDetectedError(Exception):
    pass


def check_ban(html: str):
    BAN_RE = re.compile(
        r"Your IP address,\s*\d{1,3}(?:\.\d{1,3}){3},\s*has been blocked\. Please contact us",
        re.IGNORECASE,
    )
    if BAN_RE.search(html):
        raise BanDetectedError()
