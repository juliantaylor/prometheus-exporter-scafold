# prometheus-exporter-scafold

Scafolding to run generic code that generates metrics and expose them via http.

Place plugin python files into the `plugins/` folder. The `run` function of the
file will be called every `interval` seconds (default 30). Plugins can populate
[prometheus_client](https://github.com/prometheus/client_python) metrics which
 will be exposed by the main process via http.

By the run command should be an asyncio coroutine and should not block.

If asyncio is not an option one can set set `threaded = True` in the plugin and
the run function will instead be called in a thread.

In addition to the metrics provided by the plugin files and the default
`prometheus_client` metrics the framework exposed following metrics with label
`name=pluginname`:

- `exporter_runtime_seconds`: histogram metric of the runtime of the plugins
  `run` function 
- `exporter_deadline_exceeded`: counter how often the plugin runtime was longer
  than the call interval
