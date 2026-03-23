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
from typing import Any, Iterator

from fino_filing.collection.collection import Collection
from fino_filing.filing.filing import Filing

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawDocument:
    """
    1 件分の生データ。fetch_documents() で返す単位。

    content は必須。meta にソース固有のメタデータ（accession, cik, form 等）を格納する。
    """

    content: bytes
    meta: dict[str, Any]


# parse_response(raw) の戻り型。Filing に渡す前の中間構造（コア＋ソース固有フィールドの dict）。
Parsed = dict[str, Any]


class BaseCollector(ABC):
    """
    収集の共通フローを定義する Template Method の抽象基底クラス。

    collect(**criteria) / iter_collect(**criteria) が骨格を定義し、
    fetch_documents / parse_response / build_filing をサブクラスで差し替える。
    収集条件（cik_list 等）は collect / iter_collect 呼び出し時に渡す。
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def iter_collect(self, **criteria: Any) -> Iterator[tuple[Filing, str]]:
        """
        1 件ずつ fetch → parse → build_filing → add_to_collection を行い、
        各件の (Filing, path) を yield する。collect() は本イテレータを list 化したもの。

        イテレーションを途中で止めた場合、それまでに yield した分は Collection に保存済み。
        """
        for raw in self.fetch_documents(**criteria):
            parsed = self.parse_response(raw)
            filing = self.build_filing(parsed, raw)
            yield self.add_to_collection(filing, raw.content)

    def collect(self, **criteria: Any) -> list[tuple[Filing, str]]:
        """
        収集を実行する。1 件ずつ fetch → parse → build_filing → add_to_collection の順で処理し、
        途中終了してもそれまでに処理した分は保存される。

        Args:
            **criteria: サブクラスの fetch_documents に渡す収集条件
                        （例: cik_list, limit_per_company, date_from 等）

        Returns:
            add_to_collection の戻り値のリスト（各要素は (Filing, path)）
        """
        return list(self.iter_collect(**criteria))

    def add_to_collection(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        """Collection に 1 件追加する。Facade である Collection.add に委譲する。"""
        return self._collection.add(filing, content)

    @abstractmethod
    def fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
        """取得した生ドキュメントを 1 件ずつ yield する。サブクラスで実装する。"""
        ...

    @abstractmethod
    def parse_response(self, raw: RawDocument) -> Parsed:
        """生ドキュメントをパースして Parsed に変換する。サブクラスで実装する。"""
        ...

    @abstractmethod
    def build_filing(self, parsed: Parsed, raw: RawDocument) -> Filing:
        """Parsed と raw（checksum 等に必要）から Filing を生成する。サブクラスで実装する。"""
        ...
