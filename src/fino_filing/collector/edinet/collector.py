"""
EDINET 書類一覧API・書類取得API を用いて書類を収集し、Collection に保存する Collector。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterator, cast

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edinet import EDINETFiling

from ._helpers import _build_edinet_filing, _list_item_to_parsed, _meta_to_parsed
from .client import EdinetClient
from .config import EdinetConfig


class EdinetCollector(BaseCollector):
    """
    EDINET の書類一覧APIで一覧取得し、書類取得APIで実体を取得して Collection に保存する。

    用途: 提出日範囲で書類一覧を取得し、各書類を PDF 等で取得して EDINETFiling として保存する。
    収集条件: collect(date_from=..., date_to=..., limit=...) で渡す。
    """

    def __init__(self, collection: Collection, config: EdinetConfig) -> None:
        super().__init__(collection)
        self._client = EdinetClient(config)

    def fetch_documents(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
        list_type: int = 2,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """
        書類一覧APIで日付範囲の一覧を取得し、各 doc_id で書類実体を取得して RawDocument を yield する。
        """
        if not date_from:
            return
        start = _parse_date(date_from)
        end = _parse_date(date_to) if date_to else start
        if start is None:
            return
        if end is None:
            end = start
        if end < start:
            end = start

        total_yielded = 0
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            resp = self._client.get_document_list(date_str, type=list_type)
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
                parsed = _list_item_to_parsed(item)
                meta: dict[str, Any] = {
                    **parsed,
                    "doc_id": doc_id,
                }
                yield RawDocument(content=content, meta=meta)
                total_yielded += 1
                if limit is not None and total_yielded >= limit:
                    return
            current += timedelta(days=1)

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDINETFiling 用の Parsed に正規化する。"""
        return _meta_to_parsed(raw.meta)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDINETFiling:
        """Parsed と content から EDINETFiling を生成する。"""
        name = parsed.get("doc_id") or "document"
        return _build_edinet_filing(parsed, raw.content, name)


def _parse_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None
