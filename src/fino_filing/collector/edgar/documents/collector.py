from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.collector.edgar.documents._helper import (
    _verify_and_parse_edgar_submissions_recent_filings,
)
from fino_filing.collector.edgar.documents.enum import EdgarDocumentsFetchMode
from fino_filing.collector.error import (
    CollectorInvalidFetchModeError,
    CollectorNoContentError,
    CollectorParseResponseValidationError,
    HttpNotFoundError,
)
from fino_filing.filing.filing_edgar import EdgarArchiveFiling
from fino_filing.util.content import build_zip_bytes, find_zip, sha256_checksum

from .._helpers import (
    _filenames_from_sec_index_json,
    pad_cik,
)
from ..client import EdgarClient
from ..config import EdgarConfig

logger = logging.getLogger(__name__)


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
        form_type_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgarDocumentsFetchMode = EdgarDocumentsFetchMode.PRIMARY_ONLY,
    ) -> Iterator[tuple[EdgarArchiveFiling, str]]:
        yield from cast(
            Iterator[tuple[EdgarArchiveFiling, str]],
            super().iter_collect(
                cik_list=cik_list,
                form_type_list=form_type_list,
                limit_per_company=limit_per_company,
                fetch_mode=fetch_mode,
            ),
        )

    @override
    def collect(
        self,
        *,
        cik_list: list[str] | None = None,
        form_type_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgarDocumentsFetchMode = EdgarDocumentsFetchMode.PRIMARY_ONLY,
    ) -> list[tuple[EdgarArchiveFiling, str]]:
        return list(
            self.iter_collect(
                cik_list=cik_list,
                form_type_list=form_type_list,
                limit_per_company=limit_per_company,
                fetch_mode=fetch_mode,
            )
        )

    @override
    def _fetch_documents(
        self,
        *,
        cik_list: list[str] | None = None,
        form_type_list: list[str] | None = None,
        limit_per_company: int | None = None,
        fetch_mode: EdgarDocumentsFetchMode = EdgarDocumentsFetchMode.PRIMARY_ONLY,
    ) -> Iterator[RawDocument]:
        if not cik_list:
            return
        for cik in cik_list:
            cik_pad = pad_cik(cik)

            submissions = self._client.get_submissions(cik_pad)
            if not submissions:
                raise CollectorNoContentError(cik_pad)

            company_meta: dict[str, Any] = {
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

            filings_container = submissions.get("filings") or {}
            recent_container: dict[str, Any] = (
                filings_container.get("recent") or submissions.get("recent") or {}
            )

            recent_filings = _verify_and_parse_edgar_submissions_recent_filings(
                cik_pad,
                recent_container,
            )

            recent_filings_length = len(recent_filings.get("accessionNumber"))

            accession_numbers = recent_filings["accessionNumber"]
            primary_documents = recent_filings["primaryDocument"]

            for i in range(recent_filings_length):
                accession = accession_numbers[i]
                primary_document = primary_documents[i]

                meta: dict[str, Any]
                content: bytes
                if fetch_mode == "primary_only":
                    if not primary_document:
                        raise CollectorNoContentError(
                            f"submissions.filings.recent: {cik_pad} {accession} {primary_document}"
                        )

                    content = self._client.get_archives_file(
                        cik_pad, accession, primary_document
                    )
                    if not content:
                        raise CollectorNoContentError(
                            f"primary_only: {cik_pad} {accession} {primary_document}"
                        )

                elif fetch_mode == "full":
                    content = self._fetch_full_filing_as_zip(
                        cik_pad=cik_pad,
                        accession=accession,
                    )

                else:
                    raise CollectorInvalidFetchModeError(fetch_mode.value)

                meta = {
                    **company_meta,
                    "accessionNumber": accession,
                    "filingDate": recent_filings["filingDate"][i],
                    "reportDate": recent_filings["reportDate"][i],
                    "acceptanceDateTime": recent_filings["acceptanceDateTime"][i],
                    "act": recent_filings["act"][i],
                    "form": recent_filings["form"][i],
                    "items": recent_filings["items"][i],
                    "core_type": recent_filings["core_type"][i],
                    "isXBRL": recent_filings["isXBRL"][i],
                    "isInlineXBRL": recent_filings["isInlineXBRL"][i],
                    "primaryDocument": primary_document,
                    "primaryDocDescription": recent_filings["primaryDocDescription"][i],
                    "_fetch_mode": fetch_mode,
                }
                yield RawDocument(content=content, meta=meta)

    def _fetch_full_filing_as_zip(
        self,
        cik_pad: str,
        accession: str,
    ) -> bytes:
        index_obj = self._client.try_get_filing_index_json(cik_pad, accession)
        if not index_obj:
            raise CollectorNoContentError(f"{cik_pad} {accession} index.json")

        names = _filenames_from_sec_index_json(index_obj)

        if not names:
            raise CollectorNoContentError(
                f"{cik_pad} {accession} index.json directory.item"
            )

        # If zip file is found, return the zip bytes
        if zip_name := find_zip(file_names=names):
            zip_bytes = self._client.get_archives_file(cik_pad, accession, zip_name)
            return zip_bytes

        entries: dict[str, bytes] = {}
        for name in names:
            try:
                entries[name] = self._client.get_archives_file(cik_pad, accession, name)
            except HttpNotFoundError:
                logger.warning(
                    "Archives file missing, skipped: accession=%s path=%s",
                    accession,
                    name,
                )
        if not entries:
            raise CollectorParseResponseValidationError(
                f"{cik_pad} {accession} no documents found"
            )

        zip_bytes = build_zip_bytes(entries)
        return zip_bytes

    @override
    def _parse_response(self, raw: RawDocument) -> Parsed:
        meta = raw.meta
        return {
            "cik": meta.get("cik", ""),
            "accession_number": meta.get("accession_number", ""),
            "filer_name": meta.get("filer_name", ""),
            "form_type": meta.get("form_type", ""),
            "filing_date": meta.get("filing_date"),
            "period_of_report": meta.get("period_of_report"),
            "sic_code": meta.get("sic_code", ""),
            "state_of_incorporation": meta.get("state_of_incorporation", ""),
            "fiscal_year_end": meta.get("fiscal_year_end", ""),
            "format": meta.get("format", "htm"),
            "primary_name": meta.get("primary_name", ""),
            "is_zip": bool(meta.get("is_zip", False)),
        }

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EdgarArchiveFiling:
        primary_name = parsed.get("primary_name") or (
            str(parsed.get("accession_number", "")) + "-index.htm"
        )
        filing_date = parsed.get("filing_date")
        created_at = (
            filing_date if isinstance(filing_date, datetime) else datetime.now()
        )
        filing_date_effective = parsed.get("filing_date") or created_at
        period_effective = parsed.get("period_of_report") or created_at
        return EdgarArchiveFiling(
            source="Edgar",
            name=primary_name,
            checksum=sha256_checksum(content),
            format=parsed.get("format", "htm"),
            is_zip=bool(parsed.get("is_zip", False)),
            cik=parsed.get("cik", ""),
            accession_number=parsed.get("accession_number", ""),
            filer_name=parsed.get("filer_name", ""),
            form_type=parsed.get("form_type", ""),
            filing_date=filing_date_effective,
            period_of_report=period_effective,
            sic_code=parsed.get("sic_code", ""),
            state_of_incorporation=parsed.get("state_of_incorporation", ""),
            fiscal_year_end=parsed.get("fiscal_year_end", ""),
            created_at=created_at,
        )
