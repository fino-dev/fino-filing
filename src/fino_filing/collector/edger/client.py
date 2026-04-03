"""
EDGAR 全エンドポイント対応の共通 HTTP クライアント。
Collector の内部コンポーネントとして使用する。
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Literal

from fino_filing.collector._http_client import HttpClient, HttpClientConfig
from fino_filing.collector.error import HttpNotFoundError
from fino_filing.collector.edger._helpers import _accession_to_dir, pad_cik
from fino_filing.collector.edger.config import EdgerConfig

logger = logging.getLogger(__name__)


class EdgerClient:
    _SEC_API_BASE = "https://data.sec.gov"
    _ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar"

    def __init__(
        self, config: EdgerConfig, *, _http_client: HttpClient | None = None
    ) -> None:
        self._config = config
        self._headers = {"User-Agent": config.user_agent_email}
        self._http_client = _http_client or HttpClient(
            HttpClientConfig.from_dict(asdict(config))
        )

    def get_submissions(self, cik: str) -> dict[str, Any]:
        """Fetch Submissions History from SEC Submissions API"""
        cik_pad = pad_cik(cik)
        url = f"{self._SEC_API_BASE}/submissions/CIK{cik_pad}.json"
        return self._http_client.get(url, headers=self._headers)

    def get_company_facts(self, cik: str) -> dict[str, Any]:
        """Fetch XBRL Company Facts from SEC XBRL CompanyFacts API"""
        cik_pad = pad_cik(cik)
        url = f"{self._SEC_API_BASE}/api/xbrl/companyfacts/CIK{cik_pad}.json"
        return self._http_client.get(url, headers=self._headers)

    def get_archives_file(self, cik: str, accession: str, file_name: str) -> bytes:
        """Fetch one file under the filing directory on SEC Archives (raw bytes)."""
        cik_pad = pad_cik(cik)
        acc_dir = _accession_to_dir(accession)
        url = f"{self._ARCHIVES_BASE}/data/{cik_pad}/{acc_dir}/{file_name}"
        return self._http_client.get_raw(url, headers=self._headers)

    def get_filing_document(self, cik: str, accession: str) -> bytes:
        """Fetch filing index page (``{accession}-index.htm``) from SEC Archives."""
        return self.get_archives_file(cik, accession, f"{accession}-index.htm")

    def get_filing_index_json(self, cik: str, accession: str) -> dict[str, Any] | None:
        """
        Fetch structured filing index (``{accession}-index.json``) from data.sec.gov.

        Returns None when the index JSON is not found (404).
        """
        cik_pad = pad_cik(cik)
        acc_dir = _accession_to_dir(accession)
        url = (
            f"{self._SEC_API_BASE}/Archives/edgar/data/"
            f"{cik_pad}/{acc_dir}/{accession}-index.json"
        )
        try:
            return self._http_client.get(url, headers=self._headers)
        except HttpNotFoundError:
            return None

    def get_bulk(self, type: Literal["company_facts", "submissions"]) -> bytes:
        """Fetch Bulk Data from specified URL"""

        if type == "company_facts":
            url = f"{self._ARCHIVES_BASE}/daily-index/xbrl/companyfacts.zip"
        elif type == "submissions":
            url = f"{self._ARCHIVES_BASE}/daily-index/bulkdata/submissions.zip"

        return self._http_client.get_raw(url, headers=self._headers)
