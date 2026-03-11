import logging

from fino_filing import (
    Collection,
    EDGARFiling,
    EdgerConfig,
    EdgerDocumentsCollector,
    EdgerFactsCollector,
    Field,
)

logging.basicConfig(level=logging.DEBUG)

collection = Collection()
config = EdgerConfig(user_agent_email="odukaki@gmail.com")

collector = EdgerDocumentsCollector(collection=collection, config=config)

# 収集条件は collect() 呼び出し時に渡す
collected = collector.collect(cik_list=["320193"], limit_per_company=2)
print(collected)

edger_facts_controller = EdgerFactsCollector(collection=collection, config=config)

edger_facts_collected = edger_facts_controller.collect(
    cik_list=["320193"], limit_per_company=2
)

print(edger_facts_collected)


collection = Collection()

filings = collection.search(expr=(Field("source") == "EDGAR"))

print("===================================")
print(filings)

filings = collection.search(expr=(Field("source") == EDGARFiling.source))

print("===================================")
print(EDGARFiling.source)
print("===================================")
print(filings)
