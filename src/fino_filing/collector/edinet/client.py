"""
EDINET 書類一覧API・書類取得API のリクエスト実行を行う HTTP クライアント。
Collector の内部コンポーネントとして使用する。
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import date
from typing import Any

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.edinet.config import EdinetConfig
from fino_filing.util._date import date_to_str

logger = logging.getLogger(__name__)


class EdinetClient:
    _EDINET_API_BASE = "https://api.edinet-fsa.go.jp/api/v2"

    def __init__(self, config: EdinetConfig) -> None:
        self._config = config
        self._credential = config.api_key

        self._http_client = HttpClient(HttpClientConfig.from_dict(asdict(config)))

    def get_document_list(self, date: date, type: int = 1) -> dict[str, Any]:

        params: dict[str, str | int] = {
            "Subscription-Key": self._credential,
            "date": date_to_str(date),
            "type": type,
        }
        url = f"{self._EDINET_API_BASE}/documents.json"
        return self._http_client.get(url, params=params)

    def get_document(self, doc_id: str, type: int = 1) -> bytes:
        params: dict[str, str | int] = {
            "Subscription-Key": self._credential,
            "type": type,
        }
        url = f"{self._EDINET_API_BASE}/documents/{doc_id}"
        return self._http_client.get_raw(url, params=params)
