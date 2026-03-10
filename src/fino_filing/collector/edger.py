"""
Edger Collector Boundary: EdgerClient と 3 つの Collector

責務:
- EdgerConfig: ユーザー固有設定のみ（user_agent_email 必須 / timeout 任意）
- EdgerClient: EDGAR 全エンドポイント対応の共通 HTTP クライアント
               レート制限・リトライ・User-Agent を内部管理
- EdgerFactsCollector:     JSON API から構造化データを収集して Collection に保存
- EdgerDocumentsCollector: htm / iXBRL 提出書類を収集して Collection に保存
- EdgerBulkCollector:      Bulk 一括データを収集して Collection に保存（スタブ）
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edger import EDGARFiling

logger = logging.getLogger(__name__)

# ---- package 内定数（EDGAR 仕様に準拠した固定値） ----
_SEC_API_BASE = "https://data.sec.gov"
_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar"
_BULK_BASE = "https://www.sec.gov/Archives/edgar/daily-index"
# SEC は 1 秒あたり 10 リクエスト以下を推奨
_REQUEST_DELAY_SEC: float = 0.2
_RETRY_503_MAX: int = 3
_RETRY_503_WAIT_SEC: float = 2.0
_PACKAGE_NAME = "fino-filing/0.1.0"


# ---- ヘルパー関数 ----

def _parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _accession_to_dir(accession: str) -> str:
    """accession (0001104659-25-006631) を Archives ディレクトリ名 (000110465925006631) に変換する。"""
    return accession.replace("-", "")


def _build_edgar_filing(parsed: Parsed, content: bytes, primary_name: str) -> EDGARFiling:
    """Parsed と content から EDGARFiling を組み立てる。3 Collector で共有する。"""
    checksum = hashlib.sha256(content).hexdigest()
    filing_date = parsed.get("filing_date")
    created_at = filing_date if isinstance(filing_date, datetime) else datetime.now()
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


def _parse_meta_to_parsed(meta: dict[str, Any]) -> Parsed:
    """RawDocument.meta から EDGARFiling 用 Parsed を組み立てる。3 Collector で共有する。"""
    return {
        "cik": meta.get("cik", ""),
        "accession_number": meta.get("accession_number", ""),
        "company_name": meta.get("company_name", ""),
        "form_type": meta.get("form_type", ""),
        "filing_date": meta.get("filing_date"),
        "period_of_report": meta.get("period_of_report"),
        "sic_code": meta.get("sic_code", ""),
        "state_of_incorporation": meta.get("state_of_incorporation", ""),
        "fiscal_year_end": meta.get("fiscal_year_end", ""),
        "format": meta.get("format", "htm"),
        "primary_name": meta.get("primary_name", ""),
    }


# ---- Config ----

@dataclass
class EdgerConfig:
    """
    EDGAR 用ユーザー設定。

    user_agent_email: SEC が要求する連絡用メールアドレス（必須）。
        User-Agent ヘッダーは package 側で組み立てる。
    timeout: HTTP タイムアウト（秒）。
    """

    user_agent_email: str
    timeout: int = 30


# ---- Client ----

class EdgerClient:
    """
    EDGAR 全エンドポイント対応の共通 HTTP クライアント。

    責務:
    - User-Agent ヘッダーの組み立て（package名 + user_agent_email）
    - レート制限対策（リクエスト間 delay）
    - 503 時のリトライ
    - JSON / bytes 各エンドポイントへのアクセスメソッド提供

    EdgerFactsCollector / EdgerDocumentsCollector / EdgerBulkCollector が共有する。
    """

    def __init__(self, config: EdgerConfig) -> None:
        self._config = config
        self._user_agent = f"{_PACKAGE_NAME} (contact: {config.user_agent_email})"
        self._headers = {"User-Agent": self._user_agent}

    def get_submissions(self, cik: str) -> dict[str, Any]:
        """
        SEC Submissions API から企業の提出一覧を取得する。

        https://data.sec.gov/submissions/CIK{cik}.json
        """
        cik_pad = cik.zfill(10)
        url = f"{_SEC_API_BASE}/submissions/CIK{cik_pad}.json"
        return self._request_json(url)

    def get_company_facts(self, cik: str) -> dict[str, Any]:
        """
        SEC XBRL CompanyFacts API から企業の全 XBRL ファクトを取得する。

        https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
        """
        cik_pad = cik.zfill(10)
        url = f"{_SEC_API_BASE}/api/xbrl/companyfacts/CIK{cik_pad}.json"
        return self._request_json(url)

    def get_filing_document(self, cik: str, accession: str) -> bytes:
        """
        提出物の index ページ（Archives/edgar/data/{cik}/{accession_dir}/{accession}-index.htm）を取得する。

        CIK・accession から URL を組み立て、index.htm を bytes で返す。
        """
        cik_pad = cik.zfill(10)
        acc_dir = _accession_to_dir(accession)
        primary_name = f"{accession}-index.htm"
        url = f"{_ARCHIVES_BASE}/data/{cik_pad}/{acc_dir}/{primary_name}"
        return self._request_bytes(url)

    def get_bulk(self, url: str) -> bytes:
        """指定 URL から Bulk データを bytes で取得する。"""
        return self._request_bytes(url)

    # ---- private: 共通 HTTP 処理 ----

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


# ---- Collectors ----

class EdgerFactsCollector(BaseCollector):
    """
    SEC XBRL CompanyFacts API / Submissions API から構造化データを収集して Collection に保存する。

    用途: ファクト・概念など JSON 構造化データを取得して Collection に保存する。
    収集条件: collect(cik_list=[...], limit_per_company=N) で渡す。
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    def fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """
        各 CIK の CompanyFacts JSON を取得し、JSON bytes を content にした RawDocument を yield する。

        Args:
            cik_list: 収集対象の CIK 一覧。None / 空の場合は何も yield しない。
            limit_per_company: 各 CIK の取得件数上限（None は無制限）。
        """
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = cik.zfill(10)
            # Submissions で会社メタを取得
            submissions = self._client.get_submissions(cik)
            if not submissions:
                continue
            company_name = submissions.get("name") or ""
            sic = (submissions.get("sic") or "").strip()
            sic_desc = submissions.get("sicDescription") or ""
            state = (submissions.get("stateOfIncorporation") or "").strip()
            fye = (submissions.get("fiscalYearEnd") or "").strip()

            # CompanyFacts で全ファクトを取得
            facts = self._client.get_company_facts(cik)
            if not facts:
                continue

            content = json.dumps(facts, ensure_ascii=False).encode()
            accession_number = f"facts-{cik_pad}"
            primary_name = f"CIK{cik_pad}-companyfacts.json"

            meta: dict[str, Any] = {
                "cik": cik_pad,
                "accession_number": accession_number,
                "company_name": company_name,
                "form_type": "companyfacts",
                "filing_date": None,
                "period_of_report": None,
                "sic_code": sic or sic_desc,
                "state_of_incorporation": state,
                "fiscal_year_end": fye,
                "format": "json",
                "primary_name": primary_name,
                "_origin": "facts",
            }
            yield RawDocument(content=content, meta=meta)

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDGARFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(raw.meta)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or f"{parsed.get('cik', '')}-companyfacts.json"
        return _build_edgar_filing(parsed, raw.content, primary_name)


