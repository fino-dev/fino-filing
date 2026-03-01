"""EdgerCollector の collect フローと Collection 連携を検証する"""

from typing import Iterator

from fino_filing import EDGARFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerBulkData, EdgerConfig, EdgerCollector, EdgerSecApi


class TestEdgerCollector:
    """EdgerCollector: Sec/Bulk のオーケストレーションと add_to_collection"""

    def test_collect_adds_edgar_filing_to_collection(
        self,
        temp_collection: tuple,
        sample_raw_document: RawDocument,
        edger_config: EdgerConfig,
    ) -> None:
        """fetch_documents が 1 件返すとき collect() で 1 件が Collection に add される"""
        from fino_filing.collection.collection import Collection

        collection: Collection = temp_collection[0]
        sec_api = EdgerSecApi(edger_config)
        bulk = EdgerBulkData(edger_config)
        # fetch_documents を差し替えてネットワークなしで 1 件 yield する Collector
        class OneDocEdgerCollector(EdgerCollector):
            def fetch_documents(
                self, limit_per_company: int | None = None
            ) -> Iterator[RawDocument]:
                yield sample_raw_document

        collector = OneDocEdgerCollector(
            collection=collection,
            edger_sec_api=sec_api,
            edger_bulk=bulk,
            cik_list=[],
        )
        results = collector.collect()

        assert len(results) == 1
        filing, path = results[0]
        assert isinstance(filing, EDGARFiling)
        assert filing.source == "EDGAR"
        assert filing.accession_number == sample_raw_document.meta["accession_number"]
        assert path
        # Collection に格納されていること
        got = collection.get_filing(filing.id)
        assert got is not None
        assert got.accession_number == filing.accession_number
        content = collection.get_content(filing.id)
        assert content == sample_raw_document.content
