"""
EDINET 書類一覧API・書類取得API を用いて書類を収集し、Collection に保存する Collector。
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any, Iterator, cast, override

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.collector.error import CollectorDateRangeValidationError
from fino_filing.filing.filing_edinet import EDINETFiling

from ._helpers import _parse_edinet_datetime
from .client import EdinetClient
from .config import EdinetConfig


class EdinetCollector(BaseCollector):
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
        list_type: int = 2,
        **kwargs: Any,
    ) -> Iterator[tuple[EDINETFiling, str]]:
        yield from cast(
            Iterator[tuple[EDINETFiling, str]],
            super().iter_collect(
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                list_type=list_type,
                **kwargs,
            ),
        )

    @override
    def collect(
        self,
        *,
        date_from: date,
        date_to: date,
        limit: int | None = None,
        list_type: int = 2,
        **kwargs: Any,
    ) -> list[tuple[EDINETFiling, str]]:
        return list(
            self.iter_collect(
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                list_type=list_type,
                **kwargs,
            )
        )

    def _fetch_documents(
        self,
        *,
        date_from: date,
        date_to: date,
        limit: int | None = None,
        list_type: int = 2,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        start = date_from
        end = date_to
        if end < start:
            raise CollectorDateRangeValidationError(start, end)

        total_yielded = 0
        current = start
        while current <= end:
            resp = self._client.get_document_list(current, type=list_type)
            raw_results = resp.get("results")
            if isinstance(raw_results, list):
                results = cast(list[Any], raw_results)
            else:
                results = []
            for item in results:
                if limit is not None and total_yielded >= limit:
                    return
                doc_id = item.get("docID") or item.get("doc_id") or ""
                if not doc_id:
                    continue
                content = self._client.get_document(doc_id)
                if not content:
                    continue
                meta = dict(item)
                meta["doc_id"] = doc_id
                yield RawDocument(content=content, meta=meta)
                total_yielded += 1
                if limit is not None and total_yielded >= limit:
                    return
            current += timedelta(days=1)

    def _parse_response(self, raw: RawDocument) -> Parsed:
        ここの整理を仕様書を元に行う
        https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf
        return {
            "doc_id": raw.meta.get("docID") or raw.meta.get("doc_id") or "",
            "edinet_code": raw.meta.get("edinetCode")
            or raw.meta.get("edinet_code")
            or "",
            "sec_code": raw.meta.get("secCode") or raw.meta.get("sec_code") or "",
            "jcn": raw.meta.get("JCN") or raw.meta.get("jcn") or "",
            "filer_name": raw.meta.get("filerName") or raw.meta.get("filer_name") or "",
            "ordinance_code": raw.meta.get("ordinanceCode")
            or raw.meta.get("ordinance_code")
            or "",
            "form_code": raw.meta.get("formCode") or raw.meta.get("form_code") or "",
            "doc_type_code": raw.meta.get("docTypeCode")
            or raw.meta.get("doc_type_code")
            or "",
            "doc_description": raw.meta.get("docDescription")
            or raw.meta.get("doc_description")
            or "",
            "period_start": _parse_edinet_datetime(
                raw.meta.get("periodStart") or raw.meta.get("period_start")
            ),
            "period_end": _parse_edinet_datetime(
                raw.meta.get("periodEnd") or raw.meta.get("period_end")
            ),
            "submit_datetime": _parse_edinet_datetime(
                raw.meta.get("submitDateTime") or raw.meta.get("submit_datetime")
            ),
            "parent_doc_id": raw.meta.get("parentDocID")
            or raw.meta.get("parent_doc_id"),
        }

    def _build_filing(self, parsed: Parsed, content: bytes) -> EDINETFiling:
        name = parsed.get("doc_id") or "document"
        checksum = hashlib.sha256(content).hexdigest()
        # if will generate from identifier fields
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
