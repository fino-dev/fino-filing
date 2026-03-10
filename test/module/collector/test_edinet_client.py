"""EdinetClient の get_document_list / get_document を検証する（モック利用）"""

import json
from unittest.mock import patch

import pytest

from fino_filing.collector.edinet import EdinetClient, EdinetConfig


class TestEdinetClient:
    """EdinetClient: 書類一覧・書類取得のリクエスト実行"""

    def test_get_document_list_returns_parsed_json(
        self, edinet_config: EdinetConfig
    ) -> None:
        """get_document_list は JSON レスポンスをそのまま返す"""
        client = EdinetClient(edinet_config)
        body = {"metadata": {"totalCount": 1}, "results": [{"docID": "S100XXX", "filerName": "Test"}]}
        with (
            patch("fino_filing.collector.edinet.client.time.sleep"),
            patch("fino_filing.collector.edinet.client.urlopen") as m_urlopen,
        ):
            m_urlopen.return_value.__enter__.return_value.read.return_value = (
                json.dumps(body).encode()
            )
            result = client.get_document_list("2024-01-01", type=1)
        assert result == body
        assert result.get("results")[0]["docID"] == "S100XXX"

    def test_get_document_list_failure_returns_empty_dict(
        self, edinet_config: EdinetConfig
    ) -> None:
        """get_document_list 失敗時は空 dict を返す"""
        from urllib.error import HTTPError

        client = EdinetClient(edinet_config)
        with (
            patch("fino_filing.collector.edinet.client.time.sleep"),
            patch("fino_filing.collector.edinet.client.urlopen") as m_urlopen,
        ):
            m_urlopen.side_effect = HTTPError("https://example.com", 500, "Error", {}, None)
            result = client.get_document_list("2024-01-01")
        assert result == {}

    def test_get_document_returns_bytes(
        self, edinet_config: EdinetConfig
    ) -> None:
        """get_document は書類実体を bytes で返す"""
        client = EdinetClient(edinet_config)
        content = b"%PDF-1.4 sample"
        with (
            patch("fino_filing.collector.edinet.client.time.sleep"),
            patch("fino_filing.collector.edinet.client.urlopen") as m_urlopen,
        ):
            m_urlopen.return_value.__enter__.return_value.read.return_value = content
            result = client.get_document("S100ABCD1234567890", type=1)
        assert result == content

    def test_get_document_failure_returns_empty_bytes(
        self, edinet_config: EdinetConfig
    ) -> None:
        """get_document 失敗時は空 bytes を返す"""
        from urllib.error import HTTPError

        client = EdinetClient(edinet_config)
        with (
            patch("fino_filing.collector.edinet.client.time.sleep"),
            patch("fino_filing.collector.edinet.client.urlopen") as m_urlopen,
        ):
            m_urlopen.side_effect = HTTPError("https://example.com", 404, "Not Found", {}, None)
            result = client.get_document("S100NONEXISTENT")
        assert result == b""
