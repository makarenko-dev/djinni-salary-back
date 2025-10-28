from typing import List, Optional
import aiohttp
import asyncio
import random
import logging

from app.utils import measure_time

logger = logging.getLogger("app")


def read_proxy_from_file() -> List[str]:
    with open("proxy.txt") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies


class SessionPool:
    _singletone: "SessionPool | None" = None

    @classmethod
    def instance(cls):
        if cls._singletone is None:
            cls._singletone = cls()
        return cls._singletone

    def __init__(self):
        self.sessions: List[aiohttp.ClientSession] = []
        self.proxies: List[str] = []

    def pool_init(self, proxies: List[str]):
        connector = aiohttp.TCPConnector(ttl_dns_cache=600, keepalive_timeout=120)
        for proxy in proxies:
            session = aiohttp.ClientSession(connector=connector, proxy=proxy)
            self.sessions.append(session)
            self.proxies.append(proxy)

    def get_session(self):
        # index = random.randint(0, len(self.proxies) - 1)
        index = 0
        return self.sessions[index], self.proxies[index]

    async def warm_up(self, url):
        for session in self.sessions:
            async with session.get(url) as reponse:
                text = await reponse.text()

    async def close(self):
        await asyncio.gather(*[s.close() for s in self.sessions])
