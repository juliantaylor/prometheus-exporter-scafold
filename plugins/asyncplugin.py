import logging
import asyncio
import random
from prometheus_client import Gauge

metric = Gauge("test", "", [])
interval = 30

async def run():
    s = random.uniform(0, 10)
    logging.info("metric get %d", s)
    await asyncio.sleep(s)
    metric.inc()
