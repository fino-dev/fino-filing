"""EdinetCollector の collect フローと Collection 連携を検証する"""

from datetime import date
from typing import Any, Iterator

import pytest

from fino_filing import EDINETFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.error import CollectorDateRangeValidationError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
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
        results = collector.collect(
            date_from=date(2024, 1, 1), date_to=date(2024, 1, 2)
        )

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

    def test_collect_raises_error_when_date_from_is_greater_than_date_to(
        self,
        temp_collection: tuple,
        edinet_config: EdinetConfig,
    ) -> None:
        """date_from が date_to より大きいときエラーを返す"""
        from fino_filing.collection.collection import Collection

        collection: Collection = temp_collection[0]
        collector = EdinetCollector(collection=collection, config=edinet_config)
        with pytest.raises(CollectorDateRangeValidationError):
            collector.collect(date_from=date(2024, 1, 2), date_to=date(2024, 1, 1))
