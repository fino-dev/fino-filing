"""EdgarBulkCollector の collect フローと RawDocument / Filing 連携を検証する"""

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fino_filing import Collection, EdgarBulkFiling
from fino_filing.collector.base import Parsed, RawDocument
from fino_filing.collector.edgar import EdgarBulkCollector, EdgarConfig
from fino_filing.collector.edgar.bulk.enum import EdgarBulkType
from fino_filing.collector.error import CollectorParseResponseValidationError
from fino_filing.util.content import sha256_checksum


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarBulkCollector:
    """EdgarBulkCollector Test"""

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgarBulkCollector(collection=collection, config=edgar_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"

    class TestFetchDocuments:
        """EdgarBulkCollector._fetch_documents Test"""

        def test_fetch_documents_returns_raw_document_for_company_facts(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """COMPANY_FACTS のとき get_bulk('companyfacts') の本文とメタを yield する"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            payload = b"PK\x03\x04fake-zip"
            mock_client.get_bulk.return_value = payload
            collector._client = mock_client
            fixed_date = date(2026, 4, 5)
            with patch(
                "fino_filing.collector.edgar.bulk.collector.date"
            ) as mock_date_mod:
                mock_date_mod.today.return_value = fixed_date
                results = list(
                    collector._fetch_documents(
                        bulk_type=EdgarBulkType.COMPANY_FACTS,
                    )
                )

            assert len(results) == 1
            mock_client.get_bulk.assert_called_once_with("companyfacts")
            assert isinstance(results[0], RawDocument)
            assert results[0].content == payload
            assert results[0].meta["bulk_type"] == EdgarBulkType.COMPANY_FACTS.value
            assert results[0].meta["bulk_date"] == fixed_date

        def test_fetch_documents_calls_submissions_bulk(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """SUBMISSIONS のとき get_bulk('submissions') を呼ぶ"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            mock_client.get_bulk.return_value = b"z"
            collector._client = mock_client
            fixed_date = date(2026, 1, 2)
            with patch(
                "fino_filing.collector.edgar.bulk.collector.date"
            ) as mock_date_mod:
                mock_date_mod.today.return_value = fixed_date
                list(
                    collector._fetch_documents(
                        bulk_type=EdgarBulkType.SUBMISSIONS,
                    )
                )

            mock_client.get_bulk.assert_called_once_with("submissions")

    class TestParseResponse:
        """EdgarBulkCollector._parse_response Test"""

        def test_parse_response_normalizes_meta(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """_parse_response が bulk_type / bulk_date をそのまま Parsed に載せる"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            fixed_date = date(2026, 6, 15)
            raw = RawDocument(
                content=b"x",
                meta={
                    "bulk_type": EdgarBulkType.SUBMISSIONS.value,
                    "bulk_date": fixed_date,
                },
            )
            parsed = collector._parse_response(raw)
            assert parsed["bulk_type"] == EdgarBulkType.SUBMISSIONS.value
            assert parsed["bulk_date"] == fixed_date

    class TestBuildFiling:
        """EdgarBulkCollector._build_filing Test"""

        def test_build_filing_creates_edgar_bulk_filing(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """EdgarBulkCollector._build_filing が EdgarBulkFiling を組み立てる"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            body = b"bulk-zip-bytes"
            bulk_date = date(2026, 3, 20)
            parsed: Parsed = {
                "bulk_type": EdgarBulkType.COMPANY_FACTS.value,
                "bulk_date": bulk_date,
            }
            filing = collector._build_filing(parsed, body)
            assert isinstance(filing, EdgarBulkFiling)
            assert filing.source == "EDGAR"
            assert filing.edgar_resource_kind == "bulk"
            assert filing.bulk_type == "companyfacts"
            assert filing.bulk_date == bulk_date
            assert filing.checksum == sha256_checksum(body)
            assert filing.name == EdgarBulkFiling.build_default_name(
                "companyfacts", bulk_date
            )

        def test_build_filing_requires_bulk_type(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """bulk_type が無い Parsed に対して CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing(
                    {"bulk_date": date(2026, 1, 1)},
                    b"x",
                )
            assert exc.value.field == "bulk_type"

        def test_build_filing_requires_bulk_date(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """bulk_date が無い Parsed に対して CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarBulkCollector(collection=collection, config=edgar_config)
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing(
                    {"bulk_type": EdgarBulkType.COMPANY_FACTS.value},
                    b"x",
                )
            assert exc.value.field == "bulk_date"
