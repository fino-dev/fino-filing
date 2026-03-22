"""HttpClient / HttpClientConfig / request_json の単体テスト（モック利用）"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.error import (
    HttpAuthenticationError,
    HttpNotFoundError,
    HttpRateLimitError,
    HttpRequestError,
)


def _success_json_response(data: dict[str, Any]) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@pytest.mark.module
@pytest.mark.collector
class TestHttpClientConfig:
    """HttpClientConfig Test"""

    def test_default_config(self) -> None:
        """constructorでデフォルト値が設定された HttpClientConfig を返す"""
        config = HttpClientConfig()
        assert config.rate_limit_delay == 0.1
        assert config.timeout == 30
        assert config.retry_status_codes == [429, 500, 502, 503, 504]
        assert config.retry_methods == ["GET"]
        assert config.retry_backoff_factor == 1.0
        assert config.max_retries == 3

    def test_from_dict_returns_config(self) -> None:
        """from_dict でデフォルト値が設定された HttpClientConfig を返す"""
        config = HttpClientConfig.from_dict()
        assert config.rate_limit_delay == 0.1
        assert config.timeout == 30
        assert config.retry_status_codes == [429, 500, 502, 503, 504]
        assert config.retry_methods == ["GET"]
        assert config.retry_backoff_factor == 1.0
        assert config.max_retries == 3

    def test_from_dict_overrides_default_values(self) -> None:
        """from_dict でデフォルト値を上書きできる"""
        config = HttpClientConfig.from_dict(
            {
                "rate_limit_delay": 0.2,
                "timeout": 60,
                "retry_status_codes": [401, 403],
                "retry_methods": ["POST"],
                "retry_backoff_factor": 2.0,
                "max_retries": 5,
            }
        )
        assert config.rate_limit_delay == 0.2
        assert config.timeout == 60
        assert config.retry_status_codes == [401, 403]
        assert config.retry_methods == ["POST"]
        assert config.retry_backoff_factor == 2.0
        assert config.max_retries == 5


@pytest.mark.module
@pytest.mark.collector
class TestHttpClient_RateLimit:
    """HttpClient._rate_limit Test"""

    def test_no_sleep_when_interval_sufficient(self) -> None:
        """直前リクエストから rate_limit_delay 以上の間隔があれば sleep しない"""
        fake_now = 1015.0
        delay = 10.0
        last_request = 1000.0

        with (
            patch(
                "fino_filing.collector._http_client.time.time", return_value=fake_now
            ),
            patch("fino_filing.collector._http_client.time.sleep") as mock_sleep,
        ):
            client = HttpClient(HttpClientConfig())
            client._rate_limit(delay, last_request)

        mock_sleep.assert_not_called()

    def test_updates_last_request_time(self) -> None:
        """直前リクエストから rate_limit_delay 以上の間隔があれば last_request_time を更新する"""
        fake_now = 1000.5
        delay = 10.0
        last_request = 1000.0

        with (
            patch(
                "fino_filing.collector._http_client.time.time", return_value=fake_now
            ),
            patch("fino_filing.collector._http_client.time.sleep") as mock_sleep,
        ):
            client = HttpClient(HttpClientConfig())
            client._rate_limit(delay, last_request)

        assert client._last_request_time == fake_now
        mock_sleep.assert_called_once_with(
            9.5
        )  # 1000.5 - 1000.0 = 0.5, 10.0 - 0.5 = 9.5

    def test_rate_limit_sleeps_when_interval_too_short(self) -> None:
        """直前リクエストから rate_limit_delay 未満なら sleep する"""
        config = HttpClientConfig(rate_limit_delay=10.0, timeout=5)
        mock_resp = _success_json_response({})

        # time.time() の返り値のシーケンスMOCK
        # 一回の実行で2回呼び出されるため
        time_seq = [1000.0, 1000.0, 1000.5, 1000.5]

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
class TestHttpClient_Get:
    """HttpClient.get Test"""

    def test_get_returns_parsed_json(self) -> None:
        """200 のレスポンスで JSON を dict で返す"""
        body = {"ok": True}
        mock_resp = _success_json_response(body)

        config = HttpClientConfig()

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

    def test_get_raises_rate_limit_on_429(self) -> None:
        """get は 429 で HttpRateLimitError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 429

        config = HttpClientConfig()

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
        config = HttpClientConfig()

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
        config = HttpClientConfig()
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
        config = HttpClientConfig()
        url = "https://example.com/"

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch(
                "requests.Session.get",
                side_effect=requests.ConnectionError("boom"),
            ),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRequestError) as exc_info:
                client.get(url)
        assert exc_info.value.url == url


@pytest.mark.module
@pytest.mark.collector
class TestHttpClient_GetRaw:
    """HttpClient.get_raw Test"""

    def test_get_raw_returns_content_bytes(self) -> None:
        """get_raw は response.content (bytes) を返す"""
        content = b"\x00pdf"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = content
        mock_resp.raise_for_status = MagicMock()
        config = HttpClientConfig()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            result = client.get_raw("https://example.com/doc")

        assert result == content

    def test_get_raw_raises_rate_limit_on_429(self) -> None:
        """get_raw は 429 で HttpRateLimitError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 429

        config = HttpClientConfig()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRateLimitError):
                client.get_raw("https://example.com/")

    def test_get_raw_raises_auth_on_401(self) -> None:
        """get_raw は 401 で HttpAuthenticationError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        config = HttpClientConfig()

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpAuthenticationError):
                client.get_raw("https://example.com/")

    def test_get_raw_raises_not_found_on_404(self) -> None:
        """get_raw は 404 で HttpNotFoundError"""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        config = HttpClientConfig()
        url = "https://example.com/missing"

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch("requests.Session.get", return_value=mock_resp),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpNotFoundError) as exc_info:
                client.get_raw(url)
        assert exc_info.value.url == url

    def test_get_raw_wraps_request_exception_as_http_request_error(self) -> None:
        """get_raw は session.get の接続失敗などを HttpRequestError に包む"""
        config = HttpClientConfig()
        url = "https://example.com/"

        with (
            patch("fino_filing.collector._http_client.time.sleep"),
            patch(
                "requests.Session.get",
                side_effect=requests.ConnectionError("boom"),
            ),
        ):
            client = HttpClient(config)
            with pytest.raises(HttpRequestError) as exc_info:
                client.get_raw(url)
        assert exc_info.value.url == url
