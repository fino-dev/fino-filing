import logging

from fino_filing import (
    Collection,
    EdgerBulkData,
    EdgerCollector,
    EdgerConfig,
    EdgerSecApi,
)

logging.basicConfig(level=logging.DEBUG)

collection = Collection()

edger_collector = EdgerCollector(
    collection,
    EdgerSecApi(EdgerConfig()),
    EdgerBulkData(
        EdgerConfig(),
    ),
    cik_list=["320193"],
)

collected = edger_collector.collect()
print(collected)
