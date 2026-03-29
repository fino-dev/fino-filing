"""EdgerFactsCollector: JSON API から構造化データを収集して Collection に保存する。"""

from __future__ import annotations

import json
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edger import EDGARFiling

from .._helpers import _build_edgar_filing, _parse_meta_to_parsed
from ..client import EdgerClient
from ..config import EdgerConfig


class EdgerFactsCollector(BaseCollector):
    """
    Edger Collector for Facts API
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    @override
    def iter_collect(
        self,
        *,
        cik_list: list[str] | None = None,
        limit: int | None = None,
    ) -> Iterator[tuple[EDGARFiling, str]]:
        yield from cast(
            Iterator[tuple[EDGARFiling, str]],
            super().iter_collect(
                cik_list=cik_list,
                limit=limit,
            ),
        )

    @override
    def collect(
        self,
        *,
        cik_list: list[str] | None = None,
        limit: int | None = None,
    ) -> list[tuple[EDGARFiling, str]]:
        return list(
            self.iter_collect(
                cik_list=cik_list,
                limit=limit,
            )
        )

    def _fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit: int | None = None,
    ) -> Iterator[RawDocument]:
        if not cik_list:
            return
        for cik in cik_list:
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

    def _parse_response(self, raw: RawDocument) -> Parsed:
        return _parse_meta_to_parsed(raw.meta)

    def _build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        primary_name = (
            parsed.get("primary_name") or f"{parsed.get('cik', '')}-companyfacts.json"
        )
        return _build_edgar_filing(parsed, raw.content, primary_name)
