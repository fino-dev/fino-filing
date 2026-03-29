"""EdinetCollector の collect フローと Collection 連携を検証する"""

from datetime import date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import EDINETFiling
from fino_filing.collection.collection import Collection
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.edinet.enum import (
    EDINET_DOCUMENT_DOWNLOAD_TYPE,
    EDINET_DOCUMENT_LIST_TYPE,
)
from fino_filing.collector.error import (
    CollectorDateRangeValidationError,
    CollectorLimitValidationError,
)
from fino_filing.util.content import sha256_checksum


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
            """
            Filingを取得できる場合、_document_download_typeをmetaに追加したRawDocumentをyieldする。
            """
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
                    date_from=date(2024, 1, 1),
                    date_to=date(2024, 1, 2),
                    document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV,
                )
            )

            # edinet_document_list_response_type2_5_items の場合、2日分のデータが計10件取得される。
            # Collectioに保存しないため重複はこのケースでは許容する
            assert len(results) == 10
            assert mock_client.get_document_list.call_count == 2
            mock_client.get_document_list.assert_any_call(
                date=date(2024, 1, 1), type=EDINET_DOCUMENT_LIST_TYPE.METADATA_AND_LIST
            )
            mock_client.get_document_list.assert_any_call(
                date=date(2024, 1, 2), type=EDINET_DOCUMENT_LIST_TYPE.METADATA_AND_LIST
            )
            assert mock_client.get_document.call_count == 10
            # 一つ目だけ検証
            mock_client.get_document.assert_any_call(
                doc_id="S100VIZF", type=EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV
            )
            assert isinstance(results[0], RawDocument)
            assert results[0].meta["docID"] == "S100VIZF"
            assert results[0].content == b"%PDF-1.4 dummy"
            assert (
                results[0].meta["_document_download_type"]
                == EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV
            )

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
                    date_from=date(2024, 1, 1),
                    date_to=date(2024, 1, 2),
                    document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF,
                )
            )
            assert len(results) == 0
            assert mock_client.get_document_list.call_count == 2
            assert mock_client.get_document.call_count == 0

        def test_fetch_documents_returns_raw_documents_with_limit(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
            edinet_document_list_response_type2_5_items: dict[str, Any],
        ) -> None:
            """EdinetCollector._fetch_documents が limit を指定して RawDocument をlimit件数分返す"""
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
                    date_from=date(2024, 1, 1),
                    date_to=date(2024, 1, 2),
                    limit=1,
                    document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF,
                )
            )

            assert len(results) == 1
            assert mock_client.get_document_list.call_count == 1
            assert mock_client.get_document.call_count == 1
            mock_client.get_document.assert_any_call(
                doc_id="S100VIZF", type=EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF
            )
            assert isinstance(results[0], RawDocument)
            assert results[0].meta["docID"] == "S100VIZF"
            assert results[0].content == b"%PDF-1.4 dummy"

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
                        date_from=date(2024, 1, 2),
                        date_to=date(2024, 1, 1),
                        document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV,
                    )
                )
            # limit が 0 以下のケース
            with pytest.raises(CollectorLimitValidationError):
                list(
                    collector._fetch_documents(
                        date_from=date(2024, 1, 1),
                        date_to=date(2024, 1, 2),
                        limit=0,
                        document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.ENGLISH_VERSION_FILE,
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
            assert parsed["edinet_code"] == "E06264"
            assert parsed["sec_code"] == None
            assert parsed["jcn"] == "6010001098507"
            assert (
                parsed["filer_name"] == "ＪＰモルガン・アセット・マネジメント株式会社"
            )
            assert parsed["ordinance_code"] == "030"
            assert parsed["form_code"] == "04A000"
            assert parsed["doc_type_code"] == "030"
            assert parsed["doc_description"] == "有価証券届出書（内国投資信託受益証券）"
            assert parsed["period_start"] == None
            assert parsed["period_end"] == None
            assert parsed["submit_datetime"] == datetime(2025, 4, 2, 9, 18)
            assert parsed["parent_doc_id"] == None
            # _fetch_documentsで追加される想定なのでここではNone
            assert parsed["_document_download_type"] == None

    class TestBuildFiling:
        """EdinetCollector._build_filing Test"""

        def test_build_filing_normalizes_filing(
            self,
            temp_collection: tuple[Collection, Path],
            tmp_edinet_config: EdinetConfig,
            edinet_document_list_response_type2_5_items: dict[str, Any],
        ) -> None:
            """EdinetCollector._build_filing が EDINETFiling を組み立てる"""
            collection, _ = temp_collection
            collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
            parsed = collector._parse_response(
                edinet_document_list_response_type2_5_items["results"][0]
            )
            parsed["_document_download_type"] = EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF
            before = datetime.now()
            filing = collector._build_filing(parsed, b"%PDF-1.4 dummy")
            after = datetime.now()
            assert isinstance(filing, EDINETFiling)
            assert filing.source == "EDINET"
            assert filing.name == EDINETFiling.build_name(
                doc_id="S100VIZF",
                doc_description="有価証券届出書（内国投資信託受益証券）",
                format="pdf",
            )
            assert filing.checksum == sha256_checksum(b"%PDF-1.4 dummy")
            assert filing.format == "pdf"
            assert filing.is_zip == False
            assert before <= filing.created_at <= after
            assert filing.doc_id == "S100VIZF"
            assert filing.edinet_code == "E06264"
            assert filing.sec_code == None
            assert filing.jcn == "6010001098507"
            assert filing.filer_name == "ＪＰモルガン・アセット・マネジメント株式会社"
            assert filing.ordinance_code == "030"
            assert filing.form_code == "04A000"
            assert filing.doc_type_code == "030"
            assert filing.doc_description == "有価証券届出書（内国投資信託受益証券）"
            assert filing.period_start == None
            assert filing.period_end == None
            assert filing.submit_datetime == datetime(2025, 4, 2, 9, 18)
            assert filing.parent_doc_id == None
