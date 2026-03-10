import logging

from fino_filing import Collection, EdgerConfig, EdgerDocumentsCollector

logging.basicConfig(level=logging.DEBUG)

collection = Collection()
config = EdgerConfig(user_agent_email="odukaki@gmail.com")

collector = EdgerDocumentsCollector(collection=collection, config=config)

# 収集条件は collect() 呼び出し時に渡す
collected = collector.collect(cik_list=["320193"], limit_per_company=2)
print(collected)
