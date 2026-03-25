"""BaseCollector のテンプレートメソッド collect() のフローを検証する"""

import hashlib
from typing import Any, Iterator

import pytest

from fino_filing import Collection, Filing
from fino_filing.collector.base import BaseCollector, Parsed, RawDocument


class StubCollector(BaseCollector):
    """抽象メソッドをスタブ実装した具象クラス"""

    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)
        self.fetch_called = 0
        self.parse_called = 0
        self.build_called = 0
        self.add_called = 0
        self.raws: list[RawDocument] = []

    def _fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
        self.fetch_called += 1
        yield from self.raws

    def _parse_response(self, raw: RawDocument) -> Parsed:
        self.parse_called += 1
        return {"_raw_id": id(raw)}

    def _build_filing(self, parsed: Parsed, content: bytes) -> Filing:
        self.build_called += 1
        checksum = hashlib.sha256(content).hexdigest()
        return Filing(
            source="stub",
            checksum=checksum,
            name="stub.txt",
            is_zip=False,
            format="txt",
        )

    def _add_to_collection(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        self.add_called += 1
        return super()._add_to_collection(filing, content)


@pytest.mark.module
@pytest.mark.collector
class TestBaseCollector:
    """BaseCollector Test"""

    def test_iter_collect_calls_fetch_parse_build_add_per_raw(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """iter_collectが1件ずつ内部メソッドを呼び出していること"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        raw1 = RawDocument(content=b"a", meta={})
        raw2 = RawDocument(content=b"b", meta={})
        stub.raws = [raw1, raw2]

        iterated = list(stub.iter_collect())

        # _fetch_documents は iter_collect あたり 1 回（ジェネレータが複数件 yield）
        assert stub.fetch_called == 1
        assert stub.parse_called == 2
        assert stub.build_called == 2
        assert stub.add_called == 2
        assert len(iterated) == 2
        for filing, path in iterated:
            assert filing.source == "stub"
            assert path

    def test_iter_collect_allows_progress_between_items(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """iter_collect をループで都度呼び出しして、処理を行えること"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        stub.raws = [
            RawDocument(content=b"x", meta={}),
            RawDocument(content=b"y", meta={}),
        ]

        count = 0
        for _ in stub.iter_collect():
            count += 1

        assert count == 2

    def test_collect_calls_fetch_then_parse_build_add_per_raw(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """collectが内部のメソッドを適切に呼び出していること"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        raw1 = RawDocument(content=b"a", meta={})
        raw2 = RawDocument(content=b"b", meta={})
        stub.raws = [raw1, raw2]

        results = stub.collect()

        assert stub.fetch_called == 1
        assert stub.parse_called == 2
        assert stub.build_called == 2
        assert stub.add_called == 2
        assert len(results) == 2
        for filing, path in results:
            assert filing.source == "stub"
            assert path

    def test_collect_empty_list_adds_nothing(
        self,
        temp_collection: tuple[Collection, object],
    ) -> None:
        """collectが空リストのときに不要な内部メソッドを呼び出していないこと"""
        collection, _ = temp_collection
        stub = StubCollector(collection)
        stub.raws = []

        results = stub.collect()

        assert stub.fetch_called == 1
        assert stub.parse_called == 0
        assert stub.build_called == 0
        assert stub.add_called == 0
        assert len(results) == 0
