import os
from datetime import date

import fino_filing as ff

storage = ff.LocalStorage(base_dir="debug/.store")
catalog = ff.Catalog(db_file_path="debug/.store/fino_catalog.db")
collection = ff.Collection(catalog=catalog, storage=storage)

edinet_api_key = os.getenv("EDINET_API_KEY")
if edinet_api_key is None:
    raise ValueError("EDINET_API_KEY is not set")

edinet_collector = ff.EdinetCollector(
    collection=collection, config=ff.EdinetConfig(api_key=edinet_api_key)
)

filings = edinet_collector.collect(date_from=date(2025, 1, 1), date_to=date(2025, 1, 2))

print(filings)
