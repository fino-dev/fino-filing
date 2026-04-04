"""EdgarBulkCollector: Bulk 一括データを収集して Collection に保存する（スタブ）。"""

from __future__ import annotations

import hashlib
from typing import Any, Iterator, cast, override

from fino_filing.filing.filing_edgar import EdgarBulkFiling

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import BaseCollector, Meta, Parsed, RawDocument

from .._helpers import _parse_meta_to_parsed
from ..client import EdgarClient
from ..config import EdgarConfig


class EdgarBulkCollector(BaseCollector):
    """
    SEC Bulk データを一括取得して Collection に保存する。

    用途: Bulk 用 URL から一括取得して Collection に保存する。
    収集条件: collect(date_from=..., date_to=..., cik_list=..., limit=N) で渡す。
    注意: 現状は未実装のスタブ。
    """

    def __init__(self, collection: Collection, config: EdgarConfig) -> None:
        super().__init__(collection)
        self._client = EdgarClient(config)

    @override
    def iter_collect(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        cik_list: list[str] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> Iterator[tuple[EdgarBulkFiling, str]]:
        """1 件ずつ Collection に追加し、(EdgarBulkFiling, path) を yield する。"""
        yield from cast(
            Iterator[tuple[EdgarBulkFiling, str]],
            super().iter_collect(
                date_from=date_from,
                date_to=date_to,
                cik_list=cik_list,
                limit=limit,
                **kwargs,
            ),
        )

    @override
    def collect(
        self,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        cik_list: list[str] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> list[tuple[EdgarBulkFiling, str]]:
        """収集フローを実行し、EdgarBulkFiling と保存パスのリストを返す。"""
        return list(
            self.iter_collect(
                date_from=date_from,
                date_to=date_to,
                cik_list=cik_list,
                limit=limit,
                **kwargs,
            )
        )

    @override
    def _fetch_documents(
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

    @override
    def _parse_response(self, meta: Meta) -> Parsed:
        """RawDocument の meta を EdgarBulkFiling 用の Parsed に正規化する。"""
        return _parse_meta_to_parsed(meta)

    @override
    def _build_filing(self, parsed: Parsed, content: bytes) -> EdgarBulkFiling:
        """Parsed と content から EdgarBulkFiling を生成する。"""
        primary_name = parsed.get("primary_name") or (
            parsed.get("accession_number", "") + "-index.htm"
        )
        return EdgarBulkFiling(
            source="Edgar",
            name=primary_name,
            checksum=hashlib.sha256(content).hexdigest(),
            format="zip",
            is_zip=True,
            type=parsed.get("type", ""),
        )
