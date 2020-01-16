import logging
import time
import random
from prometheus_client import Gauge

metric = Gauge("thread", "", [])
interval = 30
threaded = True


def run():
    s = random.uniform(0, 10)
    logging.info("thread metric get %d", s)
    time.sleep(s)
    metric.inc()
