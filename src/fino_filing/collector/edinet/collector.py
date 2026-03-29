from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument
from fino_filing.collector.edinet.enum import (
    EDINET_DOCUMENT_DOWNLOAD_TYPE,
    EDINET_DOCUMENT_LIST_TYPE,
)
from fino_filing.collector.error import (
    CollectorDateRangeValidationError,
    CollectorLimitValidationError,
    CollectorNoContentError,
    CollectorParseResponseValidationError,
)
from fino_filing.filing.filing_edinet import EDINETFiling
from fino_filing.util.content import is_zip_content, sha256_checksum

from ._helpers import _infer_edinet_format, _parse_edinet_date, _parse_edinet_datetime
from .client import EdinetClient
from .config import EdinetConfig


class EdinetCollector(BaseCollector):
    """
    Edinet Collector that collects filings from the Edinet API.
    """

    def __init__(self, collection: Collection, config: EdinetConfig) -> None:
        super().__init__(collection)
        self._config = config
        self._client = EdinetClient(config)

    @override
    def iter_collect(
        self,
        *,
        date_from: date,
        date_to: date,
        document_type: EDINET_DOCUMENT_DOWNLOAD_TYPE = EDINET_DOCUMENT_DOWNLOAD_TYPE.XBRL,
        limit: int | None = None,
    ) -> Iterator[tuple[EDINETFiling, str]]:
        """
        Iterates over the Edinet filing collect flow and yields tuples of (EDINETFiling, str).

        Args:
            date_from: The start date of the date range.
            date_to: The end date of the date range.
            document_type: The type of document to collect.
                - 1: XBRL (zip) <default>
                - 2: PDF
                - 3: Alternative documents and attachments (zip)
                - 4: English version of the file (zip)
                - 5: CSV (zip)
            limit: The maximum number of filings to collect.

        Yields:
            tuple[EDINETFiling, str]: A tuple containing the EDINET filing and the path.
        """
        yield from cast(
            Iterator[tuple[EDINETFiling, str]],
            super().iter_collect(
                date_from=date_from,
                date_to=date_to,
                limit=limit,
            ),
        )

    @override
    def collect(
        self,
        *,
        date_from: date,
        date_to: date,
        document_type: EDINET_DOCUMENT_DOWNLOAD_TYPE = EDINET_DOCUMENT_DOWNLOAD_TYPE.XBRL,
        limit: int | None = None,
    ) -> list[tuple[EDINETFiling, str]]:
        """
        Collects Edinet filings within the given date range.

        Args:
            date_from: The start date of the date range.
            date_to: The end date of the date range.
            document_type: The type of document to collect.
                - 1: XBRL (zip) <default>
                - 2: PDF
                - 3: Alternative documents and attachments (zip)
                - 4: English version of the file (zip)
                - 5: CSV (zip)
            limit: The maximum number of filings to collect.

        Returns:
            list[tuple[EDINETFiling, str]]: A list of tuples containing the EDINET filing and the filing path.
        """
        return list(
            self.iter_collect(date_from=date_from, date_to=date_to, limit=limit)
        )

    def _fetch_documents(
        self,
        *,
        date_from: date,
        date_to: date,
        document_type: EDINET_DOCUMENT_DOWNLOAD_TYPE,
        limit: int | None = None,
    ) -> Iterator[RawDocument]:
        # Validation
        start = date_from
        end = date_to
        if end < start:
            raise CollectorDateRangeValidationError(start, end)
        if limit is not None and limit <= 0:
            raise CollectorLimitValidationError(limit)

        total_yielded = 0
        current = start
        while current <= end:
            # Fetch document list <type=2: Metadata + metadata_list>
            resp = self._client.get_document_list(
                date=current, type=EDINET_DOCUMENT_LIST_TYPE.METADATA_AND_LIST
            )
            results = resp.get("results")
            if not isinstance(results, list):
                raise CollectorParseResponseValidationError("results")

            for i, row in enumerate(results):
                if not isinstance(row, dict):
                    raise CollectorParseResponseValidationError(f"results[${i}]")
                item = dict[str, Any](**row)
                doc_id = item.get("docID")
                if not doc_id:
                    raise CollectorParseResponseValidationError("docID")

                content = self._client.get_document(doc_id=doc_id, type=document_type)
                if not content:
                    raise CollectorNoContentError(doc_id)

                # Add document download type to infer format from API's parameter
                item["_document_download_type"] = document_type
                yield RawDocument(content=content, meta=item)

                total_yielded += 1
                # limit に達したら、その場で return して翌日の get_document_list に行かない
                if limit is not None and total_yielded >= limit:
                    return
            current += timedelta(days=1)

    def _parse_response(self, meta: Meta) -> Parsed:
        return {
            "doc_id": meta.get("docID"),
            "edinet_code": meta.get("edinetCode"),
            "sec_code": meta.get("secCode"),
            "jcn": meta.get("JCN"),
            "filer_name": meta.get("filerName"),
            "fund_code": meta.get("fundCode"),
            "ordinance_code": meta.get("ordinanceCode"),
            "form_code": meta.get("formCode"),
            "doc_type_code": meta.get("docTypeCode"),
            "doc_description": meta.get("docDescription"),
            "period_start": _parse_edinet_date(meta.get("periodStart")),
            "period_end": _parse_edinet_date(meta.get("periodEnd")),
            "submit_datetime": _parse_edinet_datetime(meta.get("submitDateTime")),
            "parent_doc_id": meta.get("parentDocID"),
            # Additinal field for internal use
            "_document_download_type": meta.get("_document_download_type"),
        }

    def _build_filing(self, parsed: Parsed, content: bytes) -> EDINETFiling:
        document_download_type = parsed.get("_document_download_type")
        if not isinstance(document_download_type, EDINET_DOCUMENT_DOWNLOAD_TYPE):
            raise CollectorParseResponseValidationError("document_download_type")

        doc_id = parsed.get("doc_id")
        format = _infer_edinet_format(document_download_type)

        return EDINETFiling(
            # ID will be automatically generated from identifier fields
            name=EDINETFiling.build_name(
                doc_id=doc_id,
                doc_description=parsed.get("doc_description"),
                format=format,
            ),
            checksum=sha256_checksum(content),
            format=format,
            is_zip=is_zip_content(content),
            doc_id=doc_id,
            edinet_code=parsed.get("edinet_code"),
            sec_code=parsed.get("sec_code"),
            jcn=parsed.get("jcn"),
            filer_name=parsed.get("filer_name"),
            fund_code=parsed.get("fund_code"),
            ordinance_code=parsed.get("ordinance_code"),
            form_code=parsed.get("form_code"),
            doc_type_code=parsed.get("doc_type_code"),
            doc_description=parsed.get("doc_description"),
            period_start=parsed.get("period_start"),
            period_end=parsed.get("period_end"),
            submit_datetime=parsed.get("submit_datetime"),
            parent_doc_id=parsed.get("parent_doc_id"),
        )
