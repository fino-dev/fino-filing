"""EdgerBulkCollector: Bulk 一括データを収集して Collection に保存する（スタブ）。"""

from __future__ import annotations

from typing import Any, Iterator

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument
from fino_filing.filing.filing_edger import EDGARFiling

from ._helpers import _build_edgar_filing, _parse_meta_to_parsed
from .client import EdgerClient
from .config import EdgerConfig


class EdgerBulkCollector(BaseCollector):
    """
    SEC Bulk データを一括取得して Collection に保存する。

    用途: Bulk 用 URL から一括取得して Collection に保存する。
    収集条件: collect(date_from=..., date_to=..., cik_list=..., limit=N) で渡す。
    注意: 現状は未実装のスタブ。
    """

    def __init__(self, collection: Collection, config: EdgerConfig) -> None:
        super().__init__(collection)
        self._client = EdgerClient(config)

    def fetch_documents(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        cik_list: list[str] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> Iterator[RawDocument]:
        """Bulk データを取得して RawDocument を yield する。TODO: 実装。"""
        yield from ()

    def parse_response(self, raw: RawDocument) -> Parsed:
        """RawDocument の meta を EDGARFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(raw.meta)

    def build_filing(self, parsed: Parsed, raw: RawDocument) -> EDGARFiling:
        """Parsed と content から EDGARFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (
            parsed.get("accession_number", "") + "-index.htm"
        )
        return _build_edgar_filing(parsed, raw.content, primary_name)
