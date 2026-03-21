"""EdgerFactsCollector: JSON API から構造化データを収集して Collection に保存する。"""

from __future__ import annotations

import json
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edger import EDGARFiling

from ._helpers import _build_edgar_filing, _parse_meta_to_parsed
from .client import EdgerClient
from .config import EdgerConfig


class EdgerFactsCollector(BaseCollector):
    """
    SEC XBRL CompanyFacts API / Submissions API から構造化データを収集して Collection に保存する。

    用途: ファクト・概念など JSON 構造化データを取得して Collection に保存する。
    収集条件: collect(cik_list=[...], limit_per_company=N) で渡す。
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    @override
    def collect(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> list[tuple[EDGARFiling, str]]:
        """収集フローを実行し、EDGARFiling と保存パスのリストを返す。"""
        return cast(
            list[tuple[EDGARFiling, str]],
            super().collect(
                cik_list=cik_list,
                limit_per_company=limit_per_company,
                **kwargs,
            ),
        )

    def fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """各 CIK の CompanyFacts JSON を取得し、JSON bytes を content にした RawDocument を yield する。"""
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

            facts = self._client.get_company_facts(cik)
            if not facts:
                continue

            content = json.dumps(facts, ensure_ascii=False).encode()
            primary_name = f"CIK{cik_pad}-companyfacts.json"

            meta: dict[str, Any] = {
                "cik": cik_pad,
                "accession_number": f"facts-{cik_pad}",
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
        primary_name = (
            parsed.get("primary_name") or f"{parsed.get('cik', '')}-companyfacts.json"
        )
        return _build_edgar_filing(parsed, raw.content, primary_name)
