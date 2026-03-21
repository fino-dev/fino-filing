from datetime import date

import fino_filing as ff

collection = ff.Collection()

edinetCollector = ff.EdinetCollector(
    collection=collection,
    config=ff.EdinetConfig(api_key="7de69cfeaf77482fae304cdef9a660de"),
)

edinetCollector.collect(date_from=date(2025, 1, 1), date_to=date(2025, 1, 2))
