"""EdinetClient の get_document_list / get_document を検証する（モック利用）"""

from datetime import date
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.edinet import EdinetClient, EdinetConfig


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetClient:
    """
    EdinetClient Test
    """

    def test_edinet_api_base_url(self) -> None:
        """
        EdinetClient._EDINET_API_BASE が V2のURL であることを確認する
        """

        assert EdinetClient._EDINET_API_BASE == "https://api.edinet-fsa.go.jp/api/v2"

    def test_edinet_client_initialize_with_http_client_configure(self) -> None:
        """EdinetClientの初期化config設定がHttpClient に設定される"""
        config = EdinetConfig(
            api_key="test-api-key",
            rate_limit_delay=100.2,
            max_retries=100,
            timeout=100,
        )

        client = EdinetClient(config=config)
        assert client._credential == "test-api-key"
        assert client._http_client.rate_limit_delay == 100.2
        assert client._http_client.max_retries == 100
        assert client._http_client.timeout == 100

    def test_edinet_client_initialize_with_http_client(self) -> None:
        """EdinetClientの初期化時にHttpClient を渡して注入できる"""
        config = EdinetConfig(
            api_key="test-api-key",
            rate_limit_delay=100.2,
            max_retries=100,
            timeout=100,
        )
        http_client = HttpClient(HttpClientConfig())
        client = EdinetClient(config=config, _http_client=http_client)
        assert client._credential == "test-api-key"
        assert client._http_client == http_client


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetClient_GetDocumentList:
    """EdinetClient.get_document_list Test"""

    def test_get_document_list_url_params(
        self, edinet_document_list_response_type1: dict[str, Any]
    ) -> None:
        """get_document_list の URL と params が正しクリクエストされていることを確認する"""
        http_client_mock = MagicMock()
        http_client_mock.get.return_value = edinet_document_list_response_type1

        config = EdinetConfig(api_key="test-api-key")
        client = EdinetClient(config=config, _http_client=http_client_mock)

        target_date = date(2025, 4, 1)

        result = client.get_document_list(target_date, type=1)

        #  Confirm response is not modified
        http_client_mock.get.assert_called_once()
        assert result == edinet_document_list_response_type1

        # Confirm http client's get function is called with correct URL and params
        assert http_client_mock.get.call_args[0][0] == (
            "https://api.edinet-fsa.go.jp/api/v2/documents.json"
        )
        assert http_client_mock.get.call_args[1]["params"] == {
            "Subscription-Key": "test-api-key",
            "date": "2025-04-01",
            "type": 1,
        }


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetClient_GetDocument:
    """EdinetClient.get_document Test"""

    def test_get_document_url_params(self) -> None:
        """get_document の URL と params が正しいリクエストされていることを確認する"""
        http_client_mock = MagicMock()
        http_client_mock.get_raw.return_value = b"test-document"

        config = EdinetConfig(api_key="test-api-key")
        client = EdinetClient(config=config, _http_client=http_client_mock)

        target_doc_id = "S100XXX"
        result = client.get_document(target_doc_id, type=1)

        http_client_mock.get_raw.assert_called_once()
        assert result == b"test-document"
        assert http_client_mock.get_raw.call_args[0][0] == (
            "https://api.edinet-fsa.go.jp/api/v2/documents/S100XXX"
        )
        assert http_client_mock.get_raw.call_args[1]["params"] == {
            "Subscription-Key": "test-api-key",
            "type": 1,
        }
