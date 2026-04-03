import logging

from fino_filing import (
    Collection,
    EDGARFiling,
    EdgerArchivesCollector,
    EdgerConfig,
    EdgerFactsCollector,
    Field,
)

logging.basicConfig(level=logging.DEBUG)

collection = Collection()
config = EdgerConfig(user_agent_email="odukaki@gmail.com")

# EdgerDocumentsCollector は互換用（既定 filing_index）。primary / xbrl_bundle は EdgerArchivesCollector を使用。
collector = EdgerArchivesCollector(collection=collection, config=config)

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
