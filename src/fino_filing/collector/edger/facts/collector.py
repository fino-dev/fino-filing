"""EdgerFactsCollector: JSON API から構造化データを収集して Collection に保存する。"""

from __future__ import annotations

import json
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.collector.error import (
    CollectorNoContentError,
    CollectorParseResponseValidationError,
)
from fino_filing.filing.filing_edger import EDGARCompanyFactsFiling
from fino_filing.util.content import sha256_checksum
from fino_filing.util.delimited_symbols import normalize_delimited_multivalue

from .._helpers import (
    _build_company_facts_json_file_name,
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
            submissions = self._client.get_submissions(cik)
            if not submissions:
                raise CollectorNoContentError(cik)

            facts = self._client.get_company_facts(cik)
            if not facts:
                raise CollectorNoContentError(cik)

            content = json.dumps(facts, ensure_ascii=False).encode()

            meta: dict[str, Any] = {
                "cik": submissions.get("cik"),
                "entityType": submissions.get("entityType"),
                "name": submissions.get("name"),
                "sic": submissions.get("sic"),
                "sicDescription": submissions.get("sicDescription"),
                "category": submissions.get("category"),
                "fiscalYearEnd": submissions.get("fiscalYearEnd"),
                "stateOfIncorporation": submissions.get("stateOfIncorporation"),
                "tickers": submissions.get("tickers"),
                "exchanges": submissions.get("exchanges"),
            }
            yield RawDocument(content=content, meta=meta)

    @override
    def _parse_response(self, raw: RawDocument) -> Parsed:
        meta = raw.meta
        return {
            "cik": meta.get("cik"),
            "entity_type": meta.get("entityType"),
            "filer_name": meta.get("name"),
            "sic": meta.get("sic"),
            "sic_description": meta.get("sicDescription"),
            "filer_category": meta.get("category"),
            "fiscal_year_end": meta.get("fiscalYearEnd"),
            "state_of_incorporation": meta.get("stateOfIncorporation"),
            "tickers": meta.get("tickers"),
            "exchanges": meta.get("exchanges"),
        }

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EDGARCompanyFactsFiling:
        cik = parsed.get("cik")
        if not cik:
            raise CollectorParseResponseValidationError("cik")

        name = _build_company_facts_json_file_name(cik)
        checksum = sha256_checksum(content)
        return EDGARCompanyFactsFiling(
            # source, format, is_zip are default defined
            # ID will be automatically generated from identifier fields
            name=name,
            checksum=checksum,
            # edgar_resource_kind is default defined
            cik=cik,
            entity_type=parsed.get("entity_type"),
            filer_name=parsed.get("filer_name"),
            sic=parsed.get("sic"),
            sic_description=parsed.get("sic_description"),
            filer_category=parsed.get("filer_category"),
            state_of_incorporation=parsed.get("state_of_incorporation"),
            fiscal_year_end=parsed.get("fiscal_year_end"),
            tickers_key=normalize_delimited_multivalue(parsed.get("tickers")),
            exchanges_key=normalize_delimited_multivalue(parsed.get("exchanges")),
        )
