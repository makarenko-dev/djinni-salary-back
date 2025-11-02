from typing import List, Optional
import aiohttp
import asyncio
import random
import logging
import time
from app.utils import measure_time

logger = logging.getLogger("app")


def read_proxy_from_file() -> List[str]:
    with open("proxy.txt") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies


def add_tracing():
    tc = aiohttp.TraceConfig()

    @tc.on_request_start.append
    async def _on_start(session, ctx, params):
        ctx.ts = {"start": time.perf_counter()}

    @tc.on_dns_resolvehost_start.append
    async def _dns_start(session, ctx, params):
        ctx.ts["dns_start"] = time.perf_counter()

    @tc.on_dns_resolvehost_end.append
    async def _dns_end(session, ctx, params):
        ctx.ts["dns"] = time.perf_counter() - ctx.ts["dns_start"]

    @tc.on_connection_create_start.append
    async def _conn_start(session, ctx, params):
        ctx.ts["conn_start"] = time.perf_counter()

    @tc.on_connection_create_end.append
    async def _conn_end(session, ctx, params):
        ctx.ts["connect"] = time.perf_counter() - ctx.ts["conn_start"]

    @tc.on_request_headers_sent.append
    async def _headers_sent(session, ctx, params):
        ctx.ts["headers_sent"] = time.perf_counter()

    # For aiohttp < 3.9
    @tc.on_response_chunk_received.append
    async def _chunk_received(session, ctx, params):
        if "ttfb" not in ctx.ts:
            ctx.ts["ttfb"] = time.perf_counter() - ctx.ts["headers_sent"]

    @tc.on_request_end.append
    async def _on_end(session, ctx, params):
        total = time.perf_counter() - ctx.ts["start"]
        print(
            f"TIMINGS dns={ctx.ts.get('dns',0):.3f}s "
            f"connect={ctx.ts.get('connect',0):.3f}s "
            f"ttfb={ctx.ts.get('ttfb',0):.3f}s total={total:.3f}s"
        )

    return tc


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
        if len(proxies) == 0:
            logger.warning("Initializing NO proxy mode")
            session = aiohttp.ClientSession(connector=connector)
            self.sessions.append(session)
            self.proxies.append(None)
            return
        for proxy in proxies:
            session = aiohttp.ClientSession(connector=connector, proxy=proxy)
            self.sessions.append(session)
            self.proxies.append(proxy)

    def get_session(self):
        index = random.randint(0, len(self.proxies) - 1)
        return self.sessions[index], self.proxies[index]

    async def warm_up(self, url):
        for session in self.sessions:
            async with session.get(url) as reponse:
                text = await reponse.text()

    async def close(self):
        await asyncio.gather(*[s.close() for s in self.sessions])
