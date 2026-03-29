"""EdgerFactsCollector: JSON API から構造化データを収集して Collection に保存する。"""

from __future__ import annotations

import json
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument
from fino_filing.collector.error import CollectorNoContentError
from fino_filing.filing.filing_edger import EDGARCompanyFactsFiling

from .._helpers import (
    _build_edgar_company_facts_filing,
    _pad_cik,
    _parse_company_facts_meta_to_parsed,
)
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
    ) -> Iterator[tuple[EDGARCompanyFactsFiling, str]]:
        """
        Iterates over the Edger company facts. yields tuples of (EDGARCompanyFactsFiling, path).

        Args:
            cik_list: The list of CIKs to collect.
            limit: The maximum number of filings to collect.

        Yields:
            tuple[EDGARCompanyFactsFiling, str]: A tuple containing the EDGARCompanyFactsFiling and the path.
        """
        yield from cast(
            Iterator[tuple[EDGARCompanyFactsFiling, str]],
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
    ) -> list[tuple[EDGARCompanyFactsFiling, str]]:
        """
        Collects Edger company facts within the given CIK list.

        Args:
            cik_list: The list of CIKs to collect.
            limit: The maximum number of filings to collect.

        Returns:
            list[tuple[EDGARCompanyFactsFiling, str]]: A list of tuples containing the EDGARCompanyFactsFiling and the filing path.
        """
        return list(
            self.iter_collect(
                cik_list=cik_list,
                limit=limit,
            )
        )

    @override
    def _fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit: int | None = None,
    ) -> Iterator[RawDocument]:
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = _pad_cik(cik)

            submissions = self._client.get_submissions(cik)
            if not submissions:
                raise CollectorNoContentError(cik)

            company_name = submissions.get("name")
            sic_raw = submissions.get("sic")
            sic_str = (
                str(sic_raw).strip()
                if sic_raw is not None and str(sic_raw).strip() != ""
                else ""
            )
            sic_desc = (submissions.get("sicDescription") or "").strip()
            state = (submissions.get("stateOfIncorporation") or "").strip()
            fye = (submissions.get("fiscalYearEnd") or "").strip()
            tickers = submissions.get("tickers")
            exchanges = submissions.get("exchanges")

            facts = self._client.get_company_facts(cik)
            if not facts:
                continue

            content = json.dumps(facts, ensure_ascii=False).encode()
            primary_name = f"CIK{cik_pad}-companyfacts.json"

            meta: dict[str, Any] = {
                "cik": cik_pad,
                "company_name": company_name,
                "sic": sic_str,
                "sic_description": sic_desc,
                "filer_category": (submissions.get("category") or "").strip(),
                "state_of_incorporation": state,
                "fiscal_year_end": fye,
                "tickers": list(tickers) if isinstance(tickers, list) else [],
                "exchanges": list(exchanges) if isinstance(exchanges, list) else [],
                "format": "json",
                "primary_name": primary_name,
                "_origin": "facts",
            }
            yield RawDocument(content=content, meta=meta)

    @override
    def _parse_response(self, meta: Meta) -> Parsed:
        return _parse_company_facts_meta_to_parsed(meta)

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EDGARCompanyFactsFiling:
        primary_name = (
            parsed.get("primary_name")
            or f"CIK{parsed.get('cik', '')}-companyfacts.json"
        )
        return _build_edgar_company_facts_filing(parsed, content, primary_name)
