"""EdgarDocumentsCollector: htm / iXBRL 提出書類を収集して Collection に保存する。"""

from __future__ import annotations

from typing import Any, Iterator, cast, override

from fino_filing.filing.filing_edgar import EDGARArchiveFiling

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument

from .._helpers import (
    _build_edgar_filing,
    _parse_edgar_date,
    _parse_meta_to_parsed,
    pad_cik,
)
from ..client import EdgarClient
from ..config import EdgarConfig


class EdgarDocumentsCollector(BaseCollector):
    """
    EdgarDocumentsCollector for SEC Archives Filings or Documents
    """

    def __init__(self, collection: Collection, config: EdgarConfig) -> None:
        super().__init__(collection)
        self._client = EdgarClient(config)

    @override
    def iter_collect(
        self,
        *,
        cik_list: list[str] | None = None,
        form_type: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> Iterator[tuple[EDGARArchiveFiling, str]]:
        yield from cast(
            Iterator[tuple[EDGARArchiveFiling, str]],
            super().iter_collect(
                cik_list=cik_list,
                limit_per_company=limit_per_company,
                **kwargs,
            ),
        )

    @override
    def collect(
        self,
        *,
        cik_list: list[str] | None = None,
        form_type: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> list[tuple[EDGARArchiveFiling, str]]:
        return list(
            self.iter_collect(
                cik_list=cik_list,
                limit_per_company=limit_per_company,
                **kwargs,
            )
        )

    @override
    def _fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        limit_per_company: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = pad_cik(cik)
            submissions = self._client.get_submissions(cik)
            if not submissions:
                continue

            filer_name = submissions.get("name") or ""
            sic = (submissions.get("sic") or "").strip()
            sic_desc = submissions.get("sicDescription") or ""
            state = (submissions.get("stateOfIncorporation") or "").strip()
            fye = (submissions.get("fiscalYearEnd") or "").strip()

            filings_container = submissions.get("filings") or {}
            recent: dict[str, Any] = (
                filings_container.get("recent") or submissions.get("recent") or {}
            )
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
                    "filer_name": filer_name,
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

    @override
    def _parse_response(self, meta: Meta) -> Parsed:
        """RawDocument の meta を EDGARArchiveFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(meta)

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EDGARArchiveFiling:
        """Parsed と content から EDGARArchiveFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (
            parsed.get("accession_number", "") + "-index.htm"
        )
        return _build_edgar_filing(parsed, content, primary_name)
