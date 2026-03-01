"""
Edger Collector Boundary: SEC API / Bulk 用 Strategy と EdgerCollector

責務:
- EdgerConfig: SEC API・Bulk のベース URL とタイムアウト
- EdgerSecApi: SEC Company Submissions API による取得・パース・EDGARFiling 生成
- EdgerBulkData: Bulk ZIP からの取得・パース・EDGARFiling 生成
- EdgerCollector: 上記 Strategy のオーケストレーション
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fino_filing.collection.collection import Collection
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edger import EDGARFiling

logger = logging.getLogger(__name__)

# SEC は User-Agent 必須。識別子を明示する。
DEFAULT_USER_AGENT = "fino-filing/0.1.0 (compliance; contact: odukaki@gmail.com)"


@dataclass
class EdgerConfig:
    """EDGAR 用設定。SEC API と Bulk のベース URL およびタイムアウト。"""

    sec_api_base: str = "https://data.sec.gov"
    archives_base: str = "https://www.sec.gov/Archives/edgar"
    bulk_base: str = "https://www.sec.gov/Archives/edgar/daily-index"
    timeout: int = 30
    user_agent: str = DEFAULT_USER_AGENT


def _parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _accession_to_slash(accession: str) -> str:
    """accession (0001104659-25-006631) を URL 用にダッシュ除去 (000110465925006631) にする。"""
    return accession.replace("-", "")


def _build_edgar_filing(
    parsed: Parsed,
    content: bytes,
    primary_name: str,
) -> EDGARFiling:
    """
    Parsed と content から EDGARFiling を組み立てる。EdgerSecApi / EdgerBulkData で共有する。
    """
    checksum = hashlib.sha256(content).hexdigest()
    filing_date = parsed.get("filing_date")
    if isinstance(filing_date, datetime):
        created_at = filing_date
    else:
        created_at = datetime.now()
    return EDGARFiling(
        source="EDGAR",
        name=primary_name,
        checksum=checksum,
        format=parsed.get("format", "htm"),
        is_zip=False,
        cik=parsed.get("cik", ""),
        accession_number=parsed.get("accession_number", ""),
        company_name=parsed.get("company_name", ""),
        form_type=parsed.get("form_type", ""),
        filing_date=parsed.get("filing_date") or created_at,
        period_of_report=parsed.get("period_of_report") or created_at,
        sic_code=parsed.get("sic_code", ""),
        state_of_incorporation=parsed.get("state_of_incorporation", ""),
        fiscal_year_end=parsed.get("fiscal_year_end", ""),
        created_at=created_at,
    )


class EdgerSecApi:
    """
    SEC Company Submissions API による取得・パース・EDGARFiling 生成の Strategy。
    """

    def __init__(self, config: EdgerConfig) -> None:
        self._config = config

    def fetch_documents(
        self,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
    ) -> list[RawDocument]:
        """
        CIK リストに基づき submissions API を叩き、各 filing の本文を取得して RawDocument のリストを返す。
        cik_list が None の場合は空リストを返す（呼び出し側で指定すること）。
        """
        if not cik_list:
            return []
        base = self._config.sec_api_base.rstrip("/")
        archives = self._config.archives_base.rstrip("/")
        headers = {"User-Agent": self._config.user_agent}
        results: list[RawDocument] = []
        for cik in cik_list:
            cik_pad = cik.zfill(10)
            url = f"{base}/submissions/CIK{cik_pad}.json"
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=self._config.timeout) as resp:
                    data = json.loads(resp.read().decode())
            except (HTTPError, URLError, json.JSONDecodeError) as e:
                logger.warning("Failed to fetch submissions for CIK %s: %s", cik, e)
                continue
            name = data.get("name") or ""
            sic = (data.get("sic") or "").strip() or ""
            sic_desc = data.get("sicDescription") or ""
            state = (data.get("stateOfIncorporation") or "").strip() or ""
            fye = (data.get("fiscalYearEnd") or "").strip() or ""
            # SEC API: filings.recent または legacy の recent
            filings_container = data.get("filings") or {}
            recent: dict[str, Any] = filings_container.get("recent") or data.get("recent") or {}
            accession_list = recent.get("accessionNumber") or []
            form_list = recent.get("form") or []
            filing_date_list = recent.get("filingDate") or []
            report_date_list = recent.get("reportDate") or []
            n = min(
                len(accession_list),
                len(form_list),
                len(filing_date_list),
                len(report_date_list) if report_date_list else len(filing_date_list),
            )
            if limit_per_company is not None:
                n = min(n, limit_per_company)
            for i in range(n):
                accession = accession_list[i] if i < len(accession_list) else ""
                form = form_list[i] if i < len(form_list) else ""
                filing_date_s = filing_date_list[i] if i < len(filing_date_list) else ""
                report_date_s = (
                    report_date_list[i]
                    if report_date_list and i < len(report_date_list)
                    else filing_date_s
                )
                content, primary_name = self._fetch_filing_content(
                    archives=archives,
                    cik=cik_pad,
                    accession=accession,
                    headers=headers,
                )
                if not content:
                    continue
                meta: dict[str, Any] = {
                    "cik": cik_pad,
                    "accession_number": accession,
                    "company_name": name,
                    "form_type": form,
                    "filing_date": _parse_edgar_date(filing_date_s),
                    "period_of_report": _parse_edgar_date(report_date_s),
                    "sic_code": sic or sic_desc,
                    "state_of_incorporation": state,
                    "fiscal_year_end": fye,
                    "format": "htm" if primary_name.endswith(".htm") else "txt",
                    "primary_name": primary_name,
                    "_origin": "sec",
                }
                results.append(RawDocument(content=content, meta=meta))
        return results

    def _fetch_filing_content(
        self,
        archives: str,
        cik: str,
        accession: str,
        headers: dict[str, str],
    ) -> tuple[bytes, str]:
        """
        提出物の index ページを取得する。index を primary として保存する。
        戻り値: (content, primary_name)
        """
        if not accession:
            return b"", ""
        acc_slash = _accession_to_slash(accession)
        primary_name = f"{accession}-index.htm"
        url = f"{archives}/data/{cik}/{acc_slash}/{primary_name}"
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=self._config.timeout) as resp:
                return resp.read(), primary_name
        except (HTTPError, URLError) as e:
            logger.debug("Failed to fetch content %s: %s", url, e)
            return b"", ""

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDGARFiling 用の Parsed に正規化する。"""
        m = raw.meta
        return {
            "cik": m.get("cik", ""),
            "accession_number": m.get("accession_number", ""),
            "company_name": m.get("company_name", ""),
            "form_type": m.get("form_type", ""),
            "filing_date": m.get("filing_date"),
            "period_of_report": m.get("period_of_report"),
            "sic_code": m.get("sic_code", ""),
            "state_of_incorporation": m.get("state_of_incorporation", ""),
            "fiscal_year_end": m.get("fiscal_year_end", ""),
            "format": m.get("format", "htm"),
            "primary_name": m.get("primary_name", ""),
        }

    def to_filing(self, parsed: Parsed, content: bytes) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (parsed.get("accession_number", "") + "-index.htm")
        return _build_edgar_filing(parsed, content, primary_name)


