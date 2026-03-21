import os
from datetime import date

import fino_filing as ff

collection = ff.Collection()

edinetCollector = ff.EdinetCollector(
    collection=collection,
    config=ff.EdinetConfig(api_key=os.getenv("EDINET_API_KEY") or ""),
)

edinetCollector.collect(date_from=date(2025, 1, 1), date_to=date(2025, 1, 2))
