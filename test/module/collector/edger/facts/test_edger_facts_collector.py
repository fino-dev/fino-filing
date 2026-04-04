"""EdgarFactsCollector の collect フローと RawDocument / Filing 連携を検証する"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from fino_filing.collector.edgar import EdgarConfig, EdgarFactsCollector

from fino_filing import EDGARCompanyFactsFiling
from fino_filing.collection.collection import Collection
from fino_filing.collector.base import RawDocument
from fino_filing.collector.error import (
    CollectorNoContentError,
    CollectorParseResponseValidationError,
)
from fino_filing.util.content import sha256_checksum


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarFactsCollector:
    """EdgarFactsCollector Test"""

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgarFactsCollector(collection=collection, config=edgar_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"

    class TestFetchDocuments:
        """EdgarFactsCollector._fetch_documents Test"""

        def test_fetch_documents_returns_raw_documents(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
            edgar_company_facts_response_apple: dict[str, Any],
        ) -> None:
            """
            Submissions と Company Facts が取得できる場合、meta を付与した RawDocument を yield する。
            """
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_company_facts.return_value = (
                edgar_company_facts_response_apple
            )
            collector._client = mock_client

            results = list(
                collector._fetch_documents(cik_list=["320193"]),
            )

            assert len(results) == 1
            mock_client.get_submissions.assert_called_once_with("320193")
            mock_client.get_company_facts.assert_called_once_with("320193")
            assert isinstance(results[0], RawDocument)
            expected_content = json.dumps(
                edgar_company_facts_response_apple, ensure_ascii=False
            ).encode()
            assert results[0].content == expected_content
            assert results[0].meta["cik"] == "0000320193"
            assert results[0].meta["entityType"] == "operating"
            assert results[0].meta["name"] == "Apple Inc."
            assert results[0].meta["sic"] == "3571"
            assert results[0].meta["sicDescription"] == "Electronic Computers"
            assert results[0].meta["category"] == "Large accelerated filer"
            assert results[0].meta["fiscalYearEnd"] == "0926"
            assert results[0].meta["stateOfIncorporation"] == "CA"
            assert results[0].meta["tickers"] == ["AAPL"]
            assert results[0].meta["exchanges"] == ["Nasdaq"]

        def test_fetch_documents_returns_empty_iterator(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """cik_list が空のとき _fetch_documents は要素を yield しない"""
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            assert list(collector._fetch_documents(cik_list=[])) == []

        def test_fetch_documents_raises_when_no_submissions(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_company_facts_response_apple: dict[str, Any],
        ) -> None:
            """Submissions が空のとき CollectorNoContentError を送出する"""
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = {}
            mock_client.get_company_facts.return_value = (
                edgar_company_facts_response_apple
            )
            collector._client = mock_client

            with pytest.raises(CollectorNoContentError) as exc:
                list(collector._fetch_documents(cik_list=["0000320193"]))
            assert exc.value.content_id == "0000320193"

        def test_fetch_documents_raises_when_no_facts(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """Company Facts が空のとき CollectorNoContentError を送出する"""
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_company_facts.return_value = {}
            collector._client = mock_client

            with pytest.raises(CollectorNoContentError) as exc:
                list(collector._fetch_documents(cik_list=["0000320193"]))
            assert exc.value.content_id == "0000320193"

    class TestParseResponse:
        """EdgarFactsCollector._parse_response Test"""

        def test_parse_response_normalizes_meta(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
            edgar_company_facts_response_apple: dict[str, Any],
        ) -> None:
            """EdgarFactsCollector._parse_response が meta を正規化する"""

            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_company_facts.return_value = (
                edgar_company_facts_response_apple
            )
            collector._client = mock_client

            iter_collect = collector._fetch_documents(cik_list=["320193"])
            rawDocument = next(iter_collect)

            parsed = collector._parse_response(
                RawDocument(content=rawDocument.content, meta=rawDocument.meta)
            )
            assert parsed["cik"] == "0000320193"
            assert parsed["entity_type"] == "operating"
            assert parsed["filer_name"] == "Apple Inc."
            assert parsed["sic"] == "3571"
            assert parsed["sic_description"] == "Electronic Computers"
            assert parsed["filer_category"] == "Large accelerated filer"
            assert parsed["fiscal_year_end"] == "0926"
            assert parsed["state_of_incorporation"] == "CA"
            assert parsed["tickers"] == ["AAPL"]
            assert parsed["exchanges"] == ["Nasdaq"]

    class TestBuildFiling:
        """EdgarFactsCollector._build_filing Test"""

        def test_build_filing_normalizes_filing(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
            edgar_company_facts_response_apple: dict[str, Any],
        ) -> None:
            """EdgarFactsCollector._build_filing が EDGARCompanyFactsFiling を組み立てる"""
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)

            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_company_facts.return_value = (
                edgar_company_facts_response_apple
            )
            collector._client = mock_client

            iter_collect = collector._fetch_documents(cik_list=["320193"])
            rawDocument = next(iter_collect)
            parsed = collector._parse_response(
                RawDocument(
                    content=rawDocument.content,
                    meta=rawDocument.meta,
                )
            )
            filing = collector._build_filing(parsed, rawDocument.content)
            assert isinstance(filing, EDGARCompanyFactsFiling)
            assert filing.source == "EDGAR"
            assert filing.name == EDGARCompanyFactsFiling.build_default_name(
                "0000320193"
            )
            assert filing.checksum == sha256_checksum(rawDocument.content)
            assert filing.format == "json"
            assert not filing.is_zip
            assert filing.cik == "0000320193"
            assert filing.entity_type == "operating"
            assert filing.filer_name == "Apple Inc."
            assert filing.sic == "3571"
            assert filing.sic_description == "Electronic Computers"
            assert filing.filer_category == "Large accelerated filer"
            assert filing.fiscal_year_end == "0926"
            assert filing.state_of_incorporation == "CA"
            assert filing.tickers_key == "AAPL"
            assert filing.exchanges_key == "Nasdaq"

        def test_build_filing_requires_cik(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """cik が無い Parsed に対して CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarFactsCollector(collection=collection, config=edgar_config)
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing({"filer_name": "Apple Inc."}, b"{}")
            assert exc.value.field == "cik"
