"""EdinetCollector の collect フローと Collection 連携を検証する"""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from fino_filing.collection.collection import Collection
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.error import CollectorDateRangeValidationError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetCollector:
    """EdinetCollector Test"""

    def test_collector_initialize_with_config(
        self, temp_collection: tuple[Collection, Path]
    ) -> None:
        """Collector の初期化が config を渡してclientを注入できる"""
        collection, _ = temp_collection
        collector = EdinetCollector(
            collection=collection, config=EdinetConfig(api_key="test-api-key")
        )
        assert collector._client._credential == "test-api-key"

    def test_fetch_documents_returns_raw_documents(
        self,
        temp_collection: tuple[Collection, Path],
        tmp_edinet_config: EdinetConfig,
    ) -> None:
        """EdinetCollector._fetch_documents のテスト"""
        collection, _ = temp_collection
        collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
        results = collector._fetch_documents(
            date_from=date(2024, 1, 1), date_to=date(2024, 1, 2)
        )

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
