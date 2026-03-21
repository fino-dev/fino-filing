import fino_filing as ff

collection = ff.Collection()

edinetCollector = ff.EdinetCollector(
    collection=collection,
    config=ff.EdinetConfig(api_key="7de69cfeaf77482fae304cdef9a660de"),
)

edinetCollector.collect(date_from="2025-01-01", date_to="2025-01-02")
