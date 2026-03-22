"""HttpClient / HttpClientConfig / request_json の単体テスト（モック利用）"""

import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
import requests
from urllib.error import HTTPError, URLError

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.error import (
    HttpAuthenticationError,
    HttpNotFoundError,
    HttpRateLimitError,
    HttpRequestError,
)


@pytest.mark.module
@pytest.mark.collector
class TestHttpClient:
    """HttpClient: GET JSON / raw / ステータス別の例外 / レート制限"""

    def _success_json_response(self, data: dict[str, Any]) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = data
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    def test_get_returns_parsed_json(self) -> None:
        """get は 200 の JSON を dict で返す"""
        body = {"ok": True}
        mock_resp = self._success_json_response(body)
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp) as m_get,
        ):
            client = HttpClient(config)
            result = client.get("https://example.com/api", params={"q": "1"})

        assert result == body
        m_get.assert_called_once()
        assert m_get.call_args[0][0] == "https://example.com/api"
        assert m_get.call_args[1]["params"] == {"q": "1"}
        assert m_get.call_args[1]["timeout"] == 5

    def test_get_raises_rate_limit_on_429(self) -> None:
        """get は 429 で HttpRateLimitError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRateLimitError):
                client.get("https://example.com/")

    def test_get_raises_auth_on_401(self) -> None:
        """get は 401 で HttpAuthenticationError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpAuthenticationError):
                client.get("https://example.com/")

    def test_get_raises_not_found_on_404(self) -> None:
        """get は 404 で HttpNotFoundError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)
        url = "https://example.com/missing"

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpNotFoundError) as exc_info:
                client.get(url)
        assert exc_info.value.url == url

    def test_get_wraps_request_exception_as_http_request_error(self) -> None:
        """get は session.get の接続失敗などを HttpRequestError に包む"""
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch(
                "requests.Session.get",
                side_effect=requests.ConnectionError("boom"),
            ),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRequestError) as exc_info:
                client.get("https://example.com/")
        assert "example.com" in exc_info.value.url

    def test_get_wraps_raise_for_status_failure(self) -> None:
        """get は raise_for_status が失敗した場合 HttpRequestError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = requests.HTTPError(response=mock_resp)
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRequestError):
                client.get("https://example.com/")

    def test_get_raw_returns_content_bytes(self) -> None:
        """get_raw は response.content を返す"""
        content = b"\x00pdf"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = content
        mock_resp.raise_for_status = MagicMock()
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            result = client.get_raw("https://example.com/doc")

        assert result == content

    def test_get_raw_raises_not_found_on_404(self) -> None:
        """get_raw も 404 で HttpNotFoundError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        config = HttpClientConfig(rate_limit_delay=0.0, timeout=5)
        url = "https://example.com/x"

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpNotFoundError):
                client.get_raw(url)

    def test_rate_limit_sleeps_when_interval_too_short(self) -> None:
        """直前リクエストから rate_limit_delay 未満なら sleep する"""
        config = HttpClientConfig(rate_limit_delay=10.0, timeout=5)
        mock_resp = self._success_json_response({})

        time_seq = [1000.0, 1000.0, 1000.5, 1000.5, 1000.5]

        with (
            patch(
                "fino_filing.collector._http_client.time.time",
                side_effect=time_seq,
            ),
            patch("fino_filing.collector._http_client.time.sleep") as m_sleep,
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            client.get("https://example.com/a")
            client.get("https://example.com/b")

        m_sleep.assert_called_once()
        assert m_sleep.call_args[0][0] == 9.5


@pytest.mark.module
@pytest.mark.collector
class TestHttpClientRequestJson:
    """HttpClient.request_json（urllib）"""

    def test_request_json_returns_parsed_body(self) -> None:
        """成功時は JSON を dict で返す"""
        payload = {"items": [1]}
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value.read.return_value = json.dumps(payload).encode()

        with patch(
            "fino_filing.collector._http_client.urlopen",
            return_value=mock_cm,
        ):
            result = HttpClient.request_json(
                "https://example.com/j",
                {"X-Foo": "bar"},
                10,
            )

        assert result == payload

    def test_request_json_returns_empty_dict_on_http_error(self) -> None:
        """HTTP エラー時は空 dict"""
        with patch(
            "fino_filing.collector._http_client.urlopen",
            side_effect=HTTPError("https://x", 500, "err", cast(Any, {}), None),
        ):
            result = HttpClient.request_json("https://x", {}, 5)
        assert result == {}

    def test_request_json_returns_empty_dict_on_url_error(self) -> None:
        """接続エラー時は空 dict"""
        with patch(
            "fino_filing.collector._http_client.urlopen",
            side_effect=URLError("reason"),
        ):
            result = HttpClient.request_json("https://x", {}, 5)
        assert result == {}

    def test_request_json_returns_empty_dict_on_invalid_json(self) -> None:
        """本文が JSON でない場合は空 dict"""
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value.read.return_value = b"not json"

        with patch(
            "fino_filing.collector._http_client.urlopen",
            return_value=mock_cm,
        ):
            result = HttpClient.request_json("https://example.com/", {}, 5)
        assert result == {}
