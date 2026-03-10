"""EdinetCollector の collect フローと Collection 連携を検証する"""

from typing import Any, Iterator

from fino_filing import EDINETFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edinet import EdinetConfig, EdinetCollector


class TestEdinetCollector:
    """EdinetCollector: collect フローと add_to_collection"""

    def test_collect_adds_edinet_filing_to_collection(
        self,
        temp_collection: tuple,
        sample_edinet_raw_document: RawDocument,
        edinet_config: EdinetConfig,
    ) -> None:
        """fetch_documents が 1 件返すとき collect() で 1 件が Collection に add される"""
        from fino_filing.collection.collection import Collection

        collection: Collection = temp_collection[0]

        class OneDocCollector(EdinetCollector):
            def fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
                yield sample_edinet_raw_document

        collector = OneDocCollector(collection=collection, config=edinet_config)
        results = collector.collect(date_from="2024-01-01")

        assert len(results) == 1
        filing, path = results[0]
        assert isinstance(filing, EDINETFiling)
        assert filing.source == "EDINET"
        assert filing.doc_id == sample_edinet_raw_document.meta["doc_id"]
        assert filing.filer_name == sample_edinet_raw_document.meta["filer_name"]
        assert path
        got = collection.get_filing(filing.id)
        assert got is not None
        assert got.doc_id == filing.doc_id
        content = collection.get_content(filing.id)
        assert content == sample_edinet_raw_document.content
