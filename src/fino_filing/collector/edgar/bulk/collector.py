"""EdgarBulkCollector: Bulk 一括データを収集して Collection に保存する（スタブ）。"""

from __future__ import annotations

from datetime import date
from typing import Iterator, Literal, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.collector.edgar.bulk.enum import EdgarBulkType
from fino_filing.collector.error import CollectorParseResponseValidationError
from fino_filing.filing.filing_edgar import EdgarBulkFiling
from fino_filing.util.content import sha256_checksum

from ..client import EdgarClient
from ..config import EdgarConfig


class EdgarBulkCollector(BaseCollector):
    """
    EdgarBulkCollector for SEC Bulk data
    """

    def __init__(self, collection: Collection, config: EdgarConfig) -> None:
        super().__init__(collection)
        self._client = EdgarClient(config)

    @override
    def iter_collect(
        self,
        *,
        bulk_type: EdgarBulkType = EdgarBulkType.COMPANY_FACTS,
    ) -> Iterator[tuple[EdgarBulkFiling, str]]:
        yield from cast(
            Iterator[tuple[EdgarBulkFiling, str]],
            super().iter_collect(
                bulk_type=bulk_type,
            ),
        )

    @override
    def collect(
        self,
        *,
        bulk_type: EdgarBulkType = EdgarBulkType.COMPANY_FACTS,
    ) -> list[tuple[EdgarBulkFiling, str]]:
        return list(
            self.iter_collect(
                bulk_type=bulk_type,
            )
        )

    @override
    def _fetch_documents(
        self,
        *,
        bulk_type: EdgarBulkType = EdgarBulkType.COMPANY_FACTS,
    ) -> Iterator[RawDocument]:
        target: Literal["companyfacts", "submissions"]
        if bulk_type == EdgarBulkType.COMPANY_FACTS:
            target = "companyfacts"
        elif bulk_type == EdgarBulkType.SUBMISSIONS:
            target = "submissions"
        content = self._client.get_bulk(target)
        yield RawDocument(
            content=content, meta={"bulk_type": bulk_type, "bulk_date": date.today()}
        )

    @override
    def _parse_response(self, raw: RawDocument) -> Parsed:
        meta = raw.meta
        return {
            "bulk_type": meta.get("bulk_type"),
            "bulk_date": meta.get("bulk_date"),
        }

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EdgarBulkFiling:
        bulk_type = parsed.get("bulk_type")
        if not bulk_type:
            raise CollectorParseResponseValidationError("bulk_type")
        bulk_date = parsed.get("bulk_date")
        if not bulk_date:
            raise CollectorParseResponseValidationError("bulk_date")
        return EdgarBulkFiling(
            source="Edgar",
            name=EdgarBulkFiling.build_default_name(
                bulk_type=bulk_type, bulk_date=bulk_date
            ),
            checksum=sha256_checksum(content),
            bulk_type=bulk_type,
            bulk_date=bulk_date,
        )
