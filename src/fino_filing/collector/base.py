"""
Collector Boundary: 共通型と BaseCollector（Template Method）

責務:
- RawDocument / Parsed の共通型定義
- 収集フロー（fetch → parse → build_filing → add_to_collection）の骨格定義
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from fino_filing.collection.collection import Collection
from fino_filing.filing.filing import Filing

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawDocument:
    """
    1 件分の生データ。Strategy が fetch_documents() で返す単位。

    content は必須。meta にソース固有のメタデータ（accession, cik, form 等）を格納する。
    """

    content: bytes
    meta: dict[str, Any]


# parse_response(raw) の戻り型。Filing に渡す前の中間構造（コア＋ソース固有フィールドの dict）。
Parsed = dict[str, Any]


class BaseCollector(ABC):
    """
    収集の共通フローを定義する Template Method の抽象基底クラス。

    collect() が骨格を定義し、fetch_documents / parse_response / build_filing を
    サブクラスで差し替える。
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def collect(self) -> list[tuple[Filing, str]]:
        """
        収集を実行する。fetch → parse → build_filing → add_to_collection の順で処理する。

        Returns:
            add_to_collection の戻り値のリスト（各要素は (Filing, path)）
        """
        raw_list = self.fetch_documents()
        results: list[tuple[Filing, str]] = []
        for raw in raw_list:
            parsed = self.parse_response(raw)
            filing = self.build_filing(parsed, raw)
            results.append(self.add_to_collection(filing, raw.content))
        return results

    def add_to_collection(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        """
        Collection に 1 件追加する。Facade である Collection.add に委譲する。
        """
        return self._collection.add(filing, content)

    @abstractmethod
    def fetch_documents(self) -> list[RawDocument]:
        """取得した生ドキュメントのリストを返す。サブクラスで実装する。"""
        ...

    @abstractmethod
    def parse_response(self, raw: RawDocument) -> Parsed:
        """生ドキュメントをパースして Parsed に変換する。サブクラスで実装する。"""
        ...

    @abstractmethod
    def build_filing(self, parsed: Parsed, raw: RawDocument) -> Filing:
        """
        Parsed と raw（checksum 等に必要）から Filing を生成する。サブクラスで実装する。
        """
        ...
