from aiohttp import web
import threading
import os
import glob
import time
import logging
import asyncio
import time
import importlib
from functools import partial
from prometheus_client import Histogram, Counter, generate_latest


plugin_dir = "plugins"
runtime = Histogram("exporter_runtime_seconds", "", ["name"], buckets=range(10))
deadline = Counter("exporter_deadline_exceeded", "", ["name"])


async def handle(request):
    return web.Response(text=generate_latest().decode('UTF-8'))


def load_plugins():
    for f in glob.glob(os.path.join(plugin_dir, "*.py")):
        yield importlib.import_module(f.replace(os.sep, ".").rstrip(".py"))


async def start_background_tasks(app):
    for plugin in load_plugins():
        logging.info("plugin: %s", plugin.__name__)
        if getattr(plugin, "threaded", False):
            run_threaded_plugin(plugin)
        else:
            app[plugin.__name__] = asyncio.create_task(run_async_plugin(plugin))


async def cleanup_background_tasks(app):
    for v in app.values():
        v.cancel()
        await v


async def run_async_plugin(plugin):
    interval = getattr(plugin, "interval", 30)
    name = plugin.__name__.lstrip(plugin_dir + ".")
    m_runtime = runtime.labels(name)
    m_deadline = deadline.labels(name)
    while True:
        try:
            t = time.time()       
            await plugin.run()
            t = time.time() - t
            m_runtime.observe(t)
            if t > interval:
                m_deadline.inc()
            await asyncio.sleep(max(interval - t, 0))
        except asyncio.CancelledError:
            logging.info("canceled")
            return


def run_threaded_plugin(plugin):
    t = threading.Thread(target=partial(thread_loop, plugin), daemon=True)
    t.start()


def thread_loop(plugin):
    interval = getattr(plugin, "interval", 30)
    name = plugin.__name__.lstrip(plugin_dir + ".")
    m_runtime = runtime.labels(name)
    m_deadline = deadline.labels(name)
    while True:
        t = time.time()
        plugin.run()
        t = time.time() - t
        m_runtime.observe(t)
        logging.info("runtime %d", t)
        if t > interval:
            m_deadline.inc()
        time.sleep(max(interval - t, 0))



app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle)])
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)
