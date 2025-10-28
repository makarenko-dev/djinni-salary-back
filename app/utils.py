from functools import wraps
import logging
import time
import asyncio

logger = logging.getLogger("app")


def measure_time(func):
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"{func.__name__} executed in {(end - start):.4f} seconds")
            return result

        return async_wrapper
    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            logger.info(f"{func.__name__} executed in {(end - start):.4f} seconds")
            return result

        return sync_wrapper
