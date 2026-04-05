"""
Edgar 全エンドポイント対応の共通 HTTP クライアント。
Collector の内部コンポーネントとして使用する。
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Literal
from urllib.parse import quote

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.edgar._helper import _accession_to_dir
from fino_filing.collector.edgar.config import EdgarConfig
from fino_filing.collector.error import HttpNotFoundError
from fino_filing.util.edgar import pad_cik

logger = logging.getLogger(__name__)


class EdgarClient:
    _SEC_API_BASE = "https://data.sec.gov"
    _ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar"

    def __init__(
        self, config: EdgarConfig, *, _http_client: HttpClient | None = None
    ) -> None:
        self._config = config
        self._headers = {"User-Agent": config.user_agent_email}
        self._http_client = _http_client or HttpClient(
            HttpClientConfig.from_dict(asdict(config))
        )

    # Submissions
    def get_submissions(self, cik: str) -> dict[str, Any]:
        """Fetch Submissions History from SEC Submissions API"""
        cik_pad = pad_cik(cik)
        url = f"{self._SEC_API_BASE}/submissions/CIK{cik_pad}.json"
        return self._http_client.get(url, headers=self._headers)

    # Company Facts
    def get_company_facts(self, cik: str) -> dict[str, Any]:
        """Fetch XBRL Company Facts from SEC XBRL CompanyFacts API"""
        cik_pad = pad_cik(cik)
        url = f"{self._SEC_API_BASE}/api/xbrl/companyfacts/CIK{cik_pad}.json"
        return self._http_client.get(url, headers=self._headers)

    # Archives
    def _archives_file_url(self, cik_pad: str, acc_dir: str, relative_path: str) -> str:
        # URL encode the relative path
        rel = relative_path.lstrip("/")
        segments = rel.split("/")
        encoded = "/".join(quote(seg, safe="") for seg in segments)
        return f"{self._ARCHIVES_BASE}/data/{cik_pad}/{acc_dir}/{encoded}"

    def get_archives_file(self, cik: str, accession: str, relative_path: str) -> bytes:
        """Fetch a single file under the filing directory on SEC Archives (relative_path may include subdirs)."""
        cik_pad = pad_cik(cik)
        acc_dir = _accession_to_dir(accession)
        url = self._archives_file_url(cik_pad, acc_dir, relative_path)
        return self._http_client.get_raw(url, headers=self._headers)

    def try_get_filing_index_json(
        self, cik: str, accession: str
    ) -> dict[str, Any] | None:
        """Return parsed filing index.json when present; None if not found (older filings may lack it)."""
        cik_pad = pad_cik(cik)
        acc_dir = _accession_to_dir(accession)
        url = self._archives_file_url(cik_pad, acc_dir, "index.json")
        try:
            return self._http_client.get(url, headers=self._headers)
        except HttpNotFoundError:
            return None

    # Bulk
    def get_bulk(self, type: Literal["companyfacts", "submissions"]) -> bytes:
        """Fetch Bulk Data from specified URL"""

        if type == "companyfacts":
            url = f"{self._ARCHIVES_BASE}/daily-index/xbrl/companyfacts.zip"
        elif type == "submissions":
            url = f"{self._ARCHIVES_BASE}/daily-index/bulkdata/submissions.zip"

        return self._http_client.get_raw(url, headers=self._headers)
