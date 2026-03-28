"""EdinetCollector の collect フローと Collection 連携を検証する"""

from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing.collection.collection import Collection
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.error import (
    CollectorDateRangeValidationError,
    CollectorLimitValidationError,
)


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

    class TestFetchDocuments:
        """EdinetCollector._fetch_documents Test"""

        def test_fetch_documents_returns_raw_documents(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
            edinet_document_list_response_type2_5_items: dict[str, Any],
        ) -> None:
            """EdinetCollector._fetch_documents のテスト"""
            collection, _ = temp_collection
            collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
            mock_client = MagicMock()
            mock_client.get_document_list.return_value = (
                edinet_document_list_response_type2_5_items
            )
            mock_client.get_document.return_value = b"%PDF-1.4 dummy"
            collector._client = mock_client

            results = list(
                collector._fetch_documents(
                    date_from=date(2024, 1, 1), date_to=date(2024, 1, 2)
                )
            )

            # edinet_document_list_response_type2_5_items の場合、2日分のデータが計10件取得される。
            # Collectioに保存しないため重複はこのケースでは許容する
            assert len(results) == 10
            assert mock_client.get_document_list.call_count == 2
            mock_client.get_document_list.assert_any_call(date(2024, 1, 1), type=2)
            mock_client.get_document_list.assert_any_call(date(2024, 1, 2), type=2)
            assert mock_client.get_document.call_count == 10
            assert results[0].meta["docID"] == "S100VIZF"
            assert results[0].content == b"%PDF-1.4 dummy"

        def test_fetch_documents_returns_empty_iterator(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
            edinet_document_list_response_type2_no_items: dict[str, Any],
        ) -> None:
            """EdinetCollector._fetch_documents が空のイテレータを返す"""
            collection, _ = temp_collection
            collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
            mock_client = MagicMock()
            mock_client.get_document_list.return_value = (
                edinet_document_list_response_type2_no_items
            )
            collector._client = mock_client
            results = list(
                collector._fetch_documents(
                    date_from=date(2024, 1, 1), date_to=date(2024, 1, 2)
                )
            )
            assert len(results) == 0
            assert mock_client.get_document_list.call_count == 2
            assert mock_client.get_document.call_count == 0

        def test_fetch_documents_argument_validation(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
        ) -> None:
            """EdinetCollector._fetch_documents の引数バリデーションのテスト"""
            collection, _ = temp_collection
            collector = EdinetCollector(collection=collection, config=tmp_edinet_config)

            # 日付指定が逆転しているケース
            with pytest.raises(CollectorDateRangeValidationError):
                list(
                    collector._fetch_documents(
                        date_from=date(2024, 1, 2), date_to=date(2024, 1, 1)
                    )
                )
            # limit が 0 以下のケース
            with pytest.raises(CollectorLimitValidationError):
                list(
                    collector._fetch_documents(
                        date_from=date(2024, 1, 1), date_to=date(2024, 1, 2), limit=0
                    )
                )

    class TestParseResponse:
        """EdinetCollector._parse_response Test"""

        def test_parse_response_normalizes_meta(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
            edinet_document_list_response_type2_5_items: dict[str, Any],
        ) -> None:
            """EdinetCollector._parse_response が meta を正規化する"""
            collection, _ = temp_collection
            collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
            parsed = collector._parse_response(
                edinet_document_list_response_type2_5_items["results"][0]
            )
            assert parsed["doc_id"] == "S100VIZF"
            assert (
                parsed["edinet_code"]
                == "1000000000000000000000000000000000000000000000000000000000000000"
            )
