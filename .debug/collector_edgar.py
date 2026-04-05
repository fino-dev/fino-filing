import logging

from fino_filing import (
    Collection,
    EdgarArchiveCollector,
    EdgarConfig,
    EdgarFactsCollector,
    EdgarFiling,
    Field,
)

logging.basicConfig(level=logging.DEBUG)

collection = Collection()
config = EdgarConfig(user_agent_email="odukaki@gmail.com")

collector = EdgarArchiveCollector(collection=collection, config=config)

# 収集条件は collect() 呼び出し時に渡す
collected = collector.collect(cik_list=["320193"], limit_per_company=2)
print(collected)

edgar_facts_controller = EdgarFactsCollector(collection=collection, config=config)

edgar_facts_collected = edgar_facts_controller.collect(
    cik_list=["320193"], limit_per_company=2
)

print(edgar_facts_collected)


collection = Collection()

filings = collection.search(expr=(Field("source") == "Edgar"))

print("===================================")
print(filings)

filings = collection.search(expr=(Field("source") == EdgarFiling.source))

print("===================================")
print(EdgarFiling.source)
print("===================================")
print(filings)
