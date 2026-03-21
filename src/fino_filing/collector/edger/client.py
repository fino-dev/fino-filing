"""
EDGAR 全エンドポイント対応の共通 HTTP クライアント。
Collector の内部コンポーネントとして使用する。
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fino_filing.collector.edger._helpers import _accession_to_dir
from fino_filing.collector.edger.config import EdgerConfig

logger = logging.getLogger(__name__)

# SEC は 1 秒あたり 10 リクエスト以下を推奨
_REQUEST_DELAY_SEC: float = 0.2
_RETRY_503_MAX: int = 3
_RETRY_503_WAIT_SEC: float = 2.0
_PACKAGE_NAME = "fino-filing/0.1.0"


class EdgerClient:
    """
    EDGAR 全エンドポイント対応の共通 HTTP クライアント。

    責務:
    - User-Agent ヘッダーの組み立て（package名 + user_agent_email）
    - レート制限対策（リクエスト間 delay）
    - 503 時のリトライ
    - JSON / bytes 各エンドポイントへのアクセスメソッド提供
    """

    _SEC_API_BASE = "https://data.sec.gov"
    _ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar"

    def __init__(self, config: EdgerConfig) -> None:
        self._config = config
        self._user_agent = f"{_PACKAGE_NAME} (contact: {config.user_agent_email})"
        self._headers = {"User-Agent": self._user_agent}

    def get_submissions(self, cik: str) -> dict[str, Any]:
        """SEC Submissions API から企業の提出一覧を取得する。"""
        cik_pad = cik.zfill(10)
        url = f"{self._SEC_API_BASE}/submissions/CIK{cik_pad}.json"
        return self._request_json(url)

    def get_company_facts(self, cik: str) -> dict[str, Any]:
        """SEC XBRL CompanyFacts API から企業の全 XBRL ファクトを取得する。"""
        cik_pad = cik.zfill(10)
        url = f"{self._SEC_API_BASE}/api/xbrl/companyfacts/CIK{cik_pad}.json"
        return self._request_json(url)

    def get_filing_document(self, cik: str, accession: str) -> bytes:
        """提出物の index ページを取得して bytes で返す。"""
        cik_pad = cik.zfill(10)
        acc_dir = _accession_to_dir(accession)
        primary_name = f"{accession}-index.htm"
        url = f"{self._ARCHIVES_BASE}/data/{cik_pad}/{acc_dir}/{primary_name}"
        return self._request_bytes(url)

    def get_bulk(self, url: str) -> bytes:
        """指定 URL から Bulk データを bytes で取得する。"""
        return self._request_bytes(url)

    def _request_json(self, url: str) -> dict[str, Any]:
        """GET して JSON をパースして返す。失敗時は空 dict を返す。"""
        time.sleep(_REQUEST_DELAY_SEC)
        try:
            req = Request(url, headers=self._headers)
            with urlopen(req, timeout=self._config.timeout) as resp:
                return json.loads(resp.read().decode())
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            logger.warning("Failed to fetch JSON %s: %s", url, e)
            return {}

    def _request_bytes(self, url: str) -> bytes:
        """GET して bytes を返す。503 時はリトライし、失敗時は空 bytes を返す。"""
        time.sleep(_REQUEST_DELAY_SEC)
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
