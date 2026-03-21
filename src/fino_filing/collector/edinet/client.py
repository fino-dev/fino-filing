"""
EDINET 書類一覧API・書類取得API のリクエスト実行を行う HTTP クライアント。
Collector の内部コンポーネントとして使用する。
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fino_filing.collector.edinet.config import EdinetConfig

logger = logging.getLogger(__name__)

# 金融庁 EDINET API v2 の固定ベース URL（Config に api_base は持たない）
_EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
# 短時間の大量リクエストを避けるため 1 リクエストあたりの推奨間隔（秒）
_REQUEST_DELAY_SEC: float = 4.0
_RETRY_503_MAX: int = 3
_RETRY_503_WAIT_SEC: float = 2.0


class EdinetClient:
    """
    EDINET 書類一覧API・書類取得API のリクエスト実行と共通処理を行うクライアント。

    責務:
    - Subscription-Key ヘッダの付与
    - レート制限対策（リクエスト間 delay）
    - 503 時のリトライ
    - 書類一覧取得・書類実体取得のメソッド提供
    """

    def __init__(self, config: EdinetConfig) -> None:
        self._config = config
        self._headers = {"Subscription-Key": config.api_key}

    def get_document_list(self, date: str, type: int = 1) -> dict[str, Any]:
        """
        書類一覧取得API を実行し、レスポンス JSON をそのまま返す。

        date: 提出日（YYYY-MM-DD）。
        type: 1=メタデータのみ、2=メタデータ+書類一覧。デフォルト 1。
        失敗時は空 dict を返す。
        """
        time.sleep(_REQUEST_DELAY_SEC)
        params = urlencode({"date": date, "type": type})
        url = f"{_EDINET_API_BASE}/documents.json?{params}"
        return self._request_json(url)

    def get_document(self, doc_id: str, type: int = 1) -> bytes:
        """
        書類取得API で doc_id に紐づく書類実体を取得する。

        doc_id: 書類管理番号。
        type: 取得種別（1=PDF 等）。デフォルト 1。
        失敗時は空 bytes を返す。
        """
        time.sleep(_REQUEST_DELAY_SEC)
        params = urlencode({"type": type})
        url = f"{_EDINET_API_BASE}/documents/{doc_id}?{params}"
        return self._request_bytes(url)

    def _request_json(self, url: str) -> dict[str, Any]:
        """GET して JSON をパースして返す。失敗時は空 dict を返す。"""
        try:
            url_with_api_key = f"{url}&{urlencode(self._headers)}"
            req = Request(url_with_api_key)
            with urlopen(req, timeout=self._config.timeout) as resp:
                return json.loads(resp.read().decode())
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            logger.warning("Failed to fetch JSON %s: %s", url, e)
            return {}

    def _request_bytes(self, url: str) -> bytes:
        """GET して bytes を返す。503 時はリトライし、失敗時は空 bytes を返す。"""
        last_err: Exception | None = None
        for attempt in range(_RETRY_503_MAX):
            try:
                req = Request(url, headers=self._headers)
                with urlopen(req, timeout=self._config.timeout) as resp:
                    return resp.read()
            except HTTPError as e:
                last_err = e
                if e.code == 503 and attempt < _RETRY_503_MAX - 1:
                    logger.debug(
                        "503 for %s, retry %s/%s in %.1fs",
                        url,
                        attempt + 1,
                        _RETRY_503_MAX,
                        _RETRY_503_WAIT_SEC,
                    )
                    time.sleep(_RETRY_503_WAIT_SEC)
                else:
                    logger.debug("Failed to fetch bytes %s: %s", url, e)
                    return b""
            except URLError as e:
                logger.debug("Failed to fetch bytes %s: %s", url, e)
                return b""
        if last_err:
            logger.debug("Failed to fetch bytes %s after retries: %s", url, last_err)
        return b""
