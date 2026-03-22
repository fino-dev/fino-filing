"""EdinetClient の get_document_list / get_document を検証する（モック利用）"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from fino_filing.collector.edinet import EdinetClient, EdinetConfig


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetClient:
    """EdinetClient: 書類一覧・書類取得のリクエスト実行"""

    def test_get_document_list_returns_parsed_json(
        self, edinet_config: EdinetConfig
    ) -> None:
        """get_document_list は JSON レスポンスをそのまま返す"""
        body = {
            "metadata": {"totalCount": 1},
            "results": [{"docID": "S100XXX", "filerName": "Test"}],
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = body
        mock_resp.raise_for_status = MagicMock()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = EdinetClient(edinet_config)
            result = client.get_document_list(date(2024, 1, 1), type=1)

        assert result == body
        assert result.get("results", [])[0]["docID"] == "S100XXX"

    def test_get_document_returns_bytes(self, edinet_config: EdinetConfig) -> None:
        """get_document は書類実体を bytes で返す"""
        content = b"%PDF-1.4 sample"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = content
        mock_resp.raise_for_status = MagicMock()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = EdinetClient(edinet_config)
            result = client.get_document("S100ABCD1234567890", type=1)

        assert result == content

    def test_get_document_list_uses_documents_json_url_and_params(
        self, edinet_config: EdinetConfig
    ) -> None:
        """一覧 API の URL・Subscription-Key・date・type が HttpClient に渡る"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp) as m_get,
        ):
            client = EdinetClient(edinet_config)
            client.get_document_list(date(2024, 6, 1), type=2)

        m_get.assert_called_once()
        assert m_get.call_args[0][0] == (
            "https://api.edinet-fsa.go.jp/api/v2/documents.json"
        )
        assert m_get.call_args[1]["params"] == {
            "Subscription-Key": "test-api-key",
            "date": "2024-06-01",
            "type": 2,
        }

    def test_get_document_uses_document_path_and_params(
        self, edinet_config: EdinetConfig
    ) -> None:
        """書類取得 API の URL・Subscription-Key・type が HttpClient に渡る"""
        doc_id = "S100ABCD1234567890"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"x"
        mock_resp.raise_for_status = MagicMock()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp) as m_get,
        ):
            client = EdinetClient(edinet_config)
            client.get_document(doc_id, type=5)

        m_get.assert_called_once()
        assert m_get.call_args[0][0] == (
            f"https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        )
        assert m_get.call_args[1]["params"] == {
            "Subscription-Key": "test-api-key",
            "type": 5,
        }
