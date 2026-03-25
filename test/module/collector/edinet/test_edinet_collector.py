"""EdinetCollector の collect フローと Collection 連携を検証する"""

from datetime import date
from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest

from fino_filing import EDINETFiling
from fino_filing.collection.collection import Collection
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.error import CollectorDateRangeValidationError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetCollector:
    """EdinetCollector Test"""

    def test_collect_adds_edinet_filing_to_collection(
        self,
        temp_collection: tuple,
        sample_edinet_raw_document: RawDocument,
        tmp_edinet_config: EdinetConfig,
    ) -> None:
        """fetch_documents が 1 件返すとき collect() で 1 件が Collection に add される"""
        collection: Collection = temp_collection[0]

        class OneDocCollector(EdinetCollector):
            def fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
                yield sample_edinet_raw_document

        collector = OneDocCollector(collection=collection, config=tmp_edinet_config)
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
        tmp_edinet_config: EdinetConfig,
    ) -> None:
        """date_from が date_to より大きいときエラーを返す"""
        collection: Collection = temp_collection[0]
        collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
        with pytest.raises(CollectorDateRangeValidationError):
            collector.collect(date_from=date(2024, 1, 2), date_to=date(2024, 1, 1))

    def test_collect_parses_list_api_keys_in_parse_response(
        self,
        temp_collection: tuple,
        tmp_edinet_config: EdinetConfig,
    ) -> None:
        collection: Collection = temp_collection[0]
        collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
        mock_client = MagicMock()
        collector._client = mock_client
        mock_client.get_document_list.return_value = {
            "results": [
                {
                    "docID": "S100APIKEY",
                    "filerName": "提出者カナメ",
                    "edinetCode": "E99999",
                }
            ]
        }
        mock_client.get_document.return_value = b"%PDF-1.4"

        results = collector.collect(
            date_from=date(2024, 8, 1), date_to=date(2024, 8, 1)
        )
        assert len(results) == 1
        filing, _path = results[0]
        assert filing.doc_id == "S100APIKEY"
        assert filing.filer_name == "提出者カナメ"
        assert filing.edinet_code == "E99999"