class EdgerDocumentsCollector(BaseCollector):
    """
    SEC Archives から提出書類（htm / iXBRL）を収集して Collection に保存する。

    用途: 提出書類（ドキュメント）そのものを取得して Collection に保存する。
    収集条件: collect(cik_list=[...], limit_per_company=N) で渡す。
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    def fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """
        各 CIK の Submissions API から accession 一覧を取得し、
        各提出物の index.htm を bytes にした RawDocument を yield する。

        Args:
            cik_list: 収集対象の CIK 一覧。None / 空の場合は何も yield しない。
            limit_per_company: 各 CIK の取得 filing 数上限（None は無制限）。
        """
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = cik.zfill(10)
            submissions = self._client.get_submissions(cik)
            if not submissions:
                continue

            company_name = submissions.get("name") or ""
            sic = (submissions.get("sic") or "").strip()
            sic_desc = submissions.get("sicDescription") or ""
            state = (submissions.get("stateOfIncorporation") or "").strip()
            fye = (submissions.get("fiscalYearEnd") or "").strip()

            filings_container = submissions.get("filings") or {}
            recent: dict[str, Any] = filings_container.get("recent") or submissions.get("recent") or {}
            accession_list: list[str] = recent.get("accessionNumber") or []
            form_list: list[str] = recent.get("form") or []
            filing_date_list: list[str] = recent.get("filingDate") or []
            report_date_list: list[str] = recent.get("reportDate") or []

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
                content = self._client.get_filing_document(cik_pad, accession)
                if not content:
                    continue

                primary_name = f"{accession}-index.htm"
                meta: dict[str, Any] = {
                    "cik": cik_pad,
                    "accession_number": accession,
                    "company_name": company_name,
                    "form_type": form,
                    "filing_date": _parse_edgar_date(filing_date_s),
                    "period_of_report": _parse_edgar_date(report_date_s),
                    "sic_code": sic or sic_desc,
                    "state_of_incorporation": state,
                    "fiscal_year_end": fye,
                    "format": "htm" if primary_name.endswith(".htm") else "txt",
                    "primary_name": primary_name,
                    "_origin": "documents",
                }
                yield RawDocument(content=content, meta=meta)

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDGARFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(raw.meta)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (parsed.get("accession_number", "") + "-index.htm")
        return _build_edgar_filing(parsed, raw.content, primary_name)


class EdgerBulkCollector(BaseCollector):
    """
    SEC Bulk データを一括取得して Collection に保存する。

    用途: Bulk 用 URL から一括取得して Collection に保存する。
    収集条件: collect(date_from=..., date_to=..., cik_list=..., limit=N) で渡す。

    注意: 現状は未実装のスタブ。EdgerClient.get_bulk() を呼ぶ実装に順次置き換える。
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    def fetch_documents(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        cik_list: list[str] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """
        Bulk データを取得して RawDocument を yield する。

        Args:
            date_from: 取得開始日（YYYY-MM-DD）
            date_to: 取得終了日（YYYY-MM-DD）
            cik_list: 絞り込む CIK 一覧（None は全件）
            limit: 取得上限件数
        """
        # TODO: EdgerClient.get_bulk() を利用した実装
        yield from ()

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDGARFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(raw.meta)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (parsed.get("accession_number", "") + "-index.htm")
        return _build_edgar_filing(parsed, raw.content, primary_name)
