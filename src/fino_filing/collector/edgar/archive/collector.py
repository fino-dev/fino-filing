from __future__ import annotations

import logging
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.collector.error import (
    CollectorNoContentError,
    CollectorParseResponseValidationError,
    HttpNotFoundError,
)
from fino_filing.filing.filing_edgar import EdgarArchiveFiling
from fino_filing.util.content import (
    build_zip_bytes,
    find_zip,
    is_zip_content,
    sha256_checksum,
)
from fino_filing.util.delimited_symbols import normalize_delimited_multivalue
from fino_filing.util.edgar import pad_cik

from .._helper import (
    _filenames_from_sec_index_json,
    _infer_edgar_format,
    _parse_edgar_date,
    _parse_edgar_datetime,
    _parse_edgar_flag,
    _verify_and_parse_edgar_submissions_recent_filings,
)
from ..client import EdgarClient
from ..config import EdgarConfig
from .enum import EdgarDocumentsFetchMode

logger = logging.getLogger(__name__)


class EdgarArchiveCollector(BaseCollector):
    """
    EdgarArchiveCollector for SEC Archives Filings or Documents
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
                "cik": cik_pad,
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
                if fetch_mode == EdgarDocumentsFetchMode.PRIMARY_ONLY:
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

                elif fetch_mode == EdgarDocumentsFetchMode.FULL:
                    content = self._fetch_full_filing_as_zip(
                        cik_pad=cik_pad,
                        accession=accession,
                    )

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
        """Fetch each filing and build zip bytes if possible"""
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
            # company meta
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
            # filing meta
            "accession_number": meta.get("accessionNumber"),
            "filing_date": _parse_edgar_date(meta.get("filingDate")),
            "report_date": _parse_edgar_date(meta.get("reportDate")),
            "acceptance_date_time": _parse_edgar_datetime(
                meta.get("acceptanceDateTime")
            ),
            "act": meta.get("act"),
            "form": meta.get("form"),
            "items": meta.get("items"),
            "core_type": meta.get("core_type"),
            "is_xbrl": _parse_edgar_flag(meta.get("isXBRL")),
            "is_inline_xbrl": _parse_edgar_flag(meta.get("isInlineXBRL")),
            "primary_document": meta.get("primaryDocument"),
            "primary_doc_description": meta.get("primaryDocDescription"),
            # additional meta
            "_fetch_mode": meta.get("_fetch_mode"),
        }

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EdgarArchiveFiling:
        cik = parsed.get("cik")
        if not cik:
            raise CollectorParseResponseValidationError("cik")

        accession_number = parsed.get("accession_number")
        if not accession_number:
            raise CollectorParseResponseValidationError("accession_number")

        fetch_mode = parsed.get("_fetch_mode")
        if not isinstance(fetch_mode, EdgarDocumentsFetchMode):
            raise CollectorParseResponseValidationError("fetch_mode")

        is_xbrl = parsed.get("is_xbrl")
        is_inline_xbrl = parsed.get("is_inline_xbrl")
        primary_document = parsed.get("primary_document")
        format = _infer_edgar_format(
            is_xbrl=is_xbrl,
            is_inline_xbrl=is_inline_xbrl,
            primary_document=primary_document,
        )

        return EdgarArchiveFiling(
            # id, created_at will be automatically generated from identifier fields
            name=EdgarArchiveFiling.build_default_name(
                cik=cik,
                accession=accession_number,
                fetch_mode=fetch_mode,
                format=parsed.get("format", "htm"),
            ),
            checksum=sha256_checksum(content),
            format=format,
            is_zip=is_zip_content(content),
            # company meta
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
            # filing meta
            accession_number=accession_number,
            filing_date=parsed.get("filing_date"),
            report_date=parsed.get("report_date"),
            acceptance_date_time=parsed.get("acceptance_date_time"),
            act=parsed.get("act"),
            form=parsed.get("form"),
            items=parsed.get("items"),
            core_type=parsed.get("core_type"),
            is_xbrl=is_xbrl,
            is_inline_xbrl=is_inline_xbrl,
            primary_document=primary_document,
            primary_doc_description=parsed.get("primary_doc_description"),
        )
