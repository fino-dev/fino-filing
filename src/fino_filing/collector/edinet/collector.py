from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument
from fino_filing.collector.error import (
    CollectorDateRangeValidationError,
    CollectorLimitValidationError,
    CollectorParseResponseValidationError,
)
from fino_filing.filing.filing_edinet import EDINETFiling

from ._helpers import _parse_edinet_date, _parse_edinet_datetime
from .client import EdinetClient
from .config import EdinetConfig


class EdinetCollector(BaseCollector):
    """
    Edinet Collector that collects filings from the Edinet API.
    """

    def __init__(self, collection: Collection, config: EdinetConfig) -> None:
        super().__init__(collection)
        self._client = EdinetClient(config)

    @override
    def iter_collect(
        self,
        *,
        date_from: date,
        date_to: date,
        limit: int | None = None,
    ) -> Iterator[tuple[EDINETFiling, str]]:
        """
        Iterates over the Edinet filing collect flow and yields tuples of (EDINETFiling, str).

        Args:
            date_from: The start date of the date range.
            date_to: The end date of the date range.
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
        limit: int | None = None,
    ) -> list[tuple[EDINETFiling, str]]:
        """
        Collects Edinet filings within the given date range.

        Args:
            date_from: The start date of the date range.
            date_to: The end date of the date range.
            limit: The maximum number of filings to collect.

        Returns:
            list[tuple[EDINETFiling, str]]: A list of tuples containing the EDINET filing and the filing path.
        """
        return list(
            self.iter_collect(date_from=date_from, date_to=date_to, limit=limit)
        )

    def _fetch_documents(
        self, *, date_from: date, date_to: date, limit: int | None = None
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
            resp = self._client.get_document_list(current, type=2)
            results = resp.get("results")
            if not isinstance(results, list):
                raise CollectorParseResponseValidationError("results")

            for i, row in enumerate(results):
                if not isinstance(row, dict):
                    raise CollectorParseResponseValidationError(f"results[${i}]")
                item = dict[str, Any](**row)
                doc_id = item.get("docID")
                if not doc_id:
                    continue

                content = self._client.get_document(doc_id)
                if not content:
                    continue

                yield RawDocument(content=content, meta=item)
                total_yielded += 1
                # limit に達したら、その場で return して翌日の get_document_list に行かない
                if limit is not None and total_yielded >= limit:
                    return
            current += timedelta(days=1)

    def _parse_response(self, meta: Meta) -> Parsed:
        doc_id = meta.get("docId")
        if doc_id is None:
            raise CollectorParseResponseValidationError("doc_id is required")

        return {
            "doc_id": doc_id,
            "edinet_code": meta.get("edinetCode"),
            "sec_code": meta.get("secCode"),
            "jcn": meta.get("JCN"),
            "filer_name": meta.get("filerName"),
            "ordinance_code": meta.get("ordinanceCode"),
            "form_code": meta.get("formCode"),
            "doc_type_code": meta.get("docTypeCode"),
            "doc_description": meta.get("docDescription"),
            "period_start": _parse_edinet_date(meta.get("periodStart")),
            "period_end": _parse_edinet_date(meta.get("periodEnd")),
            "submit_datetime": _parse_edinet_datetime(meta.get("submitDateTime")),
            "parent_doc_id": meta.get("parentDocID"),
        }

    def _build_filing(self, parsed: Parsed, content: bytes) -> EDINETFiling:
        name = parsed.get("doc_id") or "document"
        checksum = hashlib.sha256(content).hexdigest()
        # ID will be automatically generated from identifier fields
        return EDINETFiling(
            source="EDINET",
            name=name,
            checksum=checksum,
            format="pdf",
            is_zip=False,
            doc_id=parsed.get("doc_id", ""),
            edinet_code=parsed.get("edinet_code", ""),
            sec_code=parsed.get("sec_code", ""),
            jcn=parsed.get("jcn", ""),
            filer_name=parsed.get("filer_name", ""),
            ordinance_code=parsed.get("ordinance_code", ""),
            form_code=parsed.get("form_code", ""),
            doc_type_code=parsed.get("doc_type_code", ""),
            doc_description=parsed.get("doc_description", ""),
            period_start=parsed.get("period_start"),
            period_end=parsed.get("period_end"),
            submit_datetime=parsed.get("submit_datetime"),
            parent_doc_id=parsed.get("parent_doc_id"),
            created_at=datetime.now(),
        )
