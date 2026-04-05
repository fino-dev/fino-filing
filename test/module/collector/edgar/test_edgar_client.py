"""EdgarClient の各 get メソッドを検証する（モック利用）"""

from typing import Any
from unittest.mock import MagicMock

import pytest
from fino_filing.collector.edgar import EdgarClient, EdgarConfig

from fino_filing.collector._http_client import HttpClient, HttpClientConfig


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarClient:
    """EdgarClient Test"""

    def test_edgar_sec_api_base_url(self) -> None:
        """EdgarClient._SEC_API_BASE が data.sec.gov であることを確認する"""
        assert EdgarClient._SEC_API_BASE == "https://data.sec.gov"

    def test_edgar_archives_base_url(self) -> None:
        """EdgarClient._ARCHIVES_BASE が Archives のベース URL であることを確認する"""
        assert EdgarClient._ARCHIVES_BASE == "https://www.sec.gov/Archives/edgar"

    class TestConstruction:
        """TestEdgarClient.Construction Test"""

        def test_edgar_client_initialize_with_http_client_configure(self) -> None:
            """EdgarClient の初期化 config が HttpClient に反映される"""
            config = EdgarConfig(
                user_agent_email="test@example.com",
                rate_limit_delay=100.2,
                max_retries=100,
                timeout=100,
            )
            client = EdgarClient(config=config)
            assert client._headers == {"User-Agent": "test@example.com"}
            assert client._http_client.rate_limit_delay == 100.2
            assert client._http_client.max_retries == 100
            assert client._http_client.timeout == 100

        def test_edgar_client_initialize_with_http_client(self) -> None:
            """EdgarClient の初期化時に HttpClient を注入できる"""
            config = EdgarConfig(
                user_agent_email="test@example.com",
                rate_limit_delay=100.2,
                max_retries=100,
                timeout=100,
            )
            http_client = HttpClient(HttpClientConfig())
            client = EdgarClient(config=config, _http_client=http_client)
            assert client._headers == {"User-Agent": "test@example.com"}
            assert client._http_client == http_client

    class TestGetSubmissions:
        """TestEdgarClient.GetSubmissions Test"""

        def test_get_submissions_url_headers(
            self, edgar_submissions_response_apple: dict[str, Any]
        ) -> None:
            """get_submissions の URL / headers が正しく、モック応答がそのまま返る（Apple 形状スナップショット）"""
            http_client_mock = MagicMock()
            http_client_mock.get.return_value = edgar_submissions_response_apple

            config = EdgarConfig(user_agent_email="agent@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_submissions("320193")

            http_client_mock.get.assert_called_once()
            assert result == edgar_submissions_response_apple
            assert result["cik"] == "0000320193"
            assert result["name"] == "Apple Inc."
            assert result["tickers"] == ["AAPL"]
            recent = result["filings"]["recent"]
            assert len(recent["accessionNumber"]) == 5
            assert recent["accessionNumber"][0] == "0000102909-26-000630"
            assert http_client_mock.get.call_args[0][0] == (
                "https://data.sec.gov/submissions/CIK0000320193.json"
            )
            assert http_client_mock.get.call_args[1]["headers"] == {
                "User-Agent": "agent@example.com",
            }

    class TestGetCompanyFacts:
        """TestEdgarClient.GetCompanyFacts Test"""

        def test_get_company_facts_url_headers(
            self, edgar_company_facts_response_apple: dict[str, Any]
        ) -> None:
            """get_company_facts の URL / headers が正しく、モック応答がそのまま返る（Apple 形状スナップショット）"""
            http_client_mock = MagicMock()
            http_client_mock.get.return_value = edgar_company_facts_response_apple

            config = EdgarConfig(user_agent_email="facts@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_company_facts("0000320193")

            http_client_mock.get.assert_called_once()
            assert result == edgar_company_facts_response_apple
            assert result["cik"] == 320193
            assert result["entityName"] == "Apple Inc."
            shares = result["facts"]["dei"]["EntityCommonStockSharesOutstanding"][
                "units"
            ]["shares"]
            assert len(shares) == 5
            assert shares[0]["val"] == 895816758
            assert shares[0]["form"] == "10-Q"
            assert http_client_mock.get.call_args[0][0] == (
                "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
            )
            assert http_client_mock.get.call_args[1]["headers"] == {
                "User-Agent": "facts@example.com",
            }

    class TestGetFilingDocument:
        """TestEdgarClient.GetFilingDocument Test"""

        def test_get_filing_document_url_headers(self) -> None:
            """get_filing_document の URL と headers が正しくリクエストされる"""
            http_client_mock = MagicMock()
            http_client_mock.get_raw.return_value = b"<html>index</html>"

            config = EdgarConfig(user_agent_email="docs@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_filing_document("320193", "0000320193-23-000106")

            http_client_mock.get_raw.assert_called_once()
            assert result == b"<html>index</html>"
            assert http_client_mock.get_raw.call_args[0][0] == (
                "https://www.sec.gov/Archives/edgar/data/"
                "0000320193/000032019323000106/0000320193-23-000106-index.htm"
            )
            assert http_client_mock.get_raw.call_args[1]["headers"] == {
                "User-Agent": "docs@example.com",
            }

        def test_get_archives_file_url_encodes_path_segments(self) -> None:
            """get_archives_file がサブディレクトリ付き相対パスをセグメントごとに URL エンコードする"""
            http_client_mock = MagicMock()
            http_client_mock.get_raw.return_value = b"xml"

            config = EdgarConfig(user_agent_email="docs2@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_archives_file(
                "320193",
                "0000320193-23-000106",
                "xslF345X05/wk-form4_1.xml",
            )

            assert result == b"xml"
            http_client_mock.get_raw.assert_called_once()
            assert http_client_mock.get_raw.call_args[0][0] == (
                "https://www.sec.gov/Archives/edgar/data/"
                "0000320193/000032019323000106/xslF345X05/wk-form4_1.xml"
            )

    class TestGetBulk:
        """TestEdgarClient.GetBulk Test"""

        def test_get_bulk_company_facts_url(self) -> None:
            """get_bulk(company_facts) の URL と headers が正しい"""
            http_client_mock = MagicMock()
            http_client_mock.get_raw.return_value = b"ZIP"

            config = EdgarConfig(user_agent_email="bulk@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_bulk("company_facts")

            http_client_mock.get_raw.assert_called_once()
            assert result == b"ZIP"
            assert http_client_mock.get_raw.call_args[0][0] == (
                "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
            )
            assert http_client_mock.get_raw.call_args[1]["headers"] == {
                "User-Agent": "bulk@example.com",
            }

        def test_get_bulk_submissions_url(self) -> None:
            """get_bulk(submissions) の URL と headers が正しい"""
            http_client_mock = MagicMock()
            http_client_mock.get_raw.return_value = b"ZIP"

            config = EdgarConfig(user_agent_email="bulk2@example.com")
            client = EdgarClient(config=config, _http_client=http_client_mock)

            result = client.get_bulk("submissions")

            http_client_mock.get_raw.assert_called_once()
            assert result == b"ZIP"
            assert http_client_mock.get_raw.call_args[0][0] == (
                "https://www.sec.gov/Archives/edgar/"
                "daily-index/bulkdata/submissions.zip"
            )
            assert http_client_mock.get_raw.call_args[1]["headers"] == {
                "User-Agent": "bulk2@example.com",
            }