class EdgerBulkData:
    """
    Bulk ZIP からの取得・パース・EDGARFiling 生成の Strategy。
    初回は日付範囲や CIK で絞る想定。
    """

    def __init__(self, config: EdgerConfig) -> None:
        self._config = config

    def fetch_documents(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        cik_list: list[str] | None = None,
        limit: int | None = None,
    ) -> list[RawDocument]:
        """
        Bulk 用 URL から company_tickers.json 等のインデックスを参照し、
        指定範囲の submissions を取得して RawDocument のリストを返す。
        現状は submissions API と同構造の JSON を想定し、Bulk の index から
        CIK リストを取得して EdgerSecApi と同様に 1 件ずつ取得する簡易実装でも可。
        本実装では、Bulk は「指定 CIK リストについて submissions を取得」する
        形に寄せ、実際の ZIP 解凍は後続拡張とする。
        """
        # Bulk は ZIP 解凍・走査が重いため、ここでは空リストを返す。
        # テストでは RawDocument を直接組み立ててパース・to_filing を検証する。
        return []

    def parse_response(self, raw: RawDocument) -> Parsed:
        """EdgerSecApi と同様のマッピング。"""
        m = raw.meta
        return {
            "cik": m.get("cik", ""),
            "accession_number": m.get("accession_number", ""),
            "company_name": m.get("company_name", ""),
            "form_type": m.get("form_type", ""),
            "filing_date": m.get("filing_date"),
            "period_of_report": m.get("period_of_report"),
            "sic_code": m.get("sic_code", ""),
            "state_of_incorporation": m.get("state_of_incorporation", ""),
            "fiscal_year_end": m.get("fiscal_year_end", ""),
            "format": m.get("format", "htm"),
            "primary_name": m.get("primary_name", ""),
        }

    def to_filing(self, parsed: Parsed, content: bytes) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (parsed.get("accession_number", "") + "-index.htm")
        return _build_edgar_filing(parsed, content, primary_name)


class EdgerCollector(BaseCollector):
    """
    EdgerSecApi と EdgerBulkData を保持し、BaseCollector のテンプレートを Edger 用に実装する。
    """

    def __init__(
        self,
        collection: Collection,
        edger_sec_api: EdgerSecApi,
        edger_bulk: EdgerBulkData,
        cik_list: list[str] | None = None,
    ) -> None:
        super().__init__(collection)
        self._edger_sec_api = edger_sec_api
        self._edger_bulk = edger_bulk
        self._cik_list = cik_list or []

    def fetch_documents(
        self,
        limit_per_company: int | None = None,
    ) -> list[RawDocument]:
        """Sec と Bulk から取得した RawDocument をマージして返す。"""
        sec_docs = self._edger_sec_api.fetch_documents(
            cik_list=self._cik_list,
            limit_per_company=limit_per_company,
        )
        bulk_docs = self._edger_bulk.fetch_documents(limit=limit_per_company)
        return sec_docs + bulk_docs

    def parse_response(self, raw: RawDocument) -> Parsed:
        """raw の出所に応じて EdgerSecApi または EdgerBulkData の parse_response に委譲する。"""
        origin = raw.meta.get("_origin", "sec")
        if origin == "bulk":
            return self._edger_bulk.parse_response(raw)
        return self._edger_sec_api.parse_response(raw)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """出所に応じて build_filing_sec または build_filing_bulk で EDGARFiling を生成する。"""
        origin = raw.meta.get("_origin", "sec")
        if origin == "bulk":
            return self._build_filing_bulk(parsed, raw)
        return self._build_filing_sec(parsed, raw)

    def _build_filing_sec(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """SEC API 由来の Parsed から EDGARFiling を生成する。"""
        return self._edger_sec_api.to_filing(parsed, raw.content)

    def _build_filing_bulk(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """Bulk 由来の Parsed から EDGARFiling を生成する。"""
        return self._edger_bulk.to_filing(parsed, raw.content)
